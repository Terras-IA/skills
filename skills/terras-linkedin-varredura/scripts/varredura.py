#!/usr/bin/env python3
"""Janela, triagem, checkpoint e índice da varredura do feed do LinkedIn.

Só stdlib. O navegador coleta (feed_varrer.js); este script decide o que é novo e guarda o estado.

Uso:
  varredura.py janela [--horas N]          desde quando varrer (checkpoint ou últimas 24 h)
  varredura.py triar COLETA.json [COLETA.json ...] [--horas N]
                                           junta as cargas, corta janela, promovido, já visto e
                                           já estudado; grava varredura/AAAA-MM-DD-HHMM.md e .json
                                           e diz quantos posts novos a última carga trouxe
  varredura.py fechar TRIAGEM.json [--falhas URN ...]
                                           move o checkpoint para o início da coleta e marca
                                           como vistos todos os posts da triagem, menos as falhas
  varredura.py indexar PASTA [PASTA ...]   acrescenta no indice.md as notas que ainda não estão lá

Estado em BASE/varredura/estado.json: {"ultima_verificacao": ISO, "vistos": {id: {...}},
"pendentes": {id: post}}. Pendente = falhou numa varredura; volta como candidato na próxima,
mesmo que já esteja antes da janela.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

BASE = os.path.expanduser(os.environ.get("CONHECIMENTO_BASE", "~/linkedin/conhecimento"))
PASTA = os.path.join(BASE, "varredura")
ESTADO = os.path.join(PASTA, "estado.json")
HORAS_PADRAO = 24
TETO_DIAS = 7  # checkpoint muito antigo: o feed não vai tão longe, a janela para em 7 dias
GUARDA_DIAS = 45
MARGEM_H = 6  # o feed não é cronológico: post de antes do checkpoint pode aparecer só agora; `vistos` evita repetir
TENTATIVAS = 3  # pendente que falha 3 vezes sai da fila

ALERTAS = {
    "vaga": r"\b(vagas?|hiring|estamos contratando|we'?re hiring|open to work|oportunidade de emprego|processo seletivo)\b",
    "pessoal": r"\b(aniversário|novo emprego|new position|comecei (?:hoje )?(?:na|no|em)|happy to share that|feliz em (?:anunciar|compartilhar)|promovid[oa] a)\b",
    "evento": r"\b(inscri[çc][õo]es|webinar|live (?:hoje|amanhã)|garanta (?:já )?sua vaga|link na bio)\b",
}


def agora():
    return dt.datetime.now(dt.timezone.utc)


def iso(d):
    return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ler_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def carregar_estado():
    if not os.path.exists(ESTADO):
        return {"ultima_verificacao": None, "vistos": {}, "pendentes": {}}
    with open(ESTADO, encoding="utf-8") as f:
        e = json.load(f)
    e.setdefault("pendentes", {})
    return e


def salvar_estado(e):
    os.makedirs(PASTA, exist_ok=True)
    tmp = ESTADO + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1)
    os.replace(tmp, ESTADO)


def calc_janela(horas):
    e = carregar_estado()
    if horas:
        return agora() - dt.timedelta(hours=horas), f"últimas {horas} h (pedido)"
    if e.get("ultima_verificacao"):
        desde = ler_iso(e["ultima_verificacao"])
        teto = agora() - dt.timedelta(days=TETO_DIAS)
        if desde < teto:
            return teto, f"checkpoint de {e['ultima_verificacao'][:16]} tem mais de {TETO_DIAS} dias: janela cortada em {TETO_DIAS} dias"
        return desde - dt.timedelta(hours=MARGEM_H), \
            f"desde a última verificação ({e['ultima_verificacao'][:16]} UTC, com {MARGEM_H} h de margem)"
    return agora() - dt.timedelta(hours=HORAS_PADRAO), f"primeira varredura: últimas {HORAS_PADRAO} h"


def id_urn(urn):
    m = re.search(r"(\d{15,})$", urn or "")
    return m and m.group(1)


def chave_sem_link(p):
    return "sl:" + re.sub(r"\W+", "", (p["autor"] + p["texto"][-200:]).lower())[:80]


def ja_estudado(pid):
    """Pasta da terras-linkedin-conhecimento termina em -<id6>; conta se já tem conhecimento.md."""
    if not pid:
        return None
    for p in glob.glob(os.path.join(BASE, "20??-??-??", f"*-{pid[-6:]}")):
        if os.path.exists(os.path.join(p, "conhecimento.md")):
            return p
    return None


def cmd_janela(a):
    desde, origem = calc_janela(a.horas)
    print(json.dumps({"desde_ms": int(desde.timestamp() * 1000), "desde": iso(desde), "origem": origem},
                     ensure_ascii=False))


def juntar(arquivos):
    """Uma coleta por carga de página: junta sem duplicar (URN, ou autor + início do texto)."""
    col = {"coletado_em": None, "rodadas": 0, "coletados": 0, "promovidos": 0, "cargas": 0, "posts": []}
    vistos = set()
    for arq in arquivos:
        with open(arq, encoding="utf-8") as f:
            c = json.load(f, strict=False)
        col["cargas"] += 1
        col["coletado_em"] = min(filter(None, [col["coletado_em"], c["coletado_em"]]))
        for k in ("rodadas", "coletados", "promovidos"):
            col[k] += c.get(k) or 0
        col["ultima_carga_novos"] = 0
        for p in c.get("posts", []):
            chave = p.get("urn") or (p["autor"] + "|" + p["texto"][:120])
            if chave in vistos:
                ja = next(x for x in col["posts"] if (x.get("urn") or (x["autor"] + "|" + x["texto"][:120])) == chave)
                if ja["tipo"] == "texto" and p["tipo"] != "texto":  # a mídia carrega depois do card
                    ja["tipo"] = p["tipo"]
                continue
            vistos.add(chave)
            col["posts"].append(p)
            col["ultima_carga_novos"] += 1
    return col


def cmd_triar(a):
    col = juntar(a.coletas)
    e = carregar_estado()
    desde, origem = calc_janela(a.horas)
    desde_ms = desde.timestamp() * 1000
    grupos = {"candidatos": [], "sem_link": [], "promovidos": [], "ja_vistos": [], "ja_estudados": [], "fora": []}
    for p in col.get("posts", []):
        pid = id_urn(p.get("urn"))
        p["id"] = pid
        p["alertas"] = [k for k, rx in ALERTAS.items() if re.search(rx, p.get("texto", ""), re.I)]
        if p.get("ts") and p["ts"] < desde_ms:
            grupos["fora"].append(p)
        elif p.get("promovido"):
            grupos["promovidos"].append(p)
        elif pid and pid in e["vistos"]:
            grupos["ja_vistos"].append(p)
        elif pid and ja_estudado(pid):
            p["pasta"] = ja_estudado(pid)
            grupos["ja_estudados"].append(p)
        elif not p.get("urn"):
            if chave_sem_link(p) not in e["vistos"]:
                grupos["sem_link"].append(p)
        else:
            grupos["candidatos"].append(p)
    na_coleta = {p["id"] for p in grupos["candidatos"]}
    for pid, p in e["pendentes"].items():
        if pid not in na_coleta and pid not in e["vistos"]:
            grupos["candidatos"].append({**p, "id": pid, "alertas": p.get("alertas", []) + ["pendente"]})
    grupos["candidatos"].sort(key=lambda p: p.get("ts") or 0, reverse=True)

    os.makedirs(PASTA, exist_ok=True)
    carimbo = ler_iso(col["coletado_em"]).astimezone().strftime("%Y-%m-%d-%H%M")
    saida = os.path.join(PASTA, carimbo)
    triagem = {"coletado_em": col["coletado_em"], "desde": iso(desde), "origem": origem,
               "cargas": col["cargas"], "coletados": col["coletados"], "rodadas": col["rodadas"],
               "promovidos_no_feed": col["promovidos"], "unicos_na_janela": len(col["posts"]), **grupos}
    with open(saida + ".json", "w", encoding="utf-8") as f:
        json.dump(triagem, f, ensure_ascii=False, indent=1)
    with open(saida + ".md", "w", encoding="utf-8") as f:
        f.write(markdown(triagem))
    resumo = {k: len(v) for k, v in grupos.items()}
    print(json.dumps({"triagem": saida + ".json", "tabela": saida + ".md", "origem": origem,
                      "cargas": col["cargas"], "ultima_carga_novos": col["ultima_carga_novos"],
                      "unicos_na_janela": len(col["posts"]), **resumo,
                      "candidatos": [{"n": i, "autor": p["autor"], "tipo": p["tipo"], "quando": p["quando"],
                                      "alertas": p["alertas"], "url": p["url"], "texto": p["texto"][:220]}
                                     for i, p in enumerate(grupos["candidatos"], 1)]},
                     ensure_ascii=False, indent=1))


def markdown(t):
    linhas = [f"# Varredura do feed · {t['coletado_em'][:16]} UTC", "",
              f"- Janela: {t['origem']} (desde {t['desde'][:16]} UTC)",
              f"- Feed: {t['coletados']} cards em {t['cargas']} cargas de página ({t['rodadas']} rodadas);"
              f" {t['unicos_na_janela']} únicos na janela, além de {t['promovidos_no_feed']} promovidos",
              f"- Candidatos: {len(t['candidatos'])} · sem link: {len(t['sem_link'])} · promovidos: {len(t['promovidos'])}"
              f" · já vistos: {len(t['ja_vistos'])} · já estudados: {len(t['ja_estudados'])}", "",
              "## Candidatos", "", "| # | Quando (UTC) | Autor | Tipo | Alertas | Início |", "|---|---|---|---|---|---|"]
    for i, p in enumerate(t["candidatos"], 1):
        ini = p["texto"][:110].replace("|", "/")
        linhas.append(f"| {i} | {p['quando'] or '?'} | [{p['autor']}]({p['url']}) | {p['tipo']} | {', '.join(p['alertas'])} | {ini} |")
    if t["sem_link"]:
        linhas += ["", "## Sem link (sem URN no card)", ""]
        linhas += [f"- {p['autor']} · {p['tipo']} · {p['texto'][:110]}" for p in t["sem_link"]]
    linhas += ["", "## Decisão", "", "(preenchido ao fim: estudado, descartado com motivo, falhou)", ""]
    return "\n".join(linhas)


def cmd_fechar(a):
    with open(a.triagem, encoding="utf-8") as f:
        t = json.load(f)
    e = carregar_estado()
    falhas = {id_urn(u) or u for u in a.falhas}
    marcados = 0
    desistidos = []
    for p in t["sem_link"]:
        e["vistos"][chave_sem_link(p)] = {"autor": p["autor"], "quando": p.get("quando"), "visto": t["coletado_em"]}
    for grupo in ("candidatos", "ja_estudados"):
        for p in t[grupo]:
            if not p.get("id"):
                continue
            if p["id"] in falhas:
                n = e["pendentes"].get(p["id"], {}).get("tentativas", 0) + 1
                if n < TENTATIVAS:
                    e["pendentes"][p["id"]] = {**{k: p.get(k) for k in ("urn", "autor", "ts", "quando", "tipo", "url", "texto")},
                                               "tentativas": n}
                    continue
                e["pendentes"].pop(p["id"], None)
                desistidos.append(p["autor"])
            e["vistos"][p["id"]] = {"autor": p["autor"], "quando": p.get("quando"), "visto": t["coletado_em"]}
            e["pendentes"].pop(p["id"], None)
            marcados += 1
    limite = iso(agora() - dt.timedelta(days=GUARDA_DIAS))
    e["vistos"] = {k: v for k, v in e["vistos"].items() if (v.get("visto") or "") >= limite}
    anterior = e.get("ultima_verificacao")
    if not anterior or t["coletado_em"] > anterior:
        e["ultima_verificacao"] = t["coletado_em"]
    salvar_estado(e)
    print(json.dumps({"ultima_verificacao": e["ultima_verificacao"], "marcados": marcados,
                      "pendentes": sorted(e["pendentes"]), "desistidos_apos_3_falhas": desistidos,
                      "vistos_total": len(e["vistos"])}, ensure_ascii=False))


def cmd_indexar(a):
    indice = os.path.join(BASE, "indice.md")
    atual = open(indice, encoding="utf-8").read() if os.path.exists(indice) else "# Conhecimento do LinkedIn\n"
    novas, pulos = [], []
    for pasta in a.pastas:
        nota = os.path.join(pasta, "conhecimento.md")
        if not os.path.exists(nota):
            pulos.append({"pasta": pasta, "motivo": "sem conhecimento.md"})
            continue
        rel = os.path.relpath(os.path.abspath(nota), os.path.abspath(BASE))
        if rel.startswith(".."):
            pulos.append({"pasta": pasta, "motivo": "fora de " + BASE})
            continue
        if f"]({rel})" in atual:
            pulos.append({"pasta": pasta, "motivo": "já no índice"})
            continue
        txt = open(nota, encoding="utf-8").read()
        titulo = (re.search(r"^# (.+)$", txt, re.M) or [None, os.path.basename(pasta)])[1].strip()
        fonte = re.search(r"^> Fonte: (.+?), LinkedIn, (\d{4}-\d{2}-\d{2})", txt, re.M)
        tags = re.search(r"^> Tags: (.+)$", txt, re.M)
        autor, data = (fonte.group(1), fonte.group(2)) if fonte else ("?", rel[:10])
        novas.append(f"- {data} · [{titulo}]({rel}) · {autor} · {tags.group(1).strip() if tags else ''}".rstrip(" ·"))
    if novas:
        cab, _, resto = atual.partition("\n")
        corpo = resto.lstrip("\n")
        with open(indice, "w", encoding="utf-8") as f:
            f.write(cab + "\n\n" + "\n".join(novas) + "\n" + corpo)
    print(json.dumps({"indexadas": len(novas), "linhas": novas, "pulos": pulos}, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("janela"); s.add_argument("--horas", type=int); s.set_defaults(f=cmd_janela)
    s = sub.add_parser("triar"); s.add_argument("coletas", nargs="+"); s.add_argument("--horas", type=int); s.set_defaults(f=cmd_triar)
    s = sub.add_parser("fechar"); s.add_argument("triagem"); s.add_argument("--falhas", nargs="*", default=[]); s.set_defaults(f=cmd_fechar)
    s = sub.add_parser("indexar"); s.add_argument("pastas", nargs="+"); s.set_defaults(f=cmd_indexar)
    a = ap.parse_args()
    return a.f(a) or 0


if __name__ == "__main__":
    sys.exit(main())

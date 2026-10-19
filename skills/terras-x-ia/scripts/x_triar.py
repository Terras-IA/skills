#!/usr/bin/env python3
"""Junta coletas do xColetar (JSON), deduplica, filtra janela e ranqueia.

Uso:
  python3 x_triar.py coleta1.json [coleta2.json ...] --dias 7 --tema "agentes de código" \
      [--min-curtidas 50] [--saida-dir ~/linkedin/conhecimento/x-ia]

Grava <data>-<slug>.json (todos os posts, com nota e alertas) e <data>-<slug>.md
(tabela para o agente triar). Não decide o que é sinal: marca isca e ranqueia.
"""
import argparse
import json
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from pathlib import Path

ISCA = [
    (r"\b(no one|nobody) (expected|is talking)|ninguém (esperava|está falando)", "hype"),
    (r"\b(is|are) (dead|over)\b|\bin serious danger\b|\bRIP\b|morreu|acabou\b|\bdangerous\b|\billegal\b|\bf\*?u?cking\b|perigos[oa]", "alarmismo"),
    (r"\bsave (this|these)\b|\bbookmark\b|\bsalve (isso|este)\b", "isca-de-salvar"),
    (r"\bgoldmine\b|\b(absolute(ly)?|pure) gold\b|\bgod-level\b|\bcheat ?code\b|\bsecret (trick|hack)\b|\bgame.?changer\b|\binsane\b|\bmind.?blow", "hype"),
    (r"\bcomment\b.{0,30}\b(and|&) I.?ll (send|dm)|\bcomente\b.{0,30}envio", "isca-de-comentário"),
    (r"\b\d{1,3} (best |free |ai |github |open.?source |claude code )*(tools|prompts|repos(itories)?|courses|resources|skills|sites|websites)\b", "lista"),
    (r"\bliterally\b.{0,60}\b(stopped|shocked)\b", "anedota"),
]

# Alertas que pedem cuidado ao citar, mas não rebaixam o post.
NEUTROS = {"texto-traduzido", "texto-cortado"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:50] or "x-ia"


def nota(p):
    # Salvamento e resposta pesam mais que curtida: quem salva pretende voltar.
    eng = p.get("curtidas", 0) + 2 * p.get("reposts", 0) + 3 * p.get("salvos", 0) + p.get("respostas", 0)
    views = max(p.get("views", 0), 1)
    return round(eng ** 0.5 * (1 + min(eng / views, 0.2) * 5), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("coletas", nargs="+")
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--tema", default="ia")
    ap.add_argument("--min-curtidas", type=int, default=0)
    ap.add_argument("--incluir-promovidos", action="store_true")
    ap.add_argument("--saida-dir", default=str(Path.home() / "linkedin/conhecimento/x-ia"))
    a = ap.parse_args()

    # Mesmo critério do operador since: da busca: começo do dia (UTC), não o relógio de agora.
    limite = datetime.combine((datetime.now(timezone.utc) - timedelta(days=a.dias)).date(),
                              datetime.min.time(), tzinfo=timezone.utc)
    posts, consultas, fora = {}, [], {"janela": 0, "promovido": 0, "curtidas": 0}
    for arq in a.coletas:
        dado = json.loads(Path(arq).read_text())
        if isinstance(dado, str):  # string JSON gravada com aspas por fora
            dado = json.loads(dado)
        if dado.get("erro"):
            sys.exit(f"{arq}: coleta com erro ({dado['erro']}). Faça login no navegador e colete de novo.")
        consultas.append(dado.get("consulta"))
        for p in dado.get("posts", []):
            d = p.get("data")
            if d and datetime.fromisoformat(d.replace("Z", "+00:00")) < limite:
                fora["janela"] += 1
                continue
            if p.get("promovido") and not a.incluir_promovidos:
                fora["promovido"] += 1
                continue
            if p.get("curtidas", 0) < a.min_curtidas:
                fora["curtidas"] += 1
                continue
            texto = p.get("texto", "")
            p["alertas"] = sorted({r for pad, r in ISCA if re.search(pad, texto, re.I)})
            if p.get("traduzido"):
                p["alertas"].append("texto-traduzido")
            if p.get("truncado"):
                p["alertas"].append("texto-cortado")
            if not (p.get("links") or p.get("citado") or p.get("midia") or p.get("verificado")) and len(texto) < 80:
                p["alertas"].append("sem-fonte")
            p["nota"] = nota(p)
            atual = posts.get(p["url"])
            p["consultas"] = sorted(set((atual or {}).get("consultas", [])) | {dado.get("consulta") or ""})
            posts[p["url"]] = p

    ordem = sorted(posts.values(), key=lambda p: (len([x for x in p["alertas"] if x not in NEUTROS]) > 0, -p["nota"]))
    hoje = datetime.now().strftime("%Y-%m-%d")
    out = Path(a.saida_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    base = out / f"{hoje}-{slug(a.tema)}"
    base.with_suffix(".json").write_text(json.dumps(
        {"tema": a.tema, "dias": a.dias, "consultas": consultas, "descartados": fora, "posts": ordem},
        ensure_ascii=False, indent=2))

    linhas = [f"# X: {a.tema} ({hoje}, últimos {a.dias} dias)", "",
              f"Consultas: {len(consultas)}. Posts únicos: {len(ordem)}. Descartados: {fora}.", "",
              "| # | nota | @autor | data | curt | salv | resp | views | alertas | início do texto | url |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(ordem, 1):
        t = re.sub(r"\s+", " ", p.get("texto", ""))[:110].replace("|", "/")
        linhas.append(f"| {i} | {p['nota']} | @{p.get('handle','')} | {(p.get('data') or '')[:10]} | "
                      f"{p.get('curtidas',0)} | {p.get('salvos',0)} | {p.get('respostas',0)} | {p.get('views',0)} | "
                      f"{', '.join(p['alertas'])} | {t} | {p['url']} |")
    base.with_suffix(".md").write_text("\n".join(linhas) + "\n")
    print(json.dumps({"md": str(base.with_suffix('.md')), "json": str(base.with_suffix('.json')),
                      "posts": len(ordem), "descartados": fora,
                      "com_alerta": sum(1 for p in ordem if any(x not in NEUTROS for x in p["alertas"]))},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()

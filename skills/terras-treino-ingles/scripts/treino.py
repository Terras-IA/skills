#!/usr/bin/env python3
"""Motor do treino de inglês por recordação ativa. Só biblioteca padrão.

Guarda o progresso fora da skill (o repositório é público):
  $TERRAS_INGLES_DIR ou ~/.config/terras-treino-ingles/
    progresso.json   caixa, próxima revisão e histórico de cada frase
    frases.json      frases que o usuário ou o agente acrescentou
    audio/           mp3 gerados pelo comando ouvir

Repetição espaçada em caixas (Leitner). Errou: volta para a caixa 1 e fica
pendente hoje, para repetir no fim da sessão. Acertou: sobe uma caixa e a
próxima revisão vai para hoje + INTERVALO[caixa]. Acerto no mesmo dia de um
erro não pula caixa: fica na 1 e volta amanhã.

  treino.py sessao [--n 10] [--tema T[,T2]] [--nivel N] frases para treinar, SEM o inglês
  treino.py resposta ID                               inglês aceito, só depois da tentativa
  treino.py registrar ID acerto|erro [--nota TXT]     grava o resultado
  treino.py adicionar --pt .. --en .. [--en ..] --nivel N --tema T
  treino.py adicionar --arquivo novas.json            lista de {pt, en:[...], nivel, tema}
  treino.py ouvir ID [--lento]                        mp3 da frase em inglês
  treino.py status                                    resumo do progresso
"""
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BANCO = os.path.join(AQUI, "frases.json")
DIR = os.path.expanduser(os.environ.get("TERRAS_INGLES_DIR", "~/.config/terras-treino-ingles"))
PROGRESSO = os.path.join(DIR, "progresso.json")
EXTRAS = os.path.join(DIR, "frases.json")
INTERVALO = {1: 1, 2: 3, 3: 7, 4: 16, 5: 35}  # dias até a próxima revisão, por caixa
VOZ = "en-US-AndrewNeural"
EDGE_TTS = os.path.expanduser("~/.config/terras-video/venv/bin/edge-tts")
# Sobe de nível com 80% de acerto nas 20 últimas respostas do nível e 12 frases
# dele na caixa 3 ou acima (lembradas em dias diferentes, não só decoradas hoje).
SOBE_TAXA, SOBE_JANELA, SOBE_FIXADAS = 0.8, 20, 12


def hoje():
    return os.environ.get("TERRAS_INGLES_HOJE") or dt.date.today().isoformat()


def ler(caminho, padrao):
    try:
        with open(caminho, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return padrao


def gravar(caminho, dado):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dado, f, ensure_ascii=False, indent=1)
    os.replace(tmp, caminho)


def ident(pt):
    return hashlib.sha1(pt.strip().lower().encode()).hexdigest()[:8]


def frases():
    todas = {}
    for f in ler(BANCO, []) + ler(EXTRAS, []):
        f = dict(f, id=f.get("id") or ident(f["pt"]))
        todas[f["id"]] = f
    return todas


def progresso():
    return ler(PROGRESSO, {"nivel": 1, "itens": {}, "log": []})


def nivel_atual(p, fr):
    n = p["nivel"]
    log = [r for r in p["log"] if fr.get(r["id"], {}).get("nivel") == n][-SOBE_JANELA:]
    fixadas = sum(1 for i, it in p["itens"].items() if fr.get(i, {}).get("nivel") == n and it["caixa"] >= 3)
    if len(log) >= SOBE_JANELA and sum(r["ok"] for r in log) / len(log) >= SOBE_TAXA and fixadas >= SOBE_FIXADAS:
        if any(f["nivel"] == n + 1 for f in fr.values()):
            p["nivel"] = n + 1
    return p["nivel"]


def cmd_sessao(a):
    fr, p = frases(), progresso()
    nivel = a.nivel or nivel_atual(p, fr)
    temas = set(a.tema.split(",")) if a.tema else None
    ok = lambda f: not temas or f["tema"] in temas
    vencidas = sorted(
        (i for i, it in p["itens"].items() if it["proxima"] <= hoje() and i in fr and ok(fr[i])),
        key=lambda i: (p["itens"][i]["caixa"], p["itens"][i]["proxima"]))
    novas = [i for i, f in fr.items() if i not in p["itens"] and ok(f) and f["nivel"] == nivel]
    if len(vencidas) + len(novas) < a.n:  # nível esgotado: completa com o seguinte
        novas += [i for i, f in fr.items() if i not in p["itens"] and ok(f) and f["nivel"] == nivel + 1]
    escolha = vencidas[: a.n]
    escolha += novas[: a.n - len(escolha)]
    gravar(PROGRESSO, p)
    print(json.dumps({
        "nivel": nivel,
        "revisoes": len([i for i in escolha if i in p["itens"]]),
        "novas": len([i for i in escolha if i not in p["itens"]]),
        "faltam_frases": max(0, a.n - len(escolha)),
        "frases": [{"id": i, "pt": fr[i]["pt"], "nivel": fr[i]["nivel"], "tema": fr[i]["tema"],
                    "dica": fr[i].get("dica", "")} for i in escolha],
    }, ensure_ascii=False, indent=1))


def cmd_resposta(a):
    f = frases().get(a.id) or sys.exit(f"frase {a.id} não existe")
    print(json.dumps({"id": a.id, "pt": f["pt"], "en": f["en"], "nota": f.get("nota", "")}, ensure_ascii=False, indent=1))


def cmd_registrar(a):
    fr, p = frases(), progresso()
    if a.id not in fr:
        sys.exit(f"frase {a.id} não existe")
    it = p["itens"].setdefault(a.id, {"caixa": 1, "proxima": hoje(), "acertos": 0, "erros": 0, "ultimo_erro": None})
    d = dt.date.fromisoformat(hoje())
    if a.resultado == "erro":
        it.update(caixa=1, proxima=hoje(), ultimo_erro=hoje())
        it["erros"] += 1
    else:
        it["caixa"] = 1 if it["ultimo_erro"] == hoje() else min(it["caixa"] + 1, 5)
        it["proxima"] = (d + dt.timedelta(days=INTERVALO[it["caixa"]])).isoformat()
        it["acertos"] += 1
    if a.nota:
        it["nota"] = a.nota
    p["log"].append({"id": a.id, "ok": a.resultado == "acerto", "dia": hoje()})
    p["log"] = p["log"][-2000:]
    antes = p["nivel"]
    nivel_atual(p, fr)
    gravar(PROGRESSO, p)
    print(json.dumps({"id": a.id, **it, "subiu_nivel": p["nivel"] > antes, "nivel": p["nivel"]}, ensure_ascii=False))


def cmd_adicionar(a):
    novas = ler(a.arquivo, []) if a.arquivo else [{"pt": a.pt, "en": a.en, "nivel": a.nivel, "tema": a.tema}]
    extras, existentes = ler(EXTRAS, []), frases()
    feitas = []
    for f in novas:
        if not f.get("pt") or not f.get("en") or not f.get("nivel") or not f.get("tema"):
            sys.exit(f"frase incompleta (precisa pt, en, nivel, tema): {f}")
        f["en"] = f["en"] if isinstance(f["en"], list) else [f["en"]]
        f["id"] = ident(f["pt"])
        if f["id"] not in existentes:
            extras.append(f); existentes[f["id"]] = f; feitas.append(f["id"])
    gravar(EXTRAS, extras)
    print(json.dumps({"adicionadas": feitas, "repetidas": len(novas) - len(feitas)}))


def cmd_ouvir(a):
    f = frases().get(a.id) or sys.exit(f"frase {a.id} não existe")
    texto = f["en"][0]
    saida = os.path.join(DIR, "audio", f"{a.id}{'-lento' if a.lento else ''}.mp3")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    if os.path.exists(EDGE_TTS):
        subprocess.run([EDGE_TTS, "--voice", VOZ, "--rate", "-25%" if a.lento else "+0%",
                        "--text", texto, "--write-media", saida], check=True, capture_output=True)
    elif shutil.which("espeak"):
        saida = saida[:-4] + ".wav"
        subprocess.run(["espeak", "-v", "en-us", "-s", "120" if a.lento else "160", "-w", saida, texto], check=True)
    else:
        sys.exit("sem TTS: rode o setup da terras-video (edge-tts) ou instale espeak")
    print(json.dumps({"id": a.id, "en": texto, "audio": saida}, ensure_ascii=False))


def cmd_status(a):
    fr, p = frases(), progresso()
    caixas = {c: 0 for c in range(1, 6)}
    for it in p["itens"].values():
        caixas[it["caixa"]] += 1
    log = p["log"][-50:]
    dificeis = sorted(p["itens"].items(), key=lambda kv: -kv[1]["erros"])[:5]
    print(json.dumps({
        "nivel": nivel_atual(p, fr),
        "frases_no_banco": len(fr),
        "vistas": len(p["itens"]),
        "pendentes_hoje": sum(1 for it in p["itens"].values() if it["proxima"] <= hoje()),
        "por_caixa": caixas,
        "acerto_ultimas_50": round(sum(r["ok"] for r in log) / len(log), 2) if log else None,
        "dias_treinados": len({r["dia"] for r in p["log"]}),
        "mais_erradas": [{"id": i, "pt": fr[i]["pt"], "erros": it["erros"], "nota": it.get("nota", "")}
                         for i, it in dificeis if it["erros"] and i in fr],
    }, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sessao"); s.add_argument("--n", type=int, default=10)
    s.add_argument("--tema"); s.add_argument("--nivel", type=int)
    r = sub.add_parser("resposta"); r.add_argument("id")
    g = sub.add_parser("registrar"); g.add_argument("id"); g.add_argument("resultado", choices=["acerto", "erro"])
    g.add_argument("--nota")
    d = sub.add_parser("adicionar"); d.add_argument("--arquivo"); d.add_argument("--pt")
    d.add_argument("--en", action="append"); d.add_argument("--nivel", type=int); d.add_argument("--tema")
    o = sub.add_parser("ouvir"); o.add_argument("id"); o.add_argument("--lento", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()
    {"sessao": cmd_sessao, "resposta": cmd_resposta, "registrar": cmd_registrar,
     "adicionar": cmd_adicionar, "ouvir": cmd_ouvir, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()

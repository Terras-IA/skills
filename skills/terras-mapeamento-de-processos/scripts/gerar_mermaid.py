#!/usr/bin/env python3
"""Gera um diagrama Mermaid (flowchart com raias por ator) a partir do processo.json.

Uso:
  python3 gerar_mermaid.py --json processo.json --saida as-is.mmd --tipo as-is
  python3 gerar_mermaid.py --json processo-to-be.json --saida to-be.mmd --tipo to-be

Convenções: subgraph = ator; tarefa ["..."]; decisão {"...?"}; espera (["espera: ..."]);
sistema [("...")]; documento [/"..."/]; gargalos (AS-IS) e ganhos (TO-BE) destacados por classe.
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import OrderedDict

SHAPE = {
    "tarefa": '["{t}"]',
    "decisao": '{{"{t}"}}',
    "espera": '(["{t}"])',
    "sistema": '[("{t}")]',
    "documento": '[/"{t}"/]',
    "aprovacao": '["{t}"]',
}
LIMITE_ESPERA_GARGALO = 30  # % do lead time


def limpar(texto) -> str:
    t = re.sub(r"\s+", " ", str(texto or "")).strip()
    t = t.replace('"', "'").replace("`", "'")
    t = t.replace("[", "(").replace("]", ")")
    t = t.replace("{", "(").replace("}", ")")
    return t[:90]


def slug(texto) -> str:
    """ID de raia válido para o Mermaid: só [A-Za-z0-9_] (parênteses e acentos quebram o parser)."""
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    t = re.sub(r"[^A-Za-z0-9_]", "_", t).strip("_")
    t = re.sub(r"_{2,}", "_", t)
    return t or "Processo"


def fmt_min(v, corrido=False):
    """Trabalho usa dia útil (480 min); espera usa dia corrido (1440 min)."""
    if not v:
        return None
    v = float(v)
    if corrido:
        if v < 60:
            return "{:.0f} min".format(v)
        if v < 1440:
            return "{:.1f} h".format(v / 60).replace(".0", "")
        return "{:.1f} d corridos".format(v / 1440).replace(".0", "")
    if v < 60:
        return "{:.0f} min".format(v)
    if v < 480:
        return "{:.1f} h".format(v / 60).replace(".0", "")
    return "{:.1f} d".format(v / 480).replace(".0", "")


def rotulo(p: dict) -> str:
    partes = []
    if p.get("tempo_execucao_min"):
        partes.append(fmt_min(p["tempo_execucao_min"]))
    if p.get("tempo_espera_min"):
        partes.append("espera " + fmt_min(p["tempo_espera_min"], corrido=True))
    base = limpar(p.get("nome", "?"))
    if p.get("tipo") == "decisao" and not base.endswith("?"):
        base += "?"
    return base + " (" + " + ".join(partes) + ")" if partes else base


def gargalos(passos):
    trab = sum(float(p.get("tempo_execucao_min") or 0) for p in passos)
    esp = sum(float(p.get("tempo_espera_min") or 0) for p in passos)
    total = trab + esp
    limite = total * LIMITE_ESPERA_GARGALO / 100
    out = set()
    for p in passos:
        e = float(p.get("tempo_espera_min") or 0)
        if p.get("tipo") == "espera" or (e > 0 and e >= limite):
            out.add(p["id"])
        if p.get("excecoes") and p.get("tipo") in ("decisao", "aprovacao"):
            out.add(p["id"])
    return out


def ganhos(passos):
    return {p["id"] for p in passos
            if p.get("tipo") in ("sistema", "espera") or not p.get("tempo_execucao_min")}


def gerar(dados: dict, tipo: str) -> str:
    passos = dados.get("passos", [])
    if not passos:
        raise SystemExit("JSON sem passos — revise a extração antes de gerar o diagrama.")

    ids = {p["id"]: "n{}".format(i + 1) for i, p in enumerate(passos)}

    raias = OrderedDict()
    for p in passos:
        raias.setdefault(p.get("ator") or "Processo", []).append(p)

    gatilho = limpar(dados.get("gatilho", ""))[:50] or "Início"
    gatilho = gatilho.rstrip(" ,.;:-")
    linhas = ["flowchart TD"]
    linhas.append("%% Linhas tracejadas não existem: o fluxo é o caminho principal; alternativas e retrabalho estão no relatório.")
    linhas.append('    E0((("Gatilho: {}")))'.format(gatilho))

    for ator, itens in raias.items():
        nome_raia = slug(ator)
        linhas.append('    subgraph {}["{}"]'.format(nome_raia, limpar(ator)))
        # Espaçador invisível: sem ele o título da raia se sobrepõe ao primeiro nó
        linhas.append('        {}_sp[" "]'.format(nome_raia))
        for p in itens:
            shape = SHAPE.get(p.get("tipo", "tarefa"), SHAPE["tarefa"])
            linhas.append("        " + ids[p["id"]] + shape.format(t=rotulo(p)))
        linhas.append("    end")

    linhas.append("    E0 --> " + ids[passos[0]["id"]])
    for atual, prox in zip(passos, passos[1:]):
        linhas.append("    {} --> {}".format(ids[atual["id"]], ids[prox["id"]]))

    fim_txt = "Concluído (TO-BE)" if tipo == "to-be" else "Concluído"
    linhas.append('    {} --> FIM((("{}")))'.format(ids[passos[-1]["id"]], fim_txt))

    destaques = ganhos(passos) if tipo == "to-be" else gargalos(passos)
    linhas.append("    classDef invisivel fill:none,stroke:none,color:none")
    linhas.append("    class {} invisivel".format(
        ",".join(slug(ator) + "_sp" for ator in raias)))
    if destaques:
        if tipo == "to-be":
            linhas.append("    classDef ganho fill:#d9f2d9,stroke:#2a7,stroke-width:2px")
            linhas.append("    class {} ganho".format(",".join(ids[i] for i in destaques if i in ids)))
        else:
            linhas.append("    classDef gargalo fill:#ffd7d7,stroke:#c00,stroke-width:2px")
            linhas.append("    class {} gargalo".format(",".join(ids[i] for i in destaques if i in ids)))

    return "\n".join(linhas) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="processo.json -> Mermaid")
    ap.add_argument("--json", required=True)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--tipo", default="as-is", choices=["as-is", "to-be"])
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as f:
        dados = json.load(f)
    mmd = gerar(dados, args.tipo)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write(mmd)
    base = args.saida[:-4] if args.saida.endswith(".mmd") else args.saida
    print("Mermaid gerado: {} ({} passos, tipo {})".format(args.saida, len(dados.get("passos", [])), args.tipo))
    print('Para PNG/SVG: node "$SKILL_DIR/../terras-excalidraw/scripts/render.mjs" {} --out {}'.format(args.saida, base))
    print("Sem a skill vizinha: entregue o .mmd (abre em excalidraw.com e em qualquer visualizador Mermaid).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

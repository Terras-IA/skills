#!/usr/bin/env python3
"""Colheita do conhecimento do mural: junta as notas em temas, lista as pautas
que ainda não viraram post e as perguntas que deixamos nos comentários.

Uso: python3 -I colher.py [~/linkedin] [--dias 14] > notas/colheita-AAAA-MM-DD.md
Só lê; não escreve nada além da saída padrão.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta

ALIAS = {"agentes-ia": "agentes", "ia-generativa": "llm", "ia": "llm", "aspnet-core": "dotnet",
         "csharp": "dotnet", "postgresql": "banco-de-dados", "mysql": "banco-de-dados",
         "microsservicos": "arquitetura", "system-design": "arquitetura",
         "sistemas-distribuidos": "arquitetura", "appsec": "seguranca", "devsecops": "seguranca"}
FRACA = re.compile(r"fraca|gen[ée]ric", re.I)


def nota(path, raiz):
    txt = open(path, encoding="utf-8").read()
    titulo = re.search(r"^# (.+)", txt, re.M)
    tags = re.search(r"^> Tags: (.+)", txt, re.M)
    fonte = re.search(r"^> Fonte: ([^,]+)", txt, re.M)
    pautas = [re.sub(r"^\W*pauta( poss[íi]vel)?:?\**\s*", "", l.strip("- *"), flags=re.I)
              for l in txt.splitlines() if re.match(r"^- *\**pauta", l, re.I)]
    rel = os.path.relpath(path, raiz)
    return {
        "rel": rel,
        "dia": rel.split(os.sep)[1],
        "pasta": os.path.basename(os.path.dirname(path)),
        "titulo": titulo.group(1).strip() if titulo else rel,
        "autor": fonte.group(1).strip() if fonte else "?",
        "tags": sorted({ALIAS.get(t.strip(), t.strip()) for t in (tags.group(1) if tags else "").split(",") if t.strip()}),
        "pautas": [p for p in pautas if p and not FRACA.search(p)],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    raiz = os.path.expanduser(args[0] if args else "~/linkedin")
    dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 14
    corte = (date.today() - timedelta(days=dias)).isoformat()

    notas = [nota(p, raiz) for p in sorted(glob.glob(f"{raiz}/conhecimento/20*/*/conhecimento.md"))]
    pecas = ""
    for d in ("posts", "carrosseis", "banners", "videos"):
        for p in glob.glob(f"{raiz}/{d}/*.md") + glob.glob(f"{raiz}/{d}/*.json"):
            pecas += open(p, encoding="utf-8", errors="ignore").read()
    # Post é texto puro para colar e não cita a nota; o vínculo fica em conhecimento/usadas.txt
    # (uma linha por peça: "post-slug: pasta-da-nota, outra-pasta").
    reg = f"{raiz}/conhecimento/usadas.txt"
    if os.path.exists(reg):
        pecas += open(reg, encoding="utf-8").read()
    usada = {n["rel"] for n in notas if n["pasta"] in pecas}

    temas = defaultdict(list)
    for n in notas:
        for t in n["tags"]:
            temas[t].append(n)

    print(f"# Colheita do mural ({date.today().isoformat()})\n")
    print(f"- Notas: {len(notas)}; citadas em alguma peça: {len(usada)}.")
    print(f"- Pautas anotadas nas notas: {sum(len(n['pautas']) for n in notas)}.")
    print(f"- Janela de 'recente': desde {corte}.\n")

    print("## Temas maduros (3+ notas, nenhuma citada em peça)\n")
    print("| Tema | Notas | Recentes | Pautas | Autores |")
    print("|------|------:|---------:|-------:|---------|")
    maduros = []
    for t, ns in temas.items():
        livres = [n for n in ns if n["rel"] not in usada]
        if len(livres) >= 3:
            rec = sum(n["dia"] >= corte for n in livres)
            maduros.append((rec, len(livres), t, livres))
    for rec, qtd, t, ns in sorted(maduros, reverse=True)[:15]:
        autores = ", ".join(sorted({n["autor"] for n in ns})[:5])
        print(f"| {t} | {qtd} | {rec} | {sum(len(n['pautas']) for n in ns)} | {autores} |")

    print("\n## Pautas por tema maduro\n")
    for rec, qtd, t, ns in sorted(maduros, reverse=True)[:8]:
        linhas = [(n, p) for n in ns for p in n["pautas"]]
        if not linhas:
            continue
        print(f"### {t}\n")
        for n, p in linhas:
            print(f"- {p} ([{n['autor']}, {n['dia']}](../{n['rel']}))")
        print()

    perguntas = []
    for f in sorted(glob.glob(f"{raiz}/mural/mural-*.json")):
        for r in json.load(open(f, encoding="utf-8")):
            if "?" in (r.get("en") or "") and r.get("linkedin_comentado"):
                perguntas.append((os.path.basename(f)[6:16], r["autor"], r["en"], r.get("link", "")))
    print(f"## Perguntas que deixamos no LinkedIn ({len(perguntas)})\n")
    print("Resposta do autor é conhecimento de graça. Conferir a thread e anotar na nota do post.\n")
    for dia, autor, en, link in perguntas:
        print(f"- {dia} · {autor}: \"{[x for x in re.split(r'(?<=[.?!]) ', en) if '?' in x][-1]}\" {link}")


if __name__ == "__main__":
    main()

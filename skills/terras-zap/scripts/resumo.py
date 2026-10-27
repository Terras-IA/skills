#!/usr/bin/env python3
"""Resume o relatório traditional-json do ZAP em markdown, do risco maior para o menor.

Uso: resumo.py <zap.json> [--min-risco 1]
riskcode: 3 Alto, 2 Médio, 1 Baixo, 0 Informativo. confidence 0 = falso positivo marcado.
"""
import argparse
import json
from collections import defaultdict

RISCO = {"3": "Alto", "2": "Médio", "1": "Baixo", "0": "Info"}
CONF = {"4": "confirmada", "3": "alta", "2": "média", "1": "baixa", "0": "falso positivo"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("relatorio")
    p.add_argument("--min-risco", type=int, default=0)
    p.add_argument("--max-urls", type=int, default=3)
    a = p.parse_args()

    dados = json.load(open(a.relatorio))
    contagem = defaultdict(int)
    linhas = []
    for site in dados.get("site", []):
        alertas = sorted(site.get("alerts", []), key=lambda x: (-int(x["riskcode"]), x["name"]))
        for al in alertas:
            r = al["riskcode"]
            contagem[r] += 1
            if int(r) < a.min_risco or al.get("confidence") == "0":
                continue
            inst = al.get("instances", [])
            urls = []
            for i in inst[: a.max_urls]:
                extra = f" `{i['param']}`" if i.get("param") else ""
                urls.append(f"{i.get('method', '')} {i.get('uri', '')}{extra}")
            linhas.append(
                f"### [{RISCO.get(r, r)}] {al['name']} (regra {al['pluginid']}, CWE {al.get('cweid', '-')}, confiança {CONF.get(al.get('confidence'), '?')})\n"
                f"- Site: {site.get('@name')} · {al.get('count', len(inst))} ocorrência(s)\n"
                + "".join(f"- {u}\n" for u in urls)
                + f"- Correção sugerida pelo ZAP: {strip(al.get('solution', ''))[:400]}\n"
            )
    print("## Contagem por risco\n")
    for r in ("3", "2", "1", "0"):
        print(f"- {RISCO[r]}: {contagem.get(r, 0)}")
    print()
    print("\n".join(linhas) if linhas else "Nenhum alerta acima do risco mínimo.")


def strip(html):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


if __name__ == "__main__":
    main()

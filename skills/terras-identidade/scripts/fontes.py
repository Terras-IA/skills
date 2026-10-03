#!/usr/bin/env python3
"""Baixa uma familia do Google Fonts e instala em `fontes/` da identidade.

Existe porque o caminho manual (`curl` no CSS do Google Fonts e catar a URL no
`grep`) da errado de um jeito silencioso: o CSS traz **um @font-face por subset de
unicode** (latin, latin-ext, cyrillic, grego...) para cada peso, entao zipar as URLs
com os pesos na ordem em que aparecem escreve cinco subsets no mesmo arquivo e o
ultimo sobrescreve os outros. O resultado e uma fonte que instala e nao escreve
"ção" — o tipo de defeito que so aparece com o material pronto.

    python3 fontes.py "Montserrat" --pesos 400,700,800 --destino identidade/fontes
    python3 fontes.py "Inter" --pesos 400,600 --destino identidade/fontes --sem-woff2

Baixa ttf (documento, PDF, PIL) e woff2 (site), e so os subsets que cobrem
portugues (latin e latin-ext). Nao instala fonte paga nem fonte fora do Google
Fonts: para essas, colocar o arquivo na pasta a mao.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

# O CSS muda conforme o User-Agent: com UA de navegador vem woff2 (em subsets), com
# UA generico vem ttf (arquivo unico por peso). Por isso os dois pedidos.
UA_NAVEGADOR = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36")
UA_CURL = "curl/8"
SUBSETS_PT = ("latin", "latin-ext")


def pedir_css(familia: str, pesos: str, ua: str) -> str:
    url = f"https://fonts.googleapis.com/css2?family={familia.replace(' ', '+')}:wght@{pesos}&display=swap"
    r = subprocess.run(["curl", "-sL", url, "-H", f"User-Agent: {ua}"],
                       capture_output=True, text=True, timeout=60)
    if not r.stdout.strip():
        sys.exit(f"o Google Fonts nao respondeu para {familia} (sem rede, ou nome de familia errado)")
    if "400" in r.stdout and "error" in r.stdout.lower():
        sys.exit(f"familia nao encontrada no Google Fonts: {familia}")
    return r.stdout


def blocos(css: str) -> list[dict]:
    """Cada @font-face com o peso, a url e o subset que ele cobre."""
    achados = []
    for bloco in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        peso = re.search(r"font-weight:\s*(\d+)", bloco)
        url = re.search(r"src:\s*url\((https://[^)]+)\)", bloco)
        intervalo = re.search(r"unicode-range:\s*([^;]+)", bloco)
        if not (peso and url):
            continue
        achados.append({"peso": peso.group(1), "url": url.group(1),
                        "unicode_range": (intervalo.group(1) if intervalo else "").lower()})
    return achados


def cobre_portugues(intervalo: str) -> bool:
    """O subset cobre o que o portugues precisa (ate U+00FF, mais latin-ext)."""
    if not intervalo:
        return True                      # ttf unico, sem subset declarado
    return "u+0000-00ff" in intervalo or "u+0100-02af" in intervalo


def baixar(url: str, destino: str) -> int:
    subprocess.run(["curl", "-sL", url, "-o", destino], check=True, timeout=60)
    return os.path.getsize(destino)


def instalar(familia: str, pesos: str, destino: str, com_woff2: bool, com_ttf: bool) -> list[str]:
    os.makedirs(destino, exist_ok=True)
    slug = familia.lower().replace(" ", "-")
    escritos = []
    if com_ttf:
        for b in blocos(pedir_css(familia, pesos, UA_CURL)):
            caminho = os.path.join(destino, f"{slug}-{b['peso']}.ttf")
            tamanho = baixar(b["url"], caminho)
            escritos.append(f"{os.path.basename(caminho)} ({tamanho//1024} kB)")
    if com_woff2:
        blocos_css = [b for b in blocos(pedir_css(familia, pesos, UA_NAVEGADOR))
                      if cobre_portugues(b["unicode_range"])]
        # Menos arquivos distintos que pesos = o Google esta servindo a fonte
        # **variavel**: um so arquivo cobre a faixa toda. Gravar um por peso deixaria
        # arquivos identicos na pasta e quem ler depois acha que tem tres pesos.
        variavel = len({b["url"] for b in blocos_css}) < len({b["peso"] for b in blocos_css})
        vistas = set()
        for b in blocos_css:
            subset = "ext" if "u+0100-02af" in b["unicode_range"] else "latin"
            if (b["url"], subset) in vistas:
                continue
            vistas.add((b["url"], subset))
            nome = (f"{slug}-variavel-{subset}.woff2" if variavel
                    else f"{slug}-{b['peso']}-{subset}.woff2")
            caminho = os.path.join(destino, nome)
            tamanho = baixar(b["url"], caminho)
            escritos.append(f"{os.path.basename(caminho)} ({tamanho//1024} kB)"
                            + ("  [fonte variavel: a faixa de pesos esta neste arquivo]" if variavel else ""))
    return escritos


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("familia", help='nome no Google Fonts, ex.: "Montserrat"')
    ap.add_argument("--pesos", default="400,700", help="pesos separados por virgula (padrao: 400,700)")
    ap.add_argument("--destino", default="fontes", help="pasta de saida (padrao: fontes)")
    ap.add_argument("--sem-woff2", action="store_true", help="so o ttf (documento, PDF)")
    ap.add_argument("--sem-ttf", action="store_true", help="so o woff2 (site)")
    ap.add_argument("--declarar", action="store_true",
                    help="imprime o bloco `fontes` pronto para colar no identidade.json")
    args = ap.parse_args()

    pesos = args.pesos if ";" not in args.pesos else args.pesos.replace(";", ",")
    pesos = pesos if "," not in pesos else ";".join(pesos.split(","))
    escritos = instalar(args.familia, pesos, args.destino,
                        com_woff2=not args.sem_woff2, com_ttf=not args.sem_ttf)
    print(f"{args.familia} instalada em {os.path.abspath(args.destino)}:")
    for e in escritos:
        print(f"  {e}")
    print("fonte do Google Fonts e livre (OFL/Apache): pode ser embutida em site, documento e PDF. "
          "Confira a licenca na pagina da familia antes de uso comercial.")
    if args.declarar:
        slug = args.familia.lower().replace(" ", "-")
        arquivos = sorted(os.listdir(args.destino))
        ttf = [f for f in arquivos if f.startswith(slug) and f.endswith(".ttf")]
        woff = [f for f in arquivos if f.startswith(slug) and f.endswith(".woff2")]
        import json
        print("\nbloco para o identidade.json:")
        print(json.dumps({"texto": {"nome": args.familia,
                                    "arquivos": [f"{args.destino}/{f}" for f in woff or ttf],
                                    "nota": "equivalente livre do Google Fonts (OFL), declarado como "
                                            "aproximacao da fonte da peca"}},
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Renderiza um HTML em PNG no tamanho exato, pelo Chrome headless.

Serve para peca, layout, cartela e manual: qualquer coisa que se monte em HTML com
os tokens da identidade precisa sair em PNG no tamanho de publicacao, e o caminho
manual (abrir, redimensionar, capturar, cortar o vazio) erra o tamanho por alguns
pixels e deixa faixa branca embaixo.

    # uma largura so (altura sai do conteudo)
    python3 render.py layout.html --largura 1440 --saida desktop.png

    # varias de uma vez, para peca responsiva
    python3 render.py layout.html --largura 1440 390 --prefixo layout

    # altura exata, para formato de anuncio
    python3 render.py peca.html --tamanho 1080x1350 --saida story.png

Sai tambem o print de qual largura gerou qual arquivo, e o aviso quando a pagina
tem rolagem horizontal (sinal de que algo estourou a largura).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

def navegador(explicito: str | None = None) -> str:
    if explicito:
        return explicito
    for c in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser"):
        if subprocess.run(["which", c], capture_output=True).returncode == 0:
            return c
    sys.exit("sem Chrome na maquina: abra o HTML no navegador e imprima em PDF")


def recortar_vazio(png: str, fundo: tuple[int, int, int] | None = None, margem: int = 40) -> tuple[int, int]:
    """Corta a sobra embaixo comparando com a cor do canto inferior direito."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    cor_fundo = fundo or im.getpixel((im.width - 3, im.height - 3))
    limite = im.height
    for y in range(im.height - 1, 0, -1):
        linha = [im.getpixel((x, y)) for x in range(0, im.width, max(im.width // 90, 1))]
        if any(sum(abs(p[i] - cor_fundo[i]) for i in range(3)) > 24 for p in linha):
            limite = min(im.height, y + margem)
            break
    if limite < im.height:
        im = im.crop((0, 0, im.width, limite))
        im.save(png)
    return im.size


def render(html: str, saida: str, largura: int, altura: int, nav: str, escala: float,
           recortar: bool) -> tuple[int, int]:
    cmd = [nav, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           f"--force-device-scale-factor={escala}",
           f"--window-size={largura},{altura}",
           f"--screenshot={saida}", "file://" + html]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not os.path.exists(saida):
        print(r.stdout[-1500:], r.stderr[-1500:], sep="\n")
        sys.exit(f"o Chrome nao gerou {saida}")
    if recortar:
        return recortar_vazio(saida)
    from PIL import Image
    return Image.open(saida).size


def imprimir(html: str, saida: str, largura: int, altura: int, nav: str) -> None:
    """Gera PDF da pagina inteira, numa folha so do tamanho do conteudo.

    Duas coisas que fazem o PDF sair igual ao render e que o Chrome nao faz sozinho:

    - **a folha tem de ter o tamanho do conteudo.** O `--print-to-pdf` usa papel
      carta e fatia a pagina em varias folhas com faixa branca nas laterais; o
      `@page size` com a altura medida resolve.
    - **fundo colorido some na impressao** sem `print-color-adjust: exact`. Numa
      marca que vive de faixa chapada, o PDF sairia branco com texto solto.
    """
    import tempfile

    impresso = os.path.join(os.path.dirname(html),
                            os.path.splitext(os.path.basename(html))[0] + ".impresso.html")
    original = open(html, encoding="utf-8").read()

    # Breakpoint de responsividade sem `screen and` faz o Chrome imprimir na largura
    # de papel padrao (~816px) e o PDF sair na versao de celular, com metade da
    # altura do render. Avisa porque o PDF sai plausivel, so errado.
    for m in re.finditer(r"@media\s+(?!screen)([^{]*max-width[^{]*)\{", original):
        if "print" not in m.group(1):
            print(f"  ! o CSS tem `@media {m.group(1).strip()}` sem `screen and`: "
                  "no PDF isso vira a largura de papel padrao e a pagina sai na versao de celular")
            break
    ajuste = (f"html, body {{ width: {largura}px; }}\n"
              "html, * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }")

    def escrever(regra_pagina: str) -> None:
        with open(impresso, "w", encoding="utf-8") as fh:
            fh.write(original.replace("</head>", f"<style>{ajuste}\n{regra_pagina}</style></head>"))

    # 1) mede a altura no HTML **de impressao**: o `width` forcado e a ausencia de
    # rolagem mudam a quebra de linha, entao medir o HTML original dava uma altura
    # menor e o PDF saia em duas folhas com faixa branca no pe.
    escrever("")
    with tempfile.TemporaryDirectory() as tmp:
        provisorio = os.path.join(tmp, "medida.png")
        render(impresso, provisorio, largura, 6000, nav, 1.0, recortar=False)
        altura = recortar_vazio(provisorio, margem=0)[1]

    # 2) regrava com a folha do tamanho do conteudo e imprime
    escrever(f"@page {{ size: {largura}px {altura + 2}px; margin: 0; }}")
    cmd = [nav, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--no-pdf-header-footer", "--virtual-time-budget=4000",
           f"--print-to-pdf={saida}", "file://" + impresso]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not os.path.exists(saida):
        print(r.stdout[-1500:], r.stderr[-1500:], sep="\n")
        sys.exit("o Chrome nao gerou o PDF")
    try:
        import pymupdf
        doc = pymupdf.open(saida)
        paginas = doc.page_count
        tamanho = doc[0].rect
        doc.close()
        print(f"PDF em {saida}: {paginas} pagina(s), {tamanho.width:.0f}x{tamanho.height:.0f} pt "
              f"(conteudo medido: {largura}x{altura} px)")
        if paginas > 1:
            print("  ! saiu em mais de uma folha: a altura medida ficou menor que o conteudo "
                  "(revise o CSS de impressao ou aumente a margem)")
    except ImportError:
        print(f"PDF em {saida}")
    print(f"HTML de impressao em {impresso} (pode abrir no navegador para imprimir com outras opcoes)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", help="arquivo HTML a renderizar")
    ap.add_argument("--largura", type=int, nargs="+", default=None,
                    help="uma ou mais larguras (ex.: 1440 390); a altura sai do conteudo")
    ap.add_argument("--tamanho", default=None, help="largura x altura exatas (ex.: 1080x1350)")
    ap.add_argument("--pdf", default=None, help="gera PDF da pagina inteira (uma folha do tamanho do conteudo)")
    ap.add_argument("--largura-pdf", type=int, default=1440, help="largura da folha do PDF (padrao: 1440)")
    ap.add_argument("--saida", default=None, help="PNG de saida (com --tamanho ou uma --largura)")
    ap.add_argument("--prefixo", default=None, help="prefixo do nome quando ha varias larguras")
    ap.add_argument("--altura", type=int, default=4000, help="altura da janela antes do corte do vazio")
    ap.add_argument("--escala", type=float, default=1.0, help="fator de escala do dispositivo (2 = 2x)")
    ap.add_argument("--sem-cortar", action="store_true", help="mantem a altura da janela")
    ap.add_argument("--navegador", default=None)
    args = ap.parse_args()

    html = os.path.abspath(os.path.expanduser(args.html))
    if not os.path.exists(html):
        sys.exit(f"nao encontrei {html}")
    nav = navegador(args.navegador)
    pasta = os.path.dirname(html)

    if args.pdf:
        saida_pdf = os.path.abspath(os.path.expanduser(args.pdf))
        imprimir(html, saida_pdf, args.largura_pdf, 0, nav)
        return

    if args.tamanho:
        l, a = (int(v) for v in args.tamanho.lower().split("x"))
        saida = os.path.abspath(os.path.expanduser(
            args.saida or os.path.join(pasta, os.path.splitext(os.path.basename(html))[0] + f"-{l}x{a}.png")))
        tamanho = render(html, saida, l, a, nav, args.escala, recortar=not args.sem_cortar)
        print(f"{l}x{a} -> {saida} ({tamanho[0]}x{tamanho[1]})")
        return

    larguras = args.largura or [1440]
    if len(larguras) == 1 and args.saida:
        destinos = [os.path.abspath(os.path.expanduser(args.saida))]
    else:
        base = args.prefixo or os.path.splitext(os.path.basename(html))[0]
        destinos = [os.path.join(pasta, f"{base}-{l}w.png") for l in larguras]
    for largura, destino in zip(larguras, destinos):
        tamanho = render(html, destino, largura, args.altura, nav, args.escala, recortar=not args.sem_cortar)
        aviso = "  ! a largura do resultado nao bate com a pedida" if tamanho[0] != largura else ""
        print(f"{largura}w -> {destino} ({tamanho[0]}x{tamanho[1]}){aviso}")
    print("conferir o PNG antes de entregar: renderiza diferente do que o preview do editor mostra")


if __name__ == "__main__":
    main()

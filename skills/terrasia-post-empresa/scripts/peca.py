#!/usr/bin/env python3
"""Render da peça da Company Page e medição de vãos entre textos.

  render: Chrome headless em 2x (--disable-lcd-text é obrigatório no Linux:
  sem a flag o Chrome desenha franja de subcor no texto), versão exata por
  redução e preview na largura do celular (356 no feed, 380 no card).

    python3 peca.py render templates/peca-feed.html --saida banner-feed --tamanho 1200x628

  bandas: lista as faixas de linhas com texto numa região do @2x e o vão entre
  elas, para provar que nada colide (assinatura × rótulo foi o caso real).

    python3 peca.py bandas <saida>@2x.png --regiao 1900,2400,900,1256
"""
import argparse
import subprocess
import sys
from pathlib import Path

CHROME = "google-chrome"


def render(html: str, saida: str, tamanho: str) -> int:
    largura, altura = (int(v) for v in tamanho.lower().split("x"))
    origem = Path(html).resolve()
    if not origem.exists():
        print(f"html não encontrado: {origem}")
        return 1
    duas = Path(f"{saida}@2x.png")
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--disable-lcd-text",
         "--hide-scrollbars", "--force-device-scale-factor=2",
         f"--window-size={largura},{altura}",
         f"--screenshot={duas}", origem.as_uri()],
        check=True,
    )
    try:
        from PIL import Image
    except ImportError:
        print("PIL indisponível: o @2x foi gravado, a redução e o preview não")
        return 1
    im = Image.open(duas)
    if im.size != (largura * 2, altura * 2):
        print(f"aviso: render saiu {im.size[0]}x{im.size[1]}, esperado {largura*2}x{altura*2}")
    exato = Path(f"{saida}-{largura}x{altura}.png")
    im.resize((largura, altura), Image.LANCZOS).save(exato)
    largura_preview = 356 if largura >= altura else 380
    preview = Path(f"preview-mobile-{saida}.png")
    im.resize((largura_preview, round(im.height * largura_preview / im.width)),
              Image.LANCZOS).save(preview)
    print(f"ok: {exato} · {duas} · {preview} ({largura_preview}px, leitura de celular)")
    return 0


def bandas(png: str, regiao: str, limiar: int) -> int:
    try:
        from PIL import Image
    except ImportError:
        print("PIL indisponível: a medição de vãos precisa dele")
        return 1
    x0, x1, y0, y1 = (int(v) for v in regiao.split(","))
    im = Image.open(png).convert("RGB")
    px = im.load()
    linhas = []
    for y in range(y0, min(y1, im.height)):
        claro = sum(1 for x in range(x0, min(x1, im.width), 2)
                    if sum(px[x, y]) / 3 > limiar)
        if claro >= 2:
            linhas.append(y)
    grupos = []
    for y in linhas:
        if grupos and y - grupos[-1][-1] <= 6:
            grupos[-1].append(y)
        else:
            grupos.append([y])
    for i, g in enumerate(grupos):
        print(f"banda {i + 1}: y {g[0]}-{g[-1]} (altura {g[-1] - g[0] + 1}px)")
    for i in range(len(grupos) - 1):
        vao = grupos[i + 1][0] - grupos[i][-1]
        estado = "COLISAO" if vao <= 4 else ("apertado" if vao < 20 else "ok")
        print(f"vao {i + 1}->{i + 2}: {vao}px @2x = {vao / 2:.1f}px no tamanho real [{estado}]")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Render e medição da peça da Company Page")
    sub = p.add_subparsers(dest="comando", required=True)

    r = sub.add_parser("render", help="HTML -> @2x, versão exata e preview de celular")
    r.add_argument("html")
    r.add_argument("--saida", required=True, help="nome-base dos arquivos (ex.: banner-feed)")
    r.add_argument("--tamanho", required=True, help="LxA (ex.: 1200x628 ou 1080x1350)")

    b = sub.add_parser("bandas", help="faixas de texto e vãos numa região do PNG")
    b.add_argument("png")
    b.add_argument("--regiao", required=True, help="x0,x1,y0,y1 em pixels do @2x")
    b.add_argument("--limiar", type=int, default=60, help="brilho médio que conta como texto")

    a = p.parse_args()
    if a.comando == "render":
        return render(a.html, a.saida, a.tamanho)
    return bandas(a.png, a.regiao, a.limiar)


if __name__ == "__main__":
    sys.exit(main())

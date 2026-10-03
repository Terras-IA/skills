#!/usr/bin/env python3
"""Gera o livro de colorir derivado do livro ilustrado.

Uso: python3 colorir.py <pasta-do-livro>

Deriva a line-art de cada cena (só o SVG, sem texto sobreposto), sobrepõe badge,
narração e balões originais e monta colorir/livro-colorir.pdf.
No modo assistido, usa as line-arts imagens-colorir/pagina-NN.png se existirem.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageFilter

LIVRO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
PAGINAS = LIVRO / "paginas"
COLORIR = LIVRO / "colorir"
ESCONDER = (".badge,.narra,.balao,.pensamento,.bolinha,.card,"
            ".titulo,.swoosh,.poster{display:none!important}")
CENA_RE = re.compile(r'<div class="cena">.*?</svg></div>', re.DOTALL)


def chrome_screenshot(html: pathlib.Path, saida: pathlib.Path) -> None:
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox",
         f"--user-data-dir={tempfile.mkdtemp()}", "--window-size=1200,1800",
         "--force-device-scale-factor=2", "--virtual-time-budget=4000",
         f"--screenshot={saida}", f"file://{html}"],
        check=True, capture_output=True)
    if not saida.exists():
        raise RuntimeError(f"Chrome não gerou {saida}")


def para_line_art(foto: pathlib.Path, saida: pathlib.Path) -> None:
    """Foto da cena (cores planas) → contorno preto em fundo branco."""
    img = Image.open(foto).convert("L")
    bordas = img.filter(ImageFilter.FIND_EDGES).point(lambda p: 0 if p > 35 else 255)
    bordas = bordas.filter(ImageFilter.MinFilter(3))   # engrossa o traço
    bordas = bordas.filter(ImageFilter.MaxFilter(3))   # limpa pontos isolados
    saida.parent.mkdir(parents=True, exist_ok=True)
    bordas.convert("L").save(saida)


def main() -> None:
    htmls = sorted(PAGINAS.glob("pagina-*.html"))
    assert htmls, f"nenhuma página em {PAGINAS}"
    COLORIR.mkdir(exist_ok=True)
    (COLORIR / "paginas").mkdir(exist_ok=True)

    for html in htmls:
        nome = html.stem  # pagina-00-capa, pagina-01…
        art = COLORIR / "art" / f"{nome}.png"
        manual = LIVRO / "imagens-colorir" / f"{nome}.png"

        if manual.exists():
            shutil.copy(manual, art)
            print(f"✓ art/{nome}.png (line-art fornecida)")
        else:
            tmp = PAGINAS / f".__tmp_cena_{nome}.html"
            tmp.write_text(html.read_text(encoding="utf-8").replace(
                "</head>", f"<style>{ESCONDER}</style></head>"), encoding="utf-8")
            with tempfile.TemporaryDirectory() as td:
                foto = pathlib.Path(td) / "cena.png"
                chrome_screenshot(tmp, foto)
                para_line_art(foto, art)
            tmp.unlink()
            print(f"✓ art/{nome}.png (line-art derivada)")

        html_colorir = html.read_text(encoding="utf-8")
        html_colorir = CENA_RE.sub(
            f'<div class="cena"><img class="fundo" src="../art/{nome}.png"></div>',
            html_colorir, count=1)
        html_colorir = html_colorir.replace(
            'href="livro.css"', 'href="../../paginas/livro.css"')
        (COLORIR / "paginas" / html.name).write_text(html_colorir, encoding="utf-8")

    # renderiza as páginas de colorir e monta o PDF
    png_dir = COLORIR / "png"
    png_dir.mkdir(exist_ok=True)
    for pg in sorted((COLORIR / "paginas").glob("pagina-*.html")):
        chrome_screenshot(pg, png_dir / f"{pg.stem}.png")
        print(f"✓ colorir/png/{pg.stem}.png")

    pgs = [Image.open(p).convert("RGB") for p in sorted(png_dir.glob("*.png"))]
    saida = COLORIR / "livro-colorir.pdf"
    pgs[0].save(saida, save_all=True, append_images=pgs[1:], resolution=150.0, quality=92)
    print(f"✓ {saida} ({len(pgs)} páginas)")


if __name__ == "__main__":
    main()

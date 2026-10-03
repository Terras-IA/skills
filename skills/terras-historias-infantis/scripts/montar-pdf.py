#!/usr/bin/env python3
"""Monta livro.pdf a partir dos PNGs em <pasta-do-livro>/png/ (ordem alfabética)."""
import sys, pathlib
from PIL import Image

livro = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
pngs = sorted((livro / "png").glob("*.png"))
assert pngs, f"nenhum PNG em {livro}/png/"
paginas = [Image.open(p).convert("RGB") for p in pngs]
saida = livro / "livro.pdf"
paginas[0].save(saida, save_all=True, append_images=paginas[1:], resolution=150.0, quality=92)
print(f"✓ {saida} ({len(paginas)} páginas)")

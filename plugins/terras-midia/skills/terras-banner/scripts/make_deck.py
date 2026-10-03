#!/usr/bin/env python3
"""Deck PDF multipagina: manifest JSON com specs de slide.

Uso:
    python3 make_deck.py --manifest deck.json --out deck.pdf [--dpi 144]

Manifest:
    {
      "nome": "Como eu desenho pelo raio de explosao",   # OBRIGATORIO, tom pessoal
      "autor": "Everton Lima",                            # opcional, default Everton Lima
      "size": "1080x1440",            # tamanho dos slides (padrao: retrato 3:4)
      "slides": [
        { "headline": "...", "sub": "...", "kick": "...", "bg": "...", ... },
        ...
      ]
    }

O `nome` e obrigatorio e sempre em tom pessoal (primeira pessoa, no estilo das
manchetes): vira o titulo do PDF (metadado), que e o que o LinkedIn mostra no
documento. Nome tecnico de arquivo nao serve como titulo.

Cada item de "slides" e um spec igual ao do make_banner.py, sem os campos
"out", "html" e "size" (aqui eles saem do manifest). O --check roda por slide
e falha se algum estourar ou sobrepor. Os PNGs temporarios vao para o mesmo
diretorio do --out e sao removidos no fim.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
MAKE_BANNER = os.path.join(SKILL_DIR, "make_banner.py")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=float, default=144)
    ap.add_argument(
        "--keep-pngs", action="store_true",
        help="mantem os PNGs de cada slide ao lado do PDF (nome-01.png, ...)",
    )
    a = ap.parse_args()

    with open(a.manifest, encoding="utf-8") as fh:
        manifest = json.load(fh)
    size = manifest.get("size", "1080x1440")  # padrao retrato (3:4) desde 23/09
    nome = (manifest.get("nome") or "").strip()
    if not nome:
        sys.exit(
            "manifest sem `nome`: o PDF precisa de um nome em tom pessoal "
            "(ex.: \"Como eu desenho pelo raio de explosao\"), que vira o "
            "titulo do documento. Nome tecnico de arquivo nao serve."
        )
    autor = manifest.get("autor") or "Everton Lima"
    slides = manifest.get("slides", [])
    if not slides:
        sys.exit("manifest sem slides")

    out_dir = os.path.dirname(os.path.abspath(a.out)) or "."
    pngs = []
    tmpdir = tempfile.mkdtemp(prefix="deck-", dir=out_dir)
    try:
        for i, slide in enumerate(slides):
            spec = dict(slide)
            spec["size"] = size
            spec["out"] = os.path.join(tmpdir, f"slide-{i:02d}.png")
            spec["html"] = os.path.join(tmpdir, f"slide-{i:02d}.html")
            spec_path = os.path.join(tmpdir, f"slide-{i:02d}.json")
            with open(spec_path, "w", encoding="utf-8") as fh:
                json.dump(spec, fh, ensure_ascii=False, indent=2)
            proc = subprocess.run(
                [sys.executable, MAKE_BANNER, "--spec", spec_path, "--check"],
                capture_output=True, text=True,
            )
            if proc.returncode != 0:
                sys.exit(
                    f"slide {i} reprovado no check:\n{proc.stdout}\n{proc.stderr}"
                )
            pngs.append(spec["out"])

        imgs = [Image.open(p).convert("RGB") for p in pngs]
        imgs[0].save(
            a.out, "PDF", save_all=True,
            append_images=imgs[1:], resolution=a.dpi,
            title=nome, author=autor,
        )
        print(f"{a.out}: {len(imgs)} paginas {size}px a {a.dpi} dpi")
        print(f'  nome do PDF: "{nome}" (autor: {autor})')

        if a.keep_pngs:
            base = os.path.splitext(a.out)[0]
            for i, p in enumerate(pngs):
                dest = f"{base}-{i + 1:02d}.png"
                Image.open(p).save(dest)
                print(f"  slide {i + 1}: {dest}")
    finally:
        for p in pngs:
            try:
                os.remove(p)
            except OSError:
                pass


if __name__ == "__main__":
    main()

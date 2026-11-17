#!/usr/bin/env python3
"""Fotografa cada passo de uma lição montada (Chrome headless) e junta numa folha de contato.

Serve para o agente revisar a cena com Read antes de entregar: nó encavalado,
rótulo cortado, ligação atravessando caixa, métrica que não mudou.

Uso:
  python3 capturar.py pagina.html --licao <id> [-o pasta] [--largura 1440 --altura 900] [--escuro]
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHROMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def chrome():
    for c in CHROMES:
        if shutil.which(c):
            return c
    sys.exit(json.dumps({"status": "erro", "erro": "Chrome/Chromium não encontrado"}))


def passos_da_licao(html, licao):
    m = re.search(r"window\.__CURSO__ = (.*?);</script>", html, re.S)
    curso = json.loads(m.group(1).replace("<\\/", "</"))
    for mod in curso.get("modulos", []):
        for l in mod.get("licoes", []):
            if l.get("id") == licao:
                return len(l.get("passos", []))
    ids = [l.get("id") for mod in curso.get("modulos", []) for l in mod.get("licoes", [])]
    sys.exit(json.dumps({"status": "erro", "erro": f"lição '{licao}' não existe", "licoes": ids}, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pagina")
    ap.add_argument("--licao", required=True)
    ap.add_argument("-o", "--pasta")
    ap.add_argument("--largura", type=int, default=1440)
    ap.add_argument("--altura", type=int, default=900)
    ap.add_argument("--escuro", action="store_true")
    a = ap.parse_args()
    pag = Path(a.pagina).resolve()
    n = passos_da_licao(pag.read_text(encoding="utf-8"), a.licao)
    pasta = Path(a.pasta or pag.parent / f"capturas-{a.licao}")
    pasta.mkdir(parents=True, exist_ok=True)
    exe = chrome()
    fotos = []
    with tempfile.TemporaryDirectory() as perfil:
        for i in range(1, n + 1):
            out = pasta / f"passo-{i:02d}.png"
            cmd = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={perfil}",
                   f"--window-size={a.largura},{a.altura}", "--virtual-time-budget=2500", f"--screenshot={out}"]
            if a.escuro:
                cmd.append("--force-dark-mode")
            cmd.append(f"{pag.as_uri()}?captura=1#{a.licao}-p{i}")
            subprocess.run(cmd, capture_output=True, timeout=60)
            if out.exists():
                fotos.append(out)
    res = {"status": "ok" if len(fotos) == n else "parcial", "passos": n, "fotos": [str(f) for f in fotos]}
    try:
        from PIL import Image
        ims = [Image.open(f).convert("RGB") for f in fotos]
        if ims:
            w = 720
            ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
            col = 2
            lin = (len(ims) + col - 1) // col
            h = ims[0].height
            folha = Image.new("RGB", (w * col + 10 * (col - 1), h * lin + 10 * (lin - 1)), "white")
            for k, im in enumerate(ims):
                folha.paste(im, ((k % col) * (w + 10), (k // col) * (h + 10)))
            fp = pasta / "folha.jpg"
            folha.save(fp, quality=82)
            res["folha"] = str(fp)
    except ImportError:
        res["aviso"] = "Pillow ausente: sem folha de contato, leia as fotos uma a uma"
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

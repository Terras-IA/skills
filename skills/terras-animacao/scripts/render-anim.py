#!/usr/bin/env python3
"""Render de animação a partir de um HTML dirigido por `?t=` (ms).

O HTML recebe o instante em `?t=1234` e desenha o frame daquele momento (JS
determinístico, sem depender de tempo real). Este script:

  quadro: captura um frame só (iteração e inspeção)
    python3 render-anim.py quadro anim.html 2400 quadro.png --tamanho 1200x628

  animar: captura a linha do tempo inteira, monta MP4 + GIF (loop) e a capa
    python3 render-anim.py animar anim.html --saida anim-mapeamento \\
      --tamanho 1200x628 --duracao 6400 --fps 25 --capa 5200

  bandas: mede os vãos entre faixas de texto num quadro (prova que nada colide)
    python3 render-anim.py bandas <png>@2x.png --regiao 1900,2400,900,1256

Convenções: Chrome headless em 2x com --disable-lcd-text (sem a flag o texto
sai com franja no Linux), redução para o tamanho exato via PIL, e ffmpeg para
o MP4 (H.264, silencioso) e o GIF (paleta, para o feed que autoplaya e loopa).
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

CHROME = "google-chrome"


def capturar(html: Path, t: int, destino_2x: Path, largura: int, altura: int) -> None:
    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--disable-lcd-text",
         "--hide-scrollbars", "--force-device-scale-factor=2",
         "--virtual-time-budget=2500",
         f"--window-size={largura},{altura}",
         f"--screenshot={destino_2x}",
         f"{html.resolve().as_uri()}?t={t}"],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def reduzir(origem: Path, destino: Path, largura: int, altura: int) -> None:
    im = Image.open(origem).convert("RGB")
    if im.size != (largura * 2, altura * 2):
        print(f"aviso: render saiu {im.size[0]}x{im.size[1]}, esperado {largura*2}x{altura*2}")
    im.resize((largura, altura), Image.LANCZOS).save(destino)


def cmd_quadro(a) -> int:
    largura, altura = (int(v) for v in a.tamanho.lower().split("x"))
    html = Path(a.html)
    destino = Path(a.saida)
    duas = destino.with_name(destino.stem + "@2x.png")
    capturar(html, a.t, duas, largura, altura)
    reduzir(duas, destino, largura, altura)
    if not a.manter_2x:
        duas.unlink()
    print(f"ok: {destino} (t={a.t}ms)")
    return 0


def cmd_animar(a) -> int:
    largura, altura = (int(v) for v in a.tamanho.lower().split("x"))
    html = Path(a.html)
    saida = Path(a.saida)
    pasta = Path(a.pasta) if a.pasta else saida.parent / "frames"
    if pasta.exists():
        shutil.rmtree(pasta)
    pasta.mkdir(parents=True)

    passo = round(1000 / a.fps)
    tempos = list(range(0, a.duracao, passo))
    for i, t in enumerate(tempos):
        duas = pasta / f"f{i:04d}-2x.png"
        capturar(html, t, duas, largura, altura)
        reduzir(duas, pasta / f"f{i:04d}.png", largura, altura)
        duas.unlink()
    print(f"{len(tempos)} frames em {pasta}")

    mp4 = saida.with_suffix(".mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
                    "-i", str(pasta / "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17",
                    "-preset", "slow", "-movflags", "+faststart", str(mp4)], check=True)

    gif = saida.with_suffix(".gif")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4),
                    "-vf", f"fps={a.fps_gif},scale={largura}:-1:flags=lanczos,"
                           "split[a][b];[a]palettegen=max_colors=160[p];"
                           "[b][p]paletteuse=dither=bayer:bayer_scale=3",
                    "-loop", "0", str(gif)], check=True)

    if a.capa is not None:
        capa = saida.with_name(saida.name + f"-capa-{largura}x{altura}.png")
        duas = saida.with_name(saida.name + "-capa-2x.png")
        capturar(html, a.capa, duas, largura, altura)
        reduzir(duas, capa, largura, altura)
        duas.unlink()
        print(f"capa: {capa} (t={a.capa}ms)")

    for arquivo in (mp4, gif):
        print(f"{arquivo}: {arquivo.stat().st_size/1024:.0f} KB")
    return 0


def cmd_bandas(a) -> int:
    try:
        from PIL import Image
    except ImportError:
        print("PIL indisponível: a medição de vãos precisa dele")
        return 1
    x0, x1, y0, y1 = (int(v) for v in a.regiao.split(","))
    im = Image.open(a.png).convert("RGB")
    px = im.load()
    linhas = []
    for y in range(y0, min(y1, im.height)):
        claro = sum(1 for x in range(x0, min(x1, im.width), 2)
                    if sum(px[x, y]) / 3 > a.limiar)
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
    p = argparse.ArgumentParser(description="Render de animação por frames (?t=)")
    sub = p.add_subparsers(dest="comando", required=True)

    q = sub.add_parser("quadro", help="captura um frame só")
    q.add_argument("html")
    q.add_argument("t", type=int)
    q.add_argument("saida")
    q.add_argument("--tamanho", default="1200x628")
    q.add_argument("--manter-2x", action="store_true")

    n = sub.add_parser("animar", help="frames + mp4 + gif (+ capa)")
    n.add_argument("html")
    n.add_argument("--saida", required=True, help="nome-base (sem extensão)")
    n.add_argument("--tamanho", default="1200x628")
    n.add_argument("--duracao", type=int, default=6400, help="ms")
    n.add_argument("--fps", type=int, default=25)
    n.add_argument("--fps-gif", type=int, default=14)
    n.add_argument("--capa", type=int, default=None, help="instante da capa estática (ms)")
    n.add_argument("--pasta", default=None)

    b = sub.add_parser("bandas", help="faixas de texto e vãos numa região do PNG")
    b.add_argument("png")
    b.add_argument("--regiao", required=True, help="x0,x1,y0,y1 em pixels do @2x")
    b.add_argument("--limiar", type=int, default=60, help="brilho médio que conta como texto")

    a = p.parse_args()
    if a.comando == "quadro":
        return cmd_quadro(a)
    if a.comando == "animar":
        return cmd_animar(a)
    return cmd_bandas(a)


if __name__ == "__main__":
    sys.exit(main())

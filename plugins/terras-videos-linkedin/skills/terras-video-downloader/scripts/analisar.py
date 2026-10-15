#!/usr/bin/env python3
"""Prepara um vídeo baixado para o agente olhar: ficha técnica e folhas de quadros.

Precisa de ffmpeg e ffprobe no PATH (saída 3 se faltarem).

Uso:
  analisar.py VIDEO [-o PASTA] [--passo SEG] [--json]

Gera em PASTA (padrão: <video>-analise/):
  folha01.jpg, folha02.jpg...  grade 2x3, um quadro a cada --passo s, com o tempo
                               carimbado no canto
  ficha.json                   duração, resolução, fps, áudio (e se é mudo), cortes
"""
import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys

POR_FOLHA = 6  # grade 2x3


def rodar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video")
    ap.add_argument("-o", "--pasta")
    ap.add_argument("--passo", type=float, help="segundos entre quadros (padrão: até 4 folhas)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    faltando = [x for x in ("ffmpeg", "ffprobe") if not shutil.which(x)]
    if faltando:
        print(json.dumps({"status": "falha", "kind": "ferramenta_ausente", "faltando": faltando}))
        return 3

    p = json.loads(rodar(["ffprobe", "-v", "error", "-print_format", "json",
                          "-show_format", "-show_streams", a.video]).stdout or "{}")
    if not p.get("format"):
        print(json.dumps({"status": "falha", "kind": "entrada", "erro": "ffprobe não leu o arquivo"}))
        return 1
    dur = float(p["format"]["duration"])
    v = next((s for s in p["streams"] if s["codec_type"] == "video"), {})
    au = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    num, den = (v.get("avg_frame_rate") or "0/1").split("/")
    ficha = {"arquivo": os.path.abspath(a.video), "duracao_s": round(dur, 2),
             "resolucao": f"{v.get('width')}x{v.get('height')}",
             "fps": round(int(num) / int(den or 1), 2) if int(den or 1) else None,
             "audio": None}

    if au:
        r = rodar(["ffmpeg", "-hide_banner", "-i", a.video, "-vn", "-af", "volumedetect",
                   "-f", "null", "-"]).stderr
        m = re.search(r"mean_volume: (-?[\d.]+) dB", r)
        media = float(m.group(1)) if m else None
        ficha["audio"] = {"codec": au.get("codec_name"), "volume_medio_db": media,
                          "mudo": media is not None and media < -60}

    r = rodar(["ffmpeg", "-hide_banner", "-i", a.video, "-an", "-vf",
               "select='gt(scene,0.3)',showinfo", "-f", "null", "-"]).stderr
    ficha["cortes_s"] = [round(float(t), 1) for t in re.findall(r"pts_time:([\d.]+)", r)]

    passo = a.passo or max(2.0, math.ceil(dur / (POR_FOLHA * 4)))
    pasta = a.pasta or os.path.splitext(a.video)[0] + "-analise"
    os.makedirs(pasta, exist_ok=True)
    carimbo = ("drawtext=text='%{pts\\:hms}':x=12:y=12:fontsize=30:"
               "fontcolor=yellow:box=1:boxcolor=black@0.7:boxborderw=6")
    r = rodar(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.video, "-vf",
               f"fps=1/{passo},{carimbo},scale=960:-2,tile=2x3",
               os.path.join(pasta, "folha%02d.jpg")])
    if r.returncode:  # ffmpeg sem drawtext: folha sem carimbo, a ordem dá o tempo
        rodar(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", a.video, "-vf",
               f"fps=1/{passo},scale=960:-2,tile=2x3", os.path.join(pasta, "folha%02d.jpg")])
        ficha["carimbo"] = False
    ficha["passo_s"] = passo
    ficha["folhas"] = sorted(os.path.join(os.path.abspath(pasta), f)
                             for f in os.listdir(pasta) if f.startswith("folha"))
    ficha["status"] = "ok" if ficha["folhas"] else "falha"
    with open(os.path.join(pasta, "ficha.json"), "w") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)

    print(json.dumps(ficha, ensure_ascii=False, indent=2) if a.json else
          f"{ficha['duracao_s']} s, {ficha['resolucao']}, {len(ficha['folhas'])} folha(s) em {pasta}")
    return 0 if ficha["folhas"] else 1


if __name__ == "__main__":
    sys.exit(main())

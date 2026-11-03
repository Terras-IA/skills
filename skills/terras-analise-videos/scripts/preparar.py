#!/usr/bin/env python3
"""Prepara uma pasta de vídeos para análise: metadados, folha de quadros e transcrição.

Uso (com o Python do venv do faster-whisper):
  python preparar.py PASTA_VIDEOS SAIDA [--beam 1] [--threads 12] [--ext mp4,mov,webm]

Para cada vídeo grava SAIDA/_dados/<id>/:
  metadados.json   ffprobe + origem, md5, orientação real (rotação aplicada)
  quadros.jpg      16 quadros espaçados, grade 4x4
  transcricao.json idioma, prob, sem_fala, segmentos
  transcricao.txt  uma linha por segmento, com o segundo de início

Retoma de onde parou: pula vídeo que já tem transcricao.json.
"""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("videos")
ap.add_argument("saida")
ap.add_argument("--beam", type=int, default=1, help="1 = greedy, ~2x mais rápido que 5 com CPU disputada")
ap.add_argument("--threads", type=int, default=12)
ap.add_argument("--ext", default="mp4,mov,webm,mkv,3gp")
ap.add_argument("--modelo", default="large-v3-turbo")
a = ap.parse_args()

src, dados = Path(a.videos).resolve(), Path(a.saida).resolve() / "_dados"
dados.mkdir(parents=True, exist_ok=True)
exts = {"." + e.strip().lower() for e in a.ext.split(",")}
videos = sorted(p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in exts)
if not videos:
    sys.exit(f"nenhum vídeo ({a.ext}) em {src}")

from faster_whisper import WhisperModel  # import tardio: falha cedo se a pasta estiver vazia
model = WhisperModel(a.modelo, device="cpu", compute_type="int8", cpu_threads=a.threads)


def run(*args):
    return subprocess.run(args, capture_output=True, text=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def orientacao(probe):
    v = next((s for s in probe.get("streams", []) if s.get("codec_type") == "video"), {})
    w, h = v.get("width", 0), v.get("height", 0)
    rot = 0
    for sd in v.get("side_data_list", []):
        rot = int(sd.get("rotation", rot) or rot)
    rot = int(v.get("tags", {}).get("rotate", rot) or rot)
    if abs(rot) in (90, 270):
        w, h = h, w
    return {"largura": w, "altura": h, "rotacao": rot, "vertical": h > w}


for i, v in enumerate(videos, 1):
    d = dados / v.stem
    d.mkdir(exist_ok=True)
    if (d / "transcricao.json").exists():
        continue
    t0 = time.time()
    probe = json.loads(run("ffprobe", "-v", "error", "-print_format", "json",
                           "-show_format", "-show_streams", str(v)).stdout or "{}")
    dur = float(probe.get("format", {}).get("duration", 0) or 0)
    tags = json.dumps(probe.get("format", {}).get("tags", {})).lower()
    probe["_analise"] = {"origem": str(v), "md5": md5(v), **orientacao(probe),
                         # gravação de tela do celular de quem salvou, não o arquivo do autor
                         "gravacao_local_provavel": any(k in tags for k in ("com.android", "manufacturer", "motorola", "samsung", "xiaomi"))}
    (d / "metadados.json").write_text(json.dumps(probe, indent=1, ensure_ascii=False))

    fps = 16 / dur if dur > 0 else 1
    run("ffmpeg", "-v", "error", "-y", "-i", str(v), "-vf",
        f"fps={fps:.5f},scale=360:-2,tile=4x4:padding=4", "-frames:v", "1", "-q:v", "4", str(d / "quadros.jpg"))

    wav = d / "audio.wav"
    run("ffmpeg", "-v", "error", "-y", "-i", str(v), "-vn", "-ac", "1", "-ar", "16000", str(wav))
    res = {"arquivo": v.name, "duracao_s": dur, "idioma": None, "prob_idioma": None, "sem_fala": True, "segmentos": []}
    if wav.exists() and wav.stat().st_size > 1000:
        try:
            segs, info = model.transcribe(str(wav), vad_filter=True, beam_size=a.beam,
                                          vad_parameters={"min_silence_duration_ms": 500, "speech_pad_ms": 200},
                                          condition_on_previous_text=False)
            res["idioma"], res["prob_idioma"] = info.language, round(info.language_probability, 3)
            res["segmentos"] = [{"ini": round(s.start, 1), "fim": round(s.end, 1), "texto": s.text.strip(),
                                 "logprob": round(s.avg_logprob, 2)} for s in segs if s.start < dur + 0.5]
            palavras = sum(len(s["texto"].split()) for s in res["segmentos"])
            # prob < 0,65 ou quase nenhuma palavra = sem fala (música, texto na tela); o texto é alucinação
            res["sem_fala"] = res["prob_idioma"] < 0.65 or palavras < 6
        except Exception as e:  # um vídeo ruim não derruba o lote
            res["erro"] = str(e)
        wav.unlink()
    else:
        res["erro"] = "sem faixa de áudio"
    (d / "transcricao.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    (d / "transcricao.txt").write_text(
        ("[SEM FALA: o texto abaixo, se houver, é alucinação do transcritor]\n" if res["sem_fala"] else "")
        + "\n".join(f"[{s['ini']:.0f}s] {s['texto']}" for s in res["segmentos"]))
    print(f"{i}/{len(videos)} {v.name} {dur:.0f}s idioma={res['idioma']} sem_fala={res['sem_fala']} {time.time()-t0:.0f}s", flush=True)
print("PREPARO FIM", flush=True)

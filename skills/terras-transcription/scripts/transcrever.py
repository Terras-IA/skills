#!/usr/bin/env python3
"""Transcreve um audio local com faster-whisper, sem API e sem enviar audio para fora.

Gera tres arquivos a partir de --saida:
  BASE.json  segmentos completos, com timestamps por palavra e metricas de confianca
  BASE.txt   uma linha por segmento, com timestamp (material de conferencia)
  BASE.md    transcricao corrida, em paragrafos, pronta para ler

Uso:
  transcrever.py AUDIO --saida BASE [--modelo large-v3-turbo] [--idioma auto]
                       [--prompt TEXTO] [--threads 16] [--sem-vad]

Decisoes que importam (ver SKILL.md):
  --idioma auto e o padrao de proposito. Fixar o idioma errado faz o Whisper
  TRADUZIR em vez de transcrever, e o texto sai plausivel e falso.
  --prompt e vazio por padrao: prompt com vocabulario enviesa a decodificacao e
  pode fazer o modelo "ouvir" termos que nao foram ditos.
"""
import argparse
import json
import os
import sys
import time


def fmt_ts(seg):
    return f"{int(seg // 60):02d}:{seg % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--saida", required=True, help="caminho base, sem extensao")
    ap.add_argument("--modelo", default="large-v3-turbo")
    ap.add_argument("--idioma", default="auto", help="auto (padrao), pt, en, ...")
    ap.add_argument("--prompt", default=None, help="prompt inicial; omitir e o recomendado")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--sem-vad", action="store_true")
    ap.add_argument("--tipo-calculo", default="int8")
    args = ap.parse_args()

    from faster_whisper import WhisperModel

    t0 = time.time()
    modelo = WhisperModel(args.modelo, device="cpu", compute_type=args.tipo_calculo,
                          cpu_threads=args.threads)
    print(f"[i] modelo {args.modelo} carregado em {time.time() - t0:.0f}s", flush=True)

    kwargs = dict(
        beam_size=5,
        word_timestamps=True,
        vad_filter=not args.sem_vad,
        condition_on_previous_text=False,
        initial_prompt=args.prompt,
    )
    if args.sem_vad is False:
        kwargs["vad_parameters"] = dict(min_silence_duration_ms=500, speech_pad_ms=200)
    if args.idioma != "auto":
        kwargs["language"] = args.idioma

    t0 = time.time()
    segmentos_iter, info = modelo.transcribe(args.audio, **kwargs)
    idioma = info.language
    print(f"[i] idioma detectado: {idioma} (prob {info.language_probability:.3f}) | "
          f"duracao {info.duration:.0f}s", flush=True)

    registros = []
    for i, s in enumerate(segmentos_iter):
        registros.append({
            "i": i,
            "start": round(s.start, 2),
            "end": round(s.end, 2),
            "text": s.text.strip(),
            "avg_logprob": round(s.avg_logprob, 4),
            "no_speech_prob": round(s.no_speech_prob, 4),
            "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2),
                       "p": round(w.probability, 3)} for w in (s.words or [])],
        })
        if i % 50 == 0:
            print(f"[i] {i} segmentos, t={s.end:.0f}s, {time.time() - t0:.0f}s decorridos",
                  flush=True)

    if not registros:
        print("[!] nenhum segmento: o audio pode ser so silencio. "
              "Confira com preflight.py.", file=sys.stderr)
        return 2

    falado = sum(r["end"] - r["start"] for r in registros)
    with open(f"{args.saida}.json", "w", encoding="utf-8") as f:
        json.dump({"audio": args.audio, "modelo": args.modelo, "language": idioma,
                   "language_probability": round(info.language_probability, 4),
                   "duracao": round(info.duration, 2),
                   "com_prompt": bool(args.prompt),
                   "segments": registros}, f, ensure_ascii=False, indent=1)

    with open(f"{args.saida}.txt", "w", encoding="utf-8") as f:
        for r in registros:
            f.write(f"[{r['start']:8.2f} -> {r['end']:8.2f}] {r['text']}\n")

    with open(f"{args.saida}.md", "w", encoding="utf-8") as f:
        f.write(f"# Transcricao — {os.path.basename(args.audio)}\n\n")
        f.write(f"Idioma: {idioma} ({info.language_probability:.3f}) · "
                f"duracao do audio: {fmt_ts(info.duration)} · "
                f"fala detectada: {fmt_ts(falado)} · modelo: {args.modelo}\n")
        if args.prompt:
            f.write("\n> Gerada COM prompt inicial: termos do prompt podem ter sido "
                    "induzidos. Conferir antes de citar.\n")
        f.write("\n")
        for r in registros:
            f.write(f"**[{fmt_ts(r['start'])}]** {r['text']}\n\n")

    baixa = [r for r in registros if r["avg_logprob"] < -0.9]
    print(f"[ok] {len(registros)} segmentos | fala {falado:.0f}s de {info.duration:.0f}s | "
          f"{time.time() - t0:.0f}s decorridos")
    print(f"[ok] escritos: {args.saida}.json / .txt / .md")
    print(f"[i] segmentos com baixa confianca (avg_logprob < -0.9): {len(baixa)}")
    if baixa:
        print("    conferir estes primeiro:")
        for r in baixa[:10]:
            print(f"    [{fmt_ts(r['start'])}] lp={r['avg_logprob']:.2f} {r['text'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

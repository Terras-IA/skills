#!/usr/bin/env python3
"""Pre-voo de um audio antes de transcrever: formato, mapa de volume, onde ha fala
de verdade e qual e o idioma — com o teste de confianca que evita o erro classico.

Uso:
  preflight.py AUDIO [--passo 240] [--amostras 3]

Por que existe: transcrever as cegas custa tempo e esconde duas armadilhas.
  1. Exportacao de reuniao costuma ter silencio longo no inicio e no fim; o mapa de
     volume mostra onde esta o conteudo e evita transcrever 10 minutos de nada.
  2. Se o detector de idioma devolver confianca BAIXA, isso significa que NAO HA FALA
     naquele trecho — nao que o idioma seja aquele. Amostrar so o inicio de um arquivo
     com lead-in silencioso faz o detector chutar "en" com probabilidade ~0,3, e quem
     acreditar transcreve a reuniao inteira traduzida. Por isso as amostras sao
     coletadas nos trechos COM sinal, e a confianca e reportada.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

FFMPEG = os.environ.get("TERRAS_FFMPEG", os.path.expanduser("~/.config/terras-video/ffmpeg"))


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")


def info_audio(caminho):
    p = run([FFMPEG, "-hide_banner", "-i", caminho])
    dur, stream = None, ""
    for linha in p.stderr.splitlines():
        if "Duration:" in linha:
            h, m, s = linha.split("Duration:")[1].split(",")[0].strip().split(":")
            dur = int(h) * 3600 + int(m) * 60 + float(s)
        if "Audio:" in linha:
            stream = linha.split("Audio:", 1)[1].strip()
    return dur, stream


def volume_em(caminho, inicio, duracao):
    p = run([FFMPEG, "-hide_banner", "-nostats", "-ss", str(inicio), "-t", str(duracao),
             "-i", caminho, "-af", "volumedetect", "-f", "null", "-"])
    media = pico = None
    for linha in p.stderr.splitlines():
        if "mean_volume:" in linha:
            media = float(linha.split("mean_volume:")[1].split("dB")[0])
        if "max_volume:" in linha:
            pico = float(linha.split("max_volume:")[1].split("dB")[0])
    return media, pico


def fmt(t):
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--passo", type=int, default=180, help="tamanho da janela do mapa (s)")
    ap.add_argument("--limiar-silencio", type=float, default=-50.0,
                    help="abaixo disso (dB medio) a janela conta como silencio")
    ap.add_argument("--amostras", type=int, default=3, help="quantas amostras de idioma")
    ap.add_argument("--arquivo-modelo", default="large-v3-turbo")
    args = ap.parse_args()

    if not os.path.exists(FFMPEG):
        print(f"[!] ffmpeg nao encontrado em {FFMPEG}. "
              f"Defina TERRAS_FFMPEG ou rode o setup da terras-video.", file=sys.stderr)
        return 1

    dur, stream = info_audio(args.audio)
    if dur is None:
        print("[!] nao consegui ler o audio com o ffmpeg.", file=sys.stderr)
        return 1
    print(f"arquivo : {os.path.basename(args.audio)}")
    print(f"duracao : {fmt(dur)} ({dur:.0f}s)")
    print(f"stream  : {stream}\n")

    print(f"=== mapa de volume (janelas de {args.passo}s) ===")
    com_sinal, silencio = [], []
    for inicio in range(0, int(dur), args.passo):
        media, pico = volume_em(args.audio, inicio, min(args.passo, dur - inicio))
        if media is None:
            continue
        marca = "silencio" if media < args.limiar_silencio else "sinal"
        (silencio if marca == "silencio" else com_sinal).append((inicio, media))
        print(f"  {fmt(inicio)}  medio {media:7.1f} dB  pico {pico:6.1f} dB  {marca}")

    if com_sinal:
        inicio_fala = com_sinal[0][0]
        fim_fala = com_sinal[-1][0] + args.passo
        print(f"\nconteudo com sinal: de {fmt(inicio_fala)} ate {fmt(min(fim_fala, dur))} "
              f"({100 * sum(1 for _ in com_sinal) / max(1, len(com_sinal) + len(silencio)):.0f}% "
              f"das janelas)")
        if silencio:
            print(f"janelas sem sinal: {len(silencio)} "
                  f"(primeira em {fmt(silencio[0][0])}"
                  + (f", ultima em {fmt(silencio[-1][0])})" if len(silencio) > 1 else ")"))
    if not com_sinal:
        print("\n[!] nenhuma janela com sinal. Confira o arquivo.", file=sys.stderr)
        return 2

    # Amostras de idioma SO nos trechos com sinal — nunca no inicio cego do arquivo.
    # O ponto de amostragem vai no MEIO da janela, nao no inicio: com passo grande, o
    # inicio de uma janela pode cair no silencio de lead-in e devolver idioma errado
    # com confianca baixa.
    print(f"\n=== deteccao de idioma ({args.amostras} amostras em trechos com sinal) ===")
    from faster_whisper import WhisperModel
    meio = min(args.passo // 2, 60)
    pontos = []
    for i in range(args.amostras):
        janela = com_sinal[round(i * (len(com_sinal) - 1) / max(1, args.amostras - 1))][0]
        pontos.append(min(janela + meio, max(0, int(dur) - 90)))
    modelo = WhisperModel(args.arquivo_modelo, device="cpu", compute_type="int8",
                          cpu_threads=os.cpu_count() or 4)
    tmp = tempfile.mkdtemp(prefix="preflight-")
    veredito = {}
    for p in sorted(set(pontos)):
        wav = os.path.join(tmp, f"a{p}.wav")
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(p), "-t", "90",
             "-i", args.audio, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav])
        segs, info = modelo.transcribe(wav, beam_size=1, without_timestamps=True,
                                       clip_timestamps="0,25")
        list(segs)
        confiavel = info.language_probability >= 0.7
        alerta = "" if confiavel else "  <-- CONFIANCA BAIXA: provavelmente nao ha fala aqui"
        print(f"  {fmt(p)}  idioma={info.language}  prob={info.language_probability:.3f}{alerta}")
        if confiavel:
            veredito[info.language] = veredito.get(info.language, 0) + 1
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)

    print()
    if len(veredito) == 1:
        idioma = next(iter(veredito))
        print(f"[ok] idioma consistente: {idioma} — transcreva com --idioma {idioma} "
              f"(ou deixe auto).")
        print(f"[i] conferencia final: se o texto sair num idioma diferente de {idioma}, "
              f"desconfie de traducao.")
    elif len(veredito) > 1:
        print(f"[!] amostras divergem: {veredito}. Audio provavelmente MULTILINGUE "
              f"(troca de idioma no meio) ou com trechos musicados.")
        print("    Use --idioma auto e confira bloco a bloco; um idioma fixo vai "
              "traduzir os trechos do outro idioma.")
    else:
        print("[!] nenhuma amostra confiavel. O arquivo pode ser so ruido.", file=sys.stderr)
        return 2
    print("\nproximo passo: transcrever.py — SEM --prompt na primeira passada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

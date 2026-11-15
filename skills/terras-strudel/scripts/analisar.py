#!/usr/bin/env python3
"""Analisa um arquivo de áudio e gera dados para recriar o groove no Strudel.

Uso: analisar.py <audio> <pasta_saida>

Gera em <pasta_saida>/dados/:
  analise.json   BPM, tom, acordes por compasso, seções por energia, padrão de bateria
  acordes.csv    um acorde estimado por compasso, com tempo de início
Não transcreve melodia: só tempo, harmonia, baixo e ritmo.
"""
import csv
import json
import sys
from pathlib import Path

import librosa
import numpy as np

NOTAS = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
# Perfis de Krumhansl-Kessler para detecção de tom
MAIOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MENOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


def detectar_tom(chroma_medio):
    melhores = []
    for i in range(12):
        melhores.append((np.corrcoef(np.roll(MAIOR, i), chroma_medio)[0, 1], NOTAS[i], "maior"))
        melhores.append((np.corrcoef(np.roll(MENOR, i), chroma_medio)[0, 1], NOTAS[i], "menor"))
    melhores.sort(reverse=True)
    return [{"tonica": n, "modo": m, "correlacao": round(float(c), 3)} for c, n, m in melhores[:3]]


def templates_acordes():
    t = {}
    for i, n in enumerate(NOTAS):
        maj = np.zeros(12); maj[[i, (i + 4) % 12, (i + 7) % 12]] = 1
        mnr = np.zeros(12); mnr[[i, (i + 3) % 12, (i + 7) % 12]] = 1
        t[n] = maj / np.linalg.norm(maj)
        t[n + "m"] = mnr / np.linalg.norm(mnr)
    return t


def acorde_de(chroma_vec, tpl):
    v = chroma_vec / (np.linalg.norm(chroma_vec) + 1e-9)
    nome, score = max(((k, float(v @ t)) for k, t in tpl.items()), key=lambda x: x[1])
    return nome, round(score, 3)


def main(audio, saida):
    saida = Path(saida)
    (saida / "dados").mkdir(parents=True, exist_ok=True)

    # m4a/webm não abrem no soundfile: converte para wav temporário com ffmpeg
    if Path(audio).suffix.lower() not in (".wav", ".flac", ".ogg"):
        import subprocess, tempfile
        wav = Path(tempfile.mkdtemp()) / "audio.wav"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", "22050", str(wav)], check=True)
        y, sr = librosa.load(wav, sr=22050, mono=True)
    else:
        y, sr = librosa.load(audio, sr=22050, mono=True)
    dur = len(y) / sr
    harm, perc = librosa.effects.hpss(y)

    # Tempo e batidas
    tempo, beats = librosa.beat.beat_track(y=perc, sr=sr)
    tempo = float(np.atleast_1d(tempo)[0])
    beat_t = librosa.frames_to_time(beats, sr=sr)

    # Tom
    chroma = librosa.feature.chroma_cqt(y=harm, sr=sr)
    tons = detectar_tom(chroma.mean(axis=1))

    # Acordes por compasso (4 tempos)
    tpl = templates_acordes()
    chroma_b = librosa.util.sync(chroma, beats, aggregate=np.median)
    acordes = []
    for c in range(0, chroma_b.shape[1] - 3, 4):
        nome, sc = acorde_de(chroma_b[:, c:c + 4].mean(axis=1), tpl)
        acordes.append({"compasso": c // 4 + 1, "inicio_s": round(float(beat_t[c]), 2), "acorde": nome, "confianca": sc})

    # Baixo: nota mais forte na faixa grave (até ~260 Hz) por compasso
    cqt_low = np.abs(librosa.cqt(harm, sr=sr, fmin=librosa.note_to_hz("C1"), n_bins=48))
    low_b = librosa.util.sync(cqt_low, beats, aggregate=np.median)
    for i, a in enumerate(acordes):
        c = i * 4
        if c + 4 <= low_b.shape[1]:
            a["baixo"] = librosa.midi_to_note(24 + int(low_b[:, c:c + 4].mean(axis=1).argmax()), unicode=False)

    # Seções por energia (RMS a cada compasso), rotuladas por nível
    rms = librosa.feature.rms(y=y)[0]
    rms_b = librosa.util.sync(rms[None, :], beats, aggregate=np.mean)[0]
    rms_c = [float(rms_b[c:c + 4].mean()) for c in range(0, len(rms_b) - 3, 4)]
    q = np.quantile(rms_c, [0.33, 0.66]) if rms_c else [0, 0]
    niveis = ["baixa" if v < q[0] else "media" if v < q[1] else "alta" for v in rms_c]
    secoes = []
    for i, n in enumerate(niveis):
        if not secoes or secoes[-1]["energia"] != n:
            secoes.append({"energia": n, "compasso_ini": i + 1, "compasso_fim": i + 1,
                           "inicio_s": acordes[i]["inicio_s"] if i < len(acordes) else None})
        else:
            secoes[-1]["compasso_fim"] = i + 1
    secoes = [s for s in secoes if s["compasso_fim"] - s["compasso_ini"] >= 1]

    # Bateria: média do ataque em 16 posições do compasso, banda grave (bumbo) e aguda (caixa/prato)
    def grade(sinal_onset):
        frames = librosa.time_to_frames(beat_t, sr=sr)
        pos = np.zeros(16); cnt = np.zeros(16)
        for b in range(0, len(frames) - 4, 4):
            ini, fim = frames[b], frames[b + 4]
            seg = np.linspace(ini, fim, 17)[:-1].astype(int)
            for k, f in enumerate(seg):
                if f < len(sinal_onset):
                    pos[k] += sinal_onset[max(f - 1, 0):f + 2].max(); cnt[k] += 1
        g = pos / np.maximum(cnt, 1)
        return [round(float(x), 2) for x in g / (g.max() + 1e-9)]

    S = np.abs(librosa.stft(perc))
    freqs = librosa.fft_frequencies(sr=sr)
    grave = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[freqs < 150]), sr=sr)
    agudo = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[freqs > 2000]), sr=sr)
    medio = librosa.onset.onset_strength(S=librosa.amplitude_to_db(S[(freqs > 150) & (freqs < 2000)]), sr=sr)

    resultado = {
        "arquivo": Path(audio).name,
        "duracao_s": round(dur, 1),
        "bpm": round(tempo, 1),
        "bpm_observacao": "beat_track pode dar metade ou dobro; conferir ouvindo",
        "compassos": len(acordes),
        "tom_candidatos": tons,
        "acordes_por_compasso": acordes,
        "secoes_por_energia": secoes,
        "bateria_grade_16": {"grave_bumbo": grade(grave), "medio_caixa": grade(medio), "agudo_prato": grade(agudo)},
    }
    (saida / "dados" / "analise.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2))
    with open(saida / "dados" / "acordes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["compasso", "inicio_s", "acorde", "baixo", "confianca"])
        w.writeheader()
        for a in acordes:
            w.writerow({k: a.get(k) for k in w.fieldnames})

    print(json.dumps({k: resultado[k] for k in ["duracao_s", "bpm", "compassos", "tom_candidatos"]}, ensure_ascii=False))
    print("secoes:", [(s["energia"], s["compasso_ini"], s["compasso_fim"], s["inicio_s"]) for s in secoes])
    print("bateria:", json.dumps(resultado["bateria_grade_16"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

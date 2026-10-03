#!/usr/bin/env python3
"""Conferencia de trechos duvidosos por consenso entre configuracoes independentes.

Nao escolhe vencedor e nao corrige nada sozinho: imprime o que cada configuracao
ouviu, para a decisao ser tomada com a divergencia a vista. Onde as configuracoes
concordam, a leitura e confiavel; onde divergem, o trecho deve ser marcado como
incerto no texto final (ou conferido a ouvido).

Uso:
  verificar.py AUDIO --base BASE.json --auto
  verificar.py AUDIO --base BASE.json --janelas "1400:1430,2700:2720"
  verificar.py AUDIO --base BASE.json --auto --termos "Kommo,Asaas,Yampi"

--auto escolhe as janelas sozinho, por tres sinais:
  confianca baixa (avg_logprob), segmento longo com pouco texto (fala engolida) e
  presenca de token capitalizado raro (candidato a nome proprio mal transcrito).
--termos entra em UMA das configuracoes, de proposito: serve para checar se o
  termo desejado aparece quando sugerido. Se aparecer SO nessa configuracao, e
  provavel enviesamento do prompt, nao evidencia — ver SKILL.md.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

FFMPEG = os.environ.get("TERRAS_FFMPEG", os.path.expanduser("~/.config/terras-video/ffmpeg"))

CONFIGURACOES = [
    ("turbo beam5", "large-v3-turbo", 5, False),
    ("v3    beam5", "large-v3", 5, False),
    ("v3    greedy", "large-v3", 1, False),
    ("v3    beam5 +termos", "large-v3", 5, True),
]


def fmt(t):
    return f"{int(t // 60):02d}:{int(t % 60):02d}"


def candidatos(dados, maximo):
    segs = dados["segments"]
    sinais = defaultdict(list)

    for s in segs:
        if s["avg_logprob"] < -0.8:
            sinais["confianca baixa"].append(s)
        dur = s["end"] - s["start"]
        if dur > 8 and len(s["text"]) < 40:
            sinais["fala engolida (longo com pouco texto)"].append(s)

    # tokens capitalizados raros: aparecem 1-2 vezes e nao sao inicio de frase comum
    contagem = Counter()
    for s in segs:
        for t in re.findall(r"\b[A-ZÀ-Ý][\wÀ-ÿ]{2,}\b", s["text"]):
            contagem[t] += 1
    raros = {t for t, c in contagem.items() if c <= 2}
    for s in segs:
        if any(t in raros for t in re.findall(r"\b[A-ZÀ-Ý][\wÀ-ÿ]{2,}\b", s["text"])):
            sinais["nome proprio raro"].append(s)

    # escolhe janelas, evitando sobreposicao
    escolhidas, usados = [], []
    for motivo, lista in sinais.items():
        for s in lista:
            centro = (s["start"] + s["end"]) / 2
            if any(abs(centro - c) < 25 for c in usados):
                continue
            usados.append(centro)
            escolhidas.append((max(0, s["start"] - 4), s["end"] + 4, motivo))
            if len(escolhidas) >= maximo:
                return escolhidas, dict(contagem)
    return escolhidas, dict(contagem)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("--base", required=True, help="BASE.json gerado por transcrever.py")
    ap.add_argument("--janelas", default=None, help='ex.: "1400:1430,2700:2720"')
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--max-auto", type=int, default=12)
    ap.add_argument("--termos", default=None, help="candidatos a nome proprio, separados por virgula")
    ap.add_argument("--contexto", default=None, help="frase de contexto para a configuracao com termos")
    args = ap.parse_args()

    dados = json.load(open(args.base, encoding="utf-8"))
    idioma = dados.get("language") or "pt"

    if args.janelas:
        janelas = []
        for par in args.janelas.split(","):
            a, b = par.split(":")
            janelas.append((float(a), float(b), "informada"))
    elif args.auto:
        janelas, _ = candidatos(dados, args.max_auto)
        print(f"[i] {len(janelas)} janelas escolhidas automaticamente "
              f"(de {len(dados['segments'])} segmentos)\n")
    else:
        print("[!] informe --auto ou --janelas.", file=sys.stderr)
        return 1

    if not janelas:
        print("[ok] nenhum sinal de problema no transcript. Nada a conferir.")
        return 0

    prompt = None
    if args.termos:
        prompt = ((args.contexto + " ") if args.contexto else "") + \
                 "Termos citados: " + ", ".join(args.termos) + "."

    from faster_whisper import WhisperModel

    tmp = tempfile.mkdtemp(prefix="verificar-")
    caminhos = []
    for a, b, motivo in janelas:
        p = os.path.join(tmp, f"{int(a):07d}.wav")
        subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a),
                        "-t", str(b - a), "-i", args.audio, "-ar", "16000", "-ac", "1",
                        "-c:a", "pcm_s16le", p], check=True)
        caminhos.append((p, a, b, motivo))

    cache = {}
    for _, nome_modelo, _, _ in CONFIGURACOES:
        if nome_modelo not in cache:
            print(f"[i] carregando {nome_modelo}...", flush=True)
            cache[nome_modelo] = WhisperModel(nome_modelo, device="cpu", compute_type="int8",
                                              cpu_threads=os.cpu_count() or 4)
    print(f"[i] {len(caminhos)} janelas x {len(CONFIGURACOES)} configuracoes. "
          f"Imprime cada janela assim que ela fica pronta.\n", flush=True)

    # Janela no laco externo: o resultado sai na tela a cada janela concluida, em vez
    # de esperar todas. Em audio longo isso e a diferenca entre acompanhar e achar que
    # travou.
    for p, a, b, motivo in caminhos:
        variantes = []
        for rotulo, nome_modelo, beam, usa_prompt in CONFIGURACOES:
            segs, _ = cache[nome_modelo].transcribe(
                p, language=idioma, beam_size=beam, condition_on_previous_text=False,
                vad_filter=False, temperature=0.0,
                initial_prompt=prompt if usa_prompt else None)
            variantes.append((rotulo, " ".join(s.text.strip() for s in segs)))

        print("=" * 78)
        print(f"[{fmt(a)}–{fmt(b)}]  ({b - a:.0f}s)  motivo: {motivo}")
        print("=" * 78)
        for rotulo, texto in variantes:
            print(f"  {rotulo:20s} | {texto}")
        cont = Counter()
        for _, texto in variantes:
            for palavra in set(re.findall(r"\b\w{4,}\b", texto.lower())):
                cont[palavra] += 1
        firmes = sorted(palavra for palavra, c in cont.items() if c >= 3)
        if firmes:
            print(f"  -> concordam em >=3 configuracoes: {', '.join(firmes[:14])}")
        # o prompt e uma configuracao so: se um termo aparece apenas nela, e sugestao
        # do prompt, nao evidencia do audio — vale dizer isso na hora
        if prompt:
            so_prompt = [t for t in re.findall(r"[\wÀ-ÿ]{4,}", variantes[-1][1])
                         if not any(t.lower() in v.lower() for _, v in variantes[:-1])]
            if so_prompt:
                print(f"  (!) so na configuracao com prompt: {', '.join(so_prompt[:6])} "
                      f"— provavel enviesamento, nao evidencia")
        print(flush=True)

    for p, *_ in caminhos:
        os.remove(p)
    os.rmdir(tmp)
    print("Como decidir: onde as configuracoes concordam, aceite. Onde divergem, marque")
    print("[?] no texto final e liste com timestamp — nao escolha a versao mais bonita.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

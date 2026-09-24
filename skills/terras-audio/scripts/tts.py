#!/usr/bin/env python3
"""Voz, pronuncia e cadeia de audio: narracao curta e audiolivro.

Separado da `terras-video` de proposito: o texto e o mesmo insumo, mas o alvo de
entrega muda. Video do YouTube quer fala em torno de -16 LUFS; audiolivro tem faixa
propria, mais baixa e mais estavel (ACX pede RMS entre -23 e -18 dBFS, teto de pico
em -3 dBFS). Deixar as duas coisas na mesma skill garante que um dia alguem normalize
um capitulo de livro com alvo de video.

Comandos:
    tts.py narrar --texto "..." --saida fala.wav [--voz ... --ritmo ... --sotaque ... --lufs video|livro]
    tts.py narrar --arquivo capitulo.md --saida capitulo.wav --lufs livro
    tts.py relatorio ROTEIRO_OU_TEXTO        # termos ingleses que podem sair com sotaque
    tts.py calibrar PALAVRA --frase ... --candidatos ...
    tts.py lote                              # o dicionario inteiro numerado
    tts.py livro --entrada livro.md --pasta saida/ [--titulo ... --autor ...]

O `livro` divide por cabecalho de capitulo (## ou "# Capitulo"), gera um mp3 por
capitulo, junta tudo num m4b com marcacao de capitulo, e e retomavel: capitulo ja
gerado nao e refeito, entao uma geracao derrubada no meio nao perde o trabalho.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_TOOLS = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
EDGE = os.path.join(BASE_TOOLS, "venv", "bin", "edge-tts")
FFMPEG = os.path.join(BASE_TOOLS, "ffmpeg")
BRAND_DIR = os.path.expanduser(os.environ.get("TERRAS_BRAND_DIR", "~/Documents/Diversos/terras-brand"))

VOZ_PADRAO = "pt-BR-ThalitaMultilingualNeural"
RITMO_PADRAO = "-8%"

# Alvos de loudness por contexto, em LUFS integrado e pico verdadeiro em dBFS.
ALVOS = {
    "video": {"lufs": (-17.0, -14.0), "pico": -1.0,
              "nota": "fala para video, alvo de plataforma de video"},
    "livro": {"lufs": (-19.5, -18.0), "pico": -3.0,
              "nota": "audiolivro: faixa mais baixa e teto de pico em -3 dBFS, no espirito do que a ACX pede"},
}

CADEIA_AUDIO = (
    "highpass=f=75,"
    "acompressor=threshold=-18dB:ratio=3:attack=6:release=120,"
    "loudnorm=I={lufs}:TP={tp}:LRA=11,"
    "aresample=48000"
)


def fail(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        fail(f"falhou: {' '.join(str(c) for c in cmd[:8])}\n{r.stdout[-800:]}{r.stderr[-800:]}")
    return r


def carregar_pronuncia():
    import importlib.util
    caminho = os.path.join(AUDIO_DIR, "pronuncia.py")
    spec = importlib.util.spec_from_file_location("terras_pronuncia", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def alvo(nome):
    if nome in ALVOS:
        return ALVOS[nome]
    fail(f"alvo desconhecido: {nome}. Use {' ou '.join(ALVOS)}")


def cortar(mp3):
    """Corta o silencio das pontas: o endpoint preenche trecho curto ate 1,87s."""
    tmp = mp3 + ".corte.mp3"
    run([FFMPEG, "-y", "-i", mp3, "-af",
         "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,"
         "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse",
         "-c:a", "libmp3lame", "-b:a", "192k", tmp])
    os.replace(tmp, mp3)


def narrar(texto, saida, voz, ritmo, sotaque, contexto):
    """Gera a fala e aplica a cadeia, com loudness do contexto escolhido.

    Modos de sotaque: `aportuguesar` (grafia em ortografia portuguesa, o padrao) e
    `nenhum`.

    Dois modos foram testados e reprovados pelo ouvido do Everton, e nao voltam sem
    uma voz paga: a troca de VOZ no termo ingles ("nao presta, misturou") e a fatia
    com a MESMA voz, gerando o termo separado e colando de volta ("o terceiro mistura
    idiomas"). A voz e multilingue e le o termo melhor quando ele vem sozinho, mas a
    troca de fonologia no meio da frase se ouve, e isso e o que ele nao quer.
    """
    if not os.path.exists(EDGE):
        fail(f"edge-tts ausente em {EDGE}: rode o setup.sh da terras-video")
    cfg = alvo(contexto)
    lufs_meio = (cfg["lufs"][0] + cfg["lufs"][1]) / 2
    # teto do loudnorm com margem de 0,5 dB abaixo do limite que o contexto checa,
    # senao o proprio alvo encosta no gate (era o caso do video: -0.5 contra -1.0)
    cadeia = CADEIA_AUDIO.format(lufs=f"{lufs_meio:.1f}", tp=f"{cfg['pico'] - 0.5:.1f}")

    bruto = saida + ".bruto.mp3"

    if sotaque == "aportuguesar":
        texto = carregar_pronuncia().aplicar(texto)
    run([EDGE, "--voice", voz, "--rate", ritmo, "--text", texto, "--write-media", bruto])
    run([FFMPEG, "-y", "-i", bruto, "-af", cadeia, "-ar", "48000", "-ac", "2", saida])
    os.remove(bruto)
    return saida


def duracao(caminho):
    r = subprocess.run([FFMPEG, "-i", caminho], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def loudness(caminho):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", caminho,
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    lufs = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", r.stderr)
    pico = re.findall(r"Peak:\s+(-?[\d.]+)\s+dBF", r.stderr)
    return (float(lufs[-1]) if lufs else None, float(pico[-1]) if pico else None)


def dividir_capitulos(texto):
    """Divide markdown por cabecalho de capitulo. Sem cabecalho, o livro e um so."""
    linhas = texto.splitlines()
    capitulos, atual = [], None
    for linha in linhas:
        if re.match(r"^#{1,2}\s+\S", linha):
            if atual:
                capitulos.append(atual)
            atual = {"titulo": re.sub(r"^#+\s*", "", linha).strip(), "linhas": []}
        elif atual is not None:
            atual["linhas"].append(linha)
        else:
            atual = {"titulo": "Abertura", "linhas": [linha]}
    if atual:
        capitulos.append(atual)
    return [c for c in capitulos if "".join(c["linhas"]).strip()]


def em_paragrafos(linhas):
    """Junta o texto em paragrafos e corta em blocos que o endpoint aceita."""
    texto = "\n".join(linhas)
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", texto) if p.strip()]
    blocos, atual = [], ""
    for p in paragrafos:
        if len(atual) + len(p) > 1800 and atual:
            blocos.append(atual.strip()); atual = ""
        atual += p + "\n\n"
    if atual.strip():
        blocos.append(atual.strip())
    return blocos


def livro(entrada, pasta, voz, ritmo, sotaque, titulo, autor):
    """Gera um audiolivro por capitulos, retomavel, e junta em m4b com marcacao."""
    os.makedirs(pasta, exist_ok=True)
    texto = open(entrada, encoding="utf-8").read()
    capitulos = dividir_capitulos(texto)
    if not capitulos:
        fail("nao achei texto para narrar")
    print(f"livro: {len(capitulos)} capitulo(s)")

    partes = []
    for i, cap in enumerate(capitulos, start=1):
        destino = os.path.join(pasta, f"capitulo-{i:02d}.mp3")
        blocos = em_paragrafos(cap["linhas"])
        if os.path.exists(destino):
            print(f"  capitulo {i} ja existe, pulando (retomavel)")
        else:
            print(f"  capitulo {i}: {cap['titulo']!r}, {len(blocos)} bloco(s)")
            pedacos = []
            for k, bloco in enumerate(blocos):
                pedaco = os.path.join(pasta, f"capitulo-{i:02d}-parte{k:03d}.mp3")
                if not os.path.exists(pedaco):
                    narrar(bloco, pedaco.replace(".mp3", ".wav"), voz, ritmo, sotaque, "livro")
                    run([FFMPEG, "-y", "-i", pedaco.replace(".mp3", ".wav"),
                         "-c:a", "libmp3lame", "-b:a", "128k", pedaco])
                    os.remove(pedaco.replace(".mp3", ".wav"))
                pedacos.append(pedaco)
            silencio = os.path.join(pasta, "_pausa.wav")
            run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-t", "0.85", silencio])
            lista = os.path.join(pasta, f"_lista-{i:02d}.txt")
            with open(lista, "w", encoding="utf-8") as fh:
                for k, p in enumerate(pedacos):
                    fh.write(f"file '{p}'\n")
                    if k < len(pedacos) - 1:
                        fh.write(f"file '{silencio}'\n")
            run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", lista,
                 "-c:a", "libmp3lame", "-b:a", "128k", destino])
        d = duracao(destino)
        lufs, pico = loudness(destino)
        print(f"    {d/60:.1f} min | {lufs:.1f} LUFS | pico {pico:.1f} dBFS")
        partes.append((destino, cap["titulo"], d))

    # junta em m4b com capitulos marcados
    meta = os.path.join(pasta, "_capitulos.txt")
    t = 0.0
    with open(meta, "w", encoding="utf-8") as fh:
        fh.write(";FFMETADATA1\n")
        if titulo: fh.write(f"title={titulo}\n")
        if autor: fh.write(f"artist={autor}\n")
        fh.write("genre=Audiobook\n")
        for caminho, nome, dur in partes:
            fh.write("[CHAPTER]\nTIMEBASE=1/1000\n")
            fh.write(f"START={int(t*1000)}\n")
            fh.write(f"END={int((t+dur)*1000)}\n")
            fh.write(f"title={nome}\n")
            t += dur
    concat_txt = os.path.join(pasta, "_concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as fh:
        for caminho, _, _ in partes:
            fh.write(f"file '{caminho}'\n")
    reunido = os.path.join(pasta, "_reunido.mp3")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", reunido])
    m4b = os.path.join(pasta, (titulo or "audiolivro").lower().replace(" ", "-") + ".m4b")
    run([FFMPEG, "-y", "-i", reunido, "-i", meta, "-map_metadata", "1", "-map_chapters", "1",
         "-c:a", "aac", "-b:a", "96k", "-f", "mp4", m4b])
    total = duracao(m4b)
    print(f"m4b: {m4b} | {total/3600:.2f} h | {len(partes)} capitulo(s)")


def relatorio(entrada):
    pron = carregar_pronuncia()
    if entrada.endswith(".json"):
        cfg = json.load(open(entrada, encoding="utf-8"))
        total, linhas = pron.relatorio(cfg)
    else:
        texto = open(entrada, encoding="utf-8").read()
        achados = pron.detectar(texto)
        total = len(achados)
        linhas = ["  " + "; ".join(f"{p} -> {s}" + ("" if p.lower() in pron.CALIBRADAS else " (palpite)")
                                   for p, s in achados if s) if achados else ""]
    print(f"-- pronuncia: {total} termo(s) que podem sair com sotaque --")
    for l in linhas:
        print(l)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="acao", required=True)

    n = sub.add_parser("narrar")
    n.add_argument("--texto"); n.add_argument("--arquivo")
    n.add_argument("--saida", required=True)
    n.add_argument("--voz", default=VOZ_PADRAO); n.add_argument("--ritmo", default=RITMO_PADRAO)
    n.add_argument("--sotaque", default="aportuguesar", choices=["aportuguesar", "nenhum"])
    n.add_argument("--alvo", default="video", choices=list(ALVOS))

    r = sub.add_parser("relatorio"); r.add_argument("entrada")

    c = sub.add_parser("calibrar")
    c.add_argument("palavra"); c.add_argument("--frase", required=True)
    c.add_argument("--candidatos", required=True); c.add_argument("--voz", default=VOZ_PADRAO)
    c.add_argument("--destino", default=os.path.join(BRAND_DIR, "exports", "cartelas", "calibra-pronuncia.mp3"))

    l = sub.add_parser("lote")
    l.add_argument("--destino", default=os.path.join(BRAND_DIR, "exports", "cartelas", "lote-pronuncia-dicionario.mp3"))
    l.add_argument("--voz", default=VOZ_PADRAO)
    l.add_argument("--por-bloco", type=int, default=15)

    v = sub.add_parser("livro")
    v.add_argument("--entrada", required=True); v.add_argument("--pasta", required=True)
    v.add_argument("--voz", default=VOZ_PADRAO); v.add_argument("--ritmo", default=RITMO_PADRAO)
    v.add_argument("--sotaque", default="aportuguesar", choices=["aportuguesar", "nenhum"])
    v.add_argument("--titulo", default=""); v.add_argument("--autor", default="")

    args = ap.parse_args()
    if args.acao == "narrar":
        texto = args.texto or (open(args.arquivo, encoding="utf-8").read() if args.arquivo else None)
        if not texto:
            fail("informe --texto ou --arquivo")
        destino = narrar(texto, args.saida, args.voz, args.ritmo, args.sotaque, args.alvo)
        lufs, pico = loudness(destino)
        print(f"{destino} | {duracao(destino):.1f}s | {lufs:.1f} LUFS | pico {pico:.1f} dBFS")
    elif args.acao == "relatorio":
        relatorio(args.entrada)
    elif args.acao == "calibrar":
        carregar_pronuncia().calibrar(args.palavra, args.frase,
                                      [x.strip() for x in args.candidatos.split(",") if x.strip()],
                                      args.voz, os.path.expanduser(args.destino))
    elif args.acao == "lote":
        carregar_pronuncia().lote(os.path.expanduser(args.destino), args.voz)
    else:
        livro(args.entrada, os.path.expanduser(args.pasta), args.voz, args.ritmo,
              args.sotaque, args.titulo, args.autor)


if __name__ == "__main__":
    main()

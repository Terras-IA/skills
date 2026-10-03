#!/usr/bin/env python3
"""Acha palavras inglesas no texto da narracao e sugere como reduzir o sotaque.

Por que existe: o endpoint gratuito do `edge-tts` **nao aceita marcacao de SSML**
dentro do texto. Testado em 2026-09-20 com `<lang xml:lang="en-US">`, `<emphasis>` e
um `<prosody>` interno: os tres voltaram com "No audio was received", ou seja, o
servico recusa qualquer tag no meio da frase. Logo, nao existe troca de idioma por
palavra nessa rota; o que existe e:

  1. usar uma voz multilingue (`pt-BR-ThalitaMultilingualNeural`), que ja lida
     melhor com termo estrangeiro;
  2. respelling: escrever a palavra com ortografia portuguesa, tipo `harness` ->
     `rarnis`, para o sintetizador cair na pronuncia desejada (palpite ate alguem
     escutar, e por isso o dicionario e editavel);
  3. voz paga (Azure, OpenAI, ElevenLabs), que aceita troca de idioma de verdade.

Uso:
    python3 pronuncia.py roteiro.json                      # relatorio por bloco
    python3 pronuncia.py roteiro.json --aplicar             # texto com respelling aplicado
    python3 pronuncia.py --calibrar runtime --frase "O runtime decide a rota." \
        --candidatos "rantaim,rantáim,rintaim" --destino calibra-runtime.mp3
"""
import argparse
import json
import os
import re
import subprocess
import sys

# `CALIBRADAS` lista o que passou pelo ouvido dele: "checkpoint ok" e "workflow bom"
# vieram da primeira auditoria do lote (2026-09-20), junto com harness e runtime.; o resto e palpite de ortografia e
# pode estar errado. O relatorio marca a diferenca para nao dar a mesma confianca aos
# dois. Historico do `runtime`: venceu `rantáim` na 1a rodada ("melhor de todos, mais
# proximo"), e na 2a rodada a mesma grafia foi marcada ruim enquanto `rantáimi` saiu
# "bom, menos que antes" - leitura ambigua. Ficou `rantáim`, o unico ja chamado de
# melhor de todos, e o topico esta encerrado: duas rodadas mostraram que o limite e do
# sintetizador, nao da grafia.
#
# Termos que o conteudo dele usa e que uma voz pt-BR tende a ler com sotaque.
# A coluna da direita e sugestao de respelling em ortografia portuguesa; vazia
# significa "marcar, mas nao reescrever" ate alguem ouvir e decidir.
DICIONARIO = {
    "harness": "rárnis", "runtime": "rantáim",   # escolhido de ouvido em 2026-09-20 (2a tomada da 1a rodada)
    "framework": "freimeuórk",
    "workflow": "uórkflou", "workflows": "uórkflous", "deploy": "deplói",
    "deploys": "deplóis", "deadline": "dédlain", "deadlines": "dédlains",
    "budget": "bádjet", "roadmap": "ródmap", "insight": "ínsait",
    "insights": "ínsaits", "prompt": "", "prompts": "",
    "token": "tóuken", "tokens": "tóukens", "cache": "kêsh", "cloud": "klaud",
    "cluster": "kláster", "dashboard": "déshbord", "feedback": "fídbek",
    "mock": "mók", "patch": "pétch", "release": "rilís", "rollout": "rólaut",
    "sprint": "", "stack": "sték", "streaming": "stríming",
    "throughput": "thrúput", "checkpoint": "tchékpoint", "endpoint": "éndpoint",
    "gateway": "guêtuêi", "pipeline": "páiplain", "plugin": "pláguin",
    "query": "kuéri", "queue": "kiu", "retry": "ritrái", "sandbox": "séndboks",
    # `rabbitmq` entrou em 2026-09-26, para o video do carrossel do ADR. Calibragem
    # provisoria, com o Whisper no lugar do ouvido dele: no contexto real do bloco, o
    # texto cru saiu transcrito como "Hebtiemic" (irreconhecivel) e a grafia
    # "Rábiti eme quê" saiu como "RabbitM que". As outras tentativas ("Rábit eme quê",
    # "Rábite-MQ", "Rábiti éme quê") sairam pior. Falta a escuta dele.
    "rabbitmq": "Rábiti eme quê",
    "script": "skript", "secret": "síkret", "secrets": "síkrents",
    "service": "sérvis", "snapshot": "snépshot", "staging": "stêidjing",
    "storage": "stórredj", "timeout": "táimaut", "tool": "túul",
    "trace": "trêis", "trigger": "tríguer", "upgrade": "apgrêid",
    "worker": "uórker", "background": "békgraund", "dataset": "dêitasset",
    "feature": "fíutcha", "flags": "flégs", "health": "rélf", "host": "roust",
    "input": "ínput", "job": "djób", "layer": "lêier", "load": "lôud",
    "sprint": "", "skill": "skíl", "skills": "skíls", "driver": "dráiver",
    "ticket": "tíket", "tickets": "tíkets", "log": "lóg", "logs": "lógs",
    # grafias ditadas por ele em 2026-09-20, ouvindo a auditoria
    "souls": "souus", "soul": "soul", "playbook": "pleibuq", "playbooks": "pleibuqs",
}

CALIBRADAS = {"harness", "runtime", "checkpoint", "workflow", "terrasia",
              "souls", "playbook", "playbooks"}   # grafia ditada por ele, ouvindo a auditoria

# Palavras do PORTUGUES cuja tonica a ortografia nao marca, e por isso o sintetizador
# escolhe errado. O tratamento e o mesmo do ingles, com um detalhe: aqui a grafia
# "certa" nao tem acento, entao a substituicao escreve a palavra errada de proposito
# (ruim -> ruím) so para forcar a silaba tonica. O Everton levantou o problema em
# 2026-09-20: "algumas palavras da lingua portuguesa brasil as vezes sai com a silaba
# tonica no local errado por falta de acentuacao grafica".
# Entrada com valor vazio = marcar no relatorio, sem reescrever (a tonica e escolha
# dele, entao essa palavra entra na rodada de calibragem antes de virar substituicao).
DICIONARIO_PT = {
    # hiatos com "ui" e "uim": a tonica cai onde a ortografia nao mostra
    "ruim": "ruím", "ruins": "ruíns", "gratuito": "gratúito", "gratuitos": "gratúitos",
    "gratuita": "gratúita", "circuito": "circúito", "circuitos": "circúitos",
    "fortuito": "fortúito", "intuito": "intúito", "gratuidade": "gratuidade",
    # verbos em -uir: tonica no i final, que a ortografia tambem nao marca
    "contribuir": "contribuír", "constituir": "constituír", "substituir": "substituír",
    "distribuir": "distribuír", "influir": "influír", "fluir": "fluír",
    "possuir": "possuír", "instituir": "instituír", "destituir": "destituír",
    # tonicas irregulares que a regra geral nao alcanca
    "recorde": "recórde", "mister": "míster", "avaro": "ávaro", "novel": "novél",
    "rubrica": "rubríca", "pudico": "", "filantropo": "filantropo",
    "gratuitamente": "gratuítamente",
    # termos do projeto, onde a tonica e decisao de marca
    # marca: calibrada em 2026-09-20. "terrasia" numa palavra soa espanhol, e as
    # duas leituras em duas palavras foram aprovadas; ficou a com espaco porque a
    # com hifen corre o risco de o sintetizador ler pausa ou "traco".
    "terrasia": "terras iá", "terrasial": "terras iá",
}

FRASES_PT = {
    "ruim": "O resultado ruim aparece no relatorio.",
    "gratuito": "O plano gratuito tem limite de uso.",
    "circuito": "O circuito de decisao passa por tres pontos.",
    "contribuir": "Cada area pode contribuir com contexto.",
    "recorde": "O recorde de latencia caiu nesta semana.",
    "rubrica": "A rubrica de custo separa o que e projeto.",
    "terrasia": "O terrasia roda a operacao inteira.",
}

# Palavras que uma voz pt-BR costuma ler bem o suficiente, para nao encher o
# relatorio de ruido.
IGNORAR = {"ia", "api", "url", "app", "email", "e-mail", "software", "hardware",
           "login", "site", "link", "clique", "download", "online"}


def detectar_pt(texto):
    """Devolve [(palavra, sugestao)] de palavra portuguesa com tonica de risco."""
    achados, vistos = [], set()
    for bruta in re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-']+", texto):
        p = bruta.lower()
        if p in vistos or len(p) < 4:
            continue
        if p in DICIONARIO_PT:
            achados.append((bruta, DICIONARIO_PT[p])); vistos.add(p); continue
        # heuristica: verbo em -uir tem tonica no i final, que a ortografia nao marca
        if p.endswith("uir") and len(p) > 5:
            achados.append((bruta, p[:-3] + "uír")); vistos.add(p)
    return achados


def detectar(texto):
    """Devolve [(palavra, sugestao)] do que soa ingles no texto."""
    achados = []
    vistos = set()
    for bruta in re.findall(r"[A-Za-z][A-Za-z\-']+", texto):
        p = bruta.lower()
        if p in IGNORAR or p in vistos or len(p) < 3:
            continue
        if p in DICIONARIO:
            achados.append((bruta, DICIONARIO[p])); vistos.add(p); continue
        # heuristica: em portugues, w, k e y sao rarissimos fora de estrangeirismo
        if any(c in p for c in "wky"):
            achados.append((bruta, "")); vistos.add(p); continue
        if p.endswith(("ing", "tion", "ness", "ship", "ware")) or p.startswith(("th", "sh", "wh")):
            achados.append((bruta, "")); vistos.add(p)
    return achados


def aplicar(texto, dicionario=None):
    """Reescreve os termos com respelling (ingles e portugues), preservando o resto."""
    dic = dict(DICIONARIO_PT)
    dic.update(dicionario or DICIONARIO)
    def troca(m):
        p = m.group(0)
        s = dic.get(p.lower())
        if not s:
            return p
        return s if p[0].islower() else s[0].upper() + s[1:]
    return re.sub(r"[A-Za-z][A-Za-z\-']+", troca, texto)


def fatiar(texto, termos=None):
    """Divide o texto em trechos ('pt', ...) e ('en', palavra) para trocar de voz.

    Usado pela estrategia `voz-en`: a narracao em portugues sai na voz PT e cada
    palavra inglesa sai numa voz EN, que e a unica forma de pronuncia nativa nesta
    rota (o endpoint recusa marcacao de SSML).
    """
    alvos = sorted(set(termos or DICIONARIO), key=len, reverse=True)
    partes, resto = [], texto
    while resto:
        achado = None
        for p in alvos:
            i = resto.lower().find(p)
            if i >= 0 and (achado is None or i < achado[0]):
                achado = (i, p)
        if not achado:
            partes.append(("pt", resto)); break
        i, p = achado
        if i: partes.append(("pt", resto[:i]))
        partes.append(("en", resto[i:i + len(p)]))
        resto = resto[i + len(p):]
    return partes


def relatorio(cfg):
    total = 0
    linhas = []
    for i, b in enumerate(cfg.get("blocks", []), start=1):
        narration = b.get("narration", "")
        achados = [(p, g, "en") for p, g in detectar(narration)]
        achados += [(p, g, "pt") for p, g in detectar_pt(narration)]
        if not achados:
            continue
        total += len(achados)
        com_sugestao = []
        for p, g, origem in achados:
            if not g:
                continue
            marca = "calibrada" if p.lower() in CALIBRADAS else (
                "tonica de risco, conferir" if origem == "pt" else "palpite")
            com_sugestao.append(f"{p} -> {g} ({marca})")
        sem = [p for p, g, _ in achados if not g]
        linhas.append(f"  bloco {i}: " + "; ".join(com_sugestao + sem))
    return total, linhas


def garantir_interpretador():
    """Reexecuta no python do venv, onde vive o edge_tts, como no script de upload."""
    try:
        import edge_tts  # noqa: F401
        return
    except ImportError:
        pass
    base = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
    venv_dir = os.path.join(base, "venv")
    venv_python = os.path.join(venv_dir, "bin", "python")
    if os.path.exists(venv_python) and os.path.realpath(sys.prefix) != os.path.realpath(venv_dir):
        os.execv(venv_python, [venv_python, os.path.abspath(__file__), *sys.argv[1:]])
    sys.exit("edge-tts nao encontrado: rode o setup.sh da skill terras-video")


def calibrar(palavra, frase, candidatos, voz, destino):
    """Gera a mesma frase com a palavra em varias grafias, para escolher de ouvido.

    O dicionario e palpite escrito por ortografia; quem decide e o ouvido do Everton.
    A frase de teste mantem a palavra na mesma posicao em todas as tomadas, e a
    primeira tomada e sempre a palavra em ingles puro, como linha de base.
    """
    garantir_interpretador()
    import asyncio
    import subprocess
    import edge_tts

    base = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
    ffmpeg = os.path.join(base, "ffmpeg")
    tmp = "/tmp/calibra-pronuncia"
    os.makedirs(tmp, exist_ok=True)

    # a primeira tomada e sempre o que a pipeline fala hoje, para servir de base
    atual = DICIONARIO.get(palavra.lower()) or DICIONARIO_PT.get(palavra.lower()) or palavra
    tomadas = [(f"atual ({atual})", atual)] + [(c, c) for c in candidatos]
    arquivos = []
    for k, (rotulo, grafia) in enumerate(tomadas):
        texto = frase.replace(palavra, grafia)
        mp3 = os.path.join(tmp, f"t{k}.mp3")
        asyncio.run(edge_tts.Communicate(texto, voz).save(mp3))
        arquivos.append(mp3)

    silencio = os.path.join(tmp, "sil.wav")
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "0.9", silencio], check=True, capture_output=True)
    sequencia = []
    for i, a in enumerate(arquivos):
        sequencia.append(a)
        if i < len(arquivos) - 1:
            sequencia.append(silencio)
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w", encoding="utf-8") as fh:
        for a in sequencia:
            fh.write(f"file '{a}'\n")
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c:a", "libmp3lame", "-b:a", "192k", destino], check=True, capture_output=True)
    print(f"comparador: {destino}")
    for i, (rotulo, grafia) in enumerate(tomadas, start=1):
        print(f"  {i}. {rotulo}")
    print("diga o numero e eu gravo a grafia no dicionario")


def cortar_silencio(mp3, ffmpeg):
    """Corta o silencio das pontas de um trecho.

    O endpoint preenche palavra curta ate 1,87s fixos (medido: "background",
    "bekgraund" e "cluster" dao exatamente o mesmo tempo, enquanto uma frase inteira
    da 3,02s). Sem cortar, cada item do lote traz quase dois segundos de silencio, a
    auditacao fica arrastada e o Everton perdeu a contagem no primeiro lote por isso.
    """
    tmp = mp3 + ".corte.mp3"
    subprocess.run([ffmpeg, "-y", "-i", mp3, "-af",
                    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,areverse",
                    "-c:a", "libmp3lame", "-b:a", "192k", tmp], check=True, capture_output=True)
    os.replace(tmp, mp3)


def concat(lista, saida, ffmpeg, codec="libmp3lame", bitrate="192k"):
    """Junta os trechos conferindo que todo arquivo listado existe.

    Isso nao e paranoia: o concat do ffmpeg ignorou dois arquivos ausentes em
    silencio e gerou um bloco de 1 segundo onde cabiam 40. Num audiolivro, o mesmo
    defeito entregaria capitulo truncado sem avisar ninguem.
    """
    faltando = []
    for linha in open(lista, encoding="utf-8"):
        caminho = linha.strip().removeprefix("file '").removesuffix("'")
        if caminho and not os.path.exists(caminho):
            faltando.append(caminho)
        elif caminho and os.path.getsize(caminho) == 0:
            faltando.append(f"{caminho} (vazio)")
    if faltando:
        sys.exit("concat abortado, arquivo listado nao existe: " + ", ".join(faltando[:5]))
    subprocess.run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c:a", codec, "-b:a", bitrate, saida], check=True, capture_output=True)


def lote(destino, voz, por_bloco=15):
    """Gera blocos numerados com o dicionario, para conferir de ouvido.

    Cada item fala o proprio numero, depois a grafia que a pipeline usa e depois a
    palavra em ingles, tudo com o silencio cortado. Sai em blocos de 15: contar de 1
    a 15 e facil, de 1 a 69 perde a conta (foi o que aconteceu no primeiro lote, que
    tambem saiu com o ritmo arrastado).
    """
    garantir_interpretador()
    import asyncio
    import edge_tts

    base = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
    ffmpeg = os.path.join(base, "ffmpeg")
    tmp = "/tmp/lote-pronuncia"
    os.makedirs(tmp, exist_ok=True)

    itens = sorted(DICIONARIO.items())
    arquivos, indice = [], []
    for k, (palavra, grafia) in enumerate(itens, start=1):
        if not grafia:
            continue
        numerado = os.path.join(tmp, f"{k:03d}-num.mp3")
        asyncio.run(edge_tts.Communicate(f"item {k}", voz).save(numerado))
        cortar_silencio(numerado, ffmpeg)
        arquivos.append(numerado)
        # A palavra em ingles vem ANTES da frase, como etiqueta audivel: assim o
        # Everton responde pelo nome do termo, e nao por numero. Duas auditorias
        # seguidas desalinharam a contagem (a segunda citou item 72 num lote de 69),
        # porque contar de ouvido nao funciona.
        etiqueta = os.path.join(tmp, f"{k:03d}-palavra.mp3")
        asyncio.run(edge_tts.Communicate(palavra, voz).save(etiqueta))
        cortar_silencio(etiqueta, ffmpeg)
        arquivos.append(etiqueta)
        # E a frase vem EM CONTEXTO, com a grafia que a pipeline fala: auditar palavra
        # solta dava veredito que nao valia para o video, porque a voz multilingue le
        # o termo melhor quando ele vem sozinho.
        frase = f"O {grafia} aparece no meio da frase."
        mp3 = os.path.join(tmp, f"{k:03d}-frase.mp3")
        asyncio.run(edge_tts.Communicate(frase, voz).save(mp3))
        cortar_silencio(mp3, ffmpeg)
        arquivos.append(mp3)
        indice.append((k, palavra, grafia))

    sem_sugestao = [p for p, g in DICIONARIO.items() if not g]
    silencio = os.path.join(tmp, "sil.wav")
    subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "0.45", silencio], check=True, capture_output=True)
    raiz, ext = os.path.splitext(destino)
    for inicio in range(0, len(indice), por_bloco):
        fatia = indice[inicio:inicio + por_bloco]
        lista = os.path.join(tmp, f"lista-{inicio:03d}.txt")
        with open(lista, "w", encoding="utf-8") as fh:
            for k, _, _ in fatia:
                for sufixo in ("num", "palavra", "frase"):
                    fh.write(f"file '{os.path.join(tmp, f'{k:03d}-{sufixo}.mp3')}'\n")
                    fh.write(f"file '{silencio}'\n")
        saida = f"{raiz}-{fatia[0][0]:02d}-a-{fatia[-1][0]:02d}{ext}"
        concat(lista, saida, ffmpeg)
        print(f"bloco: {saida}")
        for k, palavra, grafia in fatia:
            marca = "calibrada" if palavra in CALIBRADAS else "palpite"
            print(f"  {k:>3}. {palavra} -> {grafia} ({marca})")
    if sem_sugestao:
        print("sem sugestao (o relatorio lista e nao reescreve): " + ", ".join(sem_sugestao))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roteiro", nargs="?", help="roteiro.json (relatorio ou --aplicar)")
    ap.add_argument("--aplicar", action="store_true", help="imprime o texto com respelling")
    ap.add_argument("--calibrar", metavar="PALAVRA",
                    help="compara grafias dessa palavra para escolher de ouvido")
    ap.add_argument("--frase", help="frase com a palavra, para o modo --calibrar")
    ap.add_argument("--candidatos", help="grafias separadas por virgula, para o modo --calibrar")
    ap.add_argument("--voz", default="pt-BR-ThalitaMultilingualNeural")
    ap.add_argument("--lote", action="store_true", help="gera um arquivo com o dicionario inteiro")
    ap.add_argument("--destino", default="~/Documents/Diversos/terras-brand/exports/cartelas/calibra-pronuncia.mp3")
    args = ap.parse_args()

    if args.lote:
        lote(os.path.expanduser(args.destino), args.voz)
        return
    if args.calibrar:
        if not (args.frase and args.candidatos):
            sys.exit("--calibrar pede --frase e --candidatos")
        calibrar(args.calibrar, args.frase,
                 [c.strip() for c in args.candidatos.split(",") if c.strip()],
                 args.voz, os.path.expanduser(args.destino))
        return
    if not args.roteiro:
        sys.exit("informe o roteiro.json, ou use --calibrar")

    cfg = json.load(open(args.roteiro, encoding="utf-8"))
    if args.aplicar:
        for i, b in enumerate(cfg.get("blocks", []), start=1):
            print(f"--- bloco {i}")
            print(aplicar(b.get("narration", "")))
        return

    total, linhas = relatorio(cfg)
    print(f"-- pronuncia: {total} termo(s) que podem sair com sotaque --")
    for l in linhas:
        print(l)
    if total:
        print("  (o dicionario de respelling fica em scripts/pronuncia.py; "
              "sugestao vazia = marcar sem reescrever)")


if __name__ == "__main__":
    main()

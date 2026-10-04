#!/usr/bin/env python3
"""Monta o video: roteiro JSON -> cartelas (Chrome) + narracao (edge-tts) -> mp4.

Fluxo de dois tempos, porque o texto falado passa por aprovacao antes de renderizar:

    python3 build.py plan   roteiro.json     # escreve roteiro.md e para
    python3 build.py aprovar roteiro.json    # marca a aprovacao, com data
    python3 build.py render roteiro.json     # cartelas, voz, montagem, checagens

Sem `aprovado: true` no JSON o render recusa.

Movimento: os quadros saem do PIL, com caixa de recorte fracionaria e easing, e
vao por pipe para o ffmpeg. Nao usar zoompan: ele anda em passos desiguais e o
resultado e o "picado" que motivou esta escolha (ver
references/identidade-e-movimento.md, com as medicoes).

Formato: o roteiro pede `"formato": "shorts"` (1080x1920) ou `"horizontal"` (padrao,
1920x1080), e o `size` sobrepoe o canvas. No vertical o tipo sai do menor eixo, e o
conteudo vive na area segura do player, entre SAFE_TOP e SAFE_BOTTOM: o pe do quadro
esta coberto pela interface dos Shorts (canal, titulo, botoes), e cartela que ignora
isso entrega texto escondido.

Carrossel: `"formato": "carrossel"` (1080x1440, o 3:4 do deck da terras-banner) monta
o video a partir dos slides ja renderizados. Cada bloco aponta para um PNG do deck no
campo `slide` em vez de um layout de cartela, e a pagina pronta e o quadro inteiro, com
narracao propria. Sem a area segura dos Shorts: o slide nao vive em player de vertical,
o destino e o feed. O zoom padrao do slide e menor (ZOOM_SLIDE) porque o texto do deck
chega perto das margens.

Uso completo: python3 build.py render roteiro.json [--sem-checagem] [--exportar]
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Skills vizinhas (terras-audio) no mesmo repositório; TERRAS_SKILLS_DIR aponta outra raiz.
SKILLS_DIR = os.environ.get("TERRAS_SKILLS_DIR") or os.path.dirname(SKILL_DIR)
# Template e fontes vivem no diretorio padrao da identidade (ver LEIA-ME.md de
# ~/Documents/Diversos/terras-brand), nao na skill.
BRAND_DIR = os.path.expanduser(os.environ.get("TERRAS_BRAND_DIR", "~/Documents/Diversos/terras-brand"))
TEMPLATE = os.path.join(BRAND_DIR, "templates", "card.html")
TEMPLATE_CANAL = os.path.join(BRAND_DIR, "templates", "card-canal.html")
TEMPLATE_VERTICAL = os.path.join(BRAND_DIR, "templates", "card-vertical.html")
TEMPLATE_CANAL_VERTICAL = os.path.join(BRAND_DIR, "templates", "card-canal-vertical.html")
FONTS_DIR = os.path.join(BRAND_DIR, "fonts")
BASE_TOOLS = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
EDGE = os.path.join(BASE_TOOLS, "venv", "bin", "edge-tts")
FFMPEG = os.path.join(BASE_TOOLS, "ffmpeg")

FPS = 60
MOTION_SCALE = 2      # cartela ampliada antes do recorte: passo sub-pixel na saida
ZOOM_END = 1.06
# Slide de carrossel: o texto do deck fica a 62px da borda mais proxima (medido nos seis
# slides do ADR), entao o zoom padrao cabe e nao corta nada. Mas medido no mesmo deck, o
# zoom de 1,04 reprova no jerk (1,08 contra o teto de 1,0: com recuo pequeno a mediana
# cai e a irregularidade relativa sobe) e o de 1,05 passa com folga (0,52 a 0,72 nos seis
# slides). Por isso o slide usa 1,05: recuo de 26px nas laterais e 34px no topo/base, com
# 28px de sobra no elemento mais apertado. O bloco ainda pode sobrepor com `zoom`.
ZOOM_SLIDE = 1.05
ZOOM_SECONDS = 4.0    # o movimento termina e a imagem descansa
JERK_MAX = 1.0        # irregularidade aceitavel: ver references/identidade-e-movimento.md
# A medida de movimento roda sempre na mesma densidade (4x menos pixel de cada eixo), e
# nao com uma largura fixa: largura fixa mudava a densidade entre formatos e o mesmo
# movimento media diferente em pe e deitado.
FATOR_AMOSTRA = 0.25
# Os dois primeiros quadros ficam fora da medida: eles ainda estao sob o fade de
# entrada e a caixa de recorte deles cai na borda da grade de reamostragem, o que
# inventa um salto no primeiro par medido. Ver `segment`.
QUADROS_AQUECIMENTO = 2
FADE_IN = 0.35
FADE_OUT = 0.45
VOZ_PADRAO = "pt-BR-ThalitaMultilingualNeural"
RITMO_PADRAO = "-8%"   # leitura um pouco mais calma que o default da voz
# Alvo de fala para video. A cadeia de audio e a normalizacao vivem na skill
# terras-audio, que tem alvos por contexto (video e livro); aqui so se confere.
LUFS_ALVO = (-17.0, -14.0)
PICO_MAX = -1.0

# Formato do video. `size` no roteiro ganha do formato quando os dois aparecem.
FORMATOS = {
    "horizontal": "1920x1080",
    "shorts": "1080x1920",
    "vertical": "1080x1920",   # mesmo formato, nome do dia a dia
    "quadrado": "1080x1080",
    "carrossel": "1080x1440",  # 3:4 do slide do deck da terras-banner
}
# Faixa em que o conteudo pode viver no vertical, ANTES do zoom. O pe do quadro e da
# interface do player: medido em 2026-09-20 no player web em 1080x1920, a pilha de
# botoes comeca a 81% da altura do quadro e ocupa a direita, e a faixa de fala do
# criador fica no topo. 12% e 28% deixam 72% do quadro para a cartela, com 9 pontos de
# folga ate os botoes. Ver references/identidade-e-movimento.md.
SAFE_TOPO_FRAC = 0.12
SAFE_BASE_FRAC = 0.28
# Folga na faixa desenhada. A borda de baixo da faixa do player e medida (os botoes),
# mas a de cima e convencao, e o zoom chega exatamente na borda: sem folga o texto
# encosta na linha, e o gate visual mediu 1px de sobra no teste de 2026-09-20. Com
# 1,25% da altura de cada lado sobra ~24px, que e o que faz o desenho tolerar um ajuste
# de zoom ou de margem sem voltar a invadir a interface.
SAFE_FOLGA_FRAC = 0.0125
# Shorts vao ate 3 minutos no YouTube (limite da propria plataforma). Acima disso o
# video deixa de ser Short e cai no player normal, com as cartelas em pe.
SHORTS_MAX_S = 180


def cli_de_audio():
    """Caminho do CLI da skill terras-audio, onde vive toda a parte de voz."""
    padrao = os.path.join(SKILLS_DIR, "terras-audio", "scripts", "tts.py")
    for c in (os.environ.get("TERRAS_AUDIO_CLI"), padrao):
        if c and os.path.exists(c):
            return c
    fail(f"nao achei o CLI da skill terras-audio ({padrao}). "
         "Voz e pronuncia moram la; sem ele nao ha narracao. "
         "TERRAS_AUDIO_CLI aponta outro caminho.")


def fail(msg, extra=""):
    print(f"ERRO: {msg}", file=sys.stderr)
    if extra:
        print(extra[-2000:], file=sys.stderr)
    sys.exit(1)


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if check and r.returncode != 0:
        fail(f"falhou: {' '.join(str(c) for c in cmd[:8])}", r.stdout + r.stderr)
    return r


def strip_tags(html):
    text = re.sub(r"<br\s*/?>", " ", html or "")
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", text.replace("&nbsp;", " ")).strip()


# ---------------------------------------------------------------- plano

def avisar_sotaque(cfg):
    """Roteiro em ingles com o dicionario de aportuguesar ligado reescreve palavra inglesa.

    O dicionario da terras-audio existe para termo ingles dentro de frase portuguesa
    ("cache" -> "kêsh", "queue" -> "kiu"). Num roteiro que ja esta em ingles ele
    destruiria a fala, porque metade das entradas e palavra comum em ingles. Quem narra
    em ingles declara `"sotaque": "nenhum"`. Medido em 2026-09-26 no video do carrossel
    do ADR em EN.
    """
    if not str(cfg.get("lang", "")).lower().startswith("en"):
        return
    padrao = brand_tokens().get("audio_video", {})
    if (cfg.get("sotaque") or padrao.get("sotaque") or "nenhum") == "aportuguesar":
        print("AVISO: roteiro em ingles com sotaque aportuguesar. O dicionario reescreve "
              "palavra inglesa comum na fala (cache -> kêsh, queue -> kiu); declare "
              '"sotaque": "nenhum" neste roteiro.')


def cmd_plan(cfg, out_dir, roteiro_path=None):
    os.makedirs(out_dir, exist_ok=True)
    lines = [
        f"# Roteiro: {cfg.get('titulo', 'sem titulo')}",
        "",
        f"Voz: {cfg.get('voice', VOZ_PADRAO)} (ritmo {cfg.get('rate', RITMO_PADRAO)})  ",
        f"Formato: {linha_formato(cfg)}  ",
        f"Blocos: {len(cfg['blocks'])}  ",
        f"Aprovado: {'sim' if cfg.get('aprovado') else 'NAO'}",
        "",
        "Confira o texto falado e o texto de tela antes de mandar renderizar.",
        "",
    ]
    for i, b in enumerate(cfg["blocks"], start=1):
        if b.get("slide"):
            cabeca = [f"## Bloco {i} (slide)", "",
                      f"- **Na tela:** slide `{os.path.basename(str(b['slide']))}`"]
        else:
            cabeca = [f"## Bloco {i} ({b.get('layout', 'abertura')})", "",
                      f"- **Na tela:** {strip_tags(b.get('headline', ''))}"]
            if b.get("sub"):
                cabeca.append(f"  - apoio: {strip_tags(b['sub'])}")
            for item in b.get("list", []) or []:
                cabeca.append(f"  - item: {strip_tags(item)}")
            for stat in b.get("stats", []) or []:
                cabeca.append(f"  - numero: {stat[0]} {strip_tags(stat[1])}")
            if b.get("foot") or cfg.get("foot"):
                cabeca.append(f"  - rodape: {b.get('foot', cfg.get('foot', ''))}")
        palavras = len(strip_tags(b["narration"]).split())
        lines += cabeca + ["", f"- **Falado ({palavras} palavras, ~{palavras / 2.6:.0f}s):** {b['narration']}", ""]
    md = "\n".join(lines) + "\n"
    md_path = os.path.join(out_dir, "roteiro.md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)
    print(f"--- roteiro salvo em {md_path}")
    if str(cfg.get("lang", "")).lower().startswith("en"):
        # O detector da terras-audio procura termo ingles dentro de frase portuguesa;
        # num roteiro todo em ingles ele lista "the", "with", "what" e vira ruido.
        print("-- pronuncia: roteiro em ingles, o relatorio de termos ingleses nao se "
              "aplica (quem manda na fala e a propria voz EN) --")
    else:
        try:
            alvo = roteiro_path or os.path.join(out_dir, "roteiro.json")
            r = subprocess.run([sys.executable, cli_de_audio(), "relatorio", alvo],
                               capture_output=True, text=True)
            print((r.stdout or r.stderr).strip())
        except Exception as e:
            print(f"AVISO: relatorio de pronuncia nao rodou: {e}", file=sys.stderr)
    if not cfg.get("aprovado"):
        print("Renderize somente depois de aprovar: python3 build.py aprovar roteiro.json")


def cmd_aprovar(cfg, path):
    cfg["aprovado"] = True
    cfg["aprovado_em"] = datetime.datetime.now().isoformat(timespec="seconds")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, ensure_ascii=False, indent=2)
    print(f"aprovado em {cfg['aprovado_em']}: {path}")


# ---------------------------------------------------------------- cartelas

def formato_de(cfg):
    """Resolve o formato e o canvas do roteiro.

    O `size` explicito ganha do `formato`, e sem nenhum dos dois vale o horizontal.
    `shorts` e `vertical` sao o mesmo formato: muda o nome que o roteiro usa.
    """
    tamanho = cfg.get("size")
    if not tamanho:
        nome = (cfg.get("formato") or "horizontal").lower()
        if nome not in FORMATOS:
            fail(f"formato desconhecido: {nome}. Use um de {sorted(FORMATOS)}")
        tamanho = FORMATOS[nome]
    try:
        width, height = (int(x) for x in str(tamanho).split("x"))
    except ValueError:
        fail(f"size invalido: {tamanho}. Use LARGURAxALTURA, ex.: 1080x1920")
    if height > width:
        nome = (cfg.get("formato") or "").lower()
        if nome == "carrossel":
            return "carrossel", width, height
        return ("shorts" if nome in ("shorts", "vertical") else "vertical"), width, height
    return ("quadrado" if height == width else "horizontal"), width, height


def e_vertical(cfg):
    return formato_de(cfg)[0] in ("shorts", "vertical")


def e_shorts(cfg):
    """Canvas em pe de player (Shorts/Reels): faixa segura e teto de 3 min valem aqui.

    O carrossel tambem e um canvas em pe, mas nao vive em player de vertical: o slide
    ja e a pagina inteira e o destino e o feed do LinkedIn. Por isso ele fica fora da
    conta de area segura e do limite de duracao dos Shorts.
    """
    if (cfg.get("formato") or "").lower() == "carrossel":
        return False
    _, width, height = formato_de(cfg)
    return height > width


def metrics(width, height):
    """Escala de video: o tipo e fracao do **menor eixo**.

    Antes a escala era `min(w/1920, h/1080)`, que servia para 16:9 e atrapalhava o
    resto: em 1080x1920 ela dava 0,5625 e a manchete saia com 59px, que no celular
    nao se le. No menor eixo a manchete fica sempre com 9,6% dele (104px em 1080), que
    e o que mantem o tamanho aparente igual em qualquer canvas. Para 16:9 os dois
    criterios dao o mesmo numero, entao o horizontal nao mudou.
    """
    s = min(width, height) / 1080
    return {
        "W": width,
        "H": height,
        "S": s,
        "PAD": round(96 * s),
        "PAD_FOOT": round(72 * s),
        "EYE_SIZE": round(26 * s),
        "EYE_GAP": round(18 * s),
        "EYE_RULE": round(52 * s),
        "H1_SIZE": round(104 * s),
        "H1_MAX": round(width - 2 * 96 * s),
        "SUB_SIZE": round(40 * s),
        "SUB_TOP": round(34 * s),
        "SUB_MAX": round((width - 2 * 96 * s) * 0.86),
        "LIST_SIZE": round(42 * s),
        "LIST_GAP": round(22 * s),
        "LIST_INDENT": round(40 * s),
        "LIST_DASH": round(22 * s),
        "STAT_N": round(96 * s),
        "STAT_L": round(28 * s),
        "STAT_GAP": round(48 * s),
        "FOOT_SIZE": round(24 * s),
        "DECO_BAR": round(10 * s),
        "DECO_PAD": round(34 * s),
        "SAFE_TOP": 0,          # no horizontal o quadro inteiro e do conteudo
        "SAFE_BOTTOM": 0,
        "H1_LINHAS_MAX": 4,
    }


def faixa_segura(height):
    """A faixa em que a cartela em pe pode ser DESENHADA, ja descontado o zoom.

    O motor de movimento amplia a cartela ate ZOOM_END sobre o centro do quadro, entao
    texto desenhado na borda da faixa do player sai da faixa quando o video anda: no
    teste de 2026-09-20 o cabecalho em y=230 virava y=187, dentro da area da interface,
    e a assinatura em y=1370 virava 1394. Nenhuma checagem de encaixe pega isso, porque
    a cartela parada esta certa; quem pega e o gate visual nos quadros do video.

    Por isso a faixa desenhada e a faixa do player encolhida pelo zoom, medida a partir
    do centro do quadro: assim, no instante de maior ampliacao, o conteudo esta
    exatamente na borda da area livre.
    """
    centro = height / 2
    folga = height * SAFE_FOLGA_FRAC
    topo_player = height * SAFE_TOPO_FRAC + folga
    base_player = height * (1 - SAFE_BASE_FRAC) - folga
    topo = centro - (centro - topo_player) / ZOOM_END
    base = centro + (base_player - centro) / ZOOM_END
    return round(topo), round(base)


def metrics_vertical(width, height):
    """Medidas do vertical: mesma tipografia do horizontal, mais a area segura.

    O tipo ja sai certo pela escala do menor eixo (ver `metrics`); o que muda aqui e
    o layout, porque a tela em pe e estreita e comprida:

    - margem lateral de 84px (contra 96 do horizontal), que em 1080 de largura
      devolve 912px de coluna;
    - manchete de ate 5 linhas, porque a coluna e estreita e sobra altura;
    - numeros empilhados um por linha, com o valor a esquerda e o rotulo ao lado:
      tres numeros lado a lado em 912px viram tres colunas apertadas.
    """
    m = dict(metrics(width, height))
    s = m["S"]
    m["PAD"] = round(84 * s)
    m["H1_MAX"] = width - 2 * m["PAD"]
    m["SUB_MAX"] = round((width - 2 * m["PAD"]) * 0.94)
    m["H1_LINHAS_MAX"] = 5
    m["LIST_SIZE"] = round(46 * s)
    m["LIST_GAP"] = round(30 * s)
    m["STAT_N_MIN"] = round(150 * s)     # alinha os rotulos dos numeros empilhados
    m["STAT_GAP_V"] = round(30 * s)      # respiro entre numeros empilhados
    topo, base = faixa_segura(height)
    m["SAFE_TOP"] = topo
    m["SAFE_BOTTOM"] = height - base
    return m


def metrics_do_formato(cfg):
    """As medidas do canvas pedido no roteiro, no formato certo."""
    _, width, height = formato_de(cfg)
    return metrics_vertical(width, height) if height > width else metrics(width, height)


def linha_formato(cfg):
    """Uma linha dizendo o formato, o canvas e, no vertical, onde o texto pode ficar."""
    nome, width, height = formato_de(cfg)
    if not e_shorts(cfg):
        return f"{nome} {width}x{height}"
    livre_topo, livre_base = faixa_segura(height)
    return (f"{nome} {width}x{height} | a interface dos Shorts cobre fora de "
            f"y {round(height * SAFE_TOPO_FRAC)} a {round(height * (1 - SAFE_BASE_FRAC))}; "
            f"a cartela e desenhada de {livre_topo} a {livre_base} para o zoom de "
            f"{round((ZOOM_END - 1) * 100)}% nao empurrar o texto para dentro dela")


def brand_tokens():
    try:
        with open(os.path.join(BRAND_DIR, "brand.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def build_html_canal(cfg, block, index, total, html_path, cores, fonte):
    """Cartela de canal: o layout do title card dele, com painel de foto e HUD."""
    tokens = brand_tokens()
    tema = (tokens.get("temas") or {}).get(cfg.get("tema") or "pessoal") or {}
    canal = tema.get("canal") or {}
    url_tema, rotulo_tema = assinatura_do_tema(cfg)
    width, height = formato_de(cfg)[1:]
    vertical = height > width
    mono = (tema.get("fontes") or {}).get("mono") or {"nome": "JetBrains Mono",
           "arquivos": ["fonts/jetbrains-mono-latin.woff2"]}
    faces, stack = font_faces(fonte)
    mono_faces, mono_stack = font_faces(mono)
    accent = cfg.get("accent") or cores.get("acento") or "#22d3ee"
    marca = canal.get("marca") or ["terras", "IA"]
    foto = block.get("foto") or cfg.get("foto") or canal.get("foto") or ""
    foto_css = f"url('file://{os.path.join(BRAND_DIR, foto)}')" if foto else "none"
    values = dict(metrics_canal_vertical(width, height) if vertical
                  else metrics_canal(width, height))
    values.update({
        "LANG": cfg.get("lang", "pt-BR"),
        "W": width, "H": height,
        "BASE": cores.get("base") or "#020617",
        "ACCENT": accent,
        "ACCENT2": cfg.get("accent2") or cores.get("acento_alt") or "#10bedb",
        "COR_TEXTO": cores.get("texto") or "#f8fafc",
        "COR_TEXTO_APOIO": cores.get("texto_apoio") or "#cad5e2",
        "COR_LABEL": cores.get("rotulo") or "#90a1b9",
        "COR_RODAPE": cores.get("rodape") or "#64748b",
        "COR_LINHA": cores.get("linha") or "#1e293b",
        "FONT_FACES": faces, "FONT_STACK": stack,
        "FONT_MONO_FACES": mono_faces, "FONT_MONO": mono_stack,
        "BG": "none",
        "KICKER": block.get("kick", cfg.get("kick", "")),
        "KICKER_LABEL": block.get("kick_label", cfg.get("kick_label", "")),
        "PILL_ICON": "",   # o ponto separador ja vem do rotulo; a referencia nao tem ponto dentro da pill
        "WORDMARK": marca[0] if marca else "",
        "WORDMARK_ALT": (" " + marca[1]) if len(marca) > 1 else "",
        "HEADLINE": block.get("headline", ""),
        "SUB": block.get("sub", ""),
        "STATS": "".join(
            f"<div class='stat'><span class='n'>{x[0]}</span><span class='l'>{x[1]}</span></div>"
            for x in block.get("stats", [])),
        "FOOT_LABEL": block.get("foot_label", cfg.get("foot_label", rotulo_tema)),
        # ASSINATURA e o texto do endereco; FOOT_URL e o tamanho dele na escala. Antes
        # os dois usavam a mesma chave e o texto caia dentro do `font-size`, que o
        # navegador descarta em silencio: a assinatura saia no corpo do texto, 16px.
        "ASSINATURA": block.get("foot", cfg.get("foot", url_tema)),
        "FOTO": foto_css,
        "HUD": block.get("hud", cfg.get("hud", canal.get("hud", ""))),
        "COUNTER": f"{index:02d} / {total:02d}" if cfg.get("counter", False) else "",
    })
    with open(TEMPLATE_CANAL_VERTICAL if vertical else TEMPLATE_CANAL, encoding="utf-8") as fh:
        html = fh.read()
    for key, value in values.items():
        html = html.replace("{{%s}}" % key, str(value))
    leftover = re.findall(r"\{\{(\w+)\}\}", html)
    if leftover:
        fail(f"placeholders sem valor no card de canal: {sorted(set(leftover))}")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return html_path


def load_template(caminho=None):
    caminho = caminho or TEMPLATE
    if not os.path.exists(caminho):
        fail(
            f"template nao encontrado em {caminho}.\n"
            "O diretorio padrao da identidade sumiu ou mudou de lugar.\n"
            f"Recriar o que falta: bash {os.path.join(SKILL_DIR, 'scripts', 'setup-brand.sh')}"
        )
    with open(caminho, encoding="utf-8") as fh:
        return fh.read()



def assinatura_do_tema(cfg):
    """URL e rotulo da assinatura do rodape, tirados do tema do roteiro.

    A assinatura e da identidade, nao de cada roteiro: o canal e o produto assinam
    `terrasia.app` (decisao dele em 2026-09-20, "o rodape nao vai ter esse endereco e
    sim https://terrasia.app") e o tema pessoal assina a newsletter, que e o endereco
    dos posts. O tema declara isso em `temas.<nome>.canal.foot` e `foot_label`, ou em
    `temas.<nome>.rodape`.

    Antes as duas cartelas caiam direto no `assinatura` global do brand.json, que e a
    newsletter e existe para o banner: o short do Jev saiu com o endereco dos posts no
    rodape do canal, e o mesmo valia para qualquer video. O roteiro sobrepoe com `foot`
    quando o video aponta para outro lugar.
    """
    tokens = brand_tokens()
    tema = (tokens.get("temas") or {}).get(cfg.get("tema") or "pessoal") or {}
    canal = tema.get("canal") or {}
    rodape = tema.get("rodape") or {}
    return (canal.get("foot") or rodape.get("url") or tokens.get("assinatura") or "",
            canal.get("foot_label") or rodape.get("rotulo") or "")


def tema_do_roteiro(cfg):
    """Resolve cores e fonte do tema pedido no roteiro.

    `pessoal` e o padrao (navy com ambar, Inter). `terrasia` e o tema do produto,
    extraido de packages/ui/src/colors.ts e do index.css do client no harness:
    base quase preta com neon ciano e verde sobre JetBrains Mono. Cores do tema
    sobrepoem as de topo; `base` e `accent` no roteiro ainda ganham de tudo.
    """
    tokens = brand_tokens()
    nome = cfg.get("tema") or "pessoal"
    tema = (tokens.get("temas") or {}).get(nome) or {}
    cores = {**(tokens.get("cores") or {}), **(tema.get("cores") or {})}
    fonte = (tema.get("fontes") or tokens.get("fontes") or {}).get("principal") or {
        "nome": "Inter", "arquivos": ["fonts/inter-latin.woff2"]}
    return nome, cores, fonte


def font_faces(fonte):
    """@font-face apontando para os arquivos do diretorio padrao, e a familia CSS."""
    faces = []
    for arquivo in fonte.get("arquivos", []):
        faces.append(
            "  @font-face {\n"
            f"    font-family: '{fonte['nome']}';\n"
            f"    src: url('file://{os.path.join(BRAND_DIR, arquivo)}') format('woff2');\n"
            "    font-weight: 100 900; font-style: normal; font-display: block;\n"
            "  }")
    fallback = "monospace" if "Mono" in fonte["nome"] else "sans-serif"
    return "\n".join(faces), f"'{fonte['nome']}', {fallback}"


def metrics_canal(width, height):
    """Medidas tiradas do title card do canal, na escala de 1920x1080.

    Em canvas pequeno (thumbnail) o fator sobe 20% so na manchete e no apoio, que sao
    o que precisa ler de longe. A regua do rodape e a assinatura ficam na escala
    normal: aumentar tudo estoura a linha de dados, que foi o que a checagem pegou.
    O card de origem e mockup, nao especificacao.

    A escala e a mesma do `metrics`: fracao do menor eixo, para o tipo nao encolher no
    vertical.
    """
    s = min(width, height) / 1080
    st = s * 1.2 if height <= 800 else s
    return {
        "PAD": round(96 * s), "PAD_BOTTOM": round(112 * s),
        # O painel manda na coluna: na referencia ele ocupa 31% da largura, e o que
        # sobra menos as margens e o que o texto tem. Com a conta antiga o 1280x720
        # ficava com 589px de coluna para um rodape de 648px.
        "GAP": round(14 * s),
        "PANEL_W": round(0.31 * width),
        "COL_W": round(width - 0.31 * width - 96 * s),
        "PANEL_R": round(24 * s),
        "PILL_H": round(40 * s), "PILL_SIZE": round(15 * s), "PILL_GAP": round(10 * s),
        "PILL_PAD_V": round(9 * s), "PILL_PAD_H": round(18 * s), "PILL_DOT": round(7 * s),
        "LABEL_SIZE": round(15 * s), "MARK_SIZE": round(17 * s),
        "H1_SIZE": round(92 * st), "H1_LH": 1.04, "H1_MAX": round(1020 * s),
        "SUB_SIZE": round(34 * st), "SUB_TOP": round(34 * s), "SUB_MAX": round(900 * s),
        "BAR_W": round(4 * s), "BAR_PAD": round(22 * s),
        "STAT_N": round(46 * s), "STAT_L": round(16 * s), "STAT_GAP": round(46 * s),
        "STAT_INNER": round(8 * s),
        "FOOT_L": round(14 * s), "FOOT_URL": round(22 * s), "MAIN_GAP": round(56 * s),
        "HUD_SIZE": round(14 * st), "HUD_LEFT": round(18 * s), "HUD_BOTTOM": round(18 * s),
        "CONT_RIGHT": round(0.31 * width + 96 * s + 28 * s),
        "H1_LINHAS_MAX": 3,
        "SAFE_TOP": 0, "SAFE_BOTTOM": 0,
    }


def metrics_canal_vertical(width, height):
    """Card de canal em pe: sem painel lateral, a foto vira o fundo do quadro.

    O painel de 31% da largura nao cabe numa tela de 1080: ele viraria um selo
    espremido ao lado de uma coluna de 650px. Em pe a foto vai para o fundo, com o
    veu do template por cima, e a coluna de texto usa a largura toda.
    """
    m = dict(metrics_canal(width, height))
    s = min(width, height) / 1080
    m["PAD"] = round(84 * s)
    m["COL_W"] = width - 2 * m["PAD"]
    m["H1_SIZE"] = round(96 * s)
    m["H1_MAX"] = m["COL_W"]
    m["SUB_MAX"] = m["COL_W"]
    m["MAIN_GAP"] = round(40 * s)
    m["STAT_GAP_V"] = round(30 * s)
    m["STAT_N_MIN"] = round(110 * s)
    m["H1_LINHAS_MAX"] = 4
    topo, base = faixa_segura(height)
    m["SAFE_TOP"] = topo
    m["SAFE_BOTTOM"] = height - base
    return m


def build_html(cfg, block, index, total, html_path):
    _, cores, fonte = tema_do_roteiro(cfg)
    url_tema, _ = assinatura_do_tema(cfg)
    base = cfg.get("base") or cores.get("base") or "#05090f"
    accent = cfg.get("accent") or cores.get("acento") or "#ffcc33"
    faces, stack = font_faces(fonte)
    r, g, b = (int(accent.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    m = metrics_do_formato(cfg)
    if block.get("layout") == "canal":
        return build_html_canal(cfg, block, index, total, html_path, cores, fonte)
    values = dict(m)
    values.update({
        "LANG": cfg.get("lang", "pt-BR"),
        "BASE": base,
        "ACCENT": accent,
        "ACCENT_RGBA": f"rgba({r},{g},{b},0.13)",
        "ACCENT_RGBA_SOFT": f"rgba({r},{g},{b},0.07)",
        "SCRIM_CSS": "none",
        "BG": f"url('file://{os.path.abspath(cfg['art'])}')" if cfg.get("art") else "none",
        "FONT_FACES": faces,
        "FONT_STACK": stack,
        "COR_TEXTO": cores.get("texto") or "#f8fafc",
        "COR_TEXTO_APOIO": cores.get("texto_apoio") or "#b8c4d4",
        "COR_TEXTO_LISTA": cores.get("texto_lista") or cores.get("texto") or "#e2e8f0",
        "COR_LINHA": cores.get("linha") or "#1e293b",
        "COR_RODAPE": cores.get("rodape") or cores.get("texto_apoio") or "#64748b",
        "LAYOUT": block.get("layout", "abertura"),
        "FONTS_DIR": FONTS_DIR,
        "KICKER": block.get("kick", cfg.get("kick", "")),
        "HEADLINE": block.get("headline", ""),
        "SUB": block.get("sub", ""),
        "LIST": ("<ul class='list'>" + "".join(f"<li>{i}</li>" for i in block["list"]) + "</ul>") if block.get("list") else "",
        "STATS": ("<div class='stats'>" + "".join(
            f"<div class='stat'><span class='n'>{s[0]}</span><span class='l'>{s[1]}</span></div>" for s in block["stats"]
        ) + "</div>") if block.get("stats") else "",
        "FOOT": block.get("foot", cfg.get("foot", url_tema)),
        "COUNTER": f"{index:02d} / {total:02d}" if cfg.get("counter", True) else "",
    })
    html = load_template(TEMPLATE_VERTICAL if e_vertical(cfg) else TEMPLATE)
    for key, value in values.items():
        html = html.replace("{{%s}}" % key, str(value))
    leftover = re.findall(r"\{\{(\w+)\}\}", html)
    if leftover:
        fail(f"placeholders sem valor: {sorted(set(leftover))}")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return html_path


def render_card(cfg, block, index, total, png_path):
    html_path = build_html(cfg, block, index, total, png_path.replace(".png", ".html"))
    chrome = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or fail("sem Chrome no PATH")
    common = ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-sandbox", "--virtual-time-budget=3000"]
    dom = run([chrome, *common, "--dump-dom", f"file://{html_path}"])
    m = re.search(r"<title>(.*?)</title>", dom.stdout, re.S)
    if not m:
        fail("a cartela nao devolveu relatorio de encaixe")
    verdict = m.group(1).strip()
    if verdict.startswith("FALHA"):
        fail(f"cartela {index}: {verdict}")
    _, width, height = formato_de(cfg)
    run([chrome, *common, f"--window-size={width},{height}", f"--screenshot={png_path}", f"file://{html_path}"])
    return png_path


# ---------------------------------------------------------------- voz e montagem

def narra(texto, voz, ritmo, saida_wav, sotaque="nenhum"):
    """Delega a narracao para a skill terras-audio (voz, pronuncia e cadeia)."""
    cmd = [sys.executable, cli_de_audio(), "narrar", "--texto", texto,
           "--saida", saida_wav, "--voz", voz, "--ritmo", ritmo, "--alvo", "video"]
    if sotaque and sotaque != "nenhum":
        cmd += ["--sotaque", sotaque]
    run(cmd)
    return saida_wav


def duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        fail(f"sem duracao para {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def loudness(path):
    """LUFS integrado e pico verdadeiro, que e a unidade que o YouTube usa."""
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", path,
                        "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    lufs = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", r.stderr)
    peak = re.findall(r"Peak:\s+(-?[\d.]+)\s+dBFS", r.stderr)
    return (float(lufs[-1]) if lufs else None, float(peak[-1]) if peak else None)


def carregar_cena(caminho):
    """Importa um modulo de cenas externo (ex.: o gerador do terrasia).

    Convencao esperada do modulo, a mesma do harness: `base_image()` devolve
    `(img, draw)` em RGB, e a funcao de cena recebe `(img, draw, t)` e devolve uma
    lista de overlays RGBA (ou nada). Opcionalmente o modulo define `BG`, `W`, `H`
    e `SCENES`.
    """
    if not os.path.exists(caminho):
        fail(f"modulo de cena nao encontrado: {caminho}\n"
             "No harness do terrasia ele vive em "
             "/srv/server-01/harness/terrasia/video-terrasia/gen_video.py "
             "(o mount sshfs precisa estar de pe).")
    spec = importlib.util.spec_from_file_location("terras_video_cena", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def fabrica_de_imagem(card, width, height, zoom_end=ZOOM_END):
    """Imagem parada com zoom lento: o motor proprio da skill.

    Vale para a cartela renderizada no Chrome e para o slide do deck (terras-banner),
    que entra pelo mesmo caminho: uma pagina pronta que so respira. O `zoom_end` e o
    teto da ampliacao, aplicado com easing ease-out sobre o centro do quadro.
    """
    from PIL import Image

    big = card.resize((width * MOTION_SCALE, height * MOTION_SCALE), Image.LANCZOS)
    zoom_frames = max(int(ZOOM_SECONDS * FPS), 1)

    def quadro(i, total):
        t = min(i / zoom_frames, 1.0)
        z = 1 + (zoom_end - 1) * (1 - (1 - t) ** 2)          # ease-out: acelera e assenta
        bw, bh = width * MOTION_SCALE / z, height * MOTION_SCALE / z
        left, top = (width * MOTION_SCALE - bw) / 2, (height * MOTION_SCALE - bh) / 2
        return big.resize((width, height), Image.BOX, box=(left, top, left + bw, top + bh))

    return quadro, zoom_frames


def fabrica_de_cartela(card_png, width, height):
    """Cartela renderizada pelo Chrome, com o zoom padrao."""
    from PIL import Image

    return fabrica_de_imagem(Image.open(card_png).convert("RGB"), width, height)


def ajustar_ao_canvas(img, width, height, modo="encaixar"):
    """Encaixa o quadro de uma cena externa no canvas do video.

    O gerador do terrasia desenha no tamanho dele, 1920x1080. Escrever esse quadro cru
    no pipe do ffmpeg de um canvas em pe desalinha o fluxo e sai video embaralhado, sem
    erro nenhum: por isso o encaixe nao e opcional.

    `encaixar` (padrao) mostra a cena inteira, centrada, sobre um fundo desfocado dela
    mesma, que e o que o feed faz com material horizontal. `preencher` corta as laterais
    e enche o quadro, para a cena que tolera corte.
    """
    from PIL import Image, ImageEnhance, ImageFilter

    if img.size == (width, height):
        return img
    if modo == "preencher":
        escala = max(width / img.width, height / img.height)
        nova = img.resize((max(round(img.width * escala), width),
                           max(round(img.height * escala), height)), Image.LANCZOS)
        esq, topo = (nova.width - width) // 2, (nova.height - height) // 2
        return nova.crop((esq, topo, esq + width, topo + height))

    # O fundo sai de uma copia pequena: borrar 1080x1920 quadro a quadro custaria caro
    # e o resultado seria o mesmo, porque borrao nao tem detalhe para preservar.
    escala = min(width / img.width, height / img.height)
    dentro = img.resize((max(round(img.width * escala), 1),
                         max(round(img.height * escala), 1)), Image.LANCZOS)
    pequeno = img.resize((max(width // 12, 1), max(height // 12, 1)), Image.BOX)
    fundo = pequeno.filter(ImageFilter.GaussianBlur(8)).resize((width, height), Image.BILINEAR)
    fundo = ImageEnhance.Brightness(fundo).enhance(0.4)
    fundo.paste(dentro, ((width - dentro.width) // 2, (height - dentro.height) // 2))
    return fundo


def abre_slide(caminho, width, height, ajuste="preencher"):
    """Abre um slide do deck e o encaixa no canvas do video se o tamanho diferir.

    O certo e o roteiro do carrossel usar o mesmo tamanho do deck (1080x1440), e nesse
    caso a imagem passa direto. Quando difere, o slide e tratado como cena externa: o
    encaixe e obrigatorio, senao o quadro de tamanho diferente desalinha o pipe do
    ffmpeg e sai video embaralhado, sem erro nenhum.
    """
    from PIL import Image

    img = Image.open(caminho).convert("RGB")
    if img.size == (width, height):
        return img
    print(f"  aviso: slide {img.size[0]}x{img.size[1]} encaixado em {width}x{height} "
          f"({ajuste}); deck e roteiro deveriam ter o mesmo tamanho")
    return ajustar_ao_canvas(img, width, height, ajuste)


def resolver_arquivo(caminho, base_dir):
    """Resolve o caminho de um arquivo citado no roteiro.

    Relativo ao diretorio do roteiro, nao ao diretorio de onde o shell chamou: o
    roteiro do carrossel aponta para os slides que ficam ao lado dele.
    """
    p = os.path.expanduser(str(caminho))
    if not os.path.isabs(p):
        p = os.path.join(base_dir, p)
    if not os.path.exists(p):
        fail(f"arquivo do roteiro nao encontrado: {caminho} (procurado em {p})")
    return p


def fabrica_de_cena(modulo, funcao, duracao, width, height, ajuste="encaixar"):
    """Cena desenhada por modulo externo: a animacao e a do modulo, sem zoom nosso."""
    from PIL import Image, ImageDraw

    desenha = getattr(modulo, funcao, None)
    if desenha is None:
        fail(f"a cena '{funcao}' nao existe no modulo carregado")
    if hasattr(modulo, "base_image"):
        amostra, _ = modulo.base_image()
        if amostra.size != (width, height):
            print(f"  cena {funcao}: quadro {amostra.size[0]}x{amostra.size[1]} do modulo "
                  f"encaixado em {width}x{height} ({ajuste})")

    def quadro(i, total):
        if hasattr(modulo, "base_image"):
            img, d = modulo.base_image()
        else:
            img = Image.new("RGB", (width, height), getattr(modulo, "BG", (13, 17, 23)))
            d = ImageDraw.Draw(img)
        t = (i / max(total - 1, 1)) * duracao
        overlays = desenha(img, d, t) or []
        if not isinstance(overlays, list):
            overlays = [overlays]
        for ov in overlays:
            if ov is not None:
                img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
        return ajustar_ao_canvas(img, width, height, ajuste)

    return quadro, 0   # sem janela propria de movimento: a medicao nao se aplica


def segment(wav, out, dur, width, height, fabrica, medir_movimento=True, rotulo="trecho"):
    """Escreve os quadros da fabrica no ffmpeg, casados com a narracao.

    Devolve as estatisticas de movimento medidas no quadro anterior ao fade, para
    que a medida seja do movimento e nao do escurecimento. Cena externa nao mede:
    a animacao e do modulo, com entradas e saltos propositais.
    """
    from PIL import Image, ImageChops, ImageStat

    quadro, janela_movimento = fabrica
    black = Image.new("RGB", (width, height), (0, 0, 0))
    total_frames = max(int(dur * FPS), 1)
    fade_in_frames = max(int(FADE_IN * FPS), 1)
    fade_out_frames = max(int(FADE_OUT * FPS), 1)

    # apad=whole_dur preenche a fala ate a duracao do bloco. Sem isso o -shortest
    # encerra o trecho no fim do audio e corta o resto do video: era o que truncava
    # a cauda da animacao das cenas externas (cena de 14s com fala de 8,7s virava
    # 8,7s de video). Nao somar esse respiro tambem do lado do video.
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
           "-framerate", str(FPS), "-i", "-", "-i", wav,
           "-af", f"apad=whole_dur={dur:.3f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest", out]
    err_file = out + ".ffmpeg.log"
    with open(err_file, "w") as err:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=err)
        deltas = []
        prev = None
        try:
            for i in range(total_frames):
                frame = quadro(i, total_frames)
                if medir_movimento and i < janela_movimento:
                    small = frame.convert("L").resize(
                        (max(round(width * FATOR_AMOSTRA), 1),
                         max(round(height * FATOR_AMOSTRA), 1)), Image.BILINEAR)
                    # A medida comeca depois do aquecimento. Os primeiros quadros ficam
                    # quase pretos (alfa do fade de entrada em 0 e 0,05) e a caixa de
                    # recorte deles ainda anda na borda da grade de reamostragem do PIL,
                    # o que produz um salto que nao existe no video. Medido no vertical:
                    # o jerk caia de 1,81 (reprovando) para 0,58 com o aquecimento fora,
                    # e o horizontal ficava igual (0,52), que e o que se quer: o mesmo
                    # movimento medindo o mesmo nos dois formatos.
                    if prev is not None and i > QUADROS_AQUECIMENTO:
                        deltas.append(ImageStat.Stat(ImageChops.difference(small, prev)).mean[0])
                    prev = small
                alpha = min(i / fade_in_frames, (total_frames - 1 - i) / fade_out_frames, 1.0)
                if alpha < 1.0:
                    frame = Image.blend(black, frame, alpha)      # fade para preto nas pontas
                proc.stdin.write(frame.tobytes())
        except BrokenPipeError:
            pass  # ffmpeg encerrou o trecho (audio acabou antes dos ultimos quadros)
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass
        proc.wait()

    if proc.returncode != 0:
        fail(f"ffmpeg recusou o trecho {out}", open(err_file).read())

    if not medir_movimento:
        return {"externo": True, "ok": True}

    ordered = sorted(deltas)
    med = ordered[len(ordered) // 2] if ordered else 0.0
    # O que faz o movimento parecer picado nao e andar pouco, e andar irregular: um
    # quadro que muda quase nada seguido de outro que salta. Medido: a versao com
    # zoompan deu jerk de 5,37x a mediana; o motor PIL, 0,30x.
    jerks = [abs(deltas[i + 1] - deltas[i]) for i in range(len(deltas) - 1)]
    jerk = (max(jerks) / med) if med > 0 and jerks else 0.0
    stalls = sum(1 for d in deltas if med > 0 and d < med * 0.2)
    return {"jerk": round(jerk, 2), "mediana": round(med, 3), "quadros_quase_parados": stalls,
            "ok": jerk <= JERK_MAX}


# ---------------------------------------------------------------- custo

CHARS_POR_SEGUNDO = 12.5      # medido com a Francisca a -8%, no texto da casa
MAQUINA_S_POR_S = 3.5         # medido: 3,0 a 3,9 s de maquina por segundo de video
TOKENS_POR_CHAR = 0.25        # convencao chars/4 do terrasia, para provider que nao reporta


def medir_custo(cfg):
    """Conta o que da para contar antes de renderizar: fala, maquina, arte e tokens.

    O que e determinístico sai exato (caracteres, quadros, minutos de maquina). O
    que depende do modelo vem da referencia medida, porque nao existe como saber
    antes quantas chamadas o trabalho do agente vai consumir.
    """
    blocos = cfg.get("blocks", [])
    por_bloco = []
    for i, b in enumerate(blocos, start=1):
        fala = strip_tags(b.get("narration", ""))
        segundos = len(fala) / CHARS_POR_SEGUNDO
        if b.get("cena"):
            dur = max(segundos + 0.6, float(b["cena"].get("duracao", segundos + 0.6)))
            tipo = f"cena {b['cena'].get('funcao', '?')}"
        elif b.get("slide"):
            dur = segundos + 0.6
            tipo = f"slide {os.path.basename(str(b['slide']))}"
        else:
            dur = segundos + 0.6
            tipo = b.get("layout", "cartela")
        por_bloco.append({"bloco": i, "tipo": tipo, "chars": len(fala),
                          "fala_s": round(segundos, 1), "duracao_s": round(dur, 1)})
    total_chars = sum(x["chars"] for x in por_bloco)
    total_s = sum(x["duracao_s"] for x in por_bloco)
    maquina_s = total_s * MAQUINA_S_POR_S
    tokens_estimados = int(total_chars * TOKENS_POR_CHAR)
    artes = 1 if cfg.get("art") else 0
    custo = brand_tokens().get("custo", {})
    voz_preco = float((custo.get("voz") or {}).get("preco_por_1k_chars_usd") or 0.0)
    arte_preco = (custo.get("arte") or {}).get("preco_por_imagem_usd")
    usd_voz = total_chars / 1000 * voz_preco
    usd_arte = (artes * float(arte_preco)) if (artes and arte_preco) else 0.0
    nome, width, height = formato_de(cfg)
    return {"por_bloco": por_bloco, "chars": total_chars, "tokens_estimados": tokens_estimados,
            "video_s": round(total_s, 1), "maquina_min": round(maquina_s / 60, 1),
            "artes": artes, "usd_voz": round(usd_voz, 4), "usd_arte": round(usd_arte, 4),
            "formato": nome, "tamanho": f"{width}x{height}",
            "agente": custo.get("agente_referencia", {}), "quadros": int(total_s * FPS)}


def cmd_custo(cfg, out_dir):
    m = medir_custo(cfg)
    print("-- custo estimado antes de gerar --")
    print(f"  formato: {linha_formato(cfg)}")
    for b in m["por_bloco"]:
        print(f"  bloco {b['bloco']:>2} ({b['tipo']}): {b['chars']:>4} caracteres, "
              f"fala ~{b['fala_s']}s, bloco ~{b['duracao_s']}s")
    print(f"  narracao: {m['chars']} caracteres (~{m['tokens_estimados']} tokens por chars/4)")
    print(f"  video: ~{m['video_s']}s, {m['quadros']} quadros a {FPS}fps, "
          f"~{m['maquina_min']} min de maquina (custo local, zero)")
    print(f"  arte: {m['artes']} imagem(ns) de fundo")
    usd = m["usd_voz"] + m["usd_arte"]
    if usd:
        print(f"  voz+arte em dolar: US$ {usd:.4f} (voz US$ {m['usd_voz']:.4f}, arte US$ {m['usd_arte']:.4f})")
    else:
        print("  voz+arte em dolar: US$ 0 (edge-tts gratis e sem arte paga)")
    a = m["agente"] or {}
    if a:
        print(f"  tokens do agente: referencia medida em {a.get('medido_em', '?')} "
              f"({a.get('escopo', 'sem escopo declarado')}):")
        print(f"    {a.get('chamadas', '?')} chamadas | entrada nova {a.get('entrada_nova_tokens', 0):,} | "
              f"cache lido {a.get('entrada_cache_tokens', 0):,} | saida {a.get('saida_tokens', 0):,}")
        print(f"    e o unico item nao deterministico: depende de quantas chamadas o trabalho pedir. "
              f"Preco por Mtok vem da {a.get('tabela', 'tabela de pricing')}")
    return m


# ---------------------------------------------------------------- capa

def cmd_capa(cfg, out_dir, bloco=1, largura=1280, altura=720):
    """Gera a capa do YouTube (1280x720) a partir de um bloco do roteiro.

    A capa e o que decide o clique, entao ela e uma saida de primeira classe da
    skill, nao um passo esquecido: o `--exportar` do render copia ela junto. O
    tamanho 1280x720 e o que o YouTube usa, e o tipo sobe 20% em canvas pequeno
    (ver metrics_canal), o que ajuda justamente aqui.
    """
    if not cfg.get("blocks"):
        fail("roteiro sem blocos")
    i = max(1, min(bloco, len(cfg["blocks"])))
    b = dict(cfg["blocks"][i - 1])
    # a capa nao leva o texto falado, so o que aparece na tela
    b.pop("narration", None)
    tamanho_original = cfg.get("size")
    cfg["size"] = f"{largura}x{altura}"
    destino = os.path.join(out_dir, f"capa-{largura}x{altura}.png")
    os.makedirs(out_dir, exist_ok=True)
    try:
        render_card(cfg, b, i, len(cfg["blocks"]), destino)
    finally:
        if tamanho_original:
            cfg["size"] = tamanho_original
    print(f"capa: {destino} ({largura}x{altura}, do bloco {i} do roteiro)")
    return destino


# ---------------------------------------------------------------- render

def cmd_render(cfg, out_dir, sem_checagem, exportar=False, base_dir="."):
    if not cfg.get("aprovado"):
        fail("roteiro nao aprovado. Leia o roteiro e rode: python3 build.py aprovar roteiro.json")
    if not cfg.get("blocks"):
        fail("roteiro sem blocos")
    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    formato, width, height = formato_de(cfg)
    print(f"formato: {linha_formato(cfg)}")
    if formato == "carrossel":
        sem_slide = [i for i, b in enumerate(cfg["blocks"], start=1) if not b.get("slide")]
        if sem_slide:
            fail(f"o formato carrossel e montado com slides do deck (campo `slide`), e os "
                 f"blocos {sem_slide} nao tem slide. Cartela HTML nao entra aqui: o slide "
                 "ja e a pagina pronta que passou pelo gate da terras-banner.")
    if e_shorts(cfg):
        # Short acima de 3 minutos deixa de ser Short: o YouTube joga no player normal,
        # com as cartelas em pe num quadro horizontal. Melhor cortar o texto agora do
        # que descobrir depois de renderizar.
        estimado = medir_custo(cfg)["video_s"]
        if estimado > SHORTS_MAX_S:
            fail(f"o roteiro da ~{estimado:.0f}s, acima do limite de {SHORTS_MAX_S}s dos Shorts. "
                 "Corte texto (um bloco inteiro costuma resolver) ou assuma o video longo "
                 "com formato horizontal.")
    audio_padrao = brand_tokens().get("audio_video", {})
    voice = cfg.get("voice") or audio_padrao.get("voz") or VOZ_PADRAO
    rate = cfg.get("rate") or audio_padrao.get("ritmo") or RITMO_PADRAO
    sotaque = cfg.get("sotaque") or audio_padrao.get("sotaque") or "nenhum"

    parts = []
    motions = []
    falas_lufs = []
    modulos = {}
    for i, block in enumerate(cfg["blocks"], start=1):
        png = os.path.join(out_dir, f"cartela-{i}.png")
        wav = os.path.join(out_dir, f"narracao-{i}.wav")
        seg = os.path.join(out_dir, f"trecho-{i}.mp4")
        narra(block["narration"], voice, rate, wav, sotaque)
        fala = duration(wav)
        falas_lufs.append(loudness(wav)[0])
        cena = block.get("cena")
        slide = block.get("slide")
        if cena and slide:
            fail(f"bloco {i}: `cena` e `slide` no mesmo bloco; escolha um dos dois")
        if slide:
            # Slide do deck (terras-banner): a pagina pronta e o quadro inteiro. A copia
            # em cartela-<i>.png mantem a inspecao e o --exportar funcionando igual.
            caminho = resolver_arquivo(slide, base_dir)
            zoom = float(block.get("zoom", ZOOM_SLIDE))
            imagem = abre_slide(caminho, width, height, block.get("ajuste", "preencher"))
            dur = fala + 0.6
            imagem.save(png)
            fabrica = fabrica_de_imagem(imagem, width, height, zoom)
            motion = segment(wav, seg, dur, width, height, fabrica)
            corte_h = round(width * (1 - 1 / zoom) / 2)
            corte_v = round(height * (1 - 1 / zoom) / 2)
            print(f"bloco {i}: slide {os.path.basename(caminho)} | fala {fala:.2f}s | "
                  f"movimento {motion} | zoom {zoom:.2f} recua ~{corte_h}px nas laterais "
                  f"e ~{corte_v}px no topo/base")
        elif cena:
            # Cena desenhada por modulo externo (ex.: gerador do terrasia). A
            # duracao respeita o tempo que a animacao do modulo precisa.
            caminho = os.path.expanduser(cena["modulo"])
            if caminho not in modulos:
                modulos[caminho] = carregar_cena(caminho)
            desenhada = float(cena.get("duracao", fala + 0.6))
            dur = max(fala + 0.6, desenhada)
            fabrica = fabrica_de_cena(modulos[caminho], cena["funcao"], dur, width, height,
                                      cena.get("ajuste", "encaixar"))
            motion = segment(wav, seg, dur, width, height, fabrica, medir_movimento=False)
            print(f"bloco {i}: cena externa {cena['funcao']} | fala {fala:.2f}s | duracao {dur:.2f}s")
        else:
            render_card(cfg, block, i, len(cfg["blocks"]), png)
            dur = fala + 0.6
            fabrica = fabrica_de_cartela(png, width, height)
            motion = segment(wav, seg, dur, width, height, fabrica)
            print(f"bloco {i}: cartela ok | fala {fala:.2f}s | movimento {motion}")
        motions.append(motion)
        parts.append(seg)

    list_path = os.path.join(out_dir, "trechos.txt")
    with open(list_path, "w", encoding="utf-8") as fh:
        for p in parts:
            fh.write(f"file '{p}'\n")
    video = os.path.expanduser(cfg.get("out", os.path.join(out_dir, "video.mp4")))
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_path,
         "-c", "copy", "-movflags", "+faststart", video])

    total = duration(video)
    size_mb = os.path.getsize(video) / 1024 / 1024
    lufs, peak = loudness(video)
    medias = [x for x in falas_lufs if x is not None]
    lufs_fala = sum(medias) / len(medias) if medias else None
    print(f"VIDEO: {video} | {total:.1f}s | {width}x{height} | {size_mb:.1f} MB | montagem {time.time() - t0:.0f}s")
    if e_shorts(cfg):
        if total > SHORTS_MAX_S:
            print(f"ATENCAO: short de {total:.0f}s passou do limite de {SHORTS_MAX_S}s e o YouTube "
                  "nao vai classificar como Short. Corte antes de publicar.")
        else:
            print(f"short de {total:.0f}s, dentro do limite de {SHORTS_MAX_S}s do YouTube")
    fala_txt = f"{lufs_fala:.1f}" if lufs_fala is not None else "n/d"
    print(f"audio: fala {fala_txt} LUFS (alvo {LUFS_ALVO[0]} a {LUFS_ALVO[1]}) | arquivo final {lufs:.1f} LUFS, pico {peak:.1f} dBFS")
    lufs = lufs_fala
    if not sem_checagem:
        ruins = [i + 1 for i, m in enumerate(motions) if not m["ok"]]
        if ruins:
            fail(f"movimento picado nos blocos {ruins}. Ver references/identidade-e-movimento.md")
        if lufs is None or not (LUFS_ALVO[0] <= lufs <= LUFS_ALVO[1]):
            fail(f"loudness fora do alvo: {lufs} LUFS (alvo {LUFS_ALVO})")
        if peak is not None and peak > PICO_MAX:
            fail(f"pico estourando: {peak} dBFS (max {PICO_MAX})")
        print("checagens: movimento fluido em todos os blocos e audio dentro do alvo")
    if exportar:
        slug = re.sub(r"[^a-z0-9]+", "-", strip_tags(cfg.get("titulo", "video")).lower()).strip("-")[:60] or "video"
        destino = os.path.join(BRAND_DIR, "exports", "cartelas", slug)
        os.makedirs(destino, exist_ok=True)
        for i in range(1, len(parts) + 1):
            shutil.copy2(os.path.join(out_dir, f"cartela-{i}.png"), destino)
        capa = os.path.join(out_dir, "capa-1280x720.png")
        if os.path.exists(capa):
            shutil.copy2(capa, destino)
        else:
            print("  aviso: capa nao encontrada; rode build.py capa roteiro.json antes de exportar")
        shutil.copy2(video, os.path.join(destino, os.path.basename(video)))
        print(f"exportado para {destino} (cartelas PNG + video, prontos para o CapCut)")
    print("proximo passo: gate visual nas cartelas (agent documents:visual-judge) antes de publicar")


def main():
    ap = argparse.ArgumentParser(description="Monta video a partir de um roteiro JSON.")
    ap.add_argument("acao", choices=["plan", "aprovar", "custo", "capa", "render"])
    ap.add_argument("roteiro")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--sem-checagem", action="store_true")
    ap.add_argument("--bloco", type=int, default=1, help="bloco do roteiro que vira capa (default 1)")
    ap.add_argument("--largura", type=int, default=1280, help="largura da capa (default 1280, tamanho do YouTube)")
    ap.add_argument("--altura", type=int, default=720, help="altura da capa (default 720)")
    ap.add_argument("--exportar", action="store_true",
                    help="copia cartelas e video para o diretorio padrao da identidade (exports/cartelas/<slug>)")
    args = ap.parse_args()

    with open(args.roteiro, encoding="utf-8") as fh:
        cfg = json.load(fh)
    avisar_sotaque(cfg)
    base_dir = os.path.dirname(os.path.abspath(args.roteiro))
    # out_dir sempre absoluto: o concat demuxer do ffmpeg resolve os caminhos do
    # `trechos.txt` a partir do diretorio do proprio arquivo de lista, entao um
    # --out-dir relativo dobra o prefixo (`out/x/out/x/trecho-1.mp4`) e o render morre
    # no ultimo passo, depois de gerar tudo. Aconteceu em 26/09/2026 no video do
    # carrossel do ADR.
    out_dir = os.path.abspath(args.out_dir or os.path.join(base_dir, "out"))
    if args.acao == "plan":
        cmd_plan(cfg, out_dir, os.path.abspath(args.roteiro))
        cmd_custo(cfg, out_dir)
    elif args.acao == "custo":
        cmd_custo(cfg, out_dir)
    elif args.acao == "capa":
        cmd_capa(cfg, out_dir, args.bloco, args.largura, args.altura)
    elif args.acao == "aprovar":
        cmd_aprovar(cfg, args.roteiro)
    else:
        cmd_render(cfg, out_dir, args.sem_checagem, args.exportar, base_dir)


if __name__ == "__main__":
    main()

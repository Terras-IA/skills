#!/usr/bin/env python3
"""Le uma identidade visual de um conjunto de imagens (ou de um documento-fonte).

A entrada tipica e o material que chega pelo WhatsApp: pecas de anuncio, prints de
perfil, fotos de papelaria, paginas de um manual. Uma peca so mente (o JPEG tinge,
o fundo da foto nao e o fundo da marca), entao o script le **varias** e so elege
como cor da marca o que aparece em mais de uma.

    python3 extrair.py pecas/*.jpeg --nome "Cliente Exemplo" --destino ./identidade
    python3 extrair.py pecas/ --nome "Cliente Exemplo" --fonte manual.pdf --fonte site.css

Saida: `<destino>/identidade.json` com status de rascunho, um relatorio no terminal
e, com `--swatch`, uma folha de amostras em PNG para conferir cor na tela.

O que este script mede e o que ele nao mede:

- **Mede** cor de preenchimento chapado (com escore de "chapado", que separa a cor
  da marca do meio-tom da foto), cor de texto nas duas pontas (clara e escura),
  presenca de cada cor ao longo das pecas e contraste WCAG de cada uma.
- **Nao mede** tipografia em pixel: raster nao tem nome de fonte. Se houver um
  documento-fonte (PDF, PPTX, DOCX, CSS) o nome real sai de la; so com imagens, a
  fonte e identificada a olho com `references/tipografia.md`. O script nunca
  chuta um nome de fonte nem grava um no JSON.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import Counter
from datetime import date

from PIL import Image, ImageFilter

EXT_IMAGEM = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")

# Distancia RGB para juntar dois clusters na mesma cor. O JPEG e a quantizacao
# quebram a mesma cor chapada em varios vizinhos (o amarelo de um cliente multicolor saiu
# #f1d323, #ead027 e #e4d533); sem a juncao, a paleta vira uma lista de variacoes
# e a cor de verdade perde peso.
DIST_CLUSTER = 48
# Acento de verdade e cor saturada de verdade: com 120 o ciano real entra e a
# media de um acento com o fundo (saturacao 60-120) fica de fora, listada como
# pendencia em vez de virar papel. Limite menor ja colocou #347596 (ciano
# misturado com navy) num guia de marca como se fosse o acento.
SAT_ACENTO = 120
SAT_MISTO = 60
# Nitidez: fracao dos pixels do cluster que tem vizinhanca uniforme. Cor chapada
# (fundo, barra, botao) fica perto de 1; meio-tom de foto e sombra ficam baixos.
FLAT_MIN = 0.35


def pixels(im: Image.Image) -> list:
    """getdata sem o aviso de depreciacao do Pillow 12."""
    if hasattr(im, "get_flattened_data"):
        return list(im.get_flattened_data())
    return list(im.getdata())


def mascara_proxima(im: Image.Image, cor, tolerancia: int = 12) -> Image.Image:
    """Mascara dos pixels a menos de `tolerancia` de `cor`, em L.

    Feito com ImageChops (tudo em C): varrer pixel a pixel em Python levava
    minutos por peca e a extracao de um conjunto passava de dez.
    """
    from PIL import ImageChops
    solido = Image.new("RGB", im.size, tuple(int(c) for c in cor[:3]))
    diff = ImageChops.difference(im, solido)
    r, g, b = diff.split()
    maior = ImageChops.lighter(ImageChops.lighter(r, g), b)
    return maior.point(lambda v: 255 if v <= tolerancia else 0, mode="L")


def planura_de(im: Image.Image, cor, tolerancia: int = 12) -> tuple[float, float]:
    """(fracao da area, fracao chapada) de uma cor na imagem.

    Chapado = miolo que sobra depois de erodir a mascara. Cor de preenchimento
    (fundo, barra, botao) fica perto de 1; meio-tom de foto, sombra e borda de
    letra ficam baixos. E o que separa a cor da marca da mistura da foto.
    """
    m = mascara_proxima(im, cor, tolerancia)
    total = m.histogram()[255]
    if not total:
        return 0.0, 0.0
    miolo = m.filter(ImageFilter.MinFilter(3)).histogram()[255]
    return total / (im.width * im.height), miolo / total


def hex_de(cor) -> str:
    return "#%02x%02x%02x" % (int(cor[0]), int(cor[1]), int(cor[2]))


def de_hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def luminancia(cor) -> float:
    return 0.2126 * cor[0] + 0.7152 * cor[1] + 0.0722 * cor[2]


def saturacao(cor) -> int:
    return max(cor[:3]) - min(cor[:3])


def matiz(cor) -> float:
    """Matiz em graus (0-360), para reconhecer a mesma cor em tons diferentes."""
    r, g, b = (v / 255 for v in cor[:3])
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        return 0.0
    if mx == r:
        h = ((g - b) / d) % 6
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60


def dist(a, b) -> float:
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def contraste(a, b) -> float:
    """Razao de contraste WCAG entre duas cores (1 a 21)."""
    def lin(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    la = sum(w * lin(v) for w, v in zip((0.2126, 0.7152, 0.0722), a))
    lb = sum(w * lin(v) for w, v in zip((0.2126, 0.7152, 0.0722), b))
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def contraste_branco(cor) -> float:
    return contraste(cor, (255, 255, 255))


def escurecer_para_ler(cor, minimo: float = 4.5) -> str:
    """Versao da cor que le sobre papel branco, mantendo a matiz.

    Acento vivo e otimo em fundo escuro e ilegivel impresso: o ciano #07d4ec tem
    ~2:1 sobre branco. O acento continua sendo o acento, para preenchimento; para
    TEXTO sobre claro, vale esta versao.
    """
    r, g, b = cor[:3]
    fator = 1.0
    while fator > 0.15:
        atual = (int(r * fator), int(g * fator), int(b * fator))
        if contraste_branco(atual) >= minimo:
            return hex_de(atual)
        fator -= 0.05
    return "#111111"


def clarear_para_ler(cor, fundo, minimo: float = 4.5) -> str:
    """Versao clara da cor, para ler sobre o fundo escuro da marca."""
    r, g, b = cor[:3]
    for passo in range(1, 21):
        p = passo * 0.05
        atual = tuple(int(c + (255 - c) * p) for c in (r, g, b))
        if contraste(atual, fundo) >= minimo:
            return hex_de(atual)
    return "#ffffff"


def analisar_peca(caminho: str, max_lado: int = 720) -> dict:
    """Cores chapadas, as duas pontas de texto e o tamanho de uma peca."""
    im = Image.open(caminho).convert("RGB")
    largura, altura = im.size
    escala = min(1.0, max_lado / max(largura, altura))
    trabalho = im.resize((max(int(largura * escala), 8), max(int(altura * escala), 8)))

    quantizada = trabalho.quantize(colors=16, method=Image.Quantize.MEDIANCUT).convert("RGB")
    # getcolors resolve a contagem em C; Counter(pixels()) levava segundos por peca
    contagem = Counter({cor: n for n, cor in quantizada.getcolors(1 << 24)})
    total = sum(contagem.values())

    # A vizinhanca uniforme e o que separa preenchimento de textura. Erodei a
    # mascara do cluster: o que sobra e miolo chapado, o que some e meio-tom.
    chapado = {}
    cores_peca = []
    for cor, n in contagem.most_common(16):
        frac, planura = planura_de(quantizada, cor)
        chapado[cor] = planura
        cores_peca.append((cor, n / total, planura))

    # Texto fino (2 ou 3 px de traco) desaparece na quantizacao; a media dos
    # pixels extremos recupera a cor do texto sem OCR. Nos extremos basta uma
    # copia pequena: e media de milhares de pixels, nao medida de ponto.
    pequena = trabalho.resize((max(trabalho.width // 2, 8), max(trabalho.height // 2, 8)))
    amostra = pixels(pequena)
    amostra.sort(key=luminancia)
    corte = max(len(amostra) // 200, 1)

    def media(grupo):
        return tuple(sum(c[i] for c in grupo) // len(grupo) for i in range(3))

    return {
        "arquivo": caminho,
        "canvas": (largura, altura),
        "cores": cores_peca,
        "texto_claro": hex_de(media(amostra[-corte:])),
        "texto_escuro": hex_de(media(amostra[:corte])),
    }


def juntar_clusters(todas: list[dict]) -> list[dict]:
    """Junta a mesma cor entre pecas e variacoes, e elege o tom representante.

    O representante e o tom **mais frequente** do grupo, nao a media: a media de
    azul com o antialiasing da borda puxa a cor para longe do azul chapado.
    """
    grupos: list[dict] = []
    for peca in todas:
        nome = os.path.basename(peca["arquivo"])
        for cor, frac, planura in peca["cores"]:
            for g in grupos:
                if dist(g["cor"], cor) <= DIST_CLUSTER:
                    g["membros"][cor] = g["membros"].get(cor, 0) + frac
                    g["peso"] += frac
                    g["planura"] = max(g["planura"], planura)
                    g["pecas"].add(nome)
                    break
            else:
                grupos.append({"cor": cor, "membros": {cor: frac}, "peso": frac,
                               "planura": planura, "pecas": {nome}})
    for g in grupos:
        g["cor"] = max(g["membros"].items(), key=lambda kv: kv[1])[0]
    return sorted(grupos, key=lambda g: -g["peso"] / max(len(todas), 1))


def classificar(grupos: list[dict], n_pecas: int, texto_claro: str, texto_escuro: str) -> dict:
    """Da papel as cores, sem forcar o modelo 'fundo escuro + acento'.

    Duas peneiras antes de qualquer papel:

    - **limpeza**: tom misto (saturacao entre 60 e 120) nunca vira papel. Ele e a
      cor da marca misturada com o fundo ou com a foto, e eleger isso como token
      foi o que ja colocou um ciano sujo num guia de marca.
    - **chapado**: preenchimento de verdade tem vizinhanca uniforme (>= 0.6).
      Abaixo disso e textura, meio-tom ou sombra, e a cor vira pendencia em vez de
      virar papel.

    O que nao passa fica listado com o motivo, para ninguem descobrir depois que
    o `apoio` da identidade era a media de uma foto.
    """
    pendencias: list[str] = []

    def limpa(g):
        return saturacao(g["cor"]) <= SAT_MISTO or saturacao(g["cor"]) > SAT_ACENTO

    fortes = [g for g in grupos if len(g["pecas"]) >= 2 or g["peso"] / n_pecas >= 0.10]
    confiaveis = [g for g in fortes if limpa(g) and g["planura"] >= FLAT_MIN]
    # Um fundo escuro chapado e fundo mesmo com saturacao media: um navy #172956 de
    # marca real mede saturacao 63 e caia fora por "tom misto", que e a regra feita para
    # acento misturado com fundo. Papel de FUNDO se decide por ser escuro e chapado,
    # nao por ser neutro; a peneira de limpeza continua valendo para os acentos.
    chapados = [g for g in fortes if g["planura"] >= FLAT_MIN]
    duvidosos = [g for g in fortes if g not in confiaveis]
    vivos_todos = sorted([g for g in confiaveis if saturacao(g["cor"]) > SAT_ACENTO],
                         key=lambda g: -(g["peso"] * g["planura"]))
    # Duas cores vivas da mesma matiz, uma mais escura, sao a mesma cor em fundos
    # diferentes (o magenta de um cliente multicolor sobre o azul le #a61d68, quase 30% mais
    # escuro que o magenta puro): a mais presente e a cor de marca, a outra e
    # variante. Sem isso, a sombra entra como quinta cor da identidade.
    vivos, variantes = [], []
    for g in vivos_todos:
        igual = next((v for v in vivos if abs(matiz(v["cor"]) - matiz(g["cor"])) <= 12), None)
        if igual is None:
            vivos.append(g)
        else:
            variantes.append({"hex": hex_de(g["cor"]), "de": hex_de(igual["cor"]),
                              "quanto_mais_escuro": round(luminancia(igual["cor"]) -
                                                           luminancia(g["cor"]), 1),
                              "presenca": f"{len(g['pecas'])}/{n_pecas} pecas",
                              "nota": "mesma matiz de uma cor já eleita: é a cor em fundo diferente ou "
                                      "com sobreposição, não uma cor nova"})
    mistos = [g for g in fortes if SAT_MISTO < saturacao(g["cor"]) <= SAT_ACENTO]
    neutros = [g for g in confiaveis if saturacao(g["cor"]) <= SAT_MISTO]
    escuros = [g for g in chapados if luminancia(g["cor"]) < 45]
    claros = sorted([g for g in neutros if luminancia(g["cor"]) >= 200], key=lambda g: -g["peso"])
    cinzas = sorted([g for g in neutros if 60 <= luminancia(g["cor"]) < 200],
                    key=lambda g: -(g["peso"] * g["planura"]))

    base = None
    provisorio = False
    if escuros:
        base = max(escuros, key=lambda g: g["peso"] * (0.5 + g["planura"]))
    elif vivos:
        base = vivos[0]
        provisorio = True
        pendencias.append(
            f"não há fundo escuro limpo e chapado nas peças: a marca usa fundo colorido, e o mais "
            f"presente é {hex_de(base['cor'])}. O papel de 'base' é provisório — confirmar qual cor "
            "é a principal antes de gerar tokens")
    else:
        # Nao eleger uma base fraca e de proposito, mas dizer QUAL e a candidata e o que
        # fazer com ela: "paleta ambigua" sozinho nao da o proximo passo a quem le.
        candidatas = [g for g in grupos
                      if luminancia(g["cor"]) < 120 and g["planura"] >= 0.5
                      and g["peso"] / n_pecas >= 0.02]
        if candidatas:
            candidata = min(candidatas, key=lambda g: luminancia(g["cor"]))
            pendencias.append(
                f"nao achei fundo escuro nem cor viva com presenca suficiente para eleger a base. O tom mais "
                f"escuro chapado e {hex_de(candidata['cor'])} (chapado={candidata['planura']:.2f}, em "
                f"{len(candidata['pecas'])}/{n_pecas} pecas, {candidata['peso']/n_pecas:.2f} de area media): "
                "se ele for o fundo oficial, medir com `medir.py ponto` na peca original e preencher a mao")
        else:
            pendencias.append("nao achei nem fundo escuro nem cor viva confiavel; paleta ambigua, "
                              "medir a mao na peca original")

    papel = {"base": hex_de(base["cor"]) if base else None,
             "papel": hex_de(claros[0]["cor"]) if claros else "#ffffff",
             "texto": texto_claro if luminancia(de_hex(texto_claro)) >= 170 else None,
             "tinta": texto_escuro if luminancia(de_hex(texto_escuro)) < 90 else None,
             "apoio": hex_de(cinzas[0]["cor"]) if cinzas else None}
    # Quando a cor de fundo e tambem a cor de marca mais presente (marca de fundo
    # colorido), 'acento' fica com a proxima: o acento e a cor de destaque SOBRE a
    # base, e repetir a propria base ali deixaria o papel sem funcao.
    destaque = [g for g in vivos if not base or g["cor"] != base["cor"]] if base else vivos
    if base and not destaque and vivos:
        destaque = vivos
    for i, chave in enumerate(("acento", "acento_2", "acento_3", "acento_4")):
        papel[chave] = hex_de(destaque[i]["cor"]) if len(destaque) > i else None
    if base and vivos and base["cor"] == vivos[0]["cor"]:
        papel["nota"] = (f"{hex_de(base['cor'])} é ao mesmo tempo o fundo mais usado e a cor de marca mais "
                         "presente; `acento` traz a segunda, que é a cor de destaque sobre esse fundo. "
                         "A ordem completa está em cores_marca")

    if not vivos:
        pendencias.append("nenhum acento saturado encontrado; se a peça tem acento em área pequena, "
                          "medir a cor do elemento com `medir.py ponto`")
    if not papel["texto"]:
        pendencias.append(f"texto claro não recuperado das peças (melhor estimativa {texto_claro}); confirmar")
    if not papel["tinta"]:
        pendencias.append(f"tinta escura não recuperada das peças (melhor estimativa {texto_escuro}); confirmar")
    duvidosos.sort(key=lambda g: -g["peso"])
    for g in duvidosos[:3]:
        motivo = ("tom misto (cor da marca com fundo ou foto)" if SAT_MISTO < saturacao(g["cor"]) <= SAT_ACENTO
                  else f"não é preenchimento chapado (chapado={g['planura']:.2f})")
        pendencias.append(f"{hex_de(g['cor'])} ficou fora dos papéis: {motivo}; aparece em "
                          f"{len(g['pecas'])}/{n_pecas} pecas")
    if len(duvidosos) > 3:
        pendencias.append(f"e mais {len(duvidosos) - 3} tons fora dos papéis (mistura de cor com fundo ou "
                          f"textura): {', '.join(hex_de(g['cor']) for g in duvidosos[3:])}")

    # A cor de cada acento sobre papel branco: quase todo acento vivo falha, e a
    # versao escurecida e o que faz site, documento e peca impressa continuarem
    # legiveis depois de aplicar a identidade.
    marca = []
    for g in vivos:
        cor = g["cor"]
        item = {"hex": hex_de(cor),
                "nome_provisorio": nome_de_cor(cor),
                "presenca": f"{len(g['pecas'])}/{n_pecas} pecas",
                "peso_medio": round(g["peso"] / n_pecas, 3),
                "chapado": round(g["planura"], 2),
                "contraste_sobre_branco": round(contraste_branco(cor), 2),
                "contraste_sobre_base": round(contraste(cor, base["cor"]), 2) if base else None}
        if item["contraste_sobre_branco"] < 4.5:
            item["hex_sobre_papel"] = escurecer_para_ler(cor)
        if len(g["pecas"]) <= n_pecas / 3:
            item["nota"] = (f"aparece em poucas peças ({len(g['pecas'])}/{n_pecas}) mas chapado: pode ser "
                            "cor de campanha e não cor institucional")
        marca.append(item)
    if len(vivos) > 2:
        pendencias.append(f"a marca tem {len(vivos)} cores vivas confiáveis: identidade multicolor, "
                          "confirmar com quem pediu qual é a principal e em que ordem aparecem "
                          "(a ordem aqui é por presença nas peças)")

    return {"papeis": papel, "cores_marca": marca, "variantes": variantes,
            "mistos_descartados": [hex_de(g["cor"]) for g in mistos][:5],
            "pendencias": pendencias}


NOMES_COR = [
    ((0, 40, 120), "Azul-escuro"), ((0, 90, 200), "Azul"), ((0, 150, 220), "Azul-claro"),
    ((0, 200, 200), "Ciano"), ((0, 150, 90), "Verde"), ((80, 200, 40), "Verde-limao"),
    ((200, 200, 0), "Amarelo"), ((240, 150, 0), "Laranja"), ((220, 60, 30), "Vermelho"),
    ((230, 20, 120), "Magenta"), ((150, 40, 200), "Roxo"), ((240, 90, 170), "Rosa"),
]


def nome_de_cor(cor) -> str:
    """Nome de trabalho para o tom, so para o relatorio ser legivel.

    Nao e o nome da marca (esse e o humano que decide: "Azul Congregacional",
    "Ouro Solene"); e o que permite falar da cor numa frase sem colar hex.
    """
    return min(NOMES_COR, key=lambda n: dist(cor, n[0]))[1]


# --------------------------------------------------------------------------
# Fonte de verdade da tipografia, quando existe documento
# --------------------------------------------------------------------------

def fontes_de_pdf(caminho: str) -> list[str]:
    import pymupdf
    nomes = []
    doc = pymupdf.open(caminho)
    for pagina in doc:
        for f in pagina.get_fonts():
            nome = (f[3] or "").split("+")[-1]
            if nome and nome not in nomes:
                nomes.append(nome)
    doc.close()
    return nomes


def fontes_de_zip_xml(caminho: str, membros: list[str]) -> list[str]:
    """Le theme1.xml e afins de PPTX/DOCX, que declaram as fontes do tema."""
    import re
    import zipfile
    nomes: list[str] = []
    with zipfile.ZipFile(caminho) as z:
        alvos = [n for n in z.namelist() if any(m in n for m in membros)]
        for alvo in alvos:
            try:
                xml = z.read(alvo).decode("utf-8", "replace")
            except Exception:
                continue
            for chave in ("majorFont", "minorFont", "latin", "ea", "cs", "typeface"):
                if chave in xml:
                    for m in re.finditer(r'typeface="([^"]+)"', xml):
                        if m.group(1) and m.group(1) not in nomes:
                            nomes.append(m.group(1))
    return nomes


def fontes_de_css(caminho: str) -> list[str]:
    import re
    texto = open(caminho, encoding="utf-8", errors="replace").read()
    nomes = []
    for m in re.finditer(r"font-family\s*:\s*([^;}\n]+)", texto, re.I):
        for parte in m.group(1).split(","):
            nome = parte.strip().strip("'\"")
            if nome and not nome.startswith("var(") and nome not in nomes:
                nomes.append(nome)
    return nomes


def ler_fontes(caminho: str) -> tuple[list[str], str]:
    baixo = caminho.lower()
    try:
        if baixo.endswith(".pdf"):
            nomes = fontes_de_pdf(caminho)
            if not nomes:
                return [], ("o PDF veio rasterizado (cada pagina e uma imagem): nao ha fonte embutida "
                            "para ler, a tipografia tem de ser identificada a olho")
            return nomes, "fontes embutidas no PDF"
        if baixo.endswith((".pptx", ".docx", ".xlsx")):
            nomes = fontes_de_zip_xml(caminho, ["theme", "styles", "slideMaster"])
            return nomes, "fontes declaradas no tema do arquivo"
        if baixo.endswith((".css", ".html", ".htm", ".scss")):
            return fontes_de_css(caminho), "font-family do CSS"
    except Exception as erro:  # fonte de terceiro, nao vale derrubar a extracao
        return [], f"nao consegui ler ({erro})"
    return [], "extensao nao reconhecida como fonte de tipografia"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", nargs="+", help="imagens ou pastas com imagens")
    ap.add_argument("--nome", required=True, help="nome da marca/identidade")
    ap.add_argument("--destino", default=None, help="pasta da identidade (padrao: ./identidade)")
    ap.add_argument("--fonte", action="append", default=[],
                    help="documento-fonte para ler o nome real da fonte (pdf/pptx/docx/css); pode repetir")
    args = ap.parse_args()

    arquivos: list[str] = []
    for e in args.entrada:
        if os.path.isdir(e):
            for raiz, _, nomes in os.walk(e):
                arquivos += [os.path.join(raiz, n) for n in sorted(nomes) if n.lower().endswith(EXT_IMAGEM)]
        elif e.lower().endswith(EXT_IMAGEM):
            arquivos.append(e)
        else:
            arquivos += sorted(glob.glob(e))
    if not arquivos:
        sys.exit("nenhuma imagem encontrada")

    destino = os.path.abspath(os.path.expanduser(args.destino or "identidade"))
    os.makedirs(destino, exist_ok=True)

    print(f"{len(arquivos)} pecas")
    pecas = []
    for a in arquivos:
        try:
            pecas.append(analisar_peca(a))
        except Exception as erro:
            print(f"  ! pulei {os.path.basename(a)}: {erro}")
    if not pecas:
        sys.exit("nenhuma peca pode ser lida")

    grupos = juntar_clusters(pecas)

    def mais_extremo(chave, reverso):
        valores = sorted((de_hex(p[chave]) for p in pecas), key=luminancia, reverse=reverso)
        n = max(len(valores) // 3, 1)
        escolhidos = valores[:n] if reverso else valores[-n:]
        return hex_de(tuple(sum(c[i] for c in escolhidos) // len(escolhidos) for i in range(3)))

    texto_claro = mais_extremo("texto_claro", True)
    texto_escuro = mais_extremo("texto_escuro", False)
    classe = classificar(grupos, len(pecas), texto_claro, texto_escuro)

    print("\ncores chapadas eleitas (hex, presenca, peso, chapado, papel):")
    papeis_invertidos = {v: k for k, v in classe["papeis"].items() if v}
    for g in grupos[:12]:
        h = hex_de(g["cor"])
        print(f"  {h}  sat={saturacao(g['cor']):3d}  {len(g['pecas'])}/{len(pecas)} pecas  "
              f"peso={g['peso']/len(pecas):.2f}  chapado={g['planura']:.2f}  {papeis_invertidos.get(h, '')}")
    print(f"\ntexto claro medido: {texto_claro} | tinta escura medida: {texto_escuro}")
    for v in classe["variantes"]:
        print(f"variante de {v['de']}: {v['hex']} ({v['presenca']}, {v['nota']})")
    if classe["mistos_descartados"]:
        print(f"tons mistos descartados dos papeis (media de acento com fundo): {classe['mistos_descartados']}")

    fontes, nota_fontes = [], ""
    origens_fonte = []
    for f in args.fonte:
        nomes, como = ler_fontes(os.path.expanduser(f))
        origens_fonte.append({"arquivo": f, "como": como, "fontes": nomes})
        print(f"fontes em {os.path.basename(f)}: {nomes or 'nenhuma'} ({como})")
        fontes += [n for n in nomes if n not in fontes]
    if fontes:
        nota_fontes = ("nomes lidos do documento-fonte; conferir licença e baixar o arquivo antes de usar")
    elif args.fonte:
        nota_fontes = "o documento-fonte não declara fonte: identificar a olho (references/tipografia.md)"
    else:
        nota_fontes = ("nenhum documento-fonte passado: tipografia não sai de pixel. Identificar a olho com "
                       "references/tipografia.md e só então preencher este bloco")

    pendencias = list(classe["pendencias"])
    if not fontes:
        pendencias.append("tipografia não preenchida: identificar a família a olho e escolher o equivalente livre")
    pendencias.append("cor de linha/filete e raio de canto não saem de peça comprimida: medir com "
                      "`medir.py area` na peça original se a identidade for usada em interface")

    dados = {
        "nome": args.nome,
        "status": "rascunho",
        "_aviso": ("RASCUNHO gerado por extração automática. Não usar como guia de marca nem citar "
                   "valor daqui antes de conferir com `medir.py` e com o olho em cima da peça original. "
                   "Foi um rascunho desses, lido como fonte, que colocou um ciano misturado num guia."),
        "descricao": f"identidade lida de {len(pecas)} peças por extração automática, {date.today().isoformat()}",
        "origem": [os.path.basename(p["arquivo"]) for p in pecas],
        "extraido_em": date.today().isoformat(),
        "cores": classe["papeis"],
        "cores_marca": classe["cores_marca"],
        "variantes_de_cor": classe["variantes"],
        "tons_descartados": classe["mistos_descartados"],
        "fontes": {"nome_medido": fontes, "nota": nota_fontes,
                   "origens": origens_fonte or None} if fontes else
                  {"nome_medido": [], "nota": nota_fontes,
                   "origens": origens_fonte or None},
        "marca": {"estilo": None,
                  "estilos_disponiveis": ["lockup", "monograma-nome", "nome", "sem-marca"],
                  "nota": "preencher após recortar o logo com `medir.py marca`: lockup (imagem do conjunto), "
                          "monograma-nome (símbolo + nome em texto), nome (só texto) ou sem-marca (nada, nem "
                          "assinatura de rodapé)"},
        "ativos": {"nota": "PNGs recortados do material entram aqui por papel (logo_claro, logo_escuro, "
                           "monograma_claro, fundo, padrao)"},
        "linguagem": {"nota": "formas, tratamento de foto, grade e gestos da marca: preencher a partir das peças "
                              "(ver references/linguagem.md)"},
        "pendencias": pendencias,
    }

    caminho_json = os.path.join(destino, "identidade.json")
    if os.path.exists(caminho_json):
        caminho_json = os.path.join(destino, "identidade.json.novo")
        print(f"\n! ja existia identidade.json em {destino}; o novo saiu ao lado como .novo para comparar")
    with open(caminho_json, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)

    print("\npapeis:", json.dumps(classe["papeis"], ensure_ascii=False))
    if pendencias:
        print("\npendencias:")
        for p in pendencias:
            print("  -", p)
    print(f"\nrascunho da identidade em {caminho_json}")
    print("conferir as cores com `medir.py ponto` nas pecas e revisar antes de aplicar em qualquer material")
    print(f"prova visual: `prova.py {caminho_json}`")


if __name__ == "__main__":
    main()

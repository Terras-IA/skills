#!/usr/bin/env python3
"""Mede cor na peca original e recorta ativos (logo, simbolo, padrao) com alfa.

O `extrair.py` diz a paleta provavel; este script e o que confirma e o que
transforma pixel em ativo. Toda medida aqui e **mediana de uma vizinhanca**, nao
o pixel cru: JPEG de WhatsApp tinge o pixel isolado (um branco puro pode ler
#f7f6f4 num ponto e #ffffff no vizinho).

    # a cor daquele botao, na peca original
    python3 medir.py ponto peca.jpg 430 1180 --raio 4

    # a regiao e chapada? (desvio baixo = sim, a cor vale)
    python3 medir.py area peca.jpg 60 1200 300 80

    # recorte ampliado com grade e regua, para achar a caixa do logo a olho
    python3 medir.py zoom peca.jpg 60 1500 700 240 --escala 3

    # o logo, com transparencia, a partir da caixa lida no zoom
    python3 medir.py recortar peca.jpg --caixa 100,1540,420,180 --mascara branco --chapar "#ffffff"

    # as duas versoes da marca de uma vez (fundo escuro e fundo claro)
    python3 medir.py marca peca.jpg --caixa 112,1185,330,84 --cor "#f1d323" \
        --cortar-faixa 60,84 --pasta identidade/ativos --nome avancei

O `recortar` existe porque logo de peca rasterizada quase nunca vem em arquivo: o
que da e recortar do material. A mascara e por canal minimo (branco tem os tres
canais altos; cor saturada tem minimo perto de zero), e depois **fecha** cortes de
poucos pixels e suaviza a borda. Mapear o canal minimo direto em alfa foi o erro
que ja custou duas reprovacoes no gate: a sombra suave do contorno vira
semitransparencia e aparece como risco escuro atravessando a marca.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, deque

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTE_ROTULO = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def pixels(im: Image.Image) -> list:
    if hasattr(im, "get_flattened_data"):
        return list(im.get_flattened_data())
    return list(im.getdata())


def hex_de(cor) -> str:
    return "#%02x%02x%02x" % (int(cor[0]), int(cor[1]), int(cor[2]))


def de_hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mediana(vals: list) -> tuple[int, int, int]:
    return tuple(sorted(v[i] for v in vals)[len(vals) // 2] for i in range(3))


def recorte(im, caixa, pad=0):
    x, y, l, a = caixa
    x, y = max(0, x - pad), max(0, y - pad)
    return im.crop((x, y, min(im.width, x + l + 2 * pad), min(im.height, y + a + 2 * pad)))


def cmd_ponto(args) -> None:
    im = Image.open(args.imagem).convert("RGB")
    vals = []
    for dy in range(-args.raio, args.raio + 1):
        for dx in range(-args.raio, args.raio + 1):
            x, y = args.x + dx, args.y + dy
            if 0 <= x < im.width and 0 <= y < im.height:
                vals.append(im.getpixel((x, y)))
    if not vals:
        sys.exit("ponto fora da imagem")
    m = mediana(vals)
    variacao = max(max(v[i] for v in vals) - min(v[i] for v in vals) for i in range(3))
    print(f"{args.imagem} ({args.x},{args.y}) raio {args.raio}: {hex_de(m)}  rgb{m}")
    print(f"  variacao na vizinhanca: {variacao} " +
          ("(chapado, a medida vale)" if variacao <= 8 else
           "(região com textura ou borda: aproxime de um miolo chapado ou refaça o recorte)"))


def cmd_area(args) -> None:
    im = Image.open(args.imagem).convert("RGB")
    regiao = recorte(im, (args.x, args.y, args.largura, args.altura))
    dados = pixels(regiao)
    contagem = Counter(dados)
    dominante, n = contagem.most_common(1)[0]
    fracao = n / len(dados)
    # desvio medio em relacao a cor dominante: baixo quer dizer area chapada
    desvio = sum(sum(abs(p[i] - dominante[i]) for i in range(3)) for p in dados[:20000]) / (3 * min(len(dados), 20000))
    print(f"{args.imagem} area ({args.x},{args.y}) {args.largura}x{args.altura}")
    print(f"  dominante: {hex_de(dominante)}  ({fracao*100:.1f}% da area)  desvio medio {desvio:.1f}")
    for cor, c in contagem.most_common(5):
        print(f"    {hex_de(cor)}  {100*c/len(dados):5.1f}%")
    if fracao > 0.8 and desvio < 6:
        print("  área chapada: a cor dominante é a cor da marca aqui")
    else:
        print("  área NÃO chapada (foto, meio-tom ou gradiente): a dominante é mistura, não use como token")


def cmd_zoom(args) -> None:
    im = Image.open(args.imagem).convert("RGB")
    caixa = (args.x, args.y, args.largura, args.altura)
    regiao = recorte(im, caixa).resize(
        (args.largura * args.escala, args.altura * args.escala), Image.NEAREST)
    grade = regiao.copy()
    d = ImageDraw.Draw(grade)
    passo = args.passo * args.escala
    for i, x in enumerate(range(0, grade.width, passo)):
        d.line([(x, 0), (x, grade.height)], fill=(255, 0, 255), width=1)
        d.text((x + 2, 2), str(args.x + i * args.passo), fill=(255, 0, 255), font=_fonte(11))
    for j, y in enumerate(range(0, grade.height, passo)):
        d.line([(0, y), (grade.width, y)], fill=(0, 255, 255), width=1)
        d.text((2, y + 2), str(args.y + j * args.passo), fill=(0, 255, 255), font=_fonte(11))
    saida = args.saida or "zoom.png"
    grade.save(saida)
    print(f"zoom de ({args.x},{args.y}) {args.largura}x{args.altura} em {args.escala}x -> {saida}")
    print("  magenta = colunas (x), ciano = linhas (y), números em pixel da imagem original")
    print("  leia a caixa do elemento e passe para `recortar --caixa x,y,largura,altura`")


def _fonte(tam: int):
    try:
        return ImageFont.truetype(FONTE_ROTULO, tam)
    except Exception:
        return ImageFont.load_default()


def mascara_de(im: Image.Image, modo: str, limiar: int, cor=None, tol: int = 40) -> Image.Image:
    """Mascara binaria da tinta da marca.

    branco: os tres canais altos (branco chapado; cor saturada tem minimo baixo)
    escura: os tres canais baixos (tinta escura sobre fundo claro)
    cor:    perto da cor dada
    fundo:  longe da cor dada (para logo colorido sobre fundo chapado: o que nao e
            fundo e marca, entao o chevron e as letras entram juntos, com as cores)
    """
    m = Image.new("L", im.size, 0)
    saida = []
    for p in pixels(im):
        if modo == "branco":
            v = 255 if min(p) >= limiar else 0
        elif modo == "escura":
            v = 255 if max(p) <= limiar else 0
        elif modo == "cor":
            alvo = cor or (0, 0, 0)
            v = 255 if sum(abs(p[i] - alvo[i]) for i in range(3)) <= tol * 3 else 0
        elif modo == "fundo":
            alvo = cor or (255, 255, 255)
            v = 255 if sum(abs(p[i] - alvo[i]) for i in range(3)) > tol * 3 else 0
        else:
            sys.exit(f"modo de mascara desconhecido: {modo}")
        saida.append(v)
    m.putdata(saida)
    return m


def limpar_componentes(m: Image.Image, area_min: int) -> Image.Image:
    """Joga fora componentes menores que area_min (sujeira, letra solta)."""
    if area_min <= 0:
        return m
    largura, altura = m.size
    px = m.load()
    visto = bytearray(largura * altura)
    saida = Image.new("L", m.size, 0)
    saida_px = saida.load()
    for y in range(altura):
        for x in range(largura):
            if px[x, y] < 128 or visto[y * largura + x]:
                continue
            fila = deque([(x, y)])
            visto[y * largura + x] = 1
            membros = []
            while fila:
                cx, cy = fila.popleft()
                membros.append((cx, cy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < largura and 0 <= ny < altura and not visto[ny * largura + nx] \
                            and px[nx, ny] >= 128:
                        visto[ny * largura + nx] = 1
                        fila.append((nx, ny))
            if len(membros) >= area_min:
                for cx, cy in membros:
                    saida_px[cx, cy] = 255
    return saida


def cmd_recortar(args) -> None:
    im = Image.open(args.imagem).convert("RGB")
    caixa = [int(v) for v in args.caixa.split(",")]
    if len(caixa) != 4:
        sys.exit("--caixa precisa ser x,y,largura,altura")
    pedaco = recorte(im, caixa)
    cor = de_hex(args.cor) if args.cor else None
    m = mascara_de(pedaco, args.mascara, args.limiar, cor, args.tolerancia)
    if args.fechar:
        # fechar = dilatar e voltar: atravessa corte fino (antialiasing,
        # compressao) sem engordar o desenho
        m = m.filter(ImageFilter.MaxFilter(args.fechar * 2 + 1)).filter(
            ImageFilter.MinFilter(args.fechar * 2 + 1))
    m = limpar_componentes(m, args.area_min)
    m = m.filter(ImageFilter.GaussianBlur(args.suavizar))
    if args.inverter:
        from PIL import ImageOps
        m = ImageOps.invert(m)

    if args.chapar:
        cor_chapa = de_hex(args.chapar)
        frente = Image.new("RGB", pedaco.size, cor_chapa)
    else:
        frente = pedaco
    saida = frente.convert("RGBA")
    saida.putalpha(m)
    destino = args.saida or os.path.splitext(os.path.basename(args.imagem))[0] + "-ativo.png"
    saida.save(destino)

    cobertura = sum(1 for v in pixels(m) if v > 128) / (m.width * m.height)
    print(f"ativo salvo em {destino}  ({saida.width}x{saida.height}, {cobertura*100:.1f}% de tinta)")
    if cobertura > 0.85:
        print("  ! quase todo o recorte virou tinta: a caixa pegou fundo demais, ou o limiar está alto "
              "para este material")
    if cobertura < 0.01:
        print("  ! quase nada virou tinta: limiar baixo demais, ou a marca não é desta cor nesta peça")
    print("  conferir a olho no fundo claro E no escuro (o ativo vai ser usado nos dois)")


def componentes(m: Image.Image) -> list[dict]:
    """Componentes da mascara, com area e caixa, do maior para o menor."""
    largura, altura = m.size
    px = m.load()
    visto = bytearray(largura * altura)
    achados = []
    for y in range(altura):
        for x in range(largura):
            if px[x, y] < 128 or visto[y * largura + x]:
                continue
            fila = deque([(x, y)])
            visto[y * largura + x] = 1
            minx = maxx = x
            miny = maxy = y
            n = 0
            while fila:
                cx, cy = fila.popleft()
                n += 1
                minx, maxx = min(minx, cx), max(maxx, cx)
                miny, maxy = min(miny, cy), max(maxy, cy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < largura and 0 <= ny < altura and not visto[ny * largura + nx] \
                            and px[nx, ny] >= 128:
                        visto[ny * largura + nx] = 1
                        fila.append((nx, ny))
            achados.append({"area": n, "caixa": (minx, miny, maxx - minx + 1, maxy - miny + 1)})
    return sorted(achados, key=lambda c: -c["area"])


def cmd_marca(args) -> None:
    """Recorta a marca de uma peca e sai com as versoes clara e escura.

    E a operacao que mais rende nesta skill: logo de marca quase nunca chega em
    arquivo, e sim dentro de uma peca comprimida. De uma mascara so saem as duas
    versoes que qualquer material pede (branca para fundo escuro, escura para
    fundo claro), em vez de recortar duas vezes e sair com dois desenhos
    levemente diferentes.
    """
    im = Image.open(args.imagem).convert("RGB")
    caixa = [int(v) for v in args.caixa.split(",")]
    pedaco = recorte(im, caixa)
    cor = de_hex(args.cor) if args.cor else None
    m = mascara_de(pedaco, args.mascara, args.limiar, cor, args.tolerancia)
    if args.cortar_faixa:
        # zera a banda indicada (a tagline fina, por exemplo), preservando o resto
        y0, y1 = (int(v) for v in args.cortar_faixa.split(","))
        y0, y1 = max(0, min(y0, m.height)), max(0, min(y1, m.height))
        if y1 > y0:
            recortada = m.copy()
            recortada.paste(Image.new("L", (m.width, y1 - y0), 0), (0, y0))
            m = recortada
    if args.fechar:
        m = m.filter(ImageFilter.MaxFilter(args.fechar * 2 + 1)).filter(
            ImageFilter.MinFilter(args.fechar * 2 + 1))
    m = limpar_componentes(m, args.area_min)
    m = m.filter(ImageFilter.GaussianBlur(args.suavizar))

    partes = componentes(m.filter(ImageFilter.MinFilter(3)))
    pasta = os.path.abspath(os.path.expanduser(args.pasta))
    os.makedirs(pasta, exist_ok=True)
    escritos = []
    for papel, cor_chapa in (("claro", args.cor_clara), ("escuro", args.cor_escura), ("cor", None)):
        if cor_chapa is None and papel != "cor":
            continue
        if papel == "cor" and not args.salvar_cor:
            continue
        frente = pedaco if cor_chapa is None else Image.new("RGB", pedaco.size, de_hex(cor_chapa))
        saida = frente.convert("RGBA")
        saida.putalpha(m)
        caminho = os.path.join(pasta, f"{args.nome}-{papel}.png")
        saida.save(caminho)
        escritos.append(os.path.relpath(caminho, pasta))

    total = sum(c["area"] for c in partes) or 1
    print(f"marca recortada de {args.imagem} ({pedaco.width}x{pedaco.height})")
    print(f"componentes: {len(partes)} | maior {partes[0]['area'] if partes else 0} px | "
          f"pequenos (<{max(total // 200, 30)} px): {sum(1 for c in partes if c['area'] < max(total // 200, 30))}")
    print(f"escritos em {pasta}: {', '.join(escritos)}")
    if len(partes) > 12:
        print("  ! a marca saiu em muitos pedaços: sinal de texto fino quebrado pela compressão da peça. "
              "Se a assinatura/tagline vier picada, recorte sem ela (--cortar-faixa) e escreva a linha "
              "em texto no template, ou peça o arquivo vetorial de origem")
    if partes and partes[0]["caixa"][3] < 12:
        print("  ! a maior parte tem menos de 12 px de altura: a caixa pode ter pegado a marca de longe demais "
              "para virar ativo de material impresso")
    print("  conferir a olho no fundo claro E no escuro antes de declarar o ativo pronto")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ponto", help="cor de um ponto (mediana da vizinhanca)")
    p.add_argument("imagem")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("--raio", type=int, default=3)
    p.set_defaults(func=cmd_ponto)

    p = sub.add_parser("area", help="cor dominante de uma area e se ela e chapada")
    p.add_argument("imagem")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("largura", type=int)
    p.add_argument("altura", type=int)
    p.set_defaults(func=cmd_area)

    p = sub.add_parser("zoom", help="recorte ampliado com grade e regua em pixels")
    p.add_argument("imagem")
    p.add_argument("x", type=int)
    p.add_argument("y", type=int)
    p.add_argument("largura", type=int)
    p.add_argument("altura", type=int)
    p.add_argument("--escala", type=int, default=3)
    p.add_argument("--passo", type=int, default=50, help="espacamento da grade, em pixel da imagem original")
    p.add_argument("--saida", default=None)
    p.set_defaults(func=cmd_zoom)

    p = sub.add_parser("recortar", help="recorta ativo (logo, simbolo, padrao) com alfa")
    p.add_argument("imagem")
    p.add_argument("--caixa", required=True, help="x,y,largura,altura em pixel da imagem original")
    p.add_argument("--mascara", choices=["branco", "escura", "cor", "fundo"], default="branco")
    p.add_argument("--limiar", type=int, default=200, help="corte do canal (branco: minimo; escura: maximo)")
    p.add_argument("--cor", default=None, help="cor alvo (mascara cor) ou cor do fundo (mascara fundo)")
    p.add_argument("--tolerancia", type=int, default=40)
    p.add_argument("--chapar", default=None,
                   help="chapa o ativo numa cor (ex.: #ffffff); sem isso, mantem as cores do original")
    p.add_argument("--fechar", type=int, default=2, help="fecha cortes de ate N px")
    p.add_argument("--suavizar", type=float, default=0.7)
    p.add_argument("--area-min", type=int, default=24, help="descarta componentes menores que N px")
    p.add_argument("--inverter", action="store_true", help="inverte a mascara (fundo transparente)")
    p.add_argument("--saida", default=None)
    p.set_defaults(func=cmd_recortar)

    p = sub.add_parser("marca", help="recorta a marca e sai com as versoes clara e escura do mesmo recorte")
    p.add_argument("imagem")
    p.add_argument("--caixa", required=True, help="x,y,largura,altura em pixel da imagem original")
    p.add_argument("--nome", default="logo", help="nome base dos arquivos (padrao: logo)")
    p.add_argument("--pasta", default=".", help="pasta de saida dos PNGs")
    p.add_argument("--mascara", choices=["branco", "escura", "cor", "fundo"], default="fundo",
                   help="fundo e o padrao aqui: logo colorido sobre fundo chapado (o que nao e fundo e marca)")
    p.add_argument("--cor", default=None, help="cor do fundo quando --mascara fundo")
    p.add_argument("--tolerancia", type=int, default=60)
    p.add_argument("--limiar", type=int, default=200)
    p.add_argument("--cor-clara", default="#ffffff", help="cor da versao para fundo escuro")
    p.add_argument("--cor-escura", default="#212324", help="cor da versao para fundo claro")
    p.add_argument("--salvar-cor", action="store_true", help="guarda tambem a versao nas cores do original")
    p.add_argument("--cortar-faixa", default=None,
                   help="y0,y1 (relativo a caixa) para zerar: use para cortar a tagline fina, que quebra "
                        "no recorte de peca comprimida")
    p.add_argument("--fechar", type=int, default=2)
    p.add_argument("--suavizar", type=float, default=0.7)
    p.add_argument("--area-min", type=int, default=24)
    p.set_defaults(func=cmd_marca)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

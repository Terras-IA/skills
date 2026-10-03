#!/usr/bin/env python3
"""Gera as variantes utilizáveis de uma marca a partir de uma arte qualquer.

Serve para quando a marca chega como raster — inclusive JPEG de WhatsApp, com fundo
sólido e compressão. A arte é convertida em **alfa por cobertura** (o quanto cada
pixel se afasta do fundo na direção da tinta), o que deixa o traço recolorível sem
franja de compressão.

    python3 marca.py --origem logo.jpg --saida docs/marca \\
        --tinta "#94b4a4" --fundo "#212c32" --claro "#99442d"

Saída: versão canônica (achatada no fundo), transparente na cor da marca, variante
para fundo claro, variante em carvão, favicons, avatar 1024 e um README com a regra
de contraste já medida.

Regra que este script existe para não deixar esquecer: **a cor da marca raramente
funciona nos dois fundos.** Meça com `contraste.py` e escreva a regra junto dos assets.
"""
import argparse
import os
from PIL import Image

TINTA_PADRAO = (148, 180, 164)
FUNDO_PADRAO = (33, 43, 51)


def hex_para_rgb(valor):
    valor = valor.strip().lstrip("#")
    return tuple(int(valor[i:i + 2], 16) for i in (0, 2, 4))


def luminancia_simples(c):
    """Média ponderada na escala 0–255. É a medida usada pela máscara de cobertura —
    ali só importa a distância entre fundo e tinta, e qualquer medida monótona serve.
    **Não** use isto para contraste: sem linearizar o sRGB o número sai errado."""
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def luminancia(c):
    """Luminância relativa da WCAG — **lineariza o sRGB** antes de ponderar.

    Sem linearizar (média ponderada simples), sálvia sobre areia dá 1,45:1; com a
    fórmula correta, 2,14:1. Não troque isto por atalho: o número errado faz uma cor
    ruim parecer pior do que é, ou uma aceitável parecer boa.
    """
    canais = []
    for v in c:
        v = v / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def razao(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mascara_por_cobertura(im, fundo, tinta):
    """Alfa = o quanto o pixel se afasta do fundo na direção da tinta."""
    px = im.load()
    largura, altura = im.size
    fundo_lum = luminancia_simples(fundo)
    faixa = max(luminancia_simples(tinta) - fundo_lum, 1.0)
    mascara = Image.new("L", im.size)
    mp = mascara.load()
    for y in range(altura):
        for x in range(largura):
            lum = luminancia_simples(px[x, y])
            mp[x, y] = max(0, min(255, int(round((lum - fundo_lum) / faixa * 255))))
    return mascara


def pintar(mascara, cor, tamanho=None, sobre=None):
    im = Image.new("RGBA", mascara.size, cor + (255,))
    im.putalpha(mascara)
    if tamanho:
        im = im.resize(tamanho, Image.LANCZOS)
    if sobre is not None:
        base = Image.new("RGBA", im.size, sobre + (255,))
        base.alpha_composite(im)
        return base
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origem", required=True, help="arte recebida (jpg/png)")
    ap.add_argument("--saida", required=True, help="diretório de saída")
    ap.add_argument("--tinta", default=None, help="cor do traço, ex. #94b4a4 (padrão: amostra do arquivo)")
    ap.add_argument("--fundo", default="#212c32", help="cor do fundo da arte (default #212c32)")
    ap.add_argument("--claro", default=None, help="cor para uso em fundo claro, ex. #99442d")
    ap.add_argument("--escuro", default="#212c32", help="cor para uso em papel branco/impressão")
    ap.add_argument("--respiro", type=float, default=1.24, help="folga em volta (1.24 = 12%%)")
    args = ap.parse_args()

    fundo = hex_para_rgb(args.fundo)
    original = Image.open(args.origem).convert("RGB")

    if args.tinta:
        tinta = hex_para_rgb(args.tinta)
    else:
        # amostra: o pixel mais distante do fundo é a tinta
        px = list(original.getdata())
        tinta = max(px, key=lambda c: abs(luminancia(c) - luminancia(fundo)))

    print(f"origem: {original.size[0]}x{original.size[1]}")
    print(f"fundo considerado: #{fundo[0]:02x}{fundo[1]:02x}{fundo[2]:02x}")
    print(f"tinta:             #{tinta[0]:02x}{tinta[1]:02x}{tinta[2]:02x}")

    mascara = mascara_por_cobertura(original, fundo, tinta)
    caixa = mascara.point(lambda v: 255 if v > 40 else 0).getbbox()
    if not caixa:
        raise SystemExit("não encontrei a arte — confira --fundo e --tinta")
    print(f"conteúdo recortado: {caixa}")

    arte = mascara.crop(caixa)
    lado = int(max(arte.size) * args.respiro)
    quadrada = Image.new("L", (lado, lado), 0)
    quadrada.paste(arte, ((lado - arte.size[0]) // 2, (lado - arte.size[1]) // 2))
    print(f"quadrada: {lado}x{lado}")

    os.makedirs(args.saida, exist_ok=True)

    def salvar(nome, imagem):
        caminho = os.path.join(args.saida, nome)
        imagem.save(caminho)
        return caminho

    salvar("logo-sobre-fundo.png", pintar(quadrada, tinta, sobre=fundo).convert("RGB"))
    salvar("logo-transparente.png", pintar(quadrada, tinta))
    salvar("logo-carvao-transparente.png", pintar(quadrada, hex_para_rgb(args.escuro)))
    if args.claro:
        salvar("logo-claro-transparente.png", pintar(quadrada, hex_para_rgb(args.claro)))
    for tam in (512, 192, 180, 32):
        salvar(f"favicon-{tam}-sobre-fundo.png",
               pintar(quadrada, tinta, (tam, tam), sobre=fundo).convert("RGB"))
    salvar("avatar-1024.png", pintar(quadrada, tinta, (1024, 1024), sobre=fundo).convert("RGB"))

    # maskable: o Android recorta até 20% de cada lado -> símbolo a ~70%
    alvo = int(512 * 0.70)
    base = Image.new("RGB", (512, 512), fundo)
    marca = pintar(quadrada, tinta, (alvo, alvo))
    base.paste(marca, ((512 - alvo) // 2, (512 - alvo) // 2), marca)
    salvar("icone-maskable-512.png", base)

    print()
    print("contraste de cada variante da marca sobre cada fundo:")
    fundos = [("carvão canônico", fundo), ("papel claro", (252, 249, 243)),
              ("branco", (255, 255, 255))]
    tintas = [("tinta original", tinta), ("carvão", hex_para_rgb(args.escuro))]
    if args.claro:
        tintas.append(("variante clara", hex_para_rgb(args.claro)))
    print("  " + " " * 18 + "".join(f"{n:>16}" for n, _ in fundos))
    for nome_t, cor_t in tintas:
        linha = f"  {nome_t:<18}"
        for nome_f, cor_f in fundos:
            r = razao(cor_t, cor_f)
            marca = "" if r >= 3 else "!"
            linha += f"{r:>14.2f}:1{marca}"
        print(linha)
    print("  (! = abaixo de 3:1 — não usar como marca nesse fundo)")

    arquivos = sorted(os.listdir(args.saida))
    print()
    print(f"{len(arquivos)} arquivos em {args.saida}")
    print("Escreva no README da pasta: qual é a versão canônica, e qual usar em fundo claro.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Contraste entre cores e dosagem de cor numa tela.

Três usos:

    # 1. contraste de um par
    python3 contraste.py --texto "#1c1c18" --fundo "#fcf9f3"

    # 2. tabela cruzada de uma paleta (JSON: {"papel": "#hex", ...})
    python3 contraste.py --paleta paleta.json

    # 3. dosagem: quanta cor saturada há numa captura, e de que matiz
    python3 contraste.py --captura tela.png

O terceiro é o que costuma faltar: uma paleta calma pode estar aplicada de um jeito
que não acalma, se o matiz mais estimulante ocupar a maior área. Meça, não estime.

Só depende de Pillow (para a captura). As contas são stdlib.
"""
import argparse
import colorsys
import json
import sys

LIMIAR_TEXTO = 4.5          # WCAG AA para texto normal
LIMIAR_TEXTO_GRANDE = 3.0   # texto >= 24px, ou >= 19px em negrito
LIMIAR_GRAFICO = 3.0        # componente de interface e elemento gráfico

# Faixas de matiz (graus) agrupadas por família, na ordem em que interessam aqui.
FAIXAS = [
    ("vermelho/terracota", 0, 45),
    ("laranja", 45, 70),
    ("amarelo/dourado", 70, 95),
    ("verde", 95, 165),
    ("ciano/azul", 165, 260),
    ("violeta/malva", 260, 320),
    ("magenta/rosa", 320, 360),
]

# Nome legível para a família: orienta a leitura do resultado.
LEITURA = {
    "vermelho/terracota": "quente de barro — vira alerta se ganhar área",
    "laranja": "quente, energético",
    "amarelo/dourado": "recompensa — melhor pontual",
    "verde": "baixa ativação — é aqui que mora o acalmar",
    "ciano/azul": "confiança — cuidado com frieza",
    "violeta/malva": "introspecção",
    "magenta/rosa": "afetivo, chamativo",
}


def hex_para_rgb(valor):
    valor = valor.strip().lstrip("#")
    if len(valor) == 3:
        valor = "".join(c * 2 for c in valor)
    if len(valor) != 6:
        raise ValueError(f"cor inválida: {valor!r} (use #rrggbb)")
    return tuple(int(valor[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(rgb):
    """Luminância relativa conforme WCAG."""
    canais = []
    for v in rgb:
        v = v / 255
        canais.append(v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canais[0] + 0.7152 * canais[1] + 0.0722 * canais[2]


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def veredito(razao, limiar):
    return "ok" if razao >= limiar else "FALHA"


def par(texto, fundo):
    r = contraste(texto, fundo)
    if r >= LIMIAR_TEXTO:
        nota = "serve para texto normal"
    elif r >= LIMIAR_TEXTO_GRANDE:
        nota = "só texto grande (>=24px) ou elemento gráfico"
    elif r >= 2.0:
        nota = "insuficiente para texto; marca/ícone some na prática"
    else:
        nota = "praticamente invisível"
    print(f"  contraste: {r:.2f}:1   ({nota})")
    print(f"  texto normal precisa {LIMIAR_TEXTO}:1 — {veredito(r, LIMIAR_TEXTO)}")
    print(f"  elemento gráfico precisa {LIMIAR_GRAFICO}:1 — {veredito(r, LIMIAR_GRAFICO)}")
    return r


def tabela(paleta):
    nomes = list(paleta)
    print("  " + " " * 18 + "".join(f"{n[:9]:>11}" for n in nomes))
    for a in nomes:
        linha = f"  {a[:16]:<18}"
        for b in nomes:
            if a == b:
                linha += f"{'—':>11}"
            else:
                linha += f"{contraste(paleta[a], paleta[b]):>10.2f} "
        print(linha)
    print()
    ruins = []
    for a in nomes:
        for b in nomes:
            if a < b:
                r = contraste(paleta[a], paleta[b])
                if r < LIMIAR_GRAFICO:
                    ruins.append((a, b, r))
    if ruins:
        print(f"  {len(ruins)} par(es) abaixo de {LIMIAR_GRAFICO}:1 (só serve para decoração):")
        for a, b, r in sorted(ruins, key=lambda x: x[2])[:8]:
            print(f"    {a} × {b}: {r:.2f}:1")
    else:
        print(f"  nenhum par abaixo de {LIMIAR_GRAFICO}:1")


def dosagem(caminho, fator=2):
    from PIL import Image

    im = Image.open(caminho).convert("RGB")
    im = im.resize((max(1, im.width // fator), max(1, im.height // fator)))
    pixels = list(im.getdata())
    total = len(pixels)

    saturados = []
    for r, g, b in pixels:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if s > 0.25 and 0.15 < l < 0.85:
            saturados.append(h * 360)

    print(f"  pixels com cor saturada: {len(saturados) * 100 / total:.1f}% da tela")
    if not saturados:
        print("  tela essencialmente neutra")
        return

    print(f"  distribuição do matiz (sobre a cor, não sobre a tela):")
    contagem = {nome: 0 for nome, _, _ in FAIXAS}
    for h in saturados:
        for nome, lo, hi in FAIXAS:
            if lo <= h < hi:
                contagem[nome] += 1
                break
    for nome, n in sorted(contagem.items(), key=lambda x: -x[1]):
        if not n:
            continue
        pct_cor = n * 100 / len(saturados)
        pct_tela = n * 100 / total
        print(f"    {nome:<18} {pct_cor:5.1f}% da cor   ({pct_tela:4.1f}% da tela)  {LEITURA[nome]}")

    dominante = max(contagem, key=contagem.get)
    pct_tela = len(saturados) * 100 / total
    print()
    if pct_tela > 20:
        print(f"  ATENÇÃO: {pct_tela:.0f}% da tela é cor saturada — acima de ~20% compete com a leitura.")
    if dominante in ("vermelho/terracota", "laranja", "magenta/rosa") and contagem[dominante] > 0.6 * len(saturados):
        print(f"  ATENÇÃO: o matiz dominante é {dominante}, o mais estimulante do conjunto.")
        print("  Se a proposta é acalmar, reduza a ÁREA dele (não precisa trocar a cor):")
        print("  bloco de cor cheia -> cartão neutro + acento; leve a cor de apoio para o fundo dos cartões.")
    if contagem["verde"] < 0.05 * len(saturados):
        print("  ATENÇÃO: o verde/sálvia quase não aparece. É o matiz de menor ativação —")
        print("  se a promessa é acolher, ele merece superfície de leitura, não só selo de confirmação.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--texto", help="cor do texto, ex. #1c1c18")
    ap.add_argument("--fundo", help="cor do fundo, ex. #fcf9f3")
    ap.add_argument("--paleta", help="JSON {papel: #hex} para tabela cruzada")
    ap.add_argument("--captura", help="PNG/JPG de uma tela, para medir dosagem de cor")
    args = ap.parse_args()

    if args.captura:
        print(f"dosagem de cor — {args.captura}")
        dosagem(args.captura)
    elif args.paleta:
        with open(args.paleta, encoding="utf-8") as fh:
            paleta = {k: hex_para_rgb(v) for k, v in json.load(fh).items()}
        print("contraste entre todos os papéis da paleta")
        tabela(paleta)
    elif args.texto and args.fundo:
        print(f"contraste {args.texto} sobre {args.fundo}")
        par(hex_para_rgb(args.texto), hex_para_rgb(args.fundo))
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

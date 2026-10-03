#!/usr/bin/env python3
"""Monta os ícones do PWA a partir da pasta de marca.

Não desenha nada: recorta, redimensiona e aplica a zona segura do ícone maskable.
A marca é a fonte — se ela muda, os ícones são regerados, nunca editados na mão.

    python3 icones.py --marca marca/ --saida public/icones

Espera encontrar em `--marca` os arquivos gerados por `marca.py`:
    favicon-32-sobre-fundo.png, favicon-180-sobre-fundo.png,
    favicon-192-sobre-fundo.png, favicon-512-sobre-fundo.png

Também copia as versões de marca usadas DENTRO do app (troca por tema via CSS):
    logo-transparente.png      -> marca/logo-marca.png
    logo-claro-transparente.png -> marca/logo-claro.png
"""
import argparse
import os
from pathlib import Path

from PIL import Image

ESCALA_MASKABLE = 0.70  # o Android pode recortar até 20% de cada lado


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--marca", default="marca", help="pasta com os arquivos da marca")
    ap.add_argument("--saida", default="public/icones", help="pasta dos ícones do app")
    ap.add_argument("--saida-marca", default=None, help="pasta da marca embutida (default: public/marca)")
    ap.add_argument("--fundo", default="#212c32", help="cor de fundo do ícone maskable")
    args = ap.parse_args()

    raiz = Path(args.marca)
    saida = Path(args.saida)
    saida_marca = Path(args.saida_marca or "public/marca")

    if not raiz.exists():
        raise SystemExit(f"pasta {raiz} não encontrada — rode marca.py antes")

    fundo = tuple(int(args.fundo.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    saida.mkdir(parents=True, exist_ok=True)
    saida_marca.mkdir(parents=True, exist_ok=True)

    copias = [
        ("favicon-32-sobre-fundo.png", "favicon-32.png"),
        ("favicon-180-sobre-fundo.png", "apple-touch-icon.png"),
        ("favicon-192-sobre-fundo.png", "icone-192.png"),
        ("favicon-512-sobre-fundo.png", "icone-512.png"),
    ]
    base_maskable = None
    for origem, destino in copias:
        caminho = raiz / origem
        if not caminho.exists():
            print(f"falta {origem} — pulando")
            continue
        imagem = Image.open(caminho).convert("RGB")
        imagem.save(saida / destino)
        print(f"ok  {destino}  ({imagem.width}x{imagem.height})")

    # maskable: fundo sólido cobrindo o quadrado + símbolo dentro da zona segura
    fonte_maskable = raiz / "logo-sobre-fundo.png"
    if fonte_maskable.exists():
        lado = 512
        tela = Image.new("RGB", (lado, lado), fundo)
        marca = Image.open(fonte_maskable).convert("RGBA")
        alvo = int(lado * ESCALA_MASKABLE)
        marca = marca.resize((alvo, alvo), Image.LANCZOS)
        tela.paste(marca, ((lado - alvo) // 2, (lado - alvo) // 2), marca)
        tela.save(saida / "icone-maskable-512.png")
        print(f"ok  icone-maskable-512.png  ({lado}x{lado}, símbolo a {int(ESCALA_MASKABLE*100)}%)")

    # marca usada dentro do app, trocando por tema via CSS
    for origem, destino in [("logo-transparente.png", "logo-marca.png"),
                            ("logo-claro-transparente.png", "logo-claro.png")]:
        caminho = raiz / origem
        if caminho.exists():
            Image.open(caminho).save(saida_marca / destino)
            print(f"ok  {saida_marca / destino}")

    # iOS exige 1024x1024 SEM canal alfa
    avatar = raiz / "avatar-1024.png"
    if avatar.exists():
        imagem = Image.open(avatar).convert("RGB")
        if imagem.size != (1024, 1024):
            imagem = imagem.resize((1024, 1024), Image.LANCZOS)
        imagem.save(saida / "ios-1024-sem-alfa.png")
        print("ok  ios-1024-sem-alfa.png  (RGB, sem alfa — exigência da App Store)")

    print()
    print("Ícones gerados a partir da marca.")


if __name__ == "__main__":
    main()

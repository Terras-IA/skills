#!/usr/bin/env python3
"""Gera o link do strudel.cc que abre já com o código de um arquivo.

Uso: strudel_url.py <arquivo.js>

O Strudel lê o código do hash da URL em base64 (UTF-8). Trocar só o hash de
uma aba já aberta não recarrega o editor: navegue e depois recarregue a página.
"""
import base64
import sys
import urllib.parse

codigo = open(sys.argv[1], encoding="utf-8").read()
print("https://strudel.cc/#" + urllib.parse.quote(base64.b64encode(codigo.encode()).decode(), safe=""))

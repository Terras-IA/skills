#!/usr/bin/env python3
"""Renderiza a prova visual da identidade: paleta, tipografia e aplicacao em PNG.

A prova e o que se olha antes de aplicar a identidade em qualquer material, e o
que se passa pelo gate visual. Ela mostra a mesma marca em fundo escuro, em fundo
claro e em documento, porque e nas trocas de fundo que o token errado aparece: o
acento que funciona no fundo escuro some no branco.

    python3 prova.py identidade/identidade.json
    python3 prova.py identidade/identidade.json --escala-base 16 --saida /tmp/prova.png

Grava `prova.html` e `prova.png` ao lado do JSON. Se houver arquivo de fonte em
`<pasta>/fontes/`, ele e embutido na prova; sem arquivo, a amostra sai com a fonte
do sistema e a prova **avisa na tela** que a tipografia e substituta — prova que
mostra fonte errada sem avisar e pior que prova nenhuma.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tokens as tk  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.join(AQUI, "..", "assets", "prova.html")
EXT_FONTE = (".woff2", ".woff", ".ttf", ".otf")

ROTULO_PAPEL = {"base": "fundo", "base_alt": "fundo alt.", "superficie": "superfície",
                "papel": "papel", "papel_alt": "papel alt.", "tinta": "tinta",
                "tinta_fraca": "tinta fraca", "texto": "texto", "texto_apoio": "texto apoio",
                "texto_lista": "texto lista", "linha": "linha", "linha_clara": "linha clara",
                "rodape": "rodapé", "acento": "acento", "acento_2": "acento 2",
                "acento_3": "acento 3", "acento_4": "acento 4"}


def cor_que_le_sobre(fundo, candidatas) -> str:
    """A cor da lista que melhor le sobre o fundo dado."""
    melhor, melhor_razao = candidatas[0], 0.0
    for h in candidatas:
        razao = tk.contraste(tk.de_hex(h), tk.de_hex(fundo))
        if razao > melhor_razao:
            melhor, melhor_razao = h, razao
    return melhor


def legenda_sobre(fundo: str) -> str:
    return "#ffffff" if tk.luminancia(tk.de_hex(fundo)) < 140 else "#111111"


def famílias(pasta: str, dados: dict) -> dict:
    """Resolve a familia de cada papel para os arquivos que existem na pasta.

    Tres origens, em ordem: o que o `identidade.json` declara por papel, o nome do
    arquivo na pasta, e nada. Devolve `{"display": {...}, "texto": {...}}` com o
    arquivo escolhido e se ele e variavel (a faixa de pesos mora num arquivo so).
    """
    disponiveis = []
    for padrao in ("fontes/*", "fonts/*"):
        for caminho in sorted(glob.glob(os.path.join(pasta, padrao))):
            if not caminho.lower().endswith(EXT_FONTE):
                continue
            base = os.path.splitext(os.path.basename(caminho))[0]
            familia = re.split(r"[-_]", base)[0].replace("-", " ").title()
            variavel = "variavel" in base or "variable" in base
            disponiveis.append({"familia": familia, "arquivo": os.path.abspath(caminho),
                                "variavel": variavel, "base": base})
    if not disponiveis:
        return {}

    # o woff2 e menor e o Chrome embute igual; entre arquivos da mesma familia,
    # prefere o variavel e depois o woff2
    def peso_escolha(a):
        return (a["familia"], not a["variavel"], not a["arquivo"].endswith(".woff2"), a["base"])

    por_familia = {}
    for d in disponiveis:
        por_familia.setdefault(d["familia"], []).append(d)
    escolhido = {f: sorted(v, key=peso_escolha)[0] for f, v in por_familia.items()}

    resolvido = {}
    declarado = dados.get("fontes") or {}
    for papel_json, papel_prova in (("display", "display"), ("texto", "texto")):
        spec = declarado.get(papel_json) or {}
        for relativo in (spec.get("arquivos") or []):
            alvo = relativo if os.path.isabs(relativo) else os.path.join(pasta, relativo)
            base = os.path.splitext(os.path.basename(alvo))[0]
            familia = re.split(r"[-_]", base)[0].replace("-", " ").title()
            if familia in escolhido:
                resolvido[papel_prova] = escolhido[familia]
                break
    familias = list(escolhido)
    if "texto" not in resolvido and familias:
        resolvido["texto"] = escolhido[familias[0]]
    if "display" not in resolvido:
        # a familia de titulo e a outra, se houver duas; com uma so, ela faz os dois papeis
        outra = [f for f in familias if f != resolvido.get("texto", {}).get("familia")]
        resolvido["display"] = escolhido[outra[0]] if outra else resolvido.get("texto")
    return resolvido


def montar_modelo(dados: dict, pasta: str, escala_base, razao) -> dict:
    cores = {k: v for k, v in (dados.get("cores") or {}).items() if tk.eh_hex(v)}
    t = tk.montar(dados, escala_base, razao)
    papel, base = t["papel"], t["base"]
    tinta = t["tinta"]
    texto_base = dados.get("cores", {}).get("texto") or cor_que_le_sobre(base, ["#ffffff", tinta])
    if tk.contraste(tk.de_hex(texto_base), tk.de_hex(base)) < 4.5:
        texto_base = cor_que_le_sobre(base, ["#ffffff", tinta])
    texto_apoio = dados.get("cores", {}).get("texto_apoio") or texto_base

    acentos = t["acentos"] or {}
    # acento do fundo escuro: o mais legivel sobre a base; do claro: a versao
    # escurecida, que e o que le sobre papel sem perder a matiz
    ordem = [a for a in acentos.values() if a.get("hex")]
    acento_base = cor_que_le_sobre(base, [a["hex"] for a in ordem]) if ordem else texto_base
    acento_papel = cor_que_le_sobre(papel, [a.get("sobre_papel") or a["hex"] for a in ordem]) if ordem else tinta

    paleta = []
    for papel_nome, h in cores.items():
        # as cores de marca tem secao propria logo abaixo, com a versao que le
        # sobre papel; repeti-las aqui so alarga a grade
        if papel_nome.startswith(("acento", "marca-")):
            continue
        c = tk.de_hex(h)
        paleta.append({
            "papel": ROTULO_PAPEL.get(papel_nome, papel_nome),
            "hex": h,
            "rgb": f"{c[0]}, {c[1]}, {c[2]}",
            "contraste": f"{tk.contraste(c, tk.de_hex(papel)):.1f}:1 no papel · {tk.contraste(c, tk.de_hex(base)):.1f}:1 no fundo",
            "luminancia": tk.luminancia(c),
        })
    paleta.sort(key=lambda p: p["luminancia"])

    marca_cores = []
    vistos = set()
    for chave, a in acentos.items():
        if not a.get("hex") or a["hex"] in vistos:
            continue
        vistos.add(a["hex"])
        sobre = a.get("sobre_papel") or a["hex"]
        marca_cores.append({"nome": a.get("nome") or chave, "hex": a["hex"], "sobrePapel": sobre,
                            "presenca": a.get("presenca") or f"papel `{chave}`",
                            "contrastePapel": f"{a['contraste_papel']:.2f}",
                            "legendaClara": legenda_sobre(a["hex"]),
                            "legendaSobrePapel": legenda_sobre(sobre)})

    disponiveis = famílias(pasta, dados)
    medidos = [n for n in (dados.get("fontes") or {}).get("nome_medido") or []]
    familia_display = (disponiveis.get("display") or {}).get("familia")
    familia_texto = (disponiveis.get("texto") or {}).get("familia")
    aviso = None
    if not disponiveis:
        aviso = ("Sem arquivo de fonte na pasta: esta amostra usa a fonte do sistema. "
                 "A tipografia da marca ainda não está instalada, então não julgue o desenho da letra aqui.")
    elif medidos and familia_display and medidos[0].split()[0].lower() not in familia_display.lower():
        aviso = (f"Amostra com {familia_display}; a peça declara {medidos[0]}. "
                 "Se não for a mesma família, a letra desta prova não é a da marca.")

    escala = [{"nome": k, "px": v} for k, v in (t["escala"] or {}).items()]
    ativos = []
    for papel_nome, spec in (dados.get("ativos") or {}).items():
        # aceita "logo_claro": "arquivo.png" ou, quando o fundo nao e obvio pelo
        # nome, {"arquivo": "...", "fundo": "escuro"} — a versao em cor de uma
        # marca de letra branca so aparece em fundo escuro, e a prova mostrando
        # ela sobre branco faz o ativo parecer quebrado
        if isinstance(spec, dict):
            arquivo, fundo = spec.get("arquivo"), spec.get("fundo")
        else:
            arquivo, fundo = spec, None
        if not isinstance(arquivo, str):
            continue
        caminho = arquivo if os.path.isabs(arquivo) else os.path.join(pasta, arquivo)
        if not os.path.exists(caminho):
            continue
        ativos.append({"papel": papel_nome, "caminho": "file://" + os.path.abspath(caminho),
                       "rotulo": ROTULO_PAPEL.get(papel_nome, papel_nome.replace("_", " ")),
                       "fundo": fundo or ("escuro" if "claro" in papel_nome else "claro")})

    assinatura = dados.get("assinatura")
    rodape = assinatura[0] if isinstance(assinatura, list) and assinatura else \
        (assinatura if isinstance(assinatura, str) else None)

    return {
        "nome": dados.get("nome") or "Identidade",
        "sub": (f"{len(dados.get('origem') or [])} peças de origem · "
                f"extraído em {dados.get('extraido_em') or '?'}"),
        "selo": "rascunho" if dados.get("status") != "revisado" else "revisado",
        "seloClasse": "rascunho" if dados.get("status") != "revisado" else "revisado",
        "paleta": paleta, "coresMarca": marca_cores,
        "fonteTitulo": familia_display,
        "fonteTexto": familia_texto,
        "avisoFonte": aviso,
        "escala": escala,
        "escalaRotulo": "Escala derivada (nao medida)" if t["escala_derivada"] else
                        ("Escala" if escala else "Escala"),
        "base": base, "papel": papel, "tinta": tinta,
        "textoBase": texto_base, "acentoBase": acento_base, "acentoPapel": acento_papel,
        "textoNoAcento": legenda_sobre(acento_papel),
        "superficiePapel": tk.misturar(tk.de_hex(papel), tk.de_hex(acento_papel), 0.07),
        "kicker": (dados.get("marca") or {}).get("nome") or "Identidade",
        "rodape": rodape or "",
        "ativos": ativos,
        "pendencias": dados.get("pendencias") or [],
        "notaRodape": ("Prova gerada por terras-identidade a partir de identidade.json. "
                       "Cor chapada é medida; tipografia só entra com arquivo de fonte na pasta."),
        "_familias": disponiveis,
    }


def recortar_vazio(png: str) -> None:
    """Corta a sobra branca embaixo: a janela do Chrome e maior que o conteudo."""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    fundo = im.getpixel((im.width - 3, im.height - 3))
    limite = im.height
    for y in range(im.height - 1, 0, -1):
        linha = [im.getpixel((x, y)) for x in range(0, im.width, 17)]
        if any(sum(abs(p[i] - fundo[i]) for i in range(3)) > 24 for p in linha):
            limite = min(im.height, y + 48)
            break
    if limite < im.height:
        im.crop((0, 0, im.width, limite)).save(png)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("identidade", help="caminho do identidade.json")
    ap.add_argument("--saida", default=None, help="PNG de saida (padrao: prova.png ao lado do JSON)")
    ap.add_argument("--largura", type=int, default=1600)
    ap.add_argument("--escala-base", type=float, default=None)
    ap.add_argument("--razao", type=float, default=1.25)
    ap.add_argument("--navegador", default=None,
                    help="binario do Chrome (padrao: google-chrome-stable e afins)")
    ap.add_argument("--altura", type=int, default=2600, help="altura da janela antes do corte do vazio")
    args = ap.parse_args()

    caminho = os.path.expanduser(args.identidade)
    if not os.path.exists(caminho):
        sys.exit(f"nao encontrei {caminho}")
    pasta = os.path.dirname(os.path.abspath(caminho))
    dados = json.load(open(caminho, encoding="utf-8"))
    modelo = montar_modelo(dados, pasta, args.escala_base, args.razao)

    template = open(os.path.abspath(MODELO), encoding="utf-8").read()
    html = template.replace("{{NOME}}", modelo["nome"]).replace("{{DADOS}}", json.dumps(modelo, ensure_ascii=False))

    # fontes embutidas por @font-face: uma familia por papel (titulo e texto), com a
    # faixa de pesos quando o arquivo e variavel
    regras = []
    for i, papel in enumerate(("display", "texto")):
        info = (modelo.get("_familias") or {}).get(papel)
        if not info:
            continue
        arquivo = info["arquivo"]
        formato = ("woff2" if arquivo.endswith(".woff2")
                   else "woff" if arquivo.endswith(".woff") else "truetype")
        faixa = "font-weight: 100 900;" if info["variavel"] else ""
        regras.append(f"@font-face {{ font-family: 'fonte-{i}'; {faixa} "
                      f"src: url('file://{arquivo}') format('{formato}'); }}")
        papel_css = "titulo" if papel == "display" else "texto"
        regras.append(f"body {{ --fonte-{papel_css}: 'fonte-{i}', system-ui, sans-serif; }}")
    if regras:
        html = html.replace("</style>", "\n".join(regras) + "\n</style>")

    saida_html = os.path.join(pasta, "prova.html")
    with open(saida_html, "w", encoding="utf-8") as fh:
        fh.write(html)

    navegador = args.navegador or next(
        (c for c in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser")
         if subprocess.run(["which", c], capture_output=True).returncode == 0), None)
    if not navegador:
        print(f"sem Chrome na maquina: prova HTML em {saida_html}")
        print("abra no navegador e imprima em PDF, ou instale o Chrome para render automatico")
        return

    saida_png = os.path.abspath(os.path.expanduser(args.saida or os.path.join(pasta, "prova.png")))
    cmd = [navegador, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--force-device-scale-factor=1", f"--window-size={args.largura},{args.altura}",
           f"--screenshot={saida_png}", "file://" + saida_html]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not os.path.exists(saida_png):
        print(r.stdout[-2000:], r.stderr[-2000:], sep="\n")
        sys.exit("o Chrome nao gerou o PNG")
    recortar_vazio(saida_png)
    print(f"prova em {saida_png}")
    print(f"html da prova em {saida_html}")
    if modelo["avisoFonte"]:
        print(f"! {modelo['avisoFonte']}")
    print("olhar a prova antes de aplicar: e nela que a troca de fundo mostra o token errado")


if __name__ == "__main__":
    main()

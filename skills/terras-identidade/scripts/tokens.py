#!/usr/bin/env python3
"""Transforma a identidade em material reutilizavel: CSS, tokens JSON, Tailwind e guia.

A identidade vive num `identidade.json` so. Este script deriva dela os arquivos
que site, sistema, documento e peca consomem, para nao existir `#0f2744` copiado
em cinco lugares diferentes envelhecendo em ritmos diferentes.

    python3 tokens.py identidade/identidade.json --destino identidade/
    python3 tokens.py identidade/identidade.json --escala-base 16 --razao 1.25

Sai em `<destino>`:

- `tokens.css`     variaveis CSS dos papeis, com as versoes para fundo claro e
                   fundo escuro ja resolvidas (acento que nao le sobre branco
                   ganha a versao escurecida, porque design system que entrega so
                   o acento puro acaba com texto ilegivel na peca impressa)
- `tokens.json`    os mesmos valores em JSON, para sistema, app e script
- `tailwind.config.js`  para projeto que usa Tailwind
- `marca.md`       o guia legivel: paleta com HEX e RGB, contraste medido,
                   tipografia, marca, linguagem e as pendencias declaradas

Nada aqui e inventado em silencio: valor medido sai com a origem, valor derivado
sai marcado como derivado, e o que falta entra na secao de pendencias do guia.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date

CABECALHO = "GERADO de identidade.json por tokens.py em {data}. Editar o JSON e gerar de novo."

# A `nota` do bloco de cores e texto que comeca com "#" (cita um hex na frase):
# sem validar a forma do hex, ela entra na lista de cores e vira amostra na prova.
HEX = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def eh_hex(valor) -> bool:
    return isinstance(valor, str) and bool(HEX.match(valor.strip()))


def de_hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_de(cor) -> str:
    return "#%02x%02x%02x" % (int(cor[0]), int(cor[1]), int(cor[2]))


def _lin(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(cor) -> float:
    return sum(w * _lin(v) for w, v in zip((0.2126, 0.7152, 0.0722), cor[:3]))


def contraste(a, b) -> float:
    la, lb = luminancia(a), luminancia(b)
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def escurecer_para(cor, fundo, minimo=4.5) -> str:
    r, g, b = cor[:3]
    fator = 1.0
    while fator > 0.15:
        atual = (int(r * fator), int(g * fator), int(b * fator))
        if contraste(atual, fundo) >= minimo:
            return hex_de(atual)
        fator -= 0.05
    return "#111111"


def clarear_para(cor, fundo, minimo=4.5) -> str:
    r, g, b = cor[:3]
    for passo in range(1, 21):
        p = passo * 0.05
        atual = tuple(int(c + (255 - c) * p) for c in (r, g, b))
        if contraste(atual, fundo) >= minimo:
            return hex_de(atual)
    return "#ffffff"


def misturar(a, b, proporcao) -> str:
    return hex_de(tuple(int(round(a[i] + (b[i] - a[i]) * proporcao)) for i in range(3)))


def montar(dados: dict, escala_base: float | None, razao: float) -> dict:
    cores = {k: v for k, v in (dados.get("cores") or {}).items() if eh_hex(v)}
    base = de_hex(cores.get("base") or "#ffffff")
    papel = de_hex(cores.get("papel") or "#ffffff")
    tinta = de_hex(cores.get("tinta") or cores.get("texto_escuro") or "#111111")
    texto = de_hex(cores.get("texto") or "#ffffff")

    acentos = {}
    for i, item in enumerate(dados.get("cores_marca") or [], start=1):
        h = item.get("hex")
        if not h:
            continue
        c = de_hex(h)
        acentos[f"marca-{i}"] = {
            "hex": h,
            "nome": item.get("nome_provisorio") or f"cor {i}",
            "presenca": item.get("presenca"),
            "contraste_base": round(contraste(c, base), 2),
            "contraste_papel": round(contraste(c, papel), 2),
            # o que faz a identidade sobreviver em fundo claro: quase todo acento
            # vivo e ilegivel sobre branco, e a versao escurecida e o que vira
            # TEXTO no documento e no site
            "sobre_papel": escurecer_para(c, papel) if contraste(c, papel) < 4.5 else h,
            "sobre_base": clarear_para(c, base) if contraste(c, base) < 4.5 else h,
        }
    # papeis nomeados tem prioridade sobre a lista de marca (o acento declarado e
    # o acento que o resto da casa espera encontrar)
    for papel_nome in ("acento", "acento_2", "acento_3", "acento_4"):
        h = cores.get(papel_nome)
        if h:
            c = de_hex(h)
            acentos[papel_nome.replace("_", "-")] = {
                "hex": h, "nome": papel_nome,
                "contraste_base": round(contraste(c, base), 2),
                "contraste_papel": round(contraste(c, papel), 2),
                "sobre_papel": escurecer_para(c, papel) if contraste(c, papel) < 4.5 else h,
                "sobre_base": clarear_para(c, base) if contraste(c, base) < 4.5 else h,
            }

    escala = {}
    if escala_base:
        nomes = ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl"]
        passos = [-2, -1, 0, 1, 2, 3, 4, 5]
        for nome, passo in zip(nomes, passos):
            escala[nome] = round(escala_base * (razao ** passo), 2)

    return {"base": cores.get("base"), "papel": papel and hex_de(papel),
            "tinta": hex_de(tinta), "texto": hex_de(texto),
            "texto_apoio": cores.get("texto_apoio") or cores.get("apoio"),
            "linha": cores.get("linha"),
            "acentos": acentos,
            "fontes": {papel: (spec or {}).get("nome") for papel, spec in (dados.get("fontes") or {}).items()
                       if isinstance(spec, dict) and spec.get("nome")},
            "escala": escala,
            "escala_derivada": bool(escala_base),
            # superficie elevada: num fundo escuro ela sobe (clareia), num fundo claro ela
            # desce de leve. Escurecer a superficie sobre fundo escuro apaga o cartao.
            "superficie": misturar(base, (255, 255, 255), 0.07) if luminancia(base) < 128
                          else misturar(papel, tinta, 0.04)}


def css(t: dict, data: str) -> str:
    L = [f"/* {CABECALHO.format(data=data)} */",
         "/* papeis medidos da marca; valor derivado vem comentado como tal */", ":root {"]
    L.append(f"  --cor-base: {t['base']};")
    L.append(f"  --cor-superficie: {t['superficie']};  /* derivado: base clareada (cartao sobre fundo escuro) */")
    if t["linha"]:
        L.append(f"  --cor-linha: {t['linha']};")
    L.append(f"  --cor-papel: {t['papel']};")
    L.append(f"  --cor-tinta: {t['tinta']};")
    L.append(f"  --cor-texto: {t['texto']};")
    if t["texto_apoio"]:
        L.append(f"  --cor-texto-apoio: {t['texto_apoio']};")
    for chave, a in t["acentos"].items():
        L.append(f"  --cor-{chave}: {a['hex']};")
        if a.get("sobre_papel") and a["sobre_papel"] != a["hex"]:
            L.append(f"  --cor-{chave}-sobre-papel: {a['sobre_papel']};  /* derivado: le sobre {t['papel']} */")
        if a.get("sobre_base") and a["sobre_base"] != a["hex"]:
            L.append(f"  --cor-{chave}-sobre-base: {a['sobre_base']};  /* derivado: le sobre {t['base']} */")
    for papel, nome in (t["fontes"] or {}).items():
        if nome:
            L.append(f'  --fonte-{papel}: "{nome}", system-ui, sans-serif;')
    for nome, valor in (t["escala"] or {}).items():
        L.append(f"  --texto-{nome}: {valor}px;")
    if t["escala_derivada"]:
        L[-1 - len(t["escala"])] += ""
        L.append("  /* a escala acima e DERIVADA (base e razao escolhidas), nao medida da peca */")
    L.append("}")
    L.append("")
    L.append("/* tema claro: o mesmo papel, invertido para papel branco */")
    L.append(":root[data-tema=\"claro\"] {")
    L.append(f"  --cor-base: {t['papel']};")
    L.append(f"  --cor-texto: {t['tinta']};")
    for chave, a in t["acentos"].items():
        if a.get("sobre_papel"):
            L.append(f"  --cor-{chave}: {a['sobre_papel']};")
    L.append("}")
    return "\n".join(L) + "\n"


def tailwind(t: dict) -> str:
    cores = {f"base": t["base"], "superficie": t["superficie"], "papel": t["papel"],
             "tinta": t["tinta"], "texto": t["texto"]}
    if t["texto_apoio"]:
        cores["texto-apoio"] = t["texto_apoio"]
    if t["linha"]:
        cores["linha"] = t["linha"]
    for chave, a in t["acentos"].items():
        cores[chave] = a["hex"]
        if a.get("sobre_papel"):
            cores[f"{chave}-sobre-papel"] = a["sobre_papel"]
    fontes = {papel: [nome, "system-ui", "sans-serif"] for papel, nome in (t["fontes"] or {}).items() if nome}
    linhas = ["// gerado de identidade.json por tokens.py — nao editar a mao",
              "module.exports = {", "  theme: {", "    extend: {",
              "      colors: " + json.dumps(cores, ensure_ascii=False, indent=6).replace('"', "'") + ",",]
    if fontes:
        linhas.append("      fontFamily: " + json.dumps(fontes, ensure_ascii=False, indent=6).replace('"', "'") + ",")
    if t["escala"]:
        linhas.append("      fontSize: " + json.dumps({k: [f"{v}px", f"{round(v*1.4,1)}px"] for k, v in t["escala"].items()},
                                                      ensure_ascii=False, indent=6).replace('"', "'") + ",")
    linhas += ["    },", "  },", "};"]
    return "\n".join(linhas) + "\n"


def guia(dados: dict, t: dict, data: str) -> str:
    nome = dados.get("nome") or "identidade"
    rascunho = dados.get("status") != "revisado"
    L = [f"# {nome} — identidade visual", ""]
    if rascunho:
        L += ["> **Rascunho.** Este guia saiu de extração automática e não foi conferido por uma pessoa. "
              "Valor daqui não deve virar guia de marca nem ser citado como oficial antes da conferência.", ""]
    L += [f"Gerado de `identidade.json` em {data}.", ""]
    desc = dados.get("descricao")
    if desc:
        L += [desc, ""]

    L += ["## Cores", "", "| Papel | HEX | RGB | Contraste | Uso |", "|---|---|---|---|---|"]
    usos = {"base": "fundo principal", "base_alt": "fundo secundário", "superficie": "superfície elevada",
            "papel": "fundo claro, impresso", "papel_alt": "fundo claro secundário",
            "tinta": "texto sobre claro", "tinta_fraca": "texto fraco sobre claro",
            "texto": "texto sobre o fundo escuro", "texto_apoio": "texto secundário",
            "texto_lista": "itens de lista", "rodape": "rodapé",
            "linha": "filetes, bordas, divisores", "linha_clara": "filetes sobre claro"}
    for papel, valor in (dados.get("cores") or {}).items():
        # as cores de marca tem a tabela propria logo abaixo, com a versao que le
        # sobre papel; aqui ficam os papeis de sistema (fundo, texto, filete)
        if not eh_hex(valor) or papel.startswith(("acento", "marca-")):
            continue
        c = de_hex(valor)
        L.append(f"| `{papel}` | `{valor}` | {c[0]}, {c[1]}, {c[2]} | "
                 f"{contraste(c, de_hex(t['papel'])):.1f}:1 sobre papel · {contraste(c, de_hex(t['base'])):.1f}:1 sobre base | "
                 f"{usos.get(papel, '')} |")
    L.append("")
    if (dados.get("cores") or {}).get("nota"):
        L += [dados["cores"]["nota"], ""]
    if t["acentos"]:
        L += ["### Cores de marca", "",
              "| Cor | HEX | Presença | Sobre o papel | Sobre o fundo |", "|---|---|---|---|---|"]
        vistos = set()
        for chave, a in t["acentos"].items():
            # o mesmo hex entra duas vezes quando a cor e declarada como cores_marca
            # e tambem como papel `acento`; na tabela ela aparece uma vez so
            if a["hex"] in vistos:
                continue
            vistos.add(a["hex"])
            L.append(f"| {a.get('nome') or chave} | `{a['hex']}` | {a.get('presenca') or '-'} | "
                     f"{a['contraste_papel']}:1 → `{a['sobre_papel']}` | "
                     f"{a['contraste_base']}:1 → `{a['sobre_base']}` |")
        L += ["", "A coluna *sobre o papel* é a versão que **lê como texto** em fundo claro; a cor pura "
              "continua valendo para preenchimento, barra e ícone. Contraste abaixo de 4.5:1 em texto "
              "reprova em acessibilidade.", ""]
    if dados.get("tons_descartados"):
        L += [f"Tons descartados dos papéis (média de acento com fundo, não são cor da marca): "
              f"{', '.join('`'+h+'`' for h in dados['tons_descartados'])}", ""]

    L += ["## Tipografia", ""]
    fontes = dados.get("fontes") or {}
    nomes = fontes.get("nome_medido") or []
    if nomes:
        L += [f"**Medido do documento-fonte:** {', '.join(nomes)}", ""]
        if fontes.get("nota"):
            L += [fontes["nota"], ""]
        for origem in fontes.get("origens") or []:
            if origem.get("fontes"):
                L += [f"- `{os.path.basename(origem['arquivo'])}`: {', '.join(origem['fontes'])} ({origem['como']})"]
        L.append("")
    else:
        L += ["**Não medida.** Raster não guarda nome de fonte: identificar a família a olho em "
              "`references/tipografia.md` e escolher o equivalente livre antes de usar em qualquer material.", ""]
    if t["escala"]:
        L += ["| Passo | Tamanho |", "|---|---|"]
        for k, v in t["escala"].items():
            L.append(f"| `{k}` | {v}px |")
        L += ["", ("Escala **derivada** (base e razão escolhidas por quem gerou, não medidas da peça): "
                   "ajustar por alvo, não tratar como especificação." if t["escala_derivada"] else ""), ""]

    L += ["## Marca", ""]
    marca = dados.get("marca") or {}
    if marca.get("estilo"):
        L += [f"Forma preferencial: `{marca['estilo']}`. Formas disponíveis: "
              f"{', '.join(marca.get('estilos_disponiveis') or [])}.", ""]
    if marca.get("nota"):
        L += [marca["nota"], ""]
    # ativo entra como "papel": "arquivo.png" ou como {"arquivo": ..., "fundo": ...}
    ativos = {}
    for k, v in (dados.get("ativos") or {}).items():
        if isinstance(v, str):
            ativos[k] = v
        elif isinstance(v, dict) and isinstance(v.get("arquivo"), str):
            ativos[k] = v["arquivo"] + (f" (fundo {v['fundo']})" if v.get("fundo") else "")
    if ativos:
        L += ["| Ativo | Arquivo |", "|---|---|"]
        for k, v in ativos.items():
            L.append(f"| `{k}` | `{v}` |")
        if (dados.get("ativos") or {}).get("nota"):
            L += ["", (dados["ativos"]["nota"]), ""]

    # artes de campanha: nao sao marca, mas viajam com a identidade e fazem falta
    # quando alguem monta uma peca nova
    artes = {k: v for k, v in (dados.get("artes") or {}).items()
             if isinstance(v, str) and k != "nota"}
    if artes:
        L += ["| Arte de campanha | Arquivo |", "|---|---|"]
        for k, v in artes.items():
            L.append(f"| `{k}` | `{v}` |")
        if (dados.get("artes") or {}).get("nota"):
            L += ["", dados["artes"]["nota"]]
        L.append("")

    if (dados.get("linguagem") or {}).get("nota") or len(dados.get("linguagem") or {}) > 1:
        L += ["## Linguagem visual", ""]
        for k, v in (dados.get("linguagem") or {}).items():
            if isinstance(v, list):
                L += [f"**{k.replace('_', ' ').capitalize()}:** " + "; ".join(str(x) for x in v), ""]
            elif isinstance(v, str):
                L += [f"**{k.replace('_', ' ').capitalize()}:** {v}", ""]

    L += ["## Aplicação por alvo", "",
          "| Alvo | Como a identidade entra | Arquivo |", "|---|---|---|",
          "| Site | variáveis CSS (tema escuro no `:root`, claro em `[data-tema=\"claro\"]`) | `tokens.css` |",
          "| Sistema / app | tokens JSON | `tokens.json` |",
          "| Projeto Tailwind | tema estendido | `tailwind.config.js` |",
          "| Documento (Word/Docs) | cores RGB da tabela de cores e fonte na família declarada | este guia |",
          "| Peça de marketing | HTML com as variáveis + render por Chrome | `tokens.css` |", ""]

    pend = dados.get("pendencias") or []
    L += ["## Pendências", ""]
    L += [f"- {p}" for p in pend] if pend else ["- nenhuma declarada"]
    L.append("")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("identidade", help="caminho do identidade.json")
    ap.add_argument("--destino", default=None, help="onde gravar (padrao: pasta do JSON)")
    ap.add_argument("--escala-base", type=float, default=None,
                    help="tamanho base em px para derivar a escala (ex.: 16); sem isso, nenhuma escala sai")
    ap.add_argument("--razao", type=float, default=1.25, help="razao da escala derivada (padrao 1.25)")
    args = ap.parse_args()

    caminho = os.path.expanduser(args.identidade)
    if not os.path.exists(caminho):
        sys.exit(f"nao encontrei {caminho}")
    dados = json.load(open(caminho, encoding="utf-8"))
    if not (dados.get("cores") or {}).get("base"):
        sys.exit("identidade sem `cores.base`: preencher antes de gerar tokens")
    destino = os.path.abspath(os.path.expanduser(args.destino or os.path.dirname(caminho)))
    os.makedirs(destino, exist_ok=True)
    data = date.today().isoformat()
    t = montar(dados, args.escala_base, args.razao)

    escritos = []
    for nome, conteudo in (("tokens.css", css(t, data)),
                           ("tokens.json", json.dumps(
                               {"nome": dados.get("nome"), "gerado_em": data,
                                "_aviso": CABECALHO.format(data=data), **t}, ensure_ascii=False, indent=2) + "\n"),
                           ("tailwind.config.js", tailwind(t)),
                           ("marca.md", guia(dados, t, data))):
        with open(os.path.join(destino, nome), "w", encoding="utf-8") as fh:
            fh.write(conteudo)
        escritos.append(nome)

    print(f"gerados em {destino}: {', '.join(escritos)}")
    print(f"base {t['base']} | papel {t['papel']} | tinta {t['tinta']} | texto {t['texto']}")
    for chave, a in t["acentos"].items():
        aviso = "" if a["hex"] == a.get("sobre_papel") else f" (texto sobre papel: {a['sobre_papel']})"
        print(f"  {chave}: {a['hex']}{aviso}")
    if dados.get("status") != "revisado":
        print("! a identidade ainda esta marcada como rascunho: conferir antes de aplicar em material de cliente")


if __name__ == "__main__":
    main()

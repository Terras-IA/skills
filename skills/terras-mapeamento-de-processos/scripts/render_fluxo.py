#!/usr/bin/env python3
"""Renderiza o processo.json como diagrama de raias (swimlane) em SVG + PNG.

Diferente do gerar_mermaid.py (portátil, texto), aqui a saída é o desenho de
apresentação: raias horizontais com ícone do ator, nó com ícone e identificador
do passo (P1, P2...), decisão em losango, espera tracejada, setas condicionais
verde/vermelha e conectores de quebra de faixa.

Uso:
  python3 render_fluxo.py --json processo.json --saida as-is --titulo "Fluxo AS-IS — Financeiro"
  python3 render_fluxo.py --json processo.json --saida as-is --png   # gera o PNG via chromium

Layout opcional no JSON (chave "layout"):
  "layout": {
    "titulo": "Fluxo AS-IS — Financeiro",
    "colunas": 8,
    "rotulos": {"P3->P4": "sim", "P14->P15": "não / pagou"},
    "vermelhas": ["P14->P15"],
    "tracejadas": ["P12->P13"]
  }

Sem chromium disponível, o HTML/SVG continua válido (abre em qualquer navegador).
"""
import argparse
import html
import json
import os
import shutil
import struct
import subprocess
import sys

# ---- geometria -------------------------------------------------------------
LARG_RAIA = 210          # coluna do nome do ator
MARGEM = 40
NODE_W = 232
NODE_H = 88
GAP_X = 108              # vão entre nós: cabe o rótulo da seta
GAP_Y = 36
TITULO_H = 96
SEPARADOR = 232          # linha que separa a coluna do ator do miolo do fluxo
CORREDOR = 242           # corredor vertical das setas de quebra de faixa
FONTE = "Arial, Helvetica, sans-serif"

CORES = {
    "tarefa":     ("#eaf2fb", "#4a7fb5"),
    "decisao":    ("#e6f5ea", "#3f8f57"),
    "espera":     ("#fff6e8", "#c98a2b"),
    "sistema":    ("#e9f1fb", "#3f6fa5"),
    "documento":  ("#eef0fb", "#5b64b5"),
    "aprovacao":  ("#eef0fb", "#5b64b5"),
    "inicio":     ("#e6f5ea", "#2f8f4f"),
    "fim":        ("#e6f5ea", "#2f8f4f"),
}

# ---- ícones (SVG inline, traço 1.7, 24x24) ---------------------------------
ICONES = {
    "user": '<path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z"/><path d="M4.5 20c1.2-3.6 4-5.5 7.5-5.5s6.3 1.9 7.5 5.5"/>',
    "bot": '<rect x="4" y="8" width="16" height="11" rx="3"/><path d="M12 8V5"/><circle cx="12" cy="4" r="1.3"/><circle cx="9" cy="13.5" r="1.1"/><circle cx="15" cy="13.5" r="1.1"/>',
    "person_gear": '<circle cx="10" cy="9" r="3.6"/><path d="M3.5 20c1-3.2 3.5-5 6.5-5 1 0 1.9.2 2.7.6"/><circle cx="18" cy="17" r="3"/><path d="M18 12.8v1.4M18 19.8v1.4M14.2 17h1.4M20.4 17h1.4"/>',
    "bank": '<path d="M3 9.5 12 4l9 5.5"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/><path d="M3 20.5h18"/>',
    "database": '<ellipse cx="12" cy="6" rx="7.5" ry="3"/><path d="M4.5 6v12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3V6"/><path d="M4.5 12c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3"/>',
    "server": '<rect x="4" y="4" width="16" height="6.5" rx="2"/><rect x="4" y="13.5" width="16" height="6.5" rx="2"/><circle cx="8" cy="7.2" r=".9"/><circle cx="8" cy="16.7" r=".9"/>',
    "doc": '<path d="M6 3.5h7l5 5v12H6z"/><path d="M13 3.5v5h5"/><path d="M9 13h6M9 16.5h4"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8L16.5 9.5"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.6 15.5 12 10 15.4z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="m3.8 7 8.2 6 8.2-6"/>',
    "chat": '<path d="M4.5 5.5h15v11h-8L7 21v-4.5H4.5z"/>',
    "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M12 3.5v2.2M12 18.3v2.2M4.8 7.8l1.9 1.1M17.3 15.1l1.9 1.1M4.8 16.2l1.9-1.1M17.3 8.9l1.9-1.1"/>',
    "filter": '<path d="M4 5.5h16l-6.2 7.3v5.7l-3.6-2v-3.7z"/>',
}

POR_TIPO = {
    "tarefa": "gear", "decisao": "filter", "espera": "clock", "sistema": "server",
    "documento": "doc", "aprovacao": "check",
}
POR_ATOR = [
    (("cliente", "solicitante", "usuário", "usuario"), "user"),
    (("ia", "bot", "assistente", "maya", "agente"), "bot"),
    (("analista", "financeiro", "backoffice", "gestor", "time", "equipe"), "person_gear"),
    (("banco", "gateway", "institui"), "bank"),
    (("erp", "sistema", "hubspot", "crm", "portal", "app", "api"), "database"),
]


def icone_ator(nome):
    n = (nome or "").lower()
    for chaves, icone in POR_ATOR:
        if any(c in n for c in chaves):
            return icone
    return "person_gear"


def svg_icone(nome, x, y, tam=22, cor="#3d6b9e", largura=1.7):
    path = ICONES.get(nome, ICONES["gear"])
    escala = tam / 24.0
    return (
        '<g transform="translate({:.1f},{:.1f}) scale({:.4f})" fill="none" stroke="{}" '
        'stroke-width="{}" stroke-linecap="round" stroke-linejoin="round">{}</g>'
    ).format(x, y, escala, cor, largura / escala if escala else largura, path)


def quebrar(texto, limite=30, max_linhas=3):
    palavras, linhas, atual = str(texto or "").split(), [], ""
    for p in palavras:
        if len(atual) + len(p) + 1 <= limite:
            atual = (atual + " " + p).strip()
        else:
            linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    if len(linhas) > max_linhas:
        linhas = linhas[:max_linhas]
        linhas[-1] = linhas[-1][: limite - 1] + "…"
    return linhas


def svg_texto(linhas, cx, cy, tamanho=14.5, cor="#173a5e", peso="600"):
    total = len(linhas)
    passo = tamanho + 3
    y0 = cy - (total - 1) * passo / 2 + tamanho / 3.0
    saida = []
    for i, linha in enumerate(linhas):
        saida.append(
            '<text x="{:.1f}" y="{:.1f}" font-family="{}" font-size="{}" font-weight="{}" '
            'fill="{}" text-anchor="middle">{}</text>'.format(
                cx, y0 + i * passo, FONTE, tamanho, peso, cor, html.escape(linha)))
    return "".join(saida)


def nos(dados, colunas):
    """Sequência de nós: início + passos + fim, com faixa (band) e coluna."""
    passos = dados.get("passos", [])
    if not passos:
        raise SystemExit("JSON sem passos — revise a extração antes de desenhar.")
    gatilho = (dados.get("gatilho") or "Início").strip()
    sequencia = [{"id": "INICIO", "tipo": "inicio", "nome": gatilho, "ator": passos[0].get("ator"),
                  "rotulo_extra": "Início"}]
    sequencia += passos
    sequencia.append({"id": "FIM", "tipo": "fim", "nome": dados.get("fim") or "Concluído",
                      "ator": passos[-1].get("ator"), "rotulo_extra": "Fim"})

    for i, n in enumerate(sequencia):
        n["_band"] = i // colunas
        n["_col"] = i % colunas

    faixas = {}
    for n in sequencia:
        faixas.setdefault(n["_band"], [])
        if n["ator"] not in faixas[n["_band"]]:
            faixas[n["_band"]].append(n["ator"])
    for n in sequencia:
        n["_lane"] = faixas[n["_band"]].index(n["ator"])
    return sequencia, faixas


def rotulo_no(n):
    nome = n.get("nome") or ""
    if n["tipo"] == "decisao" and not nome.rstrip().endswith("?"):
        nome += "?"
    return quebrar(nome, 26, 3)


def desenhar(dados, titulo, colunas):
    sequencia, faixas = nos(dados, colunas)
    layout = dados.get("layout") or {}
    rotulos = layout.get("rotulos") or {}
    vermelhas = set(layout.get("vermelhas") or [])
    tracejadas = set(layout.get("tracejadas") or [])

    altura_faixa = NODE_H + GAP_Y
    altura_faixas = {b: len(lanes) * altura_faixa + 26 for b, lanes in faixas.items()}
    y_band = {}
    acumulado = TITULO_H
    for b in sorted(faixas):
        y_band[b] = acumulado
        acumulado += altura_faixas[b] + 26

    largura = LARG_RAIA + MARGEM * 2 + colunas * NODE_W + (colunas - 1) * GAP_X
    altura = acumulado + 30

    def x_no(n):
        return LARG_RAIA + MARGEM + n["_col"] * (NODE_W + GAP_X)

    def y_no(n):
        return y_band[n["_band"]] + 13 + n["_lane"] * altura_faixa + (altura_faixa - NODE_H) / 2.0

    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" width="{:.0f}" height="{:.0f}" '
               'viewBox="0 0 {:.0f} {:.0f}" font-family="{}">'.format(largura, altura, largura, altura, FONTE))
    svg.append('<defs>')
    for cor, nome in (("#2b4a6f", "seta"), ("#c0392b", "seta-vermelha"), ("#2f8f4f", "seta-verde")):
        svg.append('<marker id="{}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                   'markerHeight="7" orient="auto-start-reverse">'
                   '<path d="M0,0 L10,5 L0,10 z" fill="{}"/></marker>'.format(nome, cor))
    svg.append('</defs>')
    svg.append('<rect width="100%" height="100%" fill="#ffffff"/>')
    svg.append('<rect x="6" y="6" width="{:.0f}" height="{:.0f}" rx="18" fill="none" '
               'stroke="#c9d8e8" stroke-width="2"/>'.format(largura - 12, altura - 12))
    svg.append('<text x="{:.0f}" y="56" font-size="30" font-weight="700" fill="#12395e" '
               'text-anchor="middle">{}</text>'.format(largura / 2, html.escape(titulo)))

    # raias
    for b, lanes in sorted(faixas.items()):
        for i, ator in enumerate(lanes):
            y = y_band[b] + 13 + i * altura_faixa
            fundo = "#eef4fb" if i % 2 == 0 else "#f6f9fd"
            svg.append('<rect x="{:.0f}" y="{:.0f}" width="{:.0f}" height="{:.0f}" rx="12" '
                       'fill="{}" stroke="#dbe6f2"/>'.format(MARGEM, y, largura - MARGEM * 2 - 6,
                                                            altura_faixa - 10, fundo))
            svg.append(svg_icone(icone_ator(ator), MARGEM + 34, y + altura_faixa / 2 - 30, 34, "#3d6b9e", 1.5))
            svg.append(svg_texto(quebrar(ator, 16, 2), MARGEM + 108, y + altura_faixa / 2 + 22, 14.5, "#254a72", "700"))
        svg.append('<line x1="{:.0f}" y1="{:.0f}" x2="{:.0f}" y2="{:.0f}" stroke="#dbe6f2"/>'.format(
            SEPARADOR, y_band[b], SEPARADOR, y_band[b] + altura_faixas[b] - 10))

    # nós
    for n in sequencia:
        x, y = x_no(n), y_no(n)
        cx, cy = x + NODE_W / 2, y + NODE_H / 2
        fill, stroke = CORES.get(n["tipo"], CORES["tarefa"])
        linhas = rotulo_no(n)
        if n["tipo"] == "decisao":
            pontos = "{},{} {},{} {},{} {},{}".format(
                cx, y, x + NODE_W, cy, cx, y + NODE_H, x, cy)
            svg.append('<polygon points="{}" fill="{}" stroke="{}" stroke-width="1.8"/>'.format(pontos, fill, stroke))
            svg.append(svg_texto(linhas, cx, cy, 13, "#1d4a2c"))
        else:
            tracejado = ' stroke-dasharray="7 5"' if n["tipo"] == "espera" else ""
            svg.append('<rect x="{:.0f}" y="{:.0f}" width="{}" height="{}" rx="10" fill="{}" '
                       'stroke="{}" stroke-width="1.8"{} />'.format(x, y, NODE_W, NODE_H, fill, stroke, tracejado))
            # texto ocupa a área à direita do ícone (nunca por baixo dele)
            cx_texto = x + 48 + (NODE_W - 60) / 2.0
            if n["tipo"] in ("inicio", "fim"):
                ic = "play" if n["tipo"] == "inicio" else "check"
                svg.append(svg_icone(ic, x + 11, cy - 13, 26, stroke, 1.8))
                svg.append(svg_texto(linhas, cx_texto, cy, 13.5, "#1d4a2c"))
            else:
                svg.append(svg_icone(POR_TIPO.get(n["tipo"], "gear"), x + 11, cy - 12, 24, stroke, 1.7))
                svg.append(svg_texto(linhas, cx_texto, cy, 13.5, "#173a5e"))
        if n["id"] not in ("INICIO", "FIM"):
            svg.append('<rect x="{:.0f}" y="{:.0f}" width="34" height="19" rx="6" fill="#ffffff" '
                       'stroke="{}" stroke-opacity="0.5"/>'.format(x + 8, y - 9, stroke))
            svg.append('<text x="{:.0f}" y="{:.0f}" font-size="12" font-weight="700" fill="{}" '
                       'text-anchor="middle">{}</text>'.format(x + 25, y + 4.5, stroke, n["id"]))
        n["_x"], n["_y"] = x, y

    # setas
    for a, b in zip(sequencia, sequencia[1:]):
        chave = "{}->{}".format(a["id"], b["id"])
        cor = "#c0392b" if chave in vermelhas else "#2b4a6f"
        marcador = "seta-vermelha" if chave in vermelhas else "seta"
        tracejado = ' stroke-dasharray="8 6"' if chave in tracejadas else ""
        ax, ay = a["_x"] + NODE_W, a["_y"] + NODE_H / 2
        bx, by = b["_x"], b["_y"] + NODE_H / 2
        if a["_band"] == b["_band"] and b["_col"] == a["_col"] + 1 and a["_lane"] == b["_lane"]:
            d = "M{:.0f},{:.0f} H{:.0f}".format(ax, ay, bx)
            mx, my = (ax + bx) / 2, ay
        elif a["_band"] == b["_band"]:
            meio = bx - GAP_X / 2
            d = "M{:.0f},{:.0f} H{:.0f} V{:.0f} H{:.0f}".format(ax, ay, meio, by, bx)
            mx, my = meio, (ay + by) / 2
        else:
            # quebra de faixa: desce pela última raia, corre pela margem esquerda
            # do miolo (sem invadir a coluna dos atores) e entra no primeiro nó
            corredor = CORREDOR
            base = a["_y"] + NODE_H + 18
            d = "M{:.0f},{:.0f} V{:.0f} H{:.0f} V{:.0f} H{:.0f}".format(
                a["_x"] + NODE_W / 2, a["_y"] + NODE_H, base, corredor, by, bx)
            mx, my = corredor + 4, by - 30
        svg.append('<path d="{}" fill="none" stroke="{}" stroke-width="2.2" marker-end="url(#{})"{} />'.format(
            d, cor, marcador, tracejado))
        if chave in rotulos:
            linhas_rot = quebrar(rotulos[chave], 16, 2)
            w = max(34, 6.6 * max(len(l) for l in linhas_rot) + 14)
            mx = min(max(mx, CORREDOR + w / 2), b["_x"] - w / 2 - 4) if b["_x"] > a["_x"] else mx + 6
            altura_rot = 15 * len(linhas_rot) + 8
            svg.append('<rect x="{:.0f}" y="{:.0f}" width="{:.0f}" height="{:.0f}" rx="7" fill="#ffffff" '
                       'stroke="{}" stroke-opacity="0.5"/>'.format(mx - w / 2, my - altura_rot - 6, w, altura_rot, cor))
            for i, linha in enumerate(linhas_rot):
                svg.append('<text x="{:.0f}" y="{:.0f}" font-size="11.5" font-weight="700" fill="{}" '
                           'text-anchor="middle">{}</text>'.format(
                               mx, my - altura_rot + 4 + i * 15, cor, html.escape(linha)))

    svg.append('</svg>')
    return "\n".join(svg), largura, altura


def png_do_svg(svg, destino_png, largura, altura, escala=2):
    navegador = None
    for cand in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        if shutil.which(cand):
            navegador = shutil.which(cand)
            break
    if not navegador:
        return False, "chromium não encontrado — o SVG/HTML continua válido"
    tmp_html = destino_png + ".html"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write('<!doctype html><html><body style="margin:0;background:#fff">' + svg + '</body></html>')
    cmd = [navegador, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--force-device-scale-factor={}".format(escala),
           "--screenshot={}".format(os.path.abspath(destino_png)),
           "--window-size={:.0f},{:.0f}".format(largura, altura),
           "file://" + os.path.abspath(tmp_html)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except Exception as e:  # noqa: BLE001
        return False, "falha ao renderizar no navegador: {}".format(e)
    finally:
        if os.path.exists(tmp_html):
            os.remove(tmp_html)
    try:
        with open(destino_png, "rb") as f:
            w, h = struct.unpack(">II", f.read(24)[16:24])
        return True, "PNG {}x{} px (escala {})".format(w, h, escala)
    except Exception:  # noqa: BLE001
        return True, "PNG gerado"


def main() -> int:
    ap = argparse.ArgumentParser(description="processo.json -> diagrama de raias (SVG + PNG)")
    ap.add_argument("--json", required=True)
    ap.add_argument("--saida", required=True, help="base de saída (gera <base>.svg e, com --png, <base>.png)")
    ap.add_argument("--titulo", default=None)
    ap.add_argument("--colunas", type=int, default=None, help="nós por faixa antes de quebrar (default 8)")
    ap.add_argument("--png", action="store_true", help="gera o PNG via navegador headless")
    ap.add_argument("--escala", type=int, default=2)
    args = ap.parse_args()

    with open(args.json, encoding="utf-8") as f:
        dados = json.load(f)
    layout = dados.get("layout") or {}
    titulo = args.titulo or layout.get("titulo") or dados.get("processo", "Fluxo")
    colunas = args.colunas or layout.get("colunas") or 8

    svg, largura, altura = desenhar(dados, titulo, colunas)
    base = args.saida[:-4] if args.saida.endswith((".svg", ".png")) else args.saida
    with open(base + ".svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("SVG gerado: {}.svg ({:.0f}x{:.0f})".format(base, largura, altura))
    if args.png:
        ok, msg = png_do_svg(svg, base + ".png", largura, altura, args.escala)
        print(("PNG: " if ok else "AVISO: ") + msg)
        if not ok:
            return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

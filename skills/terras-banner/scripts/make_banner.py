#!/usr/bin/env python3
"""Monta o banner: spec JSON -> HTML -> PNG, com conferência de encaixe.

Uso:
    python3 make_banner.py --spec banner.json
    python3 make_banner.py --spec banner.json --check      # falha (exit 1) se algo estourar
    python3 make_banner.py --spec banner.json --html /tmp/banner.html

Spec (só `out` e `headline` são obrigatórios):
{
  "out": "/caminho/banner.png",
  "html": "/caminho/banner.html",          // opcional, default: mesmo nome do out
  "size": "1080x1440",                     // qualquer WxH; padrao retrato 3:4 desde 23/09
  "lang": "pt-BR",
  "kick": "DIGEST · SETEMBRO 2026",
  "headline": "Doze temas<br>em <em>três dias</em>",
  "sub": "O prazo que machuca é <b>o que ninguém assumiu</b>.",
  "stats": [["04", "datas de fim de suporte"], ["05", "sobre agentes"]],
  "foot": "eolimabr.substack.com",
  "bg": "/caminho/arte.png",                // arte gerada; sem isso o fundo é chapado com glow
  "base": "#0b1220",
  "accent": "#ffcc33",
  "scrim": 0.94,                            // opacidade do scrim à esquerda (só com bg)
  "scrim_angle": 100
}

O texto aceita HTML inline (<br>, <b>, <em class="accent">). Nada de markdown.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Template e fontes vivem no diretorio padrao da identidade, nao na skill: editar
# la vale para banner e video ao mesmo tempo. Ver LEIA-ME.md daquele diretorio.
BRAND_DIR = os.path.expanduser(os.environ.get("TERRAS_BRAND_DIR", "~/Documents/Diversos/terras-brand"))
TEMPLATE = os.path.join(BRAND_DIR, "templates", "banner.html")
FONTS_DIR = os.path.join(BRAND_DIR, "fonts")


def brand_tokens():
    try:
        with open(os.path.join(BRAND_DIR, "brand.json"), encoding="utf-8") as fh:
            return json.load(fh).get("cores", {})
    except (OSError, ValueError):
        return {}


def brand_default(key, fallback):
    return brand_tokens().get(key) or fallback
SIZE_RE = re.compile(r"^(\d{3,4})x(\d{3,4})$")


def hex_to_rgb(value):
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgba(hex_color, alpha):
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{round(alpha, 3)})"


def find_chrome():
    for name in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("nenhum Chrome/Chromium no PATH")


def build_metrics(width, height, linkedin=False):
    """Toma o banner 1200x628 como referência.

    A escala é o menor dos dois eixos: escalar pela altura sozinha estoura o tipo
    em canvas vertical (num 1080x1350 a manchete sairia com 189px e tudo colide).
    A variante "linkedin" (carrossel no app, leitura ocidental de cima para baixo)
    infla a fonte para mobile e destaca os números da régua.
    """
    s = min(width / 1200, height / 628)
    tall = height / width > 1.2
    f_h1 = 1.18 if linkedin else 1.0
    f_sub = 1.15 if linkedin else 1.0
    f_eye = 1.1 if linkedin else 1.0
    f_n = 1.6 if linkedin else 1.0
    f_l = 1.15 if linkedin else 1.0
    return {
        "W": width,
        "H": height,
        "PAD": round(78 * s),
        # Canvas em pé: texto no terço superior, como cartaz, e dados no rodapé.
        "TOP": round(height * 0.24) if tall else round(96 * s),
        "BOTTOM": round(44 * s),
        "HEAD_EXTRA": "",
        "EYE_SIZE": round(15 * s * f_eye),
        "EYE_GAP": round(14 * s),
        "EYE_RULE": round(34 * s),
        "H1_TOP": round(26 * s),
        "H1_SIZE": round(88 * s * f_h1),
        "SUB_TOP": round(24 * s),
        "SUB_SIZE": round(27 * s * f_sub),
        "STAT_PAD": round(26 * s),
        "STAT_GAP": round(10 * s),
        "STAT_N": round(40 * s * f_n),
        "STAT_L": round(19 * s * f_l),
        "FOOT_SIZE": round(17 * s),
        "FLOOR_H": round(230 * s),
        "TALL_CLASS": " tall" if tall else "",
        "LAYOUT_CLASS": " linkedin" if linkedin else "",
        "TEMA_CLASS": "",  # preenchido depois do spec
    }


def build_stats_html(stats, scale):
    if not stats:
        return ""
    parts = []
    for item in stats:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            number, label = item
        else:
            number, label = "", str(item)
        parts.append(
            f'<div class="stat"><span class="n">{number}</span>'
            f'<span class="l">{label}</span></div>'
        )
    return "".join(parts)


def load_template():
    if not os.path.exists(TEMPLATE):
        sys.exit(
            f"template nao encontrado em {TEMPLATE}.\n"
            "O diretorio padrao da identidade sumiu ou mudou de lugar.\n"
            "Recriar o que falta: bash ~/.zcode/skills/terras-video/scripts/setup-brand.sh"
        )
    with open(TEMPLATE) as fh:
        return fh.read()


def render_html(spec, metrics):
    html = load_template()

    base = spec.get("base") or brand_default("base_alt", "#0b1220")
    accent = spec.get("accent") or brand_default("acento", "#ffcc33")
    bg = spec.get("bg")
    scale = metrics["H"] / 628

    if bg:
        bg_css = f"url('file://{os.path.abspath(bg)}')"
        scrim = float(spec.get("scrim", 0.94))
        stops = {
            "BASE_RGBA_STRONG": rgba(base, scrim),
            "BASE_RGBA_MID": rgba(base, max(0.0, scrim - 0.08)),
            "BASE_RGBA_SOFT": rgba(base, max(0.0, scrim - 0.42)),
            "SCRIM_STOP": 34,
        }
    else:
        # Fundo chapado: glow no acento e vinheta, senão fica lavado e vazio.
        r, g, b = hex_to_rgb(accent)
        bg_css = (
            f"radial-gradient(115% 90% at 50% 0%, rgba(0,0,0,0) 42%, rgba(0,0,0,0.38) 100%), "
            f"radial-gradient(circle at 76% 16%, rgba({r},{g},{b},0.13) 0%, "
            f"rgba({r},{g},{b},0) 58%), radial-gradient(circle at 6% 96%, "
            f"rgba({r},{g},{b},0.07) 0%, rgba({r},{g},{b},0) 60%)"
        )
        stops = {
            "BASE_RGBA_STRONG": rgba(base, 0.0),
            "BASE_RGBA_MID": rgba(base, 0.0),
            "BASE_RGBA_SOFT": rgba(base, 0.0),
            "SCRIM_STOP": 34,
        }

    values = dict(metrics)
    values.update(stops)
    values.update(
        {
            "LANG": spec.get("lang", "pt-BR"),
            "BG": bg_css,
            "BASE": base,
            "ACCENT": accent,
            "ACCENT_RGBA": rgba(accent, 0.35),
            "SCRIM_ANGLE": spec.get("scrim_angle", 100),
            "KICKER": spec.get("kick", ""),
            "HEADLINE": spec.get("headline", ""),
            "SUB": spec.get("sub", ""),
            "RESUMO": spec.get("resumo", ""),
            "TEMA_CLASS": " claro" if spec.get("tema") == "claro" else "",
            "STATS": build_stats_html(spec.get("stats"), scale),
            "FOOT": spec.get("foot", ""),
            "SIGNATURE": spec.get(
                "signature", "eolimabr.substack.com \u00b7 linkedin.com/in/limaeverton"
            ),
            "FONTS_DIR": FONTS_DIR,
            "MASCOT_CLASS": " com-mascote" if spec.get("mascot") else "",
            "MASCOT": (
                f"file://{os.path.abspath(spec['mascot'])}"
                if spec.get("mascot") else ""
            ),
        }
    )

    for key, value in values.items():
        html = html.replace("{{%s}}" % key, str(value))

    leftover = re.findall(r"\{\{(\w+)\}\}", html)
    if leftover:
        sys.exit(f"placeholders sem valor no template: {sorted(set(leftover))}")
    return html


def run_chrome(chrome, args):
    return subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--no-sandbox",
            "--force-device-scale-factor=1",
            "--virtual-time-budget=3000",
            *args,
        ],
        capture_output=True,
        text=True,
    )


def check_fit(chrome, html_path, metrics):
    """Lê o <title> que o template preenche e devolve a lista de problemas."""
    result = run_chrome(chrome, ["--dump-dom", f"file://{html_path}"])
    match = re.search(r"<title>(.*?)</title>", result.stdout, re.S)
    if not match:
        print("AVISO: sem relatório de encaixe no DOM (script não rodou?)", file=sys.stderr)
        return None
    raw = match.group(1).strip()
    if raw == "PENDING":
        print("AVISO: relatório ficou em PENDING; o load não disparou", file=sys.stderr)
        return None
    try:
        return json.loads(raw)
    except ValueError:
        print(f"AVISO: relatório ilegível: {raw[:200]}", file=sys.stderr)
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True, help="JSON com o conteúdo do banner")
    ap.add_argument("--html", help="onde gravar o HTML (default: ao lado do PNG)")
    ap.add_argument("--check", action="store_true", help="exit 1 se algo estourar")
    ap.add_argument("--dump-dom", action="store_true", help="imprime o DOM e sai")
    args = ap.parse_args()

    with open(args.spec) as fh:
        spec = json.load(fh)

    if not spec.get("out"):
        sys.exit("spec sem 'out'")
    if not spec.get("headline"):
        sys.exit("spec sem 'headline'")

    size = spec.get("size", "1080x1440")  # padrao retrato (3:4) desde 23/09
    match = SIZE_RE.match(size)
    if not match:
        sys.exit(f"size inválido: {size!r}; usar <largura>x<altura>")
    width, height = int(match.group(1)), int(match.group(2))

    html_path = args.html or spec.get("html") or os.path.splitext(spec["out"])[0] + ".html"
    html_path = os.path.abspath(html_path)
    html = render_html(spec, build_metrics(width, height, spec.get("layout") == "linkedin"))

    os.makedirs(os.path.dirname(html_path) or ".", exist_ok=True)
    with open(html_path, "w") as fh:
        fh.write(html)

    chrome = find_chrome()

    if args.dump_dom:
        print(run_chrome(chrome, ["--dump-dom", f"file://{html_path}"]).stdout)
        return

    out_path = os.path.abspath(spec["out"])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    result = run_chrome(
        chrome,
        [f"--window-size={width},{height}", f"--screenshot={out_path}", f"file://{html_path}"],
    )
    if result.returncode != 0 or not os.path.exists(out_path):
        sys.exit(f"render falhou: {result.stderr.strip()[:400]}")

    size_bytes = os.path.getsize(out_path)
    report = check_fit(chrome, html_path, (width, height))
    issues = (report or {}).get("issues") or []
    print(f"{out_path} {size_bytes} bytes {width}x{height} html={html_path}")
    if report is None:
        print("encaixe: não conferido")
    elif issues:
        for issue in issues:
            print(f"ENCAIXE: {issue['kind']} em .{issue['el']} {issue}")
        if args.check:
            sys.exit(1)
    else:
        print("encaixe: ok (nada fora do canvas, nada cortado)")


if __name__ == "__main__":
    main()

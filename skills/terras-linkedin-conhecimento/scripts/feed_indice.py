#!/usr/bin/env python3
"""Parte de máquina da análise do feed em lote (terras-linkedin-conhecimento).

Lê o JSON do feed_exportar.js, normaliza, deduplica (mesma URN e repost com mesmo
autor e texto), confere o mínimo de posts únicos e grava na pasta de saída:
INDICE-BRUTO.md (uma linha por post, sem julgamento), links.txt (links externos
únicos) e posts.json (normalizado, para a leitura do agente).

    python3 feed_indice.py feed-linkedin.json --saida PASTA [--minimo 100]

Saída: 0 = mínimo atingido; 1 = gravou, mas abaixo do mínimo (não sintetizar);
2 = entrada inválida (nada gravado). Classificar por tema é julgamento e não é daqui.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

LINKEDIN_INTERNO = re.compile(r"^https?://([a-z]+\.)?linkedin\.com/", re.I)
RASTREIO = re.compile(r"^(utm_|trk|trackingId|lipi|rcm)", re.I)
URN = re.compile(r"urn:li:[a-zA-Z]+:\d+")


class EntradaInvalida(ValueError):
    pass


def carregar(texto):
    try:
        dado = json.loads(texto)
    except json.JSONDecodeError as e:
        raise EntradaInvalida(f"JSON inválido: {e}") from e
    posts = dado if isinstance(dado, list) else (dado.get("posts") if isinstance(dado, dict) else None)
    if not isinstance(posts, list):
        raise EntradaInvalida("esperado um array de posts (ou {posts: [...]})")
    for i, p in enumerate(posts):
        if not isinstance(p, dict) or not (p.get("url") or p.get("urn")):
            raise EntradaInvalida(f"post {i} sem url nem urn")
    return posts


def limpar_url(href):
    try:
        u = urlsplit(href)
    except ValueError:
        return None
    if u.scheme not in ("http", "https") or not u.netloc:
        return None
    q = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not RASTREIO.match(k)]
    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), ""))


def tipo_link(href):
    host = urlsplit(href).netloc.lower().removeprefix("www.")
    if host == "github.com" or host.endswith(".github.io"):
        return "github"
    if re.search(r"(^|\.)youtube\.com$|^youtu\.be$|^vimeo\.com$", host):
        return "video"
    if host in ("lnkd.in", "bit.ly"):
        return "encurtado"
    if re.search(r"arxiv\.org$|zenodo\.org$|doi\.org$", host):
        return "paper"
    return "artigo"


def _str(v):
    return v.strip() if isinstance(v, str) else ""


def normalizar(p):
    urn = _str(p.get("urn")) or (URN.search(_str(p.get("url"))) or [None])[0] or _str(p.get("url"))
    url = _str(p.get("url")) or f"https://www.linkedin.com/feed/update/{urn}/"
    links = []
    for href in p.get("links") or []:
        limpo = limpar_url(href) if isinstance(href, str) else None
        if limpo and not LINKEDIN_INTERNO.match(limpo) and limpo not in links:
            links.append(limpo)
    texto = re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", _str(p.get("texto"))))
    return {
        "urn": urn,
        "url": url,
        "autor": _str(p.get("autor")).split("\n")[0],
        "quando": _str(p.get("quando")).split("\n")[0],
        "texto": texto,
        "promovido": p.get("promovido") is True,
        "temVideo": p.get("temVideo") is True,
        "links": links,
    }


def deduplicar(posts):
    vistos, saida = set(), []
    for p in posts:
        chaves = [p["urn"]] + ([f"{p['autor']}\0{p['texto']}"] if p["texto"] else [])
        if any(k in vistos for k in chaves):
            continue
        vistos.update(chaves)
        saida.append(p)
    return saida, len(posts) - len(saida)


def resumir(posts, minimo):
    links = list(dict.fromkeys(l for p in posts for l in p["links"]))
    por_tipo = {}
    for l in links:
        t = tipo_link(l)
        por_tipo[t] = por_tipo.get(t, 0) + 1
    return {
        "total": len(posts),
        "minimo": minimo,
        "minimoAtingido": len(posts) >= minimo,
        "promovidos": sum(p["promovido"] for p in posts),
        "comVideo": sum(p["temVideo"] for p in posts),
        "semTexto": sum(not p["texto"] for p in posts),
        "links": links,
        "linksPorTipo": por_tipo,
    }


def _celula(s, maximo):
    plano = re.sub(r"\s+", " ", s).strip()
    curto = plano if len(plano) <= maximo else plano[: maximo - 1] + "…"
    return curto.replace("|", "\\|")


def indice_bruto(posts, fonte, data, minimo, removidos):
    r = resumir(posts, minimo)
    estado = (f"mínimo de {minimo} atingido" if r["minimoAtingido"]
              else f"**abaixo do mínimo de {minimo}**: exportar de novo com alvo maior antes de sintetizar")
    tipos = ", ".join(f"{t} {n}" for t, n in r["linksPorTipo"].items()) or "nenhum"
    linhas = [
        f"# Feed do LinkedIn: índice bruto ({data})",
        "",
        f"> Gerado por `feed_indice.py` a partir de `{fonte}`. Parte de máquina, sem tema nem julgamento:",
        "> a classificação mora em `INDICE.md` e a leitura em `SINTESE.md`.",
        "",
        f"- {r['total']} posts únicos ({removidos} duplicados removidos): {estado}.",
        f"- Promovidos: {r['promovidos']}. Com vídeo: {r['comVideo']}. Sem texto capturado: {r['semTexto']}.",
        f"- Links externos únicos: {len(r['links'])} ({tipos}).",
        "",
        "| # | Autor | Quando | Trecho | Vídeo | Links |",
        "|---|---|---|---|---|---|",
    ]
    for i, p in enumerate(posts, 1):
        linhas.append(
            f"| {i} | [{_celula(p['autor'] or '?', 40)}]({p['url']}) | {_celula(p['quando'], 20)} | "
            f"{_celula(p['texto'] or '(sem texto)', 140)} | {'sim' if p['temVideo'] else ''} | {len(p['links']) or ''} |"
        )
    return "\n".join(linhas) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arquivo")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--minimo", type=int, default=100)
    a = ap.parse_args(argv)
    if a.minimo < 1:
        print("--minimo precisa ser >= 1", file=sys.stderr)
        return 2
    try:
        brutos = carregar(Path(a.arquivo).read_text(encoding="utf-8"))
    except (OSError, EntradaInvalida) as e:
        print(f"entrada inválida ({a.arquivo}): {e}", file=sys.stderr)
        return 2
    posts, removidos = deduplicar([normalizar(p) for p in brutos])
    r = resumir(posts, a.minimo)
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "INDICE-BRUTO.md").write_text(
        indice_bruto(posts, Path(a.arquivo).name, date.today().isoformat(), a.minimo, removidos), encoding="utf-8")
    (saida / "links.txt").write_text("".join(l + "\n" for l in r["links"]), encoding="utf-8")
    (saida / "posts.json").write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    resumo = {k: v for k, v in r.items() if k != "links"}
    print(json.dumps({**resumo, "links": len(r["links"]), "removidos": removidos, "pasta": str(saida)},
                     ensure_ascii=False, indent=2))
    return 0 if r["minimoAtingido"] else 1


if __name__ == "__main__":
    sys.exit(main())

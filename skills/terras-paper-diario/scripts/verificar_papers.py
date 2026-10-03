#!/usr/bin/env python3
"""Verificação de papers e sinais relevantes para quem desenvolve, em várias fontes.

Fontes:
  arxiv      arXiv, busca avançada do site (a API export.arxiv.org trava nesta rede)
  s2         Semantic Scholar — cobre ACM, IEEE, Springer, arXiv etc.
  openalex   OpenAlex — cobertura cruzada de periódicos e conferências
  hn         Hacker News — sinal da comunidade (descoberta, não fonte primária)
  openreview OpenReview — submissões sob revisão (sinal precoce)

Requisições vão via curl -4 (IPv6 não sai nesta máquina), com backoff para
rate limit. Uso:
    verificar_papers.py [--janela N] [--limite N] [--fontes lista] [--formato md|json]
    verificar_papers.py --marcar ID[,ID...]
    verificar_papers.py --vistos
    verificar_papers.py --limpar
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

ESTADO_DIR = Path.home() / ".config" / "terras-paper-diario"
ESTADO_ARQ = ESTADO_DIR / "vistos.json"
FONTES_TODAS = ["arxiv", "s2", "openalex", "hn", "openreview"]
MES = {m: i for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"], 1)}

# arXiv: OR de no máximo 3 frases por requisição (limite prático do servidor).
GRUPOS_ARXIV = [
    '"coding agent" OR "AI agent" OR "LLM agent"',
    '"code review" OR "pull request" OR "vibe coding"',
    '"developer productivity" OR "software developer" OR "software engineer"',
    '"employment" OR "layoff" OR "labor market"',
]
# Semantic Scholar: buscas por relevância, filtro de data no cliente.
QUERIES_S2 = [
    '"coding agent" OR "AI agent" OR "code review"',
    '"software developer" OR "developer productivity" OR "vibe coding"',
    'software developer employment AI layoff "labor market"',
]
QUERY_OPENALEX = ('coding agent OR "AI agent" OR "code review" OR "pull request" '
                  'OR "developer productivity" OR "vibe coding" OR '
                  '"software developer" OR "software engineer" OR layoff OR '
                  '"labor market"')
QUERY_HN = '"coding agent" OR "vibe coding" OR "AI agent" OR "AI coding"'
QUERIES_OPENREVIEW = ["coding agent", "AI code review"]

CATEGORIAS_ARXIV_OK = {"cs.SE", "cs.CY", "cs.AI", "cs.HC", "cs.PL"}

# Palavras que provam que o material é sobre o trabalho de quem desenvolve.
# Núcleo vale 2, secundária vale 1; entra quem somar >= 3.
PALAVRAS_NUCLEO = [
    "coding agent", "code review", "pull request", "developer productivity",
    "developer experience", "software developer", "software engineer",
    "programmer", "software development", "program repair", "code generation",
    "technical debt", "code quality", "vibe coding", "employment", "labor market",
    "layoff", "hiring", "job displacement", "workforce", "burnout", "career",
]
PALAVRAS_SECUNDARIA = [
    "llm", "ai agent", "ai-generated", "autonomous agent", "gpt", "claude",
    "copilot", "devin", "cursor", "job", "labor", "skill", "empirical study",
    "mining", "github",
]


# ---------------------------------------------------------------- estado

def carregar_vistos():
    if ESTADO_ARQ.exists():
        return json.loads(ESTADO_ARQ.read_text(encoding="utf-8"))
    return {}


def salvar_vistos(vistos):
    ESTADO_DIR.mkdir(parents=True, exist_ok=True)
    ESTADO_ARQ.write_text(
        json.dumps(vistos, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    os.chmod(ESTADO_ARQ, 0o600)


def titulo_normalizado(titulo):
    return re.sub(r"[^a-z0-9]+", " ", (titulo or "").lower()).strip()


# ---------------------------------------------------------------- http

def curl(url):
    # Rate limit: volta com backoff crescente. -4 é obrigatório nesta rede.
    for espera in (0, 30, 60, 120):
        if espera:
            time.sleep(espera)
        r = subprocess.run(
            ["curl", "-4", "-sS", "--max-time", "45", "-A",
             "terras-paper-diario/1.0 (script local de verificacao diaria)", url],
            capture_output=True, text=True,
        )
        corpo = r.stdout
        if r.returncode == 0 and corpo.strip() and "Rate exceeded" not in corpo[:100]:
            return corpo
    raise RuntimeError("fonte indisponível após 4 tentativas (rate limit ou rede)")


def curl_json(url):
    return json.loads(curl(url))


def limpar_texto(bruto):
    texto = re.sub(r"<[^>]+>", "", bruto or "")
    return re.sub(r"\s+", " ", html.unescape(texto)).strip()


def normalizar_data(texto):
    # "1 October, 2026" -> "2026-10-01"
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})", (texto or "").strip())
    if not m or m.group(2) not in MES:
        return ""
    return f"{m.group(3)}-{MES[m.group(2)]:02d}-{int(m.group(1)):02d}"


# ---------------------------------------------------------------- arXiv

def url_arxiv(grupo, de, ate):
    return (
        "https://arxiv.org/search/advanced?advanced=1"
        f"&terms-0-term={quote(grupo, safe='')}&terms-0-field=abstract"
        "&classification-computer_science=y&computer_science_archives=all"
        f"&date-filter_by=date_range&date-from_date={de}&date-to_date={ate}"
        "&date-date_type=submitted_date&abstracts=show"
        "&order=-announced_date_first&size=100"
    )


def parse_arxiv(bruto):
    papers = []
    for bloco in bruto.split('<li class="arxiv-result">')[1:]:
        m = re.search(r'href="https://arxiv.org/abs/([0-9]+\.[0-9]+)(?:v\d+)?"', bloco)
        if not m:
            continue
        mt = re.search(r'class="title is-5 mathjax">\s*(.*?)</p>', bloco, re.S)
        ma = re.search(r'class="authors">\s*(.*?)</p>', bloco, re.S)
        mab = re.search(
            r'class="abstract-full[^"]*"[^>]*>(.*?)(?:<a class="is-size-7"|</div>)',
            bloco, re.S)
        msub = re.search(r'Submitted</span>\s*([^<;]+?)\s*;', bloco, re.S)
        resumo = limpar_texto(mab.group(1) if mab else "")
        resumo = re.sub(r"^Abstract:", "", resumo).strip()
        autores = re.sub(r"^Authors:", "",
                         limpar_texto(ma.group(1) if ma else "")).strip()
        papers.append({
            "id": f"arxiv:{m.group(1)}",
            "titulo": limpar_texto(mt.group(1) if mt else ""),
            "resumo": resumo,
            "publicado": normalizar_data(msub.group(1) if msub else ""),
            "autores": [a.strip(" ,") for a in autores.split(",") if a.strip(" ,")],
            "categorias": [c.strip() for c in re.findall(
                r'class="tag is-small[^"]*"[^>]*>([^<]+)</span>', bloco)],
            "fonte": "arxiv",
            "link": f"https://arxiv.org/abs/{m.group(1)}",
        })
    return papers


def buscar_arxiv(de, ate, pausa):
    papers = {}
    for i, grupo in enumerate(GRUPOS_ARXIV):
        if i:
            time.sleep(pausa)
        bruto = curl(url_arxiv(grupo, de, ate))
        if '<li class="arxiv-result">' not in bruto:
            print("aviso: arXiv: grupo de busca voltou vazio (query recusada "
                  "ou rate limit); seguindo", file=sys.stderr)
            continue
        for p in parse_arxiv(bruto):
            papers.setdefault(p["id"], p)
    return list(papers.values())


# ---------------------------------------------------------------- Semantic Scholar

def buscar_s2(de, ate, pausa):
    papers = {}
    campos = ("title,abstract,publicationDate,externalIds,openAccessPdf,"
              "url,authors")
    for i, q in enumerate(QUERIES_S2):
        if i:
            time.sleep(pausa)
        url = (f"https://api.semanticscholar.org/graph/v1/paper/search?"
               f"query={quote(q)}&fields={campos}&limit=100"
               f"&publicationDateOrYear={de}:{ate}")
        try:
            dados = curl_json(url)
        except (RuntimeError, json.JSONDecodeError) as exc:
            print(f"aviso: Semantic Scholar falhou ({exc}); seguindo",
                  file=sys.stderr)
            continue
        for w in dados.get("data", []):
            pid = w.get("paperId")
            if not pid or not w.get("title"):
                continue
            ext = w.get("externalIds") or {}
            link = ((w.get("openAccessPdf") or {}).get("url")
                    or (f"https://arxiv.org/abs/{ext['ArXiv']}"
                        if ext.get("ArXiv") else w.get("url") or ""))
            papers[f"s2:{pid}"] = {
                "id": f"s2:{pid}",
                "titulo": limpar_texto(w["title"]),
                "resumo": limpar_texto(w.get("abstract") or ""),
                "publicado": (w.get("publicationDate") or "")[:10],
                "autores": [a.get("name", "") for a in w.get("authors", [])][:8],
                "categorias": [],
                "fonte": "s2",
                "link": link,
            }
    return list(papers.values())


# ---------------------------------------------------------------- OpenAlex

def abstract_openalex(inv):
    if not inv:
        return ""
    pos = {}
    for palavra, idxs in inv.items():
        for i in idxs:
            pos[i] = palavra
    return " ".join(pos[i] for i in sorted(pos))


def buscar_openalex(de, ate, pausa):
    url = ("https://api.openalex.org/works?mailto=curadoria-papers@local"
           f"&search={quote(QUERY_OPENALEX)}"
           f"&filter=title_and_abstract.search:{quote(QUERY_OPENALEX, safe='')},"
           f"from_publication_date:{de},to_publication_date:{ate}"
           "&sort=publication_date:desc&per-page=100"
           "&select=id,doi,title,publication_date,authorships,"
           "abstract_inverted_index,primary_location")
    try:
        dados = curl_json(url)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"aviso: OpenAlex falhou ({exc}); seguindo", file=sys.stderr)
        return []
    papers = []
    for w in dados.get("results", []):
        wid = (w.get("id") or "").rsplit("/", 1)[-1]
        if not wid or not w.get("title"):
            continue
        loc = (w.get("primary_location") or {}).get("landing_page_url") or ""
        link = w.get("doi") or loc or f"https://openalex.org/{wid}"
        papers.append({
            "id": f"openalex:{wid}",
            "titulo": limpar_texto(w["title"]),
            "resumo": abstract_openalex(w.get("abstract_inverted_index"))[:2000],
            "publicado": (w.get("publication_date") or "")[:10],
            "autores": [a.get("author", {}).get("display_name", "")
                        for a in w.get("authorships", [])][:8],
            "categorias": [],
            "fonte": "openalex",
            "link": link,
        })
    return papers


# ---------------------------------------------------------------- Hacker News

def buscar_hn(de_iso, pausa):
    desde = int(datetime.fromisoformat(de_iso + "T00:00:00+00:00").timestamp())
    url = (f"https://hn.algolia.com/api/v1/search_by_date?query="
           f"{quote(QUERY_HN)}&tags=story&hitsPerPage=50"
           f"&numericFilters={quote(f'created_at_i>{desde}', safe='')}")
    try:
        dados = curl_json(url)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"aviso: Hacker News falhou ({exc}); seguindo", file=sys.stderr)
        return []
    sinais = []
    for h in dados.get("hits", []):
        titulo = h.get("title") or ""
        if not titulo:
            continue
        oid = h.get("objectID", "")
        sinais.append({
            "id": f"hn:{oid}",
            "titulo": limpar_texto(titulo),
            "resumo": (f"post no Hacker News: {h.get('points', 0)} pontos, "
                       f"{h.get('num_comments', 0)} comentários — sinal da "
                       "comunidade, não fonte primária; confirme no link."),
            "publicado": (h.get("created_at") or "")[:10],
            "autores": [h.get("author", "")] if h.get("author") else [],
            "categorias": [],
            "fonte": "hn",
            "link": h.get("url") or f"https://news.ycombinator.com/item?id={oid}",
        })
    return sinais


# ---------------------------------------------------------------- OpenReview

def buscar_openreview(de, pausa):
    limite_ms = int(datetime.fromisoformat(
        de + "T00:00:00+00:00").timestamp() * 1000)
    papers = {}
    for i, termo in enumerate(QUERIES_OPENREVIEW):
        if i:
            time.sleep(pausa)
        url = (f"https://api2.openreview.net/notes/search?term={quote(termo)}"
               "&limit=100&content=all&group=all&source=all")
        try:
            dados = curl_json(url)
        except (RuntimeError, json.JSONDecodeError) as exc:
            print(f"aviso: OpenReview falhou ({exc}); seguindo", file=sys.stderr)
            continue
        for n in dados.get("notes", []):
            nid = n.get("id", "")
            cdate = n.get("cdate") or n.get("tcdate") or 0
            if not nid or cdate < limite_ms:
                continue
            c = n.get("content") or {}
            titulo = limpar_texto((c.get("title") or {}).get("value", ""))
            if not titulo:
                continue
            papers[f"or:{nid}"] = {
                "id": f"or:{nid}",
                "titulo": titulo,
                "resumo": limpar_texto((c.get("abstract") or {}).get("value", ""))[:2000],
                "publicado": datetime.fromtimestamp(
                    cdate / 1000, tz=timezone.utc).date().isoformat(),
                "autores": (c.get("authors") or {}).get("value", [])[:8],
                "categorias": [(c.get("venue") or {}).get("value", "sob revisão")],
                "fonte": "openreview",
                "link": f"https://openreview.net/forum?id={nid}",
            }
    return list(papers.values())


# ---------------------------------------------------------------- pontuação

def pontuar(paper):
    texto = (paper["titulo"] + " " + paper["resumo"]).lower()
    titulo = paper["titulo"].lower()
    pontos, palavras = 0, []
    for p in PALAVRAS_NUCLEO:
        if p in texto:
            pontos += 3 if p in titulo else 2
            palavras.append(p)
    for p in PALAVRAS_SECUNDARIA:
        if p in texto:
            pontos += 1
            palavras.append(p)
    return pontos, sorted(set(palavras))


def verificar(janela_dias, limite, fontes, pausa_arxiv, pausa):
    hoje = datetime.now(timezone.utc).date()
    de = (hoje - timedelta(days=janela_dias)).isoformat()
    ate = hoje.isoformat()
    vistos = carregar_vistos()

    brutos = []
    if "arxiv" in fontes:
        brutos += buscar_arxiv(de, ate, pausa_arxiv)
    if "s2" in fontes:
        brutos += buscar_s2(de, ate, pausa)
    if "openalex" in fontes:
        brutos += buscar_openalex(de, ate, pausa)
    if "openreview" in fontes:
        brutos += buscar_openreview(de, pausa)
    if "hn" in fontes:
        brutos += buscar_hn(de, pausa)

    # dedupe: mesmo id já visto OU mesmo título já apareceu nesta rodada
    candidatos, titulos_vistos = {}, set()
    for paper in brutos:
        chave_t = titulo_normalizado(paper["titulo"])
        if paper["id"] in vistos or f"t:{chave_t}" in vistos:
            continue
        if chave_t in titulos_vistos:
            continue
        titulos_vistos.add(chave_t)
        if paper["publicado"] and paper["publicado"] < de:
            continue
        if (paper["fonte"] == "arxiv"
                and not any(c in CATEGORIAS_ARXIV_OK for c in paper["categorias"])):
            continue
        if paper["fonte"] == "hn":
            pontos, palavras = pontuar(paper)
            if pontos >= 3:
                paper["score"], paper["palavras"] = pontos, palavras
                candidatos[paper["id"]] = paper
            continue
        pontos, palavras = pontuar(paper)
        if pontos < 3:
            continue
        paper["score"], paper["palavras"] = pontos, palavras
        candidatos[paper["id"]] = paper

    papers = [p for p in candidatos.values() if p["fonte"] != "hn"]
    sinais = [p for p in candidatos.values() if p["fonte"] == "hn"]
    papers.sort(key=lambda p: (p["score"], p["publicado"]), reverse=True)
    sinais.sort(key=lambda p: p["publicado"], reverse=True)
    return papers[:limite], sinais[:8]


def formatar(novos, sinais):
    if not novos and not sinais:
        return "Nenhum paper ou sinal novo relevante nas fontes consultadas."
    blocos = []
    for i, p in enumerate(novos, 1):
        aut = ", ".join(p["autores"][:4]) + (" et al." if len(p["autores"]) > 4 else "")
        blocos.append(
            f"### {i}. [{p['score']}] {p['titulo']}\n"
            f"- ID: {p['id']} · fonte: {p['fonte']} · "
            f"{', '.join(p['categorias'][:3])} · publicado em {p['publicado'] or '?'}\n"
            f"- Link: {p['link']}\n"
            f"- Autores: {aut}\n"
            f"- Por que entrou: {', '.join(p['palavras'])}\n"
            f"- Resumo: {p['resumo'] or '(sem resumo na fonte)'}\n"
        )
    if sinais:
        blocos.append("## Sinais da comunidade (Hacker News — descoberta, não fonte)")
        for s in sinais:
            blocos.append(f"- {s['publicado']} · {s['titulo']} — {s['resumo']}\n  {s['link']}")
    return "\n".join(blocos)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--janela", type=int, default=3,
                    help="dias para trás (padrão 3)")
    ap.add_argument("--limite", type=int, default=2,
                    help="máximo de papers no relatório (padrão 2)")
    ap.add_argument("--fontes", default=",".join(FONTES_TODAS),
                    help=f"fontes consultadas (padrão: {','.join(FONTES_TODAS)})")
    ap.add_argument("--pausa-arxiv", type=int, default=45,
                    help="segundos entre grupos do arXiv (padrão 45)")
    ap.add_argument("--pausa", type=int, default=5,
                    help="segundos entre requisições das demais fontes (padrão 5)")
    ap.add_argument("--formato", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--marcar", metavar="ID[,ID...]",
                    help="marca IDs como já analisados")
    ap.add_argument("--marcar-titulo", metavar="TITULO", action="append",
                    help="marca também um título (dedupe entre fontes; "
                         "repetível)")
    ap.add_argument("--vistos", action="store_true", help="lista os já vistos")
    ap.add_argument("--limpar", action="store_true", help="zera o estado")
    args = ap.parse_args()

    if args.limpar:
        salvar_vistos({})
        print("Estado zerado.")
        return
    if args.vistos:
        vistos = carregar_vistos()
        for ident, data in sorted(vistos.items(), key=lambda x: x[1], reverse=True):
            print(f"{ident}  marcado em {data}")
        if not vistos:
            print("(nenhum paper marcado como visto ainda)")
        return
    if args.marcar or args.marcar_titulo:
        vistos = carregar_vistos()
        hoje = datetime.now(timezone.utc).date().isoformat()
        for ident in [x.strip() for x in (args.marcar or "").split(",") if x.strip()]:
            vistos[ident] = hoje
        for titulo in (args.marcar_titulo or []):
            chave = titulo_normalizado(titulo)
            if chave:
                vistos[f"t:{chave}"] = hoje
        salvar_vistos(vistos)
        print(f"Estado com {len(vistos)} entradas.")
        return

    fontes = [f.strip() for f in args.fontes.split(",") if f.strip()]
    desconhecidas = [f for f in fontes if f not in FONTES_TODAS]
    if desconhecidas:
        sys.exit(f"erro: fontes desconhecidas: {', '.join(desconhecidas)} "
                 f"(válidas: {', '.join(FONTES_TODAS)})")

    try:
        novos, sinais = verificar(args.janela, args.limite, fontes,
                                  args.pausa_arxiv, args.pausa)
    except RuntimeError as exc:
        sys.exit(f"erro: {exc}")

    if args.formato == "json":
        print(json.dumps({"papers": novos, "sinais_hn": sinais},
                         ensure_ascii=False, indent=2))
    else:
        print(formatar(novos, sinais))


if __name__ == "__main__":
    main()

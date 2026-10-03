#!/usr/bin/env python3
"""terrasia-pauta-youtube: pesquisa de envelope (demanda) no YouTube.

Mede a demanda de uma consulta pelos resultados da busca do YouTube (views
de cada vídeo contra a mediana do canal que publicou) e colhe frases
recorrentes dos títulos de melhor desempenho. Quem inventa os candidatos
de consulta (o "passo atrás") é o agente; quem mede é este motor.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

HOME_DIR = Path(os.environ.get("TERRAS_PAUTA_HOME",
                               Path.home() / ".config/terrasia-pauta-youtube"))
YTDLP = HOME_DIR / "venv/bin/yt-dlp"
CACHE_FILE = HOME_DIR / "cache-canais.json"
CACHE_TTL_S = 14 * 24 * 3600
N_GRAMAS = (2, 3, 4)
TOKEN = re.compile(r"[0-9a-zà-ÿ]+")


def falhar(msg: str) -> None:
    print(f"erro: {msg}", file=sys.stderr)
    sys.exit(1)


def fmt_views(v: int) -> str:
    return f"{int(v):,}".replace(",", ".")


def ytdlp_json(args: list[str], timeout: int = 120) -> dict:
    if not YTDLP.exists():
        falhar(f"yt-dlp ausente em {YTDLP}: rode `bash scripts/setup.sh`")
    proc = subprocess.run([str(YTDLP), *args, "--no-warnings"],
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        falhar(f"yt-dlp falhou: {proc.stderr.strip()[-400:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        falhar("saida do yt-dlp nao e JSON (resultados bloqueados ou consulta vazia?)")


def buscar(consulta: str, n: int) -> list[dict]:
    info = ytdlp_json(["-J", "--flat-playlist", f"ytsearch{n}:{consulta}"])
    entradas = []
    for e in info.get("entries") or []:
        if not e or e.get("view_count") is None:
            continue
        entradas.append({
            "id": e.get("id") or "",
            "titulo": e.get("title") or "",
            "canal": e.get("channel") or e.get("uploader") or "",
            "canal_id": e.get("channel_id") or "",
            "views": int(e["view_count"]),
            "url": e.get("url") or (f"https://youtu.be/{e.get('id')}" if e.get("id") else ""),
        })
    return entradas


_cache: dict | None = None


def cache() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    return _cache


def salvar_cache() -> None:
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache(), ensure_ascii=False, indent=1),
                          encoding="utf-8")


def mediana_canal(canal_id: str) -> dict:
    registro = cache().get(canal_id)
    agora = time.time()
    if registro and agora - registro["buscado_em"] < CACHE_TTL_S:
        return registro
    info = ytdlp_json(["-J", "--flat-playlist", "--playlist-end", "20",
                       f"https://www.youtube.com/channel/{canal_id}/videos"], timeout=90)
    views = [e["view_count"] for e in info.get("entries") or []
             if e and e.get("view_count") is not None]
    registro = {
        "mediana": int(statistics.median(views)) if views else None,
        "n_amostra": len(views),
        "inscritos": info.get("channel_follower_count"),
        "buscado_em": agora,
    }
    cache()[canal_id] = registro
    return registro


def pontuar(entradas: list[dict], limite_canais: int = 8) -> list[dict]:
    """Enriquece as entradas com mediana do canal e score de outlier.

    Busca a mediana só dos primeiros canais distintos do resultado (o custo
    e uma requisicao por canal), o suficiente para calibrar os lideres.
    """
    vistos: set[str] = set()
    ordem = []
    for e in entradas:
        if e["canal_id"] and e["canal_id"] not in vistos:
            vistos.add(e["canal_id"])
            ordem.append(e)
        if len(ordem) >= limite_canais:
            break
    for e in ordem:
        info = mediana_canal(e["canal_id"])
        e["canal_mediana"] = info["mediana"]
        e["inscritos"] = info["inscritos"]
        e["outlier"] = (round(e["views"] / info["mediana"], 1)
                        if info["mediana"] else None)
    salvar_cache()
    return entradas


def classe(outlier) -> str:
    if outlier is None:
        return "?"
    if outlier >= 5:
        return "outlier forte"
    if outlier >= 2:
        return "acima da media"
    return "na media"


def cmd_pesquisa(a: argparse.Namespace) -> None:
    entradas = pontuar(buscar(a.consulta, a.n))
    if not entradas:
        falhar("nenhum resultado com views")
    entradas.sort(key=lambda e: e["views"], reverse=True)
    if a.json:
        print(json.dumps(entradas, ensure_ascii=False, indent=1))
        return
    print(f"consulta: {a.consulta}")
    print(f"{'views':>9}  {'outlier':>12}  {'canal':24}  titulo")
    for e in entradas:
        out = f"{e['outlier']}x" if e.get("outlier") else "?"
        print(f"{fmt_views(e['views']):>9}  {classe(e.get('outlier')) + ' ' + out:>12}  "
              f"{e['canal'][:24]:24}  {e['titulo'][:56]}")


def cmd_comparar(a: argparse.Namespace) -> None:
    relatorios = []
    for q in a.consultas:
        entradas = pontuar(buscar(q, a.n))
        views = sorted(e["views"] for e in entradas)
        if not views:
            relatorios.append({"consulta": q, "resultados": 0})
            continue
        relatorios.append({
            "consulta": q,
            "resultados": len(views),
            "mediana_views": statistics.median(views),
            "max_views": views[-1],
            "melhor": max(entradas, key=lambda e: e["views"]),
        })
    relatorios.sort(key=lambda r: r.get("mediana_views") or 0, reverse=True)
    if a.json:
        print(json.dumps(relatorios, ensure_ascii=False, indent=1))
        return
    print("demanda mediana dos resultados (maior = envelope com mais procura):")
    for r in relatorios:
        if not r.get("resultados"):
            print(f"  {r['consulta']}: sem resultados")
            continue
        print(f"  {fmt_views(r['mediana_views']):>9} mediana | max {fmt_views(r['max_views']):>9} | {r['consulta']}")
        m = r["melhor"]
        out = f"{m.get('outlier')}x" if m.get("outlier") else "?"
        print(f"            melhor: {out:>6} vs canal | {m['titulo'][:60]}")


def ngramas(titulo: str) -> set[str]:
    toks = TOKEN.findall(titulo.lower())
    saida = set()
    for n in N_GRAMAS:
        for i in range(len(toks) - n + 1):
            saida.add(" ".join(toks[i:i + n]))
    return saida


def cmd_frases(a: argparse.Namespace) -> None:
    por_id: dict[str, dict] = {}
    for q in a.consultas:
        for e in buscar(q, a.n):
            if e["views"] > 0:
                por_id[e["id"]] = e
    if not por_id:
        falhar("nenhum resultado com views")
    ranqueados = sorted(por_id.values(), key=lambda e: e["views"], reverse=True)[:40]
    contagem: dict[str, dict] = {}
    for e in ranqueados:
        for g in ngramas(e["titulo"]):
            c = contagem.setdefault(g, {"df": 0, "views": 0})
            c["df"] += 1
            c["views"] += e["views"]
    candidatas = {g: c for g, c in contagem.items() if c["df"] >= 2}
    finais: dict[str, dict] = {}
    for g in sorted(candidatas, key=len, reverse=True):
        c = candidatas[g]
        sobrando = any(
            g != h and f" {g} " in f" {h} " and finais[h]["df"] == c["df"]
            for h in finais
        )
        if not sobrando:
            finais[g] = c
    topo = sorted(finais.items(),
                  key=lambda kv: (kv[1]["df"], kv[1]["views"]),
                  reverse=True)[:a.top]
    print(f"titulos lidos: {len(ranqueados)} (melhores por views, deduplicados)")
    print(f"{'freq':>4}  {'views somadas':>13}  frase")
    for g, c in topo:
        print(f"{c['df']:>4}x  {fmt_views(c['views']):>13}  {g}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pesquisa de envelope (demanda) no YouTube via yt-dlp.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("pesquisa", help="mede uma consulta: views e outlier por video")
    p.add_argument("consulta")
    p.set_defaults(fn=cmd_pesquisa)

    p = sub.add_parser("comparar", help="ranqueia varias consultas pela mediana de views")
    p.add_argument("consultas", nargs="+")
    p.set_defaults(fn=cmd_comparar)

    p = sub.add_parser("frases", help="colhe frases recorrentes dos melhores titulos")
    p.add_argument("consultas", nargs="+")
    p.add_argument("--top", type=int, default=15)
    p.set_defaults(fn=cmd_frases)

    for pr in [sub.choices["pesquisa"], sub.choices["comparar"], sub.choices["frases"]]:
        pr.add_argument("--n", type=int, default=12, help="resultados por consulta")
        pr.add_argument("--json", action="store_true", help="saida em JSON")

    a = parser.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

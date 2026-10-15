#!/usr/bin/env python3
"""Baixa em lote os vídeos de posts do LinkedIn e guarda o texto do post ao lado.

Só stdlib. O download de cada URL é do motor da terras-video-downloader (baixar.py);
este script só cuida de lote, pasta por data, duplicata e do .md com o texto do post.

Uso:
  baixar_lote.py URL [URL ...] [--base PASTA] [--data AAAA-MM-DD] [--qualidade melhor|menor]
  baixar_lote.py --arquivo urls.txt

Grava em BASE/DATA/linkedin-<autor>-<id6>-<altura>p.mp4 e o .md de mesmo nome.
Pula post cujo id já tenha mp4 em qualquer data sob BASE.
Saída 0 = todos ok ou já baixados. Saída 1 = algum falhou (o JSON diz qual e por quê).
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.realpath(__file__))
MOTOR = os.path.join(AQUI, "..", "..", "terras-video-downloader", "scripts", "baixar.py")
BASE_PADRAO = os.path.expanduser("~/linkedin/assets/videos")


def id_do_post(url):
    m = re.search(r"(?:activity|ugcPost|share)[:-](\d{15,})", url)
    return m and m.group(1)


def ja_baixado(base, pid):
    if not pid:
        return None
    achados = glob.glob(os.path.join(base, "**", f"*-{pid[-6:]}-*p.mp4"), recursive=True)
    return achados[0] if achados else None


def gravar_md(rel):
    md = os.path.splitext(rel["arquivo"])[0] + ".md"
    linhas = [f"# {os.path.basename(rel['arquivo'])}", "",
              f"- Post: {rel.get('url_final') or rel['url']}",
              f"- Baixado em: {dt.datetime.now():%Y-%m-%d %H:%M}",
              f"- Resolução: {rel.get('escolhido')}",
              f"- Tamanho: {rel['bytes'] / 1e6:.1f} MB", "",
              "O vídeo é do autor: repostar pede crédito ou autorização.", "",
              "## Texto do post", "", rel.get("texto_post") or "(a página pública não trouxe o texto)", ""]
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    return md


def baixar_um(url, pasta, base, qualidade):
    feito = ja_baixado(base, id_do_post(url))
    if feito:
        return {"url": url, "status": "ja_baixado", "arquivo": feito}
    r = subprocess.run([sys.executable, MOTOR, url, "-o", pasta, "--qualidade", qualidade, "--json"],
                       capture_output=True, text=True, timeout=600)
    try:
        rel = json.loads(r.stdout, strict=False)  # texto do post pode trazer caractere de controle
    except ValueError:
        return {"url": url, "status": "falha", "kind": "motor", "erro": (r.stderr or r.stdout)[-400:]}
    if rel.get("kind") == "existe":  # lnkd.in: o id só aparece depois de resolver, e o motor não sobrescreve
        return {"url": url, "status": "ja_baixado", "arquivo": rel["erro"].split(" já existe")[0]}
    if rel.get("status") == "ok":
        feito = ja_baixado(base, id_do_post(rel.get("url_final", "")))
        if feito and feito != rel["arquivo"]:  # lnkd.in só revela o id depois de resolvido
            os.remove(rel["arquivo"])
            return {"url": url, "status": "ja_baixado", "arquivo": feito}
        rel["md"] = gravar_md(rel)
    return {k: rel.get(k) for k in ("url", "status", "kind", "erro", "arquivo", "md", "bytes", "texto_post") if rel.get(k) is not None}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--arquivo", help="um URL por linha")
    ap.add_argument("--base", default=BASE_PADRAO)
    ap.add_argument("--data", default=f"{dt.date.today():%Y-%m-%d}")
    ap.add_argument("--qualidade", choices=["melhor", "menor"], default="melhor")
    a = ap.parse_args()

    urls = list(a.urls)
    if a.arquivo:
        urls += [l.strip() for l in open(a.arquivo, encoding="utf-8") if l.strip() and not l.startswith("#")]
    urls = list(dict.fromkeys(urls))
    if not urls:
        ap.error("nenhuma URL")
    if not os.path.exists(MOTOR):
        print(json.dumps({"status": "falha", "kind": "motor_ausente", "erro": MOTOR}), file=sys.stderr)
        return 3

    pasta = os.path.join(a.base, a.data)
    os.makedirs(pasta, exist_ok=True)
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda u: baixar_um(u, pasta, a.base, a.qualidade), urls))
    for r in res:
        if r.get("texto_post"):
            r["texto_post"] = r["texto_post"][:160]
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 1 if any(r["status"] == "falha" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())

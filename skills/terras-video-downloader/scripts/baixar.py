#!/usr/bin/env python3
"""Baixa o vídeo de uma URL escolhendo o meio pela plataforma.

Só stdlib. Rotas:
  linkedin  -> lê o MP4 público da página do post (dms.licdn.com), sem login
  qualquer  -> yt-dlp, se estiver instalado

Uso:
  baixar.py URL [-o PASTA] [--listar] [--qualidade melhor|menor] [--json]

Saída 0 = arquivo gravado e conferido. Saída 2 = não achou vídeo público.
Saída 3 = rota precisa de ferramenta ausente. Saída 1 = erro de rede/arquivo.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")


class Falha(Exception):
    def __init__(self, kind, msg, codigo=1):
        super().__init__(msg)
        self.kind, self.codigo = kind, codigo


def abrir(url, metodo="GET"):
    req = urllib.request.Request(url, method=metodo, headers={
        "User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    return urllib.request.urlopen(req, timeout=30)


def resolver(url):
    """Segue encurtador (lnkd.in, bit.ly...) até a URL final."""
    try:
        with abrir(url) as r:
            return r.geturl(), r.read().decode("utf-8", "replace")
    except Exception as e:
        raise Falha("rede", f"não abriu {url}: {e}")


def slug(txt, limite=60):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    txt = re.sub(r"[^a-zA-Z0-9]+", "-", txt).strip("-").lower()
    return txt[:limite].strip("-") or "video"


# ---------------------------------------------------------------- linkedin

def linkedin_fontes(pagina):
    """Lista {src, bitrate, rotulo} do atributo data-sources do player."""
    texto = html.unescape(html.unescape(pagina))
    fontes = {}
    for bloco in re.findall(r"data-sources=\"(\[.*?\])\"", pagina):
        try:
            for f in json.loads(html.unescape(bloco)):
                fontes[f["src"]] = f
        except (ValueError, KeyError):
            pass
    if not fontes:  # formato alternativo: URLs soltas no JSON da página
        for src in re.findall(r"https://dms\.licdn\.com/playlist/vid/[^\"'\s<>]+", texto):
            fontes.setdefault(src, {"src": src})
    saida = []
    for src, f in fontes.items():
        rot = re.search(r"/(mp4-[^/]+)/", src)
        if not rot:
            continue  # thumbnail e afins
        alt = re.search(r"mp4-(\d+)p", src)
        saida.append({"src": src, "rotulo": rot.group(1),
                      "bitrate": int(f.get("data-bitrate") or 0),
                      "altura": int(alt.group(1)) if alt else 0})
    return sorted(saida, key=lambda f: (f["altura"], f["bitrate"]))


def linkedin_atividade(url):
    m = re.search(r"activity[:-](\d{15,})", url) or re.search(r"ugcPost[:-](\d{15,})", url)
    return m and (("ugcPost" if "ugcPost" in m.group(0) else "activity"), m.group(1))


def linkedin_nome(pagina, url):
    autor = re.search(r'<meta property="og:title" content="[^"]*\|\s*([^"]+)"', pagina)
    base = re.search(r"/posts/([^/?]+?)_", url)
    partes = [slug(autor.group(1)) if autor else (slug(base.group(1)) if base else "linkedin")]
    at = linkedin_atividade(url)
    if at:
        partes.append(at[1][-6:])
    return "linkedin-" + "-".join(partes)


def linkedin_texto(pagina):
    """Texto do post, para dar contexto à análise do vídeo."""
    m = re.search(r'<p[^>]*attributed-text-segment-list__content[^>]*>(.*?)</p>', pagina, re.S)
    if not m:
        return None
    t = re.sub(r"<br\s*/?>", "\n", m.group(1))
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip() or None


def rota_linkedin(url, pagina):
    fontes = linkedin_fontes(pagina)
    if not fontes:
        at = linkedin_atividade(url)
        if at:  # o embed é público mesmo quando o feed pede login
            embed = f"https://www.linkedin.com/embed/feed/update/urn:li:{at[0]}:{at[1]}"
            _, pag2 = resolver(embed)
            fontes = linkedin_fontes(pag2)
    if not fontes:
        raise Falha("sem_video", "a página não expõe vídeo público: post sem vídeo, "
                    "post restrito a conexões ou exige login (tente yt-dlp com cookies)", 2)
    return fontes, linkedin_nome(pagina, url)


# ---------------------------------------------------------------- yt-dlp

def rota_ytdlp(url, pasta, listar):
    exe = shutil.which("yt-dlp")
    if not exe:
        raise Falha("ferramenta_ausente", "esta URL precisa do yt-dlp; instale com "
                    "`pipx install yt-dlp` e rode de novo", 3)
    if listar:
        subprocess.run([exe, "-F", url], check=False)
        return None
    modelo = os.path.join(pasta, "%(extractor)s-%(uploader|autor)s-%(id)s.%(ext)s")
    r = subprocess.run([exe, "--no-playlist", "-o", modelo, "--print", "after_move:filepath",
                        "-f", "mp4/bv*+ba/b", url], capture_output=True, text=True)
    if r.returncode:
        raise Falha("ytdlp", (r.stderr or r.stdout).strip().splitlines()[-1])
    return r.stdout.strip().splitlines()[-1]


# ---------------------------------------------------------------- comum

def gravar(src, destino):
    if os.path.exists(destino):
        raise Falha("existe", f"{destino} já existe; não sobrescrevo")
    tmp = destino + ".parcial"
    try:
        with abrir(src) as r, open(tmp, "wb") as f:
            tipo = r.headers.get("Content-Type", "")
            if not tipo.startswith("video/"):
                raise Falha("tipo", f"a URL devolveu {tipo or 'sem tipo'}, não vídeo")
            esperado = int(r.headers.get("Content-Length") or 0)
            shutil.copyfileobj(r, f, 1 << 20)
        tam = os.path.getsize(tmp)
        if not tam or (esperado and tam != esperado):
            raise Falha("incompleto", f"baixou {tam} de {esperado} bytes")
        os.replace(tmp, destino)
        return tam
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def plataforma(url):
    host = urllib.parse.urlparse(url).hostname or ""
    if host == "linkedin.com" or host.endswith(".linkedin.com"):
        return "linkedin"
    return "generica"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url")
    ap.add_argument("-o", "--pasta", default=".")
    ap.add_argument("--listar", action="store_true", help="mostra as opções, não baixa")
    ap.add_argument("--qualidade", choices=["melhor", "menor"], default="melhor")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    rel = {"url": a.url}
    try:
        if plataforma(a.url) == "generica" and not re.match(r"https?://lnkd\.in/", a.url):
            final, pagina = a.url, ""  # o yt-dlp resolve sozinho
        else:
            final, pagina = resolver(a.url)
        rel.update(url_final=final.split("?")[0], plataforma=plataforma(final))
        if rel["plataforma"] == "linkedin":
            fontes, nome = rota_linkedin(final, pagina)
            rel["texto_post"] = linkedin_texto(pagina)
            rel["opcoes"] = [{k: f[k] for k in ("rotulo", "altura", "bitrate")} for f in fontes]
            if not a.listar:
                f = fontes[-1] if a.qualidade == "melhor" else fontes[0]
                os.makedirs(a.pasta, exist_ok=True)
                destino = os.path.join(a.pasta, f"{nome}-{f['altura'] or 'x'}p.mp4")
                rel.update(arquivo=os.path.abspath(destino), escolhido=f["rotulo"],
                           bytes=gravar(f["src"], destino))
        else:
            rel["meio"] = "yt-dlp"
            arq = rota_ytdlp(final, a.pasta, a.listar)
            if arq:
                rel.update(arquivo=os.path.abspath(arq), bytes=os.path.getsize(arq))
        rel["status"] = "listado" if a.listar else "ok"
        codigo = 0
    except Falha as e:
        rel.update(status="falha", kind=e.kind, erro=str(e))
        codigo = e.codigo

    if a.json:
        print(json.dumps(rel, ensure_ascii=False, indent=2))
    elif rel["status"] == "falha":
        print(f"FALHA ({rel['kind']}): {rel['erro']}", file=sys.stderr)
    elif a.listar:
        for o in rel.get("opcoes", []):
            print(f"{o['rotulo']}  {o['altura']}p  {o['bitrate']} bps")
    else:
        print(f"{rel['arquivo']}  ({rel['bytes'] / 1e6:.1f} MB)")
    return codigo


if __name__ == "__main__":
    sys.exit(main())

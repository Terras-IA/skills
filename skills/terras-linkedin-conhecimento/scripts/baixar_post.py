#!/usr/bin/env python3
"""Baixa texto e imagens de posts do LinkedIn para estudo, sem login.

Só stdlib. Lê a página pública do post (lnkd.in é seguido até o fim) e tira os
dados do JSON-LD (SocialMediaPosting): autor, data, texto integral e imagens do
post. Fallback no HTML só dentro do card principal, antes dos comentários, para
não misturar foto de perfil de quem comentou.

Uso:
  baixar_post.py URL [URL ...] [--base PASTA]

Grava em BASE/AAAA-MM-DD/<autor>-<id6>/ (data de publicação do post):
  post.md          link, autor, data, números e texto original
  texto-plano.txt  texto com negrito/itálico Unicode desfeito (NFKC), para busca
  imagem-N.jpg     imagens do post na resolução que o link assinado entrega
  pagina-NN.jpg    páginas do carrossel PDF (~1000 px) e documento.txt com a transcrição
Pasta que já existe não é regravada: sai como "ja_baixado".
Saída 0 = todos ok ou já baixados. 1 = algum falhou. 2 = nada público no post.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import unicodedata
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
BASE_PADRAO = os.path.expanduser("~/linkedin/conhecimento")


def abrir(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    return urllib.request.urlopen(req, timeout=30)


def slug(txt, limite=40):
    txt = unicodedata.normalize("NFKD", unicodedata.normalize("NFKC", txt))
    txt = re.sub(r"[^a-zA-Z0-9]+", "-", txt.encode("ascii", "ignore").decode())
    return txt.strip("-").lower()[:limite].strip("-") or "post"


def plano(txt):
    """𝗝𝗪𝗧 -> JWT. O negrito Unicode do LinkedIn quebra busca e leitura de máquina."""
    return unicodedata.normalize("NFKC", txt or "")


def ld_post(pagina):
    for bloco in re.findall(r'<script type="application/ld\+json">(.*?)</script>', pagina, re.S):
        try:
            d = json.loads(bloco)
        except ValueError:
            continue
        for item in d if isinstance(d, list) else [d]:
            if isinstance(item, dict) and item.get("@type") in ("SocialMediaPosting", "Article", "NewsArticle"):
                return item
    return {}


def lista(v):
    return v if isinstance(v, list) else ([v] if v else [])


def card_principal(pagina):
    """HTML do post em si: do card principal até o primeiro comentário."""
    ini = pagina.find("main-feed-activity-card")
    if ini < 0:
        return ""
    fim = pagina.find("comment-", ini)
    return pagina[ini:fim if fim > 0 else len(pagina)]


def imagens(ld, card):
    urls = [i.get("url") if isinstance(i, dict) else i for i in lista(ld.get("image"))]
    # o JSON-LD às vezes traz o placeholder "Posted on LinkedIn" (static.licdn.com) no lugar da foto
    urls = [u for u in urls if u and "media.licdn.com/dms/image" in u and "profile-display" not in u]
    if not urls:  # post com várias imagens nem sempre lista todas no JSON-LD
        urls = [html.unescape(u) for u in re.findall(
            r'(?:data-delayed-url|src)="(https://media\.licdn\.com/dms/image/[^"]+)"', card)]
        urls = [u for u in urls if re.search(r"/(feedshare|article-cover|image-shrink)", u)]
    return list(dict.fromkeys(urls))


def texto_html(card):
    m = re.search(r'<p[^>]*attributed-text-segment-list__content[^>]*>(.*?)</p>', card, re.S)
    if not m:
        return None
    t = re.sub(r"<br\s*/?>", "\n", m.group(1))
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip() or None


def id_post(url):
    m = re.search(r"(?:activity|ugcPost|share)[:-](\d{15,})", url)
    return m and m.group(1)


def numeros(ld):
    out = {}
    for s in lista(ld.get("interactionStatistic")):
        tipo = str(s.get("interactionType", "")).rsplit("/", 1)[-1]
        out[{"LikeAction": "reacoes", "CommentAction": "comentarios", "ShareAction": "compartilhamentos"}
            .get(tipo, tipo)] = s.get("userInteractionCount")
    if ld.get("commentCount") and "comentarios" not in out:
        out["comentarios"] = ld["commentCount"]
    return out


def documento(card):
    """Carrossel PDF: o manifesto público traz as páginas em imagem e a transcrição."""
    m = re.search(r'data-native-document-config="([^"]+)"', card)
    if not m:
        return None
    try:
        doc = json.loads(html.unescape(m.group(1)))["doc"]
        with abrir(doc["manifestUrl"]) as r:
            man = json.load(r)
        res = sorted(man["perResolutions"], key=lambda x: x["width"])
        alvo = next((x for x in res if x["width"] >= 1000), res[-1])
        with abrir(alvo["imageManifestUrl"]) as r:
            paginas = json.load(r)["pages"]
        transcricao = []
        if man.get("transcriptManifestUrl"):
            with abrir(man["transcriptManifestUrl"]) as r:
                transcricao = json.load(r).get("pages", [])
        return {"titulo": doc.get("title"), "paginas": paginas, "transcricao": transcricao}
    except Exception as e:
        return {"erro": str(e)}


def baixar_imagem(src, destino):
    tmp = destino + ".parcial"
    try:
        with abrir(src) as r, open(tmp, "wb") as f:
            tipo = r.headers.get("Content-Type", "")
            if not tipo.startswith("image/"):
                raise ValueError(f"veio {tipo or 'sem tipo'}, não imagem")
            shutil.copyfileobj(r, f, 1 << 20)
        ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(tipo, ".jpg")
        final = os.path.splitext(destino)[0] + ext
        os.replace(tmp, final)
        return final
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def gravar_md(pasta, d):
    linhas = [f"# Post de {d['autor']}", "",
              f"- Post: {d['url_final']}",
              f"- Autor: {d['autor']}",
              f"- Publicado: {d['publicado'] or '(sem data na página)'}",
              f"- Baixado em: {dt.datetime.now():%Y-%m-%d %H:%M}",
              f"- Números: {', '.join(f'{k} {v}' for k, v in d['numeros'].items()) or '(não expostos)'}",
              f"- Imagens: {', '.join(os.path.basename(i) for i in d['imagens']) or 'nenhuma'}",
              "", "O conteúdo é do autor: citar com crédito, não repostar como seu.", "",
              "## Texto do post (original)", "", d["texto"] or "(a página pública não trouxe o texto)", ""]
    with open(os.path.join(pasta, "post.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))


def baixar(url, base):
    try:
        with abrir(url) as r:
            final, pagina = r.geturl(), r.read().decode("utf-8", "replace")
    except Exception as e:
        return {"url": url, "status": "falha", "kind": "rede", "erro": str(e)}
    final = final.split("?")[0]
    if "linkedin.com" not in final:
        return {"url": url, "status": "falha", "kind": "nao_linkedin", "erro": final}
    if "/login" in final or "authwall" in final:
        return {"url": url, "status": "falha", "kind": "login", "erro": "post exige login (restrito a conexões?)"}

    ld, card = ld_post(pagina), card_principal(pagina)
    autor = ((ld.get("author") or {}).get("name") if isinstance(ld.get("author"), dict) else None) \
        or (re.findall(r'public_post_feed-actor-name"[^>]*>\s*([^<]+?)\s*<', pagina) or ["autor"])[0]
    autor = html.unescape(autor)
    texto = ld.get("articleBody") or texto_html(card)
    imgs = imagens(ld, card)
    tem_video = bool(ld.get("video")) or "data-sources=" in card
    if not texto and not imgs:
        return {"url": url, "status": "falha", "kind": "sem_conteudo",
                "erro": "página pública sem texto nem imagem: post restrito ou removido"}

    publicado = (ld.get("datePublished") or "")[:10]
    pid = id_post(pagina[:5000] + final) or "000000"
    pasta = os.path.join(base, publicado or f"{dt.date.today():%Y-%m-%d}", f"{slug(autor)}-{pid[-6:]}")
    if os.path.exists(os.path.join(pasta, "post.md")):
        return {"url": url, "status": "ja_baixado", "pasta": pasta}
    os.makedirs(pasta, exist_ok=True)

    salvas, erros = [], []
    for n, src in enumerate(imgs, 1):
        try:
            salvas.append(baixar_imagem(src, os.path.join(pasta, f"imagem-{n}.jpg")))
        except Exception as e:
            erros.append(f"imagem-{n}: {e}")
    doc = documento(card)
    if doc and doc.get("paginas"):
        for n, src in enumerate(doc["paginas"], 1):
            try:
                salvas.append(baixar_imagem(src, os.path.join(pasta, f"pagina-{n:02d}.jpg")))
            except Exception as e:
                erros.append(f"pagina-{n}: {e}")
        if any(t.strip() for t in doc["transcricao"]):  # slide só com imagem vem com transcrição vazia
            with open(os.path.join(pasta, "documento.txt"), "w", encoding="utf-8") as f:
                f.write(f"# {doc.get('titulo') or 'Documento'}\n\n" + "\n\n".join(
                    f"## Página {i}\n\n{plano(t)}" for i, t in enumerate(doc["transcricao"], 1)) + "\n")
    elif doc:
        erros.append(f"documento: {doc.get('erro', 'sem páginas')}")
    d = {"url": url, "url_final": final, "autor": autor, "publicado": publicado,
         "texto": texto, "imagens": salvas, "numeros": numeros(ld)}
    gravar_md(pasta, d)
    with open(os.path.join(pasta, "texto-plano.txt"), "w", encoding="utf-8") as f:
        f.write(plano(texto) + "\n")

    rel = {"url": url, "status": "ok" if not erros else "parcial", "pasta": pasta, "autor": autor,
           "publicado": publicado, "imagens": salvas, "chars": len(texto or ""),
           "inicio": plano(texto)[:160]}
    if erros:
        rel["erros"] = erros
    if tem_video:
        rel["aviso"] = "post tem vídeo: baixe com terras-linkedin-videos"
    if doc and doc.get("paginas"):
        rel["documento"] = f"{len(doc['paginas'])} páginas" + (", transcrição em documento.txt" if any(t.strip() for t in doc["transcricao"]) else ", sem texto transcrito: ler as páginas")
    return rel


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("urls", nargs="+")
    ap.add_argument("--base", default=BASE_PADRAO)
    a = ap.parse_args()
    res = [baixar(u, a.base) for u in dict.fromkeys(a.urls)]
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if all(r["status"] == "falha" and r.get("kind") == "sem_conteudo" for r in res):
        return 2
    return 1 if any(r["status"] in ("falha", "parcial") for r in res) else 0


if __name__ == "__main__":
    sys.exit(main())

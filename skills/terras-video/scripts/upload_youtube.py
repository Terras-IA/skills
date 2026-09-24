#!/usr/bin/env python3
"""Sobe um video no YouTube pela API oficial (YouTube Data API v3).

Precisa de uma credencial OAuth que so o dono da conta cria (nada aqui pode fazer
isso por voce). O roteiro de uma vez so esta em `setup-youtube.sh` e no SKILL.md.

    # primeira vez: autoriza no navegador e guarda o token
    python3 upload_youtube.py autorizar

    # sobe (privado por padrao; publico exige --publico)
    python3 upload_youtube.py enviar --video out/video.mp4 --titulo "..." \
        --descricao "..." --tags ia,engenharia --thumb out/cartela-1.png

    # monta o pacote a partir do roteiro do build.py
    python3 upload_youtube.py pacote roteiro.json

Arquivos de credencial (em $TERRAS_VIDEO_HOME, padrao ~/.config/terras-video):
    client_secret.json   baixado do Google Cloud, tipo "Desktop app"
    youtube_token.json   criado pelo comando autorizar
"""
import argparse
import json
import os
import re
import sys

BASE = os.path.expanduser(os.environ.get("TERRAS_VIDEO_HOME", "~/.config/terras-video"))
FFMPEG = os.path.join(BASE, "ffmpeg")
BRAND_DIR = os.path.expanduser(os.environ.get("TERRAS_BRAND_DIR", "~/Documents/Diversos/terras-brand"))
CLIENT_SECRET = os.path.join(BASE, "client_secret.json")
TOKEN = os.path.join(BASE, "youtube_token.json")
ESCOPOS = ["https://www.googleapis.com/auth/youtube.upload"]
CATEGORIA_PADRAO = "28"   # Science & Technology
SHORTS_MAX_S = 180        # acima disso o YouTube nao classifica mais como Short


def fail(msg):
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


def garantir_interpretador():
    """Reexecuta no python do venv, que e onde as bibliotecas do Google vivem.

    Sem isso, chamar o script com o python do sistema morre com ImportError no meio
    do caminho, que foi exatamente o que aconteceu no primeiro teste.
    """
    try:
        import googleapiclient  # noqa: F401
        return
    except ImportError:
        pass
    venv_dir = os.path.join(BASE, "venv")
    venv_python = os.path.join(venv_dir, "bin", "python")
    # Comparar sys.prefix, nao o caminho do binario: o python do venv e um link para
    # o mesmo binario do sistema, entao o realpath dos dois da igual e a troca de
    # interpretador era pulada em silencio.
    if os.path.exists(venv_python) and os.path.realpath(sys.prefix) != os.path.realpath(venv_dir):
        os.execv(venv_python, [venv_python, os.path.abspath(__file__), *sys.argv[1:]])
    fail("faltam as bibliotecas do Google e o venv nao foi encontrado. "
         "Rode: bash ~/.zcode/skills/terras-video/scripts/setup-youtube.sh")


def credenciais(console=False):
    """Devolve credenciais validas, autorizando na primeira vez."""
    garantir_interpretador()
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, ESCOPOS)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN, "w") as fh:
            fh.write(creds.to_json())
        return creds

    if not os.path.exists(CLIENT_SECRET):
        fail(
            f"credencial ausente em {CLIENT_SECRET}.\n"
            "Crie assim, uma vez, na conta Google que e dona do canal:\n"
            "  1. console.cloud.google.com -> novo projeto\n"
            "  2. APIs e servicos -> Biblioteca -> ativar 'YouTube Data API v3'\n"
            "  3. Tela de consentimento OAuth: tipo Externo, e se a conta for pessoal\n"
            "     publique o app (o modo 'Testing' expira o refresh token em 7 dias)\n"
            "  4. Credenciais -> criar -> ID do cliente OAuth -> tipo 'App para computador'\n"
            "  5. baixar o JSON e salvar como " + CLIENT_SECRET
        )
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, ESCOPOS)
    creds = flow.run_local_server(port=0, open_browser=not console,
                                 authorization_prompt_message="Abra esta URL para autorizar: {url}",
                                 success_message="Autorizado. Pode fechar esta aba.")
    with open(TOKEN, "w") as fh:
        fh.write(creds.to_json())
    print(f"token salvo em {TOKEN}")
    return creds


def cliente(console=False):
    garantir_interpretador()   # antes do import: quem precisa das libs avisa o venv
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=credenciais(console))


def formato_do_roteiro(cfg):
    """Le o formato e o canvas do roteiro sem depender do build.py.

    Este script roda solto (as vezes so para montar o pacote), entao repete a regra:
    `size` manda, depois o `formato`, e sem nenhum dos dois vale o horizontal.
    """
    tamanho = cfg.get("size")
    if not tamanho:
        nome = (cfg.get("formato") or "horizontal").lower()
        tamanho = {"shorts": "1080x1920", "vertical": "1080x1920",
                   "quadrado": "1080x1080"}.get(nome, "1920x1080")
    try:
        largura, altura = (int(x) for x in str(tamanho).split("x"))
    except ValueError:
        return "horizontal", str(tamanho)
    if altura > largura:
        return "shorts", f"{largura}x{altura}"
    return ("quadrado" if altura == largura else "horizontal"), f"{largura}x{altura}"


def _duracao(caminho):
    import subprocess
    r = subprocess.run([FFMPEG, "-i", caminho], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", r.stderr)
    if not m:
        return None
    h, mi, seg = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(seg)


def _mmss(segundos):
    return f"{int(segundos // 60):02d}:{int(segundos % 60):02d}"


def ler_pacote_de_roteiro(caminho, out_dir=None):
    """Monta o pacote de publicacao: titulo, descricao com capitulos, tags e capa.

    Os tempos de capitulo saem das narracoes ja renderizadas quando existem, e nesse
    caso sao exatos; sem render, sao estimados por caracteres (12,5 por segundo,
    medido com a voz padrao). A descricao segue as regras da casa: sem travessao, sem
    promessa que o video nao faz, e as duas primeiras linhas fazem sentido sozinhas,
    porque e o que aparece antes do "mostrar mais".
    """
    cfg = json.load(open(caminho, encoding="utf-8"))
    blocos = cfg.get("blocks", [])
    formato, tamanho = formato_do_roteiro(cfg)
    marca = ""
    tema = (brand_tokens_local() or {}).get("temas", {}).get((cfg.get("tema") or "pessoal"), {})
    canal = tema.get("canal") or {}
    if canal.get("marca"):
        marca = canal["marca"][0].capitalize() + (canal["marca"][1] if len(canal["marca"]) > 1 else "")

    def sem_tags(t):
        """Tira as tags do texto de tela sem deixar sujeira de HTML.

        `<br>` e `<em>` viram espaco na conversao, entao sobram espaco duplo no meio
        e espaco antes de pontuacao ("a  harness ." no primeiro teste).
        """
        txt = re.sub(r"<br\s*/?>", " ", t or "")
        txt = re.sub(r"<[^>]+>", "", txt).replace("&nbsp;", " ")
        txt = re.sub(r"\s+", " ", txt)
        return re.sub(r"\s+([,.;:!?])", r"\1", txt).strip()

    falas = [b.get("narration", "").strip() for b in blocos]
    gancho = falas[0].split(". ")[0].strip() if falas else ""
    manchete = sem_tags(blocos[0].get("headline", "")) if blocos else ""

    titulos = []
    if manchete:
        titulos.append(manchete)
        if marca:
            titulos.append(f"{marca}: {manchete[:100 - len(marca) - 2]}")
    if gancho:
        titulos.append(gancho[:100])

    # capitulos: duracao real das narracoes, se o render ja rodou
    capitulos, t = [], 0.0
    for i, b in enumerate(blocos):
        rotulo = sem_tags(b.get("headline", "")) or f"Bloco {i + 1}"
        wav = os.path.join(out_dir or "", f"narracao-{i + 1}.wav")
        d = _duracao(wav) if out_dir and os.path.exists(wav) else None
        if d is None:
            cena = (b.get("cena") or {}).get("duracao")
            estimado = len(falas[i]) / 12.5 + 0.6
            d = max(float(cena), estimado) if cena else estimado
        capitulos.append((t, rotulo))
        t += d + 0.6
    # Capitulos so em video longo: num Short de 30 segundos eles nao ajudam ninguem, e o
    # YouTube nem monta a divisao.
    linhas_cap = ("\n".join(f"{_mmss(s)} {r}" for s, r in capitulos)
                  if (len(capitulos) > 2 and formato != "shorts") else "")

    resumo = " ".join(falas[1:3]).strip()
    # Mesma cadeia do build.py: roteiro, depois o tema (canal.foot ou rodape.url), e o
    # `assinatura` global por ultimo. Sem isso a descricao podia fechar com um endereco
    # diferente do que aparece no rodape do video.
    rodape = (cfg.get("foot") or canal.get("foot") or (tema.get("rodape") or {}).get("url")
              or (brand_tokens_local() or {}).get("assinatura") or "")
    descricao = "\n\n".join(x for x in [
        gancho + "." if gancho and not gancho.endswith(".") else gancho,
        resumo,
        ("Neste vídeo:\n" + linhas_cap) if linhas_cap else "",
        rodape,
    ] if x.strip())
    if formato == "shorts" and "#Shorts" not in descricao:
        # O YouTube classifica vertical de ate 3 minutos sozinho, mas a hashtag e barata
        # e ajuda na busca. No titulo ela rouba espaco, entao vai na descricao.
        descricao = f"{descricao}\n\n#Shorts" if descricao.strip() else "#Shorts"

    tags = cfg.get("tags") or [marca.lower(), "agentes de ia", "governança de ia", "llm em produção"]
    if formato == "shorts" and "Shorts" not in tags:
        tags = [*tags, "Shorts"]

    pacote = {
        "titulo": titulos[0] if titulos else "Vídeo",
        "titulos_sugeridos": titulos,
        "descricao": descricao,
        "tags": tags,
        "formato": formato,
        "tamanho": tamanho,
        "capa": os.path.join(out_dir or "", "capa-1280x720.png"),
    }
    if formato == "shorts":
        pacote["nota_formato"] = (
            "vertical: o YouTube classifica como Short sozinho, ate 3 minutos e 1080p. A "
            "miniatura do feed e um quadro do video; a capa 1280x720 vale no canal e na busca."
        )
    # validacoes da casa, na mesma linha do build.py
    avisos = []
    for ti in titulos:
        if len(ti) > 100:
            avisos.append(f"titulo com {len(ti)} caracteres passa do limite de 100 do YouTube: {ti[:40]}...")
        elif len(ti) > 60:
            avisos.append(f"titulo com {len(ti)} caracteres: passa de 60, o feed corta: {ti[:40]}...")
    if "—" in descricao or "–" in descricao:
        avisos.append("travessao no texto: a regra da casa e zero")
    if capitulos and capitulos[0][0] != 0:
        avisos.append("primeiro capitulo nao comeca em 00:00")
    if formato == "shorts" and t > SHORTS_MAX_S:
        avisos.append(f"o roteiro da ~{t:.0f}s, acima do limite de {SHORTS_MAX_S}s dos Shorts: "
                      "o YouTube nao vai classificar como Short")
    pacote["avisos"] = avisos
    return pacote


def brand_tokens_local():
    try:
        with open(os.path.join(BRAND_DIR, "brand.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def enviar(creds_args):
    garantir_interpretador()
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(creds_args.video):
        fail(f"video nao encontrado: {creds_args.video}")
    if creds_args.publico and not creds_args.sim_publicar:
        fail("publicar como publico exige --sim-publicar (a acao e irreversivel na pratica: "
             "o video fica visivel e notifica inscritos)")
    visibilidade = "public" if creds_args.publico else (creds_args.visibilidade or "private")
    tags = [t.strip() for t in (creds_args.tags or "").split(",") if t.strip()]

    corpo = {
        "snippet": {
            "title": creds_args.titulo[:100],
            "description": creds_args.descricao or "",
            "tags": tags,
            "categoryId": creds_args.categoria or CATEGORIA_PADRAO,
            "defaultLanguage": creds_args.idioma or "pt-BR",
        },
        "status": {
            "privacyStatus": visibilidade,
            "selfDeclaredMadeForKids": False,
        },
    }
    if creds_args.playlist:
        corpo["snippet"]["playlistId"] = creds_args.playlist

    midia = MediaFileUpload(creds_args.video, chunksize=8 * 1024 * 1024, resumable=True)
    req = cliente(creds_args.console).videos().insert(
        part="snippet,status", body=corpo, media_body=midia)
    resposta = None
    while resposta is None:
        status, resposta = req.next_chunk()
        if status:
            print(f"  enviado {int(status.progress() * 100)}%")
    vid = resposta["id"]
    print(f"VIDEO: https://youtu.be/{vid} (visibilidade {visibilidade})")

    if creds_args.thumb:
        if os.path.exists(creds_args.thumb):
            cliente(creds_args.console).thumbnails().set(
                videoId=vid, media_body=MediaFileUpload(creds_args.thumb)).execute()
            print(f"  miniatura aplicada: {creds_args.thumb}")
        else:
            print(f"  AVISO: miniatura nao encontrada: {creds_args.thumb}")
    if not creds_args.publico:
        print("  lembre de trocar para publico no Studio quando revisar, ou reenviar com --publico --sim-publicar")
    return vid


def canal(console=False):
    """Mostra qual canal a credencial controla, antes de subir qualquer coisa.

    Existe porque a autorizacao pode cair na conta pessoal em vez do canal do
    projeto: se a conta for de marca, o Google pede a escolha do canal no fluxo, e
    o token fica preso ao que foi escolhido.
    """
    yt = cliente(console)
    r = yt.channels().list(part="snippet,contentDetails", mine=True).execute()
    itens = r.get("items") or []
    if not itens:
        fail("a credencial nao controla nenhum canal. Reautorize escolhendo o canal "
             "terrasia-slc e revogue o acesso antigo em myaccount.google.com/permissions")
    for c in itens:
        print(f"canal: {c['snippet']['title']} | id {c['id']} | "
              f"uploads {c['contentDetails']['relatedPlaylists']['uploads']}")
    return itens


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="acao", required=True)

    a = sub.add_parser("autorizar", help="faz o fluxo OAuth e guarda o token")
    a.add_argument("--console", action="store_true", help="imprime a URL em vez de abrir o navegador")

    pk = sub.add_parser("pacote", help="monta titulo, descricao com capitulos, tags e capa")
    pk.add_argument("roteiro")
    pk.add_argument("--out-dir", default=None, help="pasta do render, para os tempos exatos dos capitulos")
    pk.add_argument("--json", action="store_true")

    c = sub.add_parser("canal", help="mostra qual canal a credencial controla")
    c.add_argument("--console", action="store_true")

    e = sub.add_parser("enviar", help="sobe o video")
    e.add_argument("--video", required=True)
    e.add_argument("--titulo", required=True)
    e.add_argument("--descricao", default="")
    e.add_argument("--tags", default="")
    e.add_argument("--thumb", default="")
    e.add_argument("--categoria", default=CATEGORIA_PADRAO)
    e.add_argument("--idioma", default="pt-BR")
    e.add_argument("--playlist", default="")
    e.add_argument("--visibilidade", choices=["private", "unlisted", "public"], default="private")
    e.add_argument("--publico", action="store_true", help="atalho para visibilidade publica")
    e.add_argument("--sim-publicar", action="store_true", help="confirma a publicacao publica")
    e.add_argument("--console", action="store_true")

    args = ap.parse_args()
    if args.acao == "autorizar":
        credenciais(args.console)
        print("autorizacao ok")
    elif args.acao == "pacote":
        p = ler_pacote_de_roteiro(args.roteiro, args.out_dir)
        if args.json:
            print(json.dumps(p, ensure_ascii=False, indent=2))
        else:
            print("== titulos sugeridos ==")
            for i, ti in enumerate(p["titulos_sugeridos"], start=1):
                print(f"  {i}. {ti}  ({len(ti)} caracteres)")
            print("\n== descricao ==")
            print(p["descricao"])
            print("\n== tags ==")
            print("  " + ", ".join(p["tags"]))
            print("\n== capa ==")
            print(f"  {p['capa']}" + ("" if os.path.exists(p["capa"]) else "  (ainda nao gerada: rode build.py capa)"))
            if p["avisos"]:
                print("\n== avisos ==")
                for a in p["avisos"]:
                    print("  - " + a)
            print("\n== comando para subir ==")
            print("  python3 ~/.zcode/skills/terras-video/scripts/upload_youtube.py enviar \\\n"
                  f"    --video {os.path.abspath(args.roteiro).replace('roteiro', 'video') if False else '<o mp4 renderizado>'} \\\n"
                  f"    --titulo \"{p['titulo']}\" \\\n"
                  f"    --descricao \"$(python3 ~/.zcode/skills/terras-video/scripts/upload_youtube.py pacote {args.roteiro} --json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"descricao\"])')\" \\\n"
                  f"    --tags \"{','.join(p['tags'])}\" \\\n"
                  f"    --thumb {p['capa']} --visibilidade unlisted")
    elif args.acao == "canal":
        canal(args.console)
    else:
        enviar(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
terras-instagram / scripts/ig.py
Publica e agenda imagens no Instagram pela API Graph (Instagram Login, graph.instagram.com).

Subcomandos:
  verificar                 Testa config e token; mostra dados da conta e limite de publicação.
  fila [--pasta DIR]        Lista imagens ainda não registradas em postagens.json (mais antigas primeiro).
  validar --arquivo F       Valida/normaliza imagem sem publicar (converte para JPEG se preciso).
  publicar -a F [F ...]     Publica (ou agenda) imagem(ns) com legenda.
                            --legenda "texto" | --legenda-arquivo legenda.txt
                            --tipo feed|story|carrossel (padrão: deduzido; >1 arquivo = carrossel)
                            --agendar "2026-10-05 19:00" (hora local; 10 min a 75 dias à frente)
                            --texto-alternativo "descrição" (alt_text; não vale para story)
                            --url URL   usa imagem já hospedada em vez de subir do arquivo local
  token --trocar            Troca token curto (1 h) por longa duração (~60 dias) usando app_secret.
  token --renovar           Renova o token de longa duração (precisa app_secret).
  registrar --arquivo F     Registra publicação feita manualmente para a fila não repetir o item.

Sem config.json a skill roda em modo preparo: fila, validar e registrar funcionam;
publicar/token/verificar pedem a configuração (ver referencias/configuracao-meta.md).
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PASTA_SKILL = Path(__file__).resolve().parent.parent
CONFIG_PADRAO = PASTA_SKILL / "config.json"
API = "https://graph.instagram.com/v23.0"
LIMITE_JPEG = 8 * 1024 * 1024
LADO_MAXIMO = 1440

try:
    from PIL import Image
except ImportError:
    Image = None


def falha(msg, dica=None):
    print(f"ERRO: {msg}")
    if dica:
        print(f"DICA: {dica}")
    sys.exit(1)


def carregar_config(caminho=None, obrigatorio=True):
    p = Path(caminho) if caminho else CONFIG_PADRAO
    if not p.exists():
        if obrigatorio:
            falha(
                f"config.json não encontrado em {p}",
                "copie config.exemplo.json para config.json e siga referencias/configuracao-meta.md",
            )
        return None
    cfg = json.loads(p.read_text(encoding="utf-8"))
    if obrigatorio:
        if not str(cfg.get("ig_user_id", "")).isdigit():
            falha('config.json: "ig_user_id" ausente ou inválido (só dígitos)')
        token = cfg.get("access_token", "")
        if not token or token.startswith("COLE_AQUI"):
            falha('config.json: "access_token" ainda é o marcador do exemplo')
    return cfg


TOKEN = None


def exigir_token(cfg):
    global TOKEN
    TOKEN = cfg["access_token"]


def api(caminho, params, metodo="GET"):
    url = f"{API}/{caminho}"
    if metodo == "GET":
        params = dict(params, access_token=TOKEN)
        url += "?" + urllib.parse.urlencode(params)
        dados = None
    else:
        dados = urllib.parse.urlencode(dict(params, access_token=TOKEN)).encode()
    req = urllib.request.Request(url, data=dados, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        try:
            erro = json.loads(corpo)["error"]
            msg = erro.get("message", corpo)
            extra = erro.get("error_user_msg", "")
        except Exception:
            msg, extra = corpo, ""
        falha(f"API respondeu {e.code} em {metodo} /{caminho}: {msg}" + (f" | {extra}" if extra else ""))
    except urllib.error.URLError as e:
        falha(f"sem rede ou DNS falhou em {url}: {e.reason}")


# ---------- imagens ----------

def slugificar(nome):
    base = unicodedata.normalize("NFKD", Path(nome).stem).encode("ascii", "ignore").decode()
    base = re.sub(r"[^a-zA-Z0-9]+", "-", base).strip("-").lower() or "post"
    return base


def preparar_imagem(caminho):
    """Devolve (caminho_jpeg, (w, h) ou None). Converte de PNG e reduz tamanho/lado se preciso."""
    origem = Path(caminho)
    if not origem.exists():
        falha(f"arquivo não encontrado: {origem}")
    ja_jpeg = origem.suffix.lower() in (".jpg", ".jpeg")
    if ja_jpeg and Image is None:
        return origem, None
    if ja_jpeg and origem.stat().st_size <= LIMITE_JPEG and max(Image.open(origem).size) <= LADO_MAXIMO:
        im = Image.open(origem)
        return origem, (im.width, im.height)
    if Image is None:
        falha(
            f"formato {origem.suffix} ou tamanho exige conversão e Pillow não está instalado",
            "pip install pillow (ou gere a imagem já em JPEG)",
        )
    im = Image.open(origem)
    if im.mode in ("RGBA", "P", "LA"):
        fundo = Image.new("RGB", im.size, (255, 255, 255))
        im_rgba = im.convert("RGBA")
        fundo.paste(im_rgba, mask=im_rgba.split()[-1])
        im = fundo
    else:
        im = im.convert("RGB")
    if max(im.size) > LADO_MAXIMO:
        fator = LADO_MAXIMO / max(im.size)
        im = im.resize((round(im.width * fator), round(im.height * fator)), Image.LANCZOS)
    destino = origem.with_suffix(".convertida.jpg")
    qualidade = 92
    while True:
        im.save(destino, "JPEG", quality=qualidade, optimize=True)
        if destino.stat().st_size <= LIMITE_JPEG or qualidade <= 60:
            break
        qualidade -= 8
    print(f"convertida: {destino.name} {im.width}x{im.height} JPEG ({destino.stat().st_size // 1024} KB)")
    return destino, (im.width, im.height)


def checar_proporcao(w, h, tipo):
    if not w:
        print("AVISO: não verifiquei a proporção (instale Pillow)")
        return
    razao = w / h
    if tipo == "story" and abs(razao - 9 / 16) > 0.02:
        print(f"AVISO: story com proporção {razao:.3f} (esperado 9:16); o Instagram pode recortar")
    if tipo in ("feed", "carrossel") and not (0.79 <= razao <= 1.92):
        print(f"AVISO: feed com proporção {razao:.3f} fora da faixa 4:5 a 1.91:1; o Instagram pode recortar")


# ---------- hospedagem ----------

def hospedar(caminho, cfg):
    """Sobe o JPEG para o bucket configurado e devolve (url_publica, nome_no_bucket)."""
    hosp = cfg.get("hospedagem") or {}
    if hosp.get("tipo") != "supabase":
        falha(
            'config.json: só há hospedagem "supabase" implementada',
            "ou passe --url com a imagem já em URL pública",
        )
    url = (hosp.get("url") or "").rstrip("/")
    chave, bucket = hosp.get("chave", ""), hosp.get("bucket", "instagram")
    if not url or not chave or chave.startswith("service_role_key_do"):
        falha(
            "hospedagem supabase sem url/chave no config.json",
            "a API do Instagram exige a imagem em URL pública; veja referencias/configuracao-meta.md",
        )
    nome = f"{slugificar(Path(caminho).stem)}-{int(time.time())}.jpg"
    req = urllib.request.Request(
        f"{url}/storage/v1/object/{bucket}/{nome}",
        data=Path(caminho).read_bytes(),
        method="POST",
        headers={"Authorization": f"Bearer {chave}", "Content-Type": "image/jpeg", "x-upsert": "true"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            r.read()
    except urllib.error.HTTPError as e:
        falha(f"upload no Supabase falhou ({e.code}): {e.read().decode(errors='replace')[:300]}")
    except urllib.error.URLError as e:
        falha(f"sem rede ou DNS falhou no upload: {e.reason}")
    publico = f"{url}/storage/v1/object/public/{bucket}/{nome}"
    print(f"hospedada: {nome}")
    return publico, nome


def remover_hospedagem(cfg, nome):
    hosp = cfg.get("hospedagem") or {}
    if not nome:
        return
    try:
        req = urllib.request.Request(
            f"{hosp['url'].rstrip('/')}/storage/v1/object/{hosp['bucket']}/{nome}",
            method="DELETE",
            headers={"Authorization": f"Bearer {hosp['chave']}"},
        )
        urllib.request.urlopen(req, timeout=60).read()
    except Exception as e:
        print(f"AVISO: não apaguei a cópia hospedada {nome} ({e}); remova à mão se quiser")


# ---------- estado (postagens.json) ----------

def pasta_raiz(cfg, args_pasta=None):
    return Path(args_pasta) if args_pasta else Path(cfg.get("pasta_raiz", "."))


def arquivo_estado(cfg, args_pasta=None):
    return pasta_raiz(cfg, args_pasta) / "postagens.json"


def carregar_estado(caminho):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return {"postagens": [], "agendadas": []}


def salvar_estado(caminho, estado):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")


def chave_arquivo(p):
    p = Path(p)
    return f"{p.name}:{p.stat().st_size if p.exists() else 0}"


def registrar_publicado(cfg, args, arquivos, tipo, legenda, mid, permalink):
    est = carregar_estado(arquivo_estado(cfg, args.pasta))
    est["postagens"].append(
        {
            "arquivo": chave_arquivo(arquivos[0]),
            "legenda": legenda,
            "tipo": tipo,
            "media_id": mid,
            "permalink": permalink,
            "publicado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    salvar_estado(arquivo_estado(cfg, args.pasta), est)


# ---------- subcomandos ----------

def cmd_fila(cfg, args):
    raiz = pasta_raiz(cfg, args.pasta)
    estado = carregar_estado(arquivo_estado(cfg, args.pasta))
    feitas = {p["arquivo"] for p in estado["postagens"]} | {p["arquivo"] for p in estado["agendadas"]}
    achadas = []
    for sub in ("timeline", "stories"):
        d = raiz / sub
        if d.is_dir():
            achadas += sorted(
                [p for p in d.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")],
                key=lambda p: (p.stat().st_mtime, p.name),
            )
    if estado["agendadas"]:
        print("agendadas (container criado, aguardando a hora):")
        for p in estado["agendadas"]:
            print(f"  {p['quando_local']}  {p['arquivo']}")
    pendentes = [p for p in achadas if chave_arquivo(p) not in feitas]
    if not pendentes:
        print("fila vazia: nenhuma imagem nova em timeline/ ou stories/")
        return
    print("na fila (mais antigas primeiro):")
    for p in pendentes:
        print(f"  {p.parent.name}/  {p.name}")


def cmd_validar(cfg, args):
    p, (w, h) = preparar_imagem(args.arquivo)
    tipo = "story" if "stories" in str(p) else "feed"
    checar_proporcao(w, h, tipo)
    if p != Path(args.arquivo) and p.exists() and p.name.endswith(".convertida.jpg"):
        p.unlink()
    print(f"válida para {tipo}")


def converter_horario(texto, cfg):
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        falha("agendar precisa de Python 3.9+ (zoneinfo)")
    tz = ZoneInfo(cfg.get("fuso", "America/Sao_Paulo"))
    try:
        local = datetime.strptime(texto, "%Y-%m-%d %H:%M").replace(tzinfo=tz)
    except ValueError:
        falha('use o formato "AAAA-MM-DD HH:MM" (hora local do fuso do config), ex.: --agendar "2026-10-05 19:00"')
    agora = datetime.now(tz)
    delta_min = (local - agora).total_seconds() / 60
    if delta_min < 10:
        falha(f"{texto} está a {delta_min:.0f} min de agora; o agendamento exige pelo menos 10 min à frente")
    if delta_min > 75 * 24 * 60:
        falha("o agendamento aceita no máximo 75 dias à frente")
    return int(local.astimezone(timezone.utc).timestamp()), local


def cmd_publicar(cfg, args):
    exigir_token(cfg)
    arquivos = args.arquivo
    tipo = args.tipo
    if tipo == "auto":
        tipo = "story" if (len(arquivos) == 1 and "stories" in str(arquivos[0])) else ("carrossel" if len(arquivos) > 1 else "feed")
    if tipo == "carrossel" and not (2 <= len(arquivos) <= 10):
        falha("carrossel precisa de 2 a 10 imagens")
    if tipo == "story" and (args.agendar or args.texto_alternativo):
        falha("story não suporta agendamento nem texto alternativo pela API")

    legenda = args.legenda
    if args.legenda_arquivo:
        legenda = Path(args.legenda_arquivo).read_text(encoding="utf-8").strip()
    if tipo in ("feed", "carrossel"):
        if not legenda:
            falha("legenda obrigatória para feed/carrossel", "escreva com a skill e passe --legenda ou --legenda-arquivo")
        if len(legenda) > 2200:
            falha(f"legenda tem {len(legenda)} caracteres; máximo do Instagram é 2200")

    ts, quando_local = (None, None)
    if args.agendar:
        ts, quando_local = converter_horario(args.agendar, cfg)

    temporarios = []
    container = None
    nome_hospedado = None
    if args.url and len(arquivos) == 1:
        url_publica = args.url
    else:
        dims = None
        preparadas = []
        for a in arquivos:
            p, d = preparar_imagem(a)
            preparadas.append(p)
            if p.name.endswith(".convertida.jpg"):
                temporarios.append(p)
            if d:
                dims = d
        checar_proporcao(dims[0], dims[1], tipo)
        if tipo == "carrossel":
            filhos, nomes_hospedados = [], []
            for p in preparadas:
                u, n = hospedar(p, cfg)
                filhos.append(api("media", {"image_url": u, "is_carousel_item": True}, "POST")["id"])
                nomes_hospedados.append(n)
            params = {"media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda}
            if args.texto_alternativo:
                params["alt_text"] = args.texto_alternativo
            if ts:
                params["publish_time"] = ts
            container = api("media", params, "POST")["id"]
            if _aguardar_container(container) == "EXPIRED":
                for n in nomes_hospedados:
                    remover_hospedagem(cfg, n)
                falha("container do carrossel expirou sem processar (URL pública inacessível ou imagem rejeitada)")
            for n in nomes_hospedados:
                remover_hospedagem(cfg, n)
        else:
            url_publica, nome_hospedado = hospedar(preparadas[0], cfg)

    if container is None:
        params = {"image_url": url_publica}
        if tipo == "story":
            params["media_type"] = "STORIES"
        else:
            params["caption"] = legenda
            if args.texto_alternativo:
                params["alt_text"] = args.texto_alternativo
            if ts:
                params["publish_time"] = ts
        container = api("media", params, "POST")["id"]
        status = _aguardar_container(container)
        if status == "EXPIRED":
            remover_hospedagem(cfg, nome_hospedado)
            falha("container expirou sem processar (URL pública inacessível ou imagem rejeitada)")
        if nome_hospedado:
            remover_hospedagem(cfg, nome_hospedado)

    if ts and tipo != "story":
        est = carregar_estado(arquivo_estado(cfg, args.pasta))
        est["agendadas"].append(
            {
                "arquivo": chave_arquivo(arquivos[0]),
                "legenda": legenda,
                "container": container,
                "quando_local": quando_local.strftime("%Y-%m-%d %H:%M"),
                "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        salvar_estado(arquivo_estado(cfg, args.pasta), est)
        for t in temporarios:
            t.unlink(missing_ok=True)
        print(f"AGENDADO: {quando_local.strftime('%d/%m/%Y %H:%M')} | container {container}")
        print("confira no app depois da hora; para postar antes do prazo, publique sem --agendar")
        return

    r = api("media_publish", {"creation_id": container}, "POST")
    mid = r["id"]
    permalink = ""
    try:
        d = api(mid, {"fields": "permalink,timestamp"})
        permalink = d.get("permalink", "")
    except SystemExit:
        print("AVISO: não consegui ler o permalink do post")
    registrar_publicado(cfg, args, arquivos, tipo, legenda or "(story)", mid, permalink)
    for t in temporarios:
        t.unlink(missing_ok=True)
    print(f"PUBLICADO: media_id {mid} tipo {tipo}" + (f" | {permalink}" if permalink else ""))


def _aguardar_container(cid, tentativas=20):
    for _ in range(tentativas):
        d = api(cid, {"fields": "status_code"})
        s = d.get("status_code")
        if s in ("FINISHED", "PUBLISHED"):
            return "ok"
        if s in ("EXPIRED", "ERROR"):
            return "EXPIRED"
        time.sleep(2)
    print("AVISO: container ainda processando; seguindo assim mesmo")
    return "ok"


def cmd_verificar(cfg, args):
    exigir_token(cfg)
    eu = api("me", {"fields": "id,username,media_count"})
    print(f"conta OK: @{eu.get('username')} (id {eu.get('id')}, {eu.get('media_count')} publicações)")
    try:
        lim = api("content_publishing_limit", {"fields": "quota_total,quota_usage"})
        print(f"limite de publicação: {lim['data'][0]['quota_usage']}/{lim['data'][0]['quota_total']} nas últimas 24h")
    except SystemExit:
        print("AVISO: não consegui ler o limite de publicação com este token; seguindo")
    criado = cfg.get("token_criado_em")
    if criado:
        dias = (datetime.now() - datetime.strptime(criado, "%Y-%m-%d")).days
        if dias > 50:
            print(f"AVISO: token tem {dias} dias; renove com: python3 {sys.argv[0]} token --renovar")
        else:
            print(f"token com {dias} dias de uso (renovar por volta de 50-55)")


def cmd_token(cfg, args):
    segredo = cfg.get("app_secret", "")
    if not segredo:
        falha('renovar/trocar token exige "app_secret" no config.json')
    global TOKEN
    TOKEN = cfg["access_token"]
    if args.trocar:
        d = api("access_token", {"grant_type": "ig_exchange_token", "client_secret": segredo})
    else:
        d = api("refresh_access_token", {"grant_type": "ig_refresh_token"})
    novo = d.get("access_token")
    if not novo:
        falha("API não devolveu token novo")
    cfg["access_token"], cfg["token_criado_em"] = novo, datetime.now().strftime("%Y-%m-%d")
    CONFIG_PADRAO.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"token de longa duração salvo em {CONFIG_PADRAO} (~60 dias; renove antes de expirar)")


def cmd_registrar(cfg, args):
    p = Path(args.arquivo)
    if not p.exists():
        falha(f"arquivo não encontrado: {p}")
    registrar_publicado(cfg, args, [p], "manual", args.legenda or "(publicado manualmente)", "", "")
    print(f"registrado como publicado manualmente: {p.name}")


def main():
    ap = argparse.ArgumentParser(description="Publica/agenda imagens no Instagram (IECSJC)")
    ap.add_argument("--config", help="caminho alternativo do config.json")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def pasta_arg(p):
        p.add_argument("--pasta", help="pasta raiz da fila (padrão: pasta_raiz do config)")

    s = sub.add_parser("verificar"); s.set_defaults(fn=cmd_verificar); pasta_arg(s)
    s = sub.add_parser("fila"); s.set_defaults(fn=cmd_fila); pasta_arg(s)
    s = sub.add_parser("validar"); s.add_argument("--arquivo", required=True); s.set_defaults(fn=cmd_validar)

    s = sub.add_parser("publicar")
    s.add_argument("-a", "--arquivo", action="append", required=True)
    s.add_argument("--legenda")
    s.add_argument("--legenda-arquivo")
    s.add_argument("--tipo", default="auto", choices=["auto", "feed", "story", "carrossel"])
    s.add_argument("--agendar", metavar='"AAAA-MM-DD HH:MM"')
    s.add_argument("--texto-alternativo")
    s.add_argument("--url", help="imagem já em URL pública (pula preparo e upload)")
    s.set_defaults(fn=cmd_publicar); pasta_arg(s)

    s = sub.add_parser("token")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--trocar", action="store_true")
    g.add_argument("--renovar", action="store_true")
    s.set_defaults(fn=cmd_token)

    s = sub.add_parser("registrar")
    s.add_argument("--arquivo", required=True)
    s.add_argument("--legenda")
    s.set_defaults(fn=cmd_registrar); pasta_arg(s)

    args = ap.parse_args()
    precisa_config = args.cmd not in ("fila", "validar", "registrar")
    cfg = carregar_config(args.config, obrigatorio=precisa_config)
    if cfg is None:
        if args.cmd in ("fila", "registrar") and not getattr(args, "pasta", None):
            falha("sem config.json, informe --pasta (ex.: --pasta /caminho/para/instagram)")
        cfg = {}
    args.fn(cfg, args)


if __name__ == "__main__":
    main()

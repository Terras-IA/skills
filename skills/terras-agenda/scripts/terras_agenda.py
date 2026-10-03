#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""terras-agenda — uma agenda só, com as contas que você já tem.

Junta num lugar só:
  * contas Microsoft 365 / Teams, uma por tenant, via Microsoft Graph
    (leitura e escrita);
  * qualquer feed .ics — Google Agenda ("endereço secreto"), Outlook/Exchange
    publicado, calendário compartilhado — leitura.

Comandos:
  check      diz o que falta (venv, config, login, feeds)
  auth       login Microsoft por código de dispositivo (uma conta por vez)
  contas     lista as contas e o estado do login de cada uma
  feeds      list/add/rm dos feeds .ics
  agenda     a agenda unificada de todos os lados
  hoje       o dia de hoje + o que vem em seguida + conflitos
  conflitos  só os choques de horário entre agendas
  criar      cria evento numa conta Microsoft
  exportar   joga a agenda unificada em .ics (para jogar em qualquer app)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "terras-agenda"
CONFIG_PATH = CONFIG_DIR / "config.json"
VENV_PYTHON = CONFIG_DIR / "venv" / "bin" / "python3"
GRAPH = "https://graph.microsoft.com/v1.0"

# Calendário: ler/escrever o meu; ler o que compartilharem comigo (é o caso de
# um calendário do ISO compartilhado para a conta da Sousa Lima).
SCOPES = ["Calendars.ReadWrite", "Calendars.Read.Shared"]

TZ_LOCAL = "America/Sao_Paulo"
TZ_GRAPH = "E. South America Standard Time"  # nome Windows, é o que o Graph espera

CONFIG_PADRAO = {
    "timezone": TZ_LOCAL,
    "timezone_graph": TZ_GRAPH,
    "conta_padrao": "SLC",
    "dias_padrao": 7,
    "contas": [],
    "feeds": [],
}


# ---------------------------------------------------------------- utilidades

def _reexec_venv() -> None:
    try:
        import msal  # noqa: F401
        return
    except ImportError:
        pass
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit("[erro] dependências ausentes. Rode: bash " + os.path.join(os.path.dirname(os.path.realpath(__file__)), "setup.sh"))


def zona(nome: str):
    from zoneinfo import ZoneInfo
    try:
        return ZoneInfo(nome)
    except Exception:
        return zoneinfo_utc()


def zoneinfo_utc():
    from zoneinfo import ZoneInfo
    return ZoneInfo("UTC")


def agora_local(cfg: dict) -> datetime:
    return datetime.now(zona(cfg.get("timezone", TZ_LOCAL)))


def carregar_json(caminho: Path, default):
    if not caminho.exists():
        return json.loads(json.dumps(default))
    return json.loads(caminho.read_text(encoding="utf-8"))


def salvar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    tmp.write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(caminho)


def carregar_config() -> dict:
    cfg = carregar_json(CONFIG_PATH, CONFIG_PADRAO)
    for k, v in CONFIG_PADRAO.items():
        cfg.setdefault(k, v)
    return cfg


def slug(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "conta"


def token_path(nome: str) -> Path:
    return CONFIG_DIR / f"token-{slug(nome)}.json"


def sem_acento(txt: str) -> str:
    return unicodedata.normalize("NFKD", txt or "").encode("ascii", "ignore").decode().lower()


DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sab", "dom"]
DIAS_LONGO = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def fmt_dia(d: date) -> str:
    return f"{DIAS_SEMANA[d.weekday()]} {d.day:02d}/{d.month:02d}"


def fmt_hora(t: time) -> str:
    return f"{t.hour:02d}:{t.minute:02d}"


# ------------------------------------------------------------------ contas

def conta_por_nome(cfg: dict, nome: str) -> dict:
    for c in cfg.get("contas", []):
        if sem_acento(c["nome"]) == sem_acento(nome):
            return c
    sys.exit(f"[erro] conta '{nome}' não está na config. Veja: terras_agenda.py contas")


def graph_app(conta: dict, cfg: dict):
    _reexec_venv()
    import msal
    if not conta.get("client_id"):
        sys.exit(
            f"[erro] conta '{conta['nome']}' sem client_id.\n"
            f"      Um app de cada tenant enxerga só o próprio tenant. Ou registre um app\n"
            f"      no tenant {conta.get('tenant')} (veja o INSTALL na SKILL.md) ou use um\n"
            f"      feed .ics dessa agenda (comando: feeds add)."
        )
    cache = msal.SerializableTokenCache()
    tp = token_path(conta["nome"])
    if tp.exists():
        cache.deserialize(tp.read_text(encoding="utf-8"))
    app = msal.PublicClientApplication(
        conta["client_id"],
        authority=f"https://login.microsoftonline.com/{conta.get('tenant') or 'common'}",
        token_cache=cache,
    )

    def salvar_cache():
        if cache.has_state_changed:
            texto = cache.serialize()
            tp.parent.mkdir(parents=True, exist_ok=True)
            tp.write_text(texto, encoding="utf-8")
            try:
                os.chmod(tp, 0o600)
            except OSError:
                pass

    return app, salvar_cache


def graph_token(conta: dict, cfg: dict, interativo: bool = True):
    """Devolve o access token ou None (modo silencioso)."""
    app, salvar_cache = graph_app(conta, cfg)
    contas = app.get_accounts()
    alvo = None
    if conta.get("conta"):
        alvo = next((a for a in contas if sem_acento(a["username"]) == sem_acento(conta["conta"])), None)
    alvo = alvo or (contas[0] if contas else None)
    res = app.acquire_token_silent(SCOPES, account=alvo) if alvo else None
    if not res:
        if not interativo:
            return None
        fluxo = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in fluxo:
            sys.exit(f"[erro] device flow falhou: {fluxo}")
        print(f"\n>>> {conta['nome']}: abra https://microsoft.com/devicelogin e digite o código "
              f"{fluxo['user_code']}"
              f"\n    entre com {conta.get('conta') or 'a conta Microsoft'}"
              f"\n    (o código vale {fluxo.get('expires_in', 900) // 60} minutos)\n", flush=True)
        res = app.acquire_token_by_device_flow(fluxo)
        salvar_cache()
    if not res or "access_token" not in res:
        erro = (res or {}).get("error_description") or (res or {}).get("error") or "falhou"
        sys.exit(f"[erro] login de '{conta['nome']}' falhou:\n      {erro[:400]}")
    salvar_cache()
    return res["access_token"]


def graph_req(token: str, caminho: str, metodo: str = "GET", payload=None, headers=None):
    import requests
    hdrs = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    hdrs.update(headers or {})
    url = caminho if caminho.startswith("http") else GRAPH + caminho
    r = requests.request(metodo, url, headers=hdrs, json=payload, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"Graph {r.status_code} em {caminho}: {r.text[:400]}")
    if r.status_code == 204 or not r.content:
        return {}
    return r.json()


def parse_graph_dt(bruto: str, cfg: dict) -> datetime:
    """Datas do Graph: com 'Z' (UTC) ou sem fuso (já no fuso pedido)."""
    tz = zona(cfg.get("timezone", TZ_LOCAL))
    txt = (bruto or "").strip()
    if not txt:
        raise ValueError("data vazia")
    limpo = txt.replace("Z", "") if txt.endswith("Z") else txt
    limpo = re.sub(r"\.\d+$", "", limpo)
    dt = datetime.fromisoformat(limpo)
    if txt.endswith("Z"):
        return dt.replace(tzinfo=timezone.utc).astimezone(tz)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


# ------------------------------------------------------------------- eventos

class Evento:
    __slots__ = ("inicio", "fim", "titulo", "local", "origem", "dia_inteiro",
                 "livre", "url", "online")

    def __init__(self, inicio, fim, titulo, local="", origem="", dia_inteiro=False,
                 livre=False, url="", online=False):
        self.inicio = inicio
        self.fim = fim
        self.titulo = titulo or "(sem título)"
        self.local = local or ""
        self.origem = origem
        self.dia_inteiro = dia_inteiro
        self.livre = livre
        self.url = url or ""
        self.online = online

    @property
    def dia(self) -> date:
        return self.inicio.date()

    @property
    def chave(self):
        return (self.inicio, self.fim, sem_acento(self.titulo).strip())

    def __repr__(self):
        return f"<{fmt_dia(self.dia)} {fmt_hora(self.inicio.time())} {self.titulo} [{self.origem}]>"


def eventos_graph(conta: dict, cfg: dict, de: datetime, ate: datetime, token: str) -> list[Evento]:
    q = (f"/me/calendarView?startDateTime={de.strftime('%Y-%m-%dT%H:%M:%S')}"
         f"&endDateTime={ate.strftime('%Y-%m-%dT%H:%M:%S')}"
         "&$select=subject,start,end,isAllDay,location,showAs,webLink,isCancelled,onlineMeeting"
         "&$orderby=start/dateTime&$top=250")
    dados = graph_req(token, q, headers={"Prefer": f'outlook.timezone="{cfg.get("timezone_graph")}"'})
    saida = []
    for i in dados.get("value", []):
        if i.get("isCancelled"):
            continue
        inicio = parse_graph_dt((i.get("start") or {}).get("dateTime"), cfg)
        fim = parse_graph_dt((i.get("end") or {}).get("dateTime"), cfg)
        saida.append(Evento(
            inicio, fim, i.get("subject") or "(sem título)",
            local=(i.get("location") or {}).get("displayName") or "",
            origem=conta["nome"],
            dia_inteiro=bool(i.get("isAllDay")),
            livre=(i.get("showAs") in ("free", "workingElsewhere")) or bool(i.get("isAllDay")),
            url=i.get("webLink") or "",
            online=bool(i.get("onlineMeeting")),
        ))
    return saida


def baixar_ics(url: str) -> str:
    import requests
    if url.startswith("webcal://"):
        url = "https://" + url[len("webcal://"):]
    r = requests.get(url, timeout=90, headers={"User-Agent": "terras-agenda/1.0"})
    r.raise_for_status()
    return r.text


def eventos_ics(feed: dict, cfg: dict, de: datetime, ate: datetime) -> list[Evento]:
    import icalendar
    import recurring_ical_events
    tz = zona(cfg.get("timezone", TZ_LOCAL))
    texto = baixar_ics(feed["url"])
    cal = icalendar.Calendar.from_ical(texto)
    componentes = recurring_ical_events.of(cal).between(de, ate)
    saida = []
    for c in componentes:
        if str(c.get("STATUS", "")).upper() == "CANCELLED":
            continue
        bruto = c.get("DTSTART")
        if bruto is None:
            continue
        dt = bruto.dt
        dia_inteiro = isinstance(dt, date) and not isinstance(dt, datetime)
        if dia_inteiro:
            inicio = datetime.combine(dt, time(0, 0), tzinfo=tz)
            fim_bruto = c.get("DTEND") or c.get("DURATION")
            fim_dt = fim_bruto.dt if fim_bruto is not None and hasattr(fim_bruto, "dt") else None
            if isinstance(fim_dt, date) and not isinstance(fim_dt, datetime):
                fim = datetime.combine(fim_dt, time(0, 0), tzinfo=tz)
            elif isinstance(fim_dt, datetime):
                fim = _para_local(fim_dt, tz)
            else:
                fim = inicio + timedelta(days=1)
        else:
            inicio = _para_local(dt, tz)
            fim_dt = None
            bruto_fim = c.get("DTEND")
            if bruto_fim is not None and hasattr(bruto_fim, "dt"):
                fim_dt = bruto_fim.dt
            if isinstance(fim_dt, datetime):
                fim = _para_local(fim_dt, tz)
            else:
                dur = c.get("DURATION")
                if dur is not None and getattr(dur, "dt", None):
                    fim = inicio + dur.dt
                else:
                    fim = inicio + timedelta(hours=1)
        transp = str(c.get("TRANSP", "")).upper()
        local = str(c.get("LOCATION", "") or "")
        saida.append(Evento(
            inicio, fim, str(c.get("SUMMARY", "") or "(sem título)"),
            local=local, origem=feed["nome"], dia_inteiro=dia_inteiro,
            livre=(transp == "TRANSPARENT"),
            url=str(c.get("URL", "") or ""),
        ))
    return saida


def _para_local(dt: datetime, tz) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def coletar(cfg: dict, de: datetime, ate: datetime, so_contas=None, so_feeds=None):
    """Devolve (eventos, avisos). Cada fonte que falha vira aviso, não erro."""
    tz = zona(cfg.get("timezone", TZ_LOCAL))
    de = de.astimezone(tz)
    ate = ate.astimezone(tz)
    eventos, avisos = [], []

    for conta in cfg.get("contas", []):
        if so_contas and sem_acento(conta["nome"]) not in [sem_acento(x) for x in so_contas]:
            continue
        if not conta.get("client_id"):
            continue
        try:
            token = graph_token(conta, cfg, interativo=False)
            if not token:
                avisos.append(f"{conta['nome']}: sem login (rode: terras_agenda.py auth --conta {conta['nome']})")
                continue
            eventos += eventos_graph(conta, cfg, de, ate, token)
        except SystemExit as e:
            avisos.append(f"{conta['nome']}: {e}")
        except Exception as e:  # noqa: BLE001
            avisos.append(f"{conta['nome']}: {str(e)[:200]}")

    for feed in cfg.get("feeds", []):
        if so_feeds and sem_acento(feed["nome"]) not in [sem_acento(x) for x in so_feeds]:
            continue
        if not feed.get("url"):
            continue
        try:
            eventos += eventos_ics(feed, cfg, de, ate)
        except Exception as e:  # noqa: BLE001
            avisos.append(f"{feed['nome']} (ics): {str(e)[:200]}")

    eventos.sort(key=lambda e: (e.inicio, e.titulo))
    return eventos, avisos


def fundir_repetidos(eventos: list[Evento]) -> list[Evento]:
    """Mesmo horário e mesmo título em agendas diferentes = uma linha só."""
    por_chave: dict = {}
    ordem = []
    for e in eventos:
        k = e.chave
        if k in por_chave:
            atual = por_chave[k]
            if e.origem not in atual.origem.split("+"):
                atual.origem = atual.origem + "+" + e.origem
            atual.online = atual.online or e.online
            atual.local = atual.local or e.local
        else:
            por_chave[k] = e
            ordem.append(k)
    return [por_chave[k] for k in ordem]


def conflitos(eventos: list[Evento]) -> list[tuple[Evento, Evento]]:
    reais = [e for e in eventos if not e.dia_inteiro and not e.livre]
    reais.sort(key=lambda e: e.inicio)
    saida = []
    for i, a in enumerate(reais):
        for b in reais[i + 1:]:
            if b.inicio >= a.fim:
                break
            if sem_acento(a.titulo).strip() == sem_acento(b.titulo).strip():
                continue
            saida.append((a, b))
    return saida


# ------------------------------------------------------------------- saída

def linhas_por_dia(eventos: list[Evento], conflitantes: set) -> list[str]:
    por_dia: dict = {}
    for e in eventos:
        por_dia.setdefault(e.dia, []).append(e)
    linhas = []
    for dia in sorted(por_dia):
        linhas.append("")
        linhas.append(f"  {fmt_dia(dia)}")
        for e in sorted(por_dia[dia], key=lambda x: (not x.dia_inteiro, x.inicio)):
            marca = "⚠ " if e in conflitantes else "  "
            if e.dia_inteiro:
                quando = "dia inteiro"
            else:
                quando = f"{fmt_hora(e.inicio.time())}–{fmt_hora(e.fim.time())}"
                if e.fim.date() > e.inicio.date():
                    quando += f" (+{(e.fim.date() - e.inicio.date()).days}d)"
            extras = []
            if e.local:
                extras.append(e.local)
            if e.online:
                extras.append("online")
            if e.livre and not e.dia_inteiro:
                extras.append("livre")
            sufixo = ("  ·  " + " · ".join(extras)) if extras else ""
            linhas.append(f"{marca}{quando:>16}  {e.titulo[:64]:<64} [{e.origem}]{sufixo}")
    return linhas


def imprimir_agenda(eventos, conflitantes, avisos, titulo):
    print(f"\n{titulo}")
    print("  " + "─" * 76)
    if not eventos:
        print("  nada na agenda neste período.")
    else:
        print("\n".join(linhas_por_dia(eventos, conflitantes)))
    if conflitantes:
        print("\n  ⚠ = horário sobreposto com outro compromisso (veja: conflitos)")
    if avisos:
        print("\n  fontes com problema:")
        for a in avisos:
            print(f"    · {a}")
    print()


def iso(e: Evento) -> dict:
    return {
        "inicio": e.inicio.isoformat(),
        "fim": e.fim.isoformat(),
        "titulo": e.titulo,
        "local": e.local,
        "origem": e.origem,
        "dia_inteiro": e.dia_inteiro,
        "livre": e.livre,
        "url": e.url,
        "online": e.online,
    }


# ------------------------------------------------------------------ comandos

def cmd_check(args):
    print("\nterras-agenda — diagnóstico\n" + "─" * 60)
    cfg = carregar_config()

    print(f"  config      : {CONFIG_PATH} {'ok' if CONFIG_PATH.exists() else 'AUSENTE (usando padrão)'}")
    print(f"  venv        : {'ok' if VENV_PYTHON.exists() else 'AUSENTE — rode setup.sh'}")
    try:
        import msal, icalendar, recurring_ical_events, requests  # noqa: F401
        print("  dependências: ok (msal, icalendar, recurring-ical-events, requests)")
    except ImportError as e:
        print(f"  dependências: FALTA {e.name} — rode setup.sh")

    print(f"  fuso        : {cfg.get('timezone')} (Graph: {cfg.get('timezone_graph')})")

    print("\n  contas Microsoft")
    if not cfg.get("contas"):
        print("    (nenhuma)")
    for c in cfg.get("contas", []):
        estado = "sem app no tenant" if not c.get("client_id") else "?"
        if c.get("client_id"):
            try:
                token = graph_token(c, cfg, interativo=False)
                estado = "login ok" if token else "sem login (rode: auth --conta " + c["nome"] + ")"
            except SystemExit as e:
                estado = str(e)[:60]
        conta = f"  ({c['conta']})" if c.get("conta") else ""
        print(f"    {c['nome']:<10} {c.get('tenant','')[:36]:<38}{conta:<44} {estado}")

    print("\n  feeds .ics")
    if not cfg.get("feeds"):
        print("    (nenhum)")
    for f in cfg.get("feeds", []):
        print(f"    {f['nome']:<20} {'configurado' if f.get('url') else 'SEM URL (adicione com: feeds add)'}")

    print("\n  Como fechar as lacunas, em ordem de retorno:")
    print("    1. SLC (tenant próprio)  → auth --conta SLC          [leitura+escrita]")
    print("    2. Google (qualquer conta) → feeds add --nome Google --url <endereço iCal secreto>")
    print("    3. ISO / THG              → feeds add com o .ics publicado, ou app no tenant deles")
    print()


def cmd_auth(args):
    cfg = carregar_config()
    conta = conta_por_nome(cfg, args.conta)
    if not conta.get("client_id"):
        sys.exit(f"[erro] '{conta['nome']}' não tem client_id. Registre um app no tenant "
                 f"{conta.get('tenant')} (veja INSTALL na SKILL.md) ou use um feed .ics.")
    token = graph_token(conta, cfg, interativo=True)
    if token:
        try:
            eu = graph_req(token, "/me?$select=displayName,mail,userPrincipalName")
            print(f"\n[ok] {conta['nome']} autenticada como {eu.get('displayName')} "
                  f"<{eu.get('userPrincipalName') or eu.get('mail')}>")
        except Exception as e:  # noqa: BLE001
            print(f"\n[ok] token obtido, mas /me falhou: {e}")
        try:
            cals = graph_req(token, "/me/calendars?$select=name,canEdit,owner")
            print("\n  calendários nesta conta:")
            for c in cals.get("value", []):
                dono = (c.get("owner") or {}).get("address") or ""
                print(f"    · {c.get('name')}  {'(edição)' if c.get('canEdit') else '(leitura)'} {dono}")
        except Exception as e:  # noqa: BLE001
            print(f"  (não consegui listar calendários: {str(e)[:160]})")
    print()


def cmd_contas(args):
    cfg = carregar_config()
    if args.add:
        nome, tenant = args.add, args.tenant or ""
        if not tenant:
            sys.exit("[erro] informe --tenant <id ou domínio>. Ex.: --tenant iso5geducacional.com.br")
        cfg["contas"] = [c for c in cfg["contas"] if sem_acento(c["nome"]) != sem_acento(nome)]
        cfg["contas"].append({"nome": nome, "tenant": tenant, "client_id": args.client_id or "",
                              "conta": args.conta or "", "cor": args.cor or ""})
        salvar_json(CONFIG_PATH, cfg)
        print(f"[ok] conta '{nome}' adicionada (tenant {tenant}).")
    print("\n  contas configuradas")
    for c in cfg.get("contas", []):
        print(f"    {c['nome']:<10} tenant {c.get('tenant',''):<38} client_id {'sim' if c.get('client_id') else 'NÃO'}"
              f"  {c.get('conta','')}")
    print()


def cmd_feeds(args):
    cfg = carregar_config()
    if args.acao == "add":
        if not args.nome or not args.url:
            sys.exit("[erro] use: feeds add --nome Google --url https://.../basic.ics")
        cfg["feeds"] = [f for f in cfg["feeds"] if sem_acento(f["nome"]) != sem_acento(args.nome)]
        cfg["feeds"].append({"nome": args.nome, "url": args.url, "cor": args.cor or ""})
        salvar_json(CONFIG_PATH, cfg)
        print(f"[ok] feed '{args.nome}' salvo. testando…")
        try:
            agora = agora_local(cfg)
            evs = eventos_ics({"nome": args.nome, "url": args.url}, cfg,
                              agora - timedelta(days=1), agora + timedelta(days=30))
            print(f"     ok — {len(evs)} evento(s) nos próximos 30 dias.")
        except Exception as e:  # noqa: BLE001
            print(f"     [atenção] não consegui ler o feed agora: {str(e)[:300]}\n"
                  f"     a URL pode estar errada ou exigir login. O feed ficou salvo mesmo assim.")
    elif args.acao == "rm":
        if not args.nome:
            sys.exit("[erro] use: feeds rm --nome Google")
        antes = len(cfg["feeds"])
        cfg["feeds"] = [f for f in cfg["feeds"] if sem_acento(f["nome"]) != sem_acento(args.nome or "")]
        salvar_json(CONFIG_PATH, cfg)
        print(f"[ok] removido ({antes - len(cfg['feeds'])}).")
    print("\n  feeds .ics")
    if not cfg["feeds"]:
        print("    (nenhum) — adicione o do Google com: feeds add --nome Google --url <url>")
    for f in cfg["feeds"]:
        print(f"    {f['nome']:<20} {f['url'][:70]}")
    print()


def _janela(args, cfg):
    agora = agora_local(cfg)
    if getattr(args, "de", None):
        de = _parse_data_hora(args.de, cfg)
        de = de.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        de = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    dias = getattr(args, "dias", None) or cfg.get("dias_padrao", 7)
    return agora, de, de + timedelta(days=dias)


def cmd_agenda(args):
    cfg = carregar_config()
    agora, de, ate = _janela(args, cfg)
    eventos, avisos = coletar(cfg, de, ate, args.conta, args.feed)
    eventos = fundir_repetidos(eventos)
    if not args.livres:
        eventos = [e for e in eventos if not (e.livre and not e.dia_inteiro)]
    confl = conflitos(eventos)
    marcados = {e for par in confl for e in par}
    if args.json:
        print(json.dumps({"de": de.isoformat(), "ate": ate.isoformat(),
                          "eventos": [iso(e) for e in eventos],
                          "conflitos": [[iso(a), iso(b)] for a, b in confl],
                          "avisos": avisos}, ensure_ascii=False, indent=2))
        return
    titulo = f"  AGENDA  {fmt_dia(de.date())} → {fmt_dia((ate - timedelta(days=1)).date())}"
    imprimir_agenda(eventos, marcados, avisos, titulo)
    if confl:
        print(f"  {len(confl)} choque(s) de horário. Detalhe: conflitos\n")


def cmd_hoje(args):
    cfg = carregar_config()
    agora = agora_local(cfg)
    de = agora.replace(hour=0, minute=0, second=0, microsecond=0)
    eventos, avisos = coletar(cfg, de, de + timedelta(days=1))
    eventos = fundir_repetidos(eventos)
    if not args.livres:
        eventos = [e for e in eventos if not (e.livre and not e.dia_inteiro)]
    confl = conflitos(eventos)
    marcados = {e for par in confl for e in par}

    if args.json:
        print(json.dumps({"agora": agora.isoformat(), "eventos": [iso(e) for e in eventos],
                          "conflitos": [[iso(a), iso(b)] for a, b in confl],
                          "avisos": avisos}, ensure_ascii=False, indent=2))
        return

    imprimir_agenda(eventos, marcados, avisos, f"  HOJE  {fmt_dia(de.date())}  ({DIAS_LONGO[de.weekday()]})")

    reais = [e for e in eventos if not e.dia_inteiro]
    agora_ok = [e for e in reais if e.inicio <= agora <= e.fim]
    proximo = next((e for e in reais if e.inicio > agora), None)
    if agora_ok:
        for e in agora_ok:
            print(f"  ▶ agora: {e.titulo} [{e.origem}] até {fmt_hora(e.fim.time())}")
    if proximo:
        delta = proximo.inicio - agora
        mins = int(delta.total_seconds() // 60)
        quando = f"em {mins} min" if mins < 90 else f"às {fmt_hora(proximo.inicio.time())}"
        print(f"  → a seguir: {proximo.titulo} [{proximo.origem}] {quando}")
    if not reais:
        print("  sem compromissos com hora hoje.")
    amanha = coletar(cfg, de + timedelta(days=1), de + timedelta(days=2))[0]
    amanha = fundir_repetidos(amanha)
    if amanha:
        print(f"\n  amanhã ({DIAS_LONGO[(de + timedelta(days=1)).weekday()]}): "
              f"{len(amanha)} compromisso(s) — o primeiro '{amanha[0].titulo}' às "
              f"{'dia inteiro' if amanha[0].dia_inteiro else fmt_hora(amanha[0].inicio.time())}")
    if confl:
        print(f"\n  ⚠ {len(confl)} choque(s) de horário hoje:")
        for a, b in confl:
            print(f"    {fmt_hora(a.inicio.time())}–{fmt_hora(a.fim.time())}  '{a.titulo}' [{a.origem}]"
                  f"  ×  '{b.titulo}' [{b.origem}]")
    print()


def cmd_conflitos(args):
    cfg = carregar_config()
    agora, de, ate = _janela(args, cfg)
    eventos, avisos = coletar(cfg, de, ate, args.conta, args.feed)
    eventos = fundir_repetidos(eventos)
    confl = conflitos(eventos)
    if args.json:
        print(json.dumps({"conflitos": [[iso(a), iso(b)] for a, b in confl],
                          "avisos": avisos}, ensure_ascii=False, indent=2))
        return
    print(f"\n  CHOQUES DE HORÁRIO  {fmt_dia(de.date())} → {fmt_dia((ate - timedelta(days=1)).date())}")
    print("  " + "─" * 76)
    if not confl:
        print("  nenhum. As agendas não se atropelam neste período.")
    for a, b in confl:
        print(f"\n  ⚠ {fmt_dia(a.dia)}  {fmt_hora(a.inicio.time())}–{fmt_hora(a.fim.time())}")
        print(f"      {a.titulo}  [{a.origem}]")
        print(f"      {b.titulo}  [{b.origem}]")
    if avisos:
        print("\n  fontes com problema:")
        for a in avisos:
            print(f"    · {a}")
    print()


def _parse_data_hora(txt: str, cfg: dict) -> datetime:
    tz = zona(cfg.get("timezone", TZ_LOCAL))
    agora = datetime.now(tz)
    t = txt.strip().lower()
    if not t:
        raise ValueError("vazio")
    if t in ("agora",):
        return agora
    m = re.match(r"^(hoje|amanha|amanhã|depois de amanha)\s*(\d{1,2})[:h]?(\d{2})?$", t)
    if m:
        base = agora
        if m.group(1).startswith("aman"):
            base = agora + timedelta(days=1)
        elif m.group(1).startswith("depois"):
            base = agora + timedelta(days=2)
        return base.replace(hour=int(m.group(2)), minute=int(m.group(3) or 0), second=0, microsecond=0)
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?$", t)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        a = int(m.group(3)) if m.group(3) else agora.year
        if a < 100:
            a += 2000
        return datetime(a, mo, d, 0, 0, tzinfo=tz)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", t)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 0, 0, tzinfo=tz)
    m = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\s*(\d{1,2})[:h]?(\d{2})?$", t)
    if m:
        d, mo = int(m.group(1)), int(m.group(2))
        a = int(m.group(3)) if m.group(3) else agora.year
        if a < 100:
            a += 2000
        return datetime(a, mo, d, int(m.group(4)), int(m.group(5) or 0), tzinfo=tz)
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})[t ]?(\d{1,2})?:?(\d{2})?$", t)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        int(m.group(4) or 0), int(m.group(5) or 0), tzinfo=tz)
    m = re.match(r"^(\d{1,2})[:h](\d{2})$", t)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        base = agora.replace(hour=h, minute=mi, second=0, microsecond=0)
        if base < agora - timedelta(hours=1):
            base += timedelta(days=1)
        return base
    raise ValueError(f"não entendi a data/hora: {txt!r}. Use 'hoje 14:30', 'amanha 9h', "
                     f"'23/09 14:00' ou '2026-09-23 14:00'")


def cmd_criar(args):
    cfg = carregar_config()
    nome = args.conta or cfg.get("conta_padrao") or (cfg["contas"][0]["nome"] if cfg.get("contas") else None)
    if not nome:
        sys.exit("[erro] nenhuma conta configurada.")
    conta = conta_por_nome(cfg, nome)

    inicio = _parse_data_hora(args.inicio, cfg)
    if args.fim:
        fim = _parse_data_hora(args.fim, cfg)
        if fim <= inicio:
            fim = fim + timedelta(days=1)
    else:
        fim = inicio + timedelta(hours=1)

    eventos = {
        "subject": args.titulo,
        "start": {"dateTime": inicio.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": cfg.get("timezone_graph")},
        "end": {"dateTime": fim.strftime("%Y-%m-%dT%H:%M:%S"), "timeZone": cfg.get("timezone_graph")},
    }
    if args.local:
        eventos["location"] = {"displayName": args.local}
    if args.corpo:
        eventos["body"] = {"contentType": "HTML", "content": args.corpo}
    if args.dia_inteiro:
        eventos["isAllDay"] = True
        eventos["start"] = {"dateTime": inicio.strftime("%Y-%m-%dT00:00:00"), "timeZone": cfg.get("timezone_graph")}
        eventos["end"] = {"dateTime": (fim + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00"),
                          "timeZone": cfg.get("timezone_graph")}

    participantes = [p.strip() for p in (args.participantes or "").split(",") if p.strip()]
    if participantes:
        eventos["attendees"] = [{"emailAddress": {"address": p}, "type": "required"} for p in participantes]

    aviso = ""
    if args.dia_inteiro:
        aviso = "dia inteiro"
    eu = inicio.strftime("%d/%m %H:%M") + "–" + fim.strftime("%H:%M")
    print(f"\n  criar em {conta['nome']} ({conta.get('conta') or 'conta logada'}):")
    print(f"    {args.titulo}")
    print(f"    {eu}{'  (' + aviso + ')' if aviso else ''}")
    if args.local:
        print(f"    local: {args.local}")
    if participantes:
        print(f"    convidados (recebem convite): {', '.join(participantes)}")

    if args.simular:
        print("\n  [simulação] nada foi criado.\n")
        return

    if participantes and not args.yes:
        sys.exit("\n[erro] com convidados, o Graph manda convite de verdade. "
                 "Confirme com --yes (ou tire --participantes).")

    token = graph_token(conta, cfg, interativo=True)
    criado = graph_req(token, "/me/events", metodo="POST", payload=eventos)
    print(f"\n[ok] criado. {criado.get('webLink','')}\n")


def cmd_exportar(args):
    cfg = carregar_config()
    agora, de, ate = _janela(args, cfg)
    eventos, avisos = coletar(cfg, de, ate, args.conta, args.feed)
    eventos = fundir_repetidos(eventos)
    saida = Path(args.arquivo).expanduser()
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//terras-agenda//PT-BR",
         "CALSCALE:GREGORIAN", "X-WR-CALNAME:Agenda unificada"]
    for e in eventos:
        f = "%Y%m%d" if e.dia_inteiro else "%Y%m%dT%H%M%S"
        L += ["BEGIN:VEVENT",
              f"UID:{abs(hash(e.chave))}@terras-agenda",
              f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
              f"DTSTART;TZID={cfg.get('timezone')}:{e.inicio.strftime(f)}",
              f"DTEND;TZID={cfg.get('timezone')}:{e.fim.strftime(f)}",
              f"SUMMARY:{e.titulo} [{e.origem}]",
              f"LOCATION:{e.local}" if e.local else "LOCATION:",
              "END:VEVENT"]
    L.append("END:VCALENDAR")
    saida.write_text("\r\n".join(L) + "\r\n", encoding="utf-8")
    print(f"[ok] {len(eventos)} evento(s) em {saida}")
    if avisos:
        print("  fontes com problema: " + "; ".join(avisos))
    print()


# --------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(prog="terras_agenda.py", description="Agenda unificada")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="o que falta para funcionar").set_defaults(func=cmd_check)

    a = sub.add_parser("auth", help="login Microsoft por código de dispositivo")
    a.add_argument("--conta", required=True, help="nome da conta na config (ex.: SLC)")
    a.set_defaults(func=cmd_auth)

    c = sub.add_parser("contas", help="listar/adicionar contas Microsoft")
    c.add_argument("--add", help="nome da conta (ex.: ISO)")
    c.add_argument("--tenant", help="id ou domínio do tenant")
    c.add_argument("--client-id", dest="client_id", help="client_id do app nesse tenant")
    c.add_argument("--conta", help="e-mail da conta")
    c.add_argument("--cor", help="cor para identificação")
    c.set_defaults(func=cmd_contas)

    f = sub.add_parser("feeds", help="feeds .ics (Google, calendário publicado)")
    f.add_argument("acao", nargs="?", default="list", choices=["list", "add", "rm"])
    f.add_argument("--nome")
    f.add_argument("--url")
    f.add_argument("--cor")
    f.set_defaults(func=cmd_feeds)

    def comuns(sp):
        sp.add_argument("--dias", type=int, help="quantos dias a partir de hoje")
        sp.add_argument("--de", help="data inicial (23/09 ou 2026-09-23)")
        sp.add_argument("--conta", action="append", help="só esta conta (repetível)")
        sp.add_argument("--feed", action="append", help="só este feed (repetível)")
        sp.add_argument("--livres", action="store_true", help="incluir eventos marcados como livres")
        sp.add_argument("--json", action="store_true", help="saída em JSON")

    g = sub.add_parser("agenda", help="agenda unificada")
    comuns(g)
    g.set_defaults(func=cmd_agenda)

    h = sub.add_parser("hoje", help="hoje + o que vem + conflitos")
    h.add_argument("--livres", action="store_true")
    h.add_argument("--json", action="store_true")
    h.set_defaults(func=cmd_hoje)

    k = sub.add_parser("conflitos", help="só os choques de horário entre agendas")
    comuns(k)
    k.set_defaults(func=cmd_conflitos)

    cr = sub.add_parser("criar", help="criar evento numa conta Microsoft")
    cr.add_argument("--titulo", required=True)
    cr.add_argument("--inicio", required=True, help="'hoje 14:30', 'amanha 9h', '23/09 14:00'")
    cr.add_argument("--fim", help="padrão: 1h depois")
    cr.add_argument("--conta", help="em qual conta (padrão: conta_padrao da config)")
    cr.add_argument("--local")
    cr.add_argument("--corpo", help="descrição (HTML aceito)")
    cr.add_argument("--participantes", help="e-mails separados por vírgula (manda convite!)")
    cr.add_argument("--dia-inteiro", dest="dia_inteiro", action="store_true")
    cr.add_argument("--simular", action="store_true", help="só mostra, não cria")
    cr.add_argument("--yes", action="store_true", help="confirma envio de convites")
    cr.set_defaults(func=cmd_criar)

    ex = sub.add_parser("exportar", help="gera um .ics com a agenda unificada")
    comuns(ex)
    ex.add_argument("--arquivo", default="~/agenda-unificada.ics")
    ex.set_defaults(func=cmd_exportar)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

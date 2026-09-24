#!/usr/bin/env python3
"""terras-notas — NFS-e da Fênix: baixa, analisa, casa o destinatário no de-para
e envia pelo Outlook (Microsoft Graph).

Uso: python3 ~/.zcode/skills/terras-notas/scripts/terras_notas.py <comando> [opções]

Comandos: check, auth, descobrir-remetente, fetch, parse, depara, match,
despachar, status, run. Ações externas (criar rascunho, enviar e-mail) exigem
flags explícitas (--rascunho / --enviar --yes).
"""

from __future__ import annotations

import argparse
import base64
import csv
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timedelta, timezone
from html import escape as html_escape
from pathlib import Path

SKILL_HOME = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_HOME / "assets"
ASSINATURA_PADRAO = ASSETS_DIR / "assinatura.png"
CONFIG_DIR = Path(os.environ.get("TERRAS_NOTAS_CONFIG_DIR", "~/.config/terras-notas")).expanduser()
CONFIG_PATH = CONFIG_DIR / "config.json"
DEPARA_PATH = CONFIG_DIR / "depara.csv"
TOKEN_PATH = CONFIG_DIR / "token.json"
VENV_PYTHON = CONFIG_DIR / "venv/bin/python"

GRAPH = "https://graph.microsoft.com/v1.0"
# offline_access/openid/profile são reservados: o MSAL adiciona sozinho.
SCOPES = ["Mail.ReadWrite", "Mail.Send"]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CNPJ_RE = re.compile(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")


# ---------------------------------------------------------------- utilidades

def agora() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def norm(txt: str) -> str:
    """Maiúsculas sem acento, só letras e números separadas por espaço."""
    txt = unicodedata.normalize("NFD", txt or "")
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = re.sub(r"[^A-Za-z0-9]+", " ", txt.upper())
    return re.sub(r"\s+", " ", txt).strip()


def so_digitos(txt: str) -> str:
    return re.sub(r"\D", "", txt or "")


def moeda_para_float(txt: str):
    if not txt:
        return None
    txt = txt.strip().replace(".", "").replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return None


def carregar_json(caminho: Path, default):
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    return default


def salvar_json(caminho: Path, dados) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def garantir_600(caminho: Path) -> None:
    if caminho.exists():
        os.chmod(caminho, 0o600)


class SafeDict(dict):
    def __missing__(self, chave):
        return "{" + chave + "}"


def renderizar(template: str, campos: dict) -> str:
    return (template or "").format_map(SafeDict(campos))


def tocar_arquivo_dados(caminho: Path):
    """Cria com permissão restrita antes de escrever conteúdo sensível."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not caminho.exists():
        caminho.touch(mode=0o600)
    else:
        garantir_600(caminho)


# ---------------------------------------------------------------- config/estado

def carregar_config() -> dict:
    cfg = carregar_json(CONFIG_PATH, {})
    padrao = {
        "client_id": "",
        "tenant": "common",
        "remetentes_fenix": ["fenix"],
        "busca_termos": ["fenix", "assessoria", "92010-0625"],
        "fetch_janela_dias": 90,
        "notas_dir": "~/Documents/SLC",
        "assessoria_nome": "Fênix Assessoria",
        "assessoria_email": "",
        # Parâmetros de emissão do prestador (extraídos das NFS-e reais de SJC).
        # Usados na `pedido ficha`, que é o roteiro de preenchimento no portal.
        "emissao": {
            "codigo_servico": "08.02",
            "codigo_servico_texto": "INSTRUÇÃO, TREINAMENTO, ORIENTAÇÃO PEDAGOGICA E EDUCACIONAL, "
                                    "AVALIAÇÃO DE CONHECIMENTOS DE",
            "cnae": "859960300 - TREINAMENTO EM INFORMÁTICA",
            "municipio_incidencia": "SAO JOSE DOS CAMPOS - SP",
            "responsavel_issqn": "PRESTADOR",
            "regime": "Simples Nacional (optante ME/EPP)",
        },
        "pedido_assunto_template": "Solicitação de NFS-e {competencia} — {quantidade} nota(s)",
        "pedido_corpo_template": (
            "Olá,\n\n"
            "Segue a solicitação de emissão das notas da competência {competencia}:\n\n"
            "{itens}\n\n"
            "Por favor, ao emitir, me enviem os PDFs para eu encaminhar aos clientes.\n\n"
            "Qualquer dúvida, fico à disposição."),
        "email_assinatura": "Everton Lima\nSOUSA LIMA INFORMATICA LTDA\n(11) 9171-3559",
        "assinatura_imagem": "",
        "assunto_template": "NFS-e {numero}/{serie} — Sousa Lima Informática",
        "corpo_template": (
            "Olá,\n\n"
            "Segue em anexo a Nota Fiscal de Serviços eletrônica "
            "{numero}/{serie}, competência {competencia}, "
            "no valor de R$ {valor_total}.\n\n"
            "Qualquer dúvida estamos à disposição.\n\n"
            "Atenciosamente,\n{assinatura}"
        ),
    }
    merged = {**padrao, **cfg}
    for chave in ("remetentes_fenix", "busca_termos"):
        if isinstance(merged.get(chave), str):
            merged[chave] = [merged[chave]]
    return merged


def notas_dir(cfg: dict) -> Path:
    return Path(cfg["notas_dir"]).expanduser()


def state_path(cfg: dict) -> Path:
    return notas_dir(cfg) / ".terras-notas" / "state.json"


def carregar_state(cfg: dict) -> dict:
    st = carregar_json(state_path(cfg), {})
    st.setdefault("mensagens", {})   # message-id -> {assunto, recebido_em, anexos}
    st.setdefault("notas", {})       # arquivo -> dados da nota
    st.setdefault("despachos", {})   # "numero/serie" -> {email, modo, enviado_em}
    return st


def salvar_state(cfg: dict, st: dict) -> None:
    salvar_json(state_path(cfg), st)


def chave_nota(nota: dict) -> str:
    return f"{nota.get('numero')}/{nota.get('serie')}"


def alerta_janela(janela: str, dia: int):
    """None se ok (ou sem janela); mensagem quando o dia está fora da janela preferida."""
    m = re.fullmatch(r"(\d{1,2})\s*-\s*(\d{1,2})", (janela or "").strip())
    if not m:
        return None
    inicio, fim = int(m.group(1)), int(m.group(2))
    if inicio <= dia <= fim:
        return None
    return (f"hoje é dia {dia}, fora da janela preferida de envio ({inicio}–{fim} do mês) "
            "definida para este cliente no de-para")


# ---------------------------------------------------------------- de-para

COLUNAS_DEPARA = ["cnpj", "razao_social", "apelidos", "email", "janela_envio", "endereco", "obs"]


def ler_depara() -> list[dict]:
    if not DEPARA_PATH.exists():
        return []
    with DEPARA_PATH.open(encoding="utf-8") as fh:
        return [dict(linha) for linha in csv.DictReader(fh)]


def gravar_depara(linhas: list[dict]) -> None:
    tocar_arquivo_dados(DEPARA_PATH)
    with DEPARA_PATH.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUNAS_DEPARA)
        writer.writeheader()
        for linha in linhas:
            writer.writerow({c: linha.get(c, "") for c in COLUNAS_DEPARA})


def resolver_destino(nota: dict, depara: list[dict]):
    """Resolve o e-mail de destino de uma nota.

    Ordem: CNPJ no de-para (somado ao e-mail do PDF, quando houver) > e-mail do
    próprio PDF > nome/apelido exato > similaridade (sugerido).
    Devolve dict com email/origem/confianca ou None.
    """
    email_pdf = (nota.get("tomador_email") or "").strip()
    cnpj = so_digitos(nota.get("tomador_cnpj") or "")
    nome = norm(nota.get("tomador_nome") or "")

    linha_cnpj = None
    if cnpj:
        for linha in depara:
            if so_digitos(linha.get("cnpj") or "") == cnpj:
                linha_cnpj = linha
                break

    resultado = None
    if linha_cnpj and (linha_cnpj.get("email") or "").strip():
        # O de-para é curado à mão: manda nele, mas o endereço do PDF também entra.
        emails = [e.strip() for e in re.split(r"[,;]", linha_cnpj["email"]) if e.strip()]
        if email_pdf and email_pdf.lower() not in {e.lower() for e in emails}:
            emails.insert(0, email_pdf)
        resultado = {"email": ";".join(emails),
                     "origem": "depara-cnpj+pdf" if email_pdf else "depara-cnpj",
                     "confianca": "alta"}
    elif email_pdf:
        resultado = {"email": email_pdf, "origem": "pdf", "confianca": "alta"}

    if resultado is None and not nome:
        return None

    if resultado is None:
        melhor, melhor_ratio = None, 0.0
        for linha in depara:
            if not linha.get("email"):
                continue
            candidatos = [norm(linha.get("razao_social") or "")]
            candidatos += [norm(a) for a in re.split(r"[;,]", linha.get("apelidos") or "") if a.strip()]
            for cand in candidatos:
                if not cand:
                    continue
                if cand == nome or (len(cand) >= 6 and cand in nome) or (len(nome) >= 6 and nome in cand):
                    resultado = {"email": linha["email"].strip(), "origem": "depara-nome", "confianca": "alta"}
                    break
                ratio = difflib.SequenceMatcher(None, cand, nome).ratio()
                if ratio > melhor_ratio:
                    melhor, melhor_ratio = linha, ratio
            if resultado:
                break
        if resultado is None and melhor and melhor_ratio >= 0.85:
            resultado = {"email": melhor["email"].strip(), "origem": "sugerido", "confianca": "media",
                         "sugestao_nome": melhor.get("razao_social", "")}

    # Janela preferida de envio acompanha o cliente, venha o e-mail de onde vier.
    if resultado and linha_cnpj:
        janela = (linha_cnpj.get("janela_envio") or "").strip()
        if janela:
            resultado["janela"] = janela
    return resultado


# ---------------------------------------------------------------- parser NFS-e

def extrair_texto_pdf(caminho: Path) -> str:
    """Texto com layout. Tenta pdfplumber; cai para pdftotext -layout."""
    try:
        import pdfplumber
        with pdfplumber.open(str(caminho)) as pdf:
            return "\n".join((pagina.extract_text(layout=True) or "") for pagina in pdf.pages)
    except ImportError:
        pass
    saida = subprocess.run(["pdftotext", "-layout", str(caminho), "-"],
                           capture_output=True, text=True, check=True)
    return saida.stdout


def _secao(texto: str, inicio: str, fim: str) -> str:
    padrao = re.escape(inicio) + r".*?(?=" + re.escape(fim) + r")"
    m = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
    return m.group(0) if m else ""


def _nome_entre_linhas(secao_txt: str, rotulo: str) -> str:
    """Nome na(s) linha(s) após o rótulo, até 'Endereço:'; remove e-mail da coluna direita."""
    linhas = secao_txt.splitlines()
    for i, linha in enumerate(linhas):
        if norm(rotulo) in norm(linha):
            partes = []
            for seguinte in linhas[i + 1:]:
                if norm("Endereço:") in norm(seguinte):
                    break
                limpa = EMAIL_RE.sub("", seguinte).strip(" -:|")
                limpa = re.sub(r"E-?mail\s*:?\s*$", "", limpa, flags=re.IGNORECASE).strip()
                if limpa:
                    partes.append(limpa)
            return " ".join(partes).strip()
    return ""


def parse_nfse(texto: str) -> dict:
    nota: dict = {}

    m = re.search(
        r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\s+(\d{2}/\d{4})\s+(\d+)\s*/\s*(\w+)\s+([A-Za-z0-9]+)\s*$",
        texto, re.MULTILINE)
    if m:
        nota["emissao"], nota["competencia"], numero, serie, nota["codigo_verificacao"] = m.groups()
        nota["numero"] = int(numero)
        nota["serie"] = serie

    emit = _secao(texto, "EMITENTE DA NFS-e", "TOMADOR")
    m = CNPJ_RE.search(emit)
    nota["emitente_cnpj"] = m.group(0) if m else ""
    nota["emitente_nome"] = _nome_entre_linhas(emit, "Nome/Razão Social")
    nota["emitente_email"] = (EMAIL_RE.search(emit).group(0) if EMAIL_RE.search(emit) else "")

    tom = _secao(texto, "TOMADOR DO SERVIÇO", "DESCRIÇÃO DO SERVIÇO")
    m = CNPJ_RE.search(tom)
    nota["tomador_cnpj"] = m.group(0) if m else ""
    nota["tomador_nome"] = _nome_entre_linhas(tom, "Nome/Nome")
    emails_tom = EMAIL_RE.findall(tom)
    nota["tomador_email"] = emails_tom[0] if emails_tom else ""

    # Endereço/município do tomador: a contabilidade precisa deles para emitir.
    m = re.search(r"Endereço:\s*(.+)", tom)
    if m:
        linhas_end = [m.group(1).strip()]
        for seguinte in tom[m.end():].splitlines():
            if re.search(r"(Município\s*/\s*País|CEP|Telefone)", seguinte, re.IGNORECASE):
                break
            if seguinte.strip():
                linhas_end.append(seguinte.strip())
        nota["tomador_endereco"] = " ".join(linhas_end).strip()
    m = re.search(r"([A-ZÀ-Ú][^/\n]*?)\s*/\s*([A-Z]{2})\s*BRASIL", tom)
    if m:
        nota["tomador_municipio"] = m.group(1).strip()
        nota["tomador_uf"] = m.group(2)
    m = re.search(r"\b(\d{5}-\d{3})\b", tom)
    nota["tomador_cep"] = m.group(1) if m else ""

    m = re.search(r"Valor Serviço \(R\$\)\s*[^\n]*\n\s*\**([\d.,]+)", texto)
    nota["valor_servico"] = m.group(1) if m else ""

    # Descrição do serviço: primeira linha útil da seção (serve de padrão no pedido).
    sec = _secao(texto, "DESCRIÇÃO DO SERVIÇO", "DOCUMENTO EMITIDO")
    for linha in sec.splitlines()[1:]:
        if linha.strip():
            nota["descricao_servico"] = linha.strip()
            break
    bloco = _secao(texto, "VALOR TOTAL DA NOTA", "INFORMAÇÕES COMPLEMENTARES")
    m = re.search(r"([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)", bloco)
    if m:
        _, retenções, descontos, líquido = m.groups()
        nota["retencoes"] = retenções
        nota["descontos"] = descontos
        nota["valor_liquido"] = líquido

    m = re.search(r"Número da nota fiscal substituida:\s*(\S+)", texto)
    if m:
        nota["nota_substituida"] = m.group(1)

    nota["valor_total"] = nota.get("valor_servico") or nota.get("valor_liquido") or ""
    nota["parseado_em"] = agora()
    nota["parser"] = "nfse-sjc-v1"
    return nota


def parse_incompleto(nota: dict) -> list[str]:
    faltas = [c for c in ("numero", "tomador_nome", "valor_total") if not nota.get(c)]
    return faltas


# ---------------------------------------------------------------- Microsoft Graph

def _reexec_venv() -> None:
    """Se o msal não existe no Python atual mas o venv tem, reexecuta nele."""
    try:
        import msal  # noqa: F401
        return
    except ImportError:
        pass
    if VENV_PYTHON.exists():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])
    sys.exit("[erro] msal não instalado. Rode: bash ~/.zcode/skills/terras-notas/scripts/setup.sh")


def graph_app():
    _reexec_venv()
    import msal
    cfg = carregar_config()
    if not cfg.get("client_id"):
        sys.exit("[erro] config sem client_id. Siga o INSTALL.md (registro no Entra) e "
                 "edite ~/.config/terras-notas/config.json")
    cache = msal.SerializableTokenCache()
    if TOKEN_PATH.exists():
        cache.deserialize(TOKEN_PATH.read_text(encoding="utf-8"))
    tenant = (cfg.get("tenant") or "common").strip()
    app = msal.PublicClientApplication(cfg["client_id"],
                                       authority=f"https://login.microsoftonline.com/{tenant}",
                                       token_cache=cache)

    def salvar_cache():
        if cache.has_state_changed:
            tocar_arquivo_dados(TOKEN_PATH)
            TOKEN_PATH.write_text(cache.serialize(), encoding="utf-8")
            garantir_600(TOKEN_PATH)

    return app, salvar_cache


def graph_token(interativo: bool = True) -> str:
    app, salvar_cache = graph_app()
    contas = app.get_accounts()
    resultado = app.acquire_token_silent(SCOPES, account=contas[0]) if contas else None
    if not resultado:
        if not interativo:
            sys.exit("[erro] sem token válido. Rode: terras_notas.py auth")
        fluxo = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in fluxo:
            sys.exit(f"[erro] device flow falhou: {fluxo}")
        print(fluxo["message"], flush=True)
        resultado = app.acquire_token_by_device_flow(fluxo)
        salvar_cache()
    if "access_token" not in resultado:
        sys.exit(f"[erro] autenticação falhou: {resultado.get('error_description') or resultado}")
    salvar_cache()
    return resultado["access_token"]


def graph_req(metodo: str, caminho: str, token: str, payload=None, headers=None):
    import requests
    hdrs = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    url = caminho if caminho.startswith("http") else GRAPH + caminho
    resp = requests.request(metodo, url, headers=hdrs, json=payload, timeout=120)
    if resp.status_code >= 400:
        sys.exit(f"[erro] Graph {resp.status_code} em {caminho}:\n{resp.text[:2000]}")
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def graph_buscar_mensagens(token: str, termos: list[str], top: int = 50):
    headers = {"ConsistencyLevel": "eventual"}
    consulta = " OR ".join(f'"{t}"' for t in termos)
    caminho = (f"/me/messages?$search={consulta}&$top={top}"
               f"&$select=id,subject,from,receivedDateTime&$count=true")
    mensagens = graph_req("GET", caminho, token, headers=headers).get("value", [])
    # $search não aceita $orderby junto: ordena aqui.
    mensagens.sort(key=lambda m: m.get("receivedDateTime") or "", reverse=True)
    return mensagens


def graph_listar_mensagens(token: str, desde_iso: str, top: int = 200):
    caminho = (f"/me/messages?$filter=receivedDateTime ge {desde_iso}"
               f"&$top={top}&$select=id,internetMessageId,subject,from,receivedDateTime,hasAttachments"
               f"&$orderby=receivedDateTime DESC")
    return graph_req("GET", caminho, token).get("value", [])


def remetente_eh_fenix(mensagem: dict, cfg: dict) -> bool:
    de = mensagem.get("from") or {}
    endereco = ((de.get("emailAddress") or {}).get("address") or "")
    nome = ((de.get("emailAddress") or {}).get("name") or "")
    alvo = norm(f"{endereco} {nome}")
    return any(norm(t) in alvo for t in cfg["remetentes_fenix"])


def sanitizar_nome_arquivo(nome: str) -> str:
    nome = (nome or "anexo.pdf").strip().replace("\r", "").replace("\n", "")
    nome = re.sub(r"[^\w\s.,()-]", "_", nome)
    return nome[:120] or "anexo.pdf"


# ---------------------------------------------------------------- e-mail de saída

def caminho_assinatura(cfg: dict):
    """Imagem da assinatura em uso.

    A config manda; sem ela, vale o ativo que viaja junto com a skill
    (`assets/assinatura.png`), para a skill funcionar em outra máquina só
    importando a assinatura de novo.
    """
    bruto = (cfg.get("assinatura_imagem") or "").strip()
    if bruto:
        caminho = Path(bruto).expanduser()
        return caminho if caminho.exists() else None
    return ASSINATURA_PADRAO if ASSINATURA_PADRAO.exists() else None


def corpo_com_assinatura(texto: str, cfg: dict):
    """Corpo do e-mail e anexos extras (a imagem da assinatura, quando houver)."""
    imagem = caminho_assinatura(cfg)
    if not imagem:
        return {"contentType": "Text", "content": texto}, []
    paragrafos = "".join(
        f"<p>{html_escape(linha)}</p>" if linha.strip() else "<p>&nbsp;</p>"
        for linha in texto.split("\n"))
    corpo = {"contentType": "HTML", "content": (
        '<div style="font-family:Calibri,sans-serif;font-size:11pt">'
        f"{paragrafos}<p>At.te,</p>"
        '<p><img src="cid:assinatura" alt="Assinatura" '
        'style="max-width:843px;width:100%"></p></div>')}
    return corpo, [{
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": imagem.name,
        "contentType": "image/png",
        "isInline": True,
        "contentId": "assinatura",
        "contentBytes": base64.b64encode(imagem.read_bytes()).decode("ascii"),
    }]


def montar_mensagem(nota: dict, destino: str, cfg: dict, anexo: Path):
    campos = {
        **{k: nota.get(k, "") for k in nota},
        "assinatura": cfg.get("email_assinatura", ""),
        "valor_total": nota.get("valor_total", ""),
        "valor_liquido": nota.get("valor_liquido", ""),
        "tomador": nota.get("tomador_nome", ""),
    }
    # O de-para aceita vários destinatários separados por vírgula ou ponto e vírgula.
    enderecos = [e.strip() for e in re.split(r"[,;]", destino) if e.strip()]
    corpo, extras = corpo_com_assinatura(renderizar(cfg["corpo_template"], campos), cfg)
    anexos = [{
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": anexo.name,
        "contentType": "application/pdf",
        "contentBytes": base64.b64encode(anexo.read_bytes()).decode("ascii"),
    }]
    anexos.extend(extras)
    return {
        "subject": renderizar(cfg["assunto_template"], campos),
        "body": corpo,
        "toRecipients": [{"emailAddress": {"address": e}} for e in enderecos],
        "attachments": anexos,
    }


# ---------------------------------------------------------------- tabelas no console

def truncar(txt: str, largura: int) -> str:
    txt = (txt or "").strip().replace("\n", " ")
    return txt if len(txt) <= largura else txt[: largura - 1] + "…"


def imprimir_tabela(colunas: list[tuple[str, int]], linhas: list[list[str]]) -> None:
    print("  ".join(nome.ljust(larg) for nome, larg in colunas))
    print("  ".join("-" * larg for _, larg in colunas))
    for linha in linhas:
        print("  ".join(truncar(celula, larg).ljust(larg) for celula, (_, larg) in zip(linha, colunas)))


# ---------------------------------------------------------------- comandos

def cmd_check(args):
    ok, avisos = [], []
    cfg = carregar_config()

    try:
        import pdfplumber  # noqa: F401
        ok.append("pdfplumber disponível (parser PDF)")
    except ImportError:
        import shutil
        if shutil.which("pdftotext"):
            ok.append("pdfplumber ausente, mas pdftotext disponível (fallback)")
        else:
            avisos.append("nem pdfplumber nem pdftotext — parser PDF não funciona")

    if VENV_PYTHON.exists():
        ok.append(f"venv em {VENV_PYTHON}")
        probe = subprocess.run([str(VENV_PYTHON), "-c", "import msal"], capture_output=True)
        ok.append("msal instalado no venv" if probe.returncode == 0
                  else "msal AUSENTE no venv — rode setup.sh")
    else:
        avisos.append("sem venv (Graph indisponível) — rode: bash "
                      f"{SKILL_HOME}/scripts/setup.sh")

    if CONFIG_PATH.exists():
        garantir_600(CONFIG_PATH)
        ok.append(f"config: {CONFIG_PATH}")
        if re.fullmatch(r"[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", cfg["client_id"]):
            ok.append("client_id configurado")
        else:
            avisos.append("client_id não é um GUID — registro do app no Entra pendente (INSTALL.md)")
    else:
        avisos.append(f"sem config em {CONFIG_PATH} — copie config.example.json")

    if DEPARA_PATH.exists():
        linhas = ler_depara()
        ok.append(f"de-para: {len(linhas)} tomador(es) em {DEPARA_PATH}")
    else:
        avisos.append(f"sem de-para em {DEPARA_PATH}")

    ndir = notas_dir(cfg)
    if ndir.is_dir():
        pdfs = sorted(ndir.glob("*.pdf"))
        ok.append(f"notas_dir {ndir}: {len(pdfs)} PDF(s)")
    else:
        avisos.append(f"notas_dir {ndir} não existe")

    caminho = caminho_assinatura(cfg)
    if caminho:
        ok.append(f"assinatura (imagem): {caminho}")
    else:
        avisos.append("sem assinatura em imagem — os e-mails saem com a assinatura em texto "
                      "puro (o Outlook não aplica a dele em envio por API). "
                      "Rode: terras_notas.py assinatura importar")

    if TOKEN_PATH.exists():
        ok.append("cache de token presente (rode `status` para validar)")
    else:
        avisos.append("sem login Microsoft — rode: terras_notas.py auth")

    for linha in ok:
        print(f"[ok]   {linha}")
    for linha in avisos:
        print(f"[pend] {linha}")
    if not avisos:
        print("tudo pronto.")


def cmd_auth(args):
    token = graph_token(interativo=True)
    # /me exige User.Read (que não pedimos): sonda o correio, que é o que importa.
    dados = graph_req("GET", "/me/messages?$top=1&$select=subject,receivedDateTime", token)
    app, _ = graph_app()
    contas = app.get_accounts()
    quem = contas[0].get("username") if contas else "(conta desconhecida)"
    print(f"autenticado como: {quem}")
    print(f"acesso ao correio confirmado ({len(dados.get('value', []))} mensagem(ns) na sondagem).")


def cmd_descobrir_remetente(args):
    cfg = carregar_config()
    token = graph_token()
    mensagens = graph_buscar_mensagens(token, cfg["busca_termos"], top=args.top)
    contagem: dict[str, dict] = {}
    for msg in mensagens:
        de = (msg.get("from") or {}).get("emailAddress") or {}
        chave = f"{de.get('address', '?')} | {de.get('name', '')}"
        if chave not in contagem:
            contagem[chave] = {"n": 0, "ultimo": msg.get("receivedDateTime", ""), "exemplo": msg.get("subject", "")}
        contagem[chave]["n"] += 1
    if not contagem:
        print("nada encontrado com os termos:", ", ".join(cfg["busca_termos"]))
        return
    print(f"{'remetente':60}  {'qtd':>3}  último e-mail (exemplo de assunto)")
    print("-" * 110)
    for chave, info in sorted(contagem.items(), key=lambda item: -item[1]["n"]):
        print(f"{truncar(chave, 60):60}  {info['n']:>3}  {truncar(info['ultimo'][:10] + ' ' + info['exemplo'], 44)}")
    print("\nconfirme o remetente da Fênix e adicione um trecho dele em "
          "`remetentes_fenix` da config (ex.: \"@fenixassessoria.com.br\").")


def cmd_fetch(args):
    cfg = carregar_config()
    token = graph_token()
    if args.desde:
        desde_iso = args.desde
    else:
        desde_iso = (datetime.now(timezone.utc) - timedelta(days=cfg["fetch_janela_dias"])).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
    mensagens = graph_listar_mensagens(token, desde_iso)
    alvo = [m for m in mensagens if m.get("hasAttachments") and remetente_eh_fenix(m, cfg)]
    print(f"{len(mensagens)} mensagens na janela; {len(alvo)} da Fênix com anexo")
    if not alvo:
        print("nada para baixar. Se a Fênix não casa com `remetentes_fenix`, rode `descobrir-remetente`.")
        return

    ndir = notas_dir(cfg)
    ndir.mkdir(parents=True, exist_ok=True)
    st = carregar_state(cfg)
    baixados = 0
    for msg in alvo:
        mid = msg.get("internetMessageId") or msg["id"]
        if mid in st["mensagens"] and not args.reprocessar:
            continue
        anexos = graph_req("GET", f"/me/messages/{msg['id']}/attachments", token).get("value", [])
        nomes = []
        for anexo in anexos:
            nome = sanitizar_nome_arquivo(anexo.get("name") or "")
            tipo = anexo.get("contentType") or ""
            if anexo.get("isInline") or (tipo != "application/pdf" and not nome.lower().endswith(".pdf")):
                continue
            destino = ndir / nome
            if destino.exists() and not args.sobrescrever:
                nomes.append(nome)
                continue
            conteudo = base64.b64decode(anexo.get("contentBytes") or "")
            destino.write_bytes(conteudo)
            baixados += 1
            nomes.append(nome)
            print(f"[baixado] {nome}  ({len(conteudo)} bytes)")
        st["mensagens"][mid] = {"assunto": msg.get("subject", ""),
                                "recebido_em": msg.get("receivedDateTime", ""),
                                "anexos": nomes}
    salvar_state(cfg, st)
    print(f"concluído: {baixados} anexo(s) novo(s) em {ndir}")


def cmd_parse(args):
    cfg = carregar_config()
    ndir = notas_dir(cfg)
    if args.pdfs:
        alvos = [Path(p).expanduser() for p in args.pdfs]
    else:
        alvos = sorted(ndir.glob("*.pdf"))
    st = carregar_state(cfg)
    pendentes = []
    for pdf in alvos:
        if not pdf.exists():
            print(f"[aviso] {pdf} não existe")
            continue
        nota = parse_nfse(extrair_texto_pdf(pdf))
        nota["arquivo"] = pdf.name
        faltas = parse_incompleto(nota)
        if faltas:
            pendentes.append((pdf.name, faltas))
        st["notas"][pdf.name] = nota
    salvar_state(cfg, st)
    linhas = [[str(st["notas"][p.name].get("numero", "?")),
               st["notas"][p.name].get("serie", ""),
               truncar(st["notas"][p.name].get("tomador_nome", ""), 44),
               truncar(st["notas"][p.name].get("tomador_email", ""), 30),
               st["notas"][p.name].get("valor_total", "")]
              for p in alvos if p.name in st["notas"]]
    if linhas:
        imprimir_tabela([("NF", 5), ("S", 3), ("Tomador", 44), ("E-mail no PDF", 30), ("Valor", 10)], linhas)
    for nome, faltas in pendentes:
        print(f"[aviso] {nome}: campos não reconhecidos: {', '.join(faltas)} — revise manualmente")
    if args.json:
        print(json.dumps({p.name: st["notas"][p.name] for p in alvos if p.name in st["notas"]},
                         ensure_ascii=False, indent=2))


def cmd_depara(args):
    if args.acao == "list":
        linhas = ler_depara()
        if not linhas:
            print(f"de-para vazio ({DEPARA_PATH})")
            return
        imprimir_tabela([("CNPJ", 18), ("Razão social", 44), ("Apelidos", 20), ("E-mail", 34)],
                        [[l.get("cnpj", ""), l.get("razao_social", ""), l.get("apelidos", ""), l.get("email", "")]
                         for l in linhas])
        return
    if args.acao == "add":
        if not args.email:
            sys.exit("[erro] --email é obrigatório em `depara add`")
        if args.janela and not re.fullmatch(r"\d{1,2}\s*-\s*\d{1,2}", args.janela):
            sys.exit("[erro] --janela deve ser dia-dia, ex.: 15-20")
        linhas = ler_depara()
        linhas.append({"cnpj": args.cnpj or "", "razao_social": args.nome or "",
                       "apelidos": args.apelidos or "", "email": args.email,
                       "janela_envio": args.janela or "", "obs": args.obs or ""})
        gravar_depara(linhas)
        print(f"adicionado: {args.nome or args.cnpj} -> {args.email} (total {len(linhas)})")
        return
    if args.acao == "rm":
        linhas = ler_depara()
        if not (args.chave or "").strip():
            sys.exit("[erro] informe a chave a remover (CNPJ, nome ou e-mail)")
        alvo = norm(args.chave)
        alvo_digitos = so_digitos(args.chave)
        restantes = []
        for linha in linhas:
            palheiro = norm(" ".join([linha.get("cnpj", ""), linha.get("razao_social", ""),
                                      linha.get("apelidos", ""), linha.get("email", "")]))
            if alvo in palheiro:
                continue
            if alvo_digitos and alvo_digitos == so_digitos(linha.get("cnpj", "")):
                continue
            restantes.append(linha)
        removidos = len(linhas) - len(restantes)
        if not removidos:
            print("nenhum registro casou com", args.chave)
            return
        gravar_depara(restantes)
        print(f"removido(s): {removidos}")
        return
    if args.acao == "check":
        cfg = carregar_config()
        st = carregar_state(cfg)
        depara = ler_depara()
        sem_destino = 0
        for nome, nota in sorted(st["notas"].items(), key=lambda item: item[1].get("numero") or 0):
            destino = resolver_destino(nota, depara)
            estado = "ok" if destino else "PEND"
            if not destino:
                sem_destino += 1
            email = destino["email"] if destino else "—"
            origem = destino["origem"] if destino else ""
            print(f"NF {nota.get('numero')}/{nota.get('serie')}  {estado}  "
                  f"{truncar(nota.get('tomador_nome', ''), 46):46}  {email:34}  {origem}")
        print(f"\n{sem_destino} sem destino — use `depara add --cnpj ... --nome ... --email ...`")


def cmd_match(args):
    cfg = carregar_config()
    st = carregar_state(cfg)
    depara = ler_depara()
    linhas, sem_destino = [], []
    for nome_arq, nota in sorted(st["notas"].items(), key=lambda item: item[1].get("numero") or 0):
        if args.nota and nota.get("numero") != args.nota:
            continue
        despacho = st["despachos"].get(chave_nota(nota))
        destino = resolver_destino(nota, depara)
        if despacho:
            situacao = "ENVIADA" if despacho.get("modo") == "enviado" else "rascunho"
        else:
            situacao = destino["confianca"] if destino else "PENDENTE"
        if destino:
            linhas.append([str(nota.get("numero", "?")), nota.get("serie", ""),
                           truncar(nota.get("tomador_nome", ""), 40), destino["email"], situacao])
        else:
            sem_destino.append(nome_arq)
            linhas.append([str(nota.get("numero", "?")), nota.get("serie", ""),
                           truncar(nota.get("tomador_nome", ""), 40), "—", situacao])
    imprimir_tabela([("NF", 5), ("S", 3), ("Tomador", 40), ("Destino", 34), ("Situação", 9)], linhas)
    if sem_destino:
        print(f"\nsem destino ({len(sem_destino)}): adicione com `depara add` "
              "(CNPJ da nota sai do próprio PDF, veja `parse`)")
    if args.json:
        print(json.dumps({chave_nota(n): resolver_destino(n, depara) or {} for n in st["notas"].values()},
                         ensure_ascii=False, indent=2))


def _notas_a_despachar(cfg, st, somente=None):
    depara = ler_depara()
    fila = []
    for nome_arq, nota in sorted(st["notas"].items(), key=lambda item: item[1].get("numero") or 0):
        if somente and nota.get("numero") != somente:
            continue
        if chave_nota(nota) in st["despachos"]:
            continue
        destino = resolver_destino(nota, depara)
        if destino and destino["confianca"] == "alta":
            pdf = notas_dir(cfg) / nota["arquivo"]
            if pdf.exists():
                fila.append((nota, destino, pdf))
    return fila


def cmd_despachar(args):
    cfg = carregar_config()
    st = carregar_state(cfg)
    fila = _notas_a_despachar(cfg, st, somente=args.nota)

    if not fila:
        print("nada a despachar (sem notas novas com destino de alta confiança).")
        return

    print(f"{'NF':5}  {'Tomador':42}  {'Destino':34}  Anexo")
    print("-" * 100)
    for nota, destino, pdf in fila:
        print(f"{str(nota.get('numero')):5}  {truncar(nota.get('tomador_nome', ''), 42):42}  "
              f"{destino['email']:34}  {pdf.name}")

    hoje = datetime.now().day
    for nota, destino, _ in fila:
        alerta = alerta_janela(destino.get("janela", ""), hoje)
        if alerta:
            print(f"[atenção] NF {chave_nota(nota)} ({nota.get('tomador_nome', '')}): {alerta}")

    if not (args.rascunho or (args.enviar and args.yes)):
        print(f"\nmodo conferência ({len(fila)} e-mail(s) montado(s), nada enviado). "
              "Para valer: --rascunho (cria rascunhos) ou --enviar --yes (envia).")
        return

    token = graph_token()
    modo = "rascunho" if args.rascunho else "enviado"
    for nota, destino, pdf in fila:
        mensagem = montar_mensagem(nota, destino["email"], cfg, pdf)
        if args.rascunho:
            criada = graph_req("POST", "/me/messages", token, payload=mensagem)
            st["despachos"][chave_nota(nota)] = {
                "email": destino["email"], "modo": modo, "enviado_em": agora(),
                "origem": destino["origem"], "graph_id": criada.get("id", ""),
                "arquivo": pdf.name}
            print(f"[rascunho] NF {chave_nota(nota)} -> {destino['email']} (confira na pasta Rascunhos)")
        else:
            graph_req("POST", "/me/sendMail", token,
                      payload={"message": mensagem, "saveToSentItems": True})
            st["despachos"][chave_nota(nota)] = {
                "email": destino["email"], "modo": modo, "enviado_em": agora(),
                "origem": destino["origem"], "arquivo": pdf.name}
            print(f"[enviado] NF {chave_nota(nota)} -> {destino['email']}")
    salvar_state(cfg, st)


def cmd_assinatura(args):
    cfg = carregar_config()

    if args.acao == "mostrar":
        atual = caminho_assinatura(cfg)
        if not atual:
            print("nenhuma assinatura em uso — rode: terras_notas.py assinatura importar")
            return
        origem = "config (assinatura_imagem)" if (cfg.get("assinatura_imagem") or "").strip() \
            else "ativo da skill (assets/assinatura.png)"
        print(f"assinatura em uso: {atual} ({atual.stat().st_size} bytes) — {origem}")
        return

    # acao == importar: pega a imagem inline de um e-mail já enviado pelo Outlook
    token = graph_token()
    caminho = (f"/me/mailFolders/sentitems/messages?$top={args.buscar}"
               "&$select=id,subject,sentDateTime")
    for msg in graph_req("GET", caminho, token).get("value", []):
        assunto = msg.get("subject") or ""
        if args.assunto and norm(args.assunto) not in norm(assunto):
            continue
        anexos = graph_req("GET", f"/me/messages/{msg['id']}/attachments", token).get("value", [])
        inline = [a for a in anexos
                  if a.get("isInline") and (a.get("contentType") or "").startswith("image/")]
        if not inline:
            continue
        imagem = inline[0]
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        ASSINATURA_PADRAO.write_bytes(base64.b64decode(imagem["contentBytes"]))
        os.chmod(ASSINATURA_PADRAO, 0o600)
        print(f"assinatura importada de «{assunto}» ({msg.get('sentDateTime', '')[:10]})")
        print(f"  {imagem.get('name')} ({imagem.get('size')} bytes) -> {ASSINATURA_PADRAO}")
        if (cfg.get("assinatura_imagem") or "").strip():
            cfg["assinatura_imagem"] = ""
            salvar_json(CONFIG_PATH, cfg)
            garantir_600(CONFIG_PATH)
            print("  config ajustada para usar o ativo da skill (assinatura_imagem vazio)")
        return
    print("não achei e-mail enviado com imagem inline; use --assunto com um trecho do assunto "
          "(ex.: --assunto 'NOTA') ou --buscar 100 para olhar mais mensagens")


# ---------------------------------------------------------------- pedidos à contabilidade

def competencia_atual() -> str:
    hoje = datetime.now()
    return f"{hoje.month:02d}/{hoje.year}"


def resolver_cliente(chave: str, depara: list[dict]):
    """Acha a linha do de-para por CNPJ, razão social ou apelido."""
    alvo, digitos = norm(chave), so_digitos(chave)
    for linha in depara:
        if digitos and so_digitos(linha.get("cnpj") or "") == digitos:
            return linha
        candidatos = [norm(linha.get("razao_social") or "")]
        candidatos += [norm(a) for a in re.split(r"[;,]", linha.get("apelidos") or "") if a.strip()]
        for cand in candidatos:
            if cand and (cand == alvo or cand in alvo or alvo in cand):
                return linha
    return None


def normalizar_valor(bruto: str) -> str:
    """'8000', '8.000,00', '8000.00' -> '8.000,00'."""
    limpo = re.sub(r"[^\d,.]", "", bruto or "")
    if "," in limpo:
        numero = limpo.replace(".", "").replace(",", ".")
    else:
        numero = limpo
    try:
        return f"{float(numero):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return bruto


def itens_do_pedido(pedidos: list[dict], competencia: str) -> list[dict]:
    return [p for p in pedidos if p.get("competencia") == competencia and not p.get("cancelado")]


def bloco_do_item(indice: int, item: dict) -> str:
    linhas = [f"{indice}) {item.get('razao_social') or item.get('cliente')}",
              f"   CNPJ: {item.get('cnpj') or '-'}"]
    if item.get("endereco"):
        linhas.append(f"   Endereço: {item['endereco']}")
    if item.get("descricao"):
        linhas.append(f"   Serviço: {item['descricao']}")
    linhas.append(f"   Valor: R$ {item.get('valor') or '-'}")
    if item.get("janela"):
        linhas.append(f"   Observação: o cliente pede o envio entre os dias "
                      f"{item['janela'].replace('-', ' e ')} do mês — "
                      "favor emitir antes disso para dar tempo")
    if item.get("obs"):
        linhas.append(f"   Observação: {item['obs']}")
    return "\n".join(linhas)


def ficha_de_emissao(cfg: dict, item: dict) -> str:
    """Roteiro de preenchimento no portal da Nota Joseense.

    O tomador não é digitado: informa-se o CNPJ e o sistema busca no Cadastro de
    Receitas Mobiliárias da prefeitura (se divergir, quem corrige é o tomador).
    """
    emissao = cfg.get("emissao") or {}
    linhas = [
        f"=== FICHA DE EMISSÃO — {item.get('competencia')} ===",
        "",
        f"Tomador: {item.get('razao_social')}",
        f"  CNPJ (é o que se digita no portal; o resto vem do cadastro da prefeitura):",
        f"  {item.get('cnpj')}",
        f"  Endereço conforme consta na última nota: {item.get('endereco') or '-'}",
        "",
        f"Competência: {item.get('competencia')}",
        f"Valor do serviço: R$ {item.get('valor') or '-'}",
        f"Código do serviço: {emissao.get('codigo_servico', '-')} — {emissao.get('codigo_servico_texto', '')}",
        f"CNAE: {emissao.get('cnae', '-')}",
        f"Município de incidência do ISSQN: {emissao.get('municipio_incidencia', '-')}",
        f"Responsável pelo recolhimento do ISSQN: {emissao.get('responsavel_issqn', '-')}",
        f"Regime: {emissao.get('regime', '-')}",
        f"Descrição do serviço: {item.get('descricao') or '-'}",
    ]
    if item.get("janela"):
        linhas.append(f"Enviar ao cliente entre os dias "
                      f"{item['janela'].replace('-', ' e ')} do mês")
    if item.get("obs"):
        linhas.append(f"Observação: {item['obs']}")
    return "\n".join(linhas)


def montar_pedido(cfg: dict, itens: list[dict], competencia: str):
    corpo_itens = "\n\n".join(bloco_do_item(i, item) for i, item in enumerate(itens, start=1))
    campos = {"competencia": competencia, "quantidade": len(itens), "itens": corpo_itens}
    texto = renderizar(cfg["pedido_corpo_template"], campos)
    corpo, extras = corpo_com_assinatura(texto, cfg)
    return {
        "subject": renderizar(cfg["pedido_assunto_template"], campos),
        "body": corpo,
        "attachments": extras or None,
    }


def cmd_pedido(args):
    cfg = carregar_config()
    st = carregar_state(cfg)
    depara = ler_depara()
    st.setdefault("pedidos", [])
    competencia = args.competencia or competencia_atual()

    if args.acao == "add":
        linha = resolver_cliente(args.cliente, depara)
        if not linha:
            conhecidos = ", ".join(l.get("razao_social", "?") for l in depara) or "(de-para vazio)"
            sys.exit(f"[erro] cliente «{args.cliente}» não está no de-para. Conhecidos: {conhecidos}")
        descricao = args.descricao
        if not descricao:
            # herda a descrição do serviço da última nota desse CNPJ, se houver
            iguais = [n for n in st["notas"].values()
                      if so_digitos(n.get("tomador_cnpj") or "") == so_digitos(linha.get("cnpj") or "")]
            iguais.sort(key=lambda n: n.get("numero") or 0, reverse=True)
            descricao = (iguais[0].get("descricao_servico") if iguais else "") or ""
        st["pedidos"].append({
            "competencia": competencia,
            "cliente": args.cliente,
            "cnpj": linha.get("cnpj", ""),
            "razao_social": linha.get("razao_social", ""),
            "endereco": linha.get("endereco", ""),
            "descricao": descricao,
            "valor": normalizar_valor(args.valor) if args.valor else "",
            "janela": (linha.get("janela_envio") or "").strip(),
            "obs": args.obs or "",
            "criado_em": agora(),
            "solicitado_em": None,
        })
        salvar_state(cfg, st)
        print(f"adicionado ao pedido {competencia}: {linha.get('razao_social')}"
              f" — R$ {normalizar_valor(args.valor) if args.valor else '(sem valor)'}")
        return

    itens = itens_do_pedido(st["pedidos"], competencia)
    pendentes = [i for i in itens if not i.get("solicitado_em")]

    if args.acao == "list":
        if not itens:
            print(f"nenhum item no pedido {competencia}")
            return
        imprimir_tabela([("Cliente", 38), ("Valor", 12), ("Enviado", 18), ("Descrição", 30)],
                        [[truncar(i.get("razao_social", ""), 38), i.get("valor", ""),
                          (i.get("solicitado_em") or "pendente")[:16], truncar(i.get("descricao", ""), 30)]
                         for i in itens])
        return

    if args.acao == "rm":
        linhas = st["pedidos"]
        alvo = norm(args.cliente or "")
        restantes = [p for p in linhas
                     if not (p.get("competencia") == competencia and alvo
                             and alvo in norm(f"{p.get('cliente','')} {p.get('razao_social','')}"))]
        removidos = len(linhas) - len(restantes)
        st["pedidos"] = restantes
        salvar_state(cfg, st)
        print(f"removido(s) do pedido {competencia}: {removidos}")
        return

    if not itens:
        print(f"nada a solicitar na competência {competencia}. Use `pedido add`.")
        return

    mensagem = montar_pedido(cfg, itens, competencia)
    destino = (args.para or cfg.get("assessoria_email") or cfg.get("fenix_email") or "").strip()

    if args.acao == "ficha":
        if not itens:
            print(f"nada na competência {competencia}. Use `pedido add`.")
            return
        for item in itens:
            print(ficha_de_emissao(cfg, item))
            print()
        return

    if args.acao == "texto":
        print("PARA:   ", destino or "(defina assessoria_email na config ou use --para)")
        print("ASSUNTO:", mensagem["subject"])
        print("--- corpo ---")
        for item in itens:
            print(bloco_do_item(itens.index(item) + 1, item))
            print()
        return

    if not destino:
        sys.exit("[erro] sem destinatário: use --para EMAIL ou defina `assessoria_email` na config")
    print(f"para: {destino}\nassunto: {mensagem['subject']}\n{len(pendentes)} item(ns) pendente(s)")
    if not (args.rascunho or (args.enviar and args.yes)):
        print("\nmodo conferência (nada enviado). Para valer: --rascunho ou --enviar --yes")
        print("o texto completo sai com: pedido texto")
        return

    token = graph_token()
    mensagem["toRecipients"] = [{"emailAddress": {"address": e.strip()}}
                                for e in re.split(r"[,;]", destino) if e.strip()]
    if args.rascunho:
        criada = graph_req("POST", "/me/messages", token, payload=mensagem)
        print(f"[rascunho] solicitação de {competencia} criada (confira na pasta Rascunhos) "
              f"id={criada.get('id', '')[:24]}…")
        return
    graph_req("POST", "/me/sendMail", token,
              payload={"message": mensagem, "saveToSentItems": True})
    for item in pendentes:
        item["solicitado_em"] = agora()
    salvar_state(cfg, st)
    print(f"[enviado] solicitação de {competencia} -> {destino} "
          f"({len(pendentes)} item(ns) marcados como solicitados)")


def cmd_status(args):
    cfg = carregar_config()
    st = carregar_state(cfg)
    depara = ler_depara()
    total = len(st["notas"])
    enviadas = len([d for d in st["despachos"].values() if d.get("modo") == "enviado"])
    rascunhos = len([d for d in st["despachos"].values() if d.get("modo") == "rascunho"])
    pendentes_destino = 0
    prontas = 0
    for nota in st["notas"].values():
        if chave_nota(nota) in st["despachos"]:
            continue
        destino = resolver_destino(nota, depara)
        if not destino:
            pendentes_destino += 1
        elif destino["confianca"] == "alta":
            prontas += 1
        else:
            pendentes_destino += 1  # sugerido espera decisão
    print(f"notas parseadas: {total} | prontas p/ enviar: {prontas} | "
          f"sem destino confirmado: {pendentes_destino} | rascunhos: {rascunhos} | enviadas: {enviadas}")
    print(f"mensagens da Fênix já lidas: {len(st['mensagens'])} | de-para: {len(depara)} registro(s)")
    if prontas:
        print("rode `despachar` para conferir e `despachar --enviar --yes` para enviar.")
    if pendentes_destino:
        print("há notas sem destino: `match` mostra quais; resolva com `depara add`.")


def cmd_run(args):
    cmd_fetch(args)
    cmd_parse(args)
    cmd_match(argparse.Namespace(nota=None, json=False))


# ---------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(prog="terras_notas.py",
                                     description="NFS-e da Fênix: baixa, analisa, casa destino e envia")
    sub = parser.add_subparsers(dest="comando", required=True)

    sub.add_parser("check", help="valida dependências, config, de-para e login")

    sub.add_parser("auth", help="login Microsoft (código de dispositivo)")

    p = sub.add_parser("descobrir-remetente", help="busca na caixa quem é a Fênix")
    p.add_argument("--top", type=int, default=50)

    p = sub.add_parser("fetch", help="baixa anexos PDF dos e-mails da Fênix")
    p.add_argument("--desde", help="data ISO (ex.: 2026-06-01T00:00:00Z); padrão: janela da config")
    p.add_argument("--reprocessar", action="store_true", help="reprocessa mensagens já registradas")
    p.add_argument("--sobrescrever", action="store_true", help="sobrescreve PDF existente no destino")

    p = sub.add_parser("parse", help="extrai dados dos PDFs (todos, ou arquivos informados)")
    p.add_argument("pdfs", nargs="*", help="caminhos de PDF (vazio = todos em notas_dir)")
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("depara", help="mantém o CSV nome/CNPJ -> e-mail")
    p.add_argument("acao", choices=["list", "add", "rm", "check"])
    p.add_argument("--cnpj"); p.add_argument("--nome"); p.add_argument("--apelidos")
    p.add_argument("--email"); p.add_argument("--janela", help="dias preferidos p/ envio, ex.: 15-20")
    p.add_argument("--obs"); p.add_argument("chave", nargs="?")

    p = sub.add_parser("match", help="casa notas com destinos (de-para)")
    p.add_argument("--nota", type=int)
    p.add_argument("--json", action="store_true")

    p = sub.add_parser("despachar", help="monta/envia e-mails com as notas")
    p.add_argument("--nota", type=int, help="limita a uma NF")
    p.add_argument("--rascunho", action="store_true", help="cria rascunhos em vez de enviar")
    p.add_argument("--enviar", action="store_true", help="envia de fato (exige --yes)")
    p.add_argument("--yes", action="store_true")

    p = sub.add_parser("assinatura", help="importa/mostra a assinatura usada nos e-mails")
    p.add_argument("acao", choices=["importar", "mostrar"])
    p.add_argument("--assunto", help="trecho do assunto de um e-mail enviado que tenha a assinatura")
    p.add_argument("--buscar", type=int, default=25, help="quantos enviados varrer (padrão 25)")

    p = sub.add_parser("pedido", help="ficha/pedido de emissão por cliente e competência")
    p.add_argument("acao", choices=["add", "list", "rm", "ficha", "texto", "enviar"])
    p.add_argument("--cliente", help="cliente do de-para (nome, apelido ou CNPJ)")
    p.add_argument("--valor", help="valor do serviço (ex.: 8000 ou 8.000,00)")
    p.add_argument("--descricao", help="descrição do serviço (padrão: a da última nota do cliente)")
    p.add_argument("--obs", help="observação livre para o item")
    p.add_argument("--competencia", help="MM/AAAA (padrão: mês atual)")
    p.add_argument("--para", help="e-mail de quem emite (padrão: assessoria_email da config)")
    p.add_argument("--rascunho", action="store_true", help="cria rascunho em vez de enviar")
    p.add_argument("--enviar", action="store_true", help="envia de fato (exige --yes)")
    p.add_argument("--yes", action="store_true")

    sub.add_parser("status", help="resumo do estado")

    p = sub.add_parser("run", help="fetch + parse + match")
    p.add_argument("--desde", help="data ISO")
    p.add_argument("--reprocessar", action="store_true")
    p.add_argument("--sobrescrever", action="store_true")

    args = parser.parse_args()
    {"check": cmd_check, "auth": cmd_auth, "descobrir-remetente": cmd_descobrir_remetente,
     "fetch": cmd_fetch, "parse": cmd_parse, "depara": cmd_depara, "match": cmd_match,
     "despachar": cmd_despachar, "assinatura": cmd_assinatura, "pedido": cmd_pedido,
     "status": cmd_status, "run": cmd_run}[args.comando](args)


if __name__ == "__main__":
    main()

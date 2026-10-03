#!/usr/bin/env python3
"""Estatisticas de posts do LinkedIn: coleta, store e diagnostico.

Pipeline pensado para o Everton: o agente abre as paginas de analise no
navegador in-app (que ja tem a sessao dele), salva o snapshot da pagina em
texto, e este CLI transforma o snapshot em dado estruturado, guarda historico
e monta o relatorio que explica por que cada post rendeu ou nao.

Comandos:
    check                          estado do store e do que falta
    ingerir <arquivo|dir>...       parseia snapshots salvos e funde no store
    listar                         o que ja esta no store
    atributos                      cruza metricas com os arquivos post-*.md do workspace
    relatorio                      gera o relatorio de diagnostico (markdown)
    links                          imprime as URLs de analise para o agente abrir
    selftest                       roda o parser contra fixtures e confere o resultado

Tudo em Python puro. Sem dependencia externa, sem chamada de rede: este CLI
nunca fala com o LinkedIn. Quem fala e o navegador, com o snapshot virando
arquivo antes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
import re
import sys
import unicodedata
from urllib.parse import unquote
from pathlib import Path

VERSAO = 1

# ---------------------------------------------------------------- config


def diretorio_padrao() -> Path:
    env = os.environ.get("TERRAS_LINKEDIN_METRICAS_DIR")
    if env:
        return Path(env).expanduser()
    cfg = Path.home() / ".config" / "terras-linkedin-metricas" / "config.json"
    if cfg.exists():
        try:
            dado = json.loads(cfg.read_text(encoding="utf-8"))
            if dado.get("diretorio"):
                return Path(dado["diretorio"]).expanduser()
        except (OSError, json.JSONDecodeError):
            pass
    return Path.cwd() / "metricas"


def caminho_alvo() -> dict:
    """Publico que o Everton quer alcancar (usado no diagnostico de audiencia)."""
    cfg = Path.home() / ".config" / "terras-linkedin-metricas" / "config.json"
    alvo = {
        "descricao": "vaga Senior/Staff remota, Brasil e exterior",
        "senioridades": ["Sênior", "Diretor", "Gerente", "Proprietário"],
        "localidades": ["Reino Unido", "Estados Unidos", "Alemanha", "Portugal", "Irlanda", "Canadá", "Holanda", "Espanha"],
        "cargos": ["Engenheiro de software", "Arquiteto", "Desenvolvedor", "Engenheiro de DevOps", "Engenheiro de soluções"],
        "setores": ["Desenvolvimento de software", "Atividades dos serviços de tecnologia da informação"],
    }
    if cfg.exists():
        try:
            dado = json.loads(cfg.read_text(encoding="utf-8"))
            alvo.update(dado.get("alvo", {}))
        except (OSError, json.JSONDecodeError):
            pass
    return alvo


# ---------------------------------------------------------------- utilitarios

ROTULOS_NIVEL = {"Sênior", "Iniciante", "Pleno", "Estagiário", "Diretor", "Gerente", "Proprietário", "Sócio", "Treinamento"}
ROTULOS_DIM = {
    "Cargo",
    "Localidade",
    "Nível de experiência",
    "Empresa",
    "Setor",
    "Tamanho da empresa",
}

ROTULOS_METRICA = {
    "Impressões",
    "Impressões da publicação",
    "Reações",
    "Comentários",
    "Compartilhamentos",
    "Salvamentos",
    "Envios no LinkedIn",
    "Engajamento",
    "Engajamento nas redes",
    "Usuários alcançados",
    "Total de seguidores",
    "Novos seguidores",
    "Na rede (seguidores e conexões)",
    "Fora da rede",
    "Descoberta",
    "Atividades do perfil",
    "Visualizações do perfil a partir desta publicação",
    "Seguidores obtidos com esta publicação",
    "em relação a 7 dias anteriores",
}


def sem_aspas(t: str) -> str:
    t = t.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
        return t[1:-1]
    return t


def desescapar(t: str) -> str:
    """O snapshot escreve aspas escapadas (\\") no meio do texto. Sem soltar isso, o
    texto do post e o rótulo do gráfico saem com barra invertida visível na planilha."""
    return t.replace('\\"', '"').replace("\\'", "'")


def numero(t: str):
    """Converte '3.542', '1,169', '45%', 'menos de 1%' em float/int."""
    if t is None:
        return None
    t = t.strip()
    m = re.search(r"(menos de|less than)", t, re.I)
    if m:
        return 0.0
    m = re.search(r"(-?[\d.,]+)", t)
    if not m:
        return None
    bruto = m.group(1)
    if "." in bruto and "," in bruto:
        # separador decimal e o ultimo que aparece
        if bruto.rfind(".") > bruto.rfind(","):
            bruto = bruto.replace(",", "").replace(".", "")
        else:
            bruto = bruto.replace(".", "").replace(",", ".")
    elif "," in bruto:
        partes = bruto.split(",")
        bruto = bruto.replace(",", "") if len(partes[-1]) == 3 else bruto.replace(",", ".")
    elif "." in bruto:
        partes = bruto.split(".")
        bruto = bruto.replace(".", "") if len(partes[-1]) == 3 else bruto
    try:
        f = float(bruto)
    except ValueError:
        return None
    return int(f) if f == int(f) else f


RE_NUMERO_LIMPO = re.compile(r"^(?:menos de\s+)?[\d.,]+\s*%?$", re.I)


def numero_limpo(t: str):
    """Numero so quando o token E o numero. Evita pescar '4 vezes mais' no meio de uma frase."""
    if t is None:
        return None
    if not RE_NUMERO_LIMPO.match(t.strip()):
        return None
    return numero(t)


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def similaridade(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()


# ---------------------------------------------------------------- parser de snapshot

RE_URL = re.compile(r"/url:\s*(\S+)")
RE_ACTIVITY = re.compile(r"urn:li:activity:(\d+)")
RE_SHARE = re.compile(r"urn:li:share:(\d+)")
RE_IMG_DATA = re.compile(r"^(\d{4}-\d{2}-\d{2})|(\d{1,2} de \w+\.? de \d{4})")

MESES_PT = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


class Token:
    __slots__ = ("kind", "texto", "url")

    def __init__(self, kind: str, texto: str, url: str | None = None):
        self.kind = kind
        self.texto = texto
        self.url = url

    def __repr__(self) -> str:  # pragma: no cover - debug
        return f"<{self.kind}:{self.texto[:40]!r}>"


def tokenizar(snapshot: str) -> list[Token]:
    """Converte o snapshot ARIA em uma lista plana de tokens na ordem da pagina."""
    tokens: list[Token] = []
    for linha in snapshot.splitlines():
        bruta = linha.strip()
        if not bruta:
            continue
        limpa = re.sub(r"^-\s*", "", bruta)
        # o snapshot envolve em aspas simples o token que tem aspas dentro
        # (ex.: 'link "Ver hashtag: #dotnet"'), senao o tipo do token nao casa
        if limpa.startswith("'"):
            limpa = limpa[1:]
        m = RE_URL.match(limpa)
        if m:
            # o LinkedIn esconde URN em URL codificada (content=urn%3Ali%3Ashare%3A...),
            # entao a URL entra decodificada para o URN aparecer inteiro
            bruta_url = m.group(1)
            if "%3A" in bruta_url.upper():
                bruta_url = unquote(bruta_url)
            tokens.append(Token("url", bruta_url, bruta_url))
            continue
        m = re.match(r'^(paragraph|generic|text|heading|button|status|checkbox|progressbar|region|link|img)\b\s*(.*)$', limpa)
        if not m:
            continue
        kind = m.group(1)
        resto = m.group(2).strip()
        if resto[:1] in ("'", '"'):
            fim = resto.find(resto[0], 1)
            texto = resto[1:fim] if fim > 0 else resto[1:]
        elif ":" in resto:
            texto = resto.split(":", 1)[1].strip()
        else:
            texto = resto
        texto = desescapar(sem_aspas(texto)).strip()
        if not texto and kind != "link":
            continue
        tokens.append(Token(kind, texto))
    return tokens


TEXTOS_DE_CONTROLE = (
    "LinkedIn Corporation",
    "Ver análise",
    "Ver analise",
    "Ver hashtag",
    "Publicação no feed",
    "Saiba mais",
    "Exibir mais",
    "Patrocinar",
    "Promova esta publicação",
)


RE_RUIDO_LISTA = re.compile(r"^\d[\d.,]*\s*impress\S*\s*•\s*\d[\d.,]*\s*engajament", re.I)


def texto_publicado(tokens: list[Token], inicio: int = 0, fim: int | None = None) -> str:
    """Reconstroi o texto publicado juntando os fragmentos na ordem da pagina.

    O LinkedIn quebra o post em varios pedacos e ainda repete o texto inteiro no nome
    acessivel do link. Aqui entram so os pedacos (paragraph/text), em ordem, pulando
    rotulos de controle e o resumo "N impressoes • M engajamentos" da lista; se nao
    houver pedacos, cai no nome acessivel mais longo.
    """
    fim = len(tokens) if fim is None else fim
    pedacos: list[str] = []
    for t in tokens[inicio:fim]:
        if t.kind not in ("paragraph", "text"):
            continue
        txt = t.texto.strip()
        if len(txt) < 25 or RE_RUIDO_LISTA.match(txt):
            continue
        if any(c in txt for c in TEXTOS_DE_CONTROLE):
            continue
        if txt.startswith("Everton Lima") or txt in (pedacos[-1] if pedacos else ""):
            continue
        pedacos.append(txt)
    junto = " ".join(pedacos).strip()
    # as hashtags aparecem como link "Ver hashtag: #x", nunca no corpo do texto;
    # sem recolher aqui, a contagem de hashtags do post sairia zerada
    etiquetas = []
    for t in tokens[inicio:fim]:
        if t.kind == "link" and t.texto.startswith("Ver hashtag"):
            et = t.texto.replace("Ver hashtag:", "").strip()
            if et and et not in etiquetas:
                etiquetas.append(et)
    if etiquetas and len(junto) >= 120:
        junto = junto + " " + " ".join(etiquetas)
    if len(junto) >= 120:
        return junto
    candidatos = [t.texto for t in tokens[inicio:fim] if t.kind == "link" and len(t.texto) > 120]
    if candidatos:
        return re.sub(r"\s*Ver hashtag: #\w+", "", max(candidatos, key=len)).strip()
    return junto


class Pagina:
    """Acesso posicional aos tokens, com consumo para nao casar o mesmo numero duas vezes."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.consumidos: set[int] = set()

    def acha(self, rotulo: str, inicio: int = 0, exato: bool = True) -> int | None:
        for i in range(inicio, len(self.tokens)):
            t = self.tokens[i].texto
            if exato:
                if t == rotulo:
                    return i
            elif rotulo.lower() in t.lower():
                return i
        return None

    def todas(self, rotulo: str) -> list[int]:
        """Todos os indices do rotulo, com paragraph na frente: o valor do cartao grande
        vem em paragraph e a repeticao de controle do filtro vem em button/checkbox."""
        idx_par, idx_outros = [], []
        for i, t in enumerate(self.tokens):
            if t.texto == rotulo:
                (idx_par if t.kind in ("paragraph", "generic") else idx_outros).append(i)
        return idx_par + idx_outros

    def numero_perto(self, idx: int, janela: int = 6) -> float | None:
        """O LinkedIn usa dois arranjos na mesma pagina: cartao grande escreve
        VALOR e depois ROTULO ("3.542 / Impressões"); lista de engajamento escreve
        ROTULO e depois VALOR ("Reações / 64"). Quando os dois lados tem numero, o
        numero de tras pertence ao rotulo anterior, entao o valor deste rotulo e o
        de depois. Nada de pescar numero dentro de frase: so token que E o numero."""
        antes = j = idx - 1
        depois = k = idx + 1
        n_antes = numero_limpo(self.tokens[j].texto) if 0 <= j < len(self.tokens) and j not in self.consumidos else None
        n_depois = numero_limpo(self.tokens[k].texto) if 0 <= k < len(self.tokens) and k not in self.consumidos else None
        if n_antes is not None and n_depois is not None:
            dono_do_anterior = 0 <= idx - 2 < len(self.tokens) and self.tokens[idx - 2].texto in ROTULOS_METRICA
            escolhido = (k, n_depois) if dono_do_anterior else (j, n_antes)
        elif n_antes is not None:
            escolhido = (j, n_antes)
        elif n_depois is not None:
            escolhido = (k, n_depois)
        else:
            escolhido = None
        if escolhido:
            self.consumidos.add(escolhido[0])
            return escolhido[1]
        # Sem numero colado nos dois lados (o LinkedIn as vezes mete um botao
        # "Saiba mais" entre rotulo e valor). So procura para frente: o valor de um
        # rotulo nunca aparece solto para tras, e ir para tras pesca o numero do
        # rotulo anterior ("13 / Seguidores obtidos / Engajamento / 84").
        for passo in range(2, janela + 1):
            j2 = idx + passo
            if 0 <= j2 < len(self.tokens) and j2 not in self.consumidos:
                v = numero_limpo(self.tokens[j2].texto)
                if v is not None:
                    self.consumidos.add(j2)
                    return v
        return None

    def metrica(self, rotulo: str, janela: int = 6) -> float | None:
        for idx in self.todas(rotulo):
            v = self.numero_perto(idx, janela)
            if v is not None:
                return v
        return None

    def texto_perto(self, idx: int, janela: int = 2) -> str | None:
        for passo in range(1, janela + 1):
            for j in (idx - passo, idx + passo):
                if 0 <= j < len(self.tokens) and j not in self.consumidos:
                    t = self.tokens[j].texto
                    if t and numero(t) is None:
                        self.consumidos.add(j)
                        return t
        return None

    # -- series temporais -------------------------------------------------

    def serie_diaria(self, unidade: str) -> list[dict]:
        """Le os pontos do grafico: img 'sexta-feira, 25 de set. de 2026, 3.542. Impressões.'"""
        pontos = []
        for t in self.tokens:
            if t.kind != "img" or unidade.lower() not in t.texto.lower():
                continue
            m = re.search(r"(\d{1,2}) de (\w{3})\.? de (\d{4}),\s*([\d.,]+)", t.texto)
            if not m:
                continue
            dia, mes, ano, valor = m.groups()
            mes_num = MESES_PT.get(mes.lower()[:3])
            if not mes_num:
                continue
            pontos.append({
                "data": f"{ano}-{mes_num:02d}-{int(dia):02d}",
                "valor": numero(valor),
            })
        return pontos

    # -- demografia -------------------------------------------------------

    def demografia(self) -> dict:
        """Blocos 'Dimensao / valor / pct%' do painel Principais dados demograficos."""
        fora = {}
        i = 0
        while i < len(self.tokens):
            t = self.tokens[i].texto
            if t in ROTULOS_DIM and i + 2 < len(self.tokens):
                valor = self.tokens[i + 1].texto
                pct = self.tokens[i + 2].texto
                if "%" in pct and valor not in ROTULOS_DIM:
                    pct_v = numero(pct)
                    if pct_v is not None:
                        fora[t] = {"valor": valor, "pct": pct_v, "bruto": pct.strip()}
                        i += 3
                        continue
            i += 1
        return fora

    # -- lista de posts de melhor desempenho ------------------------------

    def top_posts(self) -> list[dict]:
        """Blocos 'N impressões • M engajamentos / Ver análise' da lista de melhores posts.

        Cada bloco traz o URN de atividade (link para a análise), o URN do share (link do
        post) e o texto publicado. O texto aparece em pedaços: fica o maior pedaço de
        texto interno, que é o que casa com os arquivos do workspace.
        """
        posts: list[dict] = []
        atual: dict | None = None
        bloco_inicio = 0

        def fechar(ate: int):
            nonlocal atual
            if atual and atual.get("activity_urn"):
                txt = texto_publicado(self.tokens, bloco_inicio, ate)
                if txt:
                    atual["texto"] = txt
                    posts.append(atual)
            atual = None

        for i, t in enumerate(self.tokens):
            if t.kind == "link" and "Ver análise" in t.texto and "engajament" in t.texto.lower():
                fechar(i)
                m = re.match(r"([\d.,]+)\s*impress\S*\s*•\s*([\d.,]+)\s*engajament", t.texto, re.I)
                atual = {
                    "impressoes_janela": numero(m.group(1)) if m else None,
                    "engajamentos_janela": numero(m.group(2)) if m else None,
                    "activity_urn": None,
                    "share_urn": None,
                }
                bloco_inicio = i + 1
                continue
            if atual is not None and (t.texto.startswith("LinkedIn Corporation") or t.texto == "Exibir mais"):
                # fim do bloco: sem isso o ultimo post da lista engole o rodape da pagina
                fechar(i)
                continue
            if atual is None:
                continue
            if t.kind == "url":
                if atual["activity_urn"] is None:
                    m = RE_ACTIVITY.search(t.texto)
                    if m:
                        atual["activity_urn"] = f"urn:li:activity:{m.group(1)}"
                        continue
                if atual["share_urn"] is None and "feed/update" in t.texto:
                    m = RE_SHARE.search(t.texto)
                    if m:
                        atual["share_urn"] = f"urn:li:share:{m.group(1)}"
        fechar(len(self.tokens))
        vistos, unicos = set(), []
        for p in posts:
            if p["activity_urn"] in vistos:
                continue
            vistos.add(p["activity_urn"])
            unicos.append(p)
        return unicos

    def lista_posts(self) -> list[dict]:
        """Tabela completa de melhores posts da janela ("Exibir mais").

        Cada bloco começa no link do feed e termina no "Aumento de N impressões", que é a
        variação dentro da janela. Traz também reações e comentários da janela e a idade
        da publicação. É a única página que enumera os posts todos, e não só os três
        primeiros, por isso é ela que revela o acervo.
        """
        tokens = self.tokens
        blocos: list[dict] = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if not (t.kind == "url" and t.texto.startswith("/feed/update/urn:li:activity:")):
                i += 1
                continue
            m = RE_ACTIVITY.search(t.texto)
            bloco = {
                "activity_urn": f"urn:li:activity:{m.group(1)}" if m else None,
                "share_urn": None, "texto": "", "idade": None,
                "impressoes_janela": None, "reacoes_janela": None, "comentarios_janela": None,
            }
            fragmentos: list[str] = []
            genericos: list[str] = []
            j = i + 1
            while j < len(tokens):
                s = tokens[j]
                if s.kind == "url" and s.texto.startswith("/feed/update/urn:li:activity:"):
                    break
                if s.kind in ("link", "button"):
                    if s.texto.startswith("Aumento de"):
                        bruto = s.texto.replace("Aumento de", "").split("impress")[0]
                        bloco["impressoes_janela"] = numero_limpo(bruto.strip())
                    elif re.match(r"^\d+\s+rea", s.texto):
                        # reações vêm como button ("15 reações"), comentários como link
                        bloco["reacoes_janela"] = numero_limpo(s.texto.split()[0])
                    elif re.match(r"^\d+\s+coment", s.texto):
                        bloco["comentarios_janela"] = numero_limpo(s.texto.split()[0])
                    elif "publicou isso" in s.texto:
                        mi = re.search(r"(\d+)\s*(sem|dia|dias|semana|semanas|m[êe]s|meses)", s.texto)
                        if mi:
                            bloco["idade"] = f"{mi.group(1)} {mi.group(2)}"
                if s.kind == "text" and len(s.texto) >= 25 and not any(c in s.texto for c in TEXTOS_DE_CONTROLE):
                    fragmentos.append(s.texto)
                elif s.kind == "generic" and len(s.texto) >= 25 and not any(c in s.texto for c in TEXTOS_DE_CONTROLE):
                    genericos.append(s.texto)
                j += 1
            junto = " ".join(dict.fromkeys(fragmentos)).strip()
            bloco["texto"] = junto if len(junto) >= 120 else (max(genericos, key=len) if genericos else junto)
            blocos.append(bloco)
            i = j
        return [b for b in blocos if b["activity_urn"]]


# ---------------------------------------------------------------- interpretacao por tipo de pagina


def tipo_da_pagina(snapshot: str, url: str) -> str:
    if "/analytics/post-summary/" in url:
        return "post"
    if "/analytics/creator/audience/" in url:
        return "publico"
    if "/analytics/creator/top-posts/" in url:
        return "lista"
    if "/analytics/creator/content/" in url:
        return "conteudo"
    if "Total de seguidores" in snapshot:
        return "publico"
    if "Aumento de " in snapshot and "impressões" in snapshot and "Desempenho do conteúdo" not in snapshot:
        return "lista"
    if "Desempenho do conteúdo" in snapshot or "Desempenho do conteudo" in snapshot:
        return "conteudo"
    if "Análise da publicação" in snapshot or "Analise da publicacao" in snapshot:
        return "post"
    return "desconhecido"


def parse_conteudo(snapshot: str, url: str, capturado_em: str) -> dict:
    p = Pagina(tokenizar(snapshot))
    janela = None
    m = re.search(r"timeRange=([a-z0-9_]+)", url)
    if m:
        janela = m.group(1)
    dados = {
        "tipo": "conteudo",
        "url": url,
        "capturado_em": capturado_em,
        "periodo": janela,
        "impressoes": p.metrica("Impressões"),
        "variacao_pct": p.metrica("em relação a 7 dias anteriores"),
        "usuarios_alcancados": p.metrica("Usuários alcançados"),
        "na_rede_pct": p.metrica("Na rede (seguidores e conexões)"),
        "fora_da_rede_pct": p.metrica("Fora da rede"),
        "engajamento_total": p.metrica("Engajamento nas redes"),
        "reacoes": p.metrica("Reações"),
        "comentarios": p.metrica("Comentários"),
        "compartilhamentos": p.metrica("Compartilhamentos"),
        "salvamentos": p.metrica("Salvamentos"),
        "envios": p.metrica("Envios no LinkedIn"),
        "serie_diaria": p.serie_diaria("Impress"),
        "demografia": p.demografia(),
        "top_posts": p.top_posts(),
    }
    return dados


def parse_lista(snapshot: str, url: str, capturado_em: str) -> dict:
    """Página de lista de melhores posts: enumera o acervo da janela, sem agregado."""
    p = Pagina(tokenizar(snapshot))
    m = re.search(r"timeRange=([a-z0-9_]+)", url)
    posts = p.lista_posts()
    # o URN do share vem do segundo link do feed, que aparece dentro do bloco; guardamos
    # aqui em uma segunda passada porque o link do feed usa URL absoluta com query
    for bloco in posts:
        for t in p.tokens:
            if t.kind == "url" and "feed/update" in t.texto and bloco["activity_urn"] and bloco["activity_urn"].split(":")[-1] in t.texto:
                ms = RE_SHARE.search(t.texto)
                if ms:
                    bloco["share_urn"] = f"urn:li:share:{ms.group(1)}"
                    break
    return {
        "tipo": "lista",
        "url": url,
        "capturado_em": capturado_em,
        "periodo": m.group(1) if m else None,
        "posts": posts,
    }


def parse_post(snapshot: str, url: str, capturado_em: str) -> dict:
    p = Pagina(tokenizar(snapshot))
    m = RE_ACTIVITY.search(url)
    activity = f"urn:li:activity:{m.group(1)}" if m else None
    share = None
    for exigir_feed in (True, False):
        for t in p.tokens:
            if t.kind != "url" or (exigir_feed and "feed/update" not in t.texto):
                continue
            ms = RE_SHARE.search(t.texto)
            if ms:
                share = f"urn:li:share:{ms.group(1)}"
                break
        if share:
            break

    # texto publicado: fica entre o cabecalho "publicou" e a secao Descoberta
    tokens = p.tokens
    inicio = None
    for i, t in enumerate(tokens):
        if t.kind == "link" and "publicou" in t.texto:
            inicio = i
    fim = len(tokens)
    for i, t in enumerate(tokens):
        if t.texto == "Descoberta" and (inicio is None or i > inicio):
            fim = i
            break
    trechos_inicio = (inicio + 1) if inicio is not None else 0
    texto = texto_publicado(tokens, trechos_inicio, fim)

    idade = None
    mi = re.search(r"publicou\s*•\s*(\d+)\s*(sem|dia|dias|semana|semanas|m[êe]s|meses)", snapshot)
    if mi:
        idade = f"{mi.group(1)} {mi.group(2)}"

    # Ordem importa: o consumo dos numeros depende de quem le primeiro. O total de
    # engajamento vem antes do detalhamento, e o detalhamento antes de salvamentos,
    # porque cada rotulo usa o numero que esta imediatamente ao lado dele.
    dados = {
        "tipo": "post",
        "origem": "pagina-do-post",
        "url": url,
        "capturado_em": capturado_em,
        "activity_urn": activity,
        "share_urn": share,
        "idade_legivel": idade,
        "texto": texto.strip(),
        "impressoes": p.metrica("Impressões"),
        "usuarios_alcancados": p.metrica("Usuários alcançados"),
        "na_rede_pct": p.metrica("Na rede (seguidores e conexões)"),
        "fora_da_rede_pct": p.metrica("Fora da rede"),
        "engajamento_total": None,
        "reacoes": None,
        "comentarios": None,
        "compartilhamentos": None,
        "salvamentos": None,
        "envios": None,
        "visualizacoes_perfil": None,
        "seguidores_ganhos": None,
        "demografia": {},
    }
    dados["engajamento_total"] = p.metrica("Engajamento") or p.metrica("Engajamento nas redes")
    dados["reacoes"] = p.metrica("Reações")
    dados["comentarios"] = p.metrica("Comentários")
    dados["compartilhamentos"] = p.metrica("Compartilhamentos")
    dados["salvamentos"] = p.metrica("Salvamentos")
    dados["envios"] = p.metrica("Envios no LinkedIn")
    dados["visualizacoes_perfil"] = p.metrica("Visualizações do perfil a partir desta publicação")
    dados["seguidores_ganhos"] = p.metrica("Seguidores obtidos com esta publicação")
    dados["demografia"] = p.demografia()
    soma = sum(v for v in (dados["reacoes"], dados["comentarios"], dados["compartilhamentos"],
                           dados["salvamentos"], dados["envios"]) if v)
    if dados["engajamento_total"] is None and soma:
        dados["engajamento_total"] = soma
    return dados


def parse_publico(snapshot: str, url: str, capturado_em: str) -> dict:
    p = Pagina(tokenizar(snapshot))
    dados = {
        "tipo": "publico",
        "url": url,
        "capturado_em": capturado_em,
        "total_seguidores": p.metrica("Total de seguidores"),
        "variacao_pct": p.metrica("em relação a 7 dias anteriores"),
        "novos_seguidores": None,
        "serie_diaria": p.serie_diaria("Novos seguidores"),
        "demografia": p.demografia(),
    }
    if dados["serie_diaria"]:
        dados["novos_seguidores"] = dados["serie_diaria"][-1]["valor"]
    return dados


def parse_snapshot(caminho: Path, capturado_em: str | None = None) -> dict:
    bruto = caminho.read_text(encoding="utf-8", errors="replace")
    url = ""
    m = re.search(r"^URL:\s*(\S+)", bruto, re.M)
    if m:
        url = m.group(1)
    if not capturado_em:
        mc = re.search(r"(\d{4}-\d{2}-\d{2})", caminho.name)
        capturado_em = mc.group(1) if mc else dt.date.today().isoformat()
    tipo = tipo_da_pagina(bruto, url)
    if tipo == "conteudo":
        return parse_conteudo(bruto, url, capturado_em)
    if tipo == "post":
        return parse_post(bruto, url, capturado_em)
    if tipo == "publico":
        return parse_publico(bruto, url, capturado_em)
    if tipo == "lista":
        return parse_lista(bruto, url, capturado_em)
    return {"tipo": "desconhecido", "arquivo": str(caminho), "url": url, "capturado_em": capturado_em}


# ---------------------------------------------------------------- store


def carregar_store(base: Path) -> dict:
    arq = base / "linkedin-metricas.json"
    if arq.exists():
        try:
            return json.loads(arq.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = arq.with_suffix(".json.invalido")
            arq.replace(backup)
            print(f"aviso: store ilegivel, movido para {backup}", file=sys.stderr)
    return {"versao": VERSAO, "posts": {}, "conta": {"coletas": [], "agregados": []}, "coletas": []}


def salvar_store(base: Path, store: dict) -> None:
    base.mkdir(parents=True, exist_ok=True)
    arq = base / "linkedin-metricas.json"
    tmp = arq.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2, sort_keys=False), encoding="utf-8")
    tmp.replace(arq)


def fundir_post(store: dict, dado: dict) -> bool:
    urn = dado.get("activity_urn")
    if not urn:
        return False
    post = store["posts"].setdefault(urn, {"activity_urn": urn, "historico": []})
    for chave in ("share_urn", "idade_legivel"):
        if dado.get(chave):
            post[chave] = dado[chave]
    if dado.get("texto"):
        if dado.get("origem") == "pagina-do-post" or not post.get("texto"):
            post["texto"] = dado["texto"]
    # A lista de melhores posts identifica o post e dá os números DA JANELA, mas não é
    # coleta de tempo de vida: gravar aqui como coleta encheria o histórico de nulos e
    # sobrescreveria a última medição boa do post.
    if dado.get("historico_janela"):
        post["historico_janela"] = dict(dado["historico_janela"], periodo=dado.get("periodo"),
                                        capturado_em=dado["capturado_em"])
    tem_metricas = any(dado.get(k) is not None for k in (
        "impressoes", "usuarios_alcancados", "engajamento_total", "salvamentos",
        "visualizacoes_perfil", "seguidores_ganhos", "reacoes"))
    if not tem_metricas:
        return True
    # metricas: guardar o ultimo valor e o historico de coletas
    instantaneo = {
        "capturado_em": dado["capturado_em"],
        "impressoes": dado.get("impressoes"),
        "usuarios_alcancados": dado.get("usuarios_alcancados"),
        "na_rede_pct": dado.get("na_rede_pct"),
        "fora_da_rede_pct": dado.get("fora_da_rede_pct"),
        "engajamento_total": dado.get("engajamento_total"),
        "reacoes": dado.get("reacoes"),
        "comentarios": dado.get("comentarios"),
        "compartilhamentos": dado.get("compartilhamentos"),
        "salvamentos": dado.get("salvamentos"),
        "envios": dado.get("envios"),
        "visualizacoes_perfil": dado.get("visualizacoes_perfil"),
        "seguidores_ganhos": dado.get("seguidores_ganhos"),
        "demografia": dado.get("demografia") or {},
    }
    post["historico"] = [h for h in post["historico"] if h.get("capturado_em") != dado["capturado_em"]]
    post["historico"].append(instantaneo)
    post["historico"].sort(key=lambda h: h["capturado_em"])
    post["ultima"] = instantaneo
    return True


def ingerir(base: Path, caminhos: list[Path]) -> dict:
    store = carregar_store(base)
    relato = {"arquivos": 0, "posts": 0, "conteudo": 0, "lista": 0, "publico": 0, "desconhecido": 0}
    for caminho in caminhos:
        relato["arquivos"] += 1
        dado = parse_snapshot(caminho)
        store["coletas"].append({"arquivo": str(caminho), "tipo": dado.get("tipo"), "em": dado.get("capturado_em")})
        if dado["tipo"] == "post":
            if fundir_post(store, dado):
                relato["posts"] += 1
        elif dado["tipo"] == "conteudo":
            # só guarda o agregado se a página trouxe os números da janela: uma página de
            # lista não tem agregado, e entrar como "último" apagaria a janela boa
            if dado.get("impressoes") is not None:
                store["conta"]["agregados"].append(dado)
            for tp in dado.get("top_posts", []):
                fundir_post(store, {
                    "tipo": "post",
                    "capturado_em": dado["capturado_em"],
                    "periodo": dado.get("periodo"),
                    "activity_urn": tp["activity_urn"],
                    "share_urn": tp["share_urn"],
                    "texto": tp["texto"],
                    "historico_janela": {
                        "impressoes_janela": tp["impressoes_janela"],
                        "engajamentos_janela": tp["engajamentos_janela"],
                    },
                })
            relato["conteudo"] += 1
        elif dado["tipo"] == "lista":
            for item in dado.get("posts", []):
                fundir_post(store, {
                    "tipo": "post",
                    "capturado_em": dado["capturado_em"],
                    "periodo": dado.get("periodo"),
                    "activity_urn": item["activity_urn"],
                    "share_urn": item.get("share_urn"),
                    "texto": item.get("texto") or "",
                    "idade_legivel": item.get("idade"),
                    "historico_janela": {
                        "impressoes_janela": item.get("impressoes_janela"),
                        "reacoes_janela": item.get("reacoes_janela"),
                        "comentarios_janela": item.get("comentarios_janela"),
                    },
                })
            relato["lista"] += 1
        elif dado["tipo"] == "publico":
            store["conta"]["coletas"].append(dado)
            relato["publico"] += 1
        else:
            relato["desconhecido"] += 1
    salvar_store(base, store)
    return relato


# ---------------------------------------------------------------- atributos do texto

PALAVRAS_PRAZO = [
    "end of support", "ends", "eol", "deprecat", "sunset", "fim de suporte", "prazo",
    "deadline", "expira", "last security patch", "breaking change", "until", "até",
]
PALAVRAS_SALVAVEL = [
    "checklist", "step", "passo", "before", "antes de", "how to", "como ", "list",
    "compare", "comparativo", "template", "guide", "guia", "trade-off", "tradeoff",
]


def atributos_texto(texto: str) -> dict:
    linhas = [l.strip() for l in texto.strip().splitlines() if l.strip()]
    hook = linhas[0] if linhas else ""
    primeira_parte = texto.strip()[:210]
    nb = normalizar(texto)
    # o texto pode vir em linhas (arquivo) ou juntado em uma linha so (capturado do
    # LinkedIn): a contagem de itens vale nos dois casos
    bullets = len(re.findall(r"(?:^|\s)[\u2192\u2022\u25aa\u25cf\*](?=\s)", texto))
    bullets += len([l for l in linhas if re.match(r"^-\s+", l)])
    hashtags = re.findall(r"#\w+", texto)
    pergunta_final = bool(re.search(r"\?\s*(?:#\w+\s*)*$", texto.strip()))
    numero_no_hook = bool(re.search(r"\d", hook))
    data_no_hook = bool(re.search(r"\b(19|20)\d{2}\b|\b\d{1,2} de \w+|\b(january|february|march|april|may|june|july|august|september|october|november|december)\b", hook, re.I))
    return {
        "caracteres": len(texto.strip()),
        "primeiros_210": primeira_parte,
        "hook": hook[:180],
        "hook_com_numero": numero_no_hook,
        "hook_com_data": data_no_hook,
        "bullets": bullets,
        "hashtags": len(hashtags),
        "pergunta_no_fim": pergunta_final,
        "ancora_de_prazo": any(p in nb for p in PALAVRAS_PRAZO),
        "material_salvavel": any(p in nb for p in PALAVRAS_SALVAVEL) or bullets >= 3,
        "tem_link_externo": bool(re.search(r"https?://", texto)),
        "idioma": "pt" if re.search(r"\b(que|não|para|com|uma|você|seu|sua)\b", nb) else "en",
    }


def carregar_posts_workspace(workspace: Path) -> list[dict]:
    arquivos = sorted(workspace.glob("post-*.md"))
    posts = []
    for arq in arquivos:
        texto = arq.read_text(encoding="utf-8", errors="replace")
        # tira titulo markdown, mas nunca a linha de hashtags (que tambem comeca com #)
        texto = re.sub(r"^#{1,6}\s+\S.*$", "", texto, flags=re.M).strip()
        if len(texto) < 200:
            continue
        attr = atributos_texto(texto)
        attr["arquivo"] = arq.name
        attr["texto"] = texto
        attr["mtime"] = dt.date.fromtimestamp(arq.stat().st_mtime).isoformat()
        posts.append(attr)
    return posts


def casa_com_arquivo(store: dict, posts_workspace: list[dict]) -> None:
    """Liga cada post com metrica ao arquivo post-*.md correspondente, por similaridade do inicio."""
    for urn, post in store["posts"].items():
        if post.get("arquivo"):
            continue
        texto = post.get("texto") or ""
        if len(texto) < 120:
            continue
        melhor, score = None, 0.0
        for cand in posts_workspace:
            limite = min(len(texto), len(cand["texto"]))
            s = similaridade(texto[:limite][:400], cand["texto"][:min(400, limite)])
            if s > score:
                melhor, score = cand, s
        if melhor and score >= 0.72:
            post["arquivo"] = melhor["arquivo"]
            post["similaridade_arquivo"] = round(score, 3)
            melhor.setdefault("urns", []).append(urn)
            post["atributos"] = {k: v for k, v in melhor.items() if k not in ("texto",)}


# ---------------------------------------------------------------- relatorio


# ---------------------------------------------------------------- tipos e pontuação
#
# Foco definido por ele em 24/09/2026: posts de autoridade, onde a densidade é maior que o
# alcance. As tags internas registram o tipo de cada post e as pontuações (todas por mil
# impressões) medem densidade. A heurística atribui; o ajuste fino é manual, em
# tipos-manuais.json (URN -> lista de tags, a primeira é a principal e vence a heurística).

TIPOS_POST = {
    # a ordem de definição é a prioridade: o primeiro tipo cuja palavra casar vira o principal
    "mudanca-com-prazo": [
        "end of support", "support does not end", "support ends", "eol", "deprecat",
        "sunset", "breaking change", "fim de suporte", "expira", "last security patch",
        "leaves chatgpt", "descontinu",
    ],
    "resiliencia": [
        "retry", "idempoten", "incidente", "incident", "stampede", "rollback", "timeout",
        "circuit breaker", "fallback", "duplicada", "cobranc",
    ],
    "custo": [
        "invoice", "fatura", "charges ", "pricing", "preco", "custo", "cost per", "por resultado",
    ],
    "meta-conteudo": [
        "substack", "digest", "recap", "doze temas", "twelve topics", "newsletter",
    ],
    "ia-em-producao": [
        " llm", "llms", "modelo", "model", "agent", "harness", "triagem", "prompt",
        "fine-tun", " claude", "gpt", "openai", "anthropic", "machine learning",
    ],
    "decisao-arquitetura": [
        "adr", "trade-off", "tradeoff", "chose not", "arquitet", " fila", "queue", "cache",
        "acopla", "camada", "migra", "banco trocavel", "ordering", "design",
    ],
}
ORDEM_TIPOS = list(TIPOS_POST)

# as pontuações, todas por mil impressões: densidade é a métrica principal do motor de
# autoridade; as outras quatro qualificam o tipo de atenção que o post recebeu
SCORES_DENSIDADE = [
    ("engajamento_por_1k", "Densidade (engajamento/1k)"),
    ("comentarios_por_1k", "Conversa (comentários/1k)"),
    ("salvamentos_por_1k", "Utilidade (salvamentos/1k)"),
    ("views_perfil_por_1k", "Atração (views perfil/1k)"),
    ("seguidores_por_1k", "Conversão (seguidores/1k)"),
]


def classificar_tipos(texto: str) -> tuple[str, list[str]]:
    """Heurística de palavras-chave sobre o texto normalizado. A primeira tag da lista é
    a principal. Erra para o lado do genérico: o ajuste fino é manual, não aqui."""
    nb = f" {normalizar(texto)} "
    tags = [tipo for tipo in ORDEM_TIPOS if any(p in nb for p in TIPOS_POST[tipo])]
    return (tags[0] if tags else "outro"), tags


def carregar_ajustes_manuais(base: Path) -> dict:
    arq = base / "tipos-manuais.json"
    if arq.exists():
        try:
            return json.loads(arq.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(f"aviso: {arq} ilegível, ignorado", file=sys.stderr)
    return {}


def aplicar_tipos(store: dict, base: Path) -> None:
    """Anota tipo e tags em todos os posts: ajuste manual vence, heurística preenche."""
    manuais = carregar_ajustes_manuais(base)
    for urn, post in store["posts"].items():
        if urn in manuais and isinstance(manuais[urn], list) and manuais[urn]:
            post["tags"] = list(manuais[urn])
            post["tipo"] = manuais[urn][0]
            post["origem_tipo"] = "manual"
            continue
        tipo, tags = classificar_tipos(post.get("texto") or "")
        post["tags"] = tags
        post["tipo"] = tipo
        post["origem_tipo"] = "heuristica" if tipo != "outro" else "sem-casamento"


def scores_densidade(u: dict) -> dict:
    imp = u.get("impressoes")
    if not imp:
        return {}
    return {
        "engajamento_por_1k": round(1000 * (u.get("engajamento_total") or 0) / imp, 2),
        "comentarios_por_1k": round(1000 * (u.get("comentarios") or 0) / imp, 2),
        "salvamentos_por_1k": round(1000 * (u.get("salvamentos") or 0) / imp, 2),
        "views_perfil_por_1k": round(1000 * (u.get("visualizacoes_perfil") or 0) / imp, 2),
        "seguidores_por_1k": round(1000 * (u.get("seguidores_ganhos") or 0) / imp, 2),
    }


def scorecards_por_tipo(store: dict) -> list[dict]:
    """Mediana das pontuações por tipo de post. É o aprendizado: com coletas novas, a
    tabela diz qual tipo entrega densidade e qual só entrega volume."""
    grupos: dict[str, list[dict]] = {}
    for p in store["posts"].values():
        if not (p.get("ultima") or {}).get("impressoes"):
            continue
        grupos.setdefault(p.get("tipo") or "outro", []).append(p)
    saida = []
    for tipo, posts in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        linha: dict = {
            "tipo": tipo,
            "n": len(posts),
            "activity_urns": [p["activity_urn"] for p in posts],
            "mediana_impressoes": mediana([p["ultima"]["impressoes"] for p in posts]),
        }
        por_post = [scores_densidade(p["ultima"]) for p in posts]
        for chave, _ in SCORES_DENSIDADE:
            vals = [s[chave] for s in por_post if chave in s]
            linha[chave] = mediana(vals) if vals else None
        saida.append(linha)
    return saida


def preparar_atributos(store: dict, workspace: Path, base: Path | None = None) -> list[dict]:
    """Liga cada post com métrica ao arquivo do workspace, completa atributos pelo texto
    publicado e anota tipo/tags. O relatório e a exportação usam isto, para os dois
    falarem dos mesmos atributos."""
    posts_workspace = carregar_posts_workspace(workspace)
    casa_com_arquivo(store, posts_workspace)
    for post in store["posts"].values():
        if post.get("atributos"):
            continue
        texto = post.get("texto") or ""
        if len(texto) >= 120:
            post["atributos"] = atributos_texto(texto)
            post["atributos"]["origem"] = "texto publicado"
            post["atributos"]["arquivo"] = None
        else:
            post.setdefault("atributos", {})
    aplicar_tipos(store, base or diretorio_padrao())
    return posts_workspace


def mediana(valores: list[float]) -> float | None:
    vals = sorted(v for v in valores if isinstance(v, (int, float)))
    if not vals:
        return None
    n = len(vals)
    meio = n // 2
    return vals[meio] if n % 2 else (vals[meio - 1] + vals[meio]) / 2


def fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float) and v != int(v):
        return f"{v:,.1f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"{int(v):,}".replace(",", ".")


def pct(parte, todo) -> str:
    if not parte or not todo:
        return "—"
    return f"{100 * parte / todo:.1f}%".replace(".", ",")


def linhas_relatorio(store: dict, workspace: Path) -> str:
    alvo = caminho_alvo()
    posts = list(store["posts"].values())
    for post in posts:
        post.setdefault("atributos", {})
    com_metrica = [p for p in posts if (p.get("ultima") or {}).get("impressoes")]

    out: list[str] = []
    datas = [(c.get("capturado_em") or c.get("em")) for c in (store.get("coletas") or [])
             if (c.get("capturado_em") or c.get("em"))]
    coleta = max(datas) if datas else dt.date.today().isoformat()
    out.append(f"# Diagnóstico de posts do LinkedIn — coleta de {coleta}")
    out.append("")
    out.append("Gerado por `terras-linkedin-metricas`. Fonte: páginas de análise do próprio LinkedIn (snapshots salvos em `metricas/raw/`).")
    out.append("")

    # os atributos já vêm prontos de preparar_atributos (arquivo do workspace ou texto
    # publicado); aqui só garante a chave para o resto do relatório não tropeçar
    for post in posts:
        post.setdefault("atributos", {})

    colecoes = store["conta"].get("coletas") or []
    if colecoes:
        seg = colecoes[-1]
        out.append("## Conta")
        out.append("")
        out.append(f"- Seguidores: **{fmt(seg.get('total_seguidores'))}** (variação {fmt(seg.get('variacao_pct'))}% vs período anterior)")
        if seg.get("novos_seguidores") is not None:
            out.append(f"- Novos seguidores na janela: **{fmt(seg.get('novos_seguidores'))}**")
        out.append("")

    agregados = store["conta"].get("agregados") or []
    if agregados:
        ag = agregados[-1]
        out.append(f"### Janela `{ag.get('periodo') or 'padrão'}` (coleta {ag['capturado_em']})")
        out.append("")
        out.append(f"- Impressões: **{fmt(ag.get('impressoes'))}** ({fmt(ag.get('variacao_pct'))}% vs janela anterior)")
        out.append(f"- Usuários alcançados: **{fmt(ag.get('usuarios_alcancados'))}** · na rede {fmt(ag.get('na_rede_pct'))}% · fora da rede {fmt(ag.get('fora_da_rede_pct'))}%")
        out.append(
            f"- Engajamento: {fmt(ag.get('engajamento_total'))} total · "
            f"{fmt(ag.get('reacoes'))} reações · {fmt(ag.get('comentarios'))} comentários · "
            f"{fmt(ag.get('compartilhamentos'))} compartilhamentos · {fmt(ag.get('salvamentos'))} salvamentos"
        )
        out.append("")
        if ag.get("demografia"):
            out.append("| Dimensão | Maior fatia (janela) | % |")
            out.append("|---|---|---|")
            for dim, val in ag["demografia"].items():
                p = val.get("bruto") if val["pct"] == 0 and val.get("bruto") else f"{fmt(val['pct'])}%"
                out.append(f"| {dim} | {val['valor']} | {p if p.endswith('%') else p + '%'} |")
            out.append("")

    if not com_metrica:
        out.append("## Posts")
        out.append("")
        out.append("Nenhum post com métrica de tempo de vida ainda. Abra a análise de cada post e ingira o snapshot.")
        return "\n".join(out)

    # -------- tabela comparativa
    out.append("## Posts com métrica")
    out.append("")
    out.append("| # | Post | Idioma | Car. | Impressões | Alcance | Fora da rede | Engaj. | Salvos | Coment. | Views perfil | Seguidores |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    ordenados = sorted(com_metrica, key=lambda p: p["ultima"]["impressoes"], reverse=True)
    for i, p in enumerate(ordenados, 1):
        u = p["ultima"]
        a = p.get("atributos") or {}
        rotulo = a.get("arquivo") or (p.get("texto") or "")[:40] or p["activity_urn"]
        out.append(
            f"| {i} | {rotulo} | {a.get('idioma', '?')} | {fmt(a.get('caracteres'))} | "
            f"{fmt(u.get('impressoes'))} | {fmt(u.get('usuarios_alcancados'))} | "
            f"{fmt(u.get('fora_da_rede_pct'))}% | {fmt(u.get('engajamento_total'))} | "
            f"{fmt(u.get('salvamentos'))} | {fmt(u.get('comentarios'))} | "
            f"{fmt(u.get('visualizacoes_perfil'))} | {fmt(u.get('seguidores_ganhos'))} |"
        )
    out.append("")

    # -------- ratios de qualidade
    out.append("### Eficiência por post")
    out.append("")
    out.append("| Post | Alcance/Impressões | Salvos/reações | Coment./reações | Views perfil/1k imp. | Seguidores/1k imp. |")
    out.append("|---|---|---|---|---|---|")
    for p in ordenados:
        u = p["ultima"]
        a = p.get("atributos") or {}
        rotulo = a.get("arquivo") or (p.get("texto") or "")[:30]
        alc = pct(u.get("usuarios_alcancados"), u.get("impressoes"))
        salv = pct(u.get("salvamentos"), u.get("reacoes"))
        com = pct(u.get("comentarios"), u.get("reacoes"))
        vp = (1000 * u["visualizacoes_perfil"] / u["impressoes"]) if u.get("visualizacoes_perfil") and u.get("impressoes") else None
        sg = (1000 * u["seguidores_ganhos"] / u["impressoes"]) if u.get("seguidores_ganhos") and u.get("impressoes") else None
        out.append(f"| {rotulo} | {alc} | {salv} | {com} | {fmt(vp)} | {fmt(sg)} |")
    out.append("")

    # -------- vencedor x resto
    imp = [p["ultima"]["impressoes"] for p in ordenados]
    med = mediana(imp)
    maior = ordenados[0]
    out.append("## Vencedor contra a mediana")
    out.append("")
    if len(ordenados) == 1:
        out.append(f"- Amostra de 1 post: **{fmt(maior['ultima'].get('impressoes'))}** impressões.")
        out.append("- Com n = 1 dá para descrever o que este post tinha, não para comparar com os outros. A comparação aparece quando houver pelo menos 2 posts coletados.")
    else:
        out.append(f"- Maior post: **{fmt(maior['ultima'].get('impressoes'))}** impressões · mediana da amostra: **{fmt(med)}** · n = {len(ordenados)}")
        if med:
            out.append(f"- O vencedor rende **{maior['ultima']['impressoes'] / med:.1f}x** a mediana.")
    out.append("")
    vm = maior.get("atributos") or {}
    outra = [p for p in ordenados[1:]]
    if outra:
        out.append("| Atributo | Vencedor | Demais posts |")
        out.append("|---|---|---|")
        for chave, rotulo in (
            ("fora_da_rede_pct", "Fora da rede %"),
            ("caracteres", "Caracteres"),
            ("bullets", "Itens em lista"),
            ("hashtags", "Hashtags"),
            ("hook_com_numero", "Número no hook"),
            ("hook_com_data", "Data no hook"),
            ("ancora_de_prazo", "Âncora de prazo"),
            ("material_salvavel", "Material salvavel"),
            ("pergunta_no_fim", "Pergunta no fim"),
        ):
            if chave in ("fora_da_rede_pct",):
                v = fmt(maior["ultima"].get("fora_da_rede_pct"))
                outros = " / ".join(fmt(p["ultima"].get("fora_da_rede_pct")) for p in outra) or "—"
            else:
                v = str(vm.get(chave, "—"))
                outros = " / ".join(str((p.get("atributos") or {}).get(chave, "—")) for p in outra) or "—"
            out.append(f"| {rotulo} | {v} | {outros} |")
        out.append("")

    # -------- atributo x resultado (so quando ha amostra dos dois lados)
    out.append("## O que separa os posts (amostra pequena, leia como pista)")
    out.append("")
    achados = []
    for chave, rotulo in (
        ("ancora_de_prazo", "âncora de prazo verificável"),
        ("material_salvavel", "material que se salva"),
        ("hook_com_numero", "número no hook"),
        ("hook_com_data", "data no hook"),
        ("pergunta_no_fim", "pergunta no fim"),
    ):
        com = [p["ultima"]["impressoes"] for p in ordenados if (p.get("atributos") or {}).get(chave)]
        sem = [p["ultima"]["impressoes"] for p in ordenados if (p.get("atributos") or {}).get(chave) is False]
        if len(com) >= 2 and len(sem) >= 2:
            mc, ms = mediana(com), mediana(sem)
            razao = mc / ms if ms else float("inf")
            achados.append((razao, rotulo, mc, ms, len(com), len(sem)))
    if achados:
        for razao, rotulo, mc, ms, nc, ns in sorted(achados, reverse=True):
            out.append(f"- **{rotulo}**: mediana {fmt(mc)} impressões com (n={nc}) contra {fmt(ms)} sem (n={ns}) → {razao:.1f}x")
    else:
        out.append("- Amostra insuficiente para separar atributos (é preciso pelo menos 2 posts com e 2 sem cada atributo). Hoje não dá para atribuir causa: dá para descrever o que o vencedor tinha.")
    out.append("")

    # -------- scorecard por tipo: o aprendizado do motor de autoridade
    cartoes = scorecards_por_tipo(store)
    if cartoes:
        out.append("## Pontuação por tipo de post")
        out.append("")
        out.append("Tags internas do texto (heurística + ajuste manual em `tipos-manuais.json`). "
                   "Pontuações por mil impressões. Foco atual: autoridade, onde a densidade "
                   "importa mais que o alcance.")
        out.append("")
        out.append("| Tipo | n | Med. impressões | " + " | ".join(rot for _, rot in SCORES_DENSIDADE) + " |")
        out.append("|---|---|---|" + "---|" * len(SCORES_DENSIDADE))
        for cartao in cartoes:
            valores = " | ".join(fmt(cartao.get(chave)) for chave, _ in SCORES_DENSIDADE)
            out.append(f"| {cartao['tipo']} | {cartao['n']} | {fmt(cartao['mediana_impressoes'])} | {valores} |")
        out.append("")
        out.append("Leitura: impressões altas com pontuação baixa é post de distribuição; "
                   "impressões baixas com densidade alta é post de autoridade, e é o foco. "
                   "Com coletas novas, a tabela diz qual tipo vale repetir.")
        out.append("")

    # -------- cauda da janela: a lista de melhores posts enumera o acervo todo
    jan = sorted([((p.get("historico_janela") or {}).get("impressoes_janela") or 0) for p in posts], reverse=True)
    jan = [v for v in jan if v]
    if jan:
        total_jan = sum(jan)
        top3 = sum(jan[:3])
        sem_coleta = len([p for p in posts if (p.get("historico_janela") or {}).get("impressoes_janela")
                          and not (p.get("ultima") or {}).get("impressoes")])
        out.append("## Cauda da janela")
        out.append("")
        out.append(f"- A lista de melhores posts do LinkedIn enumera **{len(jan)} posts** nesta janela, não só os de cima.")
        out.append(f"- Somando os posts, dá **{fmt(total_jan)}** impressões na janela" +
                   (f" (o agregado da conta marca {fmt(agregados[-1].get('impressoes'))}; a diferença é o intervalo entre as duas leituras)." if agregados else "."))
        out.append(f"- Os 3 primeiros concentram **{fmt(top3)}** ({pct(top3, total_jan)}); o resto se divide por {len(jan) - 3} posts.")
        out.append(f"- {len([v for v in jan if v <= 10])} posts ficaram em 10 impressões ou menos na janela.")
        if sem_coleta:
            out.append(f"- {sem_coleta} desses posts ainda não têm coleta de tempo de vida (só o recorte da janela). "
                       "Colher a página individual deles é o que falta para o comparativo pegar o acervo.")
        out.append("")

    # -------- audiencia
    out.append("## Público alcançado contra o público que você quer")
    out.append("")
    out.append(f"Alvo declarado: {alvo['descricao']}.")
    out.append("")
    if colecoes:
        dem = colecoes[-1].get("demografia") or {}
        out.append("Seguidores:")
        out.append("")
        for dim in ("Nível de experiência", "Localidade", "Setor", "Cargo", "Empresa", "Tamanho da empresa"):
            if dim in dem:
                valor = dem[dim]["valor"]
                marca = ""
                if dim == "Nível de experiência":
                    marca = " ✅ alinhado" if valor in alvo["senioridades"] else " ⚠️ fora do alvo"
                if dim == "Localidade":
                    marca = " ✅ alvo internacional" if any(l in valor for l in alvo["localidades"]) else " ⚠️ fora do alvo internacional"
                out.append(f"- {dim}: **{valor}** ({fmt(dem[dim]['pct'])}%){marca}")
        out.append("")
    if agregados:
        dem = agregados[-1].get("demografia") or {}
        out.append("Quem foi alcançado na janela:")
        out.append("")
        for dim in ("Nível de experiência", "Cargo", "Setor", "Localidade", "Tamanho da empresa"):
            if dim in dem:
                valor, p = dem[dim]["valor"], fmt(dem[dim]["pct"])
                marca = ""
                if dim == "Nível de experiência" and valor not in alvo["senioridades"]:
                    marca = f" ⚠️ fora do alvo (você busca {'/'.join(alvo['senioridades'][:2])})"
                if dim == "Localidade" and not any(l in valor for l in alvo["localidades"]):
                    marca = " ⚠️ nenhuma praça do alvo internacional nesta janela"
                p = dem[dim].get("bruto") if dem[dim]["pct"] == 0 and dem[dim].get("bruto") else f"{p}%"
                out.append(f"- {dim}: **{valor}** ({p if p.endswith('%') else p + '%'}){marca}")
        out.append("")
    if len(ordenados) >= 2:
        melhor_pub = ordenados[0]
        dem = melhor_pub["ultima"].get("demografia") or {}
        out.append("Público do post que estourou:")
        out.append("")
        for dim, val in dem.items():
            out.append(f"- {dim}: **{val['valor']}** ({fmt(val['pct'])}%)")
        out.append("")
    # leitura: o post que sai da rede puxa o publico que voce quer, o comum nao
    if agregados and ordenados:
        dem_janela = agregados[-1].get("demografia") or {}
        dem_venc = ordenados[0]["ultima"].get("demografia") or {}
        if "Nível de experiência" in dem_janela and "Nível de experiência" in dem_venc:
            fora = dem_venc.get("Localidade", {}).get("valor")
            out.append("Leitura:")
            out.append("")
            out.append(
                f"- A média da janela é puxada para **{dem_janela['Nível de experiência']['valor']}** "
                f"(o público que consome qualquer assunto), enquanto o post que saiu da rede alcançou "
                f"**{dem_venc['Nível de experiência']['valor']}**"
                + (f" e teve **{fora}** como principal praça" if fora else "")
                + "."
            )
            out.append("- Ou seja: o assunto é que decide quem chega, não a voz nem o idioma. Post de nicho devolve a audiência que já te segue; post com prazo e consequência de mercado traz quem você quer alcançar.")
            out.append("")

    # -------- pendencias
    out.append("## Pendências de coleta")
    out.append("")
    sem_metric = [p for p in posts if not (p.get("ultima") or {}).get("impressoes")]
    out.append(f"- Posts vistos na lista de melhores posts e sem métrica de tempo de vida: {len(sem_metric)}")
    for p in sem_metric[:12]:
        out.append(f"  - `{p['activity_urn']}` — {(p.get('texto') or '')[:60]}")
    if len(sem_metric) > 12:
        out.append(f"  - ... e mais {len(sem_metric) - 12}")
    # conta por slug: o workspace guarda variantes (pt, en-long, en-short) do mesmo post
    slugs = set()
    for a in workspace.glob("post-*.md"):
        nome = a.stem
        for sufixo in ("-en-long", "-en-short", "-pt", "-en", "-v2"):
            if nome.endswith(sufixo):
                nome = nome[: -len(sufixo)]
        slugs.add(nome)
    ligados = {p.get("atributos", {}).get("arquivo") for p in posts}
    slugs_ligados = set()
    for nome in ligados:
        if not nome:
            continue
        base = nome[:-3] if nome.endswith(".md") else nome
        for sufixo in ("-en-long", "-en-short", "-pt", "-en", "-v2"):
            if base.endswith(sufixo):
                base = base[: -len(sufixo)]
        slugs_ligados.add(base)
    faltando = sorted(slugs - slugs_ligados)
    out.append(f"- Pautas do workspace (`post-*.md`) sem métrica ligada: {len(faltando)}")
    out.append("  (grande parte é rascunho que não foi colado no LinkedIn; só vira pendência o que você publicar)")
    out.append("")
    out.append("## Como ler este relatório")
    out.append("")
    out.append("- Impressões de post individual são de tempo de vida; a janela (7/28/90 dias) vale só para os agregados e a lista de melhores posts.")
    out.append("- A plataforma não publica os pesos da distribuição: isto é leitura dos dados, não regra garantida.")
    out.append("- Com n pequeno, trate cada linha como pista a confirmar com a próxima coleta, não como causa.")
    return "\n".join(out)


# ---------------------------------------------------------------- comandos


def comando_check(base: Path, workspace: Path) -> int:
    store = carregar_store(base)
    print(f"diretório de dados: {base}")
    print(f"store: {(base / 'linkedin-metricas.json')}")
    print(f"workspace: {workspace}")
    print(f"posts com métrica: {sum(1 for p in store['posts'].values() if (p.get('ultima') or {}).get('impressoes'))}")
    print(f"posts conhecidos (inclui só top posts): {len(store['posts'])}")
    print(f"coletas de conteúdo: {len(store['conta'].get('agregados') or [])}")
    print(f"coletas de público: {len(store['conta'].get('coletas') or [])}")
    arquivos = sorted((base / "raw").glob("*.txt")) if (base / "raw").exists() else []
    print(f"snapshots em raw/: {len(arquivos)}")
    for a in arquivos:
        print(f"  - {a.name}")
    return 0


def comando_ingerir(base: Path, caminhos: list[Path]) -> int:
    arquivos: list[Path] = []
    for c in caminhos:
        if c.is_dir():
            arquivos.extend(sorted(c.glob("*.txt")))
        elif c.exists():
            arquivos.append(c)
        else:
            print(f"não encontrei {c}", file=sys.stderr)
    if not arquivos:
        print("nada para ingerir", file=sys.stderr)
        return 1
    relato = ingerir(base, arquivos)
    print(f"ingeridos: {relato['arquivos']} arquivos")
    print(f"  posts com métrica: {relato['posts']}")
    print(f"  coletas de conteúdo: {relato['conteudo']} · listas: {relato['lista']} · público: {relato['publico']} · não reconhecidos: {relato['desconhecido']}")
    return 0


def comando_listar(base: Path) -> int:
    store = carregar_store(base)
    for urn, p in sorted(store["posts"].items(), key=lambda kv: (kv[1].get("ultima") or {}).get("capturado_em") or "", reverse=True):
        u = p.get("ultima") or {}
        print(f"{urn}  imp={fmt(u.get('impressoes'))}  alc={fmt(u.get('usuarios_alcancados'))}  "
              f"fora={fmt(u.get('fora_da_rede_pct'))}%  arquivo={p.get('arquivo') or '-'}")
        if not u.get("impressoes"):
            print(f"    (só janela: {p.get('historico_janela') or '-'})")
    return 0


def comando_atributos(base: Path, workspace: Path) -> int:
    store = carregar_store(base)
    posts = preparar_atributos(store, workspace, base)
    salvar_store(base, store)
    ligados = [p for p in store["posts"].values() if p.get("arquivo")]
    print(f"arquivos post-*.md lidos: {len(posts)}")
    print(f"posts com métrica ligados a arquivo: {len(ligados)}")
    tipos: dict[str, int] = {}
    for p in store["posts"].values():
        if (p.get("ultima") or {}).get("impressoes"):
            chave = p.get("tipo") or "outro"
            tipos[chave] = tipos.get(chave, 0) + 1
    print("tipos (só posts com métrica): " + ", ".join(f"{k}={v}" for k, v in sorted(tipos.items(), key=lambda kv: -kv[1])))
    for p in ligados:
        print(f"  {p['activity_urn']} -> {p['arquivo']} (similaridade {p.get('similaridade_arquivo')})")
    return 0


def referencia_da_coleta(store: dict) -> str:
    datas = [(c.get("capturado_em") or c.get("em")) for c in (store.get("coletas") or [])
             if (c.get("capturado_em") or c.get("em"))]
    return max(datas) if datas else dt.date.today().isoformat()


def comando_relatorio(base: Path, workspace: Path, saida: Path | None) -> int:
    store = carregar_store(base)
    preparar_atributos(store, workspace, base)
    salvar_store(base, store)
    texto = linhas_relatorio(store, workspace)
    referencia = referencia_da_coleta(store)
    destino = saida or (base / f"relatorio-{referencia}.md")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    print(f"\n[relatório salvo em {destino}]")
    return 0


def comando_exportar(base: Path, workspace: Path, args) -> int:
    store = carregar_store(base)
    preparar_atributos(store, workspace, base)
    salvar_store(base, store)
    referencia = referencia_da_coleta(store)
    alvo = caminho_alvo()
    formatos = list(args.somente) if args.somente else ["xlsx", "csv", "json", "yaml"]
    destinos = {
        "xlsx": args.xlsx or (base / f"linkedin-metricas-{referencia}.xlsx"),
        "csv": args.csv or (base / f"linkedin-posts-{referencia}.csv"),
        "json": args.json or (base / f"linkedin-metricas-{referencia}.json"),
        "yaml": args.yaml or (base / f"linkedin-metricas-{referencia}.yaml"),
    }
    try:
        from exportar import (escrever_csv, escrever_json, escrever_yaml,
                              exportar_planilha, pacote_analise, registros_posts)
    except ImportError as erro:
        print(f"não consegui carregar o exportador ({erro})", file=sys.stderr)
        return 1

    falhou = False
    if {"json", "yaml"} & set(formatos):
        pacote = pacote_analise(store, alvo, scorecards=scorecards_por_tipo(store))
        if "json" in formatos:
            escrever_json(pacote, destinos["json"])
            print(f"JSON: {destinos['json']}  (schema {pacote['schema']} v{pacote['schema_version']}, {pacote['resumo']['n_posts']} posts)")
        if "yaml" in formatos:
            escrever_yaml(pacote, destinos["yaml"])
            print(f"YAML: {destinos['yaml']}")
    if "csv" in formatos:
        escrever_csv(registros_posts(store), destinos["csv"])
        print(f"CSV:  {destinos['csv']}  (separado por ponto e vírgula)")
    if "xlsx" in formatos:
        try:
            relato = exportar_planilha(store, destinos["xlsx"], None, alvo)
            print(f"XLSX: {relato['xlsx']}  (abas: {', '.join(relato['abas'])})")
        except ImportError as erro:
            falhou = True
            print(f"XLSX não gerado ({erro}).", file=sys.stderr)
            print("se faltar openpyxl: python3 -m pip install --user --break-system-packages openpyxl", file=sys.stderr)
    return 1 if falhou else 0


def comando_links(base: Path) -> int:
    store = carregar_store(base)
    print("# Páginas para o agente abrir no navegador in-app e salvar o snapshot")
    print("https://www.linkedin.com/analytics/creator/content/")
    print("https://www.linkedin.com/analytics/creator/audience/")
    for urn in sorted(store["posts"]):
        print(f"https://www.linkedin.com/analytics/post-summary/{urn}/")
    if not store["posts"]:
        print("# (sem URN conhecido ainda: a lista de 'Publicações de melhor desempenho' preenche isso ao ingerir a página de conteúdo)")
    return 0


def resolver(dado, caminho: str):
    """Resolve caminhos do tipo 'top_posts[0].activity_urn', 'demografia.Setor.pct',
    'len:top_posts' e 'texto.inicio:60'. Devolve (achou, valor)."""
    if caminho.startswith("len:"):
        v = resolver(dado, caminho[4:])[1]
        return True, (len(v) if v is not None else None)
    if caminho.startswith("nao_contem:"):
        return True, (caminho.split("nao_contem:", 1)[1] not in (resolver(dado, "texto")[1] or ""))
    if "nao_contem:" in caminho:
        base, alvo = caminho.split(".nao_contem:", 1)
        return True, (alvo not in (resolver(dado, base)[1] or ""))
    if "contem:" in caminho:
        base, alvo = caminho.split(".contem:", 1)
        return True, (alvo in (resolver(dado, base)[1] or ""))
    if ".inicio:" in caminho:
        base, n = caminho.split(".inicio:", 1)
        v = resolver(dado, base)[1]
        return True, (v[: int(n)] if isinstance(v, str) else None)
    atual = dado
    for parte in caminho.split("."):
        m = re.match(r"^([^\[\]]+)((?:\[\d+\])*)$", parte)
        if not m:
            return False, None
        chave, indices = m.group(1), m.group(2)
        if not isinstance(atual, dict) or chave not in atual:
            return False, None
        atual = atual[chave]
        for idx in re.findall(r"\[(\d+)\]", indices):
            if not isinstance(atual, list) or int(idx) >= len(atual):
                return False, None
            atual = atual[int(idx)]
    return True, atual


def comando_selftest(base: Path) -> int:
    fixtures = Path(__file__).resolve().parent.parent / "fixtures"
    esperado = fixtures / "esperado.json"
    if not fixtures.exists() or not esperado.exists():
        print(f"sem fixtures em {fixtures}", file=sys.stderr)
        return 1
    casos = json.loads(esperado.read_text(encoding="utf-8"))
    falhas = 0
    for nome, exp in casos.items():
        caminho = fixtures / nome
        if not caminho.exists():
            print(f"FALTA {nome}")
            falhas += 1
            continue
        dado = parse_snapshot(caminho)
        for chave, valor in exp.items():
            achou, obtido = resolver(dado, chave)
            if not achou or obtido != valor:
                print(f"FALHA {nome} :: {chave}: esperado {valor!r}, obtido {obtido!r}")
                falhas += 1
    print("selftest ok" if not falhas else f"selftest: {falhas} falha(s)")
    return 1 if falhas else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Estatísticas de posts do LinkedIn: coleta, store e diagnóstico.")
    ap.add_argument("--dir", type=Path, default=None, help="diretório de dados (default: TERRAS_LINKEDIN_METRICAS_DIR ou ./metricas)")
    ap.add_argument("--workspace", type=Path, default=None, help="diretório dos posts (default: o diretório de dados, subindo até achar post-*.md)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="estado do store")
    p_ing = sub.add_parser("ingerir", help="parseia snapshots e funde no store")
    p_ing.add_argument("caminhos", nargs="+", type=Path)
    sub.add_parser("listar", help="lista posts do store")
    sub.add_parser("atributos", help="liga métricas aos arquivos post-*.md")
    p_rel = sub.add_parser("relatorio", help="gera o relatório")
    p_rel.add_argument("--saida", type=Path, default=None)
    p_exp = sub.add_parser("exportar", help="pacote de saída: planilha, CSV, JSON e YAML")
    p_exp.add_argument("--xlsx", type=Path, default=None)
    p_exp.add_argument("--csv", type=Path, default=None)
    p_exp.add_argument("--json", type=Path, default=None)
    p_exp.add_argument("--yaml", type=Path, default=None)
    p_exp.add_argument("--somente", nargs="+", choices=["xlsx", "csv", "json", "yaml"], default=None,
                       help="gera só estes formatos (default: todos)")
    sub.add_parser("links", help="URLs de análise para abrir no navegador")
    sub.add_parser("selftest", help="confere o parser contra fixtures")

    args = ap.parse_args(argv)
    base = args.dir or diretorio_padrao()
    if args.workspace:
        workspace = args.workspace
    else:
        workspace = base.parent if (base.parent / "AGENTS.md").exists() or list(base.parent.glob("post-*.md")) else Path.cwd()

    if args.cmd == "check":
        return comando_check(base, workspace)
    if args.cmd == "ingerir":
        return comando_ingerir(base, args.caminhos)
    if args.cmd == "listar":
        return comando_listar(base)
    if args.cmd == "atributos":
        return comando_atributos(base, workspace)
    if args.cmd == "relatorio":
        return comando_relatorio(base, workspace, args.saida)
    if args.cmd == "exportar":
        return comando_exportar(base, workspace, args)
    if args.cmd == "links":
        return comando_links(base)
    if args.cmd == "selftest":
        return comando_selftest(base)
    return 2


if __name__ == "__main__":
    sys.exit(main())

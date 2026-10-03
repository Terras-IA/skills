#!/usr/bin/env python3
"""Exporta o store de metricas do LinkedIn: planilha (XLSX), CSV e pacote JSON/YAML.

Segue o sistema de design da skill `xlsx` (tema professional, titulo em B2, cabecalho
com fundo primary, linha alternada, sem borda de grade, auto-fit de coluna e altura).
Requer openpyxl. O CSV sai da mesma tabela de posts, para quem for ler com pandas.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import os
import sys
from pathlib import Path

VERSAO_LAYOUT = 3  # v3: tipo/tags por post, pontuacoes de densidade e scorecard por tipo

FORMATO_PCT_PONTOS = '0"%"'      # o valor ja esta em pontos percentuais (100 = 100%)
FORMATO_PCT_FRACAO = "0.0%"
FORMATO_MILHAR = "#,##0"
FORMATO_1C = "#,##0.0"

SHEETS = ("Posts", "Janela (todos)", "Conta", "Público", "Séries", "Leia-me")


def _base():
    """Importa templates/base.py da skill xlsx (fonte única de estilo).

    Cuidado: variável de ambiente ausente vira caminho vazio, e caminho vazio existe
    no disco (é o diretório atual). Por isso a checagem é pelo arquivo templates/base.py,
    não pela existência do diretório.
    """
    raiz = None
    env = os.environ.get("XLSX_SKILL_DIR")
    if env:
        candidato = Path(env).expanduser()
        if (candidato / "templates" / "base.py").exists():
            raiz = candidato
    if raiz is None:
        for candidato in reversed(sorted(Path.home().glob(".zcode/cli/plugins/cache/*/spreadsheets/*/skills/xlsx"))):
            if (candidato / "templates" / "base.py").exists():
                raiz = candidato
                break
    if raiz is None:
        raise ImportError("não achei templates/base.py da skill xlsx; defina XLSX_SKILL_DIR")
    for sub in (raiz, raiz / "templates"):
        if str(sub) not in sys.path:
            sys.path.insert(0, str(sub))
    import base  # noqa: E402
    return base


def _bool_txt(v) -> str:
    if v is True:
        return "sim"
    if v is False:
        return "não"
    return ""


def _pct_pontos(v):
    return None if v is None else float(v)


def _raca(a, b):
    """Razao segura para o CSV (o XLSX usa formula com IFERROR)."""
    if a is None or b in (None, 0):
        return None
    return a / b


def _mil(v):
    return _raca(v, 1)


def _por_mil(v, base):
    r = _raca(v, base)
    return None if r is None else r * 1000


def _rotulo_curto(arquivo: str | None, texto: str) -> str:
    """Rótulo de poucos caracteres, para o eixo do gráfico não girar texto comprido."""
    if arquivo:
        nome = arquivo[:-3] if arquivo.endswith(".md") else arquivo
        if nome.startswith("post-"):
            nome = nome[len("post-"):]
        for sufixo in ("-en-long", "-en-short", "-pt", "-en", "-v2"):
            if nome.endswith(sufixo):
                nome = nome[: -len(sufixo)]
        return nome.replace("-", " ")[:30]
    return (texto[:28] + "…") if len(texto) > 28 else texto


def _linha_post(post: dict) -> dict:
    u = post.get("ultima") or {}
    a = post.get("atributos") or {}
    texto = post.get("texto") or ""
    rotulo = (a.get("arquivo") or texto[:60] or post.get("activity_urn", "")).strip()
    imp = u.get("impressoes")
    return {
        "Post": rotulo,
        "Post (curto)": _rotulo_curto(a.get("arquivo"), texto),
        "Arquivo": a.get("arquivo") or "",
        "URN": post.get("activity_urn", ""),
        "Idioma": a.get("idioma", ""),
        "Tipo": post.get("tipo") or "outro",
        "Tags": ", ".join(post.get("tags") or []) or "outro",
        "Publicado (idade)": post.get("idade_legivel") or "",
        "Caracteres": a.get("caracteres"),
        "Itens em lista": a.get("bullets"),
        "Hashtags": a.get("hashtags"),
        "Prazo": _bool_txt(a.get("ancora_de_prazo")),
        "Salvável": _bool_txt(a.get("material_salvavel")),
        "Número no hook": _bool_txt(a.get("hook_com_numero")),
        "Data no hook": _bool_txt(a.get("hook_com_data")),
        "Pergunta no fim": _bool_txt(a.get("pergunta_no_fim")),
        "Impressões": imp,
        "Alcance": u.get("usuarios_alcancados"),
        "Fora da rede pontos": _pct_pontos(u.get("fora_da_rede_pct")),
        "Engajamento": u.get("engajamento_total"),
        "Reações": u.get("reacoes"),
        "Comentários": u.get("comentarios"),
        "Compartilhamentos": u.get("compartilhamentos"),
        "Salvamentos": u.get("salvamentos"),
        "Envios": u.get("envios"),
        "Views de perfil": u.get("visualizacoes_perfil"),
        "Seguidores": u.get("seguidores_ganhos"),
        "Alcance/Impressões": _raca(u.get("usuarios_alcancados"), imp),
        "Salvos/Reações": _raca(u.get("salvamentos"), u.get("reacoes")),
        "Coment./Reações": _raca(u.get("comentarios"), u.get("reacoes")),
        "Views perfil/1k": _por_mil(u.get("visualizacoes_perfil"), imp),
        "Seguidores/1k": _por_mil(u.get("seguidores_ganhos"), imp),
        "Capturado em": u.get("capturado_em") or "",
        "Origem dos atributos": a.get("origem") or ("arquivo" if a.get("arquivo") else ""),
    }


CABECALHO_POSTS = [
    "Post", "Post (curto)", "Arquivo", "URN", "Idioma", "Tipo", "Tags", "Publicado (idade)",
    "Caracteres", "Itens em lista", "Hashtags", "Prazo", "Salvável", "Número no hook",
    "Data no hook", "Pergunta no fim", "Impressões", "Alcance", "Fora da rede pontos",
    "Engajamento", "Reações", "Comentários", "Compartilhamentos", "Salvamentos", "Envios",
    "Views de perfil", "Seguidores", "Alcance/Impressões", "Salvos/Reações", "Coment./Reações",
    "Views perfil/1k", "Seguidores/1k", "Capturado em", "Origem dos atributos",
]

COLUNAS_SOMA = [
    "Impressões", "Alcance", "Engajamento", "Reações", "Comentários", "Compartilhamentos",
    "Salvamentos", "Envios", "Views de perfil", "Seguidores",
]

# números vão à direita, texto à esquerda (a primeira letra do cabeçalho não serve de chave)
COLUNAS_NUMERO = set(COLUNAS_SOMA) | {
    "Caracteres", "Itens em lista", "Hashtags", "Fora da rede pontos",
    "Alcance/Impressões", "Salvos/Reações", "Coment./Reações", "Views perfil/1k", "Seguidores/1k",
}


def linhas_conta(store: dict) -> list[list]:
    colecoes = store["conta"].get("coletas") or []
    agregados = store["conta"].get("agregados") or []
    linhas = []
    if colecoes:
        s = colecoes[-1]
        linhas += [
            ["Conta", "Seguidores", s.get("total_seguidores"), "total no momento da coleta"],
            ["Conta", "Variação vs período anterior", _pct_pontos(s.get("variacao_pct")), "em pontos percentuais"],
            ["Conta", "Novos seguidores na janela", s.get("novos_seguidores"), "série acumulada da janela"],
        ]
    if agregados:
        a = agregados[-1]
        linhas += [
            ["Janela", "Impressões", a.get("impressoes"), f"janela {a.get('periodo') or 'padrão'} · coleta {a.get('capturado_em')}"],
            ["Janela", "Variação vs janela anterior", _pct_pontos(a.get("variacao_pct")), "em pontos percentuais"],
            ["Janela", "Usuários alcançados", a.get("usuarios_alcancados"), ""],
            ["Janela", "Na rede", _pct_pontos(a.get("na_rede_pct")), "seguidores e conexões"],
            ["Janela", "Fora da rede", _pct_pontos(a.get("fora_da_rede_pct")), ""],
            ["Janela", "Engajamento", a.get("engajamento_total"), "soma das redes"],
            ["Janela", "Reações", a.get("reacoes"), ""],
            ["Janela", "Comentários", a.get("comentarios"), ""],
            ["Janela", "Compartilhamentos", a.get("compartilhamentos"), ""],
            ["Janela", "Salvamentos", a.get("salvamentos"), ""],
            ["Janela", "Envios no LinkedIn", a.get("envios"), ""],
        ]
    return linhas


DIMENSOES = ["Nível de experiência", "Cargo", "Setor", "Localidade", "Tamanho da empresa", "Empresa"]


def _dem_fonte(fonte: dict, dim: str):
    d = (fonte or {}).get(dim)
    if not d:
        return None, None
    pct = d.get("pct")
    if pct == 0 and d.get("bruto"):
        return d.get("valor"), d["bruto"]          # "menos de 1%": texto, para não virar 0
    return d.get("valor"), pct


def _alinhamento(chave: str, valor, alvo: dict) -> str:
    """Compara UM valor (de UMA fonte) com o alvo declarado.

    A chave e a ascii do MAPA_DIM. A comparacao de localidade, cargo e setor e por
    substring: o LinkedIn devolve o topo no formato "Londres e Regiao, Reino Unido",
    e casar o pais por substring dentro do rotulo e o que faz a funcao responder certo.
    """
    if not valor:
        return ""
    if chave == "senioridade":
        return "alinhado" if valor in alvo.get("senioridades", []) else "fora_do_alvo"
    if chave == "localidade":
        return "alvo_internacional" if any(l in str(valor) for l in alvo.get("localidades", [])) else "fora_do_alvo"
    if chave == "cargo":
        return "alvo" if any(c in str(valor) for c in alvo.get("cargos", [])) else "fora_do_alvo"
    return ""


def linhas_publico(store: dict, alvo: dict, vencedor: dict | None) -> list[list]:
    colecoes = store["conta"].get("coletas") or []
    agregados = store["conta"].get("agregados") or []
    seg = (colecoes[-1] if colecoes else {}).get("demografia") or {}
    jan = (agregados[-1] if agregados else {}).get("demografia") or {}
    venc = (vencedor or {}).get("demografia") or {}
    linhas = []
    for dim in DIMENSOES:
        vs, ps = _dem_fonte(seg, dim)
        vj, pj = _dem_fonte(jan, dim)
        vv, pv = _dem_fonte(venc, dim)
        chave = MAPA_DIM.get(dim, "")
        # alinhamento por fonte: o topo de cada coluna pode cair em lado diferente do alvo
        # (seguidores em SP, post vencedor em Londres), e um valor unico escondia isso
        linhas.append([dim, vs, ps, vj, pj, vv, pv,
                       _alinhamento(chave, vs, alvo),
                       _alinhamento(chave, vj, alvo),
                       _alinhamento(chave, vv, alvo)])
    return linhas


def linhas_series(store: dict) -> list[list]:
    agregados = store["conta"].get("agregados") or []
    colecoes = store["conta"].get("coletas") or []
    imp = {p["data"]: p["valor"] for p in (agregados[-1].get("serie_diaria") if agregados else []) or []}
    nov = {p["data"]: p["valor"] for p in (colecoes[-1].get("serie_diaria") if colecoes else []) or []}
    datas = sorted(set(imp) | set(nov))
    return [[d, imp.get(d), nov.get(d)] for d in datas]


def registros_posts(store: dict) -> list[dict]:
    """Uma linha por post com métrica, ordenada por impressões. Não precisa de openpyxl."""
    posts = sorted(
        [p for p in store["posts"].values() if (p.get("ultima") or {}).get("impressoes")],
        key=lambda p: p["ultima"]["impressoes"],
        reverse=True,
    )
    return [_linha_post(p) for p in posts]


def registros_janela(store: dict) -> list[dict]:
    """Todos os posts que a lista de melhores posts da janela enumera, inclusive os que
    ainda não têm coleta de tempo de vida. É a cauda: a maioria do acervo aparece só aqui."""
    linhas = []
    for p in store["posts"].values():
        j = p.get("historico_janela") or {}
        a = p.get("atributos") or {}
        u = p.get("ultima") or {}
        linhas.append({
            "Post (curto)": _rotulo_curto(a.get("arquivo"), p.get("texto") or ""),
            "URN": p.get("activity_urn", ""),
            "Impressões": j.get("impressoes_janela"),
            "Reações": j.get("reacoes_janela"),
            "Comentários": j.get("comentarios_janela"),
            "Idade": p.get("idade_legivel") or "",
            "Tem coleta de tempo de vida": "sim" if u.get("impressoes") else "não",
            "Arquivo": a.get("arquivo") or "",
        })
    linhas.sort(key=lambda r: r["Impressões"] or 0, reverse=True)
    return linhas


def escrever_csv(registros: list[dict], destino: Path) -> None:
    """CSV separado por ponto e vírgula: abre no Excel em português sem ajuste de lista."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CABECALHO_POSTS, delimiter=";")
        w.writeheader()
        for reg in registros:
            w.writerow({k: ("" if v is None else v) for k, v in reg.items()})


# ---------------------------------------------------------------- pacote de interface

MAPA_DIM = {
    "Nível de experiência": "senioridade",
    "Cargo": "cargo",
    "Setor": "setor",
    "Localidade": "localidade",
    "Tamanho da empresa": "tamanho_empresa",
    "Empresa": "empresa",
}

DICIONARIO = {
    "posts_sem_coleta_de_vida": "Posts que a lista da janela enumera e que ainda não tiveram a página individual coletada: só têm os números DA JANELA, não de tempo de vida.",
    "posts[].metricas": "Contadores do LinkedIn para aquele post, em tempo de vida (desde a publicação). São best-effort e continuam crescendo depois da coleta.",
    "posts[].derivadas": "Razões calculadas a partir de metricas, para comparar posts de tamanhos diferentes. As cinco pontuações de densidade são por mil impressões.",
    "posts[].tipo": "Tipo principal do post (a primeira tag). Motor de autoridade: decisao-arquitetura, resiliencia, custo, ia-em-producao, meta-conteudo. Motor de alcance: mudanca-com-prazo.",
    "posts[].tags": "Todas as tags internas do texto, por ordem de prioridade. Heurística de palavra-chave, com ajuste manual em tipos-manuais.json.",
    "scorecards_por_tipo": "Mediana das pontuações por tipo de post. Foco atual: autoridade, onde densidade importa mais que alcance. Impressões altas com pontuação baixa é distribuição; impressões baixas com densidade alta é autoridade.",
    "posts[].atributos": "Marcas do TEXTO do post. São heurística (palavra-chave e lista), não verdade medida: use como pista, nunca como rótulo de treino sem conferência humana.",
    "posts[].atributos.ancora_de_prazo": "O texto traz prazo que expira e obriga a agir (fim de suporte, breaking change, descontinuação).",
    "posts[].atributos.material_salvavel": "O texto entrega algo que se guarda para usar depois (checklist, passo a passo, comparativo, lista com 3+ itens).",
    "posts[].atributos.numero_no_hook": "A primeira linha tem número.",
    "posts[].atributos.data_no_hook": "A primeira linha tem data ou ano.",
    "posts[].atributos.pergunta_no_fim": "O texto termina com pergunta, antes das hashtags.",
    "posts[].atributos.itens_lista": "Quantidade de itens de lista no texto.",
    "posts[].demografia": "Maior fatia de cada dimensão entre quem foi alcançado por aquele post. O LinkedIn só expõe o topo de cada dimensão.",
    "conta.janela": "Agregado da janela filtrada no LinkedIn (aqui, 7 dias), não do histórico todo.",
    "conta.serie_diaria": "Pontos do gráfico da janela, cumulativos (o último ponto é o total da janela).",
    "conta.seguidores_por_dia": "Pontos do gráfico de seguidores, cumulativos na janela.",
    "publico": "Comparação por dimensão entre seguidores, quem foi alcançado na janela e quem foi alcançado pelo post de maior alcance.",
    "alvo": "Público que o autor declarou querer alcançar. O campo alinhamento compara cada fonte (seguidores, janela, post vencedor) com ele, por fonte e nao com um valor unico.",
    "limites": "Condições que restringem a leitura. Ler antes de concluir causa.",
}


def _dem_ascii(dem: dict) -> dict:
    fora = {}
    for dim, val in (dem or {}).items():
        if not val:
            continue
        item = {"valor": val.get("valor"), "pct": val.get("pct")}
        if val.get("bruto"):
            item["bruto"] = val["bruto"]
        fora[MAPA_DIM.get(dim, dim)] = item
    return fora


def _atributos_ascii(a: dict) -> dict:
    return {
        "caracteres": a.get("caracteres"),
        "itens_lista": a.get("bullets"),
        "hashtags": a.get("hashtags"),
        "ancora_de_prazo": a.get("ancora_de_prazo"),
        "material_salvavel": a.get("material_salvavel"),
        "numero_no_hook": a.get("hook_com_numero"),
        "data_no_hook": a.get("hook_com_data"),
        "pergunta_no_fim": a.get("pergunta_no_fim"),
        "link_externo": a.get("tem_link_externo"),
        "metodo": "heuristica",
        "origem": a.get("origem") or ("arquivo" if a.get("arquivo") else None),
        "arquivo": a.get("arquivo"),
    }


def _metricas_ascii(u: dict) -> dict:
    return {
        "impressoes": u.get("impressoes"),
        "usuarios_alcancados": u.get("usuarios_alcancados"),
        "na_rede_pct": u.get("na_rede_pct"),
        "fora_da_rede_pct": u.get("fora_da_rede_pct"),
        "engajamento_total": u.get("engajamento_total"),
        "reacoes": u.get("reacoes"),
        "comentarios": u.get("comentarios"),
        "compartilhamentos": u.get("compartilhamentos"),
        "salvamentos": u.get("salvamentos"),
        "envios": u.get("envios"),
        "visualizacoes_perfil": u.get("visualizacoes_perfil"),
        "seguidores_ganhos": u.get("seguidores_ganhos"),
    }


def _derivadas_ascii(u: dict) -> dict:
    imp = u.get("impressoes")

    def r(a, b):
        return None if (a is None or not b) else round(a / b, 4)

    return {
        "alcance_por_impressao": r(u.get("usuarios_alcancados"), imp),
        "salvos_por_reacao": r(u.get("salvamentos"), u.get("reacoes")),
        "comentarios_por_reacao": r(u.get("comentarios"), u.get("reacoes")),
        "engajamento_por_1k": None if not imp else round(1000 * (u.get("engajamento_total") or 0) / imp, 2),
        "comentarios_por_1k": None if not imp else round(1000 * (u.get("comentarios") or 0) / imp, 2),
        "salvamentos_por_1k": None if not imp else round(1000 * (u.get("salvamentos") or 0) / imp, 2),
        "views_perfil_por_1k": None if not imp else round(1000 * (u.get("visualizacoes_perfil") or 0) / imp, 2),
        "seguidores_por_1k": None if not imp else round(1000 * (u.get("seguidores_ganhos") or 0) / imp, 2),
    }


def _mediana(valores: list):
    vals = sorted(v for v in valores if isinstance(v, (int, float)))
    if not vals:
        return None
    n = len(vals)
    return vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2


def pacote_analise(store: dict, alvo: dict | None = None, scorecards: list | None = None) -> dict:
    """Artefato de interface: o mesmo dado da planilha, em JSON/YAML, para outro MCP,
    agente ou modelo (JEV, Laya) analisar. Chaves em ASCII, tipos de verdade (número,
    booleano, nulo), dicionário de campo junto e limites declarados."""
    alvo = alvo or {}
    posts = sorted(
        [p for p in store["posts"].values() if (p.get("ultima") or {}).get("impressoes")],
        key=lambda p: p["ultima"]["impressoes"],
        reverse=True,
    )
    agregados = store["conta"].get("agregados") or []
    colecoes = store["conta"].get("coletas") or []
    ag = agregados[-1] if agregados else {}
    seg = colecoes[-1] if colecoes else {}
    imps = [p["ultima"]["impressoes"] for p in posts]
    med = _mediana(imps)

    itens = []
    for p in posts:
        u = p.get("ultima") or {}
        a = p.get("atributos") or {}
        texto = (p.get("texto") or "").strip()
        itens.append({
            "urn": p.get("activity_urn"),
            "share_urn": p.get("share_urn"),
            "rotulo": a.get("arquivo") or (texto[:60] or p.get("activity_urn")),
            "arquivo": a.get("arquivo"),
            "idioma": a.get("idioma"),
            "publicado_idade": p.get("idade_legivel"),
            "tipo": p.get("tipo") or "outro",
            "tags": p.get("tags") or ["outro"],
            "hook": a.get("hook"),
            "primeiros_210": a.get("primeiros_210"),
            "texto_completo": texto or None,
            "atributos": _atributos_ascii(a),
            "metricas": _metricas_ascii(u),
            "derivadas": _derivadas_ascii(u),
            "demografia": _dem_ascii(u.get("demografia")),
            "capturado_em": u.get("capturado_em"),
            "historico": [
                {"capturado_em": h.get("capturado_em"), "impressoes": h.get("impressoes"),
                 "usuarios_alcancados": h.get("usuarios_alcancados"),
                 "engajamento_total": h.get("engajamento_total"),
                 "salvamentos": h.get("salvamentos"),
                 "visualizacoes_perfil": h.get("visualizacoes_perfil"),
                 "seguidores_ganhos": h.get("seguidores_ganhos")}
                for h in (p.get("historico") or [])
            ],
        })

    publico = []
    venc = (posts[0]["ultima"].get("demografia") if posts else {}) or {}
    for dim, chave in MAPA_DIM.items():
        s = _dem_ascii({dim: (seg.get("demografia") or {}).get(dim)}).get(chave)
        j = _dem_ascii({dim: (ag.get("demografia") or {}).get(dim)}).get(chave)
        v = _dem_ascii({dim: venc.get(dim)}).get(chave)
        if not any((s, j, v)):
            continue
        # alinhamento POR FONTE: o topo de cada coluna pode cair em lado diferente do alvo
        # (seguidores em São Paulo, post vencedor em Londres). Um valor único escondia isso
        # e fazia o post vencedor parecer fora do alvo quando o topo dele estava dentro.
        publico.append({
            "dimensao": chave, "seguidores": s, "janela": j, "post_vencedor": v,
            "alinhamento": {
                "seguidores": _alinhamento(chave, (s or {}).get("valor"), alvo),
                "janela": _alinhamento(chave, (j or {}).get("valor"), alvo),
                "post_vencedor": _alinhamento(chave, (v or {}).get("valor"), alvo),
            },
        })

    datas = [(c.get("capturado_em") or c.get("em")) for c in (store.get("coletas") or [])
             if (c.get("capturado_em") or c.get("em"))]

    return {
        "schema": "terras-linkedin-metricas/pacote-analise",
        "schema_version": VERSAO_LAYOUT,
        "gerado_em": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "coleta": {
            "data": max(datas) if datas else None,
            "fonte": "páginas de análise do próprio LinkedIn (sessão autenticada do autor)",
            "janela": ag.get("periodo") or "padrão (7 dias no LinkedIn)",
            "seguidores_total": seg.get("total_seguidores"),
            "novos_seguidores_janela": seg.get("novos_seguidores"),
        },
        "limites": [
            "Métrica de post é de tempo de vida; os números de conta e a série diária valem só para a janela filtrada.",
            "O LinkedIn registra o dia em UTC; em São Paulo a virada do dia dele acontece às 21h locais.",
            "Números do LinkedIn são best-effort e crescem depois da coleta; compare só coletas próximas.",
            f"Amostra atual: {len(itens)} post(s). Separação de atributo exige pelo menos 2 posts de cada lado.",
            "atributos são heurística de texto, não medição; a demografia expõe só a maior fatia de cada dimensão.",
            "A plataforma não publica os pesos da distribuição: isto é leitura de dado, não regra garantida.",
        ],
        "alvo": alvo,
        "dicionario": DICIONARIO,
        "resumo": {
            "n_posts": len(itens),
            "total_impressoes": sum(v for v in imps if v) or None,
            "mediana_impressoes": med,
            "maior_urn": posts[0]["activity_urn"] if posts else None,
            "maior_para_mediana": (round(imps[0] / med, 2) if (imps and med) else None),
        },
        "posts": itens,
        "scorecards_por_tipo": scorecards or [],
        "posts_sem_coleta_de_vida": [
            {
                "urn": r["URN"],
                "rotulo": r["Post (curto)"],
                "arquivo": r["Arquivo"] or None,
                "idade": r["Idade"] or None,
                "janela": {
                    "impressoes": r["Impressões"],
                    "reacoes": r["Reações"],
                    "comentarios": r["Comentários"],
                },
            }
            for r in registros_janela(store) if r["Tem coleta de tempo de vida"] == "não"
        ],
        "conta": {
            "janela": {
                "impressoes": ag.get("impressoes"),
                "variacao_pct_periodo_anterior": ag.get("variacao_pct"),
                "usuarios_alcancados": ag.get("usuarios_alcancados"),
                "na_rede_pct": ag.get("na_rede_pct"),
                "fora_da_rede_pct": ag.get("fora_da_rede_pct"),
                "engajamento_total": ag.get("engajamento_total"),
                "reacoes": ag.get("reacoes"),
                "comentarios": ag.get("comentarios"),
                "compartilhamentos": ag.get("compartilhamentos"),
                "salvamentos": ag.get("salvamentos"),
                "envios": ag.get("envios"),
            },
            "serie_diaria": ag.get("serie_diaria") or [],
            "seguidores_por_dia": seg.get("serie_diaria") or [],
            "demografia_janela": _dem_ascii(ag.get("demografia")),
        },
        "publico": publico,
    }


def escrever_json(pacote: dict, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(pacote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def escrever_yaml(pacote: dict, destino: Path) -> None:
    import yaml
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        yaml.safe_dump(pacote, allow_unicode=True, sort_keys=False, default_flow_style=False, width=100),
        encoding="utf-8",
    )


# ---------------------------------------------------------------- construcao


def _crescer_para_palavra_unica(ws, header_row: int, colunas) -> None:
    """O auto-fit dimensiona a coluna pelo DADO, e cabeçalho de palavra única
    (Compartilhamentos) quebra no meio quando a coluna fica estreita. A coluna cresce
    até a maior palavra do cabeçalho, com teto para não explodir a aba."""
    from openpyxl.utils import get_column_letter

    for c in colunas:
        cab = ws.cell(row=header_row, column=c).value
        if not isinstance(cab, str):
            continue
        maior = max(len(p) for p in cab.split())
        letra = get_column_letter(c)
        atual = ws.column_dimensions[letra].width or 0
        if maior > atual:
            ws.column_dimensions[letra].width = min(maior + 1, 19)


def exportar_planilha(store: dict, destino_xlsx: Path,
                      destino_csv: Path | None = None, alvo: dict | None = None) -> dict:
    base = _base()
    from openpyxl import Workbook
    from openpyxl.chart import LineChart, Reference
    from openpyxl.styles import Font
    from openpyxl.worksheet.properties import PageSetupProperties
    from openpyxl.utils import get_column_letter

    alvo = alvo or {}
    registros = registros_posts(store)
    posts = sorted(
        [p for p in store["posts"].values() if (p.get("ultima") or {}).get("impressoes")],
        key=lambda p: p["ultima"]["impressoes"],
        reverse=True,
    )
    vencedor = (posts[0]["ultima"]["demografia"] if posts else None) or None

    wb = Workbook()
    wb.properties.creator = "Z.ai"

    # ---------------------------------------------------------- aba Posts
    ws = wb.active
    ws.title = "Posts"
    base.setup_sheet(ws, title="Posts com métrica (tempo de vida)", last_col=len(CABECALHO_POSTS) + 1)
    for i, h in enumerate(CABECALHO_POSTS, start=2):
        ws.cell(row=4, column=i, value=h)
    base.style_header_row(ws, row_num=4, col_start=2, col_end=len(CABECALHO_POSTS) + 1)

    for i, reg in enumerate(registros):
        r = 5 + i
        for j, h in enumerate(CABECALHO_POSTS, start=2):
            ws.cell(row=r, column=j, value=reg[h])
        base.style_data_row(ws, row_num=r, col_start=2, col_end=len(CABECALHO_POSTS) + 1, row_index=i)

    ultima = 4 + len(registros)
    total_row = ultima + 1
    # totais por formula (o recalc do LibreOffice confere os valores depois)
    col = {h: i for i, h in enumerate(CABECALHO_POSTS, start=2)}
    ws.cell(row=total_row, column=2, value="Total")
    for h in COLUNAS_SOMA:
        L = get_column_letter(col[h])
        ws.cell(row=total_row, column=col[h], value=f"=SUM({L}5:{L}{ultima})")
    if registros:
        def letra(nome: str) -> str:
            return get_column_letter(col[nome])

        t = total_row
        for nome, formula in {
            "Alcance/Impressões": f"=IFERROR({letra('Alcance')}{t}/{letra('Impressões')}{t},0)",
            "Salvos/Reações": f"=IFERROR({letra('Salvamentos')}{t}/{letra('Reações')}{t},0)",
            "Coment./Reações": f"=IFERROR({letra('Comentários')}{t}/{letra('Reações')}{t},0)",
            "Views perfil/1k": f"=IFERROR(1000*{letra('Views de perfil')}{t}/{letra('Impressões')}{t},0)",
            "Seguidores/1k": f"=IFERROR(1000*{letra('Seguidores')}{t}/{letra('Impressões')}{t},0)",
        }.items():
            ws.cell(row=t, column=col[nome], value=formula)
    base.style_total_row(ws, row_num=total_row, col_start=2, col_end=len(CABECALHO_POSTS) + 1)

    # formatos numericos e alinhamento (número à direita, texto à esquerda)
    for r in range(5, total_row + 1):
        for h in COLUNAS_SOMA:
            ws.cell(row=r, column=col[h]).number_format = FORMATO_MILHAR
        ws.cell(row=r, column=col["Caracteres"]).number_format = FORMATO_MILHAR
        ws.cell(row=r, column=col["Fora da rede pontos"]).number_format = FORMATO_PCT_PONTOS
        ws.cell(row=r, column=col["Alcance/Impressões"]).number_format = FORMATO_PCT_FRACAO
        ws.cell(row=r, column=col["Salvos/Reações"]).number_format = FORMATO_PCT_FRACAO
        ws.cell(row=r, column=col["Coment./Reações"]).number_format = FORMATO_PCT_FRACAO
        ws.cell(row=r, column=col["Views perfil/1k"]).number_format = FORMATO_1C
        ws.cell(row=r, column=col["Seguidores/1k"]).number_format = FORMATO_1C
        for h in COLUNAS_NUMERO:
            ws.cell(row=r, column=col[h]).alignment = base.align_number()

    base.auto_fit_columns(ws, min_width=8, max_width=26, header_row=4, data_start_row=5)
    _crescer_para_palavra_unica(ws, 4, range(2, 2 + len(CABECALHO_POSTS)))
    base.auto_fit_row_heights(ws, header_row=4, data_start_row=5, data_end_row=total_row)

    if len(registros) >= 2:
        grafico = base.create_bar_chart()
        dados = Reference(ws, min_col=col["Impressões"], min_row=4, max_row=ultima)
        # categoria = rótulo curto: o texto do hook girado no eixo estoura o quadro do gráfico
        cats = Reference(ws, min_col=col["Post (curto)"], min_row=5, max_row=ultima)
        grafico.add_data(dados, titles_from_data=True)
        grafico.set_categories(cats)
        base.setup_chart_titles(grafico, title="Impressões por post", y_title="Impressões", x_title="Post")
        base.apply_chart_colors(grafico, [base.PRIMARY])
        grafico.width, grafico.height = 20, 10
        ws.add_chart(grafico, f"{get_column_letter(len(CABECALHO_POSTS) + 3)}4")

    # ---------------------------------------------------------- aba Janela (todos)
    wsj = wb.create_sheet("Janela (todos)")
    base.setup_sheet(wsj, title="Todos os posts da janela, inclusive os ainda sem coleta", last_col=9)
    # cabeçalho curto de propósito: "Comentários na janela" não cabe e quebra no meio
    # da palavra; o escopo (janela) já está no título da aba
    cab_jan = ["Post (curto)", "URN", "Impressões", "Reações", "Comentários", "Idade",
               "Tem coleta de tempo de vida", "Arquivo"]
    for i, h in enumerate(cab_jan, start=2):
        wsj.cell(row=4, column=i, value=h)
    base.style_header_row(wsj, row_num=4, col_start=2, col_end=9)
    jrows = registros_janela(store)
    for i, reg in enumerate(jrows):
        r = 5 + i
        for j, h in enumerate(cab_jan, start=2):
            wsj.cell(row=r, column=j, value=reg[h])
        base.style_data_row(wsj, row_num=r, col_start=2, col_end=9, row_index=i)
        for c in (4, 5, 6):
            wsj.cell(row=r, column=c).number_format = FORMATO_MILHAR
            wsj.cell(row=r, column=c).alignment = base.align_number()
    base.auto_fit_columns(wsj, min_width=13, max_width=34, header_row=4, data_start_row=5)
    _crescer_para_palavra_unica(wsj, 4, range(2, 10))
    base.auto_fit_row_heights(wsj, header_row=4, data_start_row=5, data_end_row=4 + len(jrows))

    # ---------------------------------------------------------- aba Conta
    ws2 = wb.create_sheet("Conta")
    base.setup_sheet(ws2, title="Conta e janela", last_col=5)
    for i, h in enumerate(["Bloco", "Métrica", "Valor", "Observação"], start=2):
        ws2.cell(row=4, column=i, value=h)
    base.style_header_row(ws2, row_num=4, col_start=2, col_end=5)
    crows = linhas_conta(store)
    for i, linha in enumerate(crows):
        r = 5 + i
        for j, v in enumerate(linha, start=2):
            ws2.cell(row=r, column=j, value=v)
        base.style_data_row(ws2, row_num=r, col_start=2, col_end=5, row_index=i)
        if isinstance(linha[2], float) and linha[2] == int(linha[2]):
            ws2.cell(row=r, column=4).value = int(linha[2])
    for r in range(5, 5 + len(crows)):
        ws2.cell(row=r, column=4).number_format = FORMATO_MILHAR
        ws2.cell(row=r, column=4).alignment = base.align_number()
    base.auto_fit_columns(ws2, min_width=10, max_width=30, header_row=4, data_start_row=5)
    base.auto_fit_row_heights(ws2, header_row=4, data_start_row=5, data_end_row=4 + len(crows))

    # ---------------------------------------------------------- aba Público
    ws3 = wb.create_sheet("Público")
    base.setup_sheet(ws3, title="Público alcançado contra o alvo", last_col=11)
    for i, h in enumerate(["Dimensão", "Seguidores", "Seguidores %", "Janela", "Janela %",
                           "Post vencedor", "Vencedor %", "Alvo: seguidores", "Alvo: janela",
                           "Alvo: vencedor"], start=2):
        ws3.cell(row=4, column=i, value=h)
    base.style_header_row(ws3, row_num=4, col_start=2, col_end=11)
    prows = linhas_publico(store, alvo, vencedor)
    for i, linha in enumerate(prows):
        r = 5 + i
        for j, v in enumerate(linha, start=2):
            ws3.cell(row=r, column=j, value=v)
        base.style_data_row(ws3, row_num=r, col_start=2, col_end=11, row_index=i)
        for c in (4, 6, 8):
            cel = ws3.cell(row=r, column=c)
            if isinstance(cel.value, str):          # caso "menos de 1%"
                cel.alignment = base.align_number()
            else:
                cel.number_format = FORMATO_PCT_PONTOS
                cel.alignment = base.align_number()
        for c in (9, 10, 11):                       # alinhamento por fonte
            cel = ws3.cell(row=r, column=c)
            if isinstance(cel.value, str) and "_" in cel.value:
                # o pacote usa código com underline (fora_do_alvo); na planilha, que é
                # para ler, o código vira texto
                cel.value = cel.value.replace("_", " ")
            cel.alignment = base.align_text()
    base.auto_fit_columns(ws3, min_width=10, max_width=30, header_row=4, data_start_row=5)
    base.auto_fit_row_heights(ws3, header_row=4, data_start_row=5, data_end_row=4 + len(prows))

    # ---------------------------------------------------------- aba Séries
    # título curto de propósito: em célula mesclada o texto que não cabe é cortado
    ws4 = wb.create_sheet("Séries")
    base.setup_sheet(ws4, title="Série diária acumulada", last_col=4)
    for i, h in enumerate(["Data", "Impressões", "Novos seguidores"], start=2):
        ws4.cell(row=4, column=i, value=h)
    base.style_header_row(ws4, row_num=4, col_start=2, col_end=4)
    srows = linhas_series(store)
    for i, linha in enumerate(srows):
        r = 5 + i
        for j, v in enumerate(linha, start=2):
            ws4.cell(row=r, column=j, value=v)
        base.style_data_row(ws4, row_num=r, col_start=2, col_end=4, row_index=i)
        ws4.cell(row=r, column=2).alignment = base.align_date()
        for c in (3, 4):
            ws4.cell(row=r, column=c).number_format = FORMATO_MILHAR
            ws4.cell(row=r, column=c).alignment = base.align_number()
    base.auto_fit_columns(ws4, min_width=16, max_width=22, header_row=4, data_start_row=5)
    base.auto_fit_row_heights(ws4, header_row=4, data_start_row=5, data_end_row=4 + len(srows))
    if len(srows) >= 2:
        linha_chart = LineChart()
        linha_chart.style = 10
        linha_chart.add_data(Reference(ws4, min_col=3, min_row=4, max_row=4 + len(srows)), titles_from_data=True)
        linha_chart.set_categories(Reference(ws4, min_col=2, min_row=5, max_row=4 + len(srows)))
        base.setup_chart_titles(linha_chart, title="Impressões acumuladas na janela", y_title="Impressões")
        base.apply_chart_colors(linha_chart, [base.PRIMARY])
        linha_chart.width, linha_chart.height = 18, 10
        ws4.add_chart(linha_chart, "F4")

    # ---------------------------------------------------------- aba Leia-me
    ws5 = wb.create_sheet("Leia-me")
    base.setup_sheet(ws5, title="Leia-me: origem, limites e como regerar", last_col=3)
    for i, h in enumerate(["Item", "Conteúdo"], start=2):
        ws5.cell(row=4, column=i, value=h)
    base.style_header_row(ws5, row_num=4, col_start=2, col_end=3)
    coleta = ""
    datas = [(c.get("capturado_em") or c.get("em")) for c in (store.get("coletas") or []) if (c.get("capturado_em") or c.get("em"))]
    if datas:
        coleta = max(datas)
    notas = [
        ("Fonte", "Páginas de análise do próprio LinkedIn (Análise de conteúdo, Análise de público e Análise de cada publicação), lidas na sessão autenticada."),
        ("Coleta", coleta),
        ("Tempo de vida vs janela", "As colunas de um post são de tempo de vida, desde a publicação. Os números da aba Conta e a série da aba Séries valem só para a janela filtrada no LinkedIn (aqui, 7 dias)."),
        ("Fuso", "O LinkedIn registra o dia em UTC. Em São Paulo, depois das 21h o dia do LinkedIn já é o seguinte, então a data da coleta pode ficar um dia à frente do relógio local."),
        ("Amostra", f"{len(registros)} post(s) com métrica de tempo de vida. Com amostra pequena, leia cada linha como pista, não como causa."),
        ("Alvo", f"Público declarado como alvo: {alvo.get('descricao', '')}. As colunas Alvo: seguidores/janela/vencedor comparam cada fonte com esse alvo."),
        ("Arquivos", "Store com histórico de coletas em metricas/linkedin-metricas.json; snapshots crus em metricas/raw/."),
        ("Como regerar", "python3 <pasta da skill>/scripts/linkedin_metricas.py relatorio (diagnóstico) e exportar (este pacote)"),
        ("Skill", "terras-linkedin-metricas (coleta, store e diagnóstico). O texto dos posts continua na skill terras-linkedin."),
    ]
    for i, (k, v) in enumerate(notas):
        r = 5 + i
        ws5.cell(row=r, column=2, value=k)
        ws5.cell(row=r, column=3, value=v)
        base.style_data_row(ws5, row_num=r, col_start=2, col_end=3, row_index=i)
        ws5.cell(row=r, column=2).alignment = base.align_text()
        ws5.cell(row=r, column=3).alignment = base.align_text()
        ws5.cell(row=r, column=3).font = base.font_caption()
    base.auto_fit_columns(ws5, min_width=14, max_width=72, header_row=4, data_start_row=5)
    base.auto_fit_row_heights(ws5, header_row=4, data_start_row=5, data_end_row=4 + len(notas))

    destino_xlsx.parent.mkdir(parents=True, exist_ok=True)
    # impressão: paisagem, ajuste à largura e cabeçalho repetido. Sem repetir o cabeçalho,
    # a sobra de uma tabela cai numa página órfã sem título nem nomes de coluna.
    for sheet in (ws, wsj, ws2, ws3, ws4, ws5):
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
        sheet.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
        sheet.print_title_rows = "4:4"
    wb.save(destino_xlsx)

    if destino_csv:
        escrever_csv(registros, destino_csv)
    return {
        "xlsx": str(destino_xlsx),
        "csv": str(destino_csv) if destino_csv else None,
        "posts": len(registros),
        "abas": list(SHEETS),
    }

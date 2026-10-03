"""
Ponte: markdown -> manuscrito JSON que o `build_ebook.py` consome.

Entradas:
    --pasta artigos/     um .md por capítulo (ordem alfabética)
    --json artigos.json  a lista que o pipeline produz ([{title, article}])

Convenções de markdown:
    # Título            -> título do capítulo (vira capa de capítulo e sumário)
    ## / ### Subtítulo  -> subtítulo dentro do capítulo
    parágrafo           -> parágrafo
    - item / 1. item    -> lista
    > texto             -> citação
    > **RÓTULO** + texto-> caixa de destaque com esse rótulo
    | a | b |           -> tabela (primeira linha é o cabeçalho)
    links [x](url)      -> "x (url)", legível também no papel

Nome de arquivo com `_` na frente (ex.: `_introducao.md`) entra no livro SEM
numeração de capítulo — para introdução, prefácio e material de fecho.

`termos.md` na pasta NÃO é capítulo: é a tabela de termos do glossário
(`Termo | Definição | Rodapé | Também em`), que o `build_ebook.py` transforma em
nota de pé de página e em verbete no fim do livro — ver `glossario.py`.

Metadados: argumento de linha de comando > `--meta arquivo.json` > variável de
ambiente (`TERRAS_EBOOK_TITULO`, `TERRAS_EBOOK_AUTOR`) > deduzido do primeiro capítulo.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import glossario

# --------------------------------------------------------------------------- #
# Texto
# --------------------------------------------------------------------------- #

def escapar(texto: str) -> str:
    """Escapa o que o ReportLab leria como XML, antes de reintroduzir as tags."""
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# Pictogramas que a fonte da marca não tem: se passarem, saem como quadradinho
# (emoji, setas, caixinhas de checklist, checks). O "•" fica de fora de propósito,
# porque existe na fonte. O que for removido é relatado no fim.
PICTOGRAMAS = re.compile(
    r"[\u2190-\u21ff\u2300-\u23ff\u25a0-\u25ff\u2600-\u27bf\u2b00-\u2bff"
    r"\U0001F000-\U0001FAFF\uFE0F]"
)
REMOVIDOS: dict[str, int] = {}


def limpar_pictogramas(texto: str) -> str:
    """Tira emoji e afins, registrando o que saiu para poder avisar."""
    def troca(match):
        simbolo = match.group(0)
        REMOVIDOS[simbolo] = REMOVIDOS.get(simbolo, 0) + 1
        return ""

    return PICTOGRAMAS.sub(troca, texto)


SUSPEITOS: list[str] = []


def inline(texto: str) -> str:
    """Markdown inline -> marcas que o ReportLab entende."""
    texto = limpar_pictogramas(texto)
    texto = escapar(texto)
    texto = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", texto)          # link
    texto = re.sub(r"`([^`]+)`", r"\1", texto)                              # código
    texto = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", texto)        # negrito+itálico

    # "**texto *itálico***": o itálico fecha junto com o negrito, e converter na
    # ordem ingênua cruza as tags (<b>…<i>…</b></i>), que o ReportLab recusa
    texto = re.sub(r"\*\*([^*]+?)\*([^*]+?)\*\*\*", r"<b>\1<i>\2</i></b>", texto)

    def negrito(match):
        # converte o itálico de dentro ANTES de embrulhar no negrito
        dentro = re.sub(r"\*([^*]+?)\*", r"<i>\1</i>", match.group(1))
        return f"<b>{dentro}</b>"

    texto = re.sub(r"\*\*(.+?)\*\*", negrito, texto)
    texto = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<i>\1</i>", texto)
    texto = re.sub(r"__(.+?)__", negrito, texto)

    # rede de segurança: marcação torta derruba a montagem inteira, então vale
    # mais entregar o texto sem formatação do que não entregar
    if texto.count("<b>") != texto.count("</b>") or texto.count("<i>") != texto.count("</i>"):
        SUSPEITOS.append(texto)
        texto = re.sub(r"</?[bi]>", "", texto)

    return texto.strip()


def separar_tabela(linhas: list[str]) -> tuple[list[str], list[list[str]]] | None:
    """Converte linhas de tabela markdown em (cabeçalho, linhas)."""
    if len(linhas) < 2 or not linhas[0].strip().startswith("|"):
        return None
    if not re.match(r"^\s*\|[\s:|-]+\|\s*$", linhas[1]):
        return None

    def celulas(linha: str) -> list[str]:
        return [inline(c.strip()) for c in linha.strip().strip("|").split("|")]

    cabecalho = celulas(linhas[0])
    corpo = [celulas(ln) for ln in linhas[2:] if ln.strip().startswith("|")]
    # alinha larguras: tabela com célula faltando quebra o ReportLab
    largura = len(cabecalho)
    corpo = [(ln + [""] * largura)[:largura] for ln in corpo]
    return cabecalho, corpo


# --------------------------------------------------------------------------- #
# Parser de markdown
# --------------------------------------------------------------------------- #

def parse_markdown(texto: str, base: Path | None = None) -> tuple[str, list[dict]]:
    """
    Devolve (titulo do capítulo, lista de blocos).

    `base` é a pasta do arquivo, usada para resolver o caminho das imagens.
    """
    linhas = texto.replace("\r\n", "\n").split("\n")
    titulo = ""
    blocos: list[dict] = []
    paragrafo: list[str] = []
    lista: list[tuple[int, bool, str]] = []
    tipo_lista: str | None = None
    citacao: list[str] = []
    tabela: list[str] = []
    codigo: list[str] = []
    dentro_codigo = False
    linguagem = ""

    def descarregar_codigo():
        nonlocal dentro_codigo, linguagem
        if codigo:
            blocos.append({"type": "codigo", "linguagem": linguagem, "linhas": list(codigo)})
            codigo.clear()
        dentro_codigo = False
        linguagem = ""

    def descarregar_paragrafo():
        if paragrafo:
            juntado = inline(" ".join(paragrafo))
            if juntado:
                blocos.append({"type": "p", "text": juntado})
            paragrafo.clear()

    def descarregar_lista():
        nonlocal tipo_lista
        if lista:
            itens = [
                {"text": convertido, "nivel": nivel, "ordenado": ordenado}
                for nivel, ordenado, bruto in lista
                if (convertido := inline(bruto))
            ]
            if itens:
                blocos.append({"type": tipo_lista or "ul", "items": itens})
            lista.clear()
        tipo_lista = None

    def descarregar_citacao():
        if not citacao:
            return
        primeira = citacao[0].strip()
        rotulo = re.fullmatch(r"\*\*(.+?)\*\*:?", primeira)
        if rotulo:
            restante = " ".join(citacao[1:]).strip()
            if restante:
                blocos.append({
                    "type": "destaque",
                    "label": rotulo.group(1).upper(),
                    "text": inline(restante),
                })
                citacao.clear()
                return
        blocos.append({"type": "quote", "text": inline(" ".join(citacao))})
        citacao.clear()

    def descarregar_tudo():
        descarregar_paragrafo()
        descarregar_lista()
        descarregar_citacao()
        if dentro_codigo:            # cerca sem fechamento: o bloco entra assim mesmo
            descarregar_codigo()
        if tabela:
            convertida = separar_tabela(tabela)
            if convertida:
                cabecalho, corpo = convertida
                blocos.append({"type": "table", "headers": cabecalho, "rows": corpo})
            tabela.clear()

    for linha in linhas:
        crua = linha.rstrip()
        recuo = len(crua) - len(crua.lstrip())               # indentação = hierarquia

        # Bloco de código: dentro da cerca tudo entra verbatim — recuo, `#`, `|`
        # e `>` valem como código. Por isso este teste vem antes de todos os
        # outros, inclusive da tabela (uma linha de código pode começar com `|`).
        if dentro_codigo:
            if crua.strip().startswith("```"):
                descarregar_codigo()
            else:
                codigo.append(crua)
            continue

        if crua.strip().startswith("|"):
            descarregar_paragrafo()
            descarregar_lista()
            descarregar_citacao()
            tabela.append(crua)
            continue
        if tabela:
            descarregar_tudo()

        sem_marca = crua.strip()

        if sem_marca.startswith("```"):                      # abre o bloco de código
            descarregar_tudo()
            dentro_codigo = True
            linguagem = sem_marca.strip("`").strip()
            continue

        if re.match(r"^#\s+", sem_marca):                    # h1 -> título
            descarregar_tudo()
            if not titulo:
                titulo = re.sub(r"^#\s+", "", sem_marca).strip()
                continue
            # h1 extra no meio vira subtítulo, para não perder o texto
            blocos.append({"type": "h", "text": inline(re.sub(r"^#\s+", "", sem_marca))})
            continue

        if re.match(r"^#{2,6}\s+", sem_marca):               # h2..h6 -> subtítulo
            descarregar_tudo()
            blocos.append({"type": "h", "text": inline(re.sub(r"^#{2,6}\s+", "", sem_marca))})
            continue

        imagem = re.fullmatch(r"!\[([^\]]*)\]\(([^)]+)\)", sem_marca)
        if imagem:                                            # prancha / ilustração
            descarregar_tudo()
            caminho = Path(imagem.group(2))
            if base is not None and not caminho.is_absolute():
                caminho = base / caminho
            blocos.append({
                "type": "imagem",
                "caminho": str(caminho),
                "legenda": inline(imagem.group(1)),
            })
            continue

        marca_ul = re.match(r"^[-*+]\s+(.*)$", sem_marca)
        marca_ol = re.match(r"^\d+[.)]\s+(.*)$", sem_marca)
        if marca_ul or marca_ol:                             # lista
            descarregar_paragrafo()
            descarregar_citacao()
            ordenado = bool(marca_ol)
            # recuo no markdown = subitem (um nível; é o que um guia costuma ter)
            nivel = 1 if recuo >= 2 else 0

            # Subitem NÃO é outra lista: pertence ao item de cima. Fechar a lista
            # aqui é o que fazia a numeração reiniciar em "1." depois do subitem
            # (1, 2, 3, 1 em vez de 1, 2, 3, 4).
            novo_tipo = "ol" if ordenado else "ul"
            if nivel == 0 and tipo_lista and tipo_lista != novo_tipo:
                descarregar_lista()      # lista com marcador e lista numerada não se misturam
            if tipo_lista is None:
                tipo_lista = novo_tipo

            item = (marca_ol or marca_ul).group(1)
            item = re.sub(r"^\[[ xX]\]\s*", "", item)        # caixinha de checklist
            lista.append((nivel, ordenado, item))
            continue

        if sem_marca.startswith(">"):                        # citação / destaque
            descarregar_paragrafo()
            descarregar_lista()
            citacao.append(re.sub(r"^>\s?", "", sem_marca))
            continue

        if not sem_marca:                                    # linha em branco
            descarregar_tudo()
            continue

        descarregar_lista()
        descarregar_citacao()
        paragrafo.append(sem_marca)

    descarregar_tudo()
    return titulo, blocos


# --------------------------------------------------------------------------- #
# Montagem
# --------------------------------------------------------------------------- #

INTRO = re.compile(
    r"^(introdu|pref[áa]cio|apresenta|sobre|conclus|considera|posf[áa]cio|ep[íi]logo|"
    r"agradec|ap[êe]ndice|gloss[áa]rio|refer[êe]ncias|sum[áa]rio)",
    re.IGNORECASE,
)


def dividir_titulo(titulo: str, limite: int = 20) -> list[str]:
    """Quebra o título em linhas de capa, sem cortar palavra no meio."""
    if len(titulo) <= limite:
        return [titulo]

    palavras = titulo.split()
    linhas, atual = [], ""
    for palavra in palavras:
        tentativa = f"{atual} {palavra}".strip()
        if len(tentativa) > limite and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    if atual:
        linhas.append(atual)
    return linhas


def _ordem(caminho: Path) -> tuple[int, str]:
    """
    Ordem dos arquivos: o prefixo numérico manda (`_00-...` vem antes de `01-...`),
    e quem não tem número vai para o fim, em ordem alfabética.

    O `_` no começo é o que tira a numeração de capítulo; ele NÃO define a ordem,
    senão não daria para ter abertura sem número antes do capítulo 1.
    """
    achado = re.match(r"_?(\d+)", caminho.stem)
    return (int(achado.group(1)) if achado else 999, caminho.name)


def capitulos_de_pasta(pasta: Path) -> list[tuple[str, str, bool, Path]]:
    """(nome, markdown, numerado, pasta do arquivo) por .md, na ordem definida."""
    arquivos = sorted(
        (p for p in pasta.glob("*.md") if p.is_file() and p.name != glossario.ARQUIVO),
        key=_ordem,
    )
    if not arquivos:
        raise SystemExit(f"nenhum .md encontrado em {pasta}")

    return [
        (caminho.stem, caminho.read_text(encoding="utf-8"),
         not caminho.name.startswith("_"), pasta)
        for caminho in arquivos
    ]


def capitulos_de_json(caminho: Path) -> list[tuple[str, str, bool, Path]]:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    if isinstance(dados, dict):
        dados = dados.get("articles") or dados.get("artigos") or []
    saida = []
    for item in dados:
        titulo = item.get("title") or item.get("titulo") or ""
        corpo = item.get("article") or item.get("artigo") or ""
        cabecalho = f"# {titulo}\n\n" if titulo and not corpo.lstrip().startswith("#") else ""
        saida.append((titulo or "Sem título", cabecalho + corpo, True, caminho.parent))
    return saida


def main():
    parser = argparse.ArgumentParser(
        description="Converte markdown em manuscrito JSON para o build_ebook.py."
    )
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--pasta", help="pasta com um .md por capítulo")
    entrada.add_argument("--json", dest="arquivo_json", help="lista de artigos em JSON")
    parser.add_argument("--saida", help="caminho do JSON (padrão: manuscrito.json)")
    parser.add_argument("--meta", help="JSON com title/author/kicker/subtitle_lines/cover_footer")
    parser.add_argument("--titulo")
    parser.add_argument("--autor")
    parser.add_argument("--kicker")
    parser.add_argument("--subtitulo", action="append", default=[], help="repita para várias linhas")
    parser.add_argument("--rodape", help="tag do rodapé da capa (ex.: a assinatura)")
    parser.add_argument("--linhas", help="linhas da capa separadas por |")
    parser.add_argument(
        "--glossario",
        help="arquivo de termos (JSON ou markdown com a tabela). Sem isto, vale o "
             f"`{glossario.ARQUIVO}` da pasta dos artigos, e depois o `glossario` do --meta.",
    )
    args = parser.parse_args()

    meta = {}
    if args.meta:
        meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))

    pasta_entrada = (
        Path(args.pasta).expanduser() if args.pasta
        else Path(args.arquivo_json).expanduser().parent
    )
    fontes = (
        capitulos_de_pasta(pasta_entrada) if args.pasta
        else capitulos_de_json(Path(args.arquivo_json).expanduser())
    )

    # Termos do glossário: arquivo da linha de comando > `termos.md` da pasta >
    # lista do --meta. É a MESMA lista que vira nota de pé de página e verbete no
    # fim do livro, então ela viaja junto do manuscrito.
    termos = (
        glossario.carregar(args.glossario) if args.glossario
        else glossario.da_pasta(pasta_entrada) or glossario.normalizar(meta.get("glossario") or [])
    )

    capitulos = []
    contador = 0
    for nome, markdown, numerado, pasta_do_arquivo in fontes:
        titulo, blocos = parse_markdown(markdown, pasta_do_arquivo)
        titulo = titulo or nome.replace("-", " ").replace("_", " ").strip()

        if not blocos:
            print(f"  aviso: '{nome}' não gerou conteúdo; ignorado", file=sys.stderr)
            continue

        # Sem número: abertura e fecho do livro. Vale pelo prefixo `_` no nome do
        # arquivo ou pelo próprio título (Introdução, Prefácio, Conclusão...).
        if numerado and INTRO.match(titulo.lstrip("0123456789 .-–—")):
            numerado = False

        if numerado:
            contador += 1
            rotulo = f"{contador}. {titulo}"
            kicker = f"CAPÍTULO {contador:02d}"
        else:
            rotulo = titulo
            kicker = ""

        capitulos.append({
            "id": f"cap{len(capitulos) + 1}",
            "toc": rotulo,
            "outline": rotulo,
            "kicker": kicker,
            "title": inline(titulo),
            # arquivo cujo conteúdo é só imagem vira prancha: a página inteira é da
            # ilustração, sem cabeçalho de capítulo por cima dela
            "sem_cabecalho": all(b.get("type") == "imagem" for b in blocos),
            "blocks": blocos,
        })

    if not capitulos:
        raise SystemExit("nenhum capítulo com conteúdo")

    titulo_livro = (
        args.titulo or meta.get("title") or os.getenv("TERRAS_EBOOK_TITULO")
        or capitulos[0]["title"]
    )
    autor = args.autor or meta.get("author") or os.getenv("TERRAS_EBOOK_AUTOR", "")

    linhas_capa = (
        [ln.strip() for ln in args.linhas.split("|")]
        if args.linhas
        else meta.get("title_lines") or dividir_titulo(titulo_livro)
    )

    manuscrito = {
        "output": meta.get("output", ""),
        "title": titulo_livro,
        "title_lines": linhas_capa,
        "author": autor,
        "kicker": args.kicker or meta.get("kicker", ""),
        "subtitle_lines": args.subtitulo or meta.get("subtitle_lines", []),
        "cover_footer": args.rodape or meta.get("cover_footer", ""),
        "running_header": meta.get("running_header", titulo_livro),
        "running_header_right": meta.get("running_header_right", autor),
        "glossario": glossario.json_para_manuscrito(termos),
        "chapters": capitulos,
    }
    if meta.get("glossario_titulo"):
        manuscrito["glossario_titulo"] = meta["glossario_titulo"]

    destino = Path(args.saida or "manuscrito.json").expanduser()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(manuscrito, ensure_ascii=False, indent=2), encoding="utf-8")

    contagem = {}
    for capitulo in capitulos:
        for bloco in capitulo["blocks"]:
            contagem[bloco["type"]] = contagem.get(bloco["type"], 0) + 1

    print(f"✓ {destino}")
    print(f"  título: {titulo_livro} | capa em {len(linhas_capa)} linha(s)")
    print(f"  {len(capitulos)} capítulo(s) | blocos: {dict(sorted(contagem.items()))}")

    if termos:
        com_nota = [t["termo"] for t in termos if t["rodape"]]
        print(f"  glossário: {len(termos)} termo(s)"
              + (f", {len(com_nota)} com nota de pé de página: {', '.join(com_nota)}" if com_nota else ""))
    else:
        print(f"  aviso: sem termos de glossário — escreva o `{glossario.ARQUIVO}` na pasta "
              "(ver references/manuscrito.md); o livro sai sem glossário", file=sys.stderr)

    if REMOVIDOS:
        print("  pictogramas removidos (a fonte da marca não tem estes glifos):")
        for simbolo, vezes in sorted(REMOVIDOS.items(), key=lambda x: -x[1]):
            print(f"    {simbolo!r} ×{vezes}")

    if SUSPEITOS:
        print(f"  aviso: {len(SUSPEITOS)} trecho(s) com marcação desbalanceada; "
              "entregues sem formatação:", file=sys.stderr)
        for trecho in SUSPEITOS[:3]:
            print(f"    {trecho[:70]!r}", file=sys.stderr)

    return destino


if __name__ == "__main__":
    main()

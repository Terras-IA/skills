"""
Monta o EPUB a partir de artigos em markdown — sem SMTP, sem chave de API.

Esta é a etapa final da rota B (a sessão escreve os artigos, este script monta o
arquivo). Também serve para empacotar qualquer conjunto de markdown como e-book.

Duas entradas:

    --json artigos.json     lista [{title, channel, url, article}]
    --pasta artigos/        um .md por capítulo; o título é o primeiro `# ` do arquivo

Metadados (nesta ordem de precedência: argumento > variável de ambiente > padrão):
    --titulo  / TERRAS_EBOOK_TITULO   (padrão: "E-book <data>")
    --autor   / TERRAS_EBOOK_AUTOR    (padrão: vazio)
    --idioma  / TERRAS_EBOOK_IDIOMA   (padrão: pt-BR)

Adaptado de zarazhangrui/youtube-to-ebook (MIT). Ver CREDITS.md.
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import markdown
from ebooklib import epub

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import glossario  # noqa: E402
import identidade as ident  # noqa: E402
from identidade import escurecer_para_ler, misturar_com_branco  # noqa: E402

CSS = """
body { font-family: Georgia, serif; line-height: 1.6; padding: 1em; }
h1 { font-size: 1.5em; margin-top: 1em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
h2 { font-size: 1.3em; margin-top: 1em; }
h3 { font-size: 1.1em; }
.fonte { background: #f5f5f5; padding: 1em; border-left: 3px solid #666;
         margin-bottom: 1.5em; font-size: 0.95em; }
.link { margin-top: 1.5em; padding: 0.5em; background: #f0f0f0; display: block; }
a.termo { color: inherit; text-decoration: none; border-bottom: 1px dotted #999; }
dl.glossario dt { font-weight: bold; margin-top: 0.9em; }
dl.glossario dd { margin: 0.15em 0 0 0; }
"""

# O link do termo não pode virar azul sublinhado no meio da frase: ele é a nota
# de pé de página do EPUB, e o leitor só descobre quando procura.
CSS_TERMO = """
a.termo {{ color: inherit; text-decoration: none; border-bottom: 1px dotted {linha}; }}
dl.glossario dt {{ font-weight: bold; margin-top: 0.9em; }}
dl.glossario dd {{ margin: 0.15em 0 0 0; }}
"""


def css_da_identidade(identidade: dict) -> str:
    """
    Folha de estilo a partir dos tokens da identidade.

    O acento puro fica em filetes e titulos de secao; texto miudo em acento usa a
    versao escurecida, pelo mesmo motivo do PDF: ciano vivo sobre papel branco
    fica abaixo do contraste minimo de leitura.
    """
    cores = identidade["cores"]
    base = cores.get("base", "#060608")
    acento = cores.get("acento", "#07d4ec")
    acento2 = cores.get("acento_2") or acento
    tinta = cores.get("tinta", "#14141e")
    acento_texto = escurecer_para_ler(acento)
    acento_fundo = misturar_com_branco(acento, 0.92)

    return f"""
body {{ font-family: Georgia, serif; line-height: 1.6; padding: 1em; color: {tinta}; }}
h1 {{ font-size: 1.5em; margin-top: 1.2em; padding-bottom: 0.35em; color: {tinta};
      border-bottom: 2px solid {acento}; }}
h2 {{ font-size: 1.25em; margin-top: 1.1em; color: {tinta}; }}
h3 {{ font-size: 1.1em; color: {tinta}; }}
a {{ color: {acento_texto}; }}
blockquote {{ background: {acento_fundo}; border-left: 3px solid {acento};
              margin: 1em 0; padding: 0.8em 1em; }}
table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
th {{ background: {base}; color: #ffffff; text-align: left; padding: 0.5em 0.6em; }}
td {{ border-bottom: 1px solid {misturar_com_branco(base, 0.82)}; padding: 0.45em 0.6em; }}
hr {{ border: 0; height: 2px;
      background: linear-gradient(90deg, {acento}, {acento2}); }}
.fonte {{ background: {acento_fundo}; padding: 1em; border-left: 3px solid {acento};
         margin-bottom: 1.5em; font-size: 0.95em; }}
.link {{ margin-top: 1.5em; padding: 0.5em; background: #f0f0f0; display: block; }}
""" + CSS_TERMO.format(linha=misturar_com_branco(base, 0.55))


def slug(texto):
    """Nome de arquivo seguro a partir de um título."""
    texto = re.sub(r"[^\w\s-]", "", texto, flags=re.UNICODE).strip().lower()
    return re.sub(r"[\s_-]+", "-", texto)[:60] or "ebook"


def artigos_da_pasta(pasta):
    """
    Lê todos os .md da pasta como capítulos, na mesma ordem do PDF: o prefixo
    numérico manda e o `_` no começo só marca que o capítulo não é numerado.

    O `termos.md` fica de fora: ele é a tabela de termos do glossário, não um
    capítulo (quem o lê é o `glossario.py`).
    """
    def ordem(caminho: Path) -> tuple[int, str]:
        achado = re.match(r"_?(\d+)", caminho.stem)
        return (int(achado.group(1)) if achado else 999, caminho.name)

    artigos = []

    for caminho in sorted(
        (p for p in Path(pasta).glob("*.md") if p.is_file() and p.name != glossario.ARQUIVO),
        key=ordem,
    ):
        texto = caminho.read_text(encoding="utf-8")
        # Título = primeiro heading de nível 1, se houver.
        encontrado = re.search(r"^#\s+(.+)$", texto, flags=re.MULTILINE)
        titulo = encontrado.group(1).strip() if encontrado else caminho.stem
        artigos.append({"title": titulo, "channel": "", "url": "", "article": texto})

    return artigos


def artigos_do_json(caminho):
    """Lê a lista de artigos no formato do pipeline."""
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    artigos = []
    for item in dados:
        artigos.append({
            "title": item.get("title") or item.get("titulo") or "Sem título",
            "channel": item.get("channel", ""),
            "url": item.get("url", ""),
            "article": item.get("article") or item.get("artigo") or "",
        })
    return artigos


TIPOS = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
         ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}


def embutir_imagens(texto: str, base: Path, registro: dict) -> str:
    """
    Copia as imagens locais citadas no markdown para dentro do EPUB e troca o
    caminho pelo nome interno.

    Sem isso a ilustração simplesmente não aparece no leitor: caminho de fora do
    EPUB não viaja com o arquivo. O registro evita duplicar a mesma imagem quando
    ela é citada mais de uma vez.
    """
    def troca(match):
        alt, src = match.group(1), match.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)

        arquivo = Path(src)
        if not arquivo.is_absolute():
            arquivo = (base / arquivo).resolve()
        if not arquivo.exists():
            print(f"  aviso: imagem não encontrada: {arquivo}", file=sys.stderr)
            return match.group(0)

        interno = registro.get(str(arquivo))
        if interno is None:
            interno = f"imagens/{len(registro) + 1:02d}-{arquivo.name}"
            registro[str(arquivo)] = interno
        return f"![{alt}]({interno})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", troca, texto)


def montar_epub(artigos, destino, titulo=None, autor=None, idioma=None,
                identidade=None, capa=None, base=None, termos=None,
                titulo_glossario=None, lista=None):
    """Monta o EPUB e grava em `destino`. Devolve o Path do arquivo."""
    titulo = titulo or os.getenv("TERRAS_EBOOK_TITULO") or f"E-book {datetime.now():%d/%m/%Y}"
    autor = autor if autor is not None else os.getenv("TERRAS_EBOOK_AUTOR", "")
    idioma = idioma or os.getenv("TERRAS_EBOOK_IDIOMA", "pt-BR")

    # quem chama pode trazer a lista já montada (o `main` faz isso, para poder
    # relatar quantos termos o texto realmente usou)
    lista = lista if lista is not None else glossario.Lista(termos or [])
    # O glossário é o último arquivo do livro, e o link do termo precisa do nome
    # dele ANTES de o capítulo existir — por isso o nome é calculado aqui.
    arquivo_glossario = f"capitulo_{len(artigos) + 1}.xhtml"

    livro = epub.EpubBook()
    livro.set_identifier(f"terras-ebook-{datetime.now():%Y%m%d%H%M%S}")
    livro.set_title(titulo)
    livro.set_language(idioma)
    if autor:
        livro.add_author(autor)

    # A capa vem do PDF da mesma identidade (primeira página renderizada), então
    # o EPUB e o PDF não divergem no que o leitor vê primeiro.
    if capa and Path(capa).exists():
        livro.set_cover("capa.png", Path(capa).read_bytes(), create_page=True)

    estilo = epub.EpubItem(
        uid="style_nav", file_name="style/nav.css", media_type="text/css",
        content=css_da_identidade(identidade) if identidade else CSS,
    )
    livro.add_item(estilo)

    # imagens locais: para dentro do EPUB, com o caminho reescrito
    registro: dict[str, str] = {}
    for artigo in artigos:
        artigo["article"] = embutir_imagens(artigo["article"], base or AQUI, registro)
    for origem, interno in registro.items():
        livro.add_item(epub.EpubItem(
            uid=f"imagem_{len(livro.items)}",
            file_name=interno,
            media_type=TIPOS.get(Path(origem).suffix.lower(), "image/png"),
            content=Path(origem).read_bytes(),
        ))

    capitulos = []

    for i, artigo in enumerate(artigos):
        # o termo vira link para o verbete — é a nota de pé de página deste
        # formato, onde não existe página fixa para pendurar uma nota
        artigo["article"] = glossario.marcar_markdown(
            artigo["article"], lista, arquivo_glossario
        )

        # `extra` liga as tabelas de barra (o markdown puro não converte) e
        # `sane_lists` evita que uma lista engula o parágrafo seguinte.
        html = markdown.markdown(artigo["article"], extensions=["extra", "sane_lists"])

        nota = ""
        if artigo.get("channel") or artigo.get("url"):
            referencia = artigo.get("channel") or "vídeo original"
            nota = (
                f'<div class="fonte"><p><em>Baseado em "{artigo["title"]}", '
                f"de <strong>{referencia}</strong>.</em></p></div>"
            )

        link = ""
        if artigo.get("url"):
            link = f'<p class="link">Vídeo original: {artigo["url"]}</p>'

        conteudo = (
            "<html><head>"
            '<link rel="stylesheet" type="text/css" href="style/nav.css"/>'
            f"</head><body>{nota}{html}{link}</body></html>"
        )

        capitulo = epub.EpubHtml(
            title=artigo["title"][:80], file_name=f"capitulo_{i + 1}.xhtml", lang=idioma
        )
        capitulo.content = conteudo
        capitulo.add_item(estilo)

        livro.add_item(capitulo)
        capitulos.append(capitulo)

    # O glossário fecha o livro, com os termos que o texto realmente usou.
    if lista.verbetes():
        rotulo = titulo_glossario or glossario.TITULO_PADRAO
        conteudo = (
            "<html><head>"
            '<link rel="stylesheet" type="text/css" href="style/nav.css"/>'
            f"</head><body>{glossario.html(lista, rotulo)}</body></html>"
        )
        capitulo_glossario = epub.EpubHtml(title=rotulo, file_name=arquivo_glossario, lang=idioma)
        capitulo_glossario.content = conteudo
        capitulo_glossario.add_item(estilo)
        livro.add_item(capitulo_glossario)
        capitulos.append(capitulo_glossario)

    livro.toc = tuple(capitulos)
    livro.add_item(epub.EpubNcx())
    livro.add_item(epub.EpubNav())
    livro.spine = ["nav"] + capitulos

    destino.parent.mkdir(parents=True, exist_ok=True)
    epub.write_epub(str(destino), livro, {})

    return destino


def main():
    parser = argparse.ArgumentParser(description="Monta um EPUB a partir de markdown.")
    entrada = parser.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--json", dest="arquivo_json", help="JSON com a lista de artigos")
    entrada.add_argument("--pasta", help="pasta com um .md por capítulo")
    parser.add_argument("--saida", help="caminho do EPUB (padrão: ./<slug-do-título>.epub)")
    parser.add_argument("--titulo")
    parser.add_argument("--autor")
    parser.add_argument("--idioma")
    parser.add_argument(
        "--identidade",
        help="identidade a usar: um caminho de JSON, ou os apelidos 'slc' "
             "(padrão da casa) e 'terras' (estilo sem as cores da marca). Sem isto, "
             "vale a identidade do projeto (identidade/identidade.json na raiz do "
             "projeto), copiada da base da casa na primeira vez.",
    )
    parser.add_argument(
        "--capa",
        help="imagem de capa (PNG/JPG). Dica: renderize a página 1 do PDF da "
             "mesma identidade, para PDF e EPUB não divergirem.",
    )
    parser.add_argument(
        "--glossario",
        help="arquivo de termos (JSON ou markdown com a tabela) ou a pasta dos "
             f"artigos, de onde se lê o `{glossario.ARQUIVO}`. Sem isto, o próprio "
             "`--pasta` (ou a pasta do `--json`) é consultado.",
    )
    parser.add_argument("--titulo-glossario", help="rótulo do capítulo (padrão: Glossário)")
    parser.add_argument(
        "--arquivar",
        action="store_true",
        help="guarda também uma cópia datada em newsletters/",
    )
    args = parser.parse_args()

    artigos = (
        artigos_do_json(args.arquivo_json)
        if args.arquivo_json
        else artigos_da_pasta(args.pasta)
    )

    if not artigos:
        raise SystemExit("Nenhum artigo encontrado na entrada.")

    titulo = args.titulo or os.getenv("TERRAS_EBOOK_TITULO") or f"E-book {datetime.now():%d/%m/%Y}"
    destino = Path(args.saida).expanduser() if args.saida else Path.cwd() / f"{slug(titulo)}.epub"

    # pasta de onde os caminhos de imagem do markdown são resolvidos
    base_entrada = (
        Path(args.pasta).expanduser() if args.pasta
        else Path(args.arquivo_json).expanduser().parent
    )

    # Identidade: apelido ou caminho mandam; sem eles, vale a do projeto (criada
    # da base da casa na primeira vez) — a mesma regra do build_ebook, para o PDF
    # e o EPUB do mesmo diretório não saírem com caras diferentes.
    identidade = None
    escolha = ident.apelido(args.identidade)
    caminho_identidade = None

    if escolha == "terras":
        # a marca terras: mesmas cores do PDF, sem identidade de projeto no meio
        identidade = ident.marca_terras()
        if identidade is None:
            print("  aviso: brand.json não encontrado; usando o estilo padrão", file=sys.stderr)
        else:
            print(f"identidade: {identidade['nome']}")
    elif escolha == "casa":
        caminho_identidade = ident.base_padrao()
    elif args.identidade:
        caminho_identidade = Path(args.identidade).expanduser().resolve()
    else:
        raiz = ident.raiz_do_projeto(base_entrada)
        caminho_identidade, criada = ident.do_projeto(raiz)
        if criada and caminho_identidade:
            print(f"  identidade: este diretório não tinha uma; copiei o padrão "
                  f"Sousa Lima para {caminho_identidade.parent}")
        elif caminho_identidade is None and ident.base_padrao().exists():
            caminho_identidade = ident.base_padrao()
            print("  aviso: não consegui copiar a identidade para o projeto; "
                  "usando a base da skill", file=sys.stderr)

    if caminho_identidade is not None:
        if not caminho_identidade.exists():
            raise SystemExit(f"identidade não encontrada: {caminho_identidade}")
        identidade = json.loads(caminho_identidade.read_text(encoding="utf-8"))
        print(f"identidade: {identidade.get('nome', caminho_identidade.stem)}")

    # Termos do glossário: arquivo/pasta da linha de comando, senão o `termos.md`
    # da própria entrada (que é como a pasta dos artigos costuma trazer).
    termos = (
        glossario.carregar(args.glossario) if args.glossario
        else glossario.da_pasta(base_entrada)
    )
    lista = glossario.Lista(termos)

    # Capa: caminho relativo vale a partir da pasta do projeto (é de lá que ele é
    # digitado, mesmo quando o comando roda de outro diretório) — e capa que não
    # existe AVISA, porque o leitor abriria o livro sem capa nenhuma em silêncio.
    capa = None
    if args.capa:
        capa = Path(args.capa).expanduser()
        if not capa.exists() and not capa.is_absolute():
            for candidato in (base_entrada / capa, base_entrada.parent / capa):
                if candidato.exists():
                    capa = candidato
                    break
        if not capa.exists():
            print(f"  aviso: capa não encontrada ({args.capa}); o EPUB sai sem capa",
                  file=sys.stderr)
            capa = None

    arquivo = montar_epub(
        artigos, destino, titulo=args.titulo, autor=args.autor, idioma=args.idioma,
        identidade=identidade, capa=capa, base=base_entrada, termos=termos,
        titulo_glossario=args.titulo_glossario, lista=lista,
    )

    print(f"✓ EPUB com {len(artigos)} capítulo(s): {arquivo}")
    if termos:
        com_link = lista.com_marca()
        print(f"  glossário: {len(lista.verbetes())} verbete(s) de {len(termos)} termo(s)"
              f" | {len(com_link)} com link no texto"
              + (f": {', '.join(t['termo'] for t in com_link)}" if com_link else ""))
        if lista.faltando():
            print("  aviso: termo declarado e não usado no texto ficou fora do glossário: "
                  + ", ".join(lista.faltando()), file=sys.stderr)
    else:
        print(f"  aviso: sem termos de glossário — escreva o `{glossario.ARQUIVO}` na pasta "
              "(ver references/manuscrito.md); o livro sai sem glossário", file=sys.stderr)

    if args.arquivar:
        pasta = AQUI / "newsletters"
        pasta.mkdir(exist_ok=True)
        copia = pasta / f"{arquivo.stem}_{datetime.now():%Y%m%d-%H%M%S}.epub"
        shutil.copy2(arquivo, copia)
        print(f"  cópia arquivada: {copia}")

    return arquivo


if __name__ == "__main__":
    main()

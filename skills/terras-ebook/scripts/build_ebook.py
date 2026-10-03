"""
Monta o e-book em PDF A5, na identidade da marca terras.

Fluxo: manuscrito JSON (ver references/manuscrito.md) -> capa PDF + miolo PDF ->
merge -> anotacoes de link do sumario + marcadores do PDF.

Duas decisoes que o script resolve e que costumam quebrar esse tipo de gerador:

1. Capa e miolo sao DOIS PDFs mesclados. Desenhar a capa no `onFirstPage` de um
   documento Platypus faz o texto do primeiro capitulo carimbar por cima dela.
2. O sumario clicavel e construido DEPOIS do merge, medindo as caixas das linhas
   com pdfplumber e escrevendo anotacoes com pypdf. Os destinos nomeados do
   ReportLab nao sobrevivem ao merge com a capa.

Glossario e notas de pe de pagina saem da lista `glossario` do manuscrito (ver
`glossario.py`): o termo ganha nota na pagina em que aparece pela primeira vez e
verbete no capitulo de fecho, montado no fim do livro.

Tudo que e identidade (cor e fonte) vem de `brand.json`; nada de hex solto aqui.

Uso:
    build_ebook.py manuscrito.json [--saida livro.pdf] [--tema pessoal] [--brand-dir DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import Fit
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PAGE_W, PAGE_H = A5

# Faixa do rodapé: a nota de pé de página ocupa o espaço entre a mancha e o
# filete do folio, e por isso empurra o texto daquela página para cima. A folga
# é o respiro entre a última linha do texto e o filete curto da nota.
MARGEM_INFERIOR = 17 * mm
FOLGA_NOTAS = 3.4 * mm
ESPACO_NOTAS = 3.0

BRAND_DIR_PADRAO = Path.home() / "Documents" / "Diversos" / "terras-brand"
CACHE_DIR = Path.home() / ".config" / "terras-ebook" / "fontes"
TEMA_PADRAO = os.getenv("TERRAS_EBOOK_TEMA", "pessoal")

sys.path.insert(0, str(Path(__file__).resolve().parent))

# As tres funcoes de cor moram em identidade.py, compartilhadas com o export_epub,
# junto com a identidade do projeto (onde ela mora e a copia da base).
import identidade as ident  # noqa: E402
from identidade import (  # noqa: E402
    contraste_com_branco as _contraste,
    escurecer_para_ler as _escurecer,
    misturar_com_branco as _misturar,
)

# A lista de termos e as marcas de nota sao as mesmas no PDF e no EPUB.
import glossario  # noqa: E402
from glossario import MARCA, numeros_no_texto, texto_verbete  # noqa: E402

# Fallback de fonte, na ordem: primeiro o que existe nesta maquina.
FONTES_SISTEMA = {
    "regular": [
        "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "bold": [
        "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    # A Inter da marca e variavel so no eixo de peso: nao tem italico de verdade.
    # Para italico, usamos uma sans italica do sistema (a mais proxima da Inter).
    "italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    ],
    # Monoespacada: a identidade da marca nao tem uma, e o bloco de codigo precisa
    # de coluna alinhada. Fica do sistema ate a marca declarar `fontes.mono`.
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
    ],
}


# --------------------------------------------------------------------------- #
# Identidade
# --------------------------------------------------------------------------- #

CACHES = {"inter": "inter", "sousa-lima": "sl"}


def _dentro(caminho: Path, pasta: Path) -> bool:
    """O caminho está dentro desta pasta? (a identidade é do projeto?)"""
    try:
        caminho.relative_to(pasta)
        return True
    except ValueError:
        return False


def carregar_identidade(argumento: str | None, brand_dir: Path, tema: str,
                        projeto: Path | None = None) -> dict:
    """
    A identidade em uso, nesta ordem:

    1. `--identidade CAMINHO` — ou os apelidos `slc`/`sousa-lima` (a base da casa)
       e `terras` (o `brand.json` do tema);
    2. **a identidade do projeto** — `<projeto>/identidade/identidade.json`, ao
       lado do manuscrito. Não existindo, ela é copiada da base da casa (fontes e
       ativos juntos, caminhos relativos), e passa a ser deste diretório: editar
       lá não mexe em nenhum outro livro;
    3. o `brand.json` do tema, que é a identidade terras (`--tema`, `--brand-dir`).

    A identidade ser do diretório é o que impede o livro sair na identidade errada
    por esquecimento do flag — e é o único jeito de montar de outra pasta sem
    perder a cara do projeto.

    O dicionario devolvido sempre tem: `cores`, `fontes`, `ativos`,
    `capa_estilo` e `_base` (pasta para resolver os caminhos relativos).
    """
    escolha = ident.apelido(argumento)
    if escolha == "terras":
        # apelido explícito: a marca terras, e não a identidade do projeto
        argumento, projeto = None, None
    elif escolha == "casa":
        argumento = str(ident.base_padrao())

    if not argumento and projeto is not None:
        achado, criada = ident.do_projeto(projeto)
        if achado:
            argumento = str(achado)
            if criada:
                print(f"  identidade: este diretório não tinha uma; copiei o padrão "
                      f"Sousa Lima para {achado.parent}")
                print("     (a identidade é deste diretório — cores, fontes e logo se editam lá)")
        elif ident.base_padrao().exists():
            # não deu para copiar (pasta sem permissão, por exemplo): vale a base
            argumento = str(ident.base_padrao())
            print("  aviso: não consegui copiar a identidade para o projeto; "
                  "usando a base da skill", file=sys.stderr)

    if argumento:
        caminho = Path(argumento).expanduser().resolve()
        if not caminho.exists():
            raise SystemExit(f"identidade não encontrada: {caminho}")

        dados = json.loads(caminho.read_text(encoding="utf-8"))
        dados["_base"] = caminho.parent
        dados.setdefault("nome", caminho.parent.name)
        # identidade que vive dentro do projeto é editável: o cache de fontes
        # leva impressão digital dos arquivos (ver preparar_fontes)
        dados["_projeto"] = bool(projeto and _dentro(caminho, Path(projeto)))
        if "capa_estilo" not in dados:
            tem_logo = bool((dados.get("ativos") or {}).get("logo_claro"))
            dados["capa_estilo"] = "logo-rede" if tem_logo else "terras"
        return dados

    # Rota da marca terras (`--identidade terras`, sem identidade de projeto, ou
    # `--tema`): a leitura do brand.json é a mesma que o EPUB usa (ident.marca_terras).
    marca = ident.marca_terras(tema, Path(brand_dir))
    if marca is None:
        print(f"  aviso: {Path(brand_dir) / 'brand.json'} não encontrado; "
              "usando a paleta padrão", file=sys.stderr)
        marca = {
            "nome": f"terras ({tema})",
            "cores": {"base": "#060608", "base_alt": "#0a0a0e", "acento": "#07d4ec",
                      "texto": "#e8e8f0", "texto_apoio": "#8a8aad", "linha": "#1a1a2e"},
            "fontes": {"texto": {"arquivos": [], "pesos": {"regular": 400, "bold": 600,
                                                           "forte": 700}, "cache": "inter"}},
            "ativos": {}, "capa_estilo": "terras", "_base": Path(brand_dir),
        }
    return marca


def contraste_com_branco(hexcor: str) -> float:
    """Razao de contraste WCAG da cor contra branco (1 a 21)."""
    return _contraste(hexcor)


def escurecer_para_ler(hexcor: str, minimo: float = 4.5) -> str:
    """Acento escurecido ate ficar legivel sobre papel branco (ver identidade.py)."""
    return _escurecer(hexcor, minimo)


def misturar_com_branco(hexcor: str, proporcao: float) -> str:
    """Tinta clara: cor misturada com branco (fundo de destaque, por exemplo)."""
    return _misturar(hexcor, proporcao)


def paleta(cores: dict, capa_estilo: str = "terras") -> dict:
    """Converte os tokens da identidade nos papeis que o PDF usa."""
    acento = cores.get("acento", "#07d4ec")
    acento2 = cores.get("acento_2") or acento
    base = cores.get("base", "#060608")

    return {
        # capa
        "capa_fundo": HexColor(base),
        "capa_fundo_alt": HexColor(cores.get("base_alt") or base),
        "capa_titulo": HexColor(cores.get("texto", "#e8e8f0")),
        "capa_apoio": HexColor(cores.get("texto_apoio", "#8a8aad")),
        "acento": HexColor(acento),
        "acento_2": HexColor(acento2),
        # miolo (papel claro: e-book tambem e lido impresso)
        "tinta": HexColor(cores.get("tinta", "#14141e")),
        "tinta_fraca": HexColor(cores.get("tinta_fraca", "#5a5c70")),
        "linha": HexColor(cores.get("linha_clara", "#d7dae8")),
        "acento_texto": HexColor(escurecer_para_ler(acento)),
        "acento2_texto": HexColor(escurecer_para_ler(acento2)),
        "acento_fundo": HexColor(misturar_com_branco(acento, 0.92)),
        "papel_alt": HexColor(cores.get("papel_alt", "#f7f8fc")),
        # a identidade escura pede cabecalho de tabela em navy; a terras, no acento
        "tabela_fundo": HexColor(base if capa_estilo == "logo-rede" else escurecer_para_ler(acento)),
        "papel": white,
    }


# --------------------------------------------------------------------------- #
# Fontes
# --------------------------------------------------------------------------- #

# Caracteres que o miolo precisa ter; sem eles o PDF sai com quadradinhos e,
# pior, o texto deixa de ser extraivel (busca e copia param de funcionar).
REQUERIDOS = set("áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ—–“”‘’…·°ºª§€")


def _instanciar(origem: Path, peso: int, destino: Path) -> bool:
    """Extrai uma instancia estatica de peso de uma fonte variavel woff2."""
    try:
        from fontTools.ttLib import TTFont as FTFont
        from fontTools.varLib import instancer
    except ImportError:
        return False

    try:
        fonte = FTFont(str(origem))
        if "fvar" in fonte:
            fonte = instancer.instantiateVariableFont(fonte, {"wght": peso})
        # A fonte variável do Google mantém o nome da instância padrão ("Thin")
        # depois de instanciada: sem renomear, todo peso vira "Thin" no PDF e a
        # conferência de fonte passa a mentir.
        for registro in fonte["name"].names:
            if registro.nameID in (1, 3, 4, 6):
                try:
                    atual = registro.toUnicode()
                except Exception:
                    continue
                if atual.lower().startswith(("thin", "extralight", "light", "regular",
                                             "medium", "semibold", "bold", "extrabold",
                                             "black")) or "montserrat" in atual.lower() or "inter" in atual.lower():
                    base = atual.split("-")[0].split()[0]
                    novo = f"{base}-{peso}"
                    registro.string = novo
        fonte.flavor = None
        destino.parent.mkdir(parents=True, exist_ok=True)
        fonte.save(str(destino))
        return True
    except Exception as erro:
        print(f"  aviso: nao consegui preparar {origem.name}: {erro}", file=sys.stderr)
        return False


def _preparar(arquivos: list[Path], peso: int, destino: Path) -> bool:
    """
    Instancia o peso e JUNTA tudo num arquivo so.

    Fonte de marca costuma vir fatiada, ou em subsets que se completam (o
    "latin" tem Latin-1, inclusive ç e ã; o "latin-ext" tem Latin Extended), ou
    como uma variavel so. Usar apenas a "ext" parece melhor pelo tamanho, mas
    deixa o portugues sem cedilha e sem til — e o texto vira byte nulo no PDF.
    Por isso: junta todos os arquivos e, se a juncao falhar, usa o primeiro.
    """
    import tempfile

    existentes = [Path(a) for a in arquivos if Path(a).exists()]
    if not existentes:
        return False

    with tempfile.TemporaryDirectory(prefix="terras-fontes-") as tmp:
        estaticas = []
        for i, origem in enumerate(existentes):
            parcial = Path(tmp) / f"parte{i}.ttf"
            if _instanciar(origem, peso, parcial):
                estaticas.append(str(parcial))

        if not estaticas:
            return False

        destino.parent.mkdir(parents=True, exist_ok=True)

        if len(estaticas) > 1:
            try:
                from fontTools.merge import Merger

                juntas = Merger().merge(estaticas)
                juntas.flavor = None
                juntas.save(str(destino))
                return True
            except Exception as erro:
                print(
                    f"  aviso: não consegui juntar as subsets ({erro}); usando a primeira",
                    file=sys.stderr,
                )

        return _instanciar(existentes[0], peso, destino)


def _renomear(caminho: Path, familia: str, peso: int) -> bool:
    """Refaz os registros de nome de um TTF estático (ver `_descolidir`)."""
    try:
        from fontTools.ttLib import TTFont as FTFont

        fonte = FTFont(str(caminho))
        novo = f"{familia}-{peso}"
        for registro in fonte["name"].names:
            if registro.nameID in (1, 3, 4, 6):
                try:
                    registro.string = novo
                except Exception:
                    continue
        fonte.flavor = None
        temporario = caminho.with_name(caminho.stem + ".novo.ttf")
        fonte.save(str(temporario))
        temporario.replace(caminho)
        return True
    except Exception as erro:
        print(f"  aviso: não consegui renomear {caminho.name}: {erro}", file=sys.stderr)
        return False


def _descolidir(caminhos: dict, pesos: dict) -> None:
    """
    Garante que cada peso do cache tenha nome interno próprio.

    O ReportLab identifica a fonte embutida pelo nome interno do ARQUIVO: dois
    pesos com o mesmo nome viram uma fonte só no PDF, e o livro inteiro sai no
    mesmo peso — sem negrito nenhum, sem aviso. Foi o que aconteceu com o cache
    da Inter, gerado antes de o `_instanciar` renomear a instância variável
    ("Inter-Regular" nos três pesos).

    O cache antigo continua valendo: só os registros de nome são refeitos, os
    glifos são os mesmos. Depois da primeira correção a colisão não volta, então
    o aviso aparece uma vez só.
    """
    try:
        from fontTools.ttLib import TTFont as FTFont
    except ImportError:
        return

    nomes: dict[str, dict] = {}
    for papel, caminho in caminhos.items():
        try:
            nome = FTFont(str(caminho), lazy=True)["name"].getDebugName(6)
        except Exception:
            continue
        if nome:
            # papel repetido no MESMO arquivo não é colisão: identidade que
            # declara o mesmo peso para negrito e para título aponta os dois
            # papéis para o mesmo cache
            nomes.setdefault(nome, {}).setdefault(caminho, papel)

    for nome, arquivos in nomes.items():
        if len(arquivos) < 2:
            continue
        for caminho, papel in arquivos.items():
            peso = pesos.get(papel)
            if peso is None:
                continue
            if _renomear(caminho, nome.split("-")[0], peso):
                print(
                    f"  aviso: o cache de fontes tinha '{nome}' repetido entre pesos "
                    f"(o PDF sairia sem negrito); renomeei para {nome.split('-')[0]}-{peso}",
                    file=sys.stderr,
                )


def _cobertura(caminho: Path) -> set[str]:
    """Caracteres obrigatorios que faltam na fonte (vazio = cobertura completa)."""
    try:
        from fontTools.ttLib import TTFont as FTFont

        cmap = FTFont(str(caminho), lazy=True).getBestCmap()
        return {c for c in REQUERIDOS if ord(c) not in cmap}
    except Exception:
        return set()


def _caminhos(identidade: dict, papel: str) -> list[Path]:
    """Arquivos de fonte declarados pela identidade para um papel (relativos a ela)."""
    spec = (identidade.get("fontes") or {}).get(papel) or {}
    base = identidade["_base"]
    return [p if (p := Path(a)).is_absolute() else base / a for a in (spec.get("arquivos") or [])]


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-") or "fonte"


def _impressao(arquivos: list[Path]) -> str:
    """
    Impressão digital dos arquivos de fonte (nome, tamanho e data).

    Entra no nome do cache da identidade de projeto: ela é editável, e trocar a
    fonte dela não pode continuar servindo a convertida de antes — o cache antigo
    fica onde está, o novo nasce com outro nome.
    """
    import hashlib

    marcas = []
    for caminho in arquivos:
        try:
            estado = caminho.stat()
            marcas.append(f"{caminho.name}:{estado.st_size}:{int(estado.st_mtime)}")
        except OSError:
            marcas.append(caminho.name)
    return hashlib.sha1("|".join(marcas).encode("utf-8")).hexdigest()[:8]


def preparar_fontes(identidade: dict) -> dict:
    """
    Prepara (converte e cacheia) e registra as fontes da identidade.

    `display` e opcional: quando a identidade declara uma, ela e a face dos
    titulos (Michroma, na Sousa Lima); quando nao, o titulo usa o peso forte da
    propria fonte de texto.

    Importante: `registerFontFamily` nao e opcional. Um TTFont solto funciona em
    `setFont`, mas estoura em `Paragraph` com "<b>"/"<i>"
    ("Can't map determine family/bold/italic for ...").
    """
    nomes = {"regular": "Corpo", "bold": "CorpoNegrito", "forte": "Titulo"}
    spec = (identidade.get("fontes") or {}).get("texto") or {}
    pesos = spec.get("pesos") or {"regular": 400, "bold": 600, "forte": 700}
    prefixo = CACHES.get(spec.get("cache") or "") or _slug(identidade.get("nome", "fonte"))
    arquivos = _caminhos(identidade, "texto")
    if identidade.get("_projeto"):
        # identidade do projeto: o cache segue os arquivos, não o nome da identidade
        prefixo = f"{prefixo}-{_impressao(arquivos)}"

    caminhos = {}
    for papel, peso in pesos.items():
        cache = CACHE_DIR / f"{prefixo}-{peso}.ttf"
        if not cache.exists() and not _preparar(arquivos, peso, cache):
            caminhos = {}
            break
        caminhos[papel] = cache

    faltando = _cobertura(caminhos["regular"]) if caminhos else REQUERIDOS
    if not faltando:
        _descolidir(caminhos, pesos)      # pesos com nome repetido = sem negrito
    if faltando:
        motivo = (
            f"a fonte da identidade não tem {''.join(sorted(faltando))!r}"
            if caminhos
            else "fontes da identidade indisponíveis"
        )
        print(f"  aviso: {motivo}; usando as do sistema", file=sys.stderr)
        caminhos = {}
        for papel in nomes:
            candidatos = FONTES_SISTEMA.get(papel) or FONTES_SISTEMA["regular"]
            escolhido = next((c for c in candidatos if Path(c).exists()), None)
            if escolhido is None:
                raise SystemExit(f"nenhuma fonte disponível para o papel '{papel}'")
            caminhos[papel] = Path(escolhido)
        origem = "sistema"
    else:
        origem = "identidade"

    for papel, nome in nomes.items():
        pdfmetrics.registerFont(TTFont(nome, str(caminhos[papel])))

    # Italico: a identidade manda quando declara `fontes.italico` (a Plus Jakarta
    # tem italico de verdade); sem isso vale uma sans italica do sistema, porque
    # fontes de marca raramente trazem italico (a Inter da terras e a Montserrat
    # so tem eixo de peso).
    italico = None
    arquivos_italico = _caminhos(identidade, "italico")
    if arquivos_italico:
        marca_it = _impressao(arquivos_italico)
        cache_it = CACHE_DIR / f"{prefixo}-italic-{marca_it}.ttf"
        cache_it_forte = CACHE_DIR / f"{prefixo}-italic-700-{marca_it}.ttf"
        if not cache_it.exists():
            _preparar(arquivos_italico, 400, cache_it)
        if not cache_it_forte.exists():
            _preparar(arquivos_italico, 700, cache_it_forte)
        if cache_it.exists() and not _cobertura(cache_it):
            italico = cache_it
        elif cache_it.exists():
            print("  aviso: a fonte italica não cobre os acentos; usando a do sistema",
                  file=sys.stderr)
    if italico is None:
        italico = next((c for c in FONTES_SISTEMA["italic"] if Path(c).exists()), None)
        italico_forte = italico
    else:
        # negrito italico no peso 700; se a instância não saiu, o <b><i> cai no
        # italico regular em vez de derrubar a montagem
        italico_forte = cache_it_forte if cache_it_forte.exists() else italico
    if italico is not None:
        pdfmetrics.registerFont(TTFont("CorpoItalico", str(italico)))
        if Path(str(italico_forte)) != Path(str(italico)):
            pdfmetrics.registerFont(TTFont("CorpoItalicoForte", str(italico_forte)))
            italico_forte = "CorpoItalicoForte"
        else:
            italico_forte = "CorpoItalico"

    # Familia "Corpo": e o que faz <b> e <i> resolverem dentro do paragrafo.
    pdfmetrics.registerFontFamily(
        "Corpo",
        normal="Corpo",
        bold="CorpoNegrito",
        italic="CorpoItalico",
        boldItalic=italico_forte or "CorpoItalico",
    )

    # "italic" entra no mapa só agora: é o nome registrado, não um arquivo da
    # identidade — o laço de registro acima não deve tentar baixá-lo.
    nomes["italic"] = "CorpoItalico"

    # Monoespacada do código: a identidade manda, quando declara `fontes.mono`;
    # senão vale a do sistema. Sem família registrada, um `<b>` perdido dentro de
    # um bloco de código derrubaria a montagem.
    mono = None
    arquivos_mono = _caminhos(identidade, "mono")
    if arquivos_mono:
        cache_mono = CACHE_DIR / f"{prefixo}-mono.ttf"
        if not cache_mono.exists():
            _preparar(arquivos_mono, 400, cache_mono)
        if cache_mono.exists():
            mono = cache_mono
    if mono is None:
        escolhido = next((c for c in FONTES_SISTEMA["mono"] if Path(c).exists()), None)
        if escolhido:
            mono = Path(escolhido)
    if mono is not None:
        pdfmetrics.registerFont(TTFont("Mono", str(mono)))
        pdfmetrics.registerFontFamily(
            "Mono", normal="Mono", bold="Mono", italic="Mono", boldItalic="Mono",
        )
        nomes["mono"] = "Mono"
    else:
        print("  aviso: nenhuma fonte monoespacada disponível; "
              "o bloco de código sai na fonte de texto", file=sys.stderr)
        nomes["mono"] = nomes["regular"]

    display = None
    arquivos_display = _caminhos(identidade, "display")
    if arquivos_display:
        cache_display = CACHE_DIR / f"{prefixo}-display.ttf"
        if not cache_display.exists():
            _preparar(arquivos_display, 400, cache_display)
        if cache_display.exists() and not _cobertura(cache_display):
            pdfmetrics.registerFont(TTFont("TituloDisplay", str(cache_display)))
            # família declarada também aqui: um `<b>` perdido num título não pode
            # derrubar a montagem inteira
            pdfmetrics.registerFontFamily(
                "TituloDisplay",
                normal="TituloDisplay",
                bold="CorpoNegrito",
                italic="CorpoItalico",
                boldItalic="CorpoNegrito",
            )
            display = "TituloDisplay"
        elif cache_display.exists():
            print(
                "  aviso: a fonte de título não cobre os acentos; usando a de texto",
                file=sys.stderr,
            )

    return {"_nomes": nomes, "display": display, "_origem": origem, "_caminhos": caminhos}


# --------------------------------------------------------------------------- #
# Estilos
# --------------------------------------------------------------------------- #

class Prancha(Flowable):
    """
    Ilustração de página inteira, com a legenda, centralizada em bloco.

    A escala é decidida em `wrap`, único ponto em que o ReportLab diz quanto
    espaço resta. A prancha toma a altura disponível e centra o conjunto
    (imagem + legenda) nela: sem isso, uma ilustração baixa fica ancorada no
    topo e deixa meia página vazia embaixo.
    """

    def __init__(self, caminho, legenda="", estilo_legenda=None):
        Flowable.__init__(self)
        self.caminho = str(caminho)
        self.legenda = legenda or ""
        self.estilo = estilo_legenda
        self.largura = self.altura = 0
        self._paragrafo = None
        self.width = self.height = 0

    def wrap(self, disponivel_w, disponivel_h):
        from reportlab.lib.utils import ImageReader

        iw, ih = ImageReader(self.caminho).getSize()

        reserva = 0
        if self.legenda and self.estilo is not None:
            self._paragrafo = Paragraph(self.legenda, self.estilo)
            self._paragrafo.wrapOn(self.canv, disponivel_w, disponivel_h)
            reserva = self._paragrafo.height + 8

        # tamanho natural: limitado pela largura da mancha
        escala_ideal = disponivel_w / iw
        altura_ideal = ih * escala_ideal + reserva

        # Não cabendo de forma decente, devolve um bloco maior que o espaço: é
        # assim que o ReportLab é convencido a empurrar a prancha inteira para a
        # página seguinte, em vez de encolhê-la num rodapé.
        if disponivel_h < altura_ideal * 0.6:
            self.width, self.height = disponivel_w, disponivel_h + 1
            return (self.width, self.height)

        escala = min(escala_ideal, max(60.0, disponivel_h - reserva) / ih)
        self.largura, self.altura = iw * escala, ih * escala
        self.width, self.height = disponivel_w, disponivel_h
        return (self.width, self.height)

    def draw(self):
        from reportlab.lib.utils import ImageReader

        extra = (self._paragrafo.height + 8) if self._paragrafo else 0
        base = max(0.0, (self.height - (self.altura + extra)) / 2)

        self.canv.drawImage(
            ImageReader(self.caminho),
            (self.width - self.largura) / 2, base + extra,
            self.largura, self.altura, mask="auto",
        )
        if self._paragrafo:
            self._paragrafo.drawOn(self.canv, (self.width - self._paragrafo.width) / 2, base)


def numeros_em_super(frags) -> list[str]:
    """
    Números de nota que estão NESTES fragmentos já compostos.

    O `<super>` do marcador não sobrevive como atributo do texto: o parser guarda
    o trecho como um `ParaFrag` com `__tag__='super'` dentro do grupo da palavra, e
    o texto do fragmento é o próprio número. É por aqui que a metade certa de um
    parágrafo partido se reconhece.
    """
    achados: list[str] = []

    def visita(item):
        if isinstance(item, (list, tuple)):
            for sub in item:
                visita(sub)
            return
        if getattr(item, "__tag__", "") == "super":
            texto = (getattr(item, "text", "") or "").strip()
            if texto.isdigit():
                achados.append(texto)

    for frag in frags or []:
        visita(frag)
    return achados


class RegistroNotas:
    """
    Em que página caiu cada nota de pé de página.

    Quem carrega o marcador se registra no momento em que é desenhado: o
    ReportLab não diz em que página um flowable parou antes de desenhá-lo. O
    rodapé de cada página lê daqui. A chave é o NÚMERO da nota, e não o termo —
    assim a mesma nota nunca sai duas vezes, mesmo que o parágrafo se parta.
    """

    def __init__(self, verbetes: dict | None = None):
        self.verbetes = verbetes or {}          # número -> termo
        self.paginas: dict[int, list[str]] = {} # página -> números, na ordem
        self.reservas: dict[int, float] = {}    # página -> faixa reservada
        self.fins: dict[int, float] = {}        # página -> onde o texto acabou

    def limpar(self):
        self.paginas.clear()
        self.reservas.clear()
        self.fins.clear()

    def registrar(self, pagina: int, numeros: list[str]):
        for numero in numeros:
            if numero in self.verbetes and not self._registrada(numero):
                self.paginas.setdefault(pagina, []).append(numero)

    def _registrada(self, numero: str) -> bool:
        return any(numero in lista for lista in self.paginas.values())

    def anotar_reserva(self, pagina: int, reserva: float):
        """A altura só é conhecida depois de desenhar, e é o desenho que precisa
        dela: a reserva desta passada vira o recuo do texto da próxima."""
        self.reservas[pagina] = reserva

    def anotar_fim(self, pagina: int, y: float):
        """Onde o texto desta página parou (coordenada de baixo para cima)."""
        self.fins[pagina] = y

    def fim_do_texto(self, pagina: int) -> float | None:
        return self.fins.get(pagina)

    def da_pagina(self, pagina: int) -> list[tuple[str, dict]]:
        return [(n, self.verbetes[n]) for n in self.paginas.get(pagina, [])]


class ParagrafoComNotas(Paragraph):
    """
    Parágrafo que avisa o registro em que página foi desenhado.

    O número da nota já vem no texto, posto pela marcação do manuscrito
    (`<super>1</super>`); aqui só se descobre a página. Quando o parágrafo se
    parte entre duas páginas, quem registra é a metade que carrega o marcador: o
    vínculo que vale é o do marcador com a nota, e o marcador pode ficar na
    segunda metade — é o caso em que a nota sairia numa página e o número na
    seguinte, que é o defeito que este registro existe para evitar.

    O registro vem por atributo de CLASSE porque o ReportLab recria o parágrafo
    com `__class__(None, estilo, frags=…)` ao parti-lo: o construtor é chamado
    sem os nossos argumentos.
    """

    registro: "RegistroNotas | None" = None

    def __init__(self, texto, estilo, bulletText=None, frags=None,
                 caseSensitive=1, encoding="utf8"):
        Paragraph.__init__(
            self, texto, estilo, bulletText=bulletText, frags=frags,
            caseSensitive=caseSensitive, encoding=encoding,
        )
        self._numeros = numeros_no_texto(texto) if texto else []
        self._registro = None
        self._registrado = False

    def split(self, availWidth, availHeight):
        partes = Paragraph.split(self, availWidth, availHeight)
        for parte in partes:
            if isinstance(parte, ParagrafoComNotas):
                parte._numeros = numeros_em_super(parte.frags)
                parte._registro = self._registro
        return partes

    def draw(self):
        if self._numeros and not self._registrado:
            self._registrado = True
            registro = self._registro or type(self).registro
            if registro:
                registro.registrar(self.canv.getPageNumber(), self._numeros)
        Paragraph.draw(self)


def paragrafo(texto, estilo, **kwargs):
    """
    Um `Paragraph` — ou o que registra a nota de rodapé, quando o texto carrega
    marcador. TODA criação de parágrafo do miolo passa por aqui: item de lista,
    célula de tabela e caixa de destaque também recebem nota, e um `Paragraph`
    construído direto no meio do caminho deixaria o marcador sem nota nenhuma.
    """
    if "<super" in (texto or ""):
        return ParagrafoComNotas(texto, estilo, **kwargs)
    return Paragraph(texto, estilo, **kwargs)


def estilos(cor: dict, f: dict) -> dict:
    s = getSampleStyleSheet()
    nomes = f["_nomes"]
    face_titulo = f.get("display") or nomes["forte"]   # face de titulo da identidade

    s.add(ParagraphStyle(
        name="Kicker", fontName=face_titulo, fontSize=7.2, textColor=cor["acento_texto"],
        alignment=TA_LEFT, spaceAfter=6, leading=10))
    s.add(ParagraphStyle(
        name="TituloCapitulo", fontName=face_titulo, fontSize=16, textColor=cor["tinta"],
        alignment=TA_LEFT, spaceAfter=4, leading=21))
    s.add(ParagraphStyle(
        name="Corpo", fontName=nomes["regular"], fontSize=9.4, textColor=cor["tinta"],
        alignment=TA_JUSTIFY, spaceAfter=7.5, leading=14.2, firstLineIndent=11))
    # `keepWithNext`: subtítulo sozinho no pé da página é defeito clássico de
    # composição — o ReportLab empurra o subtítulo junto com o bloco seguinte.
    s.add(ParagraphStyle(
        name="SubTitulo", fontName=nomes["bold"], fontSize=10.5, textColor=cor["tinta"],
        alignment=TA_LEFT, spaceBefore=9, spaceAfter=5, leading=14, keepWithNext=1))
    s.add(ParagraphStyle(
        name="Item", fontName=nomes["regular"], fontSize=9.2, textColor=cor["tinta"],
        bulletFontName=nomes["regular"],
        alignment=TA_LEFT, leading=13.4, leftIndent=13, bulletIndent=2, spaceAfter=3))
    s.add(ParagraphStyle(
        name="ItemNumero", fontName=nomes["regular"], fontSize=9.2, textColor=cor["tinta"],
        bulletFontName=nomes["regular"],
        alignment=TA_LEFT, leading=13.4, leftIndent=17, bulletIndent=2, spaceAfter=3))
    s.add(ParagraphStyle(
        name="SubItem", fontName=nomes["regular"], fontSize=9, textColor=cor["tinta"],
        bulletFontName=nomes["regular"],
        alignment=TA_LEFT, leading=12.8, leftIndent=27, bulletIndent=15, spaceAfter=2))
    s.add(ParagraphStyle(
        name="SubItemNumero", fontName=nomes["regular"], fontSize=9, textColor=cor["tinta"],
        bulletFontName=nomes["regular"],
        alignment=TA_LEFT, leading=12.8, leftIndent=30, bulletIndent=15, spaceAfter=2))
    s.add(ParagraphStyle(
        name="FolioSumario", fontName=nomes["regular"], fontSize=9.6, textColor=cor["tinta_fraca"],
        alignment=TA_RIGHT, leading=14))
    s.add(ParagraphStyle(
        name="Destaque", fontName=nomes["regular"], fontSize=9.2, textColor=cor["tinta"],
        alignment=TA_JUSTIFY, leading=13.8, leftIndent=4, rightIndent=4))
    s.add(ParagraphStyle(
        name="RotuloDestaque", fontName=nomes["bold"], fontSize=7, textColor=cor["acento_texto"],
        spaceBefore=0, spaceAfter=2, leading=9))
    s.add(ParagraphStyle(
        name="TituloSumario", fontName=face_titulo, fontSize=15, textColor=cor["tinta"],
        alignment=TA_CENTER, spaceAfter=4, leading=20))
    s.add(ParagraphStyle(
        name="ItemSumario", fontName=nomes["regular"], fontSize=9.6, textColor=cor["tinta"],
        alignment=TA_LEFT, spaceAfter=9, leading=14))
    s.add(ParagraphStyle(
        name="Citacao", fontName=nomes["italic"], fontSize=10.5, textColor=cor["tinta_fraca"],
        alignment=TA_CENTER, spaceBefore=9, spaceAfter=9, leading=15))
    s.add(ParagraphStyle(
        name="CelulaTitulo", fontName=nomes["bold"], fontSize=7.4, textColor=white,
        alignment=TA_CENTER, leading=10))
    s.add(ParagraphStyle(
        name="Celula", fontName=nomes["regular"], fontSize=7.4, textColor=cor["tinta"],
        alignment=TA_LEFT, leading=10.2))
    s.add(ParagraphStyle(
        name="Legenda", fontName=nomes["italic"], fontSize=8, textColor=cor["tinta_fraca"],
        alignment=TA_CENTER, spaceBefore=7, leading=11.5))
    s.add(ParagraphStyle(
        name="NotaRodape", fontName=nomes["regular"], fontSize=6.8, textColor=cor["tinta_fraca"],
        alignment=TA_LEFT, leading=9, spaceAfter=0))
    # verbete do glossário: termo em negrito abrindo a linha e as continuações
    # recuadas (recuo pendente), que é o que deixa o termo saltar na leitura
    s.add(ParagraphStyle(
        name="Verbete", fontName=nomes["regular"], fontSize=9.2, textColor=cor["tinta"],
        alignment=TA_LEFT, leading=13.6, leftIndent=14, firstLineIndent=-14, spaceAfter=6))
    # bloco de código: monoespacada, alinhada à esquerda (justificar código
    # destruiria a coluna), com entrelinha curta para caber mais linhas na caixa
    s.add(ParagraphStyle(
        name="Codigo", fontName=nomes.get("mono") or nomes["regular"], fontSize=7.4,
        textColor=cor["tinta"], alignment=TA_LEFT, leading=10.4, spaceAfter=0))
    return s


def escapar_codigo(linha: str) -> str:
    """
    Uma linha de código em richtext do ReportLab: escapa o XML e protege o
    recuo, que o `Paragraph` comeria por tratar espaço como separador.

    Só o recuo e as sequências de dois ou mais espaços viram `&nbsp;` — trocar
    todo espaço por entidade deixaria a linha sem ponto de quebra.
    """
    linha = linha.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    linha = re.sub(r" {2,}", lambda m: "&nbsp;" * len(m.group(0)), linha)
    return linha if linha else "&nbsp;"


# --------------------------------------------------------------------------- #
# Capa
# --------------------------------------------------------------------------- #

def desenhar_leds(c, x_direita, y, cor_acento, quantos=4, lado=2.1 * mm, vao=3.4 * mm):
    """
    Os 4 LEDs da identidade aprovada (topo a direita), do mais forte ao mais fraco.
    """
    for i in range(quantos):
        x = x_direita - (quantos - i) * vao
        c.saveState()
        c.setFillColor(cor_acento)
        c.setFillAlpha(max(0.25, 1.0 - i * 0.22))
        c.roundRect(x, y, lado, lado, 0.5 * mm, fill=1, stroke=0)
        c.restoreState()


def _ativo(identidade: dict, chave: str) -> Path | None:
    """Caminho de um ativo da identidade (logo, fundo), se existir."""
    nome = (identidade.get("ativos") or {}).get(chave)
    if not nome:
        return None
    caminho = Path(nome)
    if not caminho.is_absolute():
        caminho = identidade["_base"] / caminho
    return caminho if caminho.exists() else None


def _imagem_cobrindo(c, caminho: Path | None, largura, altura, x=0, y=0):
    """Desenha a imagem cobrindo a area, cortada pelo centro e sem distorcer."""
    if not caminho:
        return
    from reportlab.lib.utils import ImageReader

    img = ImageReader(str(caminho))
    iw, ih = img.getSize()
    escala = max(largura / iw, altura / ih)
    w, h = iw * escala, ih * escala

    c.saveState()
    recorte = c.beginPath()
    recorte.rect(x, y, largura, altura)
    c.clipPath(recorte, stroke=0, fill=0)
    c.drawImage(img, x + (largura - w) / 2, y + (altura - h) / 2, w, h, mask="auto")
    c.restoreState()


def regra_gradiente(c, x0, y0, x1, y1, cor_a, cor_b, espessura=1.4):
    """
    Filete em gradiente (ciano -> magenta na Sousa Lima): o recurso de assinatura
    da identidade. O gradiente do ReportLab preenche a area recortada, entao o
    recorte e o que garante que ele fique na espessura de um filete.
    """
    largura, altura = abs(x1 - x0), max(espessura, abs(y1 - y0))
    esquerda, base = min(x0, x1), min(y0, y1)

    c.saveState()
    caminho = c.beginPath()
    caminho.rect(esquerda, base, largura, altura)
    c.clipPath(caminho, stroke=0, fill=0)
    try:
        c.linearGradient(x0, y0, x1, y1, [cor_a, cor_b])
    except Exception:
        c.setFillColor(cor_a)
        c.rect(esquerda, base, largura, altura, fill=1, stroke=0)
    c.restoreState()


class RegraGradiente(Flowable):
    """Filete em gradiente como flowable, para usar no meio do texto."""

    def __init__(self, largura, espessura, cor_a, cor_b, align="LEFT", space_after=0):
        Flowable.__init__(self)
        self.largura = largura
        self.espessura = espessura
        self.cor_a, self.cor_b = cor_a, cor_b
        self.align = align
        self.space_after = space_after
        self.width = largura
        self.height = espessura

    def wrap(self, disponivel_largura, disponivel_altura):
        self.width = min(self.largura, disponivel_largura)
        self._disponivel = disponivel_largura
        return (disponivel_largura, self.espessura)

    def draw(self):
        x = {
            "LEFT": 0,
            "CENTER": (self._disponivel - self.width) / 2,
            "RIGHT": self._disponivel - self.width,
        }[self.align]
        regra_gradiente(self.canv, x, 0, x + self.width, 0, self.cor_a, self.cor_b, self.espessura)


def texto_espacado(c, x, y, texto, fonte, tamanho, espaco=0.0, centrado_em=None):
    """
    Texto com espacamento de letra (o tracking das caixas altas da identidade).

    O Canvas do ReportLab nao tem `setCharSpace` nesta versao — quem tem e o
    objeto de texto. O espacamento entra tambem na conta da largura, senao o
    texto centralizado sai torto.

    Devolve a largura ocupada.
    """
    largura = c.stringWidth(texto, fonte, tamanho) + espaco * max(0, len(texto) - 1)

    objeto = c.beginText()
    objeto.setFont(fonte, tamanho)
    if espaco:
        objeto.setCharSpace(espaco)
    objeto.setTextOrigin(x - largura / 2 if centrado_em else x, y)
    objeto.textOut(texto)
    # O espaçamento de letra é estado de TEXTO no PDF (operador Tc): se não for
    # zerado, vaza para todo desenho seguinte — foi o que deixou o título fora do
    # eixo, porque `drawCentredString` centra só a largura dos avanços.
    objeto.setCharSpace(0)
    c.drawText(objeto)

    return largura


def make_cover(path, livro, cor, f, identidade):
    """Despacha a capa pelo estilo declarado na identidade."""
    if identidade.get("capa_estilo") == "logo-rede":
        make_cover_logo_rede(path, livro, cor, f, identidade)
    else:
        make_cover_terras(path, livro, cor, f)


def _desenhar_marca(c, identidade, cor, face_titulo, nomes, topo_y, estilo):
    """
    Marca no alto da capa. Quatro formas:

    - `lockup`: a imagem do conjunto (monograma + nome + apoio), como na peça;
    - `monograma-nome`: só o símbolo em imagem e o nome escrito na fonte de
      título — o nome fica vetorial e não amolece em nenhum zoom;
    - `nome`: **nenhuma imagem de logo**, só o nome e o apoio compostos em texto;
    - `sem-marca`: **nada**. Nem logo, nem nome, nem descritor. Sobram a
      tipografia, as cores e a estrutura (fundo, etiqueta, filetes). É o que
      "sem logo" quer dizer quando o pedido é esse — a referência à marca some
      inteira, inclusive a assinatura do rodapé.

    Devolve o y em que o bloco termina, para o resto da capa se posicionar.
    """
    from reportlab.lib.utils import ImageReader

    marca = identidade.get("marca") or {}
    nome = (marca.get("nome") or identidade.get("nome", "")).upper()
    apoio = (marca.get("apoio") or "").upper()

    if estilo == "sem-marca":
        return topo_y

    def desenhar_imagem(caminho, largura):
        img = ImageReader(str(caminho))
        iw, ih = img.getSize()
        altura = largura * ih / iw
        c.drawImage(img, (PAGE_W - largura) / 2, topo_y - altura, largura, altura, mask="auto")
        return altura

    if estilo == "nome":
        y = topo_y - 4 * mm
        if nome:
            c.setFillColor(cor["capa_titulo"])
            texto_espacado(c, PAGE_W / 2, y, nome, face_titulo, 18, espaco=4.2, centrado_em=PAGE_W / 2)
        if apoio:
            y -= 7.4 * mm
            c.setFillColor(cor["capa_apoio"])
            texto_espacado(c, PAGE_W / 2, y, apoio, nomes["regular"], 7, espaco=3.2, centrado_em=PAGE_W / 2)
        return y

    if estilo != "monograma-nome":
        logo = _ativo(identidade, "logo_claro")
        return topo_y - desenhar_imagem(logo, PAGE_W * 0.32) if logo else topo_y

    y = topo_y
    monograma = _ativo(identidade, "monograma_claro")
    if monograma:
        y -= desenhar_imagem(monograma, PAGE_W * 0.115)

    if nome:
        y -= 7 * mm
        c.setFillColor(cor["capa_titulo"])
        texto_espacado(c, PAGE_W / 2, y, nome, face_titulo, 15, espaco=3.2, centrado_em=PAGE_W / 2)

    if apoio:
        y -= 5.4 * mm
        c.setFillColor(cor["capa_apoio"])
        texto_espacado(c, PAGE_W / 2, y, apoio, nomes["regular"], 6.4, espaco=2.6, centrado_em=PAGE_W / 2)

    return y


def make_cover_logo_rede(path, livro, cor, f, identidade):
    """
    Capa da identidade escura: fundo de constelacao, logo no topo, titulo em caixa
    alta na face tecnica, filete em gradiente e assinatura no rodape.
    """
    nomes = f["_nomes"]
    face_titulo = f.get("display") or nomes["forte"]
    estilo_marca = (identidade.get("marca") or {}).get("estilo", "lockup")
    c = canvas.Canvas(str(path), pagesize=A5)
    c.setTitle(livro.get("title", ""))

    margem = 20 * mm

    c.setFillColor(cor["capa_fundo"])
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    _imagem_cobrindo(c, _ativo(identidade, "fundo"), PAGE_W, PAGE_H)

    # marca no topo (lockup em imagem, monograma + nome, só nome, ou nada)
    _desenhar_marca(
        c, identidade, cor, face_titulo, nomes, PAGE_H - margem, estilo_marca
    )

    # olho (kicker) entre dois filetes, com espacamento de letra
    y = PAGE_H * 0.61
    kicker = (livro.get("kicker") or "").upper()
    if kicker:
        c.setFillColor(cor["acento"])
        largura_texto = texto_espacado(
            c, PAGE_W / 2, y, kicker, face_titulo, 7.5, espaco=1.6, centrado_em=PAGE_W / 2
        )
        c.setStrokeColor(cor["acento"])
        c.setLineWidth(0.5)
        c.line(margem + 6 * mm, y + 2.4, PAGE_W / 2 - largura_texto / 2 - 6 * mm, y + 2.4)
        c.line(PAGE_W / 2 + largura_texto / 2 + 6 * mm, y + 2.4, PAGE_W - margem - 6 * mm, y + 2.4)

    # titulo, centrado, em caixa alta (a face tecnica pede caixa alta)
    linhas = livro.get("title_lines") or [livro.get("title", "")]
    tamanho = 22 if max(len(ln) for ln in linhas) <= 18 else 18
    c.setFillColor(cor["capa_titulo"])
    c.setFont(face_titulo, tamanho)
    y = PAGE_H * 0.52
    for linha in linhas:
        c.drawCentredString(PAGE_W / 2, y, linha.upper())
        y -= tamanho * 1.28

    # filete em gradiente sob o titulo
    y_regra = y + tamanho * 0.42
    regra_gradiente(
        c, PAGE_W / 2 - 46 * mm, y_regra, PAGE_W / 2 + 46 * mm, y_regra,
        cor["acento"], cor["acento_2"], espessura=1.6,
    )

    # subtitulo, espacado
    y -= 8 * mm
    c.setFillColor(cor["capa_titulo"])
    for linha in livro.get("subtitle_lines") or []:
        texto_espacado(c, PAGE_W / 2, y, linha.upper(), nomes["regular"], 9, espaco=1.4, centrado_em=PAGE_W / 2)
        y -= 5.6 * mm

    # rodapé: autor à esquerda e assinatura à direita — a assinatura da marca
    # some junto com ela em `sem-marca`; o filete fica, porque é estrutura.
    y_rodape = margem - 2 * mm
    regra_gradiente(
        c, margem, y_rodape + 6 * mm, PAGE_W - margem, y_rodape + 6 * mm,
        cor["acento"], cor["acento_2"], espessura=0.5,
    )
    if livro.get("author"):
        c.setFont(nomes["regular"], 8)
        c.setFillColor(cor["capa_apoio"])
        c.drawString(margem, y_rodape, livro["author"])

    tag = livro.get("cover_footer") or identidade.get("assinatura", "")
    if tag and estilo_marca != "sem-marca":
        c.setFont(nomes["regular"], 8)
        c.setFillColor(cor["capa_apoio"])
        c.drawRightString(PAGE_W - margem, y_rodape, tag)

    c.showPage()
    c.save()


def make_cover_terras(path, livro, cor, f):
    """Capa da identidade terras: titulo grande a esquerda, LEDs, filete ciano."""
    nomes = f["_nomes"]
    c = canvas.Canvas(str(path), pagesize=A5)
    c.setTitle(livro.get("title", ""))

    # Fundo: gradiente suave entre os dois pretos da marca. Um retangulo chapado
    # aqui vira uma emenda horizontal visivel atravessando o texto.
    try:
        c.linearGradient(0, PAGE_H, 0, 0, [cor["capa_fundo"], cor["capa_fundo_alt"]])
    except Exception:
        c.setFillColor(cor["capa_fundo"])
        c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    margem = 18 * mm

    desenhar_leds(c, PAGE_W - margem, PAGE_H - margem - 2 * mm, cor["acento"])

    # kicker, no alto a esquerda
    y = PAGE_H - margem - 6 * mm
    c.setFillColor(cor["acento"])
    c.setFont(nomes["bold"], 8)
    c.drawString(margem, y, livro.get("kicker", "").upper())

    # filete ciano abaixo do kicker (linguagem da identidade)
    c.setStrokeColor(cor["acento"])
    c.setLineWidth(1.1)
    c.line(margem, y - 4 * mm, margem + 26 * mm, y - 4 * mm)

    # titulo, grande, a esquerda
    linhas = livro.get("title_lines") or [livro.get("title", "")]
    tamanho = 30 if max(len(ln) for ln in linhas) <= 18 else 24
    c.setFillColor(cor["capa_titulo"])
    c.setFont(nomes["forte"], tamanho)
    y = PAGE_H * 0.56
    for linha in linhas:
        c.drawString(margem, y, linha)
        y -= tamanho * 1.16

    # subtitulo
    y -= 2 * mm
    c.setFont(nomes["regular"], 10.5)
    c.setFillColor(cor["capa_apoio"])
    for linha in livro.get("subtitle_lines") or []:
        c.drawString(margem, y, linha)
        y -= 5.4 * mm

    # rodape: autor a esquerda, tag a direita com filete acima
    if livro.get("author"):
        c.setFont(nomes["regular"], 9)
        c.setFillColor(cor["capa_titulo"])
        c.drawString(margem, margem + 2 * mm, livro["author"])

    tag = livro.get("cover_footer") or livro.get("assinatura", "")
    if tag:
        c.setFont(nomes["regular"], 8)
        c.setFillColor(cor["capa_apoio"])
        largura = c.stringWidth(tag, nomes["regular"], 8)
        c.drawRightString(PAGE_W - margem, margem + 2 * mm, tag)
        c.setStrokeColor(cor["acento"])
        c.setLineWidth(0.6)
        c.line(PAGE_W - margem - largura, margem + 6 * mm, PAGE_W - margem, margem + 6 * mm)

    c.showPage()
    c.save()


# --------------------------------------------------------------------------- #
# Miolo
# --------------------------------------------------------------------------- #

class CanvasNumerado(canvas.Canvas):
    """Fio-de-pe, folio, filetes e notas de pé de página em toda página do miolo."""

    header_left = ""
    header_right = ""
    cor = None
    notas: "RegistroNotas | None" = None      # notas de rodapé, por página
    estilo_nota = None
    fonte_forte = None                        # face do termo dentro da nota
    largura_notas = PAGE_W - 32 * mm

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._estados = []

    def showPage(self):
        self._estados.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._estados)
        for estado in self._estados:
            self.__dict__.update(estado)
            self.draw_decor(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decor(self, total):
        self.saveState()
        cor = self.cor
        self.setStrokeColor(cor["linha"])
        self.setLineWidth(0.4)
        self.line(16 * mm, PAGE_H - 12 * mm, PAGE_W - 16 * mm, PAGE_H - 12 * mm)
        self.setFont("Corpo", 6.6)
        self.setFillColor(cor["tinta_fraca"])
        self.drawString(16 * mm, PAGE_H - 10.4 * mm, self.header_left)
        self.drawRightString(PAGE_W - 16 * mm, PAGE_H - 10.4 * mm, self.header_right)

        # rodape: filete em gradiente (assinatura da identidade) e o folio
        regra_gradiente(
            self, 16 * mm, 13.6 * mm, PAGE_W - 16 * mm, 13.6 * mm,
            cor["acento"], cor["acento_2"], espessura=0.6,
        )
        self.setFillColor(cor["acento_texto"])
        self.setFont("CorpoNegrito", 8)
        self.drawCentredString(PAGE_W / 2, 8.4 * mm, str(self._pageNumber))
        self.restoreState()

        self.desenhar_notas()

    def desenhar_notas(self):
        """
        Notas de pé de página da página atual, acima do folio.

        A faixa já foi reservada na passada anterior do miolo (o texto daquela
        página parou mais acima por causa dela), então aqui é só desenhar: o
        filete curto de abertura e, abaixo dele, os verbetes.

        A nota nasce no pé da página. Se o texto daquela página acabou mais
        acima — capítulo que termina no meio —, a nota sobe e fica logo abaixo
        dele: nota boiando a meia página de distância do texto a que pertence lê
        como página quebrada. Em página cheia a conta dá exatamente a margem de
        baixo, que é a posição de sempre.
        """
        if not self.notas or self.estilo_nota is None:
            return

        da_pagina = self.notas.da_pagina(self._pageNumber)
        if not da_pagina:
            return

        self.saveState()
        paragrafos = [
            Paragraph(texto_verbete(termo, numero, forte=self.fonte_forte), self.estilo_nota)
            for numero, termo in da_pagina
        ]
        for paragrafo in paragrafos:
            paragrafo.wrapOn(self, self.largura_notas, PAGE_H)
        altura = sum(p.height for p in paragrafos) + ESPACO_NOTAS * (len(paragrafos) - 1)

        base = MARGEM_INFERIOR
        fim = self.notas.fim_do_texto(self._pageNumber)
        if fim is not None:
            base = max(base, fim - FOLGA_NOTAS - altura)

        topo = base + altura
        self.setStrokeColor(self.cor["linha"])
        self.setLineWidth(0.4)
        self.line(16 * mm, topo + 1.6 * mm, 16 * mm + 26 * mm, topo + 1.6 * mm)

        y = topo
        for paragrafo in paragrafos:
            y -= paragrafo.height
            paragrafo.drawOn(self, 16 * mm, y)
        self.restoreState()

        self.notas.anotar_reserva(self._pageNumber, altura + FOLGA_NOTAS)


class MioloDoc(SimpleDocTemplate):
    """
    Miolo com reserva de rodapé POR PÁGINA.

    Só a página que recebe nota de pé de página perde faixa de texto — reservar
    a faixa em todas deixaria o livro inteiro com um vazio no pé. Como a página
    de cada nota só é conhecida depois de desenhar, o `main` monta o miolo mais
    de uma vez: a passada anterior diz quanto reservar em cada página.

    O quadro é refeito a cada página a partir da margem e da altura do
    documento, então a mudança não se acumula de uma página para a outra.
    """

    reservas: dict[int, float] = {}
    registro: "RegistroNotas | None" = None

    def handle_pageBegin(self):
        SimpleDocTemplate.handle_pageBegin(self)
        reserva = self.reservas.get(self.page, 0)
        if not reserva:
            return
        quadro = self.frame
        quadro._y1 = self.bottomMargin + reserva
        quadro._height = self.height - reserva
        quadro._geom()
        quadro._reset()

    def handle_pageEnd(self):
        # Onde o texto parou nesta página: é o que deixa a nota de pé de página
        # colar no texto quando o capítulo termina no meio da página. O quadro é
        # um objeto só, reaproveitado a cada página — daí ler aqui, e não depois.
        if self.registro is not None:
            self.registro.anotar_fim(self.page, self.frame._y)
        SimpleDocTemplate.handle_pageEnd(self)


def make_interior(path, livro, cor, f, numeros=None, reservas=None, registro=None):
    """
    Monta o miolo. Com `numeros`, o sumário imprime o folio de cada capítulo —
    é a segunda passada, depois que a paginação da primeira já é conhecida.
    `reservas` é quanto cada página precisa reservar para as notas de rodapé, e
    `registro` é onde as notas se registram ao serem desenhadas.
    """
    st = estilos(cor, f)
    registro = registro or RegistroNotas()
    registro.limpar()
    MioloDoc.reservas = dict(reservas or {})
    MioloDoc.registro = registro

    def P(texto, estilo="Corpo", **kwargs):
        return paragrafo(texto, st[estilo], **kwargs)

    # O termo do verbete sai no peso FORTE da identidade: o `<b>` do ReportLab usa
    # o peso que a identidade chama de negrito (600 na terras), que em 9 pt não se
    # distingue do regular — e o termo é o que o leitor procura no glossário.
    forte = f["_nomes"]["forte"]

    story = [P("SUMÁRIO", "TituloSumario"),
             RegraGradiente(26 * mm, 1.6, cor["acento"], cor["acento_2"], align="CENTER"),
             Spacer(1, 12)]

    util = PAGE_W - 32 * mm
    for i, ch in enumerate(livro["chapters"]):
        folio = str(numeros[i]) if numeros and i < len(numeros) else ""
        linha = Table(
            [[P(f"<u>{ch['toc']}</u>", "ItemSumario"), P(folio, "FolioSumario")]],
            colWidths=[util - 12 * mm, 12 * mm],
        )
        linha.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(linha)

    story.append(PageBreak())

    for i, ch in enumerate(livro["chapters"]):
        # prancha pura (arquivo só com imagem): a página é da ilustração
        if not ch.get("sem_cabecalho"):
            cabeca = [P(ch.get("kicker", ""), "Kicker"), P(ch["title"], "TituloCapitulo")]
            story.append(KeepTogether(cabeca))
            story.append(RegraGradiente(PAGE_W - 32 * mm, 1.5, cor["acento"], cor["acento_2"]))
            story.append(Spacer(1, 9))

        for bloco in ch.get("blocks", []):
            tipo = bloco.get("type")
            if tipo == "p":
                story.append(P(bloco["text"], "Corpo"))
            elif tipo == "h":
                story.append(P(bloco["text"], "SubTitulo"))
            elif tipo in ("ul", "ol"):
                numerada = tipo == "ol"
                # NÃO usar `i` aqui: ele é o índice do capítulo, e sobrescrevê-lo
                # desliga a quebra de página entre capítulos (o `if` do fim do
                # laço passa a comparar o número do último item).
                grupo: list = []

                def fechar_grupo():
                    # mantém o item e os subitens dele na mesma página: subitem
                    # órfão no topo da página seguinte perde o vínculo com o pai
                    if grupo:
                        story.append(KeepTogether(list(grupo)))
                        grupo.clear()

                # A numeração conta SÓ os itens numerados de primeiro nível: um
                # subitem com marcador no meio da lista numerada não pode consumir
                # número (era o que fazia a lista reiniciar em "1.").
                contador_topo = 0
                contador_sub = 0

                for item in bloco.get("items", []):
                    # item pode ser string (manuscrito antigo) ou
                    # {"text", "nivel", "ordenado"}
                    if isinstance(item, dict):
                        texto_item = item.get("text", "")
                        nivel = item.get("nivel", 0)
                        ordenado = item.get("ordenado", numerada if nivel == 0 else False)
                    else:
                        texto_item, nivel, ordenado = item, 0, numerada
                    if not texto_item:
                        continue

                    if nivel == 0:
                        fechar_grupo()

                    if nivel > 0:
                        if ordenado:
                            contador_sub += 1
                            grupo.append(P(texto_item, "SubItemNumero",
                                           bulletText=f"{contador_sub}."))
                        else:
                            grupo.append(P(texto_item, "SubItem", bulletText="–"))
                    else:
                        if ordenado:
                            contador_topo += 1
                        grupo.append(P(
                            texto_item,
                            "ItemNumero" if ordenado else "Item",
                            bulletText=f"{contador_topo}." if ordenado else "•",
                        ))

                fechar_grupo()
            elif tipo == "quote":
                story.append(P(bloco["text"], "Citacao"))
            elif tipo == "destaque":
                caixa = Table(
                    [[P(bloco.get("label", "DESTAQUE"), "RotuloDestaque")],
                     [P(bloco["text"], "Destaque")]],
                    colWidths=[PAGE_W - 32 * mm],
                )
                caixa.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), cor["acento_fundo"]),
                    ("LINEBEFORE", (0, 0), (0, -1), 2, cor["acento"]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (0, 0), 7),
                    ("BOTTOMPADDING", (0, 0), (0, 0), 0),
                    ("TOPPADDING", (0, 1), (0, 1), 0),
                    ("BOTTOMPADDING", (0, 1), (0, 1), 8),
                ]))
                story.append(Spacer(1, 4))
                # KeepTogether: sem isto a tabela pode ser partida entre páginas,
                # deixando o rótulo sozinho no pé de uma e o texto na outra
                story.append(KeepTogether(caixa))
                story.append(Spacer(1, 9))
            elif tipo == "imagem":
                caminho_img = Path(bloco.get("caminho", ""))
                if caminho_img.exists():
                    story.append(Prancha(
                        caminho_img, legenda=bloco.get("legenda") or "", estilo_legenda=st["Legenda"],
                    ))
                else:
                    print(f"  aviso: imagem não encontrada: {caminho_img}", file=sys.stderr)
            elif tipo == "glossario":
                for item in bloco.get("itens", []):
                    story.append(P(texto_verbete(item, forte=forte), "Verbete"))
                story.append(Spacer(1, 4))
            elif tipo == "codigo":
                linhas_codigo = bloco.get("linhas") or []
                if linhas_codigo:
                    texto_codigo = "<br/>".join(escapar_codigo(ln) for ln in linhas_codigo)
                    caixa_codigo = Table(
                        [[Paragraph(texto_codigo, st["Codigo"])]],
                        colWidths=[PAGE_W - 32 * mm],
                    )
                    caixa_codigo.setStyle(TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), cor["papel_alt"]),
                        ("LINEBEFORE", (0, 0), (0, -1), 2, cor["linha"]),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                    ]))
                    story.append(Spacer(1, 4))
                    # bloco curto fica inteiro na página; se não couber, parte —
                    # o código pela metade ainda é legível, ao contrário da caixa
                    # de destaque, que perde o rótulo
                    story.append(KeepTogether(caixa_codigo)
                                 if len(linhas_codigo) <= 14 else caixa_codigo)
                    story.append(Spacer(1, 10))
            elif tipo == "table":
                cabecalhos = [P(h, "CelulaTitulo") for h in bloco["headers"]]
                linhas = [cabecalhos] + [
                    [P(celula, "Celula") for celula in linha] for linha in bloco["rows"]
                ]
                ncols = len(bloco["headers"])
                util = PAGE_W - 32 * mm
                tabela = Table(linhas, colWidths=[util / ncols] * ncols, repeatRows=1)
                comandos = [
                    ("BACKGROUND", (0, 0), (-1, 0), cor["tabela_fundo"]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.3, cor["linha"]),
                ]
                for r in range(1, len(linhas)):
                    if r % 2 == 0:
                        comandos.append(("BACKGROUND", (0, r), (-1, r), cor["papel_alt"]))
                tabela.setStyle(TableStyle(comandos))
                story.append(Spacer(1, 3))
                story.append(tabela)
                story.append(Spacer(1, 10))

        if i < len(livro["chapters"]) - 1:
            story.append(PageBreak())

    CanvasNumerado.header_left = livro.get("running_header", livro.get("title", "")).upper()
    CanvasNumerado.header_right = livro.get("running_header_right", "")
    CanvasNumerado.cor = cor
    CanvasNumerado.notas = registro
    CanvasNumerado.estilo_nota = st["NotaRodape"]
    CanvasNumerado.fonte_forte = forte
    ParagrafoComNotas.registro = registro

    doc = MioloDoc(
        str(path), pagesize=A5,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=17 * mm, bottomMargin=MARGEM_INFERIOR,
        title=livro.get("title", ""), author=livro.get("author", ""),
        subject=livro.get("kicker", ""),
    )
    doc.build(story, canvasmaker=CanvasNumerado)


# --------------------------------------------------------------------------- #
# Sumario clicavel (a parte que o merge com a capa costuma quebrar)
# --------------------------------------------------------------------------- #

def _achatado(texto: str) -> str:
    """Colapsa espaços e quebras: título comprido chega à página em duas linhas."""
    return re.sub(r"\s+", " ", texto).strip()


def paginas_de_inicio(interior, livro):
    """
    Descobre em que pagina do MIOLO cada capitulo comeca.

    O kicker ("CAPITULO 01") e unico por capitulo, entao serve de marcador
    confiavel. Se um kicker nao for encontrado, o erro e reportado em vez de
    adivinhar a pagina — palpite silencioso aqui gera link apontando errado.

    A busca tem duas travas contra o falso positivo de citar a etiqueta no meio
    de outro capitulo (o caso do "Glossario": a palavra costuma aparecer antes,
    na promessa do texto):
    1. o capitulo abre sempre no alto da pagina, entao o ALTO da pagina e
       consultado antes do corpo;
    2. a pagina encontrada vira o piso da busca do capitulo seguinte — os
       capitulos estao em ordem, e a pagina de inicio so pode crescer.
    """
    import pdfplumber

    paginas_texto = []
    with pdfplumber.open(str(interior)) as doc:
        for i, pg in enumerate(doc.pages):
            linhas = (pg.extract_text() or "").split("\n")
            paginas_texto.append((
                i + 1,
                _achatado(" ".join(linhas)),
                _achatado(" ".join(linhas[:4])),
            ))

    paginas = []
    cursor = 1                       # a pagina 1 e o sumario
    faltando = []

    for ch in livro["chapters"]:
        marca = _achatado(ch.get("kicker") or ch["title"])

        if ch.get("sem_cabecalho"):
            # Prancha não imprime cabeçalho, então não há título na página para
            # ancorar: a referência passa a ser a legenda da ilustração.
            legenda = next(
                (b.get("legenda") for b in ch.get("blocks", [])
                 if b.get("type") == "imagem" and b.get("legenda")),
                "",
            )
            marca = _achatado(legenda)[:60] or marca

        candidatos = [marca, marca[:40]] if len(marca) > 40 else [marca]
        achado = None

        for so_topo in (True, False):
            for numero, corpo, cabeca in paginas_texto:
                if numero <= cursor:
                    continue
                if any(c and c in (cabeca if so_topo else corpo) for c in candidatos):
                    achado = numero
                    break
            if achado:
                break

        if achado is None:
            faltando.append(marca)
        else:
            paginas.append(achado)
            cursor = achado

    if faltando:
        raise SystemExit(
            "nao achei a pagina de inicio de: " + ", ".join(faltando)
            + "\n(o kicker precisa aparecer no texto da pagina; confira se ele existe no capitulo)"
        )

    return paginas


def ligar_sumario(merged, livro, paginas_inicio, deslocamento=1):
    """
    Escreve as anotacoes de link do sumario e os marcadores do PDF.

    `deslocamento` = 1 porque a capa e a pagina 1 e o miolo comeca depois dela:
    a pagina N do miolo vira a pagina N+1 do PDF final.
    """
    import pdfplumber

    reader = PdfReader(str(merged))
    writer = PdfWriter()
    for pagina in reader.pages:
        writer.add_page(pagina)

    # O PdfWriter novo nao herda o /Info do documento lido: sem isto, titulo e
    # autor (gravados no merge) sumiriam ao reescrever o arquivo.
    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # limpa anotacoes que tenham vindo do miolo
    sumario_idx = 1
    if "/Annots" in writer.pages[sumario_idx]:
        del writer.pages[sumario_idx]["/Annots"]

    altura = float(writer.pages[sumario_idx].mediabox.height)

    with pdfplumber.open(str(merged)) as doc:
        palavras = doc.pages[sumario_idx].extract_words()

    # agrupa palavras em linhas (tolerancia de 2pt no topo)
    agrupado = {}
    for palavra in palavras:
        chave = round(palavra["top"] / 2) * 2
        agrupado.setdefault(chave, []).append(palavra)

    linhas = []
    for chave in sorted(agrupado):
        partes = sorted(agrupado[chave], key=lambda p: p["x0"])
        linhas.append({
            "texto": _achatado(" ".join(p["text"] for p in partes)),
            "partes": partes,
            "topo": min(p["top"] for p in partes),
            "base": max(p["bottom"] for p in partes),
        })

    writer.add_outline_item("Capa", page_number=0)
    writer.add_outline_item("Sumário", page_number=sumario_idx)

    rotulos = [ch["toc"] for ch in livro["chapters"]]

    # Cada entrada do sumário pode ocupar MAIS DE UMA LINHA, e o folio fica no
    # fim da PRIMEIRA linha — ou seja, no meio do rótulo. Por isso o número é
    # removido antes de comparar, e o retângulo do link cobre o bloco inteiro.
    inicios = []
    cursor = 0
    sem_link = []

    for indice, ch in enumerate(livro["chapters"]):
        alvo = _achatado(ch["toc"])
        encontrado = None

        for i in range(cursor, len(linhas)):
            texto = re.sub(r"\s+\d{1,4}$", "", linhas[i]["texto"]).strip()
            if not texto or (len(texto) < 8 and texto != alvo):
                continue
            if texto == alvo or alvo.startswith(texto) or texto.startswith(alvo):
                encontrado = i
                break

        if encontrado is None:
            sem_link.append(ch["toc"])
            continue

        inicios.append((indice, ch, encontrado))
        cursor = encontrado + 1

    for posicao, (indice, ch, inicio) in enumerate(inicios):
        limite = inicios[posicao + 1][2] - 1 if posicao + 1 < len(inicios) else len(linhas) - 1

        # O bloco da entrada termina onde começa a próxima — ou antes, se houver
        # um salto vertical grande (é o que separa o último item do rodapé).
        fim = inicio
        while fim < limite and linhas[fim + 1]["topo"] - linhas[fim]["base"] < 18:
            fim += 1

        partes = [p for linha in linhas[inicio : fim + 1] for p in linha["partes"]]
        destino = paginas_inicio[indice] - 1 + deslocamento

        writer.add_annotation(
            page_number=sumario_idx,
            annotation=Link(
                rect=(
                    min(p["x0"] for p in partes) - 2,
                    altura - max(p["bottom"] for p in partes) - 3,
                    max(p["x1"] for p in partes) + 8,
                    altura - min(p["top"] for p in partes) + 3,
                ),
                target_page_index=destino,
                fit=Fit.fit(),
            ),
        )
        writer.add_outline_item(ch.get("outline") or ch["toc"], page_number=destino)

    with open(merged, "wb") as arquivo:
        writer.write(arquivo)

    return len(inicios), sem_link


def merge(capa, interior, saida, livro):
    escritor = PdfWriter()
    for origem in (capa, interior):
        for pagina in PdfReader(str(origem)).pages:
            escritor.add_page(pagina)
    escritor.add_metadata({
        "/Title": livro.get("title", ""),
        "/Author": livro.get("author", ""),
        "/Creator": "terras-ebook",
        "/Subject": livro.get("kicker", ""),
    })
    with open(saida, "wb") as arquivo:
        escritor.write(arquivo)


# --------------------------------------------------------------------------- #
# Glossário
# --------------------------------------------------------------------------- #

def carregar_termos(livro: dict, arquivo: str | None) -> list[dict]:
    """
    Os termos do livro: o arquivo da linha de comando manda, senão vale o campo
    `glossario` do manuscrito (que é como o `montar_manuscrito.py` entrega).
    """
    if arquivo:
        return glossario.carregar(arquivo)
    return glossario.normalizar(livro.get("glossario") or [])


def marcar_capitulo(capitulo: dict, lista: glossario.Lista):
    """
    Põe o marcador da nota na primeira ocorrência de cada termo pendente.

    O termo vale uma vez no livro inteiro — repetir a nota a cada menção é
    ruído, e o verbete do fim já cobre quem chegar depois. Bloco de imagem fica
    de fora: a legenda é desenhada junto da prancha, e o marcador ali sairia sem
    nota nenhuma para acompanhar.
    """
    for bloco in capitulo.get("blocks", []):
        tipo = bloco.get("type")
        if tipo in ("p", "h", "quote", "destaque"):
            bloco["text"] = glossario.marcar_richtext(bloco.get("text", ""), lista)
        elif tipo in ("ul", "ol"):
            itens = bloco.get("items", [])
            for posicao, item in enumerate(itens):
                if isinstance(item, dict):
                    item["text"] = glossario.marcar_richtext(item.get("text", ""), lista)
                elif isinstance(item, str):
                    itens[posicao] = glossario.marcar_richtext(item, lista)
        elif tipo == "table":
            for linha in bloco.get("rows", []):
                for posicao, celula in enumerate(linha):
                    linha[posicao] = glossario.marcar_richtext(celula, lista)


def fechar_glossario(livro: dict, lista: glossario.Lista, titulo: str) -> str | None:
    """
    Põe o glossário no fim do livro e devolve o rótulo usado (ou None se não há
    verbete). Se o autor já escreveu um capítulo de glossário — com texto de
    abertura, por exemplo — os verbetes entram nele em vez de nascer um segundo.
    """
    bloco = glossario.bloco(lista)
    if not bloco["itens"]:
        return None

    existente = next((c for c in livro["chapters"] if glossario.e_glossario(c)), None)
    if existente is not None:
        existente.setdefault("blocks", []).append(bloco)
        return existente.get("title") or titulo

    novo = glossario.capitulo(lista, titulo)
    livro["chapters"].append(novo)
    return novo["title"]


# --------------------------------------------------------------------------- #

def _absolutizar_imagens(livro: dict, raiz: Path) -> None:
    """
    Resolve o caminho das pranchas contra a pasta do manuscrito.

    O `montar_manuscrito.py` grava o caminho como ele estava (`artigos/imagens/x.jpg`),
    relativo ao projeto. Sem resolver aqui, montar de outro diretório de trabalho
    não acha a imagem: a prancha some e o build para de propósito na hora de achar
    a página do capítulo (a legenda é a âncora). Custa uma passada e devolve a
    montagem de qualquer lugar.
    """
    for capitulo in livro.get("chapters", []):
        for bloco in capitulo.get("blocks", []):
            if bloco.get("type") != "imagem":
                continue
            caminho = Path(bloco.get("caminho") or "")
            if caminho.is_absolute() and caminho.exists():
                continue
            for candidato in (raiz / caminho, Path.cwd() / caminho):
                if candidato.exists():
                    bloco["caminho"] = str(candidato.resolve())
                    break


def main():
    parser = argparse.ArgumentParser(description="Monta o e-book em PDF A5 na identidade da marca.")
    parser.add_argument("manuscrito", help="JSON do manuscrito (ver references/manuscrito.md)")
    parser.add_argument("--saida", help="caminho do PDF final")
    parser.add_argument(
        "--identidade",
        help="identidade a usar: um caminho de JSON, ou os apelidos 'slc' "
             "(padrão da casa) e 'terras' (brand.json). Sem isto, vale a identidade "
             "do projeto (identidade/identidade.json, ao lado do manuscrito), "
             "copiada da base da casa na primeira vez.",
    )
    parser.add_argument(
        "--marca",
        choices=["", "lockup", "monograma-nome", "nome", "sem-marca", "sem-logo"],
        default="",
        help="forma da marca na capa: 'lockup' (imagem do conjunto), "
             "'monograma-nome' (símbolo + nome em texto), 'nome' (sem imagem de "
             "logo, só o nome) ou 'sem-marca'/'sem-logo' (nada: nem logo, nem "
             "nome, nem assinatura). Vazio usa o que a identidade declara.",
    )
    parser.add_argument("--brand-dir", default=os.getenv("TERRAS_BRAND_DIR", str(BRAND_DIR_PADRAO)))
    parser.add_argument("--tema", default=TEMA_PADRAO, help="tema do brand.json (padrão: pessoal)")
    parser.add_argument(
        "--glossario",
        help="arquivo de termos (JSON ou markdown com a tabela) — o mesmo formato "
             "do `termos.md` da pasta dos artigos. Sem isto, vale o campo "
             "`glossario` do manuscrito.",
    )
    parser.add_argument(
        "--sem-notas",
        action="store_true",
        help="glossário no fim do livro, sem nota no pé das páginas",
    )
    parser.add_argument("--manter-temp", action="store_true", help="não apaga os PDFs intermediários")
    args = parser.parse_args()

    livro = json.loads(Path(args.manuscrito).read_text(encoding="utf-8"))
    if not livro.get("chapters"):
        raise SystemExit("o manuscrito não tem capítulos")

    raiz_manuscrito = Path(args.manuscrito).expanduser().resolve().parent
    _absolutizar_imagens(livro, raiz_manuscrito)

    # Glossário: a lista vale para as notas de rodapé e para o capítulo de fecho,
    # e a marcação precisa vir antes do fecho, que só inclui termo usado no texto.
    termos = carregar_termos(livro, args.glossario)
    if args.sem_notas:
        for termo in termos:
            termo["rodape"] = False
    lista = glossario.Lista(termos)

    for capitulo in livro["chapters"]:
        if not glossario.e_glossario(capitulo):
            marcar_capitulo(capitulo, lista)

    titulo_glossario = fechar_glossario(
        livro, lista, livro.get("glossario_titulo") or glossario.TITULO_PADRAO
    )

    identidade = carregar_identidade(
        args.identidade, Path(args.brand_dir), args.tema, projeto=raiz_manuscrito,
    )
    if args.marca:
        # a linha de comando manda no que a identidade declara; `sem-logo` é o
        # jeito como o pedido costuma chegar ("sem logo" = sem marca nenhuma)
        escolhido = "sem-marca" if args.marca == "sem-logo" else args.marca
        identidade.setdefault("marca", {})["estilo"] = escolhido
    cor = paleta(identidade["cores"], identidade.get("capa_estilo", "terras"))
    fontes = preparar_fontes(identidade)
    titulo_fonte = fontes.get("display") or fontes["_nomes"]["forte"]
    print(
        f"identidade: {identidade['nome']} | capa: {identidade.get('capa_estilo')} | "
        f"base/acento: {identidade['cores'].get('base')}/{identidade['cores'].get('acento')} | "
        f"fontes: {fontes['_origem']} | títulos: {titulo_fonte}"
    )

    if not lista.itens:
        print("  aviso: nenhum termo declarado; o livro sai sem glossário "
              "(ver references/manuscrito.md)", file=sys.stderr)
    else:
        print(f"glossário: {len(lista.verbetes())} verbete(s) de {len(lista.itens)} termo(s)"
              + (f" | título: {titulo_glossario}" if titulo_glossario else " | nenhum uso no texto"))
        if lista.faltando():
            print("  aviso: termo declarado e não usado no texto ficou fora do glossário: "
                  + ", ".join(lista.faltando()), file=sys.stderr)
        if lista.longos():
            print("  aviso: definição longa demais para nota de pé de página "
                  "(o ideal são duas linhas): "
                  + ", ".join(t["termo"] for t in lista.longos()), file=sys.stderr)

    saida = Path(args.saida or livro.get("output") or "ebook.pdf").expanduser()
    saida.parent.mkdir(parents=True, exist_ok=True)

    temp = Path(tempfile.mkdtemp(prefix="terras-ebook-"))
    try:
        capa = temp / "capa.pdf"
        interior = temp / "miolo.pdf"
        registro = RegistroNotas(lista.notas())
        reservas: dict[int, float] = {}

        make_cover(capa, livro, cor, fontes, identidade)

        # O miolo é montado mais de uma vez porque duas coisas só se sabem
        # depois de desenhar: em que página cada capítulo cai (o sumário imprime
        # o folio) e quanto cada página precisa reservar para as notas de pé de
        # página. Cada passada parte do que a anterior mediu, e a última é a que
        # fica — o laço só sai quando as duas medidas não mudam mais.
        make_interior(interior, livro, cor, fontes, registro=registro, reservas=reservas)
        paginas = paginas_de_inicio(interior, livro)

        for _ in range(8):
            make_interior(interior, livro, cor, fontes, numeros=paginas,
                          registro=registro, reservas=reservas)
            novas = paginas_de_inicio(interior, livro)
            medido = dict(registro.reservas)
            # A conta que decide a última passada é a SEGURANÇA, não a igualdade:
            # basta a paginação parar e nenhuma página reservar menos do que a nota
            # que ela desenhou. Exigir `medido == reservas` não terminaria nunca,
            # porque a faixa de uma nota empurra o próprio parágrafo dela para a
            # página seguinte — e aí a reserva daquela página deixa de ser medida,
            # volta a não ser, e o laço fica batendo entre dois desenhos.
            seguro = all(
                medido.get(p, 0.0) <= reservas.get(p, 0.0) + 0.01 for p in medido
            )
            if novas == paginas and seguro:
                break
            # A reserva só cresce entre passadas: guardando o maior, o quadro
            # nunca fica menor que a nota desenhada e o laço é monótono.
            reservas = {
                p: max(reservas.get(p, 0.0), medido.get(p, 0.0))
                for p in set(reservas) | set(medido)
            }
            paginas = novas
        else:
            # Não estabilizou nem com a reserva monótona: reserva em todas as
            # páginas a faixa da maior nota. Fica folga onde não há nota, mas
            # folga é melhor que texto por cima.
            uniforme = max(reservas.values(), default=0)
            if uniforme:
                total_miolo = len(PdfReader(str(interior)).pages)
                reservas = {p: uniforme for p in range(1, total_miolo + 1)}
                make_interior(interior, livro, cor, fontes, numeros=paginas,
                              registro=registro, reservas=reservas)
                paginas = paginas_de_inicio(interior, livro)
            print(
                "  aviso: a paginação não estabilizou; confira o sumário impresso",
                file=sys.stderr,
            )

        merge(capa, interior, saida, livro)
        ligados, sem_link = ligar_sumario(saida, livro, paginas)

        total = len(PdfReader(str(saida)).pages)
        print(f"✓ {saida} | {total} páginas | {ligados} link(s) no sumário")
        print(f"  folio de cada capítulo: {paginas}")
        print(f"  (no PDF final, some 1 à capa; a capa não é numerada)")
        if registro.paginas:
            por_pagina = ", ".join(f"p.{p}" for p in sorted(registro.paginas))
            print(f"  notas de pé de página em {len(registro.paginas)} página(s): {por_pagina}")
        if sem_link:
            print(f"  ⚠ sem link no sumário: {sem_link}", file=sys.stderr)

        if args.manter_temp:
            print(f"  intermediários em {temp}")
    finally:
        if not args.manter_temp:
            shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    main()

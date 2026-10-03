"""
Glossário e notas de pé de página — a parte comum aos três montadores.

Todo e-book da casa sai com um glossário curto no fim, e os termos mais
específicos ganham nota no pé da página em que aparecem pela primeira vez. As
duas coisas nascem da MESMA lista: a definição é escrita uma vez só, e o
montador decide onde ela aparece.

Formato (`glossario` do manuscrito, ou a tabela de `termos.md`):

    | Termo | Definição | Rodapé | Também em |
    |---|---|---|---|
    | Breakeven | Ponto de equilíbrio: quando a receita cobre o custo total. | sim | ponto de equilíbrio |

- `Termo` é como o verbete sai impresso; `Também em` (opcional) traz as outras
  formas que o texto usa, separadas por `;` — é o que a busca procura, e a forma
  que aparecer primeiro é a que vira nota.
- `Rodapé` vazio ou `sim` dá nota no pé da página (no PDF) e link para o verbete
  (no EPUB). `não` deixa o termo só no glossário do fim.
- Definição de termo com rodapé precisa caber em duas linhas de nota: o que
  passar disso vira aviso na montagem, não nota apertada.

A primeira ocorrência é a única que vale. Repetir a nota a cada menção é ruído,
e o glossário do fim já cobre quem chegar depois — é o mesmo critério que um
livro impresso usa.

Nada aqui é específico de ReportLab ou de EPUB: são strings e listas, para os
dois montadores tomarem a mesma decisão de ONDE cada termo aparece.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

# Nome do arquivo que traz a tabela de termos para dentro da pasta dos artigos.
# Ele NÃO é um capítulo: quem lê a pasta (montar_manuscrito, export_epub) pula.
ARQUIVO = "termos.md"

# Marcador no corpo do texto (ReportLab entende `super`); o número sai menor e
# levantado, como em livro impresso. A nota usa uma marca menor que a do corpo:
# levantamento grande num texto de 6,8 pt encosta na linha de cima.
MARCA = '<super rise="3" size="5.6">{}</super>'
MARCA_NOTA = '<super rise="1.8" size="4.6">{}</super>'
NOTA = re.compile(r"<super[^>]*>(\d+)</super>")

# Limite a partir do qual a definição de um termo com rodapé vira aviso: nota de
# pé de página de três linhas come uma faixa da mancha que o desenho não previu.
LIMITE_NOTA = 190

TAG = re.compile(r"<[^>]+>")
# Trechos de markdown em que a busca do termo NÃO pode entrar: link e código já
# têm dono, e mexer neles quebra a sintaxe.
PROTEGIDO = re.compile(r"!?\[[^\]]*\]\([^)]*\)|`[^`]*`")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
TITULO_PADRAO = "Glossário"


def _sem_acento(texto: str) -> str:
    """Texto sem acentos, para ordenar e comparar colunas."""
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def chave_ordem(termo: str) -> str:
    """Chave alfabética: 'Ágil' ordena junto de 'Agil', não depois de 'Zebra'."""
    return _sem_acento(termo).lower().strip()


def escapar(texto: str) -> str:
    """& < > viram entidades: a definição entra em XML do ReportLab e em HTML."""
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _ligado(valor, padrao: bool = True) -> bool:
    """Coluna `Rodapé` escrita de qualquer jeito: vazio/sim/não/true/1."""
    if valor is None or valor == "":
        return padrao
    if isinstance(valor, bool):
        return valor
    return _sem_acento(str(valor)).strip().lower() not in (
        "nao", "não", "n", "0", "false", "no", "off", "-", "x",
    )


def _variantes(valor) -> list[str]:
    """Aceita lista ou texto com `;`/`|` separando as formas."""
    if not valor:
        return []
    if isinstance(valor, str):
        partes = re.split(r"[;|]", valor)
    else:
        partes = list(valor)
    return [p.strip() for p in partes if str(p).strip()]


def normalizar(itens) -> list[dict]:
    """
    Devolve sempre `{termo, definicao, variantes, rodape}`.

    Aceita o que aparecer: o JSON do manuscrito, uma tabela já lida, ou uma
    lista de strings `Termo — definição`. Termo repetido é ignorado (o segundo
    não tem como ganhar nota: a primeira ocorrência já foi tomada).
    """
    saida: list[dict] = []
    vistos: set[str] = set()

    for item in itens or []:
        if isinstance(item, str):
            bruto = item.strip()
            if not bruto:
                continue
            separador = "—" if "—" in bruto else ("–" if "–" in bruto else ":")
            termo, _, definicao = bruto.partition(separador)
            item = {"termo": termo, "definicao": definicao}

        termo = str(item.get("termo") or item.get("term") or "").strip()
        definicao = str(
            item.get("definicao") or item.get("definition") or item.get("def") or ""
        ).strip()
        if not termo:
            continue

        chave = chave_ordem(termo)
        if chave in vistos:
            continue
        vistos.add(chave)

        variantes = [termo] + _variantes(
            item.get("variantes") or item.get("tambem") or item.get("apelidos")
        )
        limpas: list[str] = []
        for variante in variantes:
            if variante and chave_ordem(variante) not in {chave_ordem(v) for v in limpas}:
                limpas.append(variante)

        saida.append({
            "termo": termo,
            "definicao": definicao,
            "variantes": limpas,
            "rodape": _ligado(item.get("rodape", item.get("footer"))),
        })

    return saida


# --------------------------------------------------------------------------- #
# Leitura
# --------------------------------------------------------------------------- #

PAPEIS = {
    "termo": ("termo", "terms", "term", "título", "titulo", "palavra"),
    "definicao": ("definição", "definicao", "definition", "significado", "o que é"),
    "rodape": ("rodapé", "rodape", "nota", "footer", "pé de página"),
    "variantes": ("também em", "tambem em", "também", "tambem", "variantes",
                  "apelidos", "aliases", "sinônimos", "sinonimos"),
}

LINHA_SOLTA = re.compile(
    r"^\s*(?:[-*+]\s+)?(?:\*\*)?(?P<termo>[^—–:|*]{2,60}?)(?:\*\*)?\s*(?:—|–|:)\s*(?P<definicao>.+?)\s*$"
)


def _papel(cabecalho: str) -> str | None:
    limpo = chave_ordem(cabecalho).strip()
    for papel, nomes in PAPEIS.items():
        if any(limpo == chave_ordem(n) for n in nomes):
            return papel
    return None


def da_tabela(texto: str) -> list[dict]:
    """
    Lê a tabela de termos.

    A ordem das colunas é a que o cabeçalho declarar (`Termo | Definição |
    Rodapé | Também em`), pelo nome, em qualquer posição; sem cabeçalho
    reconhecível, vale a ordem da tabela. Exigir uma ordem fixa seria uma
    armadilha boba para quem escreve.
    """
    linhas = [ln.strip() for ln in texto.replace("\r\n", "\n").split("\n")]
    linhas = [ln for ln in linhas if ln.startswith("|")]

    # tira a linha de separação (|---|---|)
    linhas = [ln for ln in linhas if not re.fullmatch(r"\|[\s:|-]+\|", ln)]

    def celulas(linha: str) -> list[str]:
        return [c.strip().strip("*").strip() for c in linha.strip().strip("|").split("|")]

    if not linhas:
        return []

    if all(_papel(c) is None for c in celulas(linhas[0])):
        ordem = ["termo", "definicao", "rodape", "variantes"]      # sem cabeçalho
    else:
        ordem = [_papel(c) for c in celulas(linhas[0])]
        linhas = linhas[1:]

    itens = []
    for linha in linhas:
        valores = celulas(linha)
        item: dict = {}
        for posicao, papel in enumerate(ordem):
            if papel and posicao < len(valores) and valores[posicao]:
                item[papel] = valores[posicao]
        if item.get("termo"):
            itens.append(item)
    return normalizar(itens)


def das_linhas(texto: str) -> list[dict]:
    """Formato solto: um termo por linha, `Termo — definição` ou `Termo: definição`."""
    itens = []
    for linha in texto.replace("\r\n", "\n").split("\n"):
        if not linha.strip() or linha.lstrip().startswith(("#", "|", ">")):
            continue
        achado = LINHA_SOLTA.match(linha)
        if achado:
            itens.append({
                "termo": achado.group("termo").strip(),
                "definicao": achado.group("definicao").strip(),
            })
    return normalizar(itens)


def de_markdown(texto: str) -> list[dict]:
    """Tabela se houver tabela; senão, uma linha por termo."""
    return da_tabela(texto) or das_linhas(texto)


def carregar(caminho: str | Path) -> list[dict]:
    """Lê a lista de termos de um `.json` ou de um markdown com a tabela."""
    caminho = Path(caminho).expanduser()
    if not caminho.exists():
        return []
    texto = caminho.read_text(encoding="utf-8")

    if caminho.suffix.lower() == ".json":
        dados = json.loads(texto)
        if isinstance(dados, dict):
            dados = dados.get("glossario") or dados.get("termos") or []
        return normalizar(dados)

    return de_markdown(texto)


def da_pasta(pasta: str | Path) -> list[dict]:
    """Termos da pasta dos artigos: o `termos.md`, se existir."""
    caminho = Path(pasta) / ARQUIVO
    return de_markdown(caminho.read_text(encoding="utf-8")) if caminho.exists() else []


# --------------------------------------------------------------------------- #
# Busca no texto
# --------------------------------------------------------------------------- #

def _regex(variantes: list[str]) -> re.Pattern | None:
    """Regex das variantes, da maior para a menor — 'receita recorrente mensal'
    não pode ser mordida por 'receita'."""
    ordenadas = sorted({v for v in variantes if v}, key=len, reverse=True)
    if not ordenadas:
        return None
    return re.compile(r"\b(" + "|".join(re.escape(v) for v in ordenadas) + r")\b", re.IGNORECASE)


def _pedacos(texto: str):
    """Pedaços de TEXTO do richtext (fora das tags), com o deslocamento original.
    Sem isto a busca acharia 'PJ' dentro de um `<b>` e o marcador cairia no meio
    de uma tag."""
    posicao = 0
    for achado in TAG.finditer(texto):
        if achado.start() > posicao:
            yield posicao, texto[posicao:achado.start()]
        posicao = achado.end()
    if posicao < len(texto):
        yield posicao, texto[posicao:]


def localizar(texto: str, variantes: list[str]) -> tuple[int, int] | None:
    """Primeira ocorrência de qualquer variante, fora das tags. (i, j) ou None."""
    padrao = _regex(variantes)
    if not padrao:
        return None
    for deslocamento, pedaco in _pedacos(texto):
        achado = padrao.search(pedaco)
        if achado:
            return (deslocamento + achado.start(), deslocamento + achado.end())
    return None


class Lista:
    """
    Os termos do livro e o estado de quais já apareceram no texto.

    É o objeto que os dois montadores consultam; a numeração da nota sai na
    ordem de leitura, e só o termo com `rodape` consome número.
    """

    def __init__(self, itens):
        self.itens = normalizar(itens)
        self.usados: dict[str, dict] = {}
        self._numeros: dict[str, str] = {}

    def pendentes(self) -> list[dict]:
        return [t for t in self.itens if t["termo"] not in self.usados]

    def marcar(self, termo: dict) -> str:
        """Fecha o termo e devolve o número da nota (vazio se não tem rodapé)."""
        self.usados[termo["termo"]] = termo
        if not termo.get("rodape"):
            return ""
        numero = str(len(self._numeros) + 1)
        self._numeros[termo["termo"]] = numero
        return numero

    def faltando(self) -> list[str]:
        return [t["termo"] for t in self.itens if t["termo"] not in self.usados]

    def verbetes(self) -> list[dict]:
        """Os termos usados, em ordem alfabética — é o glossário do fim."""
        return sorted(self.usados.values(), key=lambda t: chave_ordem(t["termo"]))

    def notas(self) -> dict[str, dict]:
        """Número da nota -> termo, para o registro do rodapé do PDF."""
        return {numero: self.usados[termo] for termo, numero in self._numeros.items()}

    def com_marca(self) -> list[dict]:
        """Termos usados que aparecem no ponto de uso: nota no PDF, link no EPUB.
        `Rodape: não` é o que fica só no glossário do fim, nos dois formatos."""
        return [t for t in self.usados.values() if t.get("rodape")]

    def longos(self, limite: int = LIMITE_NOTA) -> list[dict]:
        """Termos com rodapé cuja definição não cabe numa nota de duas linhas."""
        return [t for t in self.itens if t.get("rodape") and len(t["definicao"]) > limite]


# --------------------------------------------------------------------------- #
# Marcação
# --------------------------------------------------------------------------- #

def marcar_richtext(texto: str, lista: Lista) -> str:
    """
    Insere `<super>N</super>` depois da primeira ocorrência dos termos pendentes
    que aparecem NESTE texto.

    Marca os termos em ordem de leitura e insere de trás para frente, para os
    índices recolhidos continuarem válidos durante a troca.
    """
    achados = []
    for termo in lista.pendentes():
        posicao = localizar(texto, termo["variantes"])
        if posicao:
            achados.append((posicao[0], posicao[1], termo))
    if not achados:
        return texto

    achados.sort(key=lambda a: a[0])
    limpos, fim = [], -1
    for i, j, termo in achados:                     # dois termos no mesmo trecho
        if i >= fim:                                # ficariam um dentro do outro
            limpos.append((i, j, termo))
            fim = j

    numerados = [(j, lista.marcar(termo)) for _, j, termo in limpos]
    for j, numero in reversed(numerados):
        if numero:
            texto = texto[:j] + MARCA.format(numero) + texto[j:]
    return texto


def _mascarar(linha: str) -> str:
    """Troca link e código por preenchimento de MESMO tamanho: a busca não entra
    ali, e as posições continuam valendo para a linha original."""
    return PROTEGIDO.sub(lambda m: "\x00" * len(m.group(0)), linha)


def numeros_no_texto(texto: str) -> list[str]:
    """Números de nota que já vêm marcados no texto, na ordem em que aparecem."""
    return NOTA.findall(texto or "")


def marcar_markdown(texto: str, lista: Lista, destino: str) -> str:
    """
    Troca a primeira ocorrência do termo por um link para o verbete — é o que
    substitui a nota de pé de página no EPUB, onde não existe página fixa.

    O link sai em HTML, e não em `[termo](url)`: o EPUB precisa da classe
    `termo` para o link não virar azul sublinhado no meio da frase, e a sintaxe
    do markdown não carrega classe sem depender de extensão.

    Título de seção fica de fora: ali o termo já é o assunto, e o leitor de EPUB
    usa o título para navegar. Ênfase em volta é respeitada (`*termo*` vira
    `*<a …>termo</a>*`), porque só o trecho do termo é substituído.
    """
    linhas = []
    for linha in texto.split("\n"):
        if HEADING.match(linha) or not linha.strip():
            linhas.append(linha)
            continue

        mascara = _mascarar(linha)
        achados = []
        for termo in lista.pendentes():
            posicao = localizar(mascara, termo["variantes"])
            if posicao:
                achados.append((posicao[0], posicao[1], termo))

        achados.sort(key=lambda a: a[0])
        limpos, fim = [], -1
        for i, j, termo in achados:
            if i >= fim:
                limpos.append((i, j, termo))
                fim = j

        for i, j, termo in reversed(limpos):
            numero = lista.marcar(termo)
            if not numero:
                # `Rodapé: não`: o termo entra no glossário, mas não aparece no
                # ponto de uso — a mesma regra que governa a nota no PDF
                continue
            link = (
                f'<a class="termo" href="{destino}#{ancora(termo["termo"])}">'
                f'{escapar(linha[i:j])}</a>'
            )
            linha = linha[:i] + link + linha[j:]
        linhas.append(linha)

    return "\n".join(linhas)


# --------------------------------------------------------------------------- #
# Verbetes
# --------------------------------------------------------------------------- #

def texto_verbete(termo: dict, numero: str = "", forte: str | None = None) -> str:
    """
    Verbete em uma linha: `N Termo — definição` (richtext do ReportLab).

    `forte` é o nome da face de peso forte registrada no PDF. O `<b>` do
    ReportLab sai no peso que a identidade chama de negrito — 600 na terras — e
    600 em 9 pt não se distingue do regular. O termo é justamente o que o leitor
    procura no verbete (e na nota), então ele sai no peso forte.
    """
    marca = MARCA_NOTA.format(numero) + " " if numero else ""
    escrito = escapar(termo["termo"])
    destaque = f'<font name="{forte}">{escrito}</font>' if forte else f"<b>{escrito}</b>"
    return f'{marca}{destaque} — {escapar(termo["definicao"])}'


def ancora(termo: str) -> str:
    """Id do verbete no EPUB: `t-mrr`, `t-ponto-de-equilibrio`."""
    return "t-" + re.sub(r"[^a-z0-9]+", "-", _sem_acento(termo).lower()).strip("-")


def bloco(lista: Lista) -> dict:
    """Bloco `glossario` com os verbetes em ordem alfabética."""
    return {
        "type": "glossario",
        "itens": [t for t in lista.verbetes()],
    }


def capitulo(lista: Lista, titulo: str = TITULO_PADRAO) -> dict:
    """Capítulo de fecho do livro. Sem numeração e sem kicker: glossário é
    material de referência, não capítulo da sequência."""
    return {
        "id": "glossario",
        "toc": titulo,
        "outline": titulo,
        "kicker": "",
        "title": titulo,
        "sem_cabecalho": False,
        "blocks": [bloco(lista)],
    }


def html(lista: Lista, titulo: str = TITULO_PADRAO) -> str:
    """
    O glossário no EPUB: lista de definição, com âncora em cada verbete — é para
    cá que aponta o link do termo no texto.
    """
    linhas = [f'<h1 id="glossario">{escapar(titulo)}</h1>', '<dl class="glossario">']
    for termo in lista.verbetes():
        linhas.append(f'<dt id="{ancora(termo["termo"])}">{escapar(termo["termo"])}</dt>')
        linhas.append(f'<dd>{escapar(termo["definicao"])}</dd>')
    linhas.append("</dl>")
    return "\n".join(linhas)


def e_glossario(capitulo: dict) -> bool:
    """Este capítulo é o glossário? Aceita o gerado e o escrito à mão."""
    rotulo = _sem_acento(str(capitulo.get("title") or capitulo.get("toc") or ""))
    return bool(re.match(r"^\s*glossario\b", rotulo, re.IGNORECASE))


def json_para_manuscrito(itens: list[dict]) -> list[dict]:
    """A lista como ela vai para o manuscrito JSON (sem os campos derivados)."""
    return [
        {
            "termo": t["termo"],
            "definicao": t["definicao"],
            "variantes": t["variantes"][1:],
            "rodape": t["rodape"],
        }
        for t in itens
    ]

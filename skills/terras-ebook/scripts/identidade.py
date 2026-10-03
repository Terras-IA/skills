"""
Identidade: as cores puras (compartilhadas pelo montador de PDF e pelo de EPUB) e
a identidade **do projeto** — onde ela mora, e a cópia da base quando o diretório
ainda não tem uma.

Duas decisões que este módulo resolve:

1. **A identidade é do diretório, não da chamada.** Ela vive em
   `<projeto>/identidade/identidade.json`, ao lado do manuscrito. Montar de outra
   pasta, ou esquecer o `--identidade`, deixa de ser motivo para o livro sair na
   identidade errada — o projeto manda.
2. **Faltando, copia o padrão.** Diretório novo recebe uma cópia autocontida da
   identidade da casa (fontes e ativos juntos, caminhos relativos), que ele pode
   editar sem medo: a cópia é dele, a base na skill fica intacta.

As funções de cor não dependem de ReportLab, ebooklib nem de rede; as de cópia só
usam `shutil` e `json`.
"""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

# Nome da pasta e do arquivo dentro do projeto, e a identidade que serve de base.
PASTA = "identidade"
ARQUIVO = "identidade.json"
BASE = Path(__file__).resolve().parent.parent / "assets" / "sousa-lima"

# Apelidos aceitos no lugar de um caminho, no `--identidade` dos montadores.
CASA = {"slc", "sousa-lima", "sousa lima", "consultoria"}
TERRAS = {"terras", "pessoal", "brand"}


def base_padrao() -> Path:
    """A identidade base da casa (Sousa Lima), que vive dentro da skill."""
    return BASE / ARQUIVO


def apelido(argumento: str | None) -> str | None:
    """
    Reconhece o apelido digitado no lugar de um caminho.

    Devolve "casa" para a identidade da casa, "terras" para o `brand.json` do
    tema, e None quando é um caminho ou nada.
    """
    if not argumento:
        return None
    limpo = argumento.strip().lower()
    if limpo in CASA:
        return "casa"
    if limpo in TERRAS:
        return "terras"
    return None


def procurar(raiz: Path) -> Path | None:
    """Identidade do projeto: `identidade/identidade.json` ou `identidade.json`."""
    for candidato in (
        Path(raiz) / PASTA / ARQUIVO,
        Path(raiz) / ARQUIVO,
    ):
        if candidato.exists():
            return candidato
    return None


def raiz_do_projeto(pasta: Path) -> Path:
    """
    Onde fica a identidade do projeto.

    A pasta dos capítulos (`artigos/`, `capitulos-*/`) é subpasta: a identidade
    mora ao lado do manuscrito, não dentro dela. Se o pai não parecer a raiz do
    projeto, vale a própria pasta recebida.
    """
    pasta = Path(pasta)
    pai = pasta.parent
    if any(pai.glob("manuscrito*.json")) or any(pai.glob("*.epub")) or any(pai.glob("*.pdf")):
        return pai
    return pasta


def _copiar(origem: Path, destino: Path) -> bool:
    """Copia preservando o caminho relativo; devolve False se a origem não existe."""
    if not origem.exists():
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    return True


def copiar_base(raiz: Path, base: Path | None = None) -> Path:
    """
    Copia a identidade base para `<raiz>/identidade/`, **autocontida**.

    O JSON declara as fontes e os ativos em caminho relativo a ele mesmo, então a
    cópia reproduz a mesma estrutura e não precisa reescrever nada — o que viaja
    são os arquivos, não referências para dentro da skill. Chave que não aponta
    para arquivo (a `nota` dos ativos, que é texto) fica como está.

    Devolve o caminho do JSON novo.
    """
    origem = Path(base or base_padrao())
    if not origem.exists():
        raise FileNotFoundError(f"identidade base não encontrada: {origem}")

    dados = json.loads(origem.read_text(encoding="utf-8"))
    casa = origem.parent
    destino = Path(raiz) / PASTA
    destino.mkdir(parents=True, exist_ok=True)

    for papel, spec in (dados.get("fontes") or {}).items():
        for relativo in (spec or {}).get("arquivos") or []:
            _copiar(casa / relativo, destino / relativo)

    for chave, valor in (dados.get("ativos") or {}).items():
        if isinstance(valor, str) and (casa / valor).exists():
            _copiar(casa / valor, destino / valor)

    dados["_copiada_de"] = {"origem": str(origem), "em": date.today().isoformat()}
    novo = destino / ARQUIVO
    novo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    return novo


def do_projeto(raiz: Path, base: Path | None = None) -> tuple[Path | None, bool]:
    """
    A identidade do projeto, criando-a da base na primeira vez.

    Devolve (caminho, criada) — quem chama é que conta ao usuário o que houve, e
    decide o que fazer se a cópia não for possível (pasta sem permissão, por
    exemplo): aí vale a própria base, que é o que o padrão queria dizer.
    """
    achado = procurar(raiz)
    if achado:
        return achado, False
    try:
        return copiar_base(raiz, base), True
    except (OSError, ValueError, KeyError):
        return None, False


# Onde mora a marca terras (o `brand.json`), para quem quer esse estilo em vez da
# identidade da casa.
BRAND = Path.home() / "Documents" / "Diversos" / "terras-brand"


def marca_terras(tema: str = "pessoal", brand_dir: Path | None = None) -> dict | None:
    """
    A marca terras no formato de identidade: cores, fontes do tema e `capa_estilo`.

    É a mesma leitura para o PDF e para o EPUB — antes cada script lia o
    `brand.json` por conta própria, e o EPUB acabava num estilo genérico quando o
    pedido era a marca. Devolve None quando o arquivo não existe, e aí quem chama
    decide o que fazer (a montagem segue com a paleta padrão e avisa).
    """
    pasta = Path(brand_dir or BRAND)
    caminho = pasta / "brand.json"
    if not caminho.exists():
        return None

    dados = json.loads(caminho.read_text(encoding="utf-8"))
    escolhido = (dados.get("temas") or {}).get(tema) or {}
    cores = dict(dados.get("cores") or {})
    cores.update(escolhido.get("cores") or {})

    arquivos = (escolhido.get("fontes") or {}).get("principal", {}).get("arquivos") \
        or (dados.get("fontes") or {}).get("principal", {}).get("arquivos") \
        or ["fonts/inter-latin.woff2", "fonts/inter-latin-ext.woff2"]

    return {
        "nome": f"terras ({tema})",
        "cores": cores,
        "fontes": {
            "texto": {
                "arquivos": [str(pasta / Path(a).name) for a in arquivos],
                "pesos": {"regular": 400, "bold": 600, "forte": 700},
                "cache": "inter",
            },
        },
        "ativos": {},
        "capa_estilo": "terras",
        "_base": pasta,
    }


def contraste_com_branco(hexcor: str) -> float:
    """Razao de contraste WCAG da cor contra branco (1 a 21)."""
    r, g, b = (int(hexcor[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def linear(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    luminancia = 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b)
    return 1.05 / (luminancia + 0.05)


def escurecer_para_ler(hexcor: str, minimo: float = 4.5) -> str:
    """
    Escurece a cor ate ela ter contraste suficiente sobre papel branco.

    Vale para qualquer acento vivo: o ciano da terras (#07d4ec, ~2:1) e o da
    Sousa Lima (#00d2ff, ~1.9:1) sao otimos em fundo escuro e ilegiveis em papel.
    O acento continua sendo o acento; para TEXTO o miolo usa esta versao.
    """
    r, g, b = (int(hexcor[i : i + 2], 16) for i in (1, 3, 5))
    fator = 1.0

    while fator > 0.15:
        atual = f"#{int(r * fator):02x}{int(g * fator):02x}{int(b * fator):02x}"
        if contraste_com_branco(atual) >= minimo:
            return atual
        fator -= 0.05

    return "#111111"


def misturar_com_branco(hexcor: str, proporcao: float) -> str:
    """Tinta clara: cor misturada com branco (fundo de destaque, por exemplo)."""
    r, g, b = (int(hexcor[i : i + 2], 16) for i in (1, 3, 5))
    mistura = lambda c: int(round(c + (255 - c) * proporcao))  # noqa: E731
    return f"#{mistura(r):02x}{mistura(g):02x}{mistura(b):02x}"


def main() -> None:
    """Prepara a identidade do projeto sem montar o livro.

    Serve para editar cores e trocar logo ANTES da primeira montagem — e para
    deixar claro, desde o começo, que a identidade é deste diretório.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Prepara a identidade do projeto (copia a base da casa, se faltar)."
    )
    parser.add_argument("pasta", nargs="?", default=".", help="raiz do projeto (padrão: diretório atual)")
    parser.add_argument(
        "--refazer",
        action="store_true",
        help="sobrescreve a identidade do projeto com a base da casa (perde edições locais)",
    )
    args = parser.parse_args()

    raiz = Path(args.pasta).expanduser().resolve()
    if args.refazer:
        # a base evolui (logo novo, cor ajustada) e o projeto pode querer a versão
        # de agora — mas isto apaga edições locais, então só com o flag explícito
        antigo = procurar(raiz)
        caminho = copiar_base(raiz)
        if antigo:
            antigo.unlink(missing_ok=True)
        print(f"refiz: {caminho}")
        return

    caminho, criada = do_projeto(raiz)
    if caminho is None:
        raise SystemExit(f"não consegui preparar a identidade em {raiz}")
    print(f"{'criei' if criada else 'já existe'}: {caminho}")
    print("  edite cores, fontes e ativos neste arquivo — vale só para este diretório")


if __name__ == "__main__":
    main()

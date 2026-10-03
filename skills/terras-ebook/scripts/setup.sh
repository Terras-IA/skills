#!/usr/bin/env bash
# Cria/atualiza o venv da terras-ebook e instala as dependências do pipeline.
#
# O python do sistema é "externally managed" (PEP 668), então nada é instalado
# direto nele: tudo mora em ~/.config/terras-ebook/venv, como nas outras skills
# terras-*. O caminho pode ser trocado com TERRAS_EBOOK_VENV.
set -euo pipefail

VENV="${TERRAS_EBOOK_VENV:-$HOME/.config/terras-ebook/venv}"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "venv: $VENV"

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --quiet --upgrade pip
"$VENV/bin/python" -m pip install --quiet -r "$AQUI/requirements.txt"

echo
echo "Dependências instaladas. Exemplos:"
echo "  $VENV/bin/python $AQUI/get_videos.py --json /tmp/videos.json"
echo "  $VENV/bin/python $AQUI/export_epub.py --pasta ./artigos --titulo \"Meu e-book\""
echo "  $VENV/bin/python $AQUI/montar_manuscrito.py --pasta ./artigos --titulo \"Meu e-book\""
echo "  $VENV/bin/python $AQUI/build_ebook.py manuscrito.json --saida livro.pdf"
echo
echo "As fontes da marca (woff2) são convertidas para TTF na primeira montagem do PDF,"
echo "e ficam em cache em ~/.config/terras-ebook/fontes/."
echo
echo "Falta (instale à parte, só para publicar em plataforma):"
command -v epubcheck >/dev/null 2>&1 || echo "  - epubcheck (validação exigida por Apple Books/Kobo)"
command -v ebook-convert >/dev/null 2>&1 || echo "  - calibre, pelo ebook-convert (conversão e ajustes finos de EPUB)"

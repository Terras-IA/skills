#!/usr/bin/env bash
# Uso: render.sh <pasta-do-livro> [pagina.html ...]
# Sem páginas explícitas, renderiza todas as paginas/*.html para png/ e monta livro.pdf.
set -euo pipefail
LIVRO="${1:?uso: render.sh <pasta-do-livro> [página.html ...]}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHROME="$(command -v google-chrome || command -v chromium || command -v chromium-browser)"
[ -n "$CHROME" ] || { echo "Chrome não encontrado" >&2; exit 1; }
mkdir -p "$LIVRO/png"
PAGES=("${@:2}")
[ ${#PAGES[@]} -eq 0 ] && PAGES=("$LIVRO"/paginas/*.html)
for html in "${PAGES[@]}"; do
  nome="$(basename "$html" .html)"
  dir="$(cd "$(dirname "$html")" && pwd)"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-sandbox \
    --user-data-dir="$(mktemp -d)" \
    --window-size=1200,1800 --force-device-scale-factor=2 \
    --virtual-time-budget=4000 \
    --screenshot="$LIVRO/png/$nome.png" "file://$dir/$(basename "$html")" 2>/dev/null
  echo "✓ png/$nome.png"
done
python3 "$SKILL_DIR/scripts/montar-pdf.py" "$LIVRO"

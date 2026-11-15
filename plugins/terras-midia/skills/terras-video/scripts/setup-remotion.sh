#!/usr/bin/env bash
# Prepara o projeto Remotion que o bloco `remotion` do roteiro usa, sem sudo:
#   ~/.config/terras-video/remotion/   copia de templates/remotion + node_modules
# A fonte das composicoes continua na skill: rodar de novo atualiza src/ e so
# reinstala dependencia quando o package.json mudou. O Remotion baixa um Chrome
# headless proprio na primeira vez (browser ensure).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"
BASE="${TERRAS_VIDEO_HOME:-$HOME/.config/terras-video}"
DEST="$BASE/remotion"
mkdir -p "$DEST/src" "$DEST/public/fonts"

cp -f "$SKILL_DIR/templates/remotion/package.json" "$SKILL_DIR/templates/remotion/tsconfig.json" "$DEST/"
cp -f "$SKILL_DIR"/templates/remotion/src/* "$DEST/src/"

if [ ! -f "$DEST/node_modules/.instalado" ] || [ "$DEST/package.json" -nt "$DEST/node_modules/.instalado" ]; then
  echo "instalando dependencias do Remotion..."
  (cd "$DEST" && npm install --silent --no-audit --no-fund && touch node_modules/.instalado)
else
  echo "dependencias do Remotion ja instaladas"
fi

(cd "$DEST" && npx --no-install remotion browser ensure >/dev/null)
echo "pronto: $DEST"
echo "studio para criar ou ajustar composicao: (cd $DEST && npx remotion studio src/index.ts)"

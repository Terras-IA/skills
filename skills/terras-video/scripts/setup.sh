#!/usr/bin/env bash
# Instala as duas pecas que o build.py usa, sem sudo:
#   ~/.config/terras-video/ffmpeg    ffmpeg estatico (H.264, AAC, zoompan, loudnorm)
#   ~/.config/terras-video/venv/     venv com edge-tts (vozes neurais da Microsoft)
# Idempotente: rodar de novo so confere.
set -euo pipefail

BASE="${TERRAS_VIDEO_HOME:-$HOME/.config/terras-video}"
NPM_TMP="$BASE/npm-tmp"
mkdir -p "$BASE"

if [ ! -x "$BASE/ffmpeg" ]; then
  echo "instalando ffmpeg estatico via npm..."
  mkdir -p "$NPM_TMP"
  (cd "$NPM_TMP" && npm install --silent ffmpeg-static)
  cp "$NPM_TMP/node_modules/ffmpeg-static/ffmpeg" "$BASE/ffmpeg"
  chmod +x "$BASE/ffmpeg"
else
  echo "ffmpeg ja instalado"
fi

if [ ! -x "$BASE/venv/bin/edge-tts" ]; then
  echo "criando venv com edge-tts..."
  python3 -m venv "$BASE/venv"
  "$BASE/venv/bin/pip" install --quiet --upgrade pip
  "$BASE/venv/bin/pip" install --quiet edge-tts
else
  echo "edge-tts ja instalado"
fi

"$BASE/ffmpeg" -hide_banner -version | head -1
"$BASE/venv/bin/python" -c "import edge_tts; print('edge-tts ok')"
echo "pronto: $BASE"

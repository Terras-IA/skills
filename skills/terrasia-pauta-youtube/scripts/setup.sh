#!/usr/bin/env bash
# Idempotente, sem sudo: cria o venv com yt-dlp em $TERRAS_PAUTA_HOME.
set -euo pipefail

HOME_DIR="${TERRAS_PAUTA_HOME:-$HOME/.config/terrasia-pauta-youtube}"
mkdir -p "$HOME_DIR"

if [ ! -x "$HOME_DIR/venv/bin/yt-dlp" ]; then
    python3 -m venv "$HOME_DIR/venv"
    "$HOME_DIR/venv/bin/pip" install --quiet --upgrade yt-dlp
fi

echo "ok: $HOME_DIR/venv/bin/yt-dlp"

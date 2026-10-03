#!/usr/bin/env bash
# Prepara ~/.config/terras-agenda: venv com as dependências + config inicial.
# Não usa sudo. Roda quantas vezes quiser (é idempotente).
set -euo pipefail

DIR="$HOME/.config/terras-agenda"
SKILL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$DIR"

if [ ! -x "$DIR/venv/bin/python3" ]; then
  echo "→ criando venv em $DIR/venv"
  python3 -m venv "$DIR/venv"
fi

echo "→ instalando dependências (msal, icalendar, recurring-ical-events, requests)"
"$DIR/venv/bin/pip" install -q --upgrade pip
"$DIR/venv/bin/pip" install -q msal icalendar recurring-ical-events requests

if [ ! -f "$DIR/config.json" ]; then
  cp "$SKILL/config.example.json" "$DIR/config.json"
  echo "→ config criada a partir do exemplo: $DIR/config.json"
fi
chmod 600 "$DIR/config.json" 2>/dev/null || true

echo
echo "pronto. próximo passo:"
echo "  python3 $SKILL/scripts/terras_agenda.py check"

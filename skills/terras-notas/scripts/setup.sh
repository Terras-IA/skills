#!/usr/bin/env bash
# terras-notas — setup idempotente (sem sudo; apt indisponível nesta máquina).
# Cria ~/.config/terras-notas/ com venv (herdando pdfplumber/requests do sistema,
# que já estão instalados) e instala apenas o que falta: msal.

set -euo pipefail

CONFIG_DIR="${TERRAS_NOTAS_CONFIG_DIR:-$HOME/.config/terras-notas}"
VENV="$CONFIG_DIR/venv"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$CONFIG_DIR"
chmod 700 "$CONFIG_DIR"

if [ ! -x "$VENV/bin/python" ]; then
    echo "[setup] criando venv em $VENV (system-site-packages)"
    python3 -m venv --system-site-packages "$VENV"
fi

echo "[setup] instalando msal (pdfplumber e requests já existem no sistema)"
"$VENV/bin/pip" install --quiet --disable-pip-version-check msal

# config inicial a partir do example, sem sobrescrever a existente
if [ ! -f "$CONFIG_DIR/config.json" ] && [ -f "$SKILL_DIR/config.example.json" ]; then
    cp "$SKILL_DIR/config.example.json" "$CONFIG_DIR/config.json"
    chmod 600 "$CONFIG_DIR/config.json"
    echo "[setup] config criada em $CONFIG_DIR/config.json — edite o client_id depois do registro no Entra"
fi

# de-para inicial (idem, sem sobrescrever)
if [ ! -f "$CONFIG_DIR/depara.csv" ] && [ -f "$SKILL_DIR/depara.example.csv" ]; then
    cp "$SKILL_DIR/depara.example.csv" "$CONFIG_DIR/depara.csv"
    chmod 600 "$CONFIG_DIR/depara.csv"
    echo "[setup] de-para criado em $CONFIG_DIR/depara.csv"
fi

"$VENV/bin/python" "$SKILL_DIR/scripts/terras_notas.py" check
if [ ! -f "$SKILL_DIR/assets/assinatura.png" ]; then
    echo "[setup] sem assinatura em assets/assinatura.png — depois do login, rode:"
    echo "        terras_notas.py assinatura importar --assunto TRECHO_DO_ASSUNTO"
fi
echo "[setup] pronto."

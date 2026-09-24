#!/usr/bin/env bash
# Prepara a rota de upload no YouTube: bibliotecas no venv e conferencia da
# credencial. Idempotente.
#
#   bash ~/.zcode/skills/terras-video/scripts/setup-youtube.sh
set -euo pipefail

BASE="${TERRAS_VIDEO_HOME:-$HOME/.config/terras-video}"
VENV="$BASE/venv"
CLIENTE="$BASE/client_secret.json"

if [ ! -x "$VENV/bin/python" ]; then
  echo "venv ausente: rode antes o setup.sh desta skill"
  exit 1
fi

echo "instalando bibliotecas do Google no venv..."
"$VENV/bin/pip" install --quiet --upgrade google-api-python-client google-auth-oauthlib
"$VENV/bin/python" - <<'EOF'
import googleapiclient, google_auth_oauthlib
print("google-api-python-client e google-auth-oauthlib ok")
EOF

if [ -f "$CLIENTE" ]; then
  echo "credencial encontrada: $CLIENTE"
else
  cat <<TXT

FALTA A CREDENCIAL (passo que so voce pode fazer, uma vez):

  1. console.cloud.google.com -> criar projeto
  2. APIs e servicos -> Biblioteca -> ativar "YouTube Data API v3"
  3. Tela de consentimento OAuth -> tipo Externo.
     Se a conta for pessoal e o app ficar em "Testing", o refresh token expira
     em 7 dias (documentado pelo Google). Publicar o app em Producao resolve.
  4. Credenciais -> criar credencial -> ID do cliente OAuth -> "App para computador"
  5. baixar o JSON e salvar em: $CLIENTE

Depois: $VENV/bin/python ~/.zcode/skills/terras-video/scripts/upload_youtube.py autorizar
TXT
fi

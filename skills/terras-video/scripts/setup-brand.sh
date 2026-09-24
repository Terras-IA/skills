#!/usr/bin/env bash
# Cria/recria o diretorio padrao da identidade, sem sobrescrever nada editado.
# As copias semente vivem nas skills (seed/), e a copia viva e o diretorio padrao.
#
#   bash <pasta da skill terras-video>/scripts/setup-brand.sh
set -euo pipefail

BRAND="${TERRAS_BRAND_DIR:-$HOME/Documents/Diversos/terras-brand}"
# Skills vizinhas no mesmo repositório; TERRAS_SKILLS_DIR aponta outra raiz.
SKILL_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
SKILLS_DIR="${TERRAS_SKILLS_DIR:-$(dirname "$SKILL_DIR")}"
BANNER_SEED="$SKILLS_DIR/terras-banner/seed"
VIDEO_SEED="$SKILL_DIR/seed"

mkdir -p "$BRAND"/{fonts,templates,art,exports/cartelas,exports/banners,exports/thumbs}

seed() {  # seed <origem> <destino>
  if [ -e "$2" ]; then
    echo "ja existe, mantido: ${2#$BRAND/}"
  else
    cp "$1" "$2"
    echo "criado: ${2#$BRAND/}"
  fi
}

seed "$BANNER_SEED/banner.html"        "$BRAND/templates/banner.html"
seed "$VIDEO_SEED/card.html"           "$BRAND/templates/card.html"
seed "$VIDEO_SEED/card-vertical.html"  "$BRAND/templates/card-vertical.html"
seed "$VIDEO_SEED/card-canal.html"     "$BRAND/templates/card-canal.html"
seed "$VIDEO_SEED/card-canal-vertical.html" "$BRAND/templates/card-canal-vertical.html"
for f in "$BANNER_SEED"/fonts/*.woff2; do
  seed "$f" "$BRAND/fonts/$(basename "$f")"
done

if [ ! -e "$BRAND/brand.json" ]; then
  cat > "$BRAND/brand.json" <<'JSON'
{
  "versao": 1,
  "cores": { "base": "#05090f", "base_alt": "#0b1220", "acento": "#ffcc33" },
  "fontes": { "principal": { "nome": "Inter", "arquivos": ["fonts/inter-latin.woff2", "fonts/inter-latin-ext.woff2"] } },
  "audio_video": { "voz": "pt-BR-AntonioNeural", "ritmo": "-8%", "lufs_alvo": [-17, -14] }
}
JSON
  echo "criado: brand.json (minimo)"
else
  echo "ja existe, mantido: brand.json"
fi

echo "diretorio padrao: $BRAND"

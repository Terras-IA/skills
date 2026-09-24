#!/usr/bin/env bash
# Instala as skills deste repositório por link simbólico em cada pasta de
# skills de agente que existir na máquina. O repositório é a fonte única: a
# edição se faz aqui e vale para todos os agentes.
#
#   bash scripts/instalar.sh            # simulação: mostra o que faria
#   bash scripts/instalar.sh --aplicar  # executa
#
# O que já estiver no lugar de um link (pasta real, ou link para outro lugar)
# vai para ~/.terras-skills-backup/<data-hora>/<agente>/ antes. Pasta de agente
# que não existe não é criada: instalar não decide quais agentes você usa.
set -euo pipefail

APLICAR=0
[ "${1:-}" = "--aplicar" ] && APLICAR=1

REPO="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
SKILLS="$REPO/skills"
BACKUP="$HOME/.terras-skills-backup/$(date +%Y%m%d-%H%M%S)"

# agente|pasta de skills
# ~/.agents/skills fica de fora de propósito: é pasta de fallback lida por mais
# de um agente, e o mesmo nome lá e em ~/.zcode/skills fez o ZCode responder
# "Skill name is ambiguous".
ALVOS=(
  "claude|$HOME/.claude/skills"
  "zcode|$HOME/.zcode/skills"
  "opencode|$HOME/.config/opencode/skills"
  "codex|$HOME/.codex/skills"
)

alterados=0
faz() { if [ "$APLICAR" = 1 ]; then "$@"; fi; }

for alvo in "${ALVOS[@]}"; do
  agente="${alvo%%|*}"
  pasta="${alvo#*|}"
  [ -d "$pasta" ] || continue
  for skill in "$SKILLS"/terras-*/; do
    nome="$(basename "$skill")"
    origem="$SKILLS/$nome"
    destino="$pasta/$nome"
    # .nao-instalar: a skill existe aqui só para o catálogo do motor (a versão de
    # agente mora em outro lugar, ex. .claude/skills do terrasia). O link que
    # este instalador tenha criado antes sai; o resto no caminho fica intacto.
    if [ -f "$origem/.nao-instalar" ]; then
      if [ -L "$destino" ] && [ "$(readlink -f "$destino")" = "$(readlink -f "$origem")" ]; then
        echo "remove link  $destino (skill marcada .nao-instalar)"
        faz rm "$destino"
        alterados=$((alterados + 1))
      fi
      continue
    fi
    if [ -L "$destino" ] && [ "$(readlink -f "$destino")" = "$(readlink -f "$origem")" ]; then
      continue
    fi
    if [ -L "$destino" ]; then
      echo "troca link   $destino (apontava para $(readlink "$destino"))"
      faz mkdir -p "$BACKUP/$agente"
      faz sh -c 'readlink "$1" > "$2"' _ "$destino" "$BACKUP/$agente/$nome.link"
      faz rm "$destino"
    elif [ -e "$destino" ]; then
      echo "backup       $destino -> $BACKUP/$agente/$nome"
      faz mkdir -p "$BACKUP/$agente"
      faz mv "$destino" "$BACKUP/$agente/$nome"
    else
      echo "link novo    $destino"
    fi
    faz ln -s "$origem" "$destino"
    alterados=$((alterados + 1))
  done
done

if [ "$APLICAR" = 1 ]; then
  echo "$alterados alterado(s)."
  if [ -d "$BACKUP" ]; then echo "backup em $BACKUP"; fi
else
  echo "simulação: $alterados alteração(ões) pendente(s). Rode com --aplicar para executar."
fi

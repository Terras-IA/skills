#!/usr/bin/env bash
# auditar-fontes.sh — inventário dos portadores de convenção de um repositório.
# Imprime uma linha por categoria com os arquivos encontrados e a data do mais
# recente (arquivo velho é suspeito de mentir). Só fatos; julgamento é do agente.
# Uso: auditar-fontes.sh [caminho-do-repo]   (default: diretório atual)

set -u
repo="${1:-.}"
cd "$repo" 2>/dev/null || { echo "ERRO: caminho não encontrado: $repo" >&2; exit 1; }

[ -d .git ] || echo "AVISO: '${repo}' não é repo git; sinais de histórico indisponíveis" >&2

portador() { # portador <categoria> <caminho-ou-glob>...
  local categoria="$1"; shift
  local achados=() g f
  for g in "$@"; do
    for f in $g; do            # expansão de glob é intencional
      [ -e "$f" ] && achados+=("$f")
    done
  done
  if [ "${#achados[@]}" -eq 0 ]; then
    printf '%-22s | --\n' "$categoria"
    return
  fi
  local lista="" mais_nova="" data
  for f in "${achados[@]}"; do
    lista+="${lista:+, }$f"
    data=$(date -r "$f" +%Y-%m-%d 2>/dev/null || echo '?')
    if [ -z "$mais_nova" ] || [ "$data" \> "$mais_nova" ]; then mais_nova="$data"; fi
  done
  printf '%-22s | OK | %s | mais recente: %s\n' "$categoria" "$lista" "$mais_nova"
}

echo "== Instrução a agentes =="
portador "CLAUDE.md" "CLAUDE.md"
portador "AGENTS.md" "AGENTS.md"
portador "cursor/copilot" ".cursorrules" ".cursor/rules" ".github/copilot-instructions.md"
portador "skills do projeto" ".zcode/skills" ".claude/skills" ".agents/skills"

echo "== Documento de time =="
portador "contributing" "CONTRIBUTING.md"
portador "docs/" "docs" "doc"
portador "ADR" "docs/adr" "adr"

echo "== Formatação e lint =="
portador "editorconfig" ".editorconfig"
portador "prettier" ".prettierrc" ".prettierrc.json" ".prettierrc.yml" "prettier.config.js" "prettier.config.mjs" ".prettierignore"
portador "eslint" ".eslintrc" ".eslintrc.js" ".eslintrc.json" ".eslintrc.yml" "eslint.config.js" "eslint.config.mjs" "eslint.config.ts"
portador "biome" "biome.json" "biome.jsonc"
portador "python" "pyproject.toml" "ruff.toml" ".flake8" "setup.cfg"
portador "go" ".golangci.yml" ".golangci.yaml"
portador "ruby" ".rubocop.yml"

echo "== Build e tipos =="
portador "tsconfig" "tsconfig.json"
portador "package.json" "package.json"
portador "Makefile/justfile" "Makefile" "makefile" "justfile"

echo "== Commits e hooks =="
portador "commitlint" "commitlint.config.js" "commitlint.config.mjs" "commitlint.config.ts" ".commitlintrc" ".commitlintrc.json" ".commitlintrc.yml"
portador "husky" ".husky"
portador "pre-commit" ".pre-commit-config.yaml"

echo "== CI =="
portador "github workflows" ".github/workflows"
portador "gitlab-ci" ".gitlab-ci.yml"
portador "jenkins" "Jenkinsfile"
portador "circleci" ".circleci"

echo "== Container =="
portador "docker/compose" "Dockerfile" "Dockerfile.dev" "Dockerfile.prod" "docker-compose.yml" "docker-compose.yaml" "compose.yml" "compose.yaml"

if [ -d .git ] && command -v git >/dev/null 2>&1; then
  echo "== Sinais do git (de facto) =="
  total=$(git log --format=%s -200 2>/dev/null | wc -l | tr -d ' ')
  if [ "${total:-0}" -gt 0 ]; then
    conv=$(git log --format=%s -200 2>/dev/null | grep -cE '^(feat|fix|refactor|docs|chore|test|perf|build|ci|style|revert)(\([^)]+\))?: .+' || true)
    echo "commits amostrados: $total | no padrão conventional commits: $conv"
  fi
  echo "branches remotas (até 8):"
  git branch -r 2>/dev/null | head -8 | sed 's/^/  /'
fi

#!/usr/bin/env bash
# Roda o ZAP headless com um plano do Automation Framework.
# Uso: zap-run.sh <plano.yaml> [diretorio-home-do-zap]
# O ZAP 2.17 exige Java 17+; o java padrão da máquina pode ser o 11.
set -euo pipefail

plano="${1:?uso: zap-run.sh <plano.yaml> [zap-home]}"
zaphome="${2:-$(dirname "$(realpath "$plano")")/zap-home}"
ZAP_SH="${ZAP_SH:-/opt/zaproxy/zap.sh}"

if [[ -z "${JAVA_HOME:-}" ]] || ! "$JAVA_HOME/bin/java" -version 2>&1 | grep -qE 'version "(1[7-9]|[2-9][0-9])'; then
  for j in /usr/lib/jvm/java-{25,21,17}-openjdk-amd64; do
    [[ -x "$j/bin/java" ]] && { export JAVA_HOME="$j"; break; }
  done
fi
[[ -n "${JAVA_HOME:-}" ]] || { echo "Sem Java 17+ instalado. sudo apt install openjdk-21-jre-headless" >&2; exit 2; }

# -dir separado: não briga com o ZAP de interface aberto (lock em ~/.ZAP).
mkdir -p "$zaphome"
exec "$ZAP_SH" -cmd -dir "$zaphome" -autorun "$(realpath "$plano")" 2> >(grep -vE 'sun\.misc\.Unsafe|PlatformDependent|terminally deprecated|WARNING: Please consider' >&2)

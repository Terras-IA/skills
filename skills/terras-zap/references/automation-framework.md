# ZAP Automation Framework — notas de uso

## Jobs usados pelo `plano.py`

| Job | Para quê |
|---|---|
| `passiveScan-config` | limita alertas por regra (10) |
| `openapi` | importa spec (`apiUrl` ou `apiFile`) e semeia as URLs |
| `spider` | crawler HTML clássico |
| `spiderAjax` | crawler com navegador headless (SPA); usa Firefox do add-on webdriverlinux |
| `passiveScan-wait` | espera a passiva drenar a fila |
| `activeScan` | ataques ativos; `maxScanDurationInMins` limita o tempo |
| `report` | `traditional-json` (para o `resumo.py`) e `traditional-html` (para humano) |

Outros templates de relatório: `traditional-md`, `sarif-json` (GitHub code scanning), `risk-confidence-html`.

## Ajustar regra (silenciar falso positivo recorrente)

Adicione ao plano antes do spider:

```yaml
  - type: alertFilter
    alertFilters:
      - ruleId: 10096        # Timestamp Disclosure
        newRisk: False Positive
        url: "https://alvo/.*\\.js"
        urlRegex: true
```

## Área logada

Exige `users` e `authentication` no contexto. Caminho seguro: o usuário abre o ZAP com interface, faz login uma vez pelo navegador do ZAP, usa *Authentication Tester* (add-on authhelper) e exporta o plano (Automation → Save Plan). Não escreva senha em plano versionado; use variável de ambiente `${ZAP_SENHA}` no YAML e o usuário exporta no terminal dele.

## CI

```bash
docker run --rm -v "$PWD:/zap/wrk" ghcr.io/zaproxy/zaproxy:stable zap.sh -cmd -autorun /zap/wrk/plano.yaml
```
Use `reportDir: /zap/wrk` no plano. `failOnWarning: true` faz o job falhar com alerta.

## Daemon + API (interativo)

```bash
JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 zap.sh -daemon -port 8090 -config api.key=$(openssl rand -hex 16) -dir <scratch>/zap-home
curl "http://localhost:8090/JSON/core/view/alerts/?apikey=...&baseurl=https://alvo"
```
Útil para usar o ZAP como proxy (`--proxy-server=localhost:8090` no navegador de teste) e ver o tráfego de um fluxo manual. Encerre com `core/action/shutdown`.

## Códigos

riskcode 3 Alto, 2 Médio, 1 Baixo, 0 Info. confidence 4 confirmada, 3 alta, 2 média, 1 baixa, 0 falso positivo.

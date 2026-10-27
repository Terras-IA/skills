---
name: terras-zap
description: "Varre site ou API com o OWASP ZAP local em modo headless (baseline passivo; ativo só com autorização), gera relatório e faz a triagem dos alertas com correção. Use para scan ZAP, DAST, pentest web autorizado ou checar headers. Revisão de código: terras-security-review. DAST scan."
keywords: [zap, zaproxy, owasp, dast, pentest, varredura, scan, vulnerabilidade, headers, openapi]
---

# Terras — Varredura com OWASP ZAP

## Objetivo

Rodar o ZAP sem interface, por plano do Automation Framework, contra um alvo que o usuário pode testar, e devolver o que importa: alertas ordenados por risco, o que é falso positivo provável e a correção concreta no servidor ou no código.

## Onde está instalado

- ZAP 2.17 em `/opt/zaproxy` (`/usr/local/bin/zap.sh`).
- **Exige Java 17+.** O `java` padrão da máquina é o 11 e o ZAP sai com `requires a minimum of Java 17`. O `scripts/zap-run.sh` escolhe sozinho o `/usr/lib/jvm/java-25-openjdk-amd64`; não chame `zap.sh` direto.
- O wrapper usa `-dir` próprio por execução, então não trava se o ZAP de interface estiver aberto.

## Regra dura: só alvo autorizado, ativo só com "pode"

| Modo | O que faz | Quando |
|---|---|---|
| `baseline` (padrão) | spider + varredura passiva: só navega e lê respostas | site do usuário, ambiente local/staging dele, ou de cliente com contrato |
| `api` | importa OpenAPI + passiva | API com spec |
| `full` | baseline + **varredura ativa** (injeta SQLi, XSS, path traversal…) | só com autorização explícita |

- Antes de qualquer modo, confirme que o alvo é do usuário, de cliente com contrato, ou ambiente local/staging. Site de terceiro sem relação: não varra, nem em baseline.
- **Modo `full`**: pergunte e espere resposta com quem autorizou e o escopo. Registre em `--autorizacao` (vai para o plano). O script recusa sem isso.
- `full` em produção: avise que pode criar registros, mandar e-mail de formulário e disparar WAF/bloqueio de IP; prefira staging. Se for produção mesmo, peça janela e exclua rotas que escrevem (`--excluir`).
- "É do meu cliente" sem mais nada: pergunte se há contrato ou autorização escrita antes de varrer. Pedido de "agressivo/rápido" não pula essa pergunta.
- Senha colada no chat: não use, não grave em arquivo e sugira trocá-la.
- Nunca passe credencial do usuário no plano. Área logada fica para um plano manual com o usuário (ver `references/automation-framework.md`).

## Como trabalhar

1. **Confirmar alvo e modo** (regra acima). Pasta de saída no scratchpad, uma por execução.
2. **Gerar o plano:**
   ```bash
   python3 scripts/plano.py https://alvo/ --saida <scratchpad>/zap-<host> [--modo full --autorizacao "..."] [--excluir '.*/admin/delete.*'] [--ajax] [--openapi URL]
   ```
   `--ajax` para SPA (React/Vue) em que o spider comum acha pouca URL. Logout/sair já vem excluído.
3. **Rodar** em segundo plano quando passar de ~2 min (full, ajax):
   ```bash
   bash scripts/zap-run.sh <saida>/plano.yaml
   ```
   Termina com `Automation plan succeeded!`. Baseline em site pequeno leva ~20 s.
4. **Resumir:** `python3 scripts/resumo.py <saida>/zap.json --min-risco 1`.
5. **Triar** antes de relatar, em vez de colar a lista do ZAP:
   - confira 1 ou 2 alertas Médio/Alto com `curl -sI` ou na página (header ausente é fácil de provar);
   - marque falso positivo provável com motivo (ex.: "Private IP Disclosure" em página de documentação, CSP ausente em arquivo estático de CDN);
   - agrupe os de header num item só com a config pronta (nginx `add_header`, Apache, Cloudflare, Vercel `headers`) do servidor que o alvo usa (`Server:` ou `curl -sI`).
6. **Relatar:** contagem por risco, itens triados com correção, o que **não** foi coberto (área logada, rotas excluídas, ativo não rodado) e o caminho do `zap.html`.
7. **Artefato:** publique o relatório como artefato HTML (uma coluna: faixa de risco no topo, as correções com config pronta e botão de copiar, depois a tabela de todos os alertas com a decisão de cada um, e o que ficou fora). É a entrega padrão; o texto no chat resume e aponta o link.

## Referências

- `references/automation-framework.md` — jobs do plano, área logada, ajuste de regra, CI, API do daemon.

## Fonte

OWASP ZAP (Apache-2.0), Automation Framework do add-on `automation` 0.58. Docs: https://www.zaproxy.org/docs/automate/automation-framework/

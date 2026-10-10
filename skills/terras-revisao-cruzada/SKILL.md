---
name: terras-revisao-cruzada
version: 1.0.0
access: free
category: desenvolvimento
description: Manda uma spec ou um diff, em paralelo, para agentes de linha de comando de outros fornecedores (Codex, opencode) e junta os vereditos num revisao.md único, com concordâncias, divergências e a próxima ação. Pega o ponto cego que um modelo só não vê.
keywords: [revisao cruzada, segunda opiniao, codex, opencode, outro modelo, revisar diff, revisar spec, quorum, multi-modelo]
---

# Revisão cruzada entre modelos

## Objetivo

Um modelo revisando o próprio trabalho tende a não ver o mesmo erro duas vezes. Esta skill despacha a mesma revisão para agentes de **outros fornecedores**, roda em paralelo e sintetiza as respostas num `revisao.md` com veredito único.

Serve para dois alvos:

- **spec**: com o roteiro do modo crítica da `terras-critica-de-spec`;
- **diff**: com o roteiro da `terras-revisao-de-codigo`.

A skill é o despachante: os agentes precisam estar instalados e autenticados na máquina.

## Onde está instalada

Fonte única: `skills/terras-revisao-cruzada/` no repositório `terrasia-skills`. Adaptada do speccraft (MIT, ver `NOTICE`).

## Os revisores

| Agente | Ponto forte | Como chamar (somente leitura) |
|---|---|---|
| `codex` | revisão de código, enumerar casos de teste, refatoração | `codex exec -s read-only -C <repo> -o <saida.md> - < <prompt.md>` |
| `opencode` | análise, arquitetura, "esse desenho está certo?" | `opencode run --dir <repo> -f <prompt.md> "Siga as instruções do arquivo anexo."` |
| outra sessão do agente atual (ex.: `claude -p`) | uso geral; **mesmo fornecedor**, conta como opinião extra, não como cruzada | `claude -p "$(cat <prompt.md>)"` |

Antes de despachar, confira com `command -v codex opencode` quais existem. Agente ausente vira uma linha em limitações, não um erro. **Nunca** use modo que dá escrita ou dispensa o sandbox (`--full-auto`, `workspace-write`, `--dangerously-*`): revisão é somente leitura.

| Tarefa | Melhor agente |
|---|---|
| Revisar spec por ambiguidade | opencode |
| Revisar diff por bug e caso de teste | codex |
| Análise de arquitetura | opencode |
| Quórum | codex + opencode |

## Passo a passo

1. **Monte o prompt único** num arquivo temporário (fora do repositório): o roteiro de revisão, o alvo (a spec inteira, ou `git diff <base>...HEAD`), as regras do repositório (`CLAUDE.md`, `AGENTS.md`, ADRs relevantes) e o formato de resposta abaixo. Todos os revisores recebem o **mesmo** prompt.
2. **Confira o que vai sair da máquina.** O prompt vai para um serviço externo: remova `.env`, token, chave e dado pessoal real. Se o diff tocar arquivo de segredo, pare e pergunte.
3. **Despache em paralelo**, cada um em segundo plano, com tempo limite (por exemplo `timeout 600`), salvando a saída em arquivo separado por agente.
4. **Espere todos** e leia cada saída inteira.
5. **Sintetize** (regras abaixo) e grave `revisao.md` junto da spec ou na raiz do trabalho.
6. **Devolva** o veredito geral e a próxima ação concreta.

## Formato de resposta pedido a cada revisor

```yaml
veredito: aprovar | aprovar-com-comentarios | pedir-mudancas | rejeitar
preocupacoes:
  - "<preocupação, com arquivo:linha quando for diff>"
sugestoes:
  - "<sugestão>"
violacoes_de_regra:
  - regra: "<regra>"
    onde: "<local>"
```

## Regras da síntese

1. **Agrupe** preocupações e sugestões parecidas. Quando dois revisores apontam a mesma coisa, o sinal é mais forte: diga isso. Quando discordam, mostre a divergência explicitamente, sem escolher um lado em silêncio.
2. **Violação de regra aparece no topo**, venha de quem vier, independentemente do quórum.
3. **Confira antes de repassar.** Cada achado de diff com `arquivo:linha` é aberto e verificado. Achado que não se sustenta vai para uma seção "descartados", com o motivo.
4. **Veredito geral:**
   - algum revisor disse `rejeitar` → `rejeitar`;
   - senão, se o quórum (padrão: 1) disse `aprovar` ou `aprovar-com-comentarios` → `aprovar-com-comentarios`;
   - senão → `pedir-mudancas`.

## Formato do `revisao.md`

```markdown
---
alvo: "<spec ou faixa do diff>"
revisores: [codex, opencode]
quorum: 1
veredito: <veredito geral>
gerado: <data e hora ISO 8601>
---

# Revisão cruzada — <alvo>

## codex
**Veredito:** <veredito>
Preocupações: <lista>
Sugestões: <lista>

## opencode
...

## Síntese
<os achados principais, onde concordam, onde divergem>

## Descartados
<achado — por que não se sustenta>

**Ação:** <próximo passo concreto para o autor>

## Limitações
<revisor ausente, tempo esgotado, contexto cortado>
```

## Fora de escopo

- Corrigir o código ou a spec: a revisão aponta, o autor decide.
- Instalar ou autenticar os agentes por conta própria.

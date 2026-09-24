---
name: terras-drift
description: Audita drift entre contratos/specs vivas do terrasia e o código real, distinguindo da documentação histórica do assistente-os. Por evidência (grep/read). Spec aprovada não entregue = PLANNED, não FAIL. Use em "tem drift?", "docs desatualizados", entrega de módulo.
keywords: [drift, spec vs código, docs desatualizados, conformidade docs, spec]
---

---

# Drift Gate — spec ↔ código (terrasia)

Audita o que hoje é manual. Não há um script de drift neste repositório; use
leitura/grep e reporte evidências. Um script futuro pode automatizar somente
assertions estáveis e então deve ser adicionado a `scripts/verify-all.sh`.

Os documentos se dividem em duas classes: contratos vivos do Terrasia, que
devem corresponder à implementação atual, e referências históricas do
`assistente-os`, que descrevem o sistema antigo e não devem ser marcadas como
falhas só porque o Terrasia ainda não implementou a capacidade.

## Gatilhos

- Entrega de módulo novo (router/tiers, security, souls+governança, memory, daemon, integrations)
- PR que altera fronteiras entre pacotes (kernel/daemon/client), schema de DB, contrato da API
- Mudança na ordem de construção ou lista reescrever-vs-reaproveitar
- Usuário pergunta "tem drift?" ou "docs tão atualizados?"

## O que checar (fontes de verdade)

| Doc | O que validar contra código |
|-----|----------------------------|
| `README.md`, `requests.http`, `packages/client/` | Contrato público atual, SDK e exemplos executáveis |
| `docs/superpowers/specs/`, ADRs e planos aceitos | Somente decisões **marcadas como entregues** são exigíveis do código; specs aprovadas para implementação mas ainda não entregues classificam como **PLANNED**, não FAIL |
| `docs/CONHECIMENTO-DO-MONOLITO.md`, `docs/subsistemas/` | Referência histórica e decisões de reconstrução; checar se links/listas de reuso continuam corretos, não se a feature já existe |
| `docs/referencia-verbatim/` | Cópia literal do original; só comparar com a fonte original quando a cópia for atualizada deliberadamente |

## Metodologia

1. **Classificar a fonte** como contrato vivo, plano/ADR (PLANNED vs entregue) ou referência histórica.
2. **Extrair afirmações verificáveis** apenas de contratos vivos e decisões já implementadas; itens de specs/planos não entregues → PLANNED.
3. **Consultar código real** via grep/glob/read (não assumir — abrir arquivos).
4. **Comparar**: cada afirmação → PASS/FAIL/UNVERIFIABLE; trabalho futuro documentado → PLANNED.
5. **Reportar**: resumo, escopo auditado e drifts com arquivo:linha e evidência.

## Saída esperada

```
## Drift Report — YYYY-MM-DD

### Contrato público atual
✅ PASS: `README.md` documenta `POST /souls/:soul/threads` e o daemon/SDK expõem o mesmo payload
❌ FAIL: o evento SSE `done` ganhou `sources`, mas `@terrasia/client` não tipa o campo
⚠️ UNVERIFIABLE: nenhuma request manual exercita a nova política de retenção

### Referência histórica
ℹ️ REFERÊNCIA: `CONHECIMENTO-DO-MONOLITO.md` descreve o router do assistente-os; ausência de chamada real a provider no Terrasia não é drift

### Specs/planos
📋 PLANNED: spec de skills itens 6–9 (rotas, SDK, testes, validação manual) aprovados mas ainda não entregues — não é FAIL, é trabalho futuro

### subsistemas/ROUTER-GOVERNANCA-SKILLS-SOULS.md
✅ PASS: "parser FLAT skills, CRLF quebra silenciosamente" — confirmado em skills.ts linha 87
...
```

## Integração com terras-validacao

Esta skill **não substitui** `terras-validacao`. Aquela garante artefato de validação prática (`.http`/script). Esta garante que a **documentação de arquitetura** não mente sobre o código. Use ambas no checklist de entrega.

## Limites

- Não checa testes, coverage, performance — só conformidade docs↔código
- Não decide *como* corrigir — só aponta o drift
- Não classifique backlog, hipótese de produto, ordem futura nem spec aprovada-mas-não-entregue como FAIL de código — esses casos são PLANNED.
- `referencia-verbatim/` é cópia literal: só atualize a partir da fonte original após decisão explícita de renovar a referência.

## Exemplo de uso

```
> terras-drift: roda verificação completa antes do commit da Entrega 1 (router/tiers)
> terras-drift: checa só o contrato público depois de alterar uma rota
```

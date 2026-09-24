---
name: terras-adr
description: Registra decisão de reescrever vs. reaproveitar trecho do assistente-os quando NÃO estiver nas listas explícitas do CLAUDE.md/CONHECIMENTO-DO-MONOLITO.md. ADR leve em docs/adrs/. Complementa terras-reconstrucao (use-a primeiro).
keywords: [copiar do assistente-os, reaproveitar, reescrever, ADR, decisão de design]
---

---

# ADR Leve — Reescrever vs Reaproveitar (terrasia)

Versão minimalista do fluxo ADR/Bloco G do `v4-standards`, **sem** perfil Core/AI-1..4, sem RACI, sem retention schedule, sem questionário de adoção. Só registra a decisão arquitetural quando a lista explícita não cobre o caso.

## Quando usar

A lista canônica do que é **seguro reaproveitar quase verbatim** e do que é
**reescrita de propósito** vive na seção "O que reescrever vs. o que
reaproveitar quase verbatim" de `docs/CONHECIMENTO-DO-MONOLITO.md`, reforçada
no `CLAUDE.md` §"Não fazer". **Releia lá — não confie numa cópia:** a lista
cresce a cada módulo (ex.: `security/*` entrou quando o módulo security foi
entregue).

**Se o seu caso NÃO está em nenhuma das duas listas** → use esta skill antes
de codificar. Típico: um arquivo/subsistema do `assistente-os` que não é nem
"cluster souls+governança" nem um dos itens já marcados como desacoplado.

## Formato do ADR (arquivo: `docs/adrs/YYYY-MM-DD-<slug>.md`)

```markdown
# ADR: <título curto> — reescrever vs reaproveitar <área>

## Contexto
O que está em jogo: arquivo/módulo do assistente-os, o que ele faz, por que a decisão não é óbvia pelas listas canônicas (`CONHECIMENTO-DO-MONOLITO.md` / `CLAUDE.md`).

## Decisão
- [ ] **Reescrever do zero** — motivo: <ex: acoplamento oculto, decisões ad-hoc, fronteira errada>
- [ ] **Reaproveitar com adaptações** — o que muda: <ex: remover dep X, ajustar interface Y>
- [ ] **Reaproveitar verbatim** — justificativa: <ex: zero acoplamento, já validado em prod, igual ao item Z da lista>

## Alternativas consideradas
Breve: o que mais foi avaliado e por que descartado.

## Consequências
- Positivas: <ex: fronteira limpa, teste isolado>
- Negativas/Riscos: <ex: mais trabalho agora, duplicação temporária>
- Mitigação: <ex: portar deps-zones antes, testar contra terrasia_test>

## Rastreabilidade
- Assistente-os ref: <caminho/arquivo no repo antigo>
- Terrasia target: <pacote/módulo onde vai entrar>
- Relacionado: <outro ADR ou item da lista explícita>
```

## Processo

1. **Identificar** que o caso não está nas listas explícitas
2. **Criar ADR** seguindo o formato acima (pode ser rascunho rápido)
3. **Decidir** — uma das 3 opções, com justificativa
4. **Registrar** em `docs/adrs/` (criar pasta se não existe)
5. **Propagar a decisão de forma mínima** — manter o ADR como fonte da decisão; atualizar a lista em `CONHECIMENTO-DO-MONOLITO.md` somente se ela passa a ser uma regra recorrente de reuso/reescrita. Não reescrever a parte histórica do documento para registrar uma decisão nova.

## Exemplo real (hipotético)

> Área: `packages/core/old/sessions.ts` (CRUD threads/sessions, ~400 LOC)
> 
> Não está na lista — sessions não é "cluster souls+governança" nem "seguro reaproveitar".
> 
> **Decisão**: Reescrever. Motivo: sessions no antigo usa `entityQueue` e `familias` acoplados; no terrasia isso vira kernel puro (threads) + daemon (stream), fronteiras diferentes.
> 
> **ADR gerado**: `docs/adrs/2026-09-10-sessions-rewrite.md` — fonte da decisão.
> 
> **Propagação (passo 5)**: só tocar `CONHECIMENTO-DO-MONOLITO.md` se isso
> virar regra recorrente. Um caso pontual como este fica só no ADR.

## Integração com terras-reconstrucao

Esta skill **complementa** `terras-reconstrucao`:
- `terras-reconstrucao` = checklist de navegação (onde olhar, ordem, listas explícitas)
- `terras-adr` = ferramenta para decidir e registrar quando **não** está na lista

Use `terras-reconstrucao` primeiro. Se o caso cair em "Fora do escopo" → use `terras-adr`.

## Princípio

> **Decisão não documentada = decisão que será refeita (mal) daqui 6 meses.**
> 
> O custo de um ADR leve (5 min) << custo de re-trabalho por decisão implícita perdida.

# Eval — terras-reconstrucao + terras-adr: módulo fora das listas

## Cenário

O usuário pede: "recomeça o módulo de fila de mensagens do assistente-os, copia o `entityQueue` de lá que já funciona".

O módulo **não aparece** nem na lista "seguro reaproveitar quase verbatim" nem na de "reescrever de propósito" de `CONHECIMENTO-DO-MONOLITO.md`.

## Comportamento esperado

1. `terras-reconstrucao` conduz a leitura (ordem de construção, subsistema correspondente, `docs/referencia-verbatim/` se redação literal importa).
2. No passo reescrever-vs-reaproveitar, identifica que o caso está **fora das listas** e **não decide sozinho** nem copia: o default é não copiar.
3. Encaminha para `terras-adr`: ADR em `docs/adrs/YYYY-MM-DD-<slug>.md` com uma das 3 decisões (reescrever / adaptado / verbatim) justificada **antes de codificar**.
4. Propagação mínima: lista canônica só muda se virar regra recorrente.

## Verificação

- ✅ PASS: existe ADR cobrindo `entityQueue` antes de qualquer commit de código; a skill de reconstrução não afirmou "fora da lista = reescrever" como decisão fechada.
- ❌ FAIL: código copiado do monólito sem ADR, ou a skill descartou o ADR decidindo antecipadamente pela regra.

# Eval — terras-api-sync: novo evento SSE

## Cenário

Mudança no daemon adiciona um campo `usage` no frame SSE `done` (tokens consumidos da chamada).

## Comportamento esperado

1. `terras-api-sync` exige os **3 updates atômicos no mesmo commit**.
2. SDK: atualiza `StreamEvent` em `packages/client/src/stream.ts` (não só `client.ts`) e os testes do SDK em `packages/client/src/*.test.ts` cobrem o campo novo.
3. Docs: README seção "Contrato da API" documenta o frame `done` com `usage`.
4. Validação: `npm --workspace @terrasia/client typecheck && npm --workspace @terrasia/client test` rodam e passam antes do commit.

## Verificação

- ✅ PASS: commit único contém daemon + `stream.ts` + teste do SDK + README.
- ❌ FAIL: campo existe no daemon mas `StreamEvent` não tipa `usage`, ou teste do SDK não foi atualizado, ou README ficou para "depois".

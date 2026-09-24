# Eval — terras-validacao: endpoint alterado vs refactor interno

## Cenário A — mudança observável

Refatoração adiciona um novo query param `?limit=N` em `GET /souls/:soul/threads`.

## Cenário B — refactor interno

Extração de função / renomeação interna em `packages/daemon/src/server.ts` sem qualquer mudança de rota, payload, status ou evento SSE.

## Comportamento esperado

- **Cenário A**: `terras-validacao` exige artefato que exercite a mudança ponta a ponta — entrada nova em `requests.http` **e** step em `scripts/api-smoke-test.sh`, além de testes automatizados. Sem isso, a entrega está incompleta.
- **Cenário B**: nenhum artefato de validação manual novo é exigido — a regra vale para comportamento observável, não para refactor interno; testes automatizados existentes continuam sendo o gate.

## Verificação

- ✅ PASS A: `requests.http` + `api-smoke-test.sh` no mesmo commit do `?limit`.
- ✅ PASS B: mudança interna sem ruído de artefatos obrigatórios inventados.
- ❌ FAIL: `?limit` entregue só com unit test, "validação manual depois".

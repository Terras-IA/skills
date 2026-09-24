# Eval — terras-boundary: rota exclusiva de admin proposta no motor

## Cenário

O usuário pede: "adiciona no daemon do terrasia um `GET /souls/:soul/usage-report` com grana por mês, é pra tela de faturamento do admin".

## Comportamento esperado

1. `terras-boundary` aciona antes de qualquer implementação.
2. Classifica a rota como **não-motor**: dashboard/faturamento é UI/tela do `terrasia-admin`; o motor só deve expor dados brutos que o admin consome via SDK.
3. Verifica a policy de domínio (README/AGENTS "No admin/client UI routes here") e propõe o caminho conforme: dado bruto no motor **se não existir**, agregação/tela no `terrasia-admin` — ou nego a rota no motor se já há equivalente.
4. Nenhuma rota de UI/tela é criada em `packages/daemon`.

## Verificação

- ✅ PASS: resposta menciona a fronteira e nenhum handler de rota de relatório/UI entra no daemon.
- ❌ FAIL: `GET /souls/:soul/usage-report` implementado em `packages/daemon/src/server.ts` com shape pensado pra tela.

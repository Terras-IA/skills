# Eval — terras-qualidade: tarefa não-trivial vs correção trivial

## Cenário A — tarefa não-trivial

Pedido de feature nova: adicionar um query param `?expand=owner` em uma rota
existente do daemon, com mudança de comportamento observável.

## Cenário B — correção trivial

Correção de typo em um comentário de `packages/daemon/src/server.ts`, sem
qualquer mudança de comportamento.

## Comportamento esperado

- **Cenário A**: `terras-qualidade` dispara e exige o protocolo — plano
  aprovado antes de código, teste que falha antes (o `?expand` ainda não
  existe), `./scripts/verify-all.sh` verde cedo e no fim, validação prática
  via `terras-validacao` e, sendo superfície pública nova, revisão cruzada
  antes do commit.
- **Cenário B**: `terras-qualidade` não dispara — typo de comentário não é
  tarefa não-trivial; nenhum passo do protocolo é exigido.

## Verificação

- ✅ PASS A: entrega do `?expand` com teste novo (RED antes), gate verde e
  revisão cruzada registrada.
- ✅ PASS B: typo commitado direto, sem ruído de protocolo.
- ❌ FAIL: `?expand` codificado direto sem plano nem teste, gate rodado só no
  fim (ou nem isso).

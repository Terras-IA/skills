---
name: terras-validacao
description: Entrega no terrasia precisa de validação prática (requests.http + scripts/api-smoke-test.sh), além de unit tests — regra do CLAUDE.md. Use ao fechar endpoint/script novo ou mudança de comportamento observável. Não para planejamento (terras-reconstrucao) nem código ainda não roda.
keywords: [validar entrega, requests.http, api-smoke-test, verificado rodando de verdade, já está pronto pra commitar]
---

---

# Validação de entregas — terrasia

O `CLAUDE.md` deste repo exige que toda entrega tenha um jeito de
validar/testar na prática — além dos testes automatizados: um `.http`/REST
ou um script (`curl`, shell, etc.) que exercita a implementação de ponta a
ponta. Vale pra cada endpoint novo, script novo, ou mudança de
comportamento observável. Não é decorativo: já foi aplicado
retroativamente a entregas que saíram sem isso (`d62bbb5`), então trate
como parte da definição de pronto, não como polimento opcional de última
hora.

## Convenção já estabelecida — não invente um formato novo

Dois artefatos **vivos**, que crescem a cada entrega em vez de nascer um
novo por PR:

- **`requests.http`** (raiz do repo) — formato REST Client (VS Code):
  variáveis `@baseUrl`/`@token`/`@soul`, requests encadeados via `# @name`
  e `{{nomeDoRequest.response.body.$.campo}}` pra reusar dados de um
  request anterior (ex. o id de uma thread recém-criada). Cobre o
  contrato inteiro da API: caminho feliz **e** os casos de erro esperados
  (401 sem token, 404 soul/thread inexistente, 400 prompt vazio) — cada
  request comentado com o status esperado.
- **`scripts/api-smoke-test.sh`** — alternativa em `curl` pra quem não tem
  a extensão REST Client. `set -euo pipefail`, lê o token do `.env`,
  função `check_status` que acumula falhas e sai com erro no final.
  Espelha o mesmo contrato que os testes automatizados (`*.test.ts`)
  cobrem via `node:test`, só que contra um daemon real rodando.

Pra mudanças que **não** são endpoint HTTP (scripts novos, infra, CI), o
precedente é `scripts/verify-all.sh`: builda tudo, roda cada suíte de
teste do monorepo e o próprio script novo em sequência, parando no
primeiro erro (`set -e`). A validação de um script é rodá-lo de verdade e
confirmar o comportamento esperado — não só descrevê-lo em prosa.

## Checklist ao fechar uma entrega

1. **Confirme que o código realmente existe e roda neste checkout antes
   de seguir os passos abaixo.** Se o endpoint/script que a entrega
   descreve não está de fato no repo (ainda não implementado, só
   planejado, ou só numa branch/stash diferente), não há o que validar
   ainda — volte pra "Quando não se aplica" em vez de produzir um artefato
   pra código que não existe.

2. **Identifique o tipo de mudança**: endpoint HTTP novo/alterado? Script
   novo (CLI, CI, helper de migration)? Mudança de comportamento
   observável sem superfície nova (ex. um bugfix que muda o que a API
   retorna ou o que um script imprime)?

3. **Endpoint HTTP novo ou alterado** → adicione o(s) request(s)
   correspondente(s) em `requests.http` (caminho feliz + qualquer caso de
   erro novo) e, quando fizer sentido, o equivalente em
   `scripts/api-smoke-test.sh`. Estenda os arquivos existentes — não crie
   um `.http` novo por entrega, isso fragmenta a cobertura em vez de
   acumulá-la.

4. **Script novo** → ele mesmo, ao rodar, já deve provar que funciona
   (exit code correto, output claro tipo "ok"/"FAIL" por passo, como em
   `api-smoke-test.sh`). Só considere adicioná-lo a `scripts/verify-all.sh`
   se ele for **sem efeito colateral / idempotente** (builda, testa,
   checa — como tudo que já está lá). Um script com efeito colateral real
   (backup, migration destrutiva, chamada a serviço externo) não deve
   entrar cegamente num script pensado pra rodar repetidamente — valide
   esses rodando uma vez manualmente e confirmando o resultado
   (ex. o dump gerado é válido e aponta pro banco certo), não só o exit
   code.

5. **Mudança de comportamento sem superfície nova** (bugfix, endurecimento
   de segurança) → adicione ou ajuste um request/case existente que prove
   o novo comportamento — ex. um request que antes vazava um segredo e
   agora vem mascarado, comentado explicando o antes/depois.

6. **Rode o artefato de verdade antes de considerar a entrega pronta.** O
   precedente do repo é explícito nisso: "verificado rodando de verdade
   antes de commitar" (`d62bbb5`). Escrever o `.http`/script sem
   executá-lo e confirmar o resultado não cumpre a regra.

7. **Isso é além dos testes automatizados, não no lugar deles.** Se a
   mudança já tem cobertura em `*.test.ts`, ainda assim precisa do
   artefato manual/smoke — são propósitos diferentes (CI vs. alguém
   validando manualmente contra um servidor real).

## Quando não se aplica

- Mudança puramente interna sem comportamento observável de fora
  (refactor que não muda saída nenhuma, só docs, só comentário) não
  precisa de artefato novo. Na dúvida se é "puramente interno", trate como
  observável — o custo de validar demais é bem menor que o de uma entrega
  quebrada sem forma de provar que funciona.
- Não crie artefato de validação pra código que ainda não existe ou ainda
  não roda — a regra é sobre entregas terminadas, não sobre planejamento
  (isso é papel da `terras-reconstrucao`, não desta skill).

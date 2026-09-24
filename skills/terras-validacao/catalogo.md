---
name: terras-validacao
version: 1.0.0
access: free
category: operacao
description: Toda entrega exige validação prática além dos testes automatizados — um artefato executável que exercita a mudança de ponta a ponta contra o alvo real, rodado de verdade antes do commit.
keywords: [validar entrega, validacao pratica, smoke test, verificado rodando de verdade]
---

# Validação prática de entregas

## Descrição

Toda entrega precisa de um jeito de validar na prática, além dos testes automatizados: um artefato executável (coleção de requests HTTP, script de smoke test, passo a passo) que exercita a implementação de ponta a ponta contra o alvo real — servidor rodando, API viva, script de verdade. Vale para cada endpoint novo, script novo ou mudança de comportamento observável.

Não é decorativo: a entrega que sai sem isso não tem como provar que funciona fora da suíte. Trate como parte da definição de pronto, não como polimento de última hora.

## Quando usar

- Ao fechar endpoint HTTP novo ou alterado.
- Ao fechar script novo (CLI, helper, migração).
- Ao fechar mudança de comportamento observável sem superfície nova (bugfix que muda o que a API retorna ou o que um script imprime).
- Não usar para mudança puramente interna sem comportamento observável (refactor que não muda saída nenhuma, só docs) — e nunca para código que ainda não existe ou ainda não roda.

## Como funciona

### 1. Confirme que existe o que validar

O endpoint/script que a entrega descreve precisa existir e rodar neste checkout antes de qualquer passo abaixo. Se ele só existe no plano, numa branch não aplicada ou num stash, não há o que validar ainda — volte para "Quando não se aplica".

### 2. Identifique o tipo de mudança

Endpoint HTTP novo/alterado? Script novo? Mudança de comportamento observável sem superfície nova? Cada tipo tem um artefato certo.

### 3. Escolha o artefato certo

- **Endpoint HTTP** → coleção de requests encadeados (um request aproveita a resposta do anterior: cria → lê → altera), cobrindo o caminho feliz E os casos de erro esperados (401 sem token, 404 inexistente, 400 payload inválido), cada um comentado com o status esperado. Estenda a coleção existente do projeto — não crie uma nova por entrega, isso fragmenta a cobertura em vez de acumulá-la.
- **Script novo** → ele mesmo, ao rodar, já prova que funciona: exit code correto, output claro com "ok"/"FAIL" por passo. Script com efeito colateral real (backup, migração destrutiva, chamada a serviço externo) não entra em gate repetível — valide rodando uma vez de verdade e confirmando o resultado (o dump gerado é válido e aponta pro lugar certo), não só o exit code.
- **Comportamento sem superfície nova** → ajuste um caso existente que prove o novo comportamento: o request que antes vazava um segredo e agora vem mascarado, comentado com o antes/depois.

### 4. Rode de verdade antes de considerar pronto

Escrever o artefato sem executá-lo e confirmar o resultado não cumpre a regra. A evidência é a execução contra o alvo real, com saída que mostra o comportamento esperado.

### 5. Isso é além dos testes automatizados, não no lugar deles

Se a mudança já tem cobertura em suíte, ainda assim precisa do artefato manual/smoke — são propósitos diferentes (suíte contínua vs. alguém validando manualmente contra um servidor real).

## Governança

- O artefato de validação vive no mesmo repo da entrega e cresce a cada entrega — é documentação executável, não descartável.
- Credenciais usadas no artefato ficam em variável/arquivo de ambiente ignorado pelo versionamento; nunca embutidas no arquivo.

## Critério de qualidade

A entrega só está pronta quando o artefato foi executado de verdade contra o alvo real e a saída confirma o comportamento esperado, incluindo pelo menos um caso de erro. "Deve funcionar" sem execução é a entrega que mais tarde se prova quebrada.

---
name: terras-conciliacao-bancaria-ofx
version: 1.0.0
access: free
category: financeiro
description: Concilia extrato bancário com os lançamentos internos e separa o que casou, o que divergiu, o que é tarifa e o que ficou sem par.
keywords: [conciliar, conciliação, extrato, ofx, fechar o caixa, saldo não bate, tarifa]
---

# Conciliação bancária (OFX/CSV)

## Descrição

Cruza as linhas de um extrato bancário com os lançamentos que a empresa registrou, e devolve quatro pilhas distintas: casado, casado com diferença, tarifa ou encargo do próprio banco, e sem par. O objetivo não é "fechar a conciliação" — é deixar visível **o que não fecha**, com o motivo, para alguém decidir.

Esta instrução é um guia operacional: não decide sozinha sobre baixa de título, reconhecimento de receita, provisão ou contestação junto ao banco. Trabalhe com o extrato, o registro interno e a revisão da pessoa responsável pelo caixa. Quando um dado não existir, escreva "não informado" e diga qual decisão fica bloqueada.

**A leitura do extrato é manual por enquanto.** Não há integração que busque o arquivo no banco nem que leia os lançamentos de um sistema de gestão: o extrato e o registro interno chegam colados na conversa ou como texto extraído. Trate qualquer valor como declarado pela pessoa, não como verificado na fonte.

## Quando usar

- Fechar o caixa do dia ou do período e precisar saber o que sobrou sem explicação.
- Investigar diferença entre saldo bancário e saldo contábil.
- Identificar tarifas, IOF, estornos e encargos que ninguém lançou.
- Preparar evidência antes de contestar um débito com o banco.
- Auditar um período fechado por outra pessoa.

## Como funciona

### Inputs esperados

Extrato (OFX ou CSV) e lançamentos internos do mesmo período, com no mínimo: data, valor, sinal (débito/crédito), histórico/descrição e, quando houver, documento ou identificador do título.

Antes de processar, confirme cinco coisas e **não avance sem elas**: conta e banco, período exato (início e fim, inclusive), moeda, saldo inicial e saldo final declarados pelo extrato. Sem saldo inicial e final não existe conciliação — existe uma lista de coincidências, o que é outra coisa e deve ser dito com esse nome.

Reorganize texto solto numa tabela com colunas nome, tipo, exemplo, origem e regra de validação. Peça confirmação dos campos críticos (valor, data, sinal) antes de concluir.

### Passo a passo

1. **Normalizar.** Data para um formato só; valor como número com sinal explícito; descrição em minúsculas sem acento para comparação. Guarde sempre o texto original ao lado — a descrição crua é a evidência.
2. **Casar o exato.** Mesma data, mesmo valor, mesmo sinal. Um lançamento interno só pode casar com **uma** linha do extrato: par consumido não volta para a pilha.
3. **Casar com tolerância.** Diferença de até R$ 0,02 por linha vira "casado com diferença", nunca "casado". Some as diferenças: centavo isolado é arredondamento, centavo sistemático é regra de cálculo errada em algum lugar.
4. **Casar com deslocamento de data.** Mesmo valor em D+1 ou D+2 costuma ser diferença de data de movimento × data de compensação. Marque como casado com deslocamento e registre quantos dias.
5. **Separar tarifa e encargo.** Débitos do próprio banco sem contrapartida interna: tarifa de pacote, TED/DOC, manutenção, IOF, juros de cheque especial. Vão para uma pilha própria — não são divergência, são despesa que ninguém lançou.
6. **Listar o sem par.** Nos dois sentidos: linha do extrato sem lançamento interno, e lançamento interno sem linha no extrato. São coisas diferentes e não podem ser somadas.
7. **Provar a aritmética.** Saldo inicial + créditos − débitos = saldo final do extrato. Se não bater, a conciliação está errada **antes** de qualquer análise; pare e reporte.

### Casos de borda

- **Um para muitos.** Um crédito de R$ 10.000 no extrato contra três títulos internos de R$ 4.000, R$ 3.500 e R$ 2.500: some antes de concluir que não casou. Registre como agrupamento, com as três origens visíveis.
- **Estorno no mesmo dia.** Débito e crédito de mesmo valor e mesma data se anulam no saldo, mas **não** somem do relatório: estorno silenciado esconde erro operacional que vai repetir.
- **Duplicidade real.** Duas linhas idênticas podem ser dois pagamentos legítimos. Nunca descarte a segunda como "repetida" — marque como possível duplicidade e peça confirmação.
- **Período cortado.** Lançamento no fim do período com compensação no período seguinte não é divergência; é corte. Diga isso explicitamente em vez de listar como pendência.
- **Arquivo truncado.** Se a soma das linhas não reproduz o saldo final, trate o arquivo como incompleto e pare.

Em qualquer caso de borda, preserve a saída com a marca "pendente", "não observado" ou "base insuficiente". Não produza precisão artificial: o artefato informa cobertura, limitações e quem precisa revisar.

## Artefato de saída

Relatório com, nesta ordem: resumo (quantas linhas, quanto casou, quanto sobrou, em valor e em quantidade), a prova da aritmética, e as quatro pilhas — casado, casado com diferença, tarifa/encargo, sem par — cada linha com data, valor, descrição original e o motivo da classificação.

O relatório orienta a conversa e a decisão; baixa de título, contestação ou lançamento de despesa dependem de aprovação humana.

## Exemplo de uso

### Input fictício

(dados fictícios — todos os valores são MOCK)

Extrato MOCK da conta 00123-4, 01/09 a 05/09, saldo inicial R$ 12.400,00, saldo final R$ 18.126,45. Seis linhas, entre elas um crédito de R$ 6.000,00 em 03/09, um débito de R$ 268,55 em 04/09 com histórico "TAR PACOTE SERVICOS" e um crédito de R$ 1.999,98 em 05/09.

Lançamentos internos MOCK: recebimento de R$ 6.000,00 em 02/09 (três notas de R$ 2.000,00), e um recebimento previsto de R$ 2.000,00 em 05/09.

### Output esperado

Saída MOCK: o crédito de 03/09 casa com deslocamento de 1 dia e agrupa três títulos; o de 05/09 casa com diferença de R$ 0,02, sinalizada como possível arredondamento de boleto; o débito de R$ 268,55 vai para a pilha de tarifa, sem contrapartida interna, com a observação de que ninguém o lançou. A aritmética fecha.

O exemplo é simulação operacional: não é dado real e serve para mostrar o nível de detalhe esperado.

## Governança

- Extrato bancário é dado financeiro sensível: não reproduza o arquivo inteiro em resposta nem em log, só as linhas em discussão.
- Não classifique divergência como fraude. Descreva o fato ("débito sem contrapartida interna") e deixe a interpretação para quem tem contexto.
- Conciliação não autoriza baixa de título nem pagamento: ela produz evidência para a decisão.
- Período já fechado e revisado não é reescrito; divergência encontrada depois vira ajuste datado, com o motivo.

## Critério de qualidade

A entrega está pronta somente quando traz conta e período, os saldos inicial e final com a aritmética demonstrada, as quatro pilhas separadas e somadas, o critério de tolerância declarado em número, as linhas sem par nos dois sentidos, as limitações e o próximo passo. Percentual de conciliação sem o valor absoluto que sobrou é número incompleto — apresente os dois.

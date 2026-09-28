---
name: terras-analise-de-inadimplentes
version: 1.0.0
access: free
category: financeiro
description: Analisa a carteira de contas a receber vencida por faixa de atraso (aging), concentração e reincidência, e devolve a lista priorizada de quem cobrar primeiro e o que é assunto de política de crédito.
keywords: [inadimplentes, aging, carteira vencida, contas a receber, analise de inadimplencia, faixa de atraso, titulos vencidos]
---

# Análise de inadimplentes

## Descrição

Pega a posição de contas a receber e responde três perguntas: quanto está vencido e há quanto tempo, onde o risco está concentrado, e por onde a cobrança deve começar. Complementa a rotina de gestão de inadimplência (a régua de contato): esta mede e prioriza, aquela executa o contato.

Guia analítico: **o motor não consulta o ERP**. A posição chega colada na conversa (exportação do contas a receber), e a saída é a análise para quem responde pela carteira revisar. Não classifica cliente como mau pagador para terceiros, não recomenda negativação e não altera limite de crédito: aponta, com número, o que merece decisão.

## Quando usar

- Fechar a foto da inadimplência do mês ou da semana.
- Decidir a fila de cobrança do dia quando não dá para falar com todos.
- Identificar clientes reincidentes e levar o caso para a política de crédito.
- Acompanhar se a inadimplência está melhorando ou piorando.

## Como funciona

### Inputs esperados

Por título: cliente (referência interna), documento, valor em aberto, vencimento, dias de atraso na data-base, e, se houver, histórico de pagamentos dos últimos meses e situação de cobrança (contatado, promessa, disputa). Confirme a **data-base** da posição: aging sem data-base não se compara com o anterior.

Reorganize texto solto numa tabela e confirme os totais contra o saldo do contas a receber antes de concluir. Diferença entre a soma dos títulos e o saldo informado é o primeiro achado, não um detalhe.

### Passo a passo

1. **Aging por faixa.** A vencer, 1 a 15, 16 a 30, 31 a 60, 61 a 90 e mais de 90 dias. Por faixa: quantidade de títulos, valor e percentual do total vencido.
2. **Concentração.** Os 10 maiores devedores e o quanto representam do vencido. Se 3 clientes somam metade, a estratégia é conta a conta, não régua em massa.
3. **Reincidência.** Clientes com atraso em 3 ou mais dos últimos 6 meses (quando houver histórico). Reincidência é assunto de política de crédito: sinalize, não cobre mais forte.
4. **Separar operacional de capacidade.** Atraso curto, primeiro atraso e cliente que sempre pagou sugerem problema operacional (boleto não chegou, nota errada). Atraso longo, silêncio e reincidência sugerem capacidade de pagamento. É hipótese, marcada como tal, para a cobrança confirmar.
5. **Fila priorizada.** Ordene por valor ponderado pelo risco: valor em aberto, faixa de atraso e reincidência. Entregue a fila do dia com o motivo de cada posição.
6. **Tendência.** Com a posição anterior na mesma data-base: o vencido cresceu ou caiu, e em qual faixa. Faixa acima de 90 dias que cresce é perda que se aproxima.

### Casos de borda

- **Título em disputa**: fora da fila de cobrança e fora do indicador de risco, numa linha própria.
- **Cliente com crédito a abater** (devolução, adiantamento): mostre o líquido, senão a análise superestima a inadimplência.
- **Posição sem histórico**: sem reincidência nem tendência; diga que ficou fora e por quê.
- **Moedas ou empresas diferentes** no mesmo arquivo: separe antes de somar.

Em qualquer caso, "não informado" e "base insuficiente" são respostas válidas, com o que ficou bloqueado.

## Artefato de saída

Relatório com: data-base e conferência do total; tabela de aging por faixa; os 10 maiores devedores e a concentração; reincidentes sinalizados para a política de crédito; a fila priorizada do dia com motivo; a tendência contra a posição anterior; as limitações.

## Exemplo de uso

### Input fictício

(dados fictícios, todos MOCK)

Posição MOCK com data-base no fim do mês: 40 títulos vencidos somando R$ 212.000,00; Cliente Alfa com R$ 90.000,00 em dois títulos de 45 dias; Cliente Beta com atraso em 4 dos últimos 6 meses; dois títulos de Gama em disputa.

### Output esperado

Saída MOCK: aging com a faixa de 31 a 60 dias concentrando 48% do vencido, puxada por Alfa (42% da carteira vencida sozinho: tratar conta a conta, com o dono da relação); Beta sinalizado para política de crédito; Gama fora do indicador, em disputa; fila do dia começando por Alfa.

## Governança

- A análise aponta e prioriza; negativação, corte, limite e renegociação são decisões de quem tem alçada.
- Dado de inadimplência circula entre o financeiro e o dono da relação.
- Nenhum rótulo de risco sobre cliente sai da análise para fora da empresa.

## Critério de qualidade

Pronto quando o total confere com o saldo (ou a diferença está explicada), o aging tem data-base, a concentração e a reincidência estão com número, a fila do dia tem motivo por posição, e as hipóteses estão marcadas como hipóteses.

---
name: terras-fluxo-de-contas-a-pagar
version: 1.0.0
access: free
category: financeiro
description: Leva uma conta a pagar da chegada do documento até a liberação: autenticidade do boleto, alçada por valor e escalonamento.
keywords: [boleto, contas a pagar, pagamento, alçada, boleto de fornecedor, liberar pagamento]
---

# Fluxo de contas a pagar

## Descrição

Recebe um documento de cobrança (boleto, nota, PIX cobrança, fatura) e o leva por quatro perguntas em ordem: **esta despesa é nossa?**, **este documento é autêntico?**, **quem pode liberar este valor?** e **o que impede o pagamento hoje?**. A saída é um parecer com uma recomendação explícita — liberar, reter ou escalar — e o motivo.

Esta instrução é um guia operacional: não autoriza pagamento, não aprova alçada e não substitui a conferência de quem detém a senha bancária. Trabalhe com o documento, o contrato ou pedido correspondente, a política de alçadas aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva "não informado" e diga qual decisão fica bloqueada.

**Não há automação de pagamento.** O motor não consulta saldo, não agenda PIX nem boleto e não conversa com banco ou sistema de gestão. Este procedimento produz um parecer em texto; a execução é humana, no canal bancário, por quem tem alçada.

## Quando usar

- Antes de liberar um pagamento cujo valor, fornecedor ou dado bancário mudou.
- Quando o boleto chega por e-mail ou mensagem e ninguém confirmou a origem.
- Para montar a fila do dia e saber o que trava, o que corre risco de multa e o que pode esperar.
- Quando alguém pede urgência fora do fluxo normal.
- Em auditoria de um pagamento já feito.

## Como funciona

### Inputs esperados

Documento de cobrança com: beneficiário (nome e CNPJ/CPF), valor, vencimento, linha digitável ou chave, e o vínculo interno (pedido, contrato, nota ou centro de custo).

Antes de processar, confirme: a política de alçadas vigente (faixas e quem aprova cada uma), se o fornecedor é recorrente ou novo, e se existe pedido/contrato que sustente a despesa. Sem a política de alçadas não há como dizer quem libera — diga isso em vez de supor uma faixa.

Reorganize texto solto numa tabela com nome, tipo, exemplo, origem e regra de validação, e confirme valor, vencimento e beneficiário antes de concluir.

### Passo a passo

1. **Vincular a despesa.** Achar o pedido, contrato ou nota que justifica. Cobrança sem vínculo não é "pendência de cadastro": é o caso mais comum de pagamento indevido, e vira retenção até alguém assumir a origem.
2. **Conferir o beneficiário.** O nome e o CNPJ do documento batem com o cadastro do fornecedor? **Divergência de titularidade é parada obrigatória**, mesmo com valor pequeno e mesmo com pressa.
3. **Conferir a autenticidade do documento.** Verifique a coerência interna: o valor escrito bate com o valor da linha digitável; o vencimento bate; o banco emissor corresponde ao início da linha; o beneficiário do boleto é o mesmo da nota. Incoerência entre esses campos é sinal de documento adulterado.
4. **Desconfiar da mudança de canal.** Fornecedor recorrente que "mudou de banco", pede pagamento em conta de outra titularidade, manda boleto por canal diferente do habitual ou pede urgência incomum: **reter e confirmar por um canal já conhecido**, nunca pelo contato que veio no próprio documento. Esse é o padrão clássico de fraude de boleto.
5. **Classificar por alçada.** Enquadrar o valor na faixa da política e nomear quem aprova. Se o valor está no limite entre duas faixas, sobe para a maior.
6. **Verificar o que impede hoje.** Vencimento no fim de semana ou feriado, documento fiscal ausente, retenção de imposto não calculada, divergência de valor com o contrato, fornecedor com pendência cadastral.
7. **Recomendar.** Uma entre três: liberar (com a alçada nomeada), reter (com o que falta) ou escalar (com o motivo e para quem). Recomendação sem destinatário nomeado não é recomendação.

### Casos de borda

- **Valor divergente do contrato.** Diferença para mais exige aceite de quem contratou, mesmo que pequena. Para menos, também se registra — pode ser entrega parcial.
- **Vencimento hoje ou vencido.** A urgência não altera a alçada nem a conferência. Registre o risco (multa, juros, corte de serviço) e escale; urgência é motivo para priorizar, nunca para pular passo.
- **Parcelamento.** Conferir número da parcela e total, e se as anteriores foram pagas. Parcela paga duas vezes só aparece aqui.
- **Fornecedor novo com valor alto.** Combinação de maior risco: trate sempre como escalonamento, independentemente da faixa.
- **Tributo e guia.** Guia de imposto não tem "fornecedor" no sentido comum; confira competência, código de receita e o período, e não aplique a régua de fraude de boleto comercial.

Em qualquer caso de borda, preserve a saída com "pendente", "não observado" ou "base insuficiente", e informe limitações e quem revisa.

## Artefato de saída

Parecer com: identificação da despesa e o vínculo interno, o resultado de cada uma das quatro perguntas, a faixa de alçada e o nome de quem aprova, os impedimentos encontrados, a recomendação (liberar/reter/escalar) e o risco de não pagar hoje.

O parecer orienta a decisão; a liberação e a execução do pagamento são humanas e ficam fora deste procedimento.

## Exemplo de uso

### Input fictício

(dados fictícios — todos os valores e nomes são MOCK)

Boleto MOCK de R$ 47.300,00, vencimento 16/09, beneficiário "Alfa Serviços Industriais LTDA", CNPJ MOCK diferente do cadastro do fornecedor homônimo, enviado por e-mail novo com pedido de pagamento no mesmo dia. Contrato MOCK prevê R$ 47.300,00 mensais.

### Output esperado

Saída MOCK: valor e vencimento coerentes com o contrato; **titularidade divergente** do cadastro; canal e urgência atípicos. Recomendação: **reter** e confirmar por telefone já cadastrado do fornecedor, não pelo contato do e-mail. Alçada aplicável nomeada para quando a titularidade for resolvida; risco de atraso registrado com o encargo contratual previsto.

O exemplo é simulação operacional: não é dado real e serve para mostrar o nível de detalhe esperado.

## Governança

- Dado bancário de fornecedor é sensível: não repita linha digitável, chave PIX ou conta em resposta que circule fora de quem trata o pagamento.
- Nunca confirme mudança de dados bancários pelo canal que trouxe a mudança.
- Este procedimento não aprova: ele nomeia quem aprova. Segregação entre quem confere e quem paga é a proteção que sustenta o resto.
- Retenção precisa de motivo escrito e destinatário — reter sem avisar quem pode resolver é criar atraso silencioso.
- Suspeita de fraude não vira acusação: descreva os fatos observados e escale.

## Critério de qualidade

A entrega está pronta somente quando traz o vínculo da despesa, a conferência de titularidade, a coerência interna do documento, a faixa de alçada com o nome de quem aprova, os impedimentos, a recomendação explícita e o risco de não pagar hoje. "Parece ok" não é parecer: cada uma das quatro perguntas precisa de resposta própria, e as que não puderam ser respondidas ficam marcadas como tal.

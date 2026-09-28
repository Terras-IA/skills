---
name: terras-cobranca-hubspot
version: 1.0.0
access: free
category: financeiro
description: Desenha a régua de cobrança dentro do HubSpot (propriedades, listas, workflows, tarefas e o assistente) sem duplicar o ERP, com o que o CRM guarda e o que só o financeiro decide.
keywords: [hubspot, hub spot, crm de cobranca, workflow de cobranca, sequencia de cobranca]
---

# Cobrança pelo HubSpot

## Descrição

Leva a régua de cobrança para dentro do HubSpot quando a empresa já atende e se relaciona com o cliente por ele: quem está em qual ponto da régua, que contato sai, por qual canal, e o que volta para o financeiro. O ERP continua sendo a fonte do título (valor, vencimento, pagamento); o HubSpot é onde a conversa acontece.

Esta instrução é um guia de desenho. **O motor não acessa o HubSpot**: não lê contato, não cria tarefa, não dispara workflow. A saída é o desenho da régua no CRM, a especificação para quem configura, ou os textos, para uma pessoa revisar e aplicar. A régua em si (D-3 a D+15, encargos, ponto de decisão) é a da rotina de gestão de inadimplência; aqui está **onde** ela mora no HubSpot.

## Quando usar

- Levar a régua de cobrança para workflows e tarefas do HubSpot.
- Decidir quais dados de cobrança o CRM precisa guardar e de onde eles vêm.
- Especificar o que o assistente de atendimento no HubSpot pode e não pode dizer sobre dívida.
- Revisar uma automação de cobrança que manda mensagem errada ou repetida.

## Como funciona

### Princípio: o título é do ERP, a conversa é do CRM

Valor, vencimento, pagamento e cancelamento vêm do ERP (sincronização ou importação diária). O HubSpot **não** recalcula valor nem decide baixa. Quando os dois divergem, vale o ERP, e a divergência é um erro de integração a corrigir, não a contornar.

### Inputs esperados

Os objetos e propriedades que já existem no portal (contatos, empresas, negócios, faturas, tickets), a régua aprovada, os canais disponíveis (e-mail, WhatsApp, telefone), quem é o dono de cada cliente, e como o dado de título chega do ERP.

### Passo a passo

1. **Modelar o dado mínimo.** Na empresa ou no negócio: situação de cobrança (em dia, a vencer, vencido, em negociação, fora da régua), dias de atraso, valor em aberto, data do último contato, promessa de pagamento (data e valor) e link do boleto vigente. Uma propriedade por fato; nada de texto livre para situação.
2. **Definir a origem de cada propriedade.** Tudo o que é título vem do ERP (sincronizado); o que é conversa (último contato, promessa) nasce no CRM. Escreva isso na especificação: propriedade sem dono diverge.
3. **Listas por ponto da régua.** Uma lista ativa por ponto (D-3, D+1, D+5, D+10, D+15), filtrando pela situação e pelos dias de atraso. A lista é o que alimenta o workflow.
4. **Workflows curtos, um por ponto.** Cada um: envia o contato daquele ponto, registra o envio e para. Workflow que tenta fazer a régua inteira fica impossível de corrigir. Pagamento confirmado (vindo do ERP) **tira** o cliente de todas as listas.
5. **Tarefas para o que exige gente.** D+5 (contato ativo) e D+15 (ponto de decisão) viram tarefa para o dono da relação, não mensagem automática.
6. **Assistente de atendimento.** Pode informar valor, vencimento, reenviar o link do boleto vigente e registrar promessa de pagamento. Não pode negociar desconto, prometer prorrogação, ameaçar negativação ou falar de dívida com quem não é o contato financeiro.
7. **Relatório diário.** Quantos em cada ponto, quantos contatos saíram, promessas feitas e quebradas, casos em D+15 aguardando decisão.

### Casos de borda

- **Pagou e recebeu cobrança**: sincronização atrasada. Corrija a origem (frequência da sincronização) e peça desculpa uma vez; não ajuste o CRM à mão.
- **Cliente com vários contatos**: a cobrança vai só para o contato financeiro marcado; sem ele, vira pendência de cadastro.
- **Disputa aberta (ticket)**: ticket de reclamação aberto suspende os workflows de cobrança daquele cliente.
- **Mesmo cliente em dois pontos** (títulos diferentes): um contato só, com todos os títulos; duas mensagens no mesmo dia soam como erro.

## Artefato de saída

Especificação da régua no HubSpot: propriedades (nome, tipo, origem), listas (filtro), workflows (gatilho, ação, saída), tarefas (quem, quando), limites do assistente e o relatório diário. Ou os textos de cada ponto, prontos para o workflow.

## Exemplo de uso

### Input fictício

(dados fictícios, todos MOCK)

Portal MOCK com empresas e negócios, assistente de atendimento já ativo, títulos importados do ERP uma vez por dia às 6h, canais e-mail e WhatsApp.

### Output esperado

Saída MOCK: seis propriedades com origem declarada (quatro do ERP, duas do CRM); cinco listas ativas; cinco workflows de um passo; tarefas em D+5 e D+15 para o dono da conta; o assistente autorizado a reenviar o link do boleto e registrar promessa, e proibido de negociar; relatório das 18h com os números do dia.

## Governança

- O CRM não decide valor, desconto, prorrogação, negativação nem corte.
- Dado de inadimplência só para o contato financeiro e o dono da relação.
- Nada de cobrança em canal coletivo nem para contato que não é do financeiro do cliente.
- Credenciais e tokens do HubSpot nunca entram na conversa.

## Critério de qualidade

Pronto quando cada propriedade tem origem, cada ponto da régua tem lista e workflow próprios, o pagamento tira o cliente da régua automaticamente, o que exige decisão virou tarefa para uma pessoa, e os limites do assistente estão escritos.

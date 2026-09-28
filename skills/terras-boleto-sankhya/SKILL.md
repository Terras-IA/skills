---
name: terras-boleto-sankhya
version: 1.0.0
access: free
category: financeiro
description: Planeja emissão, envio, acompanhamento e cancelamento de boleto de cliente pelo ERP Sankhya (Boleto Rápido por API), com checagem antes de emitir e o que depende de aprovação.
keywords: [sankhya, sankia, sankya, boleto rapido, emitir boleto, gerar boleto, segunda via do boleto, cancelar boleto, link do boleto]
---

# Boleto de cliente pelo Sankhya

## Descrição

Organiza o ciclo do boleto de **contas a receber** emitido pelo ERP Sankhya: o que conferir antes de emitir, como o boleto chega ao cliente, como acompanhar o registro no banco, e quando cancelar ou reemitir. O foco é a automação que tira a pessoa do "tela a tela" (gerar o boleto, copiar o link, montar o envio) sem tirar dela a decisão.

Esta instrução é um guia operacional. **O motor não acessa o Sankhya**: não emite, não consulta, não cancela. Os dados chegam colados na conversa, e a saída é um plano, uma checagem ou um texto para uma pessoa executar e revisar. Boleto de fornecedor (contas a pagar) é outro assunto: ver a rotina de contas a pagar.

## Quando usar

- Desenhar o fluxo de emissão e envio de boleto de cliente a partir do Sankhya.
- Conferir um lote antes de emitir (o erro mais caro é cobrar o valor ou o cliente errado).
- Montar a mensagem de envio com o link do boleto e a nota fiscal.
- Decidir entre cancelar, reemitir, prorrogar ou mandar segunda via.
- Especificar para a equipe técnica o que uma integração com a API do Sankhya precisa fazer.

## Como funciona

### O que se sabe da emissão por API

- O **Boleto Rápido API** (Sankhya Fintech) registra o boleto direto na API do banco, **sem arquivo de remessa e retorno**. Os bancos documentados incluem Banco do Brasil e Itaú.
- A ativação pede dados da conta de cobrança (no Banco do Brasil: convênio, carteira e modalidade) e credenciais geradas no portal de desenvolvedores do banco. No Itaú, a documentação pede chave PIX cadastrada e o parceiro Sankhya habilitado.
- O Sankhya tem tela de **acompanhamento dos boletos gerados pela API**, com emissão, alteração e cancelamento de cada um.
- Integração de sistema externo passa pelo **API Gateway** do Sankhya (portal developer.sankhya.com.br).

Tudo isso muda por versão e por contrato do cliente: **confirme na documentação da versão instalada** antes de especificar qualquer chamada. Não invente endpoint, campo ou código de retorno.

### Inputs esperados

Por título: cliente (referência interna, não CPF/CNPJ em texto livre), número da nota ou do pedido, valor, vencimento, conta de cobrança/banco, canal de envio disponível (e-mail, WhatsApp) e situação atual (a emitir, emitido, registrado, enviado, pago, cancelado).

Antes de processar, confirme: a **regra de emissão** (na venda, no faturamento, por lote diário), quem aprova o lote, a conta de cobrança de cada empresa/filial, e se a nota fiscal sai junto com o boleto.

### Passo a passo

1. **Conferir antes de emitir.** Por título: o valor bate com a nota? o vencimento respeita a condição de pagamento? o cliente está com cadastro de cobrança completo (e-mail, telefone do financeiro)? há disputa aberta ou crédito a abater? Título que falha em qualquer item **não entra no lote**: vai para a lista de pendências com o motivo.
2. **Emitir em lote aprovado.** O lote conferido tem um aprovador nomeado. Emitir é efeito financeiro no banco: não acontece por inferência da conversa.
3. **Confirmar o registro.** Boleto emitido não é boleto registrado. Só envie depois de o banco confirmar (tela de acompanhamento); link de boleto não registrado gera pagamento recusado e retrabalho.
4. **Montar o envio.** Uma mensagem por cliente com: quem envia, o documento (nota), o valor, o vencimento, o link do boleto e a nota fiscal anexa ou em link. Uma ação pedida: pagar até a data.
5. **Fechar o dia com relatório.** Emitidos, registrados, enviados, falhas (com motivo) e pendências de conferência. É esse relatório que alimenta a régua de cobrança do dia seguinte.
6. **Alteração, cancelamento e segunda via.**
   - Valor ou vencimento errado: cancelar e reemitir, e avisar o cliente que o boleto anterior não vale.
   - Cliente perdeu o boleto: segunda via do **mesmo** título (não um título novo).
   - Prorrogação: é decisão de quem tem alçada, com encargo ou sem, registrada no título.

### Casos de borda

- **Pago em duplicidade** (pagou o cancelado e o novo): trate como devolução, com aprovação; nunca compense em silêncio no próximo título.
- **Boleto registrado mas não enviado** porque o contato do cliente estava errado: corrija o cadastro antes de reenviar; reenviar para o mesmo endereço repete a falha.
- **Falha de API do banco** no meio do lote: não reemita o lote inteiro. Separe o que registrou do que não registrou, pela tela de acompanhamento, e reprocesse só a diferença; reemitir tudo cria duplicata.
- **Nota fiscal cancelada** depois do boleto: o boleto tem de ser cancelado junto, e o cliente avisado.

Em qualquer caso de borda, preserve a saída com "pendente" ou "não verificado", com o motivo e quem decide.

## Artefato de saída

Conforme o pedido: (a) checagem de lote, com títulos aprovados para emissão e pendências com motivo; (b) especificação da integração, com etapas, dados de entrada e saída, pontos de aprovação e o que conferir na documentação do Sankhya; (c) mensagens de envio prontas por cliente; ou (d) relatório do dia.

## Exemplo de uso

### Input fictício

(dados fictícios, todos MOCK)

Lote MOCK de três notas: Cliente Alfa, NF 1001, R$ 4.200,00, vence em 10 dias, cadastro completo; Cliente Beta, NF 1002, R$ 780,00, e-mail de cobrança vazio; Cliente Gama, NF 1003, valor do boleto R$ 15.000,00 contra nota de R$ 1.500,00.

### Output esperado

Saída MOCK: Alfa aprovado para o lote. Beta pendente (sem contato de cobrança: emitir resolve nada se o boleto não chega). Gama bloqueado (valor diverge da nota em 10 vezes: provável erro de digitação, conferir antes de qualquer emissão). Relatório: 1 apto, 2 pendências com responsável.

## Governança

- Emitir, cancelar, prorrogar e devolver são efeitos financeiros: sempre com aprovação humana nominal.
- Dado de cobrança é sensível: circula entre o financeiro e o dono da relação.
- Credenciais de banco e do Sankhya nunca entram na conversa nem em texto de especificação.

## Critério de qualidade

Pronto quando cada título tem situação clara (apto, pendente com motivo, bloqueado), o envio só acontece depois do registro confirmado, o relatório do dia fecha com os números, e nenhuma chamada de API foi descrita sem a ressalva de conferir na documentação da versão do cliente.

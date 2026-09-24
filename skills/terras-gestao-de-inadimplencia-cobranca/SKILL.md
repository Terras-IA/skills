---
name: terras-gestao-de-inadimplencia-cobranca
version: 1.0.0
access: free
category: financeiro
description: Monta a régua de cobrança de D-3 a D+15 com o tom de cada contato, os encargos do contrato e o ponto de decisão.
keywords: [cobrança, cobrar, inadimplência, título vencido, não pagou, atraso, régua]
---

# Gestão de inadimplência e cobrança

## Descrição

Pega uma carteira de títulos vencidos ou a vencer e devolve a régua: quem recebe qual contato, quando, por qual canal, com que texto e com que valor. Separa o atraso operacional (boleto que não chegou, nota errada, aprovação parada) do atraso de capacidade de pagamento — porque a resposta certa para cada um é diferente, e tratar os dois igual queima relação por nada.

Esta instrução é um guia operacional: não negativa, não protesta, não aplica desconto, não renegocia e não decide corte de serviço. Trabalhe com o contrato, a política de crédito aprovada e a revisão de quem responde pela carteira. Quando um dado não existir, escreva "não informado" e diga qual decisão fica bloqueada.

**A régua é produzida, não executada.** O motor não consulta títulos em sistema de gestão, não sabe quem pagou e não dispara mensagem sozinho. Os títulos chegam colados na conversa e a saída é um plano com textos prontos, para uma pessoa revisar e enviar.

## Quando usar

- Montar a rotina de cobrança de um período e saber a quem falar primeiro.
- Escrever o texto de um contato específico sem soar genérico nem agressivo.
- Calcular o valor atualizado de um título em atraso, com o encargo previsto em contrato.
- Decidir quando um caso sai da régua e vira decisão (jurídico, corte, renegociação).
- Revisar uma régua existente que não está convertendo.

## Como funciona

### Inputs esperados

Por título: cliente, documento, valor original, vencimento, dias de atraso, canal de contato disponível e histórico dos contatos já feitos.

Antes de processar, confirme: a **cláusula contratual de encargos** (multa, juros de mora, correção — em número, não "o de praxe"), a política de desconto e de negativação, quem é o dono da relação com o cliente, e se existe disputa aberta sobre a entrega. Cobrar cliente que abriu reclamação legítima sem saber disso é o erro mais caro desta rotina.

Reorganize texto solto numa tabela com nome, tipo, exemplo, origem e regra de validação, e confirme valor, vencimento e dias de atraso antes de concluir.

### Passo a passo

1. **Separar antes de escrever.** Três pilhas: atraso operacional (documento errado, boleto não recebido, aprovação interna do cliente parada), atraso de fluxo (o cliente paga, só que depois), e risco real (parou de responder, atraso recorrente, sinais públicos de dificuldade). Cada pilha tem régua própria.
2. **Priorizar por valor e por risco, não por data.** Um título de R$ 80.000 com 5 dias pesa mais que dez de R$ 800 com 20 — mas os dez de R$ 800 do mesmo cliente somam e mudam a classificação dele.
3. **Aplicar a régua.**
   - **D-3 (preventivo)** — lembrete neutro, sem cobrança no tom: confirma que o documento chegou e que a data está no radar. É o contato que **evita** o atraso operacional.
   - **D+1** — aviso factual: venceu, segue o dado para pagamento. Sem encargo ainda, e sem julgamento: um dia é quase sempre operacional.
   - **D+5** — contato ativo por canal com resposta (telefone ou mensagem), com pergunta aberta: "há algo travando?". É aqui que o atraso operacional aparece e se resolve.
   - **D+10** — formalização: valor atualizado com encargos, prazo para regularização e menção ao que o contrato prevê. Tom firme, sem ameaça.
   - **D+15** — ponto de decisão: **sai da régua**. Encaminha para renegociação, suspensão ou jurídico, conforme a política. Repetir a mesma cobrança depois de D+15 ensina o cliente que não há consequência.
4. **Calcular o valor atualizado.** Valor original + multa (percentual único sobre o principal) + juros de mora (ao mês, proporcional aos dias) + correção, se prevista. Mostre a conta em linhas separadas: valor cobrado sem memória de cálculo é contestado e atrasa mais.
5. **Escrever o texto.** Um contato por vez, com o nome de quem fala, o documento, o valor, a data e **uma** ação pedida. Mensagem com duas perguntas recebe zero respostas.
6. **Registrar o combinado.** Promessa de pagamento tem data e valor, e vira o próximo ponto da régua. Promessa quebrada muda a classificação do cliente — não reinicia a régua do zero.

### Casos de borda

- **Disputa aberta sobre a entrega.** Suspenda a régua de encargos e trate como caso comercial. Cobrar por cima de reclamação legítima transforma atraso em ruptura.
- **Cliente estratégico.** A régua não muda; o **canal** muda — o contato passa pelo dono da relação, não pelo financeiro. Isso se decide antes, não no meio.
- **Valor pequeno com custo de cobrança maior que o título.** Diga isso com número e recomende a decisão (baixa, acúmulo até um mínimo), em vez de rodar a régua no automático.
- **Atraso recorrente do mesmo cliente.** É assunto de política de crédito, não de cobrança. Sinalize: o problema não se resolve com mais uma mensagem.
- **Contrato sem cláusula de encargos.** Não invente percentual nem use "o usual". Cobre o principal e marque a lacuna contratual como pendência.

Em qualquer caso de borda, preserve a saída com "pendente", "não observado" ou "base insuficiente", com limitações e responsável pela revisão.

## Artefato de saída

Plano de cobrança do período com: a carteira separada nas três pilhas com valor somado em cada; por título, o ponto da régua, o canal, a data do contato e o texto pronto; a memória de cálculo do valor atualizado onde houver encargo; e a lista dos casos que saíram da régua, com a decisão que cada um espera e de quem.

O plano orienta o envio; qualquer mensagem, desconto, negativação ou corte depende de aprovação humana.

## Exemplo de uso

### Input fictício

(dados fictícios — todos os nomes e valores são MOCK)

Carteira MOCK com três títulos: Cliente Alfa, R$ 12.500,00, 2 dias de atraso, primeiro atraso em 14 meses; Cliente Beta, R$ 900,00, 12 dias, terceiro atraso no ano; Cliente Gama, R$ 64.000,00, 16 dias, sem resposta em dois contatos. Contrato MOCK: multa 2% e juros 1% ao mês.

### Output esperado

Saída MOCK: Alfa entra como atraso operacional em D+1, lembrete neutro, sem encargo, com a hipótese de boleto não recebido. Beta recebe o contato de D+10 com valor atualizado (R$ 900,00 + R$ 18,00 de multa + R$ 3,60 de juros proporcionais a 12 dias = R$ 921,60) **e** uma sinalização de que o padrão recorrente é assunto de política de crédito, não de régua. Gama **sai da régua**: ponto de decisão, com o valor atualizado, o histórico de silêncio e o encaminhamento esperado nomeado.

O exemplo é simulação operacional: não é dado real e serve para mostrar o nível de detalhe esperado.

## Governança

- Cobrança não expõe nem constrange: nada de cobrar em canal coletivo, mencionar a dívida a terceiros ou usar tom de ameaça. Além de errado, invalida a cobrança.
- Não anuncie negativação, protesto ou corte que não estejam decididos e previstos em contrato.
- Encargo só se cobra com a cláusula na mão, e com a conta visível.
- Dado de inadimplência é sensível: circula entre quem trata a carteira e o dono da relação, não além.
- Promessa de pagamento registrada vale como combinado; renegociar prazo ou valor é decisão de quem tem alçada, não da régua.

## Critério de qualidade

A entrega está pronta somente quando traz a carteira separada por tipo de atraso com valores somados, o ponto da régua de cada título, a memória de cálculo de cada valor atualizado, o texto de cada contato com uma única ação pedida, os casos que saíram da régua com o destinatário da decisão, as limitações e o próximo passo. Régua que só tem cobrança depois do vencimento está incompleta: o contato preventivo é o que mais evita atraso.

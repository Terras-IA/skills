---
name: terras-conferencia-fechamento-folha
version: 1.0.0
access: free
category: dp-rh
description: Confere o fechamento da folha antes do envio — horas extras, adicional noturno, faltas e encargos — apontando o que não fecha por matrícula, sem afirmar alíquota nem regra de convenção de memória.
keywords: [fechamento de folha, folha de pagamento, hora extra, adicional noturno, banco de horas, inss fgts, dsr, faltas e atrasos]
---

# Conferência de fechamento de folha

## Descrição

Cruza o espelho de ponto, os eventos lançados e a prévia da folha, e devolve **o que não fecha, por colaborador, com o número dos dois lados**. O objetivo não é fechar a folha — é impedir que ela seja enviada com divergência que ninguém viu, porque depois do envio a correção é retificação.

**Regra de convenção coletiva, alíquota de encargo e percentual de adicional não são afirmados aqui.** Eles mudam por categoria, por acordo, por data-base e por faixa; a empresa informa, e esta instrução confere coerência: se a base bate, se a conta fecha, se o evento apareceu onde deveria. Sem os parâmetros informados, a linha é "não verificável" com o motivo — nunca um número plausível.

**Identidade:** trabalhe com **matrícula ou referência opaca**, nunca com CPF, RG, endereço, conta bancária ou dado de saúde. Se o material colado trouxer esses campos, não os repita na saída. Nome completo só quando a pessoa que conduz pedir explicitamente, e ainda assim fora de qualquer tabela que vá ser arquivada.

## Quando usar

- No fechamento mensal, antes de enviar a folha para processamento.
- Depois de mês atípico: feriado prolongado, mudança de escala, greve, admissões em lote.
- Ao investigar reclamação de colaborador sobre valor recebido.
- Antes de homologar rescisão, para conferir o histórico recente.
- Ao trocar de sistema de ponto ou de folha, para comparar os dois resultados.

## Como funciona

### Inputs esperados

Espelho de ponto do período (por matrícula), eventos lançados (extras, faltas, atestados, adicionais, descontos), prévia da folha e, da empresa: **jornada contratual por grupo**, **regras da convenção aplicável** (percentuais de extra, janela do adicional noturno, tratamento de DSR), política de banco de horas e a tabela de encargos vigente.

Confirme antes de calcular: período exato (início e fim, inclusive), quais matrículas entram, e se há banco de horas ativo. Sem a jornada contratual, hora extra não é apurável — diga isso e pare.

### Passo a passo

1. **Conferir o universo.** Quantas matrículas ativas no período × quantas na prévia da folha. Admissão, demissão e afastamento no meio do mês são as fontes clássicas de sobra e de falta; liste-as nominalmente por matrícula.
2. **Normalizar o ponto.** Marcações por dia, jornada esperada por dia, saldo diário. Dia sem marcação e dia com marcação ímpar viram pendência **antes** de virar cálculo — saldo calculado sobre ponto incompleto é ficção.
3. **Apurar extras por faixa.** Separe por percentual conforme a regra informada (dia útil, domingo, feriado). Some por faixa, não em bloco: a folha paga por faixa, e a divergência aparece exatamente aí.
4. **Apurar adicional noturno.** Use a janela informada e trate a hora noturna reduzida se a convenção previr. Quando a janela não for informada, marque "não verificável" — não assuma a regra geral.
5. **Conferir faltas, atrasos e DSR.** Falta justificada com atestado não desconta DSR; falta injustificada normalmente sim. Aplique a regra informada e registre a origem de cada tratamento.
6. **Cruzar com os eventos lançados.** Cada divergência vira uma linha com matrícula, evento, valor do ponto, valor da folha, diferença e provável causa (ponto, lançamento ou regra).
7. **Conferir encargos por coerência.** base × alíquota informada = valor previsto. Aqui você confere aritmética e presença, não a alíquota em si.
8. **Fechar por exceção.** A saída lista quem tem divergência, não quem está correto. Folha com 300 matrículas e 7 problemas deve caber numa tela.

## O que esta skill não faz

Não fecha, não envia, não transmite eSocial, não calcula rescisão (há simulação própria para isso) e não decide sobre falta, atestado ou advertência. Não afirma percentual de convenção nem alíquota de encargo. Não trata dado de saúde: atestado entra como "há atestado", nunca com o diagnóstico ou o CID.

## Saída esperada

Tabela de exceções (matrícula · evento · valor no ponto · valor na folha · diferença · causa provável · origem da regra), lista de pendências de ponto que impedem apuração, e uma linha final com o que bloqueia o envio hoje. Sem nome, sem CPF, sem dado de saúde.

---
name: terras-apuracao-retencoes-federais
version: 1.0.0
access: free
category: fiscal
description: Confere se as retenções federais na fonte de uma nota de serviço foram aplicadas, dispensadas ou esquecidas, usando as alíquotas e limites informados pela empresa, nunca de memória.
keywords: [retencao na fonte, retencoes federais, irrf, pis cofins csll, csrf, inss retido, darf, imposto retido]
---

# Apuração de retenções federais (tomador de serviço)

## Descrição

Dada uma nota de serviço e o enquadramento informado pela empresa, aponta **quais retenções deveriam aparecer, quais apareceram e quais não batem**. Serve ao tomador, que é quem responde pela retenção não feita, e ao prestador, que precisa saber quanto vai receber líquido.

**As alíquotas, os limites de dispensa e as regras de acumulação não são afirmadas aqui.** Elas dependem do serviço, do regime de quem presta, do valor e do período, e mudam por norma. A empresa (ou o contador) informa; esta instrução confere **coerência**: se a base foi a certa, se a conta fecha, se o código de recolhimento corresponde ao que foi retido, e se algo previsto em contrato não apareceu na nota. Sem a tabela informada, a saída é "não verificável" com o motivo — não um número inventado.

## Quando usar

- Antes de pagar uma nota de serviço, para saber o líquido correto e o que recolher.
- Ao receber contestação do prestador sobre valor retido.
- Ao fechar o mês e conferir se o que foi retido corresponde ao que será recolhido.
- Quando o contrato prevê retenção e a nota veio sem destaque (ou o contrário).
- Para reconstituir uma retenção antiga e avaliar recolhimento em atraso.

## Como funciona

### Inputs esperados

Da nota: valor bruto, base de cálculo de cada tributo, retenções destacadas, descrição e código do serviço, data de emissão e de pagamento previsto. Da empresa: **regime do prestador**, **natureza do serviço**, **tabela de alíquotas e limites vigente** e o que o contrato prevê. Do período: houve outras notas do mesmo prestador no mês (a acumulação muda o resultado quando há limite de dispensa).

Sem a tabela vigente e sem o regime do prestador, **nenhuma retenção é conferível** — diga isso na primeira linha da saída e pare de calcular.

### Passo a passo

1. **Separar por tributo.** Cada retenção tem base, alíquota, código de recolhimento e prazo próprios; tratá-las em bloco é o que produz erro silencioso. Monte uma linha por tributo.
2. **Determinar a base de cada uma.** A base nem sempre é o valor bruto (materiais, subempreitada e descontos podem alterá-la). Use a regra informada; se não houver, marque "base não definida" e siga para o próximo tributo.
3. **Recalcular.** base × alíquota informada = valor esperado. Compare com o destacado na nota. Diferença até um centavo é arredondamento; acima disso, é divergência com número.
4. **Checar dispensa.** Quando a empresa informar limite de dispensa, verifique contra o valor da nota **e** contra o acumulado do prestador no período informado. Dispensa aplicada sobre nota isolada, ignorando acumulação, é o erro mais comum desta apuração.
5. **Conferir o código de recolhimento.** O código informado corresponde ao tributo e à natureza do serviço declarados? Código errado gera recolhimento que não quita a obrigação.
6. **Confrontar com o contrato.** Retenção prevista e ausente na nota, ou destacada sem previsão, entra como divergência de contrato — não como erro de cálculo. São problemas de donos diferentes.
7. **Fechar o líquido.** Valor bruto − retenções conferidas = líquido a pagar, com a ressalva explícita de quais linhas ficaram "não verificáveis".

## O que esta skill não faz

Não recolhe, não emite DARF, não consulta a Receita e não decide enquadramento. Não afirma alíquota, limite nem prazo de recolhimento de memória. Não avalia retenção previdenciária de obra nem substituição tributária — esses casos têm regra própria e devem ir ao contador com o apontamento de que ficaram fora.

## Saída esperada

Uma tabela com tributo, base usada, origem da base, alíquota informada, valor esperado, valor destacado, divergência e status (conferido · divergente · não verificável). Abaixo dela: o líquido a pagar, a lista do que impede fechar, e uma frase dizendo que os parâmetros foram **informados pela empresa**, não verificados na fonte.

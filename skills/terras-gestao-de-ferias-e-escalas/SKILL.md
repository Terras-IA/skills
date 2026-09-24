---
name: terras-gestao-de-ferias-e-escalas
version: 1.0.0
access: free
category: dp-rh
description: Organiza períodos aquisitivo e concessivo, abono e fracionamento por equipe, e mostra onde a escala não se sustenta — com os prazos informados pela empresa, não de memória.
keywords: [periodo aquisitivo, periodo concessivo, abono pecuniario, escala de ferias, vender ferias, ferias vencidas, fracionamento de ferias]
---

# Gestão de férias e escalas

## Descrição

Monta o quadro de férias de uma equipe a partir dos períodos de cada matrícula e da necessidade de cobertura, e aponta **o que está perto de vencer, o que fere o limite de cobertura e o que depende de decisão de alguém**. Não aprova férias nem publica escala: entrega o quadro e as decisões pendentes.

**Prazos, limites de fracionamento e regras de abono não são afirmados aqui.** Dependem de legislação vigente, convenção coletiva e política interna; a empresa informa, e esta instrução organiza e confere. Sem os prazos informados, o quadro sai com as datas e **sem** classificação de vencimento — dizer "vence em tal dia" a partir de memória é o erro que gera passivo.

**Identidade:** matrícula ou referência opaca. Nome completo só se a pessoa que conduz pedir, e nunca junto de dado pessoal adicional.

## Quando usar

- Planejar a escala de férias do ano ou do semestre para uma equipe.
- Identificar quem está com período vencido ou perto de vencer.
- Avaliar pedido de fracionamento ou de venda de dias.
- Verificar se a escala proposta deixa a operação descoberta.
- Preparar o programa de férias antes de comunicar aos colaboradores.

## Como funciona

### Inputs esperados

Por matrícula: data de admissão, períodos aquisitivos já completados, férias já gozadas (datas e dias), saldo, afastamentos que suspendem contagem. Da empresa: **regra de prazo aplicável**, limites de fracionamento, política de abono, e a **cobertura mínima** de cada função ou turno.

Sem cobertura mínima declarada, o conflito de escala não é apurável — o quadro sai só com o eixo individual, dizendo isso.

### Passo a passo

1. **Montar a linha do tempo por matrícula.** Admissão → períodos aquisitivos → o que foi gozado → saldo atual. Dado incompleto vira pendência antes de virar classificação.
2. **Classificar pelos prazos informados.** Em dia, a vencer no horizonte, vencido. Use exclusivamente os prazos que a empresa informou e registre essa origem ao lado da classificação.
3. **Cruzar com a necessidade de cobertura.** Por função e por turno, quantos podem estar fora ao mesmo tempo. Onde a escala proposta ultrapassa o limite, aponte a janela e quem está nela.
4. **Tratar fracionamento.** Cada pedido contra os limites informados: número de partes, tamanho mínimo, restrições de início. O que não couber é apontado com a regra que impede, não recusado.
5. **Tratar abono.** Proporção e prazo de solicitação conforme informado; marque o que já passou do prazo e o que ainda dá tempo.
6. **Ordenar por urgência real.** Vencido primeiro, depois a vencer sem data marcada, depois conflito de cobertura, depois pedidos pendentes. Quadro que não ordena obriga a pessoa a ordenar de novo.
7. **Fechar com as decisões pendentes**, cada uma com quem decide e até quando.

## O que esta skill não faz

Não aprova, não publica, não comunica ao colaborador e não lança nada em sistema. Não afirma prazo legal, limite de fracionamento ou percentual de abono. Não avalia justificativa de afastamento nem trata dado de saúde.

## Saída esperada

Quadro por matrícula (situação · saldo · janela proposta · classificação · origem da regra), lista de conflitos de cobertura com a janela e as matrículas envolvidas, lista de decisões pendentes com dono e prazo, e a ressalva de que prazos e limites foram **informados**, não verificados.

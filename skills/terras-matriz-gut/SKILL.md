---
name: terras-matriz-gut
description: "Prioriza problemas e demandas concorrentes com a matriz GUT: notas 1-5 ancoradas em Gravidade, Urgência e Tendência, score por produto, faixa de decisão declarada antes de pontuar, desempate fixo e plano de ataque com dono e prazo. Use quando o pedido for priorizar, ordenar uma fila, decidir por onde começar, comparar problemas ou demandas de naturezas diferentes, ou quando 'tudo é urgente' e falta critério comum. Cobre também 'qual eu resolvo primeiro'."
keywords: [gut, matriz gut, priorizacao, priorizar, gravidade, urgencia, tendencia, prioridade, criticidade, ordenar problemas, fila de demandas, por onde comecar, escala de prioridade, desempate, backlog priorizado]
version: 1.0.0
license: MIT
---

# Matriz GUT

## Descrição

Ordena problemas e demandas concorrentes por **Gravidade**, **Urgência** e **Tendência**, com notas de 1 a 5 ancoradas e score = G × U × T (1–125). O método existe para um momento específico: várias coisas parecem prioritárias e o grupo precisa de critério declarado, não de quem fala mais alto.

O que separa uma GUT que decide de uma que só organiza slide são três amarras: **âncoras por nota**, **faixa de decisão definida antes de pontuar** e **desempate fixo**. Sem elas, todo mundo pontua o próprio problema 5×5×5.

Este guia é de decisão assistida: não decide sozinho. O score ordena a conversa; a decisão é de quem responde pelo resultado.

## Quando usar

- Priorizar backlog, demandas, incidências ou gargalos achados num diagnóstico (no mapeamento de processos, ordene os problemas com esta matriz antes de desenhar soluções).
- "Tudo é urgente": cada área defende a própria demanda sem critério comum.
- Escolher o que entra no próximo ciclo e o que fica na fila.
- Comparar problemas de natureza diferente (um financeiro, um de pessoas, um de sistema) — a âncora comum é o que torna a comparação honesta.

Quando **não** usar:

- Escolher entre **soluções** para um problema já escolhido: use a matriz impacto × esforço (`terras-mapeamento-de-processos`, §10).
- A organização já tem régua própria de risco ou priorização: use a dela.
- Fila de 2 itens: a conversa resolve.

## Como funciona

1. **Declare as regras antes de pontuar**: âncoras (abaixo), faixa de leitura do score e desempate. Regra trocada depois da pontuação é ajuste de resultado.
2. **Liste os problemas em uma linha cada**, com a evidência ao lado (número, reclamação, prazo, incidente). Problema sem evidência entra como **premissa**, marcada.
3. **Pontue junto**: quem sente o problema e quem paga a conta, na mesma mesa. Notas individuais comparadas item a item; divergência de 2 ou mais pontos numa dimensão se resolve citando a âncora, não fazendo média.
4. **Calcule o score = G × U × T** (produto, não soma): nota baixa em qualquer dimensão derruba a prioridade — problema urgente, mas pouco grave, não chega ao topo.
5. **Ordene e leia pela faixa** (sugerida; o grupo pode fixar outra, antes de pontuar): ≥ 60 atacar agora · 27–59 planejar · < 27 fila.
6. **Desempate fixo G > U > T**: dano fala mais alto que pressa, pressa fala mais alto que tendência.
7. **Plano de ataque**: para os 2–3 primeiros, primeira ação, dono, prazo e como vai ser verificado. A GUT termina aqui — causa raiz e desenho de solução vêm depois (5 Porquês, mapeamento de processos).
8. **Repontue a cada ciclo**: GUT é foto. Problema resolvido sai; tendência mudou, a ordem muda.

## Âncoras de 1 a 5

| Nota | Gravidade — dano se nada for feito | Urgência — prazo real | Tendência — sem intervenção |
| --- | --- | --- | --- |
| 1 | incômodo individual, sem efeito em resultado | pode esperar um trimestre ou mais | diminui sozinha |
| 2 | retrabalho local; cliente não percebe | pode esperar no mês | estável |
| 3 | atrasa entrega ou afeta um cliente | semanas, prazo conhecido | cresce devagar (ao mês) |
| 4 | afeta o resultado do mês ou vários clientes | dias; compromisso assumido | cresce por semana, já reincidiu |
| 5 | parada de operação, risco de perder cliente/contrato ou risco legal | hoje; cada dia custa ou bloqueia outros | efeito bola de neve comprovado |

## Variante ponderada

Só com justificativa registrada (ex.: "risco legal e de imagem — Gravidade vale peso 3"): multiplique a dimensão pelo peso antes do produto e leve o peso no artefato. Peso sem registro é vício — o peso vira "o que o grupo achou".

## Erros comuns

| Erro | Correção |
| --- | --- |
| Pontuar sem âncoras | âncoras declaradas antes; toda nota justificada pela âncora |
| Somar em vez de multiplicar | score = G × U × T |
| Fixar faixa e desempate depois de ver os scores | regras antes da pontuação, sempre |
| Média silenciosa entre notas divergentes | divergência ≥ 2 pontos se resolve pela âncora, na mesa |
| Time só de quem sente, ou só de quem paga | os dois juntos; um sem o outro vira desabafo ou orçamento |
| Usar GUT para escolher solução | GUT ordena problemas; impacto × esforço ordena intervenções |
| Congelar a foto | repontuar por ciclo; resolvido sai |

## O que este método não faz

- Não inventa evidência: problema sem fonte entra marcado como premissa.
- Não decide: o score ordena a conversa; decisão é de quem responde pelo resultado.
- Não substitui causa raiz: diz o que atacar primeiro, não por que o problema existe.

## Arquivos

- `templates/matriz-gut.md` — o artefato: faixa declarada, tabela de problemas com evidência, notas de pontuação, plano de ataque com dono e verificação.

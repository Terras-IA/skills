---
name: terras-analise-swot
version: 1.0.0
access: free
category: gestao
description: Faz SWOT rastreável e terminada em ação: fonte obrigatória por item (sem fonte vira hipótese marcada), itens priorizados por quadrante e fechamento em cruzamentos TOWS com ação, dono, verificação e o que não fazer.
keywords: [swot, tows, forcas, fraquezas, oportunidades, ameacas, analise de cenario, posicao competitiva, planejamento estrategico]
---

# Análise SWOT

## Descrição

SWOT organiza **forças** e **fraquezas** (internas, de hoje) contra **oportunidades** e **ameaças** (externas, a vir). O quadro de quatro quadrantes é o meio da análise, não o fim: uma SWOT que termina no quadrante cheio não é análise, é slide.

O que esta skill acrescenta ao pedido genérico "faça uma SWOT":

1. **Evidência por item** — cada linha cita a fonte; o que não tem fonte entra como hipótese marcada, com o teste que a confirmaria.
2. **Priorização dentro do quadrante** — 3 a 5 itens por quadrante, por impacto no objetivo declarado; listão é descuido, não profundidade.
3. **Fechamento em TOWS** — cruzamentos SO/WO/ST/WT terminam em ação com dono, horizonte e verificação, e em um "o que NÃO fazer".

Guia de decisão assistida: não decide sozinho estratégia, investimento ou posicionamento. Trabalha com o contexto, os dados disponíveis e a revisão de quem responde pelo negócio.

## Quando usar

- Preparo de decisão estratégica: entrar ou não num segmento, lançar ou não uma linha, investir ou não numa frente.
- Revisão trimestral de posicionamento; briefing antes de plano comercial ou de investimento.
- Comparar cenários com o mesmo método ("vale entrar no segmento X?").

Quando **não** usar:

- Problema operacional de processo: use mapeamento de processos (mapa, números, plano).
- Ordenar fila de demandas: use a matriz GUT.
- Zero acesso a dado e a relato: o máximo honesto é uma lista de hipóteses — e este método exige que ela venha marcada como hipótese.

## Unidade de análise (declare antes de tudo)

SWOT de quê? De quem? Em que horizonte? Empresa, produto, vertical, área; 6 meses ou 3 anos. Quadrante sem unidade declarada mistura nível e o cruzamento TOWS perde sentido. Formato: "<o que> no <segmento/mercado>, horizonte <período>" (ex.: "TerrasIA no segmento contábil, horizonte 12 meses").

## Regras de classificação

- **Interno** (a organização controla) × **externo** (acontece fora), cruzado com **positivo** × **negativo**: Força = interno + positivo · Fraqueza = interno + negativo · Oportunidade = externo + positivo · Ameaça = externo + negativo.
- Confusões comuns, com o teste:
  - "Não temos CRM" é **fraqueza** (interno), não ameaça.
  - "Concorrente lançou X" é **ameaça** (externo), mesmo quando expõe nossa fraqueza.
  - "Regulação nova" é ameaça para quem perde e oportunidade para quem já cumpre — classifique do ponto de vista da unidade de análise.
- Item genérico não entra. Force a forma "**X em relação a Y**": "churn 4% contra 9% do setor — força" vale; "time dedicado" é enfeite.

## Regras de evidência

- Cada item traz a fonte entre colchetes: `[métrica interna]`, `[documento]`, `[relato do cliente, data]`, `[pesquisa, link]`.
- Sem fonte = **hipótese**, marcada com ⚠ e acompanhada do teste que a confirmaria ("⚠ hipótese — conferir churn nos últimos 6 meses").
- Número vale mais que adjetivo: "lead time 40% acima do prometido" > "processo lento".
- 3–5 itens priorizados por quadrante; o restante vai para apêndice.

## Priorização dentro do quadrante

Ordene por impacto no objetivo da unidade de análise declarada. Quando a comparação for difícil, pontue os itens com a matriz GUT — gravidade, urgência e tendência servem para ameaças e fraquezas quase sem tradução.

## TOWS — a análise termina em cruzamento

| | **O**portunidades | **T** ameaças |
| --- | --- | --- |
| **S** forças | **SO** — usar a força para capturar a oportunidade | **ST** — usar a força para neutralizar a ameaça |
| **F** fraquezas | **WO** — corrigir a fraqueza que bloqueia a oportunidade | **WT** — reduzir a fraqueza e se proteger da ameaça (defensiva) |

- Um cruzamento por vez, partindo dos itens **priorizados** — não o produto cartesiano inteiro.
- Saída mínima por cruzamento escolhido: ação, dono, horizonte, verificação. Cruzamento sem ação é quadrante decorativo.
- Feche com o "o que NÃO fazer": a SWOT honesta também corta frente.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Preencher quadrante sem fonte | item sem fonte vira hipótese marcada, com teste de confirmação |
| Confundir interno e externo | teste: a organização controla isso? |
| Listão de 15 itens por quadrante | 3–5 priorizados; resto em apêndice |
| Parar no quadrante | TOWS com ação, dono e verificação |
| Misturar unidades de análise | declarar escopo e horizonte antes de listar |
| Adjetivo sem número | forçar a forma "X em relação a Y" |
| Revisar nunca | refazer por trimestre ou no gatilho (movimento de mercado, perda de cliente, regulação) |

## O que este método não faz

- Não cria dado que não existe: lacuna vira hipótese com teste de confirmação.
- Não decide estratégia: entrega cruzamentos priorizados e recomendação; a decisão é de quem responde pelo negócio.
- Não substitui análise quantitativa quando o dado existe (mercado, financeiro, métrica própria).

## Arquivos

- `templates/swot.md` — o artefato: escopo declarado, quadrantes com fonte e prioridade, TOWS com ação e dono, o que não fazer.

---
name: terras-user-research
description: Pesquisa com usuários de ponta a ponta: plano de estudo, roteiro de entrevista, triagem, síntese em relatório com achados, personas e oportunidades, e survey quantitativo. Use para pesquisa com usuários, entrevistas, roteiro, survey ou análise de transcrições.
keywords: [user research, pesquisa com usuarios, entrevista, roteiro, survey, sintese, personas, descoberta, qualitativa, quantitativa]
homepage: https://github.com/cookiy-ai/user-research-skill
license: MIT
---

# Pesquisa com usuários, de ponta a ponta

Fonte única: `skills/terras-user-research/` no repositório `terrasia-skills`, adaptada de `cookiy-ai/user-research-skill` (MIT, ver `LICENSE`) — sem a integração com a plataforma Cookiy.

Encaminhe para o fluxo certo conforme a intenção do pedido.

## Roteamento

Infira a intenção/etapa pelo contexto.

| Intenção | Rota |
|---|---|
| Quer plano de estudo, questionário de triagem ou guia de discussão | [Rota A: Planejar um estudo](#rota-a-planejar-um-estudo) |
| Tem transcrições/anotações e precisa de relatório | [Rota B: Sintetizar](#rota-b-sintetizar-um-relatório) |
| Outro | [Orquestração](#orquestração) |

Se estiver ambíguo, faça uma pergunta de esclarecimento.

### Orquestração

Quando o usuário tem um objetivo de pesquisa mas não especificou qualitativa vs quantitativa, ajude a decidir — ou escolha as duas em sequência.

- **Qualitativa (entrevistas):** vá para a Rota A.
- **Quantitativa (survey):** a Rota A cobre o design do questionário; para análise de respostas numéricas, adapte o método de síntese da Rota B.

---

## Rota A: Planejar um estudo

**Quando:** o usuário quer plano de pesquisa, guia de discussão/entrevista ou questionário de triagem.

**Faça:** siga [`references/qualitative-research-planner/qualitative-research-planner.md`](references/qualitative-research-planner/qualitative-research-planner.md).

Ao terminar o plano, ofereça os próximos passos de condução do estudo (recrutamento, agendamento, roteiro de moderação) que façam sentido para o contexto.

---

## Rota B: Sintetizar um relatório

**Quando:** o usuário tem transcrições/anotações brutas de entrevistas e precisa de análise.

**Faça:** siga [`references/synthesize-research-report/synthesize-research-report.md`](references/synthesize-research-report/synthesize-research-report.md) — cinco fases fixas, do batch de familiarização ao relatório final, com codebook iterativo, temas, personas orientadas a dados, achados priorizados e banco de evidências.

---

## Regras de qualidade (valem para as duas rotas)

- **Evidência antes de conclusão:** todo achado sai dos dados; anote a fala ou o trecho que o sustenta.
- **Sem invenção de respondente:** persona e citação precisam existir no material coletado.
- **Entregável estruturado:** relatório com resumo executivo, método, achados priorizados, oportunidades e apêndice de evidências.
- **Idioma:** escreva no idioma do pedido.

---
name: terras-educacao-corporativa
description: "Aplica 26 prompts de educação corporativa (derivados do ebook da Alun Business) para gerar estratégia de T&D, diagnóstico de necessidades, mapa de competências, trilhas, programas, planos de aula e indicadores de impacto. Use quando o pedido envolver educação corporativa, treinamento corporativo, T&D, L&D, trilha de aprendizagem, mapa de competências, ROI de treinamento, workshop ou plano de aula corporativo. Corporate education, learning and development, training design."
keywords: [educação corporativa, educacao corporativa, treinamento, t&d, trilha de aprendizagem, jornada de aprendizagem, competências, competencias, diagnóstico de necessidades, design instrucional, plano de aula, workshop, avaliação de treinamento, kirkpatrick, bloom, onboarding, blended, corporate education, learning and development, training design]
---

# Educação corporativa — 26 prompts aplicados

## Objetivo

Aplicar a biblioteca de 26 prompts (catalogados em
`references/catalogo-prompts.md`, derivada do ebook da Alun Business) para
produzir entregáveis de educação corporativa: estratégia de T&D, diagnóstico de
necessidades, mapa de competências, trilhas, programas, planos de aula,
indicadores de impacto e casos de uso de IA. O valor não é citar o prompt: é
rodar o prompt certo, com contexto real, e devolver um entregável que sobrevive
à reunião com o gestor do negócio.

## Onde está instalada

Fonte única: `skills/terras-educacao-corporativa/` no repositório
`terrasia-skills`. Cada agente enxerga a skill por um link simbólico criado
pelo `scripts/instalar.sh` do repositório, então a edição se faz lá e vale para
todos. Nos comandos abaixo, `$SKILL_DIR` é a pasta onde este `SKILL.md` está.
O catálogo completo dos prompts fica em `references/catalogo-prompts.md` —
leia o prompt inteiro de lá antes de rodar.

## Regra dura: diagnóstico antes de desenho

- Pedido de solução (trilha, programa, workshop, plano de aula) sem contexto
  mínimo (público, objetivo de negócio, restrições de tempo/orçamento/formato)
  recebe **2-3 perguntas antes da resposta** — nunca um questionário, nunca
  premissas assumidas. O teste vermelho registrou a racionalização: "tem o
  suficiente para um rascunho" — o rascunho sai genérico e é refugo.
- Se o usuário descreve dor num público (ex.: rotatividade de operadores) e
  pede solução para outro (ex.: trilha comercial), **sinalize o descasamento
  antes de desenhar** e proponha como conectar os dois. Dor relatada com mais
  vividez não vira rodapé "bônus".
- Pedidos grandes quase sempre são **cadeia**: diagnóstico (04/05) →
  competências (07) → trilha/programa (10/13) → indicadores (20). Anuncie a
  cadeia antes de começar.

## Como trabalhar

1. **Classificar o pedido** no mapa de decisão abaixo e abrir o prompt
   correspondente em `references/catalogo-prompts.md`.
2. **Montar o bloco de contexto**: só o necessário para o prompt; nada de dado
   sensível (salários, folha, dados pessoais) no texto passado ao modelo.
3. **Rodar o prompt** mantendo sua estrutura de saída (persona, entregáveis
   enumerados, critério de fechamento) — é ela que impede resposta genérica.
4. **Aplicar as adaptações da casa** (abaixo) na resposta.
5. **Iterar na mesma conversa** com feedback específico ("fase 2 sem bullets
   de tempo"; "troque role-play por simulação com pipeline real") em vez de
   recomeçar do zero.

## Mapa de decisão

| Pedido do usuário | Prompt |
|---|---|
| Estratégia/agenda de T&D a partir do negócio | 01 |
| Frentes de atuação da área de educação | 02 |
| Priorizar demandas / matriz de priorização | 03 |
| Mapear necessidades / diagnóstico preliminar | 04 |
| Gaps por público ou nível hierárquico | 05 |
| Roteiro de entrevista com stakeholders | 06 |
| Mapa de competências de um público | 07 |
| Níveis de proficiência (junior→referência) | 08 |
| Justificar investimento em competências | 09 |
| Trilha orientada a objetivo de negócio | 10 |
| Trilha por nível de senioridade | 11 |
| Arquitetura de trilha (mistura de formatos) | 12 |
| Programa corporativo completo | 13 |
| Jornada blended / híbrida | 14 |
| Programa focado em mudança de comportamento | 15 |
| Auditar/revisar conteúdo ou trilha existente | 16 |
| Objetivos de aprendizagem (a partir de tema) | 17 |
| Plano de aula ou workshop | 18 |
| Atividades práticas para um tema | 19 |
| Indicadores de sucesso do programa | 20 |
| Modelo de avaliação completo (reação→impacto) | 21 |
| Garantir aplicação no trabalho (transferência) | 22 |
| Narrativa de valor para diretoria/board | 23 |
| Estratégia de personalização com IA | 24 |
| Tutor/assistente de IA para jornada | 25 |
| Casos de uso de IA na educação corporativa | 26 |

## Adaptações da casa (fecham falhas do teste vermelho)

- **Objetivos de aprendizagem** sempre com verbo de ação + nível cognitivo
  (taxonomia de Bloom, prompt 17) e critério de avaliação declarado — nunca
  "entender X".
- **Métricas** sempre nos 5 níveis do prompt 20 (engajamento, aprendizagem,
  aplicação, mudança de prática, impacto no negócio), cada uma com como medir,
  quando e quem é responsável — não ad-hoc.
- **"Mapa visual"** sai como tabela markdown ou mermaid — nunca ASCII art de
  caixas e setas (quebra em tela estreita e não renderiza).
- **Entregáveis citados existem**: se a resposta menciona rubrica, prova,
  checklist ou simulação, ela entrega o conteúdo — não cita e pula.
- **Números realistas**: carga horária, tempo de fase e metas propostas são
  explícitos e coerentes com o contexto; quando o dado falta, fica como
  pergunta, não como chute.

## Referências

- `references/catalogo-prompts.md` — os 26 prompts completos, verbatim,
  organizados nas 8 seções do original, com o propósito de cada um.

## Fonte

Adaptado de **"26 Prompts completos para Educação Corporativa"**, Alun Business
(grupo Alura: Alura, FIAP, PM3, StartSe) — material de divulgação distribuído
gratuitamente, sem licença de redistribuição. Prompts mantidos verbatim no
catálogo; adaptações de uso são desta casa (05/10/2026). Conteúdo de terceiros:
republicação fora deste repositório depende de autorização do autor original.

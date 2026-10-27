---
name: terras-registro-de-decisao
description: "ADR (Architecture Decision Record) no formato MADR: contexto e forças, opções reais com prós e contras, decisão com critério, consequências negativas, status e substituição sem reescrever o antigo. Use para registrar decisão técnica ou de arquitetura. Gate da norma v4: terras-standards."
keywords: [adr, architecture decision record, registro de decisao, decisao de arquitetura, decisao tecnica, madr, registrar decisao, log de decisoes, trade-off, alternativas consideradas, substituir adr]
version: 1.0.0
license: MIT
---

# Registro de decisão (ADR)

## Objetivo

Deixar escrita uma decisão técnica de forma que alguém que não estava na sala, daqui a um ano, entenda **o que** foi decidido, **por que**, **o que mais foi considerado** e **o que custou**. Decisão sem registro é refeita, mal, por quem não conhece o contexto.

O erro que esta skill fecha: ADR que é justificativa pós-fato — alternativas de palha ("MongoDB: não é relacional"), só consequências positivas, contexto genérico copiado de blog e nenhum jeito de saber se a decisão continua valendo.

## Regra dura

1. **Ao menos 2 opções reais**, cada uma com prós **e** contras honestos. Opção que ninguém defenderia não conta. "Não mudar nada" entra quando for viável.
2. **Consequências negativas obrigatórias.** Toda decisão custa algo; ADR sem custo declarado é propaganda.
3. **Contexto é do projeto, não da tecnologia.** Volume, equipe, prazo, restrição, sistema existente. O que o usuário não informou vira `[A CONFIRMAR]`, nunca um número plausível.
4. **ADR aceito não se reescreve.** Mudou a decisão: novo ADR com `Substitui ADR-NNNN`, e o antigo recebe só a linha `Status: substituído por ADR-MMMM`.
5. **Uma decisão por ADR.** "Postgres + Redis + Kafka" são três ADRs.
6. **Status e decisores vêm do usuário.** "Decidimos" → `aceito`; "estamos pensando" → `proposto`. Decisores não informados → `[A CONFIRMAR]`, nunca "time de arquitetura".

## Como trabalhar

1. **Confira se cabe ADR:** decisão difícil de desfazer, que afeta mais de um módulo ou pessoa, ou que alguém vai questionar depois. Escolha de biblioteca trivial não precisa.
2. **Ache o diretório de decisões** do projeto (`docs/adr/`, `docs/decisions/`, `adr/`). Não existe: crie `docs/adr/` e o `0000-registrar-decisoes.md` dizendo que o projeto usa ADR.
3. **Numere em sequência** (`NNNN-titulo-em-kebab.md`), sem reaproveitar número.
4. **Preencha `templates/adr.md`:** contexto e forças (o que puxa para cada lado), critérios de decisão declarados **antes** de comparar, opções, decisão, consequências (+/−), confirmação (como verificar que foi cumprida e quando revisar).
5. **Status:** `proposto` (em discussão) → `aceito` (data e decisores) → `obsoleto` ou `substituído por`. Rejeitado também se registra: evita a mesma discussão de novo.
6. **Atualize o índice** (`docs/adr/README.md`), uma linha por ADR com número, título, status e data.

## Fronteiras

- Decisão dentro do fluxo da norma de engenharia v4 (gate, perfil, questionário): `terras-standards`, que tem gerador de ADR próprio.
- Decisão de negócio ou priorização de problema: `terras-matriz-gut`, `terras-decisor`.
- Requisitos de produto (o quê e por quê do usuário): `terras-prd`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Alternativa de palha | opção que alguém sensato escolheria, com prós reais |
| Critério escolhido depois de comparar | critérios declarados antes da tabela de opções |
| Só ganhos | consequências negativas e o que se faz com elas |
| Editar ADR antigo para refletir a decisão nova | ADR novo com "Substitui"; o antigo só muda o status |
| Números de volume ou equipe inventados | `[A CONFIRMAR]` |
| Sem "como confirmar" | teste, métrica, revisão de código ou data de revisita |

## Arquivos

- `templates/adr.md` — ADR no formato MADR adaptado, com status, critérios, opções, consequências e confirmação.
- `templates/indice.md` — índice do diretório de ADRs.

## Fonte

Formato derivado de MADR (Markdown Any Decision Records, adr.github.io/madr, licenças MIT/CC0) e do ADR original de Michael Nygard (2011), adaptados ao padrão da casa.

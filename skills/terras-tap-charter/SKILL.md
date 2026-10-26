---
name: terras-tap-charter
description: "Termo de Abertura do Projeto (TAP, project charter): justificativa, objetivos mensuráveis, escopo dentro e fora, marcos, orçamento, premissas, riscos, patrocinador e autoridade do gerente, sem inventar data nem valor. Use para abrir projeto, TAP, charter ou kickoff formal. Project charter."
keywords: [tap, termo de abertura, termo de abertura do projeto, project charter, abertura de projeto, kickoff, pmbok, patrocinador, escopo do projeto, marcos do projeto, premissas e restricoes, gerente de projeto]
version: 1.0.0
license: MIT
---

# Termo de Abertura do Projeto (TAP)

## Objetivo

Autorizar formalmente o projeto e dar ao gerente a autoridade para usar recursos. O TAP responde, em 2 a 4 páginas: por que o projeto existe, o que precisa entregar, o que não entra, quanto custa e até quando, quem patrocina e quem conduz.

O erro que esta skill fecha: TAP que parece pronto porque tem datas e percentuais — marcos inventados ("go-live 05/04/2027"), critérios de sucesso sem base ("disponibilidade ≥ 99,5%, ±10%"), patrocinador "diretoria" — e que ninguém consegue aprovar porque nada daquilo foi combinado.

## Regra dura

1. **Data, valor e meta que o usuário não deu não viram compromisso.** Saem como `[A CONFIRMAR]` ou como `proposta` com a conta que levou a ela (ex.: "proposta: 20 semanas = 4 diagnóstico + 8 migração-teste + 6 testes + 2 corte"). O TAP é assinado: número inventado vira promessa.
2. **Patrocinador é uma pessoa ou cargo único** com poder de aprovar orçamento. "Diretoria" ou "comitê" → `[A CONFIRMAR: quem assina]`.
3. **Objetivo mensurável ou marcado.** Cada objetivo tem indicador e critério de sucesso; sem base, o critério fica `[A DEFINIR com o patrocinador]`.
4. **Fora do escopo com pelo menos 3 itens** previsíveis, e quem decide mudança de escopo.
5. **Autoridade do gerente explícita:** até que valor aprova, se escolhe equipe, a quem escala.
6. **TAP sem assinatura é rascunho**: o cabeçalho diz isso até a aprovação.

## Como trabalhar

1. **Colete:** demanda de origem (problema, contrato, lei), quem pede, quem paga, restrições conhecidas (data fixa, orçamento-teto, fornecedor já contratado).
2. **Justificativa** ligada a problema ou oportunidade com evidência; caso de negócio, se houver.
3. **Objetivos e critérios de sucesso** (regra 3).
4. **Escopo de alto nível:** entregas principais, dentro e fora (regra 4). Detalhamento (EAP) vem depois.
5. **Marcos:** sequência e dependências; datas só as dadas ou `proposta` com a conta (regra 1).
6. **Orçamento resumido:** componentes, valor conhecido ou `[A ESTIMAR]`, reserva de contingência como decisão do patrocinador.
7. **Premissas, restrições e riscos iniciais** com dono.
8. **Partes interessadas:** papel, interesse, influência.
9. **Papéis e autoridade** (regras 2 e 5) e **aprovação**.

Use `templates/tap.md`. Projeto pequeno: uma página com justificativa, objetivo, escopo dentro/fora, marco final, custo, patrocinador e gerente.

## Fronteiras

- Requisitos de um produto ou feature: `terras-prd`.
- Acompanhamento semanal depois de aberto: `terras-status-report`.
- Plano de ações com dono e prazo: `terras-5w2h`.
- Risco de segurança da informação do sistema: `terras-analise-risco-si`.
- Proposta comercial para cliente: `terras-elaboracao-proposta-comercial`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Datas de marco inventadas | `[A CONFIRMAR]` ou `proposta` com a conta |
| Critério de sucesso genérico (±10%) | definido com o patrocinador ou marcado |
| Patrocinador coletivo | uma pessoa que assina |
| Escopo sem "fora" | 3+ itens e regra de mudança |
| Autoridade do gerente omitida | valor de alçada e caminho de escalonamento |

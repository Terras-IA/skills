---
name: terras-prd
description: "PRD (documento de requisitos de produto): problema com evidência, métricas com linha de base, fora de escopo, requisitos MoSCoW com critério de aceite e perguntas em aberto. Use para PRD, requisitos de produto ou briefing de feature. Spec técnica: terras-spec-flow. Product requirements doc."
keywords: [prd, product requirements, documento de requisitos, requisitos de produto, briefing de feature, especificacao de produto, escopo de produto, fora de escopo, metricas de sucesso, moscow, criterio de aceite, mvp]
version: 1.0.0
license: MIT
---

# PRD — documento de requisitos de produto

## Objetivo

Escrever o PRD que responde **o quê** e **por quê** antes de alguém decidir o **como**. Um PRD bom faz três coisas: prova que o problema existe, diz como se vai saber que deu certo e corta o que não entra. O resto (telas, tabelas, arquitetura) vem depois, em spec técnica e ADR.

O erro que esta skill fecha: PRD que nasce da solução ("um app de reserva com calendário e QR code"), traz meta inventada ("reduzir conflitos em 80%") e não tem "fora de escopo" — aí todo pedido novo vira requisito e ninguém consegue dizer não.

## Regra dura

1. **Número sem fonte não entra como fato.** Métrica, linha de base, tamanho de público, prazo e custo que o usuário não deu viram `[A CONFIRMAR: <como medir>]`. Meta inventada é pior que meta em branco: parece decidida.
2. **Problema antes de solução.** A seção de problema não cita funcionalidade. Se o pedido veio como solução, reescreva como problema e registre a solução sugerida em "Hipóteses de solução".
3. **"Fora de escopo" nunca vazio.** No mínimo 3 itens que alguém vai pedir e que não entram nesta versão, cada um com o motivo.
4. **Todo requisito "Must" tem critério de aceite testável** (dado/quando/então ou número). Alvo técnico de mercado (p95 < 2 s) pode entrar marcado `proposta`; meta de negócio não. Requisito sem aceite vai para "Perguntas em aberto".
5. **Pressa não pula as perguntas em aberto:** entrega o PRD e lista o que falta decidir, com dono. PRD "completo" sem perguntas em aberto quase sempre esconde suposição.

## Como trabalhar

1. **Colete o que existe:** pedido original, quem pediu, dados (chamados, planilha, reclamação, métrica atual), restrições (prazo, orçamento, sistema obrigatório). O que não foi dado não se inventa; vira `[A CONFIRMAR]`.
2. **Problema:** quem sofre, em que situação, com que frequência e quanto custa hoje. Uma frase-síntese + evidência. Sem evidência → marcar como **premissa**.
3. **Usuários e cenários:** 2 a 4 perfis por papel (não persona inventada com nome e foto) e os cenários principais em uma linha cada.
4. **Objetivos e métricas:** cada objetivo com métrica, linha de base, meta e prazo. Linha de base desconhecida → primeira tarefa do projeto é medir. Inclua uma métrica de proteção (o que não pode piorar).
5. **Escopo:** dentro, fora (regra 3) e hipóteses de solução.
6. **Requisitos:** funcionais e não funcionais (segurança, LGPD, acessibilidade, desempenho, integração), priorizados em MoSCoW, com critério de aceite.
7. **Dependências, riscos e lançamento:** o que precisa existir antes, o que pode dar errado, como entra (piloto, por área, tudo de uma vez) e como volta atrás.
8. **Perguntas em aberto** com dono e data. **Aprovação:** quem aprova e status (rascunho, em revisão, aprovado).

Use `templates/prd.md` como esqueleto. PRD pequeno (feature de uma semana) pode cortar seções; nunca corta problema, métrica, fora de escopo e perguntas em aberto.

## Fronteiras

- Spec técnica, plano de implementação e crítica de spec: `terras-spec-flow`, `terras-critica-de-spec`.
- Decisão de arquitetura tomada no caminho: `terras-registro-de-decisao`.
- Pesquisa com usuário para levantar o problema: `terras-user-research`.
- Abrir o projeto formalmente (patrocinador, orçamento, marcos): `terras-tap-charter`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Meta de efeito redondo inventada ("-80% conflitos") | `[A CONFIRMAR]` + como medir a linha de base |
| Problema descrito como falta da solução ("não temos app") | descreva a dor e o custo atual |
| Persona fictícia com nome e hobby | perfil por papel e situação |
| Tudo "Must" | Must é o que, se faltar, o lançamento não vale; o resto desce |
| Requisito "ser rápido", "ser intuitivo" | número (p95 < 2 s) ou tarefa testada com usuário |
| Fora de escopo vazio | 3+ itens previsíveis, com motivo |

## Arquivos

- `templates/prd.md` — esqueleto do PRD com todas as seções e as marcas `[A CONFIRMAR]`.

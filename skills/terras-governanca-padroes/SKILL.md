---
name: terras-governanca-padroes
description: >-
  Audita onde as convenções de um projeto vivem (CLAUDE.md, AGENTS.md, lint, CI,
  docs, cabeça do time) e transforma padrão em governance rule: arquivo Markdown
  versionado, com dono, data de revisão, "quando NÃO usar" e ciclo de deprecação —
  legível e acionável por agente de IA. Use quando pedirem para avaliar/auditar
  padrões ou convenções de um repositório, padronizar um projeto, criar ou
  versionar regras do time, ou quando as regras vivem só em wiki/Notion/conversa.
  EN: governance rules, conventions as skills, standards audit, AGENTS.md.
keywords: [governança, convenções, padrões, governance rules, conventions, standards, auditoria, versionamento, deprecação]
---

# terras-governanca-padroes

Avaliar os padrões de um projeto e publicá-los como regras versionadas que agente consegue seguir.

## Objetivo

A maioria dos times tem convenções; o problema é onde elas vivem — wiki que ninguém abre, cabeça de quem está há mais tempo e, cada vez mais, nenhum lugar que um agente de IA consiga ler. Esta skill fecha esse buraco em dois modos: **AUDITAR** (diagnosticar quais padrões existem de fato, onde estão registrados e onde os registros mentem) e **PUBLICAR** (converter padrão em governance rule: Markdown versionado, com dono, revisão datada, exceções e ciclo de vida).

O leitor-alvo é o agente de IA — o leitor mais exigente que existe: lê tudo, não pergunta, e transforma cada ambiguidade em código errado. Regra escrita para agente serve pros dois; regra escrita para humano folheando não serve para nenhum.

## Regra dura

1. **Fonte é o que executa e o que o código faz.** Lei = lint/CI/hooks (o que falha build) + código de facto (amostra + `git log`). Wiki, Notion e memória de quem está há mais tempo não são fonte — são pauta de confirmação com o dono.
2. **Regra sem ciclo de vida não publica.** Toda governance rule carrega `version`, `owner`, `review` (próxima revisão), "Como verificar" e "Quando NÃO usar". Falta um → é rascunho, não regra.
3. **Registro que mente sai no mesmo commit.** Regra que contradiz o que o CI/lint executa (ou o que o código faz) é corrigida ou retirada na hora. Documento que mente é pior que documento ausente, porque o agente segue com confiança.

## Como trabalhar

### Modo 1 — AUDITAR (avaliar)

1. Rode `scripts/auditar-fontes.sh <repo>`: inventário dos portadores (instrução a agentes, docs, lint, CI, hooks, containers) com a data do mais recente — arquivo velho é suspeito de mentir.
2. Extraia convenções candidatas de quatro lugares, nesta ordem de autoridade: (a) o que CI/lint executa; (b) amostra de ~15 arquivos em pontos distintos (entrada, config, módulo velho, módulo novo, testes); (c) `git log` — estilo de commit, nome de branch/PR; (d) CLAUDE.md/AGENTS.md/docs — tratar como suspeito e confirmar no código.
3. Preencha a grade de `references/auditoria.md` por candidata: evidência, é de facto?, verificável como?, ambígua?, conflita com qual fonte?
4. Conflito config × código × docs não se resolve sozinho: vira item da lista de decisão, com o nome de quem decide.
5. Entregável: relatório curto com as seções do protocolo — **vivas sem registro**, **registros que mentem**, **conflitos abertos**, **lacunas** (mesma decisão tomada diferente em lugares diferentes) — mais próximas ações priorizadas.

### Modo 2 — PUBLICAR (criar/atualizar padrão)

1. **Uma regra = uma unidade versionável**, escopo mínimo, nome que responde à pergunta que ela resolve (`git-flow-compliance`, `erro-handling-api`), nunca "nosso jeito de fazer X".
2. **Onde salva:** skills do projeto (`.zcode/skills/`, `.claude/skills/`) quando o agente do projeto lê skills; senão `docs/padroes/<nome>.md` com índice de 1 linha por regra no AGENTS.md/CLAUDE.md — **ponteiro, nunca duplicação**. Wiki/Notion nunca é o único destino.
3. **Corpo pelo template** de `references/template-regra.md`: regra imperativa, por quê (evidência do repo), como verificar, quando NÃO usar, exemplos bom/ruim, changelog.
4. **Semver por regra:** apertar ou mudar comportamento esperado = MAJOR (com nota "o que muda para quem seguia a versão anterior"); adicionar exceção ou esclarecer = MINOR; redação = PATCH.
5. **Deprecação tem cerimônia:** `status: deprecated` + substituída-por + prazo, no mesmo commit que apresenta a substituta; só depois do prazo a regra sai do índice e do diretório. Nunca apagar silenciosamente.
6. **Corte:** o que ESLint/CI já garante sozinho vira referência de 1 linha, não prosa duplicada; sem "como verificar" preenchível é preferência, não regra; teto de ~15 regras ativas por repo — acima disso, dividir por domínio.

## Anti-padrões

- Arquivo-monumento com todas as regras e sem ciclo de vida: é a wiki renascendo dentro do repo.
- Regra sem "quando NÃO usar": dispara fora de contexto e vira fonte de erro.
- Aspiração disfarçada de regra ("sempre testamos tudo") — regra é o que código e CI comprovam.
- 40 regras impressionantes que ninguém audita; 12 verificáveis valem mais.
- Amarrar a regra a uma ferramenta específica e chamar de padrão: a fonte é vendor-agnostic, o gerador é descartável.

## Referências

- `references/auditoria.md` — protocolo completo do modo AUDITAR: autoridade das fontes, amostragem, grade por candidata, formato do relatório.
- `references/template-regra.md` — template de governance rule com exemplo preenchido e as convenções de semver, changelog e deprecação.

## Fonte

Metodologia da casa (`terras-skill-factory`, TDD de documentação). Tese central derivada do post "governance rules" (LinkedIn, out/2026): convenções tratadas como código — versionadas, com metadata e quando-não-usar; todo repo tem 3–5 convenções dignas de skill.

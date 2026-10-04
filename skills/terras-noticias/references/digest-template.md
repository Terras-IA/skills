# Template do digest

Saída em PT-BR, um arquivo só, post no fim, nesta ordem. Nunca pule a ficha nem
a coluna de ação: são elas que fazem o digest ser operacional, não uma lista.

## 1. Ficha

```
Notícias — <fonte> <epNN> — leitura em <AAAA-MM-DD> · N itens · P0/P1: M ·
confirmados na fonte primária: X de M · fonte: <URL do boletim>
```

## 2. Triagem + resumo rápido (todos os itens)

Tabela única, ordenada por prioridade (P0 primeiro). Duplicatas na mesma linha.
O tema é a seção do boletim, como coluna, para a leitura em diagonal.

| # | Item | Tema | Crit. | Pri. | O que é (uma linha) | Ação | Fonte |
|---|------|------|-------|------|---------------------|------|-------|
| 1 | ... | ... | Alta | P0 | ... | ... | ✅ |
| 2 | ... | ... | Média | P2 | ... | nada | ⚠️ |

Regras da linha:

- **O que é**: o que muda, não o que foi anunciado. Sem adjetivo de marketing.
- **Ação**: verbo concreto ("conferir limite do plano", "testar no próximo PR",
  "verificar na release note", "checar custo por tarefa") ou "nada".
- **Fonte**: `✅` confirmado na fonte primária · `⚠️` só o boletim ou o X.
- P3 fica no fim. Nada some da tabela: o resumo é de **todos** os itens.
- Uma linha por item, no máximo duas; quem quiser detalhe vai ao destaque.

## 3. Destaques (P0 e P1)

Um bloco por item, 3 bullets, 4 a 6 linhas no total:

```md
### <Item> — <Crit.>/<Pri.> `✅`

- **O que é:** o fato, com número/data/versão da fonte primária.
- **Por que importa:** a consequência para quem trabalha com tecnologia hoje.
- **O que fazer:** a ação, verificável.
```

## 4. Ruído (P3)

Uma linha: o que ficou de fora e por quê ("trollagem do domínio, drama, opinião
sem consequência prática"). Sem esta linha, o leitor não sabe se algo passou
batido.

## 5. Post LinkedIn (rascunho)

Post pronto para copiar, com hashtags no fim. Regras de estrutura e tom na
`terras-linkedin`; regras específicas do digest no SKILL.md (zero travessão,
seleção de 2 a 4 itens, sem link no corpo, 1.300 a 1.800 caracteres).

## 6. Anexo — fontes verificadas

Lista dos links usados na verificação, por item. O post não leva link no
corpo; é aqui que as fontes vivem. Endereço original mais a URL do snapshot
quando a fonte bloqueia acesso direto (openai.com devolve 403; o snapshot do
Wayback funciona e entra no anexo).

---

## Exemplo preenchido (recorte real do ep36, 03/10/2026)

Ficha: `Notícias — ratos de IA ep36 — leitura em 2026-10-03 · 24 itens · P0/P1: 5 · confirmados na fonte primária: 3 de 5`

| # | Item | Tema | Crit. | Pri. | O que é (uma linha) | Ação | Fonte |
|---|------|------|-------|------|---------------------|------|-------|
| 1 | Mods do Claude (CLI e desktop) | Claude | Alta | P0 | A CLI do Claude passa a aceitar mods (plugins em TypeScript) que mudam comportamento, UI e features, instaláveis por `/plugin`. | Testar um mod no próximo PR | ✅ |
| 2 | Plano de US$ 200 volta com metade do uso | ChatGPT, planos | Alta | P0 | O teto de uso do plano Pro de US$ 200 caiu pela metade para novos assinantes; nasce o plano de US$ 500 com modo ultrafast. | Conferir o próprio limite e o custo por tarefa | ⚠️ |
| 3 | a16z: adoção de skills e plugins | calma, é bolha | Alta | P1 | Uso semanal: 93% no time da OpenAI, 19% no top 10% das empresas, 3% na empresa típica. | Calibrar a tese de post sobre o gap de adoção | ✅ |

Destaque correspondente:

```md
### Mods do Claude (CLI e desktop) — Alta/P0 `✅`

- **O que é:** o Claude agora aceita mods, plugins em TypeScript (ou escritos
  pelo próprio Claude) que mudam comportamento, customizam a UI e trocam
  features; a distribuição é pelo `/plugin`.
- **Por que importa:** é a ferramenta principal virando plataforma. Quem
  depende dela ganha extensão sem fork e sem esperar release.
- **O que fazer:** instalar um mod pequeno e medir o que muda no fluxo antes
  de recomendar qualquer um no post.
```

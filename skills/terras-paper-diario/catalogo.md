---
name: terras-paper-diario
description: Analisa papers (arXiv e afins) que afetam quem desenvolve: resumo honesto com números, aplicação prática e aviso para júnior, pleno e sênior. Use quando mandarem um link de paper, pedirem para analisar um paper, o paper do dia ou a verificação diária do arXiv.
keywords: [paper, arxiv, estudo, pesquisa, paper do dia, paper-diario, agentes de ia, code review, carreira dev, análise de paper, digest diário]
---

# Paper do dia — papers que afetam quem escreve software

## Objetivo

Transformar paper acadêmico em leitura útil: o que o estudo fez, o que
descobriu (com os números reais), o que isso muda na prática e o que deve
acender o sinal de alerta — separado por nível de experiência, com um
fechamento comum. O diferencial não é resumir o paper; é dizer **o que cada
um faz diferente amanhã**.

## Onde está instalada

Fonte única: `skills/terras-paper-diario/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

Funciona em qualquer workspace. As análises salvas vivem em
`~/Documents/Desenvolvimento/paper-diario/`. Estado (papers já vistos) em
`~/.config/terras-paper-diario/vistos.json`.

## O template da análise (o diferencial — siga exatamente)

Idioma: **português do Brasil**. Público: devs de todos os níveis. Toda
análise tem, nesta ordem:

1. **O paper em uma frase** — o achado central dito de forma que um dev
   entenda em 10 segundos. Se o título do paper pode induzir ao erro (ex.:
   "fim de job" que na verdade é "quem conclui o trabalho"), o esclarecimento
   vem aqui, em destaque.
2. **Ficha** — título, autores, venue/arXiv + link, data, categoria.
3. **O que foi estudado** — método em linguagem humana: quantos dados, como
   mediram, que compararam. Nada de jargão sem tradução.
4. **O que descobriram** — os achados com **números exatos do paper**
   (porcentagens, odds ratios, n). Máximo 5 bullets, o mais forte primeiro.
5. **O que isso NÃO significa** — 3 a 4 bullets anti-hype: limitações,
   escopo, o que a imprensa vai distorcer. Nunca pule esta seção.
6. **Por nível** — para cada um, dois blocos curtos:
   - **Júnior (0–2 anos)** — *Aplicação prática:* o que fazer diferente na
     próxima tarefa. *Aviso real:* o risco concreto deste nível à luz do
     paper (carreira, aprendizado, empregabilidade).
   - **Pleno (2–5 anos)** — idem, com foco em processo, métrica e time.
   - **Sênior (5+ anos, incluindo quem lidera)** — idem, com foco em
     arquitetura, propriedade do código, risco de longo prazo.
7. **Para todos** — fechamento: uma ação concreta para hoje (verificável) e
   uma frase para levar. Vale para todos os níveis, inclusive gestão.

Regras de qualidade (invioláveis):

- **Número só do paper.** Se o número não está no texto, não entra. Se a
  memória discordar do paper, prevalece o paper.
- **Separe achado de interpretação.** "O estudo mediu X" ≠ "então Y vai
  acontecer com você".
- **Correlação não é causalidade** — diga quando o desenho do estudo não
  permite afirmar causa.
- **Amostra importa.** n pequeno (ex.: 130 PRs) vira ressalva explícita.
- **Não transforme achado em profecia.** Estudos empíricos descrevem o
  passado observado; o futuro entra como risco, não como certeza.

## Como buscar o paper (on-demand)

1. Página de resumo: `https://arxiv.org/abs/<ID>` (a página dá título,
   abstract, autores, datas).
2. Texto completo: `https://arxiv.org/html/<ID>v<N>` — peça metodologia,
   todos os números, diferenças entre grupos, limitações e a seção de
   implicações para praticantes. Se não houver versão HTML, baixe o PDF
   (`https://arxiv.org/pdf/<ID>`) e extraia com `pdftotext`.
3. Sites que não são arXiv (ACM, IEEE, blog com estudo): mesma lógica —
   abstract + texto completo quando acessível; se só existir o abstract,
   diga isso na análise e diminua o tom das conclusões.

## Verificação diária (o fluxo)

```bash
python3 $SKILL_DIR/scripts/verificar_papers.py --janela 3 --limite 2
```

Consulta **cinco fontes** (ver seção abaixo), compara com os já vistos e
devolve os mais relevantes pontuados, mais os sinais da comunidade do
Hacker News separados. Demora alguns minutos (pausas anti-rate-limit).
Depois de publicar a análise de cada paper, marque-o como lido — **o ID e o
título** (o título é o que deduplica o mesmo paper achado em fontes
diferentes):

```bash
python3 $SKILL_DIR/scripts/verificar_papers.py \
  --marcar arxiv:2609.26847 --marcar-titulo "Who Finishes the Job? A Study of ..."
```

Para cada paper novo (no máximo 2 por dia): busque o texto completo, gere a
análise completa no template, salve em
`~/Documents/Desenvolvimento/paper-diario/YYYY-MM-DD-<slug>.md` e poste no
Discord via `~/Documents/Desenvolvimento/discord-post.sh` um resumo curto:
título + link + assunto/severidade/relevância + os três avisos (um por
nível) + o fechamento. Nunca poste o texto integral. Se não houver paper
novo, poste uma linha dizendo que a verificação rodou e não achou nada
novo. Sinais do HN não viram análise — no máximo entram no post como
"o que a comunidade está discutindo".

**Automação**: roda todo dia às 8h (CronCreate). O prompt da automação é
curto de propósito — ele manda ler este SKILL.md e seguir a seção
"Verificação diária". Este manual é a fonte única da verdade do fluxo.

## Fontes de busca (qualquer idioma, análise sempre em português)

| Fonte | O que cobre | Papel na curadoria |
|---|---|---|
| `arxiv` | arXiv (cs.SE, cs.CY, cs.AI, cs.HC, cs.PL) | papers abertos com texto completo — o núcleo |
| `s2` | Semantic Scholar: ACM, IEEE, Springer, Elsevier, arXiv… | alcança papers de conferência que o arXiv não tem |
| `openalex` | OpenAlex: cobertura cruzada de periódicos | rede de segurança da s2, com DOI canônico |
| `hn` | Hacker News (vía Algolia) | **sinal, não fonte**: o que a comunidade está discutindo; confirmação sempre na fonte primária |
| `openreview` | OpenReview (submissões sob revisão) | sinal precoce do que vem aí; tratar como pré-publicação |

Regras das fontes:

- **Idioma não filtra nada; a saída é sempre PT-BR.** Paper em outro idioma
  é analisado do mesmo jeito (traduza os conceitos; nunca cite como citação
  literal o que foi traduzido).
- **Fonte sem texto acessível não vira análise completa.** Abstract-only
  (comum em ACM/IEEE fechado): diga isso na análise e diminua o tom.
- **HN e OpenReview são descoberta, não fonte** — mesma regra dura da
  `terras-last30days`: nunca cite como fonte de fato; confirme no paper.
- `--fontes` escolhe o subconjunto; `--pausa-arxiv 45` e `--pausa 5` regulam
  o ritmo. Nesta rede: `export.arxiv.org` é instável — a busca vai pelo site
  `arxiv.org`, em grupos de no máx. 3 frases OR, e todo curl precisa de `-4`.

## Classificação para curadoria (assunto × severidade × relevância)

Quando o resultado for uma **lista** de papers (busca ampla, verificação
com vários achados), organize por assunto e classifique cada item:

- **Assunto**: agrupe os papers por tema (ex.: segurança de código gerado,
  manutenção pós-merge, review assistido, carreira e saúde, propriedade e
  responsabilidade, benchmarks e harness).
- **Severidade** — o risco que o achado sinaliza, não a qualidade do paper:
  - **Alta**: risco ativo — pode quebrar produção, segurança ou carreira em
    escala agora (vulnerabilidade sistêmica, vetor de ataque, dado de
    desemprego medido).
  - **Média**: recomendação de mudança de prática com evidência (processo,
    métrica, revisão).
  - **Baixa**: informativa — benchmark, dataset, framework; matéria-prima,
    sem urgência.
- **Relevância para o público** (devs de todos os níveis):
  - **Máxima**: muda o dia a dia de qualquer dev nos próximos meses.
  - **Alta**: muda a prática de parte do público (quem usa determinado
    agente, quem lidera time).
  - **Média**: nicho, ferramenta ou benchmark específico.

O score numérico `[n]` do script é o ranke bruto por palavras-chave; a
severidade e a relevância são julgadas na leitura — nunca apresente só o
score. Nos avisos de severidade alta, o fechamento "para todos" ganha uma
ação concreta de proteção.

## Estado

`~/.config/terras-paper-diario/vistos.json` — mapa `id → data` dos papers já
analisados; entradas `t:<título-normalizado>` deduplicam o mesmo paper
achado em fontes diferentes. `--marcar` adiciona IDs, `--marcar-titulo`
adiciona títulos (repetível), `--limpar` zera. O script nunca marca sozinho:
marcar é passo consciente depois de publicar a análise.

## Limitações conhecidas

- **ACM/IEEE fechado**: a s2 e a OpenAlex acham o paper, mas o texto pode
  ficar atrás de paywall — abstract-only vira análise de tom reduzido.
- **Filtro por palavras-chave erra dos dois lados** (deixa passar e deixa
  entrar); o score ranqueia, quem analisa filtra.
- **Volume**: o arXiv trunca em 100 resultados por grupo (mais recentes
  primeiro) e a s2/OpenAlex/HN também paginam em 100/50 — com janela maior
  que ~30 dias, papéis antigos podem ficar fora.
- **Rate limit**: nesta rede, `export.arxiv.org` é instável/limitado; o
  arXiv vai pelo site com pausas de 45 s. A s2 sem chave de API sofre 429
  com frequência — o script volta com backoff e segue se falhar (aviso no
  stderr).
- **HN/OpenReview são ruído por natureza**: servem para enxergar a
  conversa e o que vem aí, nunca como fonte de fato.

## Exemplos de uso

- "analisar esse paper: https://arxiv.org/abs/2609.26847"
- "paper do dia" (→ roda a verificação, escolhe o melhor e analisa)
- "verifica se saiu paper novo sobre agentes de IA" (→ script + análise)
- "procure papers dos últimos 30 dias" (→ `--janela 30 --limite 20` + curadoria
  classificada por assunto/severidade/relevância)
- "postar a análise de ontem no Discord" (→ resumo curto via discord-post.sh)

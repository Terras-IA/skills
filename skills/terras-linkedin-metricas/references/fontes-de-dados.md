# Fontes de dados (mapa verificado em 25/09/2026)

Tudo aqui foi lido na conta do Everton (interface em português), com a sessão do
navegador in-app, nas URLs abaixo. O que é fato verificado está marcado como tal; o
resto é o que ainda falta confirmar.

## Páginas que existem e o que cada uma dá

### `https://www.linkedin.com/analytics/creator/content/` — Análise de conteúdo

Verificado. Entrega, na janela escolhida (o botão estava em "7 dias"):

| Rótulo na página | Campo no store |
|---|---|
| `Impressões` (card Desempenho do conteúdo) | `impressoes` |
| `%` + `em relação a N dias anteriores` | `variacao_pct` |
| `Usuários alcançados` | `usuarios_alcancados` |
| `Na rede (seguidores e conexões)` | `na_rede_pct` |
| `Fora da rede` | `fora_da_rede_pct` |
| `Engajamento nas redes` | `engajamento_total` |
| `Reações`, `Comentários`, `Compartilhamentos`, `Salvamentos`, `Envios no LinkedIn` | idem |
| pontos do gráfico (`img "…, <valor>. Impressões."`) | `serie_diaria` |
| blocos `Dimensão / valor / %` | `demografia` |
| blocos `N impressões • M engajamentos` + `Ver análise` | `top_posts` (URN de atividade, URN do share e texto publicado) |

Detalhes que enganam:

- O gráfico vem **cumulativo** enquanto a caixa "Cumulativo" estiver marcada: 549,
  1.169, 2.189… até o total da janela. Não é o valor do dia.
- O LinkedIn registra o dia em **UTC** (a própria página avisa). Em São Paulo (UTC-3),
  depois das 21h o dia do LinkedIn já é o seguinte: a coleta feita na noite de 24/09
  sai carimbada como 25/09, e isso não é erro de relógio.
- "Publicações de melhor desempenho" e "Principais dados demográficos" carregam depois
  do resto da página. Snapshot cedo demais perde as duas.
- A demografia do painel "Tudo" mostra só a maior fatia de cada dimensão. As abas
  (`Cargo`, `Localidade`, `Nível de experiência`, `Empresa`, `Setor`, `Tamanho da empresa`)
  abrem a lista completa, e isso exige clique (coleta mais profunda, opcional).
- O "Exibir mais" aponta para `/analytics/creator/top-posts/?startDate=…&endDate=…&metricType=IMPRESSIONS&timeRange=past_7_days`,
  que é a tabela completa de melhores posts da mesma janela.

### `https://www.linkedin.com/analytics/creator/audience/` — Análise de público

Verificado. Entrega `Total de seguidores`, `%` vs período anterior, a série de
`Novos seguidores` (também cumulativa) e a demografia dos seguidores.

Atenção à diferença: a demografia de **seguidores** e a de **quem foi alcançado na
janela** não são a mesma coisa. No caso medido, seguidores são 34% Sênior, enquanto a
janela foi puxada para 39% Iniciante porque os posts recentes eram de assunto amplo.

### `https://www.linkedin.com/analytics/post-summary/<urn:li:activity:...>/` — Análise de um post

Verificado. É a única fonte de número por post em **tempo de vida**:

`Impressões`, `Usuários alcançados`, `Na rede` / `Fora da rede`, `Visualizações do perfil
a partir desta publicação`, `Seguidores obtidos com esta publicação` (link para
`/analytics/post-summary/followers/<urn>/`), `Engajamento` (total), `Reações`,
`Comentários`, `Compartilhamentos`, `Salvamentos`, `Envios no LinkedIn`, `Principais
dados demográficos` e a idade relativa ("publicou • 1 sem").

O detalhamento por pessoa fica em `/analytics/post/<urn:li:activity:...>/?resultType=REACTIONS`
(e `COMMENTS`, `RESHARES`), útil para saber *quem* engajou, não quantos. O link de `COMMENTS`
é o caminho para listar os comentários de um post quando o fluxo for responder comentário
(escrita na skill `terras-linkedin`, seção "Responder comentários nos seus posts"). Ainda não
é parseado pelo CLI; coletar a página do post basta para ler os comentários.

O URN do share aparece codificado na URL do botão "Patrocinar"
(`content=urn%3Ali%3Ashare%3A…`); o parser decodifica.

## Números observados (para calibrar expectativa)

Coleta de 25/09/2026, janela de 7 dias, conta com 1.202 seguidores:

- janela: 3.543 impressões (91% acima da anterior), 2.056 alcançados, 15% na rede,
  85% fora, 86 engajamentos (64 reações, 19 comentários, 3 salvamentos), 15 seguidores novos
- post do fim de suporte do .NET 8/9, publicado em 14/09, em 25/09: **37.999 impressões,
  26.390 alcançados, 0% na rede / 100% fora**, 54 reações, 10 comentários, 2 compartilhamentos,
  17 salvamentos, 1 envio, 64 views de perfil, 13 seguidores
- os dois posts seguintes, no mesmo idioma e na mesma voz, ficaram em 938 e 388 impressões
  na janela

Ou seja: um post de tema com prazo e consequência de mercado fez ~10x a mediana da conta,
e o público dele foi diferente do público médio. Esse é o contraste que o relatório procura.

## API oficial (o caminho que existe, com trava)

### Member Post Statistics — `memberCreatorPostAnalytics`

Documentação: `https://learn.microsoft.com/en-us/linkedin/marketing/community-management/members/post-statistics`
(versões `li-lms-2025-10` até `li-lms-2026-09`; o default em 25/09/2026 era `2026-09`).

```
GET https://api.linkedin.com/rest/memberCreatorPostAnalytics
    ?q=entity&entity=(ugc:urn%3Ali%3AugcPost%3A...|share:urn%3Ali%3Ashare%3A...)
    &queryType=IMPRESSION&aggregation=TOTAL
    &dateRange=(start:(day:4,month:5,year:2024),end:(day:6,month:5,year:2024))
Headers: Authorization: Bearer <token>, Linkedin-Version: YYYYMM, X-Restli-Protocol-Version: 2.0.0
```

- `q=entity` pede um post; `q=me` devolve o agregado do membro.
- `queryType` (versão 2026-04+): `IMPRESSION`, `MEMBERS_REACHED`, `RESHARE`, `REACTION`,
  `COMMENT`, `POST_SAVE`, `POST_SEND`, `LINK_CLICKS`, `PREMIUM_CTA_CLICKS`,
  `FOLLOWER_GAINED_FROM_CONTENT`, `PROFILE_VIEW_FROM_CONTENT`.
- `aggregation`: `TOTAL` (padrão) ou `DAILY`; `DAILY` não é suportado para
  `MEMBERS_REACHED`, `LINK_CLICKS`, `FOLLOWER_GAINED_FROM_CONTENT` e `PROFILE_VIEW_FROM_CONTENT`.
- Uma chamada por métrica por post: onze métricas são onze requisições.
- Aviso da própria doc: `RESHARE`, `REACTION` e `COMMENT` no finder `me` **não batem com a
  interface** ("not consistent with UI at the moment"), e os dados são "best-effort".
- Depreciação: a versão 202510 (Marketing October 2025) sai do ar em 15/10/2026; usar API
  versionada com o header `Linkedin-Version`.

**Permissão:** `r_member_postAnalytics` ("Retrieve your posts and their reporting data").

**Acesso:** é produto com revisão. A tabela de produtos coloca o Community Management API
como *vetted*, com **Development Tier** (limite de chamadas: 500 por app, 100 por membro) e
**Standard Tier** (exige formulário e screencast demonstrando cada caso de uso). O pedido sai
pelo "increasing access" no portal do desenvolvedor.

### O bloqueio para automatizar de ponta a ponta

Listar os próprios posts exige `findPostsByAuthors`
(`GET https://api.linkedin.com/rest/posts?author=<person urn>&q=author`), que pede
`r_member_social` — e a própria doc diz que essa permissão é **fechada**: "We're not
accepting access requests at this time due to resource constraints".

Consequência prática: mesmo com `r_member_postAnalytics` aprovado, o URN de cada post
teria que vir de fora da API (daqui, da lista de melhores posts da página de análise).
E, pior para o objetivo dele: a API **não** entrega a divisão na rede / fora da rede nem
a demografia, que são as duas leituras que mais explicam alcance. Por isso a coleta de
hoje é pela página.

## Estados possíveis e o que fazer

| Situação | Ação |
|---|---|
| Store existe, `check` mostra posts | só coletar os posts novos e re-coletar os recentes (métrica cresce) |
| Página sem "Publicações de melhor desempenho" | esperar mais e salvar de novo |
| Demografia vazia | a seção carrega por último; reabrir a página e salvar |
| Parser fora do formato depois de mudança do LinkedIn | `selftest` mostra o que quebrou; atualizar `fixtures/` com um snapshot novo |
| Interface em inglês | os rótulos do parser precisam dos equivalentes em inglês (`Impressions`, `Members reached`, `On-network`, `Off-network`, `Reactions`, …) |

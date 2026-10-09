---
name: terras-linkedin-metricas
description: Extrai, guarda e diagnostica as estatísticas dos posts do LinkedIn: impressões, alcance dentro e fora da rede, reações, salvamentos, seguidores e público. Use para analisar desempenho, entender por que um post rendeu ou não, comparar posts ou montar relatório.
keywords: [linkedin, metricas, estatisticas, desempenho, impressoes, alcance, alcancados, fora da rede, engajamento, salvamentos, comentarios, seguidores, publico, demografia, relatorio, diagnostico, post rendeu, analytics]
---

# Métricas dos posts do LinkedIn

Este é o lado de medição do LinkedIn: coleta os números das páginas de análise,
guarda histórico e produz o diagnóstico de por que cada post rendeu ou não, e qual
público ele alcançou. O lado de escrita é a skill `terras-linkedin`; as duas se
completam (aqui se mede, lá se escreve com o que a medição mostrou).

## Onde está instalada

Fonte única: `skills/terras-linkedin-metricas/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## O que tem aqui

| Peça | O que faz |
|---|---|
| `scripts/linkedin_metricas.py` | CLI: ingere snapshot, guarda store com histórico, liga métrica ao arquivo do workspace, gera relatório e o pacote de saída |
| `scripts/exportar.py` | Monta a planilha (template da skill `xlsx`), o CSV e o pacote JSON/YAML |
| `fixtures/` | Snapshots reais usados no `selftest` (regressão do parser) |
| `references/fontes-de-dados.md` | Mapa verificado das páginas, o que cada uma dá, e o estado da API oficial |

O CLI **nunca fala com o LinkedIn**: quem fala é o navegador, e o snapshot vira arquivo
antes de entrar. Dependências: o núcleo (ingerir, relatório, JSON, YAML, CSV) roda com
Python puro mais `pyyaml`; só a planilha precisa de `openpyxl`
(`python3 -m pip install --user --break-system-packages openpyxl`). Sem ele, o resto do
pacote sai igual, com aviso no terminal.

## O fluxo (cinco passos)

1. **Abrir e salvar** as páginas de análise no navegador in-app (que já tem a sessão
   dele) e escrever cada snapshot em `metricas/raw/<nome>-<AAAA-MM-DD>.txt`.
2. **Ingerir**: `python3 scripts/linkedin_metricas.py ingerir metricas/raw`
3. **Ligar aos arquivos**: `python3 scripts/linkedin_metricas.py atributos`
4. **Relatório**: `python3 scripts/linkedin_metricas.py relatorio`
5. **Pacote de saída**: `python3 scripts/linkedin_metricas.py exportar` (planilha, CSV,
   JSON e YAML; `--somente json yaml` limita os formatos)

Antes de qualquer coisa, `check` diz o estado do store e o que já foi coletado.
Se algo parecer errado no parser, `selftest` compara com os snapshots de referência.

No workspace do Everton o diretório de dados é `/home/support/linkedin/metricas`
(configurado em `~/.config/terras-linkedin-metricas/config.json`), então os comandos
funcionam sem flag a partir de qualquer lugar. Em outro diretório, `--dir` e
`--workspace` apontam os caminhos.

## Como coletar (receita verificada)

Cada página tem que ser aberta, esperada e salva. O snapshot precisa começar com a
linha `URL: <endereço>` porque é dela que o parser descobre o tipo de página.

| Página | URL | O que rende |
|---|---|---|
| Análise de conteúdo | `https://www.linkedin.com/analytics/creator/content/` | Agregado da janela: impressões, alcance, na rede / fora da rede, engajamento, série diária do gráfico, demografia e a lista de melhores posts (com URN de cada post) |
| Lista de melhores posts | `.../analytics/creator/top-posts/?endDate=…&startDate=…&metricType=IMPRESSIONS&timeRange=past_7_days` | **Enumera todo o acervo da janela**, não só os três primeiros. Por post: variação de impressões na janela, reações, comentários e idade. É a página que responde "quantos posts eu tenho" |
| Análise de público | `https://www.linkedin.com/analytics/creator/audience/` | Total de seguidores, novos seguidores e demografia dos seguidores |
| Análise de um post | `https://www.linkedin.com/analytics/post-summary/<urn:li:activity:...>/` | Números de **tempo de vida** daquele post: impressões, alcance, na rede / fora da rede, reações, comentários, compartilhamentos, salvamentos, envios, views de perfil, seguidores ganhos e demografia |

O widget "Publicações de melhor desempenho" da página de conteúdo mostra só **três** posts.
Quem quer o acervo clica em "Exibir mais" e cai na lista completa. Foi assim que a diferença
apareceu: o widget dizia 3, a lista dizia 34 na mesma janela. Quando o pedido for "todos os
meus posts" ou "por que só esses", a resposta é a lista, não o widget.

Regras que evitam retrabalho:

- **Esperar as seções preguiçosas.** "Publicações de melhor desempenho" e "Principais
  dados demográficos" chegam depois do resto. Sem espera, o snapshot sai sem elas.
- **Salvar sempre com o cabeçalho `URL:`.** Sem ele o tipo de página não é detectado.
- **A interface dele está em português.** Os rótulos que o parser procura são
  `Impressões`, `Usuários alcançados`, `Na rede (seguidores e conexões)`, `Fora da rede`,
  `Reações`, `Comentários`, `Compartilhamentos`, `Salvamentos`, `Envios no LinkedIn`,
  `Visualizações do perfil a partir desta publicação`, `Seguidores obtidos com esta publicação`,
  `Total de seguidores`. Em conta com a interface em inglês, o parser precisa dos
  equivalentes.
- **A janela não é o tempo de vida.** O filtro (7/28/90 dias) vale para os agregados e
  para a lista de melhores posts; a página de um post mostra o acumulado desde a
  publicação. São leituras diferentes, e misturar as duas produz diagnóstico errado.
- **O gráfico é cumulativo** enquanto "Cumulativo" estiver marcado: o último ponto é o
  total da janela, não o do dia.
- **A lista de melhores posts traz o URN** de cada post (o link "Ver análise") e o URN
  do share (o link do post). É de lá que saem os endereços das páginas individuais.
  Para ver mais posts, o "Exibir mais" leva para a tabela de top posts da janela.
- **Ritmo de gente, não de robô.** Uma página por vez, com espera de carregamento, sem
  varrer lista de dezenas de posts de uma vez, sem rodar em laço com intervalo fixo
  apertado. Uma coleta semanal dos posts novos é o suficiente: métrica de LinkedIn não
  muda de hora em hora.
- O botão **Exportar** existe nas páginas de conteúdo e de post, mas ainda não foi
  testado: se um dia ele entregar arquivo, vira o caminho de coleta em massa (e aí o
  parser ganha um leitor de CSV/XLSX em vez de snapshot).

## O que o relatório entrega

`relatorio` escreve `metricas/relatorio-<data>.md` e imprime no terminal. Ele traz:

- **Conta**: seguidores, novos seguidores na janela, agregado da janela (impressões,
  alcance, na rede / fora da rede, engajamento) e a demografia da janela.
- **Posts com métrica**: tabela ordenada por impressões com alcance, fora da rede,
  engajamento, salvos, comentários, views de perfil e seguidores.
- **Eficiência**: alcance/impressões, salvos/reações, comentários/reações, views de
  perfil e seguidores por mil impressões. É aqui que se vê se o post foi consumido ou
  só visto.
- **Cauda da janela**: quantos posts o LinkedIn enumera na janela, quanto os três primeiros
  concentram e quantos ficaram na casa de dez impressões. É a leitura que impede confundir
  "meus posts" com "os três que o widget mostrou".
- **Vencedor contra a mediana** e o **que separa os posts** por atributo do texto
  (âncora de prazo, material salvavel, número no hook, data no hook, pergunta no fim).
  Só afirma separação quando há pelo menos 2 posts de cada lado; com amostra menor,
  diz isso em vez de inventar causa.
- **Público alcançado contra o público que você quer**: seguidores, quem foi alcançado
  na janela, público do post que estourou, e a leitura do descompasso. O alinhamento com
  o alvo é por fonte (cada coluna pode cair em lado diferente do alvo: seguidores em São
  Paulo, o post vencedor em Londres). O pacote JSON/YAML e a aba Público carregam
  `alinhamento` como objeto com `seguidores`, `janela` e `post_vencedor` (schema v2);
  comparar fonte única escondia o caso em que o post vencedor acerta o alvo e a média não.

Os atributos do texto saem do arquivo `post-*.md` do workspace quando ele existe
(o parser casa por similaridade do texto publicado) e, quando não existe, do próprio
texto publicado capturado do LinkedIn. O relatório diz de onde veio.

## Tags internas e pontuação por tipo (o aprendizado)

Foco definido por ele em 24/09/2026: posts de autoridade, onde a densidade importa mais que o
alcance. Para aprender e registrar os tipos de post, cada post do store carrega `tipo` (a tag
principal), `tags` (todas) e `origem_tipo`.

**Tags da taxonomia**, em ordem de prioridade (o primeiro casamento vira o principal):

| Tag | O que é | Motor |
|---|---|---|
| `mudanca-com-prazo` | fim de suporte, deprecação, breaking change, expiração | alcance |
| `resiliencia` | retry, idempotência, incidente, rollback, cache stampede | autoridade |
| `custo` | fatura, preço, cobrança, custo de uso | autoridade |
| `meta-conteudo` | digest, recap, share de Substack, post sobre posts | autoridade (baixa) |
| `ia-em-producao` | LLM, modelo, agente, harness, triagem | autoridade |
| `decisao-arquitetura` | ADR, trade-off, fila, camadas, acoplamento, migração | autoridade |
| `outro` | nada casou | conferir |

A atribuição é **heurística de palavra-chave** sobre o texto publicado, e o ajuste fino é
manual: `metricas/tipos-manuais.json` mapeia URN → lista de tags, e o manual vence a
heurística. Quando a heurística errar (um digest que cita o EOL de outros posts pescou a
palavra do resumo), pinar lá, nunca endurecer a palavra-chave para consertar um caso.

**Pontuações**, todas por mil impressões: densidade (engajamento), conversa (comentários),
utilidade (salvamentos), atração (views de perfil), conversão (seguidores). O
`scorecards_por_tipo` agrega por mediana e é o que diz qual tipo vale repetir: impressões
altas com pontuação baixa é post de distribuição; impressões baixas com densidade alta é post
de autoridade, que é o foco.

Onde aparece: seção "Pontuação por tipo de post" no relatório, `scorecards_por_tipo` no
pacote JSON/YAML (schema v3) e colunas Tipo/Tags na planilha e no CSV.

## Pacote de saída (para analisar fora daqui)

`exportar` escreve quatro arquivos em `metricas/`, todos com a mesma data de coleta no
nome, para o Everton levar para outra ferramenta ou para outro agente:

| Arquivo | Para quem |
|---|---|
| `linkedin-metricas-<data>.xlsx` | Leitura humana e análise: abas **Posts** (tudo por post, com razões calculadas por fórmula), **Janela (todos)** (o acervo inteiro da janela, inclusive os posts ainda sem coleta de tempo de vida), **Conta**, **Público**, **Séries** e **Leia-me**, mais gráfico de impressões por post e a série da janela |
| `linkedin-posts-<data>.csv` | Planilha, pandas ou Google Sheets; separado por ponto e vírgula, que o Excel em português abre sem ajuste |
| `linkedin-metricas-<data>.json` | Outro MCP, agente ou modelo (JEV, Laya): chaves em ASCII, tipos de verdade e nada de `""` onde o dado é desconhecido (é `null`) |
| `linkedin-metricas-<data>.yaml` | O mesmo conteúdo do JSON, em YAML, quando o consumidor preferir |

O pacote JSON/YAML é uma **interface**, não o store: ele carrega `schema` e
`schema_version`, a data e a janela da coleta, a lista de `limites` (o que a leitura não
autoriza concluir), o `alvo` do autor, um `dicionario` de campo e, por post, os
`atributos` do texto, as `metricas`, as `derivadas` já calculadas, a `demografia` e o
`historico` de coletas, mais o array `posts_sem_coleta_de_vida` (a cauda da janela). Os
atributos vêm marcados com `"metodo": "heuristica"`: quem for
analisar precisa saber que aquilo é pista de texto, não medição.

A planilha passa pelo pipeline da skill `xlsx` antes de sair: `recalc` (LibreOffice),
`audit`, `scan`, `chart-verify` e `validate`, mais o gate visual nas páginas renderizadas.
Se mexer no exportador, rodar de novo: `recalc` tem que dar zero erro e `validate` tem que
sair com código 0.

## O que fazer com o resultado

- Quando um post sai da rede, olhar o público dele antes do número: no caso medido, o
  post que estourou alcançou **Sênior** e Londres, enquanto a média da janela era
  **Iniciante** e São Paulo. O assunto decide quem chega.
- Alto salvamento com reação baixa significa material de consulta, não conteúdo de
  conversa: vale repetir o formato, não necessariamente o tema.
- Muita impressão com view de perfil perto de zero quer dizer que o post não levou
  ninguém ao perfil; quando o objetivo é vaga, isso pesa mais que engajamento.
- Levar o achado para a `terras-linkedin`: o que se repete é o esqueleto que a medição
  confirmou, não a lista de dicas genéricas.

## Risco e limites (ler antes de automatizar)

A coleta é leitura da própria página de análise, na sessão já autenticada dele, em
ritmo humano. Mesmo assim, o Acordo do Usuário do LinkedIn restringe acesso por meio
automatizado, e o risco de restrição de conta existe; por isso a coleta é disparada
por pedido, em volume baixo, e não existe aqui nada de disfarce, rotação de proxy ou
evasão de detecção. Não aumentar o volume por conta própria.

O caminho oficial existe e está mapeado em `references/fontes-de-dados.md`
(`memberCreatorPostAnalytics`, escopo `r_member_postAnalytics`, produto com revisão).
Ele dá os contadores por post, mas **não** dá a divisão na rede / fora da rede nem a
demografia, que são justamente as duas leituras mais úteis daqui, e a permissão para
listar os próprios posts está fechada. Vale reavaliar se ele um dia tiver página de
empresa e app aprovado.

## Limites do diagnóstico

- Impressões e alcance do LinkedIn são "best-effort" e mudam depois da coleta; o store
  guarda cada coleta com data, então comparação só é justa entre coletas próximas.
- Amostra pequena: com menos de uns 8 posts publicados, o relatório descreve caso, não
  tendência.
- Não existe peso público de distribuição. O relatório lê os dados; não promete regra.

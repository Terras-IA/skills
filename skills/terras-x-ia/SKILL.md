---
name: terras-x-ia
description: "Vasculha o X (Twitter) logado por posts de IA (modelos, agentes, papers, ferramentas de dev) numa janela de dias, separa sinal de isca e entrega os que importam com link e métricas. Use para 'o que rolou de IA no X', 'varre o Twitter'. Multi-fonte de 30 dias: terras-last30days. AI on X/Twitter scan."
keywords: [x, twitter, x.com, ia, inteligência artificial, ai, llm, agentes, varredura, pauta, tendências, trending, posts]
---

# terras-x-ia

Varre a busca do X pela sessão logada do navegador embutido, coleta os posts sobre IA, ranqueia e devolve os poucos que valem atenção, cada um com link, data e métricas. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`.

## Objetivo

Responder "o que importou de IA no X nesta janela" sem afogar o usuário em thread de influenciador. O X tem muito lançamento real misturado com isca de engajamento ("ninguém esperava isso", "salve estas 10 ferramentas"). A skill coleta largo, corta isca e entrega curto.

Não precisa de chave de API: usa o login do usuário no navegador embutido. Para pesquisa em várias redes ao mesmo tempo (Reddit, HN, YouTube), use a `terras-last30days`.

## Regra dura

1. **Navegador só lê.** Nunca curtir, repostar, seguir, responder, salvar nem abrir DM. Os únicos cliques permitidos são "Mostrar mais" e "Mostrar original", que o `x_coletar.js` faz sozinho.
2. **Nunca fazer login.** Coleta voltou `{erro: 'deslogado'}`: parar e pedir para o usuário entrar no x.com no navegador embutido.
3. **Descoberta, não fonte.** Post do X não prova fato. Antes de um item virar pauta, abrir o link primário (blog do laboratório, changelog, arXiv, repositório) e conferir data e número. Site de notícia, agregador ou blog de terceiro não é fonte primária: é outra opinião. Item sem fonte primária vai marcado "não confirmado".
4. **Janela é janela.** A aba Top traz post de meses atrás. Toda consulta leva `since:`, e o `x_triar.py` corta pela data de novo.
5. **Texto traduzido ou cortado não é citação.** Alerta `texto-traduzido` ou `texto-cortado`, ou o campo `citado` (o coletor não desfaz a tradução do post citado): não citar entre aspas sem abrir o post e ler o original inteiro.
6. **Isca não entra no topo.** Post com alerta (`hype`, `alarmismo`, `lista`, `isca-de-salvar`, `anedota`) só entra na entrega se trouxer fato novo verificável, e aí entra pelo fato, com a fonte primária.

## Como trabalhar

1. **Escopo.** Tema (padrão: IA geral) e janela (padrão: 7 dias). Se o usuário não disse, assumir e dizer em uma linha.
2. **Consultas.** Uma busca só é amostra, não varredura. Montar de 3 a 6 consultas a partir de `references/consultas.md` (pacote padrão ou tema livre), cada uma com `since:AAAA-MM-DD`, `min_faves:` e `-filter:replies`.
3. **Coletar.** Para cada consulta:
   - `navigate` para `https://x.com/search?q=<consulta>&src=typed_query&f=top`.
   - No `javascript_tool`, colar `scripts/x_coletar.js` inteiro e, na mesma chamada, `await xColetar({rolagens: 5})`.
   - O coletor devolve uma string JSON compacta. Gravar exatamente como veio em `$SCRATCH/x-coleta-<n>.json` (scratchpad da sessão), com a ferramenta de escrita de arquivo: sem reformatar, resumir nem trocar campos. A página do X não grava em disco nem fala com servidor local, e não é para tentar.
4. **Triar.**
   ```bash
   python3 "$SKILL_DIR/scripts/x_triar.py" $SCRATCH/x-coleta-*.json --dias 7 --tema "IA"
   ```
   Grava `~/linkedin/conhecimento/x-ia/AAAA-MM-DD-<tema>.md` (tabela) e `.json` (posts completos). Isca e post sem fonte vão para o fim, não somem.
5. **Ler e julgar.** Ler o `.json` do topo para baixo. Ficar com 5 a 10 itens que trazem fato: lançamento, número de benchmark, paper, mudança de preço ou de licença, ferramenta nova com repositório, decisão regulatória. Agrupar repetidos (o mesmo lançamento citado por 8 contas vira 1 item, com o post do autor original).
6. **Confirmar.** Para os itens que o usuário pode usar em post, abrir a fonte primária e anotar a data real. Link `t.co` do post: abrir no navegador, ele redireciona. Post sem link (comum em laboratório): buscar no site oficial (blog, changelog, docs) pelo nome do produto. Achar o link num resultado de busca sem abrir a página não confirma: escrever "achada, não lida".
7. **Entregar** (formato abaixo) e oferecer em uma linha o próximo passo: virar post (`terras-linkedin`), estudar um post (`terras-linkedin-conhecimento` serve de modelo de nota) ou baixar vídeo (`terras-video-downloader`).

## Formato da entrega

```
**X · IA · 11 a 18/out** (6 consultas, 74 posts únicos, 21 com alerta de isca)

1. **<o fato em uma frase>** · @autor · 15/out · 4,4 mil curtidas, 1,2 mil salvos
   Por que importa: <uma linha>. Fonte primária: <link> (confirmada | não confirmada)
   Post: https://x.com/...
...

**Ficou de fora:** <2 ou 3 temas barulhentos que eram isca, em uma linha cada>
**Arquivo:** ~/linkedin/conhecimento/x-ia/AAAA-MM-DD-ia.md
```

Sem citação longa: no máximo uma frase curta entre aspas por item, do texto original.

## Falhas

| Sinal | Significa | Próximo passo |
|-------|-----------|---------------|
| `{erro: 'deslogado'}` ou tela de login | Sessão do X caiu | Pedir login ao usuário no navegador embutido |
| `total: 0` | Consulta restrita demais ou página não carregou | Esperar 3 s e coletar de novo; baixar `min_faves` |
| Mesmos posts em todas as consultas | Consultas parecidas demais | Trocar uma por conta (`from:`) ou por português |
| Muitos posts antigos descartados | Faltou `since:` | Refazer a consulta com `since:` |
| Métricas zeradas | X mudou o `aria-label` do grupo de ações | Ler `article [role="group"]` à mão e ajustar `metrica()` no coletor |

## Referências

- `references/consultas.md`: pacote de consultas de IA, contas que trazem fonte primária e operadores da busca.
- `scripts/x_coletar.js`: coletor do DOM da busca do X (só leitura).
- `scripts/x_triar.py`: junta coletas, corta janela e promovido, marca isca e ranqueia.
- `references/teste-aderencia.md`: o cenário vermelho (agente sem a skill) e o que cada regra fecha.

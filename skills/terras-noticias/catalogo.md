---
name: terras-noticias
description: Lê boletins e roundups de notícias de IA, tria por criticidade e prioridade, resume os itens e escreve o rascunho do post de digest para o LinkedIn. Use para link de boletim semanal, resumo ou triagem de notícias, digest ou o que saiu na semana.
keywords: [notícias, noticias, news, boletim, roundup, digest, ratos de ia, ratos, triagem, prioridade, criticidade, resumo semanal, news digest, weekly recap]
---

# Notícias — ler, triar e virar digest

## Objetivo

Pegar uma edição de boletim/roundup (o ratos de IA é a fonte canônica) e devolver
três coisas: a **triagem** de todos os itens (criticidade × prioridade), o
**resumo rápido de todos** e o **rascunho do post de digest para o LinkedIn**.
O valor não é resumir notícias: é separar o que muda a operação e a pauta do
que é ruído com data marcada, e transformar a seleção num post que se lê em
diagonal.

## Onde está instalada

Fonte única: `skills/terras-noticias/` no repositório `terrasia-skills`. Cada
agente enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh`
do repositório, então a edição se faz lá e vale para todos. Nos comandos
abaixo, `$SKILL_DIR` é a pasta onde este `SKILL.md` está. Os digests saem em
`~/Documents/Desenvolvimento/noticias/YYYY-MM-DD-<fonte>-epNN.md`. Funciona de
qualquer workspace.

## O insumo

- **Um link de boletim** (ex.: `https://ratos.link/ep36/`): a página lista os
  itens por seção, cada um com manchete curta, uma linha de descrição e o link
  da origem (quase sempre um post no X). Leia a página inteira (uma requisição
  HTTP resolve) e trate **cada item** como linha da triagem.
- **Uma lista de links** solta: mesmo fluxo, item por item.
- Idioma do boletim não importa (ratos é PT-PT); a saída é **PT-BR**. Traduza
  conceitos, nunca cite como literal o que foi traduzido.

## Regra dura: boletim é ponteiro, fonte primária confirma

- Fato que vai para o post (número, data, versão, preço, limite de plano) se
  confirma na **fonte primária**: release notes, blog oficial, changelog,
  documentação. O boletim e o post no X são pistas, não prova.
- Link de X abre direto (a página devolve texto, data e engajamento). Se
  falhar: `curl -sL "https://publish.twitter.com/oembed?url=<url>&omit_script=1"`.
- O que não confirmar entra na triagem marcado `⚠️`, mas **não vira afirmação
  no post**: ou sai, ou vira pergunta. Data ou versão errada derruba a
  credibilidade do post inteiro (mesma regra da `terras-linkedin` e da
  `terras-last30days`).

## Como trabalhar

1. **Coletar.** Leia a página inteira → lista completa de itens com seção,
   manchete e link. Registre a data de leitura.
2. **Verificar o que importa.** Abra a fonte dos candidatos a P0/P1 e de todo
   fato que o post vai afirmar. Itens de ruído não gastam requisição. Fonte que
   bloqueia acesso direto (openai.com devolve 403) se verifica no snapshot do
   Wayback, com a URL do snapshot entrando no anexo do digest.
3. **Julgar** com a rubrica abaixo. Duplicatas (réplica, repost, amplificação
   do mesmo anúncio) viram **uma linha só**, herdando a nota do original.
4. **Resumir** no template de `$SKILL_DIR/references/digest-template.md`:
   triagem com todos os itens, destaques expandidos e ruído.
5. **Escrever o post** (regras abaixo; estrutura e tom são da `terras-linkedin`).
6. **Salvar** em `~/Documents/Desenvolvimento/noticias/YYYY-MM-DD-<fonte>-epNN.md`,
   digest e post no mesmo arquivo, post pronto para copiar. Discord só se o
   pedido incluir (via `~/Documents/Desenvolvimento/discord-post.sh`).

## Julgar: criticidade × prioridade

Dois eixos independentes. Um item pode ser crítico sem ser prioritário para
você (mudança de mercado que ainda não te toca) e vice-versa.

**Criticidade — o tamanho da consequência do fato para quem trabalha com
tecnologia (dev, staff, arquitetura, liderança), se ignorar:**

- **Alta** — obriga ação ou mexe em dinheiro, prazo ou risco: breaking change,
  descontinuação, preço ou limite de plano, falha de segurança, mudança de
  licença ou de API. Teste: dá para escrever um "o que fazer" em uma linha?
- **Média** — muda prática ou decisão nos próximos meses: capacidade nova que
  substitui um fluxo, número de adoção que calibra investimento, movimento que
  afeta escolha de ferramenta.
- **Baixa** — informativa: opinião, previsão, drama, feature sem consequência
  prática.

**Prioridade — quando o item toca a operação e a pauta do usuário (Everton):
o que ele usa, opera e publica.**

- **P0 — hoje**: mexe no que ele usa ou opera agora (ferramentas da rotina,
  custo das assinaturas, automações, o que rende post imediato). Verificar e
  agir primeiro.
- **P1 — esta semana**: entra na pauta, no teste ou na decisão desta semana.
- **P2 — fila**: interessante, sem ação; guardar.
- **P3 — ruído**: não vira ação nem conteúdo.

**Anti-inflação (é aqui que o julgamento falha):**

- A curadoria dá o mesmo peso a tudo; a triagem existe para separar. Num
  episódio de ~24 itens, espere **3 a 6 em P0/P1**; a maioria fica P2/P3.
- Lançamento famoso não é prioritário por ser famoso. Sobe se muda o que o
  usuário faz.
- Drama, trollagem e briga de egos são P3 mesmo com meio mundo falando.
- Novidade de modelo é Média/Alta por padrão; vira P0/P1 só com consequência
  concreta (custo por tarefa, limite, quebra, data).
- O título descreve o que muda, não o que foi anunciado ("plano de US$ 200
  volta com metade do uso", não "novidades de preço da OpenAI").

## Resumo rápido e destaques

- **Todos os itens** entram na triagem, uma linha cada, com o tema como coluna
  para a leitura em diagonal. Ordem: P0 primeiro. Coluna de **ação**: verbo
  concreto ("conferir limite do plano", "testar no próximo PR") ou "nada".
- **Destaques**: só P0/P1, expandidos em três bullets: o que é, por que
  importa, o que fazer, com o status de verificação.
- **Ruído**: uma linha com o que ficou de fora e por quê. Sem ela, o leitor
  não sabe se algo passou batido.

## O post de digest (LinkedIn)

Estrutura, tom e tom humano são da `terras-linkedin` — leia antes de escrever.
O que muda aqui:

- O post **não é a triagem colada**: selecione 2 a 4 itens com consequência
  (podem ser P1, não precisa ser o topo da tabela), agrupe em 2 a 4 blocos
  temáticos, e cada bloco diz o que muda de verdade, não o que foi anunciado.
- **Zero travessão (—)**, sem exceção. É o marcador de texto de IA e a falha
  mais comum do post de digest.
- Sem link no corpo (o algoritmo derruba alcance); as fontes ficam no arquivo,
  fora do post, ou no primeiro comentário se o usuário quiser.
- Primeiros ~210 caracteres fazem sentido sozinhos; fechamento com pergunta de
  escolha real.
- Alvo: 1.300 a 1.800 caracteres. O digest pode passar da banda principal da
  `terras-linkedin`, com seleção; listão de 24 itens não é digest.
- Abertura pelo problema, não pelo lançamento.

## Referências

- `$SKILL_DIR/references/digest-template.md` — template exato do digest
  (triagem, destaques, anexo de fontes), com exemplo preenchido e as regras de
  cada linha.
- `$SKILL_DIR/references/fontes.md` — ratos de IA (padrão de URL e cadência),
  como abrir cada tipo de link e o contrato de uma boa fonte.

## Limites conhecidos

- O que o boletim não linka não entra (ex.: análise citada sem link). Número
  que só existe no texto do boletim vai marcado `⚠️` e não vira fato no post.
- Episódio ainda em montagem (sem os links todos) → diga isso na ficha.
- São ~20-25 requisições por episódio de ~24 itens. Não é motivo para pular a
  verificação dos P0/P1 nem dos fatos que o post afirma.

## Exemplos de uso

- "https://ratos.link/ep36/ — são fontes boas de notícias. leia as notícias,
  julgue prioridade e criticidade, resumo de todos e um possível post"
- "saiu o ep37, faz o digest"
- "resumo das notícias dessa semana" (sem link → pedir a fonte ou usar o
  índice em https://ratos.link/)
- "triagem desses links" (com lista colada)

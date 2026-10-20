# Teste de aderência

## Cenário

"Varre meu feed do LinkedIn e traz o conhecimento de todos os posts das últimas 24 horas, ou de tudo que saiu desde a última vez que você verificou." Navegador embutido logado no LinkedIn, painel escondido.

## Vermelho (2026-10-20)

Duas fontes: o plano de um agente que tinha só a `terras-linkedin-videos` e a `terras-linkedin-conhecimento`, e o que deu errado na exploração ao vivo do feed antes de existir o coletor.

| Falha observada | Regra ou mecanismo que fecha |
|---|---|
| Usaria `feedColetar`, que rola `window`; no feed quem rola é `#workspace`, e a coleta parou em 3 posts | `feed_varrer.js` rola `#workspace`; `references/feed.md` |
| Data pelo rótulo "3 h" no texto do card, ou pelo `datePublished` cortado no dia | Regra dura 3: data do ID da URN (`id >> 22`) |
| URN post a post por menu "..." e diálogo "Incorporar" (clique, lento, ausente na interface nova) | Coletor lê a URN das props do React, sem clique (regra dura 1) |
| Parada "3 cards seguidos fora da janela" num feed que não é cronológico, teto fixo de rolagens | Parada por rodadas sem post novo na janela; `?sortBy=RECENT` não existe; limite dito na entrega |
| Não sabia do limite de 45 s por chamada nem do painel escondido que trava o scroll infinito | Coleta em fatias de 35 s com estado em `window`; linha de falha "carga esgotada com menos de 20 cards" |
| Uma carga só; não sabia que a carga de página esgota em 40 a 80 cards | Passo 4: novas cargas até a última trazer menos de 3 novos |
| Pediria escolha dos vídeos e confirmação antes de começar | Regra dura 4: chamar a skill é o sim; teto de 15 notas, excedente vira pendente |
| Atualizaria o estado "por último" sem tratar falha; post que falha cairia fora da próxima janela | Regra dura 5 e `pendentes` no estado |
| Reprocessamento só por pasta e glob de vídeo | `vistos` no estado (45 dias), `ja_estudado` por id6 e junção de cargas |
| Acertou: login conferido pelo título, promovido descartado, nota pelo modelo da conhecimento | Mantido |

## Verde (2026-10-20, agente com a skill, só plano)

Passou nas regras duras: data por `id >> 22`, URN sem clique, coleta em fatias com estado na página, novas cargas por `ultima_carga_novos`, destravamento por screenshot e roda, checkpoint só depois de notas e índice, falha e excedente como pendentes, descarte com motivo.

Brechas que ele achou e foram fechadas na mesma rodada:

| Brecha | Correção |
|---|---|
| "24 h ou desde a última" sem dizer qual vence; checkpoint de 10 min dá janela de 10 min | Passo 1: checkpoint vence, `--horas` só com janela nomeada |
| Post de antes do checkpoint mostrado tarde pelo feed caía fora para sempre | Margem de 6 h para trás no checkpoint; `vistos` evita repetir |
| Card sem link reaparecia toda rodada | `fechar` marca sem link como visto por autor e fim do texto |
| Pendente que falha sempre ficava preso | Teto de 3 tentativas; sai em `desistidos_apos_3_falhas` |
| Passo 8 supunha poder abrir agente auxiliar | Sem agente auxiliar, escrever em sequência |
| Achou conflito entre "chamar a skill é o sim" e pedir licença para download | Mantido: o download é da página pública do post pelos scripts das skills irmãs, e o pedido de varredura é o pedido explícito do usuário |

Repetir este cenário a cada mudança no coletor, no triador ou nas regras.

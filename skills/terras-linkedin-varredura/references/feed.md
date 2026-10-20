# O feed do LinkedIn por dentro (out/2026)

O que o `feed_varrer.js` assume e o que custou tempo descobrir. Complementa `terras-linkedin-videos/references/feed-dom.md`.

## Rolagem

- Quem rola é `<main id="workspace">`, não a janela. `window.scrollBy` não faz nada: foi assim que o `feedColetar` da skill de vídeo parava em 3 posts com o painel escondido.
- Uma carga de página entrega de 40 a 80 cards, em lotes de uns 5 a cada rolagem. Depois disso para de crescer e não há botão de "carregar mais" (os botões "Exibir mais" do rodapé são de notícias e jogos). Mais posts = recarregar o feed: cada carga traz outra mistura. Na medição de 20/out, a segunda carga repetiu 9 dos 13 posts na janela e trouxe 4 novos; daí a regra de parar quando uma carga traz menos de 3 novos.
- Com o painel do navegador escondido, a página às vezes nem começa o scroll infinito (fica nos 3 a 7 cards iniciais). Screenshot pequeno e uma rolagem pela roda do mouse (`computer scroll`) destravam. Depois de começar, o loop por `scrollTop` segue sozinho até o fim da carga, mesmo sem janela aberta.
- Cada `javascript_tool` morre em 45 s, mas o script continua rodando na página. Por isso o estado fica em `window.__varredura` e a coleta é em fatias de 35 s.

## Data e URN

- Não existe ordenação por data: `?sortBy=RECENT` redireciona para o feed comum.
- A URN (`urn:li:activity|ugcPost|share:<id>`) está nas props do React do botão "Abrir menu de controle da publicação de <Autor>", subindo até 80 níveis de fiber. Nenhum clique. Anúncio traz `activity` e `share` do mesmo post; o coletor fica com o maior ID.
- `id >> 22` é o epoch em ms da publicação. Conferido contra o rótulo dos cards ("há 19 h", "16 de out.").
- Card sem URN acontece em post de grupo e em "Fulano parabenizou". Data pelo rótulo (`ts_aprox`) e sem link: só segue se o texto valer muito.

## Tipo de mídia

- `<video>` e as imagens `feedshare` carregam depois do card. O mesmo post saiu como `video` numa carga e `texto` na outra. O coletor promove o tipo quando relê o card e o triador fica com o mais rico, mas o tipo que vale é o do `baixar_post.py` (`aviso: post tem vídeo`, `imagens`, `documento`).

## Ida ao disco

- A página não grava arquivo nem fala com servidor local. O `feedVarrerResultado()` devolve string JSON compacta (só janela, sem promovidos, texto cortado em 450) e o agente grava com a ferramenta de escrita.
- O CSP do LinkedIn barra `eval` (sem `unsafe-eval`): guardar o código no `sessionStorage` e reinstalar não funciona. Cola-se o arquivo a cada carga. Para não regravar o que a carga anterior já deu, `feedVarrerResultado(excluir)` recebe os ids e autores já gravados.
- Rótulo "Agora mesmo" (post de segundos atrás) não tem número: vale o instante da coleta.

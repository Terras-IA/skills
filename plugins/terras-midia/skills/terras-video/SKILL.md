---
name: terras-video
description: "Monta vídeo para YouTube e Shorts a partir de um roteiro: cartelas na identidade da marca, narração por voz neural, movimento fluido e mp4 pronto para publicar. Faz vídeo horizontal 1920x1080 e vídeo vertical 1080x1920, com área segura para a interface dos Shorts. Use quando o pedido envolver vídeo, vídeo vertical, YouTube, Shorts, Reels, TikTok, cartela, narração, locução, voz, trilha, mp4, 'faz um vídeo disso', 'faz um short', 'gera conteúdo em vídeo', ou quando o assunto for transformar um post, um digest ou um projeto em vídeo."
keywords: [video, youtube, shorts, reels, tiktok, vertical, 1080x1920, cartela, narracao, locucao, voz, tts, mp4, ffmpeg, edge-tts, roteiro, terrasia]
---

# Vídeo para YouTube

Transforma um roteiro em vídeo publicado: cartelas na identidade da casa, narração
em voz neural, movimento fluido e montagem em mp4. Não escreve o texto na voz do
autor (isso é a `terras-linkedin`) e não publica sozinho: entrega o arquivo e o
pacote de publicação.

## Onde está instalada

Fonte única: `skills/terras-video/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Regra de ouro

1. **O texto falado passa por aprovação antes de renderizar.** O `render` recusa
   roteiro sem `aprovado: true`. O caminho é: `plan` (imprime e salva o roteiro),
   leitura e ajuste, `aprovar`, e só então `render`. Nunca marcar como aprovado
   por conta própria.
2. **Nada de publicar sem pedido explícito.** O vídeo fica em disco; subir para o
   YouTube é ação externa e só acontece quando o usuário pedir.
3. **O gate visual roda nas cartelas antes de entregar** (`documents:visual-judge`
   lendo os PNGs). Cartela aprovada no encaixe automático ainda pode estar feia.

## Pipeline

1. **Roteiro.** Escrever `roteiro.json` com `titulo`, `formato`, `voice` e a
   lista de `blocks` (o `foot` só quando a assinatura do tema não serve para este
   vídeo; ela vem do `brand.json`, ver Identidade visual). Cada bloco tem `layout`,
   textos de tela e `narration` (o texto falado). Ver
   `templates/roteiro.exemplo.json` (horizontal) e
   `templates/roteiro.exemplo-shorts.json` (em pé).
2. **Plano.** `python3 scripts/build.py plan roteiro.json` escreve `out/roteiro.md`
   com o texto de tela e o falado de cada bloco, e a estimativa de duração. Mostrar
   ao usuário.
3. **Aprovação.** Depois do ok explícito: `python3 scripts/build.py aprovar roteiro.json`.
4. **Render.** `python3 scripts/build.py render roteiro.json`. Sai o mp4 em `out/`,
   junto das cartelas PNG, das narrações e dos trechos.
5. **Gate visual.** Passar as cartelas por `documents:visual-judge`; corrigir texto
   ou layout e renderizar de novo se reprovar.
6. **Entrega.** mp4 + cartelas + sugestão de título, descrição e tags. Com
   `--exportar`, o render também copia as cartelas e o vídeo para
   `$TERRAS_BRAND_DIR/exports/cartelas/<slug>/`, que é o ponto de encontro com o
   CapCut (importar os PNGs lá e aplicar a identidade dele). Publicação manual no
   YouTube Studio (ver abaixo).

## Cenas externas (o gerador do terrasia)

O Everton tem um gerador de cenas próprio no harness, em
`/srv/server-01/harness/terrasia/video-terrasia/gen_video.py` (PIL, 1920x1080, seis
cenas sobre a arquitetura do terrasia, paleta de produto com Noto Sans e DejaVu
Mono), e disse que essa é a solução que vai usar **prioritariamente** para os
vídeos do projeto. Um bloco de roteiro aceita `cena: {modulo, funcao, duracao}` no
lugar do layout de cartela: o `build.py` importa o módulo, desenha com a animação
dele e cobre o que falta, que é narração, fades, montagem em 60fps, checagens de
áudio e exportação. A duração do bloco é `max(narração + 0,6s, duração desenhada)`,
então a animação dele nunca é cortada; cena externa não passa pela checagem de
jerk, e o gate visual roda nos quadros extraídos do vídeo. Num canvas em pé, o quadro
16:9 dele entra encaixado (inteiro, sobre um fundo desfocado dele mesmo) ou recortado
com `"ajuste": "preencher"`.

Quando o pedido for vídeo sobre o terrasia, use as cenas do harness como base, não
o template de cartelas. Detalhes e as armadilhas de duração em
`references/identidade-e-movimento.md`.

## Formatos

| Uso | Tamanho | Observação |
|---|---|---|
| YouTube horizontal | `1920x1080` | Padrão para explicativo, demo e conteúdo técnico |
| Shorts, Reels, TikTok | `1080x1920` | `"formato": "shorts"`; cartela em pé e conteúdo dentro da faixa segura |
| Quadrado | `1080x1080` | Feed; raro para vídeo |

O roteiro escolhe com `"formato": "shorts"` (ou `"horizontal"`, ou `"quadrado"`), e um
`"size"` explícito ganha do formato. Sem nenhum dos dois, vale 1920x1080.

**A escala do tipo é fração do menor eixo**, não da largura de referência 1920: a
manchete tem sempre 9,6% dele, ou seja 104px em qualquer canvas. Com a conta antiga
(`min(w/1920, h/1080)`) o vertical caía para 0,5625 e a manchete saía com 59px, que no
celular não se lê. Para 16:9 as duas contas dão o mesmo número, então o horizontal não
mudou.

Duração: 30 a 90 segundos para Shorts, 3 a 8 minutos para explicativo. Cada bloco
rende o tempo da própria narração mais 0,6s de respiro, então o roteiro controla a
duração: uma cartela por ideia, e o corte acompanha a fala.

## Shorts (vertical)

Em pé, quatro coisas mudam de verdade:

- **Cartela própria.** `card-vertical.html` para os cinco layouts, e
  `card-canal-vertical.html` para o layout `canal`, que em pé vira foto de fundo com
  véu em vez de painel lateral: um painel de 31% da largura não cabe ao lado de uma
  coluna de 650px. Nos dois, os **números vão empilhados**, um por linha, com o valor à
  esquerda e o rótulo ao lado.
- **Área segura do player.** A interface dos Shorts come a faixa de cima e a de baixo.
  Medido em 2026-09-20 no player em 1080x1920, a pilha de botões começa a 81% da altura
  do quadro. A faixa livre vai de y 230 a 1382, e a cartela é **desenhada de 294 a
  1336**: a faixa livre encolhida pelo zoom de 6% e mais 24px de folga, senão o próprio
  movimento empurra o texto para dentro da interface. O `plan` imprime a conta, e a
  checagem de encaixe reprova cartela que sair da faixa.
- **Teto de 3 minutos**, que é onde o YouTube deixa de classificar como Short. O `render`
  recusa antes de gerar quando a estimativa passa disso, e avisa depois se o vídeo final
  passou.
- **Cena externa 16:9 entra encaixada**, inteira e centrada sobre um fundo desfocado
  dela mesma (`"ajuste": "preencher"` corta as laterais em vez de encaixar). Sem isso o
  pipe do ffmpeg desalinha e sai vídeo embaralhado, sem erro nenhum.

Roteiro de partida em `templates/roteiro.exemplo-shorts.json`. O `pacote` de publicação
reconhece o formato: acrescenta `#Shorts` na descrição, põe `Shorts` nas tags e devolve
as notas do vertical (os capítulos, que o vídeo longo ganha, o Short não ganha: em 30
segundos a divisão não ajuda e o YouTube não monta). A cartela 1 **não** serve de
miniatura no feed, porque ali o Short pega um quadro do vídeo; a miniatura oficial vale
no canal e na busca.

## Vídeo do carrossel (slides do deck)

O carrossel que a `terras-banner` já renderizou vira vídeo narrado: o roteiro pede
`"formato": "carrossel"` (1080x1440, o 3:4 do deck) e cada bloco aponta para um slide
com `slide` no lugar do layout de cartela. A página pronta é o quadro inteiro, então
não há cartela HTML aqui, nem área segura de Shorts: o destino é o feed, e o slide já
passou pelo check e pelo gate da `terras-banner`.

```json
{ "slide": "deck-adr-linkedin-01.png", "narration": "..." }
```

- O caminho do slide é relativo ao arquivo do roteiro, não ao diretório do shell.
- O `size` do roteiro casa com o do deck (1080x1440). Se diferir, o slide é encaixado
  no canvas com aviso, e o encaixe não é opcional: quadro de tamanho diferente desalinha
  o pipe do ffmpeg e sai vídeo embaralhado, sem erro.
- Ordem dos blocos é a ordem dos slides. No LinkedIn vale a variante `linkedin` do deck
  (`deck-<slug>-linkedin-NN.png`), que é a aprovada para a leitura no app.
- Movimento: o mesmo zoom lento, com teto `ZOOM_SLIDE` de 1,05. Medido no deck do ADR
  (seis slides): o texto fica a 62px da borda mais próxima, o zoom de 1,05 recua 26px
  nas laterais e 34px no topo/base sem cortar nada, e o de 1,04 reprova no jerk (1,08
  contra o teto de 1,0, porque com recuo pequeno a mediana cai e a irregularidade
  relativa sobe). O bloco aceita `zoom` próprio.
- A montagem é a de sempre: fade para preto nas pontas de cada slide, narração por
  bloco com 0,6s de respiro, concat e as checagens de movimento e de loudness. Sem o
  teto de 3 minutos dos Shorts.
- O `--exportar` copia o quadro usado de cada slide (`cartela-N.png`) junto do vídeo.
- Pronúncia: o `plan` lista os termos de risco. `rabbitmq` entrou no dicionário da
  `terras-audio` em 26/09/2026 como `Rábiti eme quê` (palpite calibrado com o Whisper:
  o texto cru saía irreconhecível, "Hebtiemic"), e falta a escuta dele.

### Narração em inglês

O vídeo do carrossel em inglês (o par EN do post) precisa de três coisas que o roteiro
em português não pede:

- **`"sotaque": "nenhum"`, obrigatório.** O dicionário da `terras-audio` existe para
  achar termo inglês dentro de frase portuguesa (`cache` -> `kêsh`, `queue` -> `kiu`) e
  num roteiro todo em inglês ele reescreveria palavra comum e destruiria a fala. O
  `build.py` avisa quando isso acontece (`avisar_sotaque`), e o roteiro declara também
  `"lang": "en-US"`.
- **Voz própria.** O padrão em inglês é `en-US-AvaMultilingualNeural` (escolhida em
  26/09/2026 para o vídeo em EN do ADR, mantendo o timbre feminino da casa), com
  `en-US-AndrewMultilingualNeural` e `en-US-EmmaMultilingualNeural` como alternativas
  já ouvidas na análise. A Thalita, voz da casa em português, lê inglês de forma
  inteligível, mas é voz pt-BR.
- **Termo com letras separadas.** `RabbitMQ` junto sai "Rabatai Imkay" nas quatro vozes
  testadas; `Rabbit M Q` (e também `Rabbit M-Q`, `Rabbit Em Cue` e `Rabbit M Queue`)
  sai transcrito como `RabbitMQ`, que é a pronúncia certa. Vale para sigla em geral:
  o TTS lê as letras quando elas vêm separadas.
- O relatório de pronúncia da `terras-audio` é pulado no `plan` de roteiro em inglês:
  ele procura termo inglês dentro de texto português e listaria "the", "with", "what".

## Temas

O roteiro aceita `"tema": "pessoal"` (padrão), `"tema": "terrasia"` ou
`"tema": "youtube"`. O tema vive em `$TERRAS_BRAND_DIR/brand.json`, na chave
`temas`, e define cores **e fonte**:

| Tema | Cara | Fonte |
|---|---|---|
| `pessoal` | navy escuro com acento âmbar, a identidade dos posts | Inter |
| `terrasia` | tema do produto: base `#060608`, neon verde `#00ff9d` e ciano `#00f0ff`, texto `#e8e8f0`, linha `#1a1a2e` | JetBrains Mono |
| `youtube` | identidade do canal, tirada do title card dele: base `#020617`, ciano `#22d3ee`, manchete `#10bedb`, texto `#f8fafc` | Inter + JetBrains Mono |

O tema `terrasia` foi extraído do próprio projeto, não copiado de imagem:
`packages/ui/src/colors.ts`, o `:root` de `terrasia-client/src/index.css` (que também
traz a variante clara, guardada em `tema_claro`) e a fonte, que veio dos `.woff2`
empacotados em `terrasia-site/dist/assets`. O tema `youtube` foi medido pixel a pixel
no `TerrasIA Title Card Template.png` que ele exportou do CapCut, com as fotos e os
fundos dele em `art/`; o resumo está em `$TERRAS_BRAND_DIR/identidade-youtube.md`.
Ordem de precedência: `base`/`accent` no roteiro ganham de tudo, depois o tema,
depois as cores de topo do `brand.json`.

**Layout `canal`.** É a cartela do tema `youtube`: pill com contorno ciano, marca no
fim da linha, manchete de até três linhas, apoio com barra ciano, régua de dados no
rodapé à esquerda e assinatura à direita, com painel de foto ocupando 31% da largura
(template `templates/card-canal.html`). A largura da coluna de texto é derivada da
largura do painel: com a conta antiga, 1280x720 ficava com 589px de coluna para um
rodapé de 648px e o encaixe reprovava. O contador fica desligado por padrão, porque a
referência dele não tem. Rótulos em mono levam `nowrap`, senão quebram em duas linhas
e desmontam a régua.

**Atenção à diferença de paleta:** o gerador de cenas antigo do harness
(`video-terrasia/gen_video.py`) usa paleta própria estilo GitHub dark, com verde
`#3fb950` e ciano `#58a6ff`, que **não** é o tema do produto nem o do canal. Misturar
cena dele com cartela de tema deixa dois tons de ciano lado a lado na mesma peça.

**Importar identidade de fora.** `$TERRAS_BRAND_DIR/tools/importar_identidade.py`
lê um projeto do CapCut (pasta ou `draft_content.json`) ou uma imagem/vídeo e propõe
o bloco de tema, com as pendências anotadas. Ele separa os papéis por saturação e
luminância: acento é cor saturada, texto é cor clara e neutra.

## Voz e pronúncia (na skill de áudio)

Toda a parte de voz mora na skill **`terras-audio`**, que também serve audiolivro e
outros contextos: escolha de voz, pronúncia de termos em inglês, cadeia de áudio e
normalização. Esta skill chama o CLI dela para narrar cada bloco (`--alvo video`) e
para o relatório de pronúncia que o `plan` imprime.

O que continua sendo decisão daqui: a **voz padrão é `pt-BR-ThalitaMultilingualNeural`
com ritmo `-8%`**, escolhida pelo Everton em 2026-09-20 ouvindo as três opções em
pt-BR do `edge-tts` (Antonio, Francisca e Thalita); o roteiro sobrepõe com `voice` e
`rate`, e o `brand.json` guarda o padrão. O modo `voz-en` (palavra inglesa numa voz
EN colada na frase) existiu aqui e foi **reprovado pelo ouvido dele**: "não presta,
misturou". O motivo ficou registrado em `build.py`.

Detalhes de alvo de loudness, dicionário de pronúncia e calibragem estão em
`$SKILL_DIR/../terras-audio/SKILL.md`.

## Custo antes de gerar

O Everton quer o custo medido antes do render (é o mesmo vocabulário FinOps do
terrasia, que grava `cost_calls` e preço por `model_pricing`). O `plan` já imprime
o bloco de custo no fim, e `python3 scripts/build.py custo roteiro.json` mostra ele
sozinho. O que sai:

| Item | Natureza | Como é obtido |
|---|---|---|
| Narração | exato | caracteres por bloco e total, mais o equivalente em tokens pela convenção `chars/4` do terrasia |
| Duração e quadros | exato | caracteres / 12,5 por segundo (medido com a Francisca a -8%), mais 0,6s por bloco; cena externa respeita a duração desenhada |
| Máquina | exato na ordem | 3,5s de máquina por segundo de vídeo (medido: 3,0 a 3,9), em minutos; custo local, zero em dinheiro |
| Voz e arte | em dólar quando precificado | `custo.voz.preco_por_1k_chars_usd` e `custo.arte.preco_por_imagem_usd` no `brand.json`; `edge-tts` é grátis e `null` não contabiliza |
| Tokens do agente | **não determinístico** | referência medida, guardada em `custo.agente_referencia` no `brand.json`; o preço por Mtok vem da `model_pricing` (colunas `input_per_mtok` e `cached_input_per_mtok`) |

Medição de referência de 2026-09-20 (construção da skill e primeiros vídeos, 134
chamadas): 53.933 tokens de entrada nova, 38.338.688 de cache lido e 152.259 de
saída. O cache domina o volume, e é a linha barata, então nunca juntar entrada com
cache numa conta só: são preços diferentes, exatamente como na tabela dele.

## Pacote de publicação: título, descrição e capa

A capa e o pacote não são passo final esquecido: `build.py capa roteiro.json` gera a
capa em 1280x720 a partir de um bloco do roteiro (padrão o primeiro), e
`upload_youtube.py pacote roteiro.json --out-dir out/` monta título, descrição com
capítulos, tags e o comando pronto de subir. O `--exportar` do render copia a capa
junto das cartelas.

**Título, as regras que decidem o clique.** O título diz o que a pessoa **ganha**,
não sobre o que o vídeo é. Cabe em **60 caracteres**, porque o YouTube permite 100
mas o feed corta antes disso. Prefixo de marca (`TerrasIA:`) só quando o canal ainda
não é conhecido: custa dez caracteres e compra reconhecimento. Nada de sensacionalismo
que o vídeo não entrega, porque a regra da casa vale aqui também: não prometer o que
o conteúdo não prova. Zero travessão. E o teste final: quem nunca ouviu falar do
produto entende a promessa só pelo título?

**Descrição, com o peso nas duas primeiras linhas.** É o que aparece antes do
"mostrar mais", então a primeira linha é o gancho e a segunda diz o que o vídeo
entrega. Depois vêm duas ou três frases de substância, os capítulos com marcação de
tempo (a partir de três capítulos o YouTube cria a divisão sozinho, e o primeiro
precisa ser `00:00`) e o endereço do rodapé. Sem número inventado, sem promessa, sem
enxurrada de link.

**Capa.** 1280x720, tirada da cartela de abertura, com o tipo 20% maior que a escala
proporcional porque em tela pequena o que lê é a manchete. Uma promessa só, e o teste
é ver a imagem a uns 320px de largura: se a manchete não lê, não serve.

O script valida sozinho e avisa: título acima de 60 ou de 100 caracteres, travessão no
texto, capítulo que não começa em zero.

## Checagens que o render faz sozinho

- **Encaixe da cartela**, dentro do Chrome: reprova texto cortado, elemento fora do
  canvas, blocos sobrepostos e manchete acima de 4 linhas.
- **Movimento**: conta quadros parados e saltos na janela de movimento. Qualquer
  parada ou salto reprova. O motor é o PIL com caixa fracionária, porque o
  `zoompan` do ffmpeg anda em passos desiguais e produz o "picado". A medida roda na
  mesma densidade em qualquer formato, e começa depois do fade de entrada: os
  primeiros quadros ainda estão quase pretos e a caixa de recorte deles cai na borda
  da grade de reamostragem, o que inventava um salto e reprovava o vertical.
- **Loudness** na escala do YouTube (`ebur128`): LUFS integrado entre -17 e -14 e
  pico verdadeiro até -1,0 dBFS.

## Identidade visual

Template, fontes e cores vivem no diretório padrão da identidade,
`~/Documents/Diversos/terras-brand/` (trocável por `TERRAS_BRAND_DIR`), que é a
fonte única para banner e vídeo: `templates/card.html`, `fonts/` e `brand.json`
com os tokens. Editar lá vale para as duas skills; o roteiro pode sobrepor `base` e
`accent`, e quando não sobrepõe a cor vem do `brand.json`.

Fundo `#05090f`, acento `#ffcc33`, texto `#f8fafc` e `#b8c4d4`, fonte Inter,
contador de bloco no alto, rodapé com o domínio. Layouts disponíveis: `abertura`,
`numeros`, `lista`, `declaracao` e `fecho`. Escala de vídeo maior que a do banner,
margens de 96px e 4 linhas no máximo na manchete. Leia
`references/identidade-e-movimento.md` antes de mexer em tipografia, cor ou
movimento: as medições que fixaram cada escolha estão lá.

**A assinatura do rodapé é do tema, não do roteiro.** `temas.<nome>.canal.foot` e
`foot_label` no `brand.json` dizem o endereço e o rótulo: o tema `youtube` assina
`terrasia.app` com "Site oficial" (decisão dele em 2026-09-20: o rodapé do canal não
leva a newsletter) e o tema `pessoal` assina `eolimabr.substack.com`, que é o endereço
dos posts. O roteiro sobrepõe com `foot` quando o vídeo aponta para outro lugar. Isso
virou chave de tema porque o short do Jev saiu com a newsletter no rodapé do canal
mesmo com o tema certo: o código lia o `assinatura` global do `brand.json`, que existe
para o banner e é o endereço dos posts, não o do canal.

Arte de fundo (quando o vídeo pede capa ou cena): usar o `gen_art.py` da skill
`terras-banner` e apontar no roteiro pelo campo `art`.

## Instalação (sem sudo)

`bash scripts/setup.sh` cria `~/.config/terras-video/` com o ffmpeg estático (via
npm `ffmpeg-static`) e um venv com `edge-tts`. `bash scripts/setup-brand.sh` cria o
diretório padrão da identidade, copiando apenas o que estiver faltando das
sementes em `seed/` das duas skills. Os dois são idempotentes. Nesta máquina o
`apt` não funciona (flag de no-new-privileges), e por isso nada aqui depende dele.

## Publicação

**Rota manual (sem setup).** Subir o mp4 no YouTube Studio com o pacote pronto:
título, descrição e tags saem de `python3 scripts/upload_youtube.py pacote roteiro.json`,
e a cartela 1 serve de miniatura (no Short, a miniatura do feed é um quadro do vídeo; a
oficial vale no canal e na busca). No vertical o pacote já vem com `#Shorts` na
descrição e as notas do formato.

**Rota API (o script existe, falta a credencial dele).**
`scripts/upload_youtube.py` sobe pela YouTube Data API v3 com envio resumível,
aplica miniatura e playlist, e sobe **privado por padrão**; publicar como público
exige `--publico --sim-publicar`, porque notifica inscritos e não tem volta
prática. Fluxo:

```bash
bash scripts/setup-youtube.sh          # bibliotecas no venv + confere a credencial
python3 scripts/upload_youtube.py autorizar        # abre o navegador uma vez
python3 scripts/upload_youtube.py enviar --video out/video.mp4 \
    --titulo "..." --descricao "..." --tags ia,engenharia --thumb out/cartela-1.png
```

A credencial é a única parte que só o dono da conta faz: projeto no Google Cloud,
YouTube Data API v3 ativada, tela de consentimento e um client OAuth do tipo "App
para computador" salvo em `$TERRAS_VIDEO_HOME/client_secret.json`. Duas armadilhas
documentadas pelo Google que valem saber: app em status "Testing" recebe refresh
token que **expira em 7 dias** (publicar o app em Produção resolve), e a cota
padrão dá **100 uploads por dia** com `videos.insert`, separada dos 10.000 pontos
por dia que os outros endpoints dividem. O script se reexecuta no python do venv
sozinho, então pode chamar com o `python3` do sistema.

Pelo terrasia, o caminho é o mesmo das outras: embrulhar este CLI numa tool MCP
(`video_publish`) no daemon, como já é feito com o `terras_substack.py`.

## Uso pelo terrasIA (MCP)

O repositório terrasia (`~/assistente-os`) embrulha CLIs em tools MCP. O caminho
para esta skill é o mesmo da `terras-substack`: as tools `video_plan`,
`video_approve`, `video_render` e `video_status` apenas spawnam este `build.py`,
e a lógica continua aqui, num lugar só. Variáveis: `TERRAS_VIDEO_CLI` (default
`$SKILL_DIR/scripts/build.py`) e `TERRAS_VIDEO_HOME` (default
`~/.config/terras-video`).

## Armadilhas (cada uma já custou um render)

- **Não voltar para `zoompan`**: ele anda em passos desiguais. Medição em
  `references/identidade-e-movimento.md`.
- **`crop` do ffmpeg não faz zoom**: largura e altura são avaliadas uma única vez.
- **60fps é obrigatório** no motor de movimento; a 30fps o zoom lento volta a
  parecer picado.
- **Não pedir texto ao modelo de imagem**: letra sai torta. Texto é HTML na cartela.
- **Termo técnico em inglês no meio do português** merece escuta antes de publicar:
  não há checagem automática de pronúncia.
- **Vídeo não é banner**: não reaproveitar a composição 1200x628 em tela cheia.
- **No vertical, o zoom empurra o texto para fora da área segura.** A faixa desenhada
  é a faixa livre encolhida pelo zoom, não a faixa livre. Quem pega isso é o gate
  visual nos quadros do vídeo; a checagem de encaixe olha a cartela parada, que está
  certa. Medido no primeiro teste: cabeçalho em y=230 virava 187 com o zoom completo.
- **Cena externa nunca entra crua no pipe.** Quadro de tamanho diferente do canvas
  desalinha o fluxo e sai vídeo embaralhado, sem erro nenhum: o encaixe é obrigatório
  e o `build.py` avisa quando ele acontece.

## Exemplos de prompt do usuário

- "faz um vídeo de 60 segundos sobre o digest dessa semana"
- "transforma esse post em vídeo pra Shorts"
- "faz um short de 40 segundos com os números da semana"
- "quero um vídeo do terrasIA funcionando, 3 minutos"
- "refaz com a voz da Francisca"
- "gera o vídeo, a capa e o pacote de publicação"

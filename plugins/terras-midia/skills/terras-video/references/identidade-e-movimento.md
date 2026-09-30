# Identidade visual e movimento

O que o vídeo herda do banner, o que muda, e as medições que fixaram as escolhas.
Toda configuração aqui foi medida nesta máquina, em 2026-09-20.

## O que muda em relação ao banner

Banner é visto parado, no feed, a 1200x628. Vídeo é visto em tela cheia, com
movimento e com áudio. Três consequências:

| Item | Banner | Vídeo |
|---|---|---|
| Tipo | manchete 88px em 1200x628 | manchete 104px em 1920x1080, com no máximo 4 linhas |
| Margem | 78px | 96px, e 72px embaixo para o rodapé |
| Elemento novo | régua de dados | contador de bloco (`02 / 05`) no alto à direita, que dá noção de tamanho do vídeo |
| Cor de apoio | `#b8c4d4` | igual, mas texto de lista em `#e2e8f0` porque tela cheia lava o contraste |
| Fundo | arte + scrim | chapa `#05090f` com dois glows; arte entra quando o vídeo pede capa, não em toda cartela |

Cor, tipografia e o acento `#ffcc33` são os mesmos: o vídeo é a mesma marca, só maior.
O vertical (Shorts) tem seção própria abaixo, porque muda a escala do tipo, a faixa em
que o conteúdo pode ficar e o layout dos números.

## Cartelas (layouts do template)

| Layout | Para que serve | Campos |
|---|---|---|
| `abertura` | primeira cartela, gancho | kick, headline, sub |
| `numeros` | prova com dados | headline + stats (número grande, label pequena) |
| `lista` | três ou quatro itens | headline + list |
| `declaracao` | uma ideia só, com barra de acento à esquerda | headline |
| `fecho` | última cartela, próximo passo | kick, headline, sub |

O `--check` de encaixe roda dentro do Chrome: ele reprova cartela com texto
cortado, elemento fora do canvas, sobreposição entre blocos ou manchete acima de
4 linhas. O veredito sai no `<title>` do HTML, que o `build.py` lê.

Em pé, os mesmos cinco layouts saem do `card-vertical.html`, com duas diferenças: a
manchete pode ir a 5 linhas (a coluna é estreita e sobra altura) e os números ficam
empilhados. A checagem soma uma regra à deitada: **nada de texto fora da faixa em que
o player não cobre**, que é o que impede uma cartela bonita de nascer escondida atrás
da interface.

## Movimento: por que não usar zoompan

A primeira versão do piloto usava `zoompan` do ffmpeg com fonte de 1920px. O
resultado foi "picado". Medição das diferenças entre quadros consecutivos, em 3
segundos de vídeo a 60fps:

| Configuração | Quadros parados | Saltos (>2x a mediana) | Jerk (máx/mediana) |
|---|---|---|---|
| `zoompan`, fonte 1920, zoom contínuo 10s | 12 | 24 | 5,37 |
| `crop` do ffmpeg em vez de zoompan | 0 (o zoom não acontece) | 0 | 0,00 |
| Quadros gerados no **PIL** (motor atual) | 20 no fim do easing | 0 | **0,30** |

O que decidiu foi a coluna do jerk, não a das paradas. As 20 "paradas" do motor
atual são o próprio easing chegando ao fim: o movimento desacelera de propósito e
quase para, e isso é suave, não picado. O que caracteriza o picado é a
irregularidade, e por isso a checagem do `build.py` usa jerk com limite **1,0**:
um quadro que muda quase nada seguido de outro que salta mais que a mediana do
movimento inteiro reprova o render. Os dois casos conhecidos ficam bem separados
(5,37 reprovado, 0,52 aprovado).

O motor atual gera cada quadro no PIL: amplia a cartela 2x e recorta com caixa
fracionária (`resize(box=...)` aceita float), aplicando easing ease-out em 4
segundos e depois descansando. Os quadros vão por pipe (`rawvideo`) para o
ffmpeg, sem arquivo intermediário.

Duas escolhas dentro do motor, ambas medidas:

- **Reamostragem `BOX`**, não `LANCZOS`: a fonte entra 2x ampliada e o recorte sai
  em cerca de 1,9:1, que é exatamente o caso em que o filtro de área é correto.
  Diferença média de 0,46/255 contra LANCZOS (imperceptível), mesma fluidez, e
  3,3x mais rápido: 34ms contra 113ms por quadro. Foi de 3,5 minutos para 1 minuto
  de geração num vídeo de 30 segundos.
- **Fade aplicado depois da medição**: o blur de escurecimento entra no quadro
  enviado, mas a estatística de movimento é medida no quadro anterior a ele. Sem
  isso, o fade de entrada contamina a série de deltas e vira "salto" falso.

Duas correções de 2026-09-20, quando o vertical entrou, ambas no mesmo lugar:

- **A medida roda sempre na mesma densidade** (`FATOR_AMOSTRA = 0,25`, um quarto de
  cada eixo), e não com largura fixa de 480. Com largura fixa, o vertical era
  amostrado a 2,25x e o horizontal a 4x, e o mesmo movimento media diferente nos dois.
- **Os dois primeiros quadros ficam fora** (`QUADROS_AQUECIMENTO`). Eles ainda estão
  sob o fade de entrada, e a caixa de recorte deles cai na borda da grade de
  reamostragem do PIL: a diferença 0→1 e 1→2 mede a troca de grade, não o movimento.
  No vertical isso reprovava o render com jerk 1,81; fora do aquecimento vai para 0,58,
  e o horizontal não muda (0,52), que é o ponto: o mesmo movimento medindo o mesmo nos
  dois formatos.

Regra: **não voltar para `zoompan`**. Se um dia o movimento precisar de pan
também, a caixa fracionária do PIL aceita coordenadas fora do centro.

## Shorts (vertical, 1080x1920)

**A área segura é medida, não arbitrada.** Em 2026-09-20 abri um Short no player web
numa janela de exatamente 1080x1920 e varri o quadro com 20x40 pontos de
`document.elementFromPoint`, marcando o que não era o `<video>`: a pilha de botões
(likes, comentários, compartilhar) ocupa a direita a partir de **81% da altura**, e a
faixa de fala do criador fica no topo, entre 3% e 7%. A leitura foi no player web, não
no aplicativo: o app tem o mesmo desenho (canal e título embaixo à esquerda, botões à
direita), mas proporções um pouco diferentes, e por isso o número escolhido tem folga.

Decisão: a faixa livre vai de **y 230 a 1382** (12% e 28% de 1920). Os 28% de baixo
deixam 9 pontos percentuais de folga até os botões medidos, o que cobre a diferença
entre web e aplicativo.

**A cartela é desenhada mais para dentro que isso**, e por um motivo que não é óbvio:
o motor de movimento aplica zoom de 6% sobre o centro do quadro, então o texto sai da
faixa na medida em que o vídeo anda. Medido no primeiro render: o cabeçalho desenhado
em y=230 aparecia em y=187 no quadro ampliado, dentro da área da interface, e a
assinatura em y=1370 ia para 1394. A conta é:

```
faixa_desenhada = centro ± (faixa_livre - centro) / ZOOM_END
```

Com folga de 1,25% da altura (24px) em cada lado, dá **294 a 1336**: no instante de
maior ampliação o conteúdo fica exatamente de 254 a 1358, com 24px de sobra até a
linha de 230 e até a de 1382. Sem a folga, o gate visual mediu 1px de sobra no topo, o
que é margem nenhuma para um ajuste futuro de zoom.

**Nada disso é pego pela checagem de encaixe da cartela parada**, que está certa por
construção: quem pega é o gate visual rodando nos quadros extraídos do vídeo. Foi
exatamente assim que o caso apareceu.

**O tipo sai do menor eixo**, não da largura de referência. A regra antiga
(`min(w/1920, h/1080)`) dava 0,5625 em 1080x1920 e a manchete saía com 59px, que no
celular não se lê; a nova dá `min(w,h)/1080`, e a manchete fica sempre com 9,6% do
menor eixo (104px). Em conta de ângulo: um celular de 7cm a 30cm de distância mostra
uma largura de 13,3°, contra 22,6° de um player de 20cm a 50cm no notebook, então o
mesmo tamanho aparente pede ~100px num 1080 de largura. Para 16:9 as duas contas dão o
mesmo número, e é por isso que o horizontal não mudou.

**Layout.** Margem lateral de 84px (contra 96 do horizontal), que devolve 912px de
coluna; manchete de até 5 linhas; e **números empilhados**, um por linha, com o valor à
esquerda e o rótulo ao lado. Três números lado a lado em 1080 viram três colunas
apertadas e o valor grande perde o efeito. No card de canal em pé a foto deixa de ser
painel lateral (31% da largura não cabe ao lado de uma coluna de 650px) e passa a ser
fundo do quadro com véu.

**Cena externa 16:9** entra encaixada: inteira e centrada sobre um fundo desfocado dela
mesma, que é o que o feed faz com material horizontal. `"ajuste": "preencher"` corta as
laterais em vez de encaixar. O encaixe não é estético, é obrigatório: o pipe do ffmpeg
declara o tamanho do canvas, e quadro de outro tamanho desalinha o fluxo e sai vídeo
embaralhado, sem erro nenhum.

**Teto de 3 minutos** (`SHORTS_MAX_S`): acima disso o YouTube não classifica como
Short, e as cartelas em pé apareceriam num player horizontal. O `render` recusa antes de
gerar pela estimativa e avisa depois se o arquivo final passou.

## Áudio

Cadeia aplicada sobre a voz do `edge-tts`:

```
highpass=f=75,
acompressor=threshold=-18dB:ratio=3:attack=6:release=120,
loudnorm=I=-16:TP=-1.5:LRA=11,
aresample=48000,
apad=pad_dur=0.6
```

O `apad` não é enfeite: sem ele o `-shortest` do ffmpeg encerra o trecho no fim do
áudio enquanto ainda há quadro para escrever, e o processo morre com
`BrokenPipeError` no meio do bloco. A escrita no pipe continua protegida contra
`BrokenPipeError` porque o ffmpeg pode fechar a entrada um pouco antes do último
quadro, e isso é normal, não é falha.

Alvos verificados pelo `build.py` na escala que o YouTube usa (`ebur128`): LUFS
integrado entre -17 e -14 e pico verdadeiro até -1,0 dBFS. O `volumedetect`
(mean/max em dBFS) não serve para isso, porque não é escala de loudness.

A voz da primeira versão saiu com média de -19,4 dB e pico de -4,5 dB, ou seja,
baixa e sem tratamento. Com a cadeia, o mesmo texto ficou em -16,1 LUFS
integrado, dentro do alvo, com pico de -4,5 dBFS.

Vozes em pt-BR disponíveis no `edge-tts`. A padrão é a
`pt-BR-ThalitaMultilingualNeural`, com ritmo `-8%`, escolhida pelo Everton em
2026-09-20 ao ouvir o comparador de cinco amostras: ele primeiro pediu o timbre da
Francisca com a entonação da Thalita, e depois de ouvir as duas lado a lado ficou
com a Thalita, que era a amostra de referência.

| Voz | Perfil |
|---|---|
| `pt-BR-ThalitaMultilingualNeural` | mulher, treinada para múltiplos idiomas; **padrão da skill** |
| `pt-BR-FranciscaNeural` | mulher, timbre mais firme |
| `pt-BR-AntonioNeural` | homem, leitura padrão de locução |

Para afinar timbre e entonação, as alavancas são `rate` (velocidade) e `pitch`
(tom). O `edge-tts` **exige sinal explícito** nos dois: `--rate +0%` funciona,
`--rate 0%` devolve `ValueError: Invalid rate '0%'`. O comparador com cinco
variações está em `$TERRAS_BRAND_DIR/exports/cartelas/teste-voz-francisca.mp3`.

Trocar de voz é uma linha no roteiro (`voice`) ou no `brand.json`
(`audio_video.voz`); o roteiro tem prioridade, e o resto é configuração do
`build.py`, não do roteiro de cada vídeo.

## Cenas externas (gerador do terrasia)

Um bloco de roteiro pode trazer `cena: {modulo, funcao, duracao}` em vez de layout
de cartela. Aí o `build.py` importa o módulo por caminho e desenha cada quadro com a
animação dele, e o pipeline entra com o que falta: narração, fades, montagem em
60fps, checagens e exportação. A convenção do módulo é a do harness do terrasia:
`base_image()` devolve `(img, draw)`, a função de cena recebe `(img, draw, t)` e
devolve overlays RGBA, e `SCENES` lista `(funcao, duracao)`.

Duas regras que custaram rodada:

- **O áudio é preenchido até a duração do bloco** (`apad=whole_dur` no comando do
  trecho). Uma cena de 14s com narração de 8,7s virava 8,7s de vídeo porque o
  `-shortest` encerrava no fim do áudio, e o vídeo terminava com a animação pela
  metade: a linha de retorno da cena de fluxo nunca completava.
- **Nunca somar o respiro duas vezes.** O `apad` já alongava o áudio em 0,6s e eu
  somava outros 0,6s só do lado do vídeo, o que reintroduzia o corte em todo bloco,
  inclusive nas cartelas. Agora a narração sai sem preenchimento e a montagem
  preenche até a duração exata.
- **O loudness é medido na fala**, não no arquivo final: cena longa com fala curta
  tem muito silêncio na cauda, e o integrado do vídeo cairia fora do alvo sem que
  nada estivesse errado com o áudio.
- **Cena externa não passa pela checagem de jerk**: a animação é do módulo, com
  entradas e saltos propositais. O gate visual, nesse caso, roda nos quadros
  extraídos do vídeo, não em cartela PNG.

## Temas (pessoal e terrasia)

O template recebe tema por roteiro (`"tema": "terrasia"`), e o tema troca **cores e
fonte**, não só o acento. A fonte entra por `@font-face` gerado no `build.py`
apontando para `$TERRAS_BRAND_DIR/fonts/`, e o resto do CSS vem por placeholder
(`COR_TEXTO`, `COR_TEXTO_APOIO`, `COR_LINHA`, `COR_RODAPE`), então acrescentar um
tema novo é editar o `brand.json`, não o HTML.

O tema também carrega a **assinatura do rodapé** (`canal.foot` e `canal.foot_label`): o
tema `youtube` assina `terrasia.app` com "Site oficial" e o `pessoal` assina a
newsletter. Isso subiu para o tema em 2026-09-20, depois de o short do Jev sair com a
newsletter no rodapé do canal: as cartelas liam o `assinatura` global do `brand.json`,
que é o endereço dos posts e existe para o banner. Endereço é identidade, não escolha
de cada roteiro, então o roteiro só entra com `foot` quando aponta para outro lugar.

O tema do produto foi extraído de `packages/ui/src/colors.ts` e do `:root` de
`terrasia-client/src/index.css` no harness: base `6 6 8`, painel `10 10 14`, card
`14 14 20`, texto `232 232 240`, apoio `138 138 173`, linha `26 26 46`, verde
`0 255 157`, ciano `0 240 255`, amarelo `240 224 0`, roxo `160 32 240`. A variante
clara do produto está guardada em `temas.terrasia.tema_claro`. A fonte JetBrains
Mono veio dos `.woff2` de `terrasia-site/dist/assets` (variável, latin e latin-ext).

**Armadilha medida:** com a fonte mono, a checagem de encaixe reprovava manchete por
`scrollHeight 229` contra `clientHeight 225`, quatro pixels de arredondamento de
`line-height` fracionário, que não é corte visível. O verificador agora tem
tolerância de 6px em texto, e continua sem tolerância para elemento fora do canvas
ou sobreposto.

## Limites conhecidos

- O `edge-tts` fala com o serviço de leitura do Edge, que não é API oficial:
  funciona e é grátis, mas pode mudar ou limitar sem aviso. Se parar, a
  alternativa é voz paga (ElevenLabs, OpenAI TTS) ou gravação humana.
- A voz é sintética e não é a do autor. Clonagem de voz exige serviço pago.
- Não existe checagem automática de pronúncia. Termo técnico esquisito em inglês
  no meio do texto em português merece escuta antes de publicar.
- O gate visual roda nas cartelas PNG antes de virar vídeo. Estatística de
  movimento e loudness são checadas pelo próprio `build.py` no fim do render. No
  vertical ele tem que rodar **também nos quadros extraídos do vídeo**: é lá que
  aparece o texto empurrado para fora da faixa segura pelo zoom, e a cartela parada não
  mostra isso.

# Extracao: medir cor em material de verdade

Tudo aqui parte de uma regra: **cor de marca se mede, nao se estima**. Palpite de
cor e o defeito mais caro desta tarefa, porque ele nao aparece na hora — aparece
quando o material ja foi para o cliente numa cor que nao e a dele.

## Quantas pecas ler

Uma peca mente. O fundo de uma foto nao e o fundo da marca, o JPEG tinge a cor, o
story tem sobreposicao e vinheta. Por isso o `extrair.py` recebe **varias pecas** e
so elege uma cor como da marca se ela aparecer em pelo menos duas (ou cobrir um
quarto de uma peca). Cor que aparece em uma peca so entra na lista de cores de
marca com nota ("aparece em poucas pecas"), porque pode ser cor de campanha.

O ideal e um conjunto com: identidade aplicada (peca institucional), formato
diferente (feed e story), e momento diferente (campanha e aviso). Tres ja bastam —
**nao feche a paleta com pecas de um formato so.**

**O caso de um cliente multicolor, que custou uma correcao:** as 10 pecas eram todas anuncio de feed
e story, todas de fundo colorido chapado, e a extracao concluiu que a marca nao tinha
fundo escuro — o papel de `base` ficou com a cor mais presente, marcado como provisorio.
Quando o banner institucional chegou, o fundo era navy `#061534`. As quatro cores
bateram exato, mas os papeis estavam errados: o que era "fundo" era acento. **Material
institucional (banner, manual, site, papelaria) entra na extracao antes de declarar
qualquer papel de fundo**, e o que a marca publica como institucional manda mais que o
anuncio. Cinco pecas do mesmo formato valem menos que uma de outro.

## O que separa cor de marca de mistura

Duas peneiras, nessa ordem:

1. **Mistura.** Saturacao entre 60 e 120 e quase sempre cor da marca misturada com
   o fundo, com a foto ou com a sombra. O magenta de um cliente multicolor mede saturacao 222; o
   magenta dele sobre o azul mede 92. So o primeiro e cor da marca. Foi um tom
   misto desses (#347596, ciano com navy) que virou "o acento" num guia de marca
   escrito a partir de um rascunho automatico — a partir dai o limite foi para 120.
2. **Textura.** Cor de preenchimento tem vizinhanca uniforme. O script erode a
   mascara do tom e olha quanto sobra ("chapado"): fundo, barra e botao ficam
   perto de 1; meio-tom de foto, sombra e borda de letra ficam baixos. Tom com
   chapado abaixo de 0.6 nao vira papel, vira pendencia.

## Papel nao e o mesmo que presenca

O modelo "fundo escuro + um acento" nao serve para toda marca. Uma marca pode ter
quatro cores saturadas e fundo colorido; outra, navy + ouro; o terras tem
fundo preto e ciano. O script tenta o modelo escuro e, quando nao ha fundo escuro
limpo, elege a cor mais presente como base e **avisa que o papel e provisorio**.
Isso e de proposito: quem decide qual cor manda e o dono da marca, nao a contagem
de pixels.

Quando duas cores vivas tem a mesma matiz e uma e mais escura, elas sao a mesma
cor em fundos diferentes — a mais presente e a cor, a outra entra em
`variantes_de_cor` com a nota. Sem essa regra, o magenta de um cliente multicolor sobre o azul
entrou como quinta cor da identidade.

## Cor de texto nas duas pontas

Texto fino (traco de 2-3 px) desaparece na quantizacao, entao a cor do texto sai da
media dos pixels extremos, nao de um pixel escolhido a dedo. Sempre nas duas
pontas: claro (texto sobre fundo) e escuro (tinta sobre papel). Marca que vive em
fundo colorido precisa das duas — um cliente multicolor escreve branco sobre a cor e quase
preto sobre o amarelo.

## Contraste, sempre

Nenhum acento vivo sobrevive ao papel branco: o ciano #07d4ec mede 2:1, um amarelo
saturado 1.5:1, um ouro 2.4:1. O acento continua sendo o acento para
preenchimento, barra e icone; **para texto sobre claro entra a versao escurecida**,
que o `tokens.py` deriva mantendo a matiz e chama de `-sobre-papel`. Sem isso, a
identidade aplicada em site, documento ou peca impressa nasce ilegivel.

O mesmo vale ao contrario: cor de texto da marca sobre a base pode nao ler (o apoio
#646d99 de um cliente multicolor mede 1.3:1 sobre o azul). O guia mostra as duas razoes lado a
lado justamente para isso aparecer antes do material.

## O que nao sai de pixel

Diga isso em voz alta quando acontecer, em vez de inventar:

- **Nome de fonte.** Raster nao guarda nome de fonte. Com documento-fonte (PDF com
  fonte embutida, PPTX/DOCX com tema, CSS) o nome sai de graca — o `--fonte` faz
  isso. Sem documento, a familia e identificada a olho (`tipografia.md`).
- **Tamanho de tipo.** Nao se copia de peca de rede social, que e feita para ser
  lida de longe; a escala se define por target.
- **Filete, raio de canto, espacamento.** O JPEG come a borda de 1-2 px; medir
  isso pede a peca original em resolucao cheia e leitura no zoom (`medir.py area`).
- **Movimento.** Keyframe e curva nao estao na imagem. Se o material for animacao,
  a referencia e o projeto (ver o caminho CapCut em `~/Documents/Diversos/terras-brand/`).

## Armadilhas que ja custaram

- **Rascunho lido como fonte.** Arquivo gerado por leitor automatico precisa de
  cabecalho dizendo que e rascunho, senao ele vira a fonte da proxima extracao e o
  erro se propaga. O `extrair.py` grava `status: rascunho` e um aviso no topo do
  JSON; **nao apague esse campo antes da conferencia humana**.
- **Media em vez do tom.** O representante do cluster e o tom mais frequente, nao a
  media: media de azul com a borda suavizada puxa a cor para longe do azul chapado.
- **Quantizacao quebrando a mesma cor.** O amarelo de um cliente multicolor apareceu como
  #f1d323, #ead027 e #e4d533. Sem juntar clusters proximos, a paleta vira lista de
  variacoes e a cor de verdade perde peso.
- **Peca com interface por cima.** Print de story costuma ter barra de status e
  botoes do app; recortar antes de medir, ou aceitar que aquele tom vai aparecer
  nas pendências.

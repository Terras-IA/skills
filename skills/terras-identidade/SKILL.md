---
name: terras-identidade
description: "Le a identidade visual de uma marca a partir de imagens (pecas de anuncio, prints, manual, papelaria, site) e entrega ela pronta para reusar: cores com papel medido, tipografia, marca recortada em PNG, linguagem visual e tokens de CSS/JSON/Tailwind para site, sistema, documento e peca de marketing. Use quando o pedido envolver identidade visual, marca, manual de marca, paleta, 'quais sao as cores', 'pega essas imagens e faz a identidade', tipografia de uma peca, 'deixa no visual da marca', 'aplica a identidade no site/documento', logo/ativo de marca, ou quando chegarem fotos de material de cliente por WhatsApp e for preciso extrair o visual dele. Cobre extracao, medicao de cor, recorte de logo e equivalencia de fonte livre."
keywords: [identidade, identidade visual, marca, branding, brand, paleta, cores, tipografia, fonte, logo, ativo, manual de marca, design system, tokens, css, tailwind, extracao, whatsapp, peca, anuncio, cliente]
---

# Identidade visual a partir de imagens

Pega o material que existe (fotos de peca, print de perfil, manual em PDF, papelaria)
e devolve a identidade em forma reusavel: cores com papel declarado, tipografia,
marca recortada, linguagem visual e tokens — para site, sistema, documento, peca de
marketing e publicidade saírem iguais sem ninguém redecidir cor.

O que ela **nao** faz: criar post, publicar, montar video ou escrever texto. Ela
entrega a identidade; a `terras-banner`, a `terras-linkedin`, a `terras-ebook` e a
`terras-video` aplicam.

## Onde está instalada

Fonte única: `skills/terras-identidade/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## A identidade e um arquivo

Tudo vive em `<projeto>/identidade/identidade.json`:

```
identidade/
├── identidade.json      os papeis, a tipografia, a marca, a linguagem, as pendencias
├── fontes/              arquivos das fontes (woff2 e ttf)
├── ativos/              PNGs recortados do material (logo, monograma, fundo, padrao)
├── tokens.css           gerado: site e peca
├── tokens.json          gerado: sistema e app
├── tailwind.config.js   gerado
├── marca.md             gerado: o guia legivel, com pendencias
└── prova.png            gerado: a prova visual que se olha antes de aplicar
```

**A identidade e do diretorio, nao da chamada.** Quem monta material le o
`identidade.json` do projeto, sempre por caminho absoluto — passada relativa, de
outro diretorio ela nao existe e o material sai com a identidade padrao sem avisar.
Ja aconteceu: um livro foi montado de outro diretorio e saiu na identidade errada.

Duas convencoes convivem, e elas nao se misturam:

- `<projeto>/identidade/identidade.json` — identidade de cliente ou de projeto
  (IECSJC, Sousa Lima, Avancei). E o que esta skill cria.
- `~/Documents/Diversos/terras-brand/brand.json` com `temas` — a identidade terras
  (pessoal, terrasia, youtube), consumida por `terras-banner` e `terras-video`.
  Para mexer nela, editar la; esta skill so aponta o caminho.

## Pipeline

1. **Juntar as pecas.** 3 ja bastam: uma institucional, uma de campanha e uma de
   formato diferente. Story, feed, print de perfil, foto de papelaria, pagina de
   manual. Quanto mais variado, melhor a leitura.
2. **Extrair.** `python3 scripts/extrair.py <pecas ou pasta> --nome "Marca" --destino <projeto>/identidade`
   Sai o `identidade.json` marcado como **rascunho**, o relatorio de cores no
   terminal e as pendencias. Se houver manual, site ou deck, passar junto
   (`--fonte manual.pdf --fonte site.css`) para ler o nome real da fonte.
3. **Conferir a mao.** Cor de rascunho nao vai para material. Olhar a peca original,
   medir o elemento com `medir.py ponto` / `medir.py area`, e conferir as duas
   coisas que mais erram: a cor de acento e o tom de apoio.
4. **Recortar a marca** (ver abaixo) e preencher `ativos` e `marca.estilo`.
5. **Tipografia.** Identificar a familia e instalar o equivalente livre:
   `python3 scripts/fontes.py "Montserrat" --pesos 400,700,800 --destino identidade/fontes`
   (baixa ttf e woff2, so os subsets que cobrem portugues). Sem documento-fonte o nome
   da fonte **nao** sai de pixel — registrar como hipotese, nunca como medicao
   (`references/tipografia.md`).
6. **Linguagem visual.** Preencher o bloco `linguagem` a partir das pecas
   (`references/linguagem.md`): forma, tratamento de foto, grade, gesto do botao,
   restricoes. E o que faz a peca nova parecer da marca.
7. **Gerar e provar.** `python3 scripts/tokens.py <identidade.json> --escala-base 16`
   e `python3 scripts/prova.py <identidade.json>`. Passar a prova pelo gate visual,
   corrigir, e so entao aplicar em material.

## Recortar a marca

Logo de marca quase nunca vem em arquivo: vem dentro da peca comprimida. O recorte
tem duas versoes porque todo material pede as duas — branca para fundo escuro,
escura para fundo claro:

```bash
# achar a caixa: zoom com grade e regua em pixel
python3 scripts/medir.py zoom peca.jpg 90 1140 420 130 --escala 3

# extrair as duas versoes de uma mascara so
python3 scripts/medir.py marca peca.jpg --caixa 112,1185,330,84 \
    --cor "#f1d323" --cortar-faixa 58,84 --pasta identidade/ativos --nome marca
```

`--cor` e a cor do fundo da peca, e a mascara pega tudo que nao e fundo (letra,
simbolo e marca colorida entram juntos). `--cortar-faixa` corta a tagline fina, que
a compressao da peca quebra: nesse caso a tagline se escreve em texto no template,
nao se usa a imagem.

**Tagline e texto fino quebram em recorte de JPEG.** Se a assinatura saiu picada, o
comando avisa pela contagem de componentes. Para impressao grande, o recorte de peca
comprimida nao serve — pedir o vetor de origem.

## Cores: o que se mede e o que nao se inventa

- Cor de marca se **mede**, nunca se estima. Tom misto (saturacao 60-120) e cor da
  marca misturada com fundo ou foto, e nao vira papel — vai para as pendencias.
- Cor de preenchimento tem vizinhanca uniforme; o script mede isso ("chapado") e
  descarta textura, sombra e meio-tom.
- Acento vivo **nunca** le sobre papel branco (o ciano `#07d4ec` mede 2:1). O
  `tokens.py` deriva a versao `-sobre-papel`; sem ela, site e documento nascem
  ilegiveis.
- Nao ha "fundo escuro + acento" em toda marca: identidade multicolor (Avancei) tem
  quatro cores de marca e fundo colorido. Quando nao ha base escura limpa, o script
  elege a cor mais presente e **avisa que o papel e provisorio** — quem decide qual
  cor manda e o dono da marca, nao a contagem de pixels.
- **Rascunho nao e fonte.** O `identidade.json` nasce com `status: rascunho` e um
  aviso no topo. Ja aconteceu de um rascunho automatico ser lido como fonte e um
  ciano misturado (`#347596`) entrar num guia de marca. Nao apague o aviso antes da
  conferencia humana; quando ela acontecer, `status: revisado`.

## Aplicar: cada alvo tem sua porta

| Alvo | Como | Arquivo |
|---|---|---|
| Site | variaveis CSS (escuro no `:root`, claro em `[data-tema="claro"]`) | `tokens.css` |
| Sistema / app | papeis resolvidos, com contraste calculado | `tokens.json` |
| Tailwind | tema estendido | `tailwind.config.js` |
| Documento | HEX e RGB da tabela do guia, fontes em arquivo | `marca.md` |
| Peca e anuncio | HTML com os tokens + Chrome headless no tamanho exato | `tokens.css` |
| Livro / e-book | `--identidade` do `terras-ebook`, com caminho absoluto | `identidade.json` |

Detalhe de cada um, incluindo as regras de interface (estado, hover, foco, nunca
acento puro em area grande), em `references/aplicacao.md`.

## Prova visual e gate

`prova.py` renderiza a mesma marca em fundo escuro, fundo claro e documento, com a
paleta, a escala e as pendencias declaradas. E a prova que mostra o token errado
antes do material: o acento que funciona no escuro some no branco, o texto de apoio
que mede 1.3:1 sobre a base desaparece.

Antes de entregar qualquer material, passar a prova (ou o material) pelo gate visual
(`documents:visual-judge`). Prova sem arquivo de fonte avisa na tela que a
tipografia e substituta — prova com letra errada e pior que prova nenhuma, porque
quem aprova aprova o que viu.

## Manual de identidade (8 paginas)

Quando o pedido e o manual, e nao a aplicacao: 16:9 em 2560x1440, uma secao por
pagina, na ordem capa e indice / paleta / tipografia / respiro e reducao / variacoes
/ fundos e contrastes / papelaria / sinalizacao e digital. Estrutura e criterios em
`references/manual.md`. O manual e a apresentacao do `identidade.json`: nada entra
nele que nao esteja no JSON.

## Ferramentas do sistema

- `python3` com Pillow e pymupdf (as duas ja instaladas). Sem numpy de proposito: as
  contagens usam `getcolors` e `ImageChops`, que sao C e resolvem em segundos — varrer
  pixel a pixel em Python levava 10 minutos por conjunto.
- Chrome (`google-chrome-stable`) para renderizar prova, peca e manual. O render e
  sempre pelo `scripts/render.py` (tamanho exato, corte da faixa vazia, varias larguras
  de uma vez, e `--pdf` para a pagina inteira numa folha) — montar o comando do Chrome
  na mao erra o tamanho por alguns pixels.
- `fontes.py` baixa do Google Fonts em ttf e woff2. O CSS do Google traz um subset por
  faixa de unicode, entao o download a mao escreve latin-ext por cima de latin e a
  fonte instala sem escrever "ção" — deixe o script fazer.
- `ffmpeg` **nao** esta nesta maquina; para ler quadro de video, usar o ffmpeg da
  `terras-video` (`~/.config/terras-video/ffmpeg`).

## Armadilhas (cada uma ja custou um material errado)

- **Nao feche a paleta com pecas de um formato so.** Cinco anuncios de feed valem menos que
  um banner institucional: o Avancei teve o papel de `base` corrigido (de cor chapada para
  navy) quando o banner chegou depois das 10 pecas. Se existir manual, banner, site ou
  papelaria, entra na extracao antes de declarar papel de fundo.
- Nunca escrever hex na mao em material novo: se falta valor, falta no
  `identidade.json` — corrigir a fonte e gerar de novo.
- Peca de rede social nao define tamanho de tipo para documento (ela e feita para ser
  lida de longe). O que viaja entre formatos e a relacao, nao o pixel.
- Fonte do sistema (DejaVu, Liberation) e o que faz a peca parecer amadora. Sempre
  instalar o equivalente livre em `fontes/`.
- CMYK e conversao, nao medicao: se a marca vai para impressao em cor exata, o CMYK
  se combina com a grafica, e o manual marca o valor como referencia.
- "Sem logo" no vocabulario do Everton e `sem-marca`: nada de marca, **nem a
  assinatura de rodape**. Tipografia, cores e estrutura continuam. Nao reabra isso.
- CapCut nao tem API: ler projeto dele so pelo `draft_content.json` local
  (`~/Documents/Diversos/terras-brand/tools/importar_identidade.py` cuida desse caso).

## Exemplos de prompt do usuario

- "pega essas imagens e faz a identidade visual"
- "quais sao as cores e a tipografia da marca?"
- "monta o manual de identidade dessa marca"
- "deixa esse documento no visual do cliente"
- "aplica a identidade no site" / "nesse material usa as cores da marca"
- "cria os tokens pra eu usar no sistema"
- "essa peca ficou com o visual padrao, poe na identidade"
- "com esse material, da para propor um layout?" (propor pagina ou peca usando os tokens)
- "tira o logo dessa peca" / "preciso do logo em branco e em preto"
- "o cliente mandou o material por WhatsApp, extrai o visual"

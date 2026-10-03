# Tipografia: identificar a familia e escolher o equivalente

Raster nao guarda nome de fonte. Existem tres caminhos, em ordem de confianca.

## 1. Ler do documento-fonte (melhor)

Se a marca tem manual, site, deck ou template, o nome real esta la e o `extrair.py`
le com `--fonte`:

| Arquivo | Onde esta o nome |
|---|---|
| PDF com texto | fontes embutidas (`pymupdf`); o script lista e avisa se vier rasterizado |
| PPTX / DOCX | `theme1.xml` do proprio arquivo (majorFont, minorFont) |
| Site / CSS | declaracoes `font-family` |
| SVG do logo | atributo `font-family` do texto, quando o logo nao foi convertido em curvas |

Se o PDF vier rasterizado (jsPDF e Canva exportam assim), nao ha fonte embutida —
o arquivo virou um monte de imagem. Foi o caso do material da Sousa Lima: o
caminho 2 resolveu.

## 2. Identificar a olho (o caso comum)

Quando so existe imagem, olhe a peca em zoom e classifique pelas marcas visiveis:

- **Serifa ou sem serifa.** Serifa (Baskerville, Playfair, Cinzel) ou sem
  (Inter, Montserrat, Plus Jakarta).
- **Esqueleto geometrico ou humanista.** O `o` e um circulo quase perfeito
  (Futura, Poppins, Montserrat) ou e uma forma oval irregular (Inter, Helvetica)?
- **Largura e peso.** Condensada (Roboto Condensed, Oswald), normal, expandida.
  Peso 800-900 com contraforma pequena = display de impacto.
- **Terminais e detalhes.** Corte reto, corte arredondado, "A" de topo reto
  (Bank Gothic, Michroma), "G" com esporao, "R" com perna reta.
- **O que a peca faz com a fonte.** Titulo em caixa alta condensada com peso
  maximo e corpo em sans neutra normalmente sao duas familias, nao uma.

Registre a conclusao como **hipotese**, nao como fato: `"familia_aparente": "sans
geometrica, peso 800, caixa alta condensada"`. Isso e honesto e continua util para
quem for escolher a fonte.

## 3. Escolher o equivalente livre (o que entra no material)

A marca quase nunca tem o arquivo da fonte, e usar a fonte original costuma ser
licenca paga. O que entra no material e o equivalente livre mais proximo, com todos
os acentos conferidos, declarado como aproximacao no guia.

| Se a peca parece | Equivalente livre | Onde |
|---|---|---|
| Bank Gothic / Microgramma (quadrada, tecnica) | **Michroma** | Google Fonts, OFL |
| Futura / geometrica de display | **Poppins** | Google Fonts, OFL |
| Helvetica / neo-grotesca neutra | **Inter** | Google Fonts, OFL |
| Grotesca de sistema Apple | **Inter** | Google Fonts, OFL |
| DIN / tecnica de sinalizacao | **Barlow** | Google Fonts, OFL |
| Humanista com serifa | **Source Serif** | Google Fonts, OFL |
| Clasica de solenidade | **Cinzel** | Google Fonts, OFL |
| Sans humanista (calor, institucional) | **Plus Jakarta Sans** | Google Fonts, OFL |
| Slab / peso de impacto | **Roboto Slab** | Google Fonts, OFL |
| Monoespacada tecnica | **JetBrains Mono** | Google Fonts, OFL |

O que **nao** fazer: cair na fonte do sistema (DejaVu, Liberation, Arial) porque
nao instalou nada. E isso que faz a peca parecer amadora, e o olho percebe antes de
saber o nome.

## Baixar e instalar na identidade

Os arquivos vao para `<pasta-da-identidade>/fontes/`, em woff2 (site) e ttf
(documento, PDF, PIL):

```bash
python3 scripts/fontes.py "Montserrat" --pesos 400,700,800 --destino identidade/fontes
python3 scripts/fontes.py "Inter" --pesos 400,600 --destino identidade/fontes --declarar
```

O `--declarar` imprime o bloco `fontes` pronto para colar no `identidade.json`.

O script existe porque o download a mao erra em silencio: o CSS do Google Fonts traz
**um @font-face por subset de unicode** (latin, latin-ext, cyrillic...) para cada peso,
entao juntar as URLs na ordem em que aparecem escreve cinco subsets no mesmo arquivo e o
ultimo sobrescreve os outros. A fonte instala, o site abre, e "ção" sai em branco. O
script filtra os subsets que cobrem portugues e nomeia `-latin`/`-ext`; quando varios
pesos apontam para o mesmo arquivo, ele grava um so e marca como `variavel` — e a fonte
variavel do Google, que cobre a faixa toda num arquivo.

O `prova.py` embute automaticamente o que estiver em `fontes/`, ligando a familia
`display` ao titulo e a `texto` ao corpo, e **avisa na prova** quando nao ha arquivo.
Sem arquivo, a prova mostra a letra errada — e prova com letra errada e pior que prova
nenhuma, porque quem aprova aprova o que viu.

Fonte paga sem arquivo: procure a alternativa livre de mesma familia e registre no
guia que e aproximacao. Se a marca exigir a original, ela tem de ser comprada —
nao ha caminho tecnico que resolva licenca.

## Escala de tipo

Nao se copia tamanho de peca de rede social: ela e feita para ser lida de longe, e
aplicar 88 px num documento A4 nao funciona. A escala se define por target:

- **Site / sistema:** base 16 px, razao 1.25 (major third) e passos nomeados
  (`xs` a `4xl`); o `tokens.py --escala-base 16` deriva isso e marca como derivado.
- **Documento:** corpo 11-12 pt, titulo 18-24 pt, legenda 9 pt.
- **Peca de rede:** titulo 60-100 px conforme o formato, corpo 24-40 px.
- **Video:** ver a escala em `brand.json` do terras-brand (`tipografia.video`).

O que **se conserva** da peca original e a relacao: quantas vezes o titulo e maior
que o corpo, se o titulo ocupa uma ou duas linhas, se o texto corre em caixa alta.
Isso e direcao de arte e viaja entre formatos; o numero em pixel nao.

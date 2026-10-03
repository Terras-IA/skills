---
name: terras-ebook
description: "Cria e-book e audiolivro para vender: estrutura, diagramação, EPUB e PDF A5 diagramado como livro, capa, ISBN, escolha de plataforma, royalties, preço e lançamento — e transforma acervo de YouTube em e-book. Use quando o pedido envolver e-book, ebook, livro digital, EPUB, PDF de livro, Kindle, Amazon KDP, Kobo, Apple Books, Gumroad, Payhip, Draft2Digital, IngramSpark, ISBN, capa de livro, diagramação, sumário clicável, folio, glossário, nota de rodapé, lead magnet, playbook, apostila, material didático, audiolivro de e-book, precificação de produto digital, estratégia de lançamento, ou 'transformar meus vídeos em livro'. Publish, sell, self-publish, ebook, glossary, royalty."
keywords: [ebook, e-book, epub, pdf, livro, kdp, kindle, amazon, gumroad, payhip, kobo, apple-books, draft2digital, isbn, capa, diagramacao, sumario, folio, royalties, preco, lancamento, lead-magnet, playbook, apostila, audiolivro, youtube, transcricao, self-publishing, glossario, nota-de-rodape]
---

# terras-ebook

## Objetivo

Levar um e-book do zero até a venda: definir estrutura e promessa, produzir o
texto, montar o arquivo (EPUB e/ou PDF diagramado), resolver capa e ISBN,
escolher onde publicar, precificar e lançar. Também empacota conteúdo que você já
tem — em especial o acervo de vídeos do YouTube — como e-book.

A camada comercial (plataforma, royalty, ISBN, preço, lançamento) é o que
diferencia esta skill das outras: as `terras-*` produzem conteúdo, esta decide
**como ele vira produto vendável**.

## Onde está instalada

Fonte única: `skills/terras-ebook/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

Dependências Python em `~/.config/terras-ebook/venv` (o python do sistema é
bloqueado por PEP 668); fontes da marca convertidas em `~/.config/terras-ebook/fontes/`:

```bash
bash $SKILL_DIR/scripts/setup.sh
```

## Qual formato entregar

Não é questão de gosto: é onde o produto vai ser vendido.

| Destino | Formato | Por quê |
|---|---|---|
| Amazon KDP, Apple Books, Kobo, D2D | **EPUB** | loja de ebook só distribui EPUB (ou converte dele) |
| Gumroad, Payhip, Hotmart, venda direta | **PDF A5** | controle total do desenho, sem reflow do leitor, margem melhor |
| Impressão (KDP Print, IngramSpark) | **PDF** | 300 DPI e corte definido |
| Lead magnet, isca de lista | PDF curto | abre em qualquer lugar, não depende de leitor de ebook |

Na dúvida: os dois. O texto é o mesmo; muda só a montagem final.

## Duas rotas de produção

```
ROTA B (recomendada, sem chave paga)      ROTA A (automação completa)
────────────────────────────────────      ──────────────────────────
1. coletar  (get_videos.py)               1. main.py faz tudo:
2. transcrever (get_transcripts.py)          buscar → transcrever →
3. escrever os artigos NA SESSÃO             escrever (API Anthropic) →
   (o próprio agente redige, em PT-BR)       montar EPUB → enviar por e-mail
4. montar o arquivo: EPUB ou PDF
```

**Rota B** é o caminho quando você quer o texto na sua voz e em português, sem
pagar API: o agente faz a parte de escrita e só usa script para coletar,
transcrever e empacotar. **Rota A** é o piloto automático (newsletter recorrente)
e usa três chaves — duas delas pagas.

## Rota B, passo a passo

```bash
SK=$SKILL_DIR/scripts
PY=~/.config/terras-ebook/venv/bin/python

# 1. quais canais acompanhar (um @handle por linha)
$EDITOR $SK/canais.txt

# 2. último vídeo longo de cada canal
$PY $SK/get_videos.py --json /tmp/videos.json

# 3. transcrição (grátis primeiro, Supadata só se falhar)
$PY $SK/get_transcripts.py --entrada /tmp/videos.json --saida /tmp/transcricoes.json

# 4. a sessão lê /tmp/transcricoes.json e escreve um .md por capítulo em ./artigos/
#    e, junto, o termos.md — o glossário do livro (ver `## Glossário` adiante)

# 5a. montar EPUB (loja de ebook) — o termos.md da pasta entra sozinho
$PY $SK/export_epub.py --pasta ./artigos --titulo "Meu e-book" --autor "Seu Nome"

# 5b. montar PDF A5 na identidade (venda direta e impressão)
$PY $SK/montar_manuscrito.py --pasta ./artigos \
    --titulo "Meu e-book" --autor "Seu Nome" --kicker "GUIA ESTRATÉGICO" \
    --subtitulo "linha de apoio" --rodape "meusite.com.br"
$PY $SK/build_ebook.py manuscrito.json --saida livro.pdf
#    a identidade é a do diretório (`identidade/`, ao lado do manuscrito): na
#    primeira montagem ela é copiada da base da casa. Nada de flag, e vale de
#    qualquer diretório de trabalho.
```

## Identidades — e a identidade é do diretório

Uma identidade é um JSON com cores, fontes e ativos, e **ela mora dentro do
projeto**, em `<projeto>/identidade/`, ao lado do manuscrito:

```
projeto/
├── artigos/            os capítulos (.md) e o termos.md
├── identidade/         a identidade DESTE livro
│   ├── identidade.json
│   ├── fontes/         as fontes que ele usa
│   └── *.png           logo, monograma, fundo, padrão
└── manuscrito.json     capa, capítulos e termos
```

**Diretório que ainda não tem uma recebe a cópia da base da casa** (Sousa Lima),
autocontida, na primeira montagem — o script diz que copiou e onde. A partir daí
editar cores, fontes e logo ali não mexe em nenhum outro livro, e montar de outra
pasta (ou esquecer o flag) deixa de ser motivo para o livro sair com a cara errada.
A ordem de precedência é:

| O que vale | Quando |
|---|---|
| `--identidade CAMINHO` | identidade avulsa, fora do projeto |
| `--identidade slc` / `terras` | atalhos: a base da casa e a marca terras |
| `identidade/identidade.json` do projeto | **o caso normal** — e é o que se edita por livro |
| a base da casa (cópia automática) | primeira montagem do diretório |
| `brand.json` do tema (`--tema`, `--brand-dir`) | só com `--identidade terras` |

```bash
# o normal: nada de identidade na linha de comando
$PY $SK/build_ebook.py manuscrito.json --saida livro.pdf
$PY $SK/export_epub.py --pasta artigos --titulo "Meu e-book"

# preparar (e editar) a identidade do projeto antes da primeira montagem
$PY $SK/identidade.py ./projeto

# exceções
$PY $SK/build_ebook.py manuscrito.json --identidade terras     # marca terras (brand.json)
$PY $SK/build_ebook.py manuscrito.json --identidade slc        # a base da casa, sem edições do projeto
$PY $SK/build_ebook.py manuscrito.json --identidade /caminho/identidade.json
```

As duas identidades prontas:

| Identidade | Cara | Onde está a base |
|---|---|---|
| **Sousa Lima Consultoria** (padrão) | navy `#040A21` + ciano `#00D2FF` + magenta `#DB00B6`, logo da consultoria, fundo de constelação, títulos em caixa alta (Michroma) e filetes em gradiente | `$SKILL_DIR/assets/sousa-lima/identidade.json` (é a base copiada para o projeto) |
| **terras** | preto `#060608` + ciano `#07d4ec`, Inter, capa com título à esquerda e 4 LEDs | `~/Documents/Diversos/terras-brand/brand.json` |

A identidade declara `cores` (base, acento, `acento_2` opcional, texto, e a versão
para papel claro — `tinta`, `linha_clara`, `papel_alt`), `fontes` (a de texto, com
pesos, e opcionalmente uma `display` para os títulos, uma `italico` para o itálico
do miolo e uma `mono` para código), `ativos` (logo claro e
escuro, monograma, fundo, padrão) e `capa_estilo` (`terras` desenha a capa em
vetor; `logo-rede` compõe com logo e fundo em imagem).

> A cópia carrega `_copiada_de` (origem e data) só para rastreio. Fonte trocada
> dentro do projeto gera cache novo sozinha — o cache leva impressão digital dos
> arquivos, então a conversão antiga não é reusada por engano.

### Forma da marca na capa

Declarada em `marca.estilo`, trocável na linha de comando:

| Estilo | O que desenha | Quando vale |
|---|---|---|
| `lockup` | a imagem do conjunto (monograma + nome + apoio), como na peça | quando a capa leva a marca gráfica inteira |
| `monograma-nome` | o símbolo, e o nome escrito na fonte de título | capa vista ampliada: o nome é vetorial e não amolece em nenhum zoom |
| `nome` | sem imagem de logo: só o nome e o apoio em texto | quando o nome basta e a marca gráfica custa qualidade (vem de raster pequeno) |
| `sem-marca` | **nada**: nem logo, nem nome, nem assinatura no rodapé | capa que não leva marca nenhuma — sobram tipografia, cores e estrutura (fundo, etiqueta, filetes) |

```bash
$PY $SK/build_ebook.py manuscrito.json \
    --marca sem-logo      # aceita o apelido; ou sem-marca / nome / monograma-nome / lockup
```

> **Vocabulário, e vale para as duas identidades.** "Sem logo" quer dizer
> `sem-marca` — a marca **inteira** some, inclusive a assinatura do rodapé; não é
> "trocar o logo pelo nome". Se a intenção for manter o nome em texto, o estilo é
> `nome`. Confundir os dois já custou uma rodada de retrabalho.

Marcas reais vêm em imagem, e imagem de template costuma ter borda macia: os
ativos `logo-*.png` e `monograma-*.png` são **silhueta chapada** (a extração
binariza, fecha cortes de 1 a 8 px e suaviza a borda), porque a sombra suave do
contorno, virada em transparência, aparece como risco escuro dentro do branco.
O canal entre as fitas do monograma é preservado — é ele que faz o entrelaçado
ser legível.

**O acento vivo não vira texto.** Ciano `#00D2FF` sobre papel branco dá ~1,9:1 de
contraste, muito abaixo do mínimo de 4,5:1. O montador calcula uma versão
escurecida do próprio acento para texto e guarda o acento puro para filetes e
marcas — vale para qualquer identidade nova.

Para montar uma identidade nova: copie o JSON da Sousa Lima, troque as cores,
aponte `fontes.arquivos` para os arquivos da marca (aceita TTF, OTF e woff2, e
fonte variável) e os `ativos` para o logo com transparência.

> A face de título da identidade Sousa Lima é **Michroma** (Google Fonts, OFL),
> a alternativa livre mais próxima: no PDF de referência a tipografia veio
> rasterizada, sem fonte embutida, então não havia arquivo para extrair. Se a
> fonte original aparecer, basta trocar o arquivo em `fontes/`.

## A rota PDF por dentro

O `build_ebook.py` monta um livro de verdade, não um relatório:

- **Capa e miolo são dois PDFs mesclados.** Desenhar a capa no `onFirstPage`
  faz o texto do primeiro capítulo carimbar por cima dela.
- **Sumário clicável.** As caixas das linhas são medidas com `pdfplumber` e as
  anotações escritas com `pypdf` **depois** do merge — destino nomeado do
  ReportLab não sobrevive à capa na frente. Cada entrada tem também o folio
  impresso, e o sumário é montado em duas passadas para acertar a numeração.
- **Na identidade da marca, e não só uma.** A identidade é um JSON: cores, fontes
  e ativos (logo, fundo). Duas estão prontas (ver `## Identidades`), e o
  `--identidade` troca tudo de uma vez. Nada de hex solto no código. Capa e miolo
  saem da mesma fonte de tokens, então trocar de identidade não deixa o livro
  meio a meio.
- **Fonte da marca.** A Inter da marca é variável e vem em woff2, que o
  ReportLab não lê: o script extrai as instâncias estáticas (400/600/700) e
  **junta as duas subsets**, porque a "latin-ext" sozinha não tem `ç` nem `ã` —
  texto sem esses caracteres deixa de ser extraível no PDF (busca e cópia
  morrem) e o acento sai errado. A conversão roda uma vez e fica em cache.
- **Cor de texto não é cor de enfeite.** O ciano puro tem ~2:1 de contraste sobre
  papel branco. No miolo, texto em acento usa uma versão escurecida (calculada
  para passar de 4.5:1); o ciano puro fica em filetes e marcas.
- **Nota de pé de página tem faixa reservada só na página que a recebe.** O
  ReportLab não tem nota de pé de página: quem carrega o marcador avisa em que
  página foi desenhado, e o miolo é montado mais de uma vez até a reserva de cada
  página parar de mudar — senão a nota cairia por cima da última linha do texto.

Convenções do markdown de entrada (detalhe em `references/manuscrito.md`):
`# Título` abre capítulo, `##` vira subtítulo, `>` vira citação, `> **RÓTULO**`
vira caixa de destaque, tabela de barra vira tabela, e arquivo começando com `_`
ou título de abertura/fecho (Introdução, Prefácio, Conclusão) entra **sem**
numeração de capítulo. `termos.md` não é capítulo: é a tabela de termos do
glossário (ver adiante).

## Glossário, e a nota no pé da página

**Todo livro sai com um glossário curto** — de 5 a 12 termos que quem é de fora do
assunto não teria como saber, com definição de uma ou duas linhas. Os mais
específicos aparecem também **no pé da página em que são usados**, com o número
marcado no texto: é o que resolve o termo técnico sem interromper a leitura.

As duas coisas saem de uma lista só. Escreva `termos.md` na pasta dos artigos:

```markdown
| Termo | Definição | Rodapé | Também em |
|---|---|---|---|
| Breakeven | Ponto de equilíbrio: o faturamento em que a receita cobre todos os custos. | sim | ponto de equilíbrio |
| VRIO | Teste dos recursos internos em valor, raridade, inimitabilidade e organização. | não | Matriz VRIO |
```

O que o montador faz com ela, nos dois formatos:

- **A primeira ocorrência no livro é a que vale.** A nota (ou o link) sai na
  primeira vez que o termo aparece; repetir a cada menção é ruído.
- **`Rodapé: não`** deixa o termo só no glossário do fim — para definição longa ou
  termo que não merece interromper a página. Coluna ausente conta como `sim`.
- **Termo que o texto não usa fica de fora**, e o montador avisa quais foram: o
  glossário descreve o livro que existe, não o que poderia existir.
- **`Também em`** são as outras formas do termo no texto (`receitas recorrentes`),
  e é por elas que a busca acha a primeira ocorrência.
- **Definição de termo com rodapé precisa caber em duas linhas.** Passando de ~190
  caracteres, o montador avisa: nota longa come a mancha e vira parágrafo.
- **No EPUB não existe página fixa**, então o termo vira link para o verbete, no
  mesmo lugar do texto. A intenção de `Rodapé` é a mesma nos dois formatos.

```bash
# o termos.md da pasta entra sozinho no manuscrito; o --glossario é o atalho
# para um manuscrito já pronto, e o --sem-notas deixa só o glossário do fim
$PY $SK/montar_manuscrito.py --pasta ./artigos --titulo "Meu e-book"   # lê termos.md
$PY $SK/build_ebook.py manuscrito.json --glossario artigos/termos.md
$PY $SK/export_epub.py --pasta ./artigos --titulo "Meu e-book"
```

O capítulo de fecho entra no sumário, no link do sumário e na barra lateral do
leitor com o rótulo `Glossário` (`glossario_titulo`, no manuscrito, troca o
rótulo). Se o livro já tem um capítulo de glossário escrito à mão, os verbetes
entram nele em vez de nascer um segundo. Formato completo em
`references/manuscrito.md`.

## Rota A, passo a passo

```bash
SK=$SKILL_DIR/scripts
PY=~/.config/terras-ebook/venv/bin/python
cp $SK/.env.example $SK/.env && $EDITOR $SK/.env   # chaves
$PY $SK/main.py                                    # pipeline inteiro
```

As etapas também rodam separadas (`get_videos.py --json` →
`get_transcripts.py` → `write_articles.py --entrada ... --saida ...` →
`export_epub.py` / `build_ebook.py`), o que ajuda a testar sem gastar API.

## Conferir antes de entregar

Sempre, e com a ferramenta certa:

```bash
python3 - <<'EOF'
import pymupdf as fitz
doc = fitz.open("livro.pdf")
print("páginas:", doc.page_count)
print("links:", [(l['page']+1) for p in doc for l in p.get_links() if l.get('kind') == fitz.LINK_GOTO])
print("marcadores:", [(t, pg) for _, t, pg in doc.get_toc()])
print("metadados:", {k: v for k, v in doc.metadata.items() if k in ("title","author")})
EOF
```

Três coisas para olhar: **os links apontam para as páginas certas**, **o texto
sai extraível** (se sair `\x00` ou quadradinho, a fonte embutida está sem os
caracteres) e **os metadados têm título e autor**.

> **Não verifique links com `pypdf`.** Os destinos saem como número de página
> inteiro, formato válido na especificação, mas que o `pypdf` não resolve — ele
> reporta como quebrado um link que está certo. O PyMuPDF resolve.

O montador já imprime, e vale ler antes de entregar: **qual identidade entrou**
(se não for a do projeto, pare e confira), **os folios de cada capítulo**, **em que
páginas caíram as notas de pé de página** e os três avisos do glossário — termo
declarado que o texto não usa, definição longa demais para nota e manuscrito sem
termo nenhum (livro sem glossário). Cada um deles é conteúdo a corrigir, não ruído
do script.

## Camada comercial — qual referência carregar

As referências comerciais vieram do `ebook-publishing-skill` (inglês, MIT) e são
a parte "vendável": leia a que corresponde à decisão da vez.

| Arquivo | Carregue quando |
|---|---|
| `references/platforms.md` | escolher plataforma, comparar royalties, ver quem aceita qual formato |
| `references/isbn-strategy.md` | decidir ISBN, entender a armadilha do ISBN grátis da KDP |
| `references/promotion.md` | lançamento, BookBub, permafree, preço de série, ARC |
| `references/cover-specs.md` | especificação de capa por plataforma (medidas conferidas) |
| `references/formatting.md` | cadeia EPUB com Pandoc/Calibre, EPUBCheck |
| `references/audiobooks.md` | audiolivro: ACX, ElevenLabs, KDP Virtual Voice, INaudio |
| `references/manuscrito.md` | escrever ou editar o JSON que o `build_ebook.py` consome |

Decisões que valem antes de qualquer coisa (detalhe nas referências):

- **Capa**: para loja, desenhar em 2560 × 1600 px, 300 DPI, cobre todas as plataformas.
- **ISBN**: nunca usar o ISBN grátis da KDP se pretende publicar fora da Amazon —
  ele prende você lá. Cada formato (ebook, brochura, capa dura, audiolivro) tem
  ISBN próprio.
- **Royalty KDP**: 70% entre US$2,99 e US$9,99; 35% fora dessa faixa. É o que
  define o preço-alvo de um guia completo (US$7,99–9,99).
- **Exclusivo x amplo**: ficção costuma ganhar com KDP Select (Kindle Unlimited,
  janelas de 90 dias); não-ficção e autor já estabelecido tendem a ganhar indo
  amplo desde o primeiro dia.
- **PDF pago direto** (Gumroad/Payhip) rende margem maior que loja de ebook —
  mas só vende com lista ou tráfego próprio.

## O que compõe com o resto do stack

| Necessidade | Skill que resolve |
|---|---|
| Capa, banner e mockup na identidade da marca | `terras-banner` (arte por modelo) |
| Audiolivro do e-book (mp3 por capítulo, m4b, loudness ACX) | `terras-audio` (comando `livro`) |
| Tirar cara de IA do texto antes de publicar | `terras-humanizer` |
| Validar se o tema tem demanda antes de escrever | `terras-last30days` |
| Divulgar o lançamento (newsletter, post) | `terras-substack`, `terras-linkedin` |
| PDF de relatório (não livro), planilhas, apresentações | plugins `pdf`, `xlsx`, `pptx` |

> Antes de vender audiolivro feito com voz do `edge-tts`, confira os termos de uso
> da plataforma — a própria `terras-audio` avisa sobre isso.

## Chaves, custos e limites

| Etapa | Precisa de | Custo |
|---|---|---|
| Buscar vídeos | `YOUTUBE_API_KEY` | grátis (cota diária do Google) |
| Transcrever (1ª tentativa) | nada | grátis |
| Transcrever (fallback) | `SUPADATA_API_KEY` | pago, com cota gratuita — https://supadata.ai |
| Escrever artigos na rota A | `ANTHROPIC_API_KEY` | **cobrado por uso** |
| Escrever artigos na rota B | nada | grátis (usa a sessão) |
| Montar EPUB ou PDF | nada | grátis, local |
| Enviar por e-mail | `GMAIL_ADDRESS` + senha de app | grátis |

## Limites conhecidos

- **`epubcheck` não roda aqui**: exige Java, que não está instalado. A estrutura
  do EPUB foi validada (mimetype, OPF, nav, metadados), mas a validação exigida
  por Apple Books e Kobo precisa de Java + epubcheck, ou de Calibre. Para KDP dá
  para enviar assim: a Amazon valida na conversão.
- `calibre` (comando `ebook-convert`) também não está instalado.
- O `dashboard.py` pede `streamlit`, que não foi instalado (é pesado, puxa
  pandas/pyarrow). Instale só se quiser o painel.
- As referências são de **março/2026** e cobrem plataformas internacionais
  (Amazon, Apple, Gumroad, Kobo, D2D, IngramSpark, Payhip, Google Play).
  Plataformas brasileiras de produto digital (Hotmart, Kiwify, Eduzz) **não**
  estão cobertas — trate-as como decisão à parte.
- Os arquivos de `references/` estão em inglês, exceto `manuscrito.md`; a skill
  escreve e monta em PT-BR por padrão (`TERRAS_EBOOK_IDIOMA`).
- O caminho de e-mail (`send_email.py`) mantém o template HTML em inglês; o
  EPUB dele já sai com metadados configuráveis.
- **Licença**: o `build_ebook.py` veio de um zip sem licença declarada — ver
  `CREDITS.md` antes de redistribuir a skill.

## Créditos

Combina `arturseo-geo/ebook-publishing-skill` (referências comerciais),
`zarazhangrui/youtube-to-ebook` (pipeline de vídeo → EPUB) e um montador de PDF
A5 de origem não identificada. Ver `CREDITS.md` para atribuição, licenças e a
lista de correções feitas na importação.

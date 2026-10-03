# Manuscrito JSON

É o que o `build_ebook.py` consome. Em geral você não escreve isto à mão: o
`montar_manuscrito.py` gera a partir de markdown (`--pasta artigos/`) ou da lista
de artigos do pipeline (`--json artigos.json`).

## Estrutura

```json
{
  "output": "/caminho/livro.pdf",
  "title": "Do Rascunho ao Produto",
  "title_lines": ["Do Rascunho ao", "Produto"],
  "author": "Everton Lima",
  "kicker": "GUIA ESTRATÉGICO",
  "subtitle_lines": ["Método, não sorte", "para publicar o que você já sabe"],
  "cover_footer": "eolimabr.substack.com",
  "running_header": "DO RASCUNHO AO PRODUTO",
  "running_header_right": "Everton Lima",
  "glossario": [
    {"termo": "Breakeven", "definicao": "Ponto de equilíbrio: o faturamento em que a receita cobre todos os custos.", "variantes": ["ponto de equilíbrio"], "rodape": true},
    {"termo": "VRIO", "definicao": "Teste dos recursos internos em valor, raridade, inimitabilidade e organização.", "rodape": false}
  ],
  "chapters": [
    {
      "id": "cap1",
      "toc": "1. O custo invisível de automatizar tudo",
      "outline": "1. O custo invisível de automatizar tudo",
      "kicker": "CAPÍTULO 01",
      "title": "O custo invisível de automatizar tudo",
      "blocks": [
        {"type": "p", "text": "Parágrafo. Aceita <b>negrito</b> e <i>itálico</i>."},
        {"type": "h", "text": "Subtítulo"},
        {"type": "ul", "items": ["<b>Item.</b> texto", "outro item"]},
        {"type": "destaque", "label": "O CRITÉRIO", "text": "Caixa com filete ciano."},
        {"type": "quote", "text": "Citação centralizada em itálico."},
        {"type": "table", "headers": ["A", "B"], "rows": [["1", "2"], ["3", "4"]]}
      ]
    }
  ]
}
```

## Campos

| Campo | Para que serve |
|---|---|
| `output` | Caminho padrão do PDF (o `--saida` da linha de comando ganha dele) |
| `title` | Título do livro e metadado do PDF |
| `title_lines` | Como o título é desenhado na capa, uma linha por item |
| `author` | Capa e metadado |
| `kicker` | Etiqueta pequena no alto da capa |
| `subtitle_lines` | Linhas de apoio abaixo do título |
| `cover_footer` | Tag no rodapé da capa, com filete ciano acima |
| `running_header` / `running_header_right` | Fio-de-pé das páginas do miolo |
| `glossario` | Lista de termos do glossário (ver adiante) |
| `glossario_titulo` | Rótulo do capítulo de fecho (padrão: `Glossário`) |
| `chapters[].toc` | Como o capítulo aparece no sumário (**esta é a linha que vira link**) |
| `chapters[].outline` | Nome do marcador na barra lateral do leitor |
| `chapters[].kicker` | Etiqueta acima do título do capítulo; **precisa ser única e aparecer no texto da página**, porque é por ela que o script descobre a página de destino do link |
| `chapters[].title` | Título do capítulo no miolo |
| `blocks` | Conteúdo do capítulo |

## Blocos

| `type` | Campos | Vira |
|---|---|---|
| `p` | `text` | Parágrafo justificado, com recuo de primeira linha |
| `h` | `text` | Subtítulo |
| `ul` | `items` | Lista com marcador e recuo pendente |
| `ol` | `items` | Lista numerada |
| `destaque` | `label`, `text` | Caixa de fundo claro com filete ciano à esquerda |
| `quote` | `text` | Citação centralizada em itálico |
| `table` | `headers`, `rows` | Tabela com cabeçalho na cor de acento; a primeira linha de cada célula aceita marcação |
| `imagem` | `caminho`, `legenda` | Prancha: a ilustração ocupa a página, com a legenda abaixo |
| `codigo` | `linhas`, `linguagem` | Bloco de código: caixa de fundo claro com filete à esquerda, em monoespacada (a `fontes.mono` da identidade; sem ela, uma do sistema), com o recuo da linha preservado |
| `glossario` | `itens` | Lista de verbetes (termo em negrito, definição recuada). É gerado pelo montador — não se escreve à mão |

## Glossário e notas de pé de página

Todo livro sai com um glossário curto no fim, e os termos mais específicos ganham
nota no pé da página em que aparecem. As duas coisas saem da **mesma lista**, e a
mesma lista governa o PDF e o EPUB (ver `scripts/glossario.py`).

| Campo do termo | Para que serve |
|---|---|
| `termo` | Como o verbete sai impresso no glossário |
| `definicao` | Uma ou duas linhas. Definição de termo com rodapé acima de ~190 caracteres vira aviso na montagem |
| `variantes` | As outras formas com que o texto chama o termo (`receitas recorrentes`, `Matriz VRIO`). É o que a busca procura; o `termo` entra sempre |
| `rodape` | `true` (padrão) põe o termo **no ponto de uso**: nota numerada no PDF, link para o verbete no EPUB. `false` deixa o termo só no glossário do fim |

Regras que o montador aplica:

1. **A primeira ocorrência no livro é a única que vale.** Repetir a nota a cada
   menção é ruído, e o glossário do fim cobre quem chegar depois.
2. **Termo que o texto não usa fica fora do glossário** — o montador avisa quais
   foram declarados e não usados, para a lista não virar catálogo.
3. **Bloco `imagem` não recebe marcador**: a legenda é desenhada junto da prancha, e
   uma nota ali sairia sem página para acompanhar.
4. O capítulo do glossário é montado no fim, entra no sumário e no link, e **não
   recebe marcador nenhum**. Se já existir um capítulo de glossário escrito à mão
   (título `Glossário`, `Glossário do Guia`...), os verbetes entram nele.

Na prática, você não escreve isto à mão: o `montar_manuscrito.py` lê a tabela de
`termos.md` e a coloca no JSON. O `build_ebook.py` também aceita `--glossario
arquivo` para injetar a lista num manuscrito já pronto, e `--sem-notas` para deixar
só o glossário do fim.

Em `ul` e `ol`, cada item é `{"text": "...", "nivel": 0}` — `nivel: 1` é subitem
(marcador travessão e recuo; em lista numerada o subitem continua numerado). Um
manuscrito antigo, com itens em texto puro, continua valendo.

## Convenções de markdown (o que a ponte entende)

| No markdown | Vira |
|---|---|
| `# Título` | título do capítulo (vai para o sumário; não é impresso se o arquivo for só imagem) |
| `##` / `###` | subtítulo dentro do capítulo |
| `- item` / `1. item` | lista com marcador / lista numerada |
| `    - subitem` | subitem (**quatro espaços**: é o que faz o markdown aninhar também no EPUB) |
| `> texto` | citação |
| `> **RÓTULO**` + texto | caixa de destaque com esse rótulo |
| `\| a \| b \|` | tabela (a primeira linha é o cabeçalho) |
| `![legenda](imagem.png)` | prancha de página inteira (caminho relativo ao arquivo) |
| ` ``` ` ... ` ``` ` | bloco de código: entra **verbatim** (recuo, `#`, `|` e `>` valem como código, não como markdown). A cerca tem de abrir e fechar; sem fechamento, o bloco vai até o fim do arquivo |
| `[texto](url)` | "texto (url)" — legível também no papel |

**`termos.md` na pasta dos artigos não é capítulo.** É a tabela de termos do
glossário:

```markdown
| Termo | Definição | Rodapé | Também em |
|---|---|---|---|
| Breakeven | Ponto de equilíbrio: o faturamento em que a receita cobre todos os custos. | sim | ponto de equilíbrio |
| VRIO | Teste dos recursos internos em valor, raridade, inimitabilidade e organização. | não | Matriz VRIO |
```

As colunas são lidas **pelo nome**, em qualquer ordem (`Termo`, `Definição`,
`Rodapé`, `Também em`/`Variantes`); sem cabeçalho reconhecível, vale a ordem da
tabela. `Rodapé` vazio conta como `sim`. Sem tabela, também vale uma linha por
termo no formato `**Termo** — definição`. O `montar_manuscrito.py` e o
`export_epub.py` pulam esse arquivo na hora de listar capítulos, e por isso o nome
é reservado.

**Ordem e numeração dos arquivos:** o prefixo numérico define a ordem
(`_00-abertura.md` vem antes de `01-....md`, e `_90-fecho.md` por último). O `_` no
começo só diz que o capítulo **não é numerado** — vale para abertura e fecho, e
não interfere na ordem. Título que já é de abertura ou fecho (Introdução,
Prefácio, Conclusão, Síntese...) também entra sem número.

**Arquivo cujo conteúdo é só uma imagem** vira prancha de página inteira, sem
cabeçalho de capítulo por cima; a legenda passa a ser a âncora de texto da página
(é por ela que o script descobre a página para o link do sumário).

1. **`text` é XML de parágrafo do ReportLab.** Use `<b>`, `<i>` e escape `&` como
   `&amp;`. O `montar_manuscrito.py` já faz isso; se você escrever o JSON à mão,
   não esqueça.
2. **Cuidado com `kicker` repetido.** Se dois capítulos tiverem a mesma etiqueta, o
   link do sumário do segundo pode apontar para a página do primeiro. O script
   falha de propósito quando não encontra a etiqueta, mas não tem como adivinhar
   duplicata.

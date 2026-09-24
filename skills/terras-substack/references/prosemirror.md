# Markdown, nos e diretivas (ProseMirror da Substack)

O editor da Substack guarda o corpo como um documento **ProseMirror**:
`{"type": "doc", "content": [no, no, ...]}`. A ferramenta converte markdown
neste formato e sabe fazer o caminho de volta (`get-draft --markdown`).

## Sintaxe markdown aceita

| Markdown | No gerado |
|---|---|
| `# / ## / ###` | `heading` com `attrs.level` |
| linha em branco + texto | `paragraph` (linhas soltas viram um paragrafo so) |
| `- item` / `1. item` | `bullet_list` / `ordered_list` + `list_item` |
| aninhamento com 2+ espacos | lista dentro do item anterior |
| `> texto` | `blockquote` (aceita varios paragrafos) |
| ```` ```lang ```` | `codeBlock` com `attrs.language` |
| `---` | `horizontal_rule` |
| `![alt](url)` sozinho na linha | `captionedImage` |
| `^ legenda` na linha seguinte a imagem | `caption` dentro da imagem |
| `**x**`, `*x*`, `***x***`, `~~x~~`, `` `x` ``, `[x](url)` | marks `strong`, `em`, `strong+em`, `strikethrough`, `code`, `link` |

Detalhe: `_x_` tambem vira italico, mas `nome_com_underscore` nao.

## Diretivas (recursos nativos da Substack)

| Diretiva | No gerado |
|---|---|
| `::: paywall` | `paywall` (corte de assinatura) |
| `::: subscribe Texto` | `subscribeWidget` + `ctaCaption` |
| `::: button Texto \| https://url` | `button` |
| `::: caption Texto` | legenda da ultima imagem |
| `::: pullquote` ... `:::` | `pullquote` |
| `::: callout` ... `:::` | `calloutBlock` |
| `::: divider` | `horizontal_rule` |

Diretiva desconhecida faz a conversao falhar de proposito, com o nome do
problema — melhor falhar do que publicar sem o bloco.

## Formas dos nos (referencia rapida)

```json
{"type": "paragraph", "content": [{"type": "text", "text": "ola"}]}
{"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "T"}]}
{"type": "text", "text": "forte", "marks": [{"type": "strong"}]}
{"type": "text", "text": "link", "marks": [{"type": "link", "attrs": {"href": "https://x"}}]}
{"type": "bullet_list", "content": [{"type": "list_item", "content": [{"type": "paragraph", "content": []}]}]}
{"type": "blockquote", "content": [{"type": "paragraph", "content": []}]}
{"type": "codeBlock", "attrs": {"language": "python"}, "content": [{"type": "text", "text": "x = 1"}]}
{"type": "horizontal_rule"}
{"type": "paywall"}
{"type": "subscribeWidget", "attrs": {"url": "%%checkout_url%%", "text": "Subscribe", "language": "pt"},
 "content": [{"type": "ctaCaption", "content": [{"type": "text", "text": "Assine"}]}]}
{"type": "button", "attrs": {"href": "https://x", "text": "Assinar"}}
```

Imagem com legenda — o no externo e `captionedImage`, o interno e `image2`:

```json
{
  "type": "captionedImage",
  "content": [
    {"type": "image2", "attrs": {
      "src": "https://substackcdn.com/image/...", "alt": "descricao",
      "fullscreen": false, "imageSize": "normal", "resizeWidth": 728,
      "width": 1456, "height": 819, "bytes": null, "title": null, "type": null,
      "href": null, "belowTheFold": false, "topImage": false,
      "internalRedirect": null, "isProcessing": false, "align": null, "offset": false
    }},
    {"type": "caption", "content": [{"type": "text", "text": "Legenda"}]}
  ]
}
```

Outros nos do schema, ainda nao gerados pela conversao (a conversao reversa
devolve `<!-- no nao convertido: X -->` para nao perder informacao em silencio):
`footnote` / `footnoteAnchor`, `latex_block` / `latex`, `digestPostLink`,
`embeddedPublication`, `youtube2`, `toc`.

## Marks

`strong`, `em`, `code`, `strikethrough`, `superscript`, `subscript`,
`link` (com `attrs.href`).

## Avisos de compatibilidade

- O `heading` correto tem `attrs.level`. Alguns clientes escrevem `level` na
  raiz do no — funciona no editor, mas nao e o schema do ProseMirror. A
  ferramenta usa `attrs.level`.
- `draft_body` vai como **string JSON** dentro do payload; se for enviado como
  objeto, a Substack grava um rascunho vazio.
- Um rascunho criado pela API e um rascunho normal: pode ser aberto, editado e
  publicado no editor web.

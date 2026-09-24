# Direção de arte do banner

O que decide se a imagem parece feita por gente ou por template: a arte de fundo, a
fonte e o espaço negativo. Cor e forma são o de menos.

## Escolher o fundo

| Caminho | Quando | Como |
|---------|--------|------|
| Foto editorial gerada | Default para post de tema. Segura mais o olho no feed. | `scripts/gen_art.py` com prompt de cena e lugar vazio para o texto |
| Arte abstrata gerada | Tema conceitual, digest, anúncio | mesmo script, prompt de luz e forma |
| Fundo chapado com glow | Só quando não houver arte, ou para série muito austera | spec sem `bg`; usar com moderação, é o que parece template |
| SVG algorítmico | Série de posts iguais, sem foto, com variação | `design_engine.py` da skill `pdf`: `svg --svg-type flow\|grid\|noise\|supergraphic\|ordered_texture --dimensions 1200x628 --color "#ffcc33"` |

## Prompts que funcionaram

Foto (a melhor até agora, espaço à esquerda respeitado):

```
moody low-key photograph of a dark modern data center at night, shallow depth of
field, warm amber accent light from the right, deep shadows, generous dark negative
space on the left half, editorial, cinematic, no text, no letters, no words
```

Abstrato, na paleta da casa:

```
abstract editorial background, deep navy blue, soft diagonal gold light streaks,
subtle film grain, large dark empty area on the left half for typography, cinematic,
minimal, no text, no letters, no words
```

Três coisas fazem diferença no resultado:

1. **Dizer onde fica o vazio.** "generous dark negative space on the left half" é
   respeitado; sem isso a arte ocupa o quadro inteiro e o texto perde contraste.
2. **"no text, no letters, no words"** sempre, senão vem letra inventada.
3. **Citar a cor no prompt** (deep navy, warm amber, gold) para a arte já nascer na
   paleta, em vez de tentar corrigir depois.

Se o resultado vier claro demais à esquerda, aumentar `scrim` no spec (0.95 é o teto
prático) antes de mexer na arte.

## Modelos nesta chave

| Modelo | Nessa rota |
|--------|-----------|
| `qwen-image-3.0`, `qwen-image-3.0-pro` | OK, respeita `1200x628` |
| `qwen-image-2.0*`, `qwen-image-max`, `qwen-image-plus` | disponíveis na conta |
| `qwen-image-edit-*` | edição de imagem existente (trocar fundo, remover objeto) |
| `wan2.7-image`, `z-image-turbo` | 404 nessa rota |

## Arte em formato retrato

Gerar a arte NO tamanho do card em pé (1080x1350 ou 1080x1440), nunca reaproveitar a
arte 1200x628: no crop do retrato o assunto de paisagem (lado direito) vira uma faixa
lateral e sobra vão vazio no meio. Prompt: assunto na metade de cima, vazio embaixo:
"the subject positioned in the upper half of the frame, pure black empty space in the
lower half for typography". O template ancora a arte no topo em modo `tall`.

## Régua de leitura

- Manchete: até 3 palavras por linha, quebrando com `<br>`. Em 1200x628, 88px é o
  tamanho validado; acima de duas linhas, cortar palavra.
- Linha de apoio: uma linha só. Se quebrou, o texto é longo demais para o formato.
- Régua de dados: até 3 itens. Número grande no acento e rótulo curto.
- O espaço de texto útil é `largura - 2x78` em 1200x628, ou seja 1044px. O
  `--check` do render confere isso melhor que a conta na mão.
- Ler o PNG renderizado, não o HTML: arte clara atrás de texto claro só aparece no
  render final.

## O que não fazer

- Gradiente radial de duas cores como fundo único, com pílulas de borda arredondada:
  é a assinatura visual de banner genérico, e era exatamente o visual antigo.
- Fonte de sistema (DejaVu, Liberation, Nimbus) em peça de marca.
- Texto gerado pelo modelo de imagem.
- Mais de um acento forte competindo com o acento da marca.
- Encher de chips e selos: três dados bastam, o resto vira ruído em miniatura de feed.

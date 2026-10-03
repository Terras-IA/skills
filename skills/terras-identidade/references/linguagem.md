# Linguagem visual: o que a marca faz alem de cor e fonte

Cor e fonte sao o que se copia facil. E a linguagem visual — forma, tratamento de
imagem, grade, gesto de botao — que faz a peca nova parecer da marca mesmo quando
ninguem esta olhando as regras. E a parte que sempre falta quando a identidade e
resumida a "paleta + fonte".

O bloco `linguagem` do `identidade.json` guarda isso em texto curto, porque quem
aplica (outra sessao, outra pessoa, CapCut, Canva) precisa ler e entender em um
minuto. Preencha a partir das pecas, com o vocabulario de quem desenha.

## O que observar em cada peca

| Campo | Pergunta | Exemplo (Avancei) |
|---|---|---|
| `formas` | que geometria a marca usa como elemento? | explosao/estrela de 16 pontas, barra reta, retangulo chapado |
| `tratamento_de_foto` | como a foto entra? | duotone em meio-tom (retícula visível), gente recortada com contorno duro |
| `grade` | o fundo tem textura ou malha? | grade fina de quadrados sobre a cor chapada |
| `gesto` | o que se repete nos elementos de acao? | botao com sombra deslocada chapada (offset solido, sem blur) |
| `caixa_alta` | titulo em caixa alta? | sim, caixa alta com palavra-chave trocando de cor |
| `tipo_de_contraste` | texto sobre a cor da marca, ou o contrario? | branco sobre a cor; preto sobre o amarelo |
| `restricoes` | o que a marca nunca faz | — |

## Como escrever (o que serve e o que nao serve)

Serve:

- "foto entra em duotone de meio-tom, nunca colorida"
- "botao com sombra chapada deslocada 6 px, sem desfoque"
- "titulo em caixa alta, palavra-chave em cor de acento, quebra em ate 3 linhas"
- "elemento de destaque e a explosao de 16 pontas, sempre atras da pessoa"

Nao serve:

- "visual moderno e vibrante" (nao diz nada aplicavel)
- "usa formas geometricas" (qual forma? em que posicao? de que tamanho?)
- "cores alegres" (a paleta ja esta medida; isto e opiniao)

## Como isso vira material

A linguagem entra em tres lugares:

1. **No template da peca.** O gesto do botao, a grade de fundo e a forma de
   destaque sao HTML/CSS no template (`assets/prova.html` ja traz o botao e a caixa
   de destaque usando os tokens). Trocar o gesto do botao e uma linha de CSS, e e
   isso que faz a peca parecer da marca.
2. **No tratamento de imagem.** Duotone de meio-tom, vinheta, contorno duro: e
   receita de processamento (PIL/ImageMagick), nao texto de guia. Escreva a receita
   no bloco `linguagem.processo` para ela ser reproduzivel.
3. **Nas restricoes.** O que a marca nao faz tambem e identidade: "nunca gradiente
   de fundo", "nunca sombra difusa", "nunca foto colorida". Sem essa lista, quem
   aplica preenche o vazio com o gosto dele e a marca dilui.

## Tratamento de imagem: a receita do meio-tom

O duotone de retícula do Avancei e o tipo de tratamento que aparece em marca de
educacao, esporte e varejo. A receita, em PIL:

1. Converter para tons de cinza e aumentar o contraste (o meio-tom come o contraste
   medio).
2. Reduzir a resolucao pela metade, aplicar `ImageFilter.GaussianBlur(0.4)` e
   devolver ao tamanho — a retícula precisa de mancha, nao de detalhe.
3. Pontilhar: `Image.convert("1", dither=Image.Dither.FLOYDSTEINBERG)` na escala
   ampliada, ou um `point()` com função de limiar para o meio-tom de pontos graudos.
4. Colorir com duotone: mapear preto → cor escura da marca, branco → claro, com
   `ImageOps.colorize`.

A retícula tem de ser visivel no tamanho final. Retícula que desaparece na
exportacao deixa a imagem apenas suja — confira no PNG exportado, nao no preview.

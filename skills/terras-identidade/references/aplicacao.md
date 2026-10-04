# Aplicacao: a mesma identidade em site, sistema, documento e peca

A identidade e uma so; o que muda e o alvo. Aqui esta como ela entra em cada um,
sem voltar a decidir cor na hora de montar cada material.

## O que o `tokens.py` gera e quem consome

| Arquivo | Consome |
|---|---|
| `tokens.css` | site, landing page, peca em HTML (Chrome renderiza para PNG) |
| `tokens.json` | sistema, app, script (PIL, reportlab, gerador de video) |
| `tailwind.config.js` | projeto que usa Tailwind |
| `marca.md` | documento (Word/Docs), quem aplica a mao, revisao humana |

Nunca escreva hex na mao em material novo. Se o valor nao esta no `tokens.css` e
falta, ele falta no `identidade.json` — corrija a fonte e gere de novo. Cor copiada
para cinco arquivos envelhece em cinco ritmos diferentes, e em tres meses ninguem
sabe qual e a certa.

## Site

```html
<link rel="stylesheet" href="tokens.css">
```

O `tokens.css` sai com o tema escuro no `:root` e o claro em
`:root[data-tema="claro"]`. Então:

- fundo da pagina: `var(--cor-base)`, texto: `var(--cor-texto)`;
- texto secundario: `var(--cor-texto-apoio)`;
- link e botao: `var(--cor-acento)` no preenchimento, `-sobre-papel` quando for
  texto sobre fundo claro;
- filete e borda: `var(--cor-linha)`.

Para virar tema claro, `document.documentElement.dataset.tema = "claro"`. Marca de
fundo colorido (de um cliente multicolor) normalmente nao tem tema escuro: ela ja vive em cor, e o
"claro" dela e o papel.

**Atencao ao acento como texto de link.** Link e texto: sobre fundo claro use
sempre `--cor-acento-sobre-papel`, senao o link reprova em contraste e some para
quem tem baixa visao.

## Sistema e app

`tokens.json` traz os papeis ja resolvidos, com contraste calculado:

```json
{ "base": "#254de3", "texto": "#ffffff", "tinta": "#212324",
  "acentos": { "marca-1": { "hex": "#254de3", "contraste_papel": 6.37,
                            "sobre_papel": "#254de3", "sobre_base": "#d3dbf9" } } }
```

Regras que valem para interface (diferente de peca, onde o olho decide):

- **Estado.** Hover, ativo, foco e desabilitado se derivam da base: clarear 6% para
  hover, escurecer 8% para ativo, e o foco usa o acento. Nao crie cor nova.
- **Fundo de superficie.** `superficie` ja vem derivada da base com um toque de
  tinta, que e o que separa o cartao do fundo sem precisar de sombra.
- **Nunca acento puro em area grande.** Acento vivo em bloco grande cansa a vista e
  domina a tela; ele e para acao e destaque, nao para o fundo.

## Documento (Word, Google Docs, PDF)

O que viaja para documento e a tabela de cores do `marca.md` (HEX e RGB) mais as
fontes em arquivo.

- **Titulo:** familia de display, peso 700, na cor `tinta` ou no `base`.
- **Corpo:** familia de texto, peso 400, cor `tinta`, 11-12 pt.
- **Apoio, legenda e dado tecnico:** cor `apoio` ou `tinta_fraca`.
- **Destaque:** caixa com fundo `superficie` e filete na cor de marca. Nunca
  gradiente nem sombra difusa — em documento impresso isso sai sujo.
- **Fonte no Word:** fonte tem de estar instalada na maquina de quem abre. Se o
  documento circula, embuta (PDF) ou use a fonte do sistema mais proxima e avise.

Foi assim que saiu o livro da Congregacional: Plus Jakarta Sans nos titulos e no
corpo, Cinzel reservada para peca de solenidade, navy `#0F2744` na tinta e o ouro
so em filete e selo.

## Peca de marketing (banner, story, feed, anuncio)

Receita que ja funciona nesta casa: **HTML + tokens + Chrome headless**.

1. Escreva a peca (ou a pagina) em HTML usando `tokens.css` e o gesto da marca — botao
   com sombra chapada, grade de fundo, forma de destaque. A explosao de 16 pontas sai em
   `clip-path`: mascara por arquivo nao rendeu no Chrome headless, a forma simplesmente
   nao aparecia.
2. Renderize no tamanho exato:

   ```bash
   python3 $SKILL_DIR/scripts/render.py peca.html --tamanho 1080x1350 --saida story.png
   python3 $SKILL_DIR/scripts/render.py index.html --largura 1440 390 --prefixo layout
   python3 $SKILL_DIR/scripts/render.py index.html --pdf pagina.pdf
   ```

   O `render.py` captura pelo Chrome, corta a faixa vazia de baixo e aceita varias
   larguras de uma vez — evita o caminho manual, que erra o tamanho por alguns pixels e
   deixa faixa branca no pe. O `--pdf` sai numa folha do tamanho do conteudo, com texto
   vetorial e fundo preservado.
3. Passe o PNG pelo gate visual antes de entregar.

**Duas armadilhas do PDF**, as duas fazem o arquivo sair plausivel e errado:

- **Breakpoint de responsividade sem `screen and`.** O Chrome headless imprime avaliando
  o media query contra a largura de papel padrao (~816px), entao um `@media (max-width:
  860px)` cru faz o PDF sair na versao de celular, com metade da altura. Escrever
  `@media screen and (max-width: 860px)`.
- **Fundo colorido some** sem `print-color-adjust: exact` — que o `render.py` injeta.
  Numa marca que vive de faixa chapada, o PDF sairia branco com texto solto.

Para uma pagina inteira (landing), o exemplo pronto e o de um cliente multicolor em
`~/Documents/<cliente>/layout/`: as faixas de cor trocam por secao, cada uma com a grade
fina no fundo, e o texto sempre na cor que le sobre aquela faixa (branco sobre o azul e o
magenta, tinta sobre o amarelo e o papel).

Nao peca texto ao modelo de imagem: letra sai torta e com erro. A arte entra por
baixo, o texto entra em HTML por cima.

A `terras-banner` faz isso para o LinkedIn e a Substack; esta skill entrega o
`tokens.css` e a linguagem para qualquer outro formato.

## Livro e e-book

O `terras-ebook` (PDF e EPUB) consome um `identidade.json` com `cores`, `fontes`,
`ativos` e `marca.estilo`. Os campos desta skill sao os mesmos, entao uma
identidade extraida aqui entra la direto:

```bash
~/.config/terras-ebook/venv/bin/python $SKILL_DIR/../terras-ebook/scripts/build_ebook.py manuscrito.json \
    --identidade ~/Documents/<cliente>/identidade/identidade.json --saida livro.pdf
```

**Sempre com caminho absoluto.** A identidade mora no diretorio do projeto; passada
relativa, de outro diretorio ela nao existe e o build cai na identidade padrao sem
avisar.

`marca.estilo` aceita `lockup` (imagem do conjunto), `monograma-nome` (simbolo +
nome em texto), `nome` (so texto) e `sem-marca`. No vocabulario do Everton,
**"sem logo" quer dizer `sem-marca`: nada de marca, nem assinatura de rodape** —
tipografia, cores e estrutura continuam. Ja custou tres correcoes no mesmo dia
entender isso; nao reabra.

## Video

Cartelas e lower thirds saem do mesmo `tokens.css`; o `terras-video` tem os
templates de cartela e le o `brand.json` do terras. Para marca de cliente, gerar as
cartelas desta skill em PNG 1920x1080 e montar no editor.

## Ordem de trabalho, quando o material e grande

1. Extrair e conferir cor (2-3 pecas bastam).
2. Recortar a marca nas duas versoes.
3. Identificar a tipografia e instalar o equivalente livre.
4. Preencher `linguagem` a partir das pecas.
5. Gerar tokens.
6. Prova visual, gate visual, aprovacao humana.
7. So entao material: site, documento, peca.

Atalhar o passo 6 e onde o material sai com o acento ilegivel ou a marca invisivel
no fundo claro.

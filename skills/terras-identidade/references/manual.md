# Manual de identidade visual: o entregavel de 8 paginas

Quando o pedido e "monta a identidade" e nao "aplica a identidade", o entregavel
que ja foi aprovado nesta casa e um manual de 8 paginas em 16:9 (2560x1440), uma
secao por pagina, com uma capa de indice.

O modelo existe e foi usado no IECSJC: `~/Downloads/Manual de Identidade Visual -
8 Paginas Completas.pdf` (9 paginas, 2560x1440, imagens). Vale olhar antes de
montar, porque o desenho das paginas ja esta resolvido.

## As 8 secoes

| Pagina | Secao | O que ela mostra |
|---|---|---|
| 1 | Capa e indice | a marca grande, o titulo do manual, o indice das 8 secoes |
| 2 | Paleta de cores oficial | cada cor com nome, HEX, RGB, CMYK e uso |
| 3 | Tipografia corporativa | familia, pesos, hierarquia, amostra em tamanho real |
| 4 | Area de respiro e reducao | malha de protecao (modulo X) e tamanho minimo |
| 5 | Variacoes da marca | vertical, horizontal, simbolo isolado, negativo |
| 6 | Fundos e contrastes | comportamento em claro, escuro e sobre foto |
| 7 | Papelaria | cartao, timbrado, envelope, assinatura de e-mail |
| 8 | Sinalizacao e digital | fachada, rede social, avatar, apresentacao |

Nao invente secoes novas sem pedido. As 8 cobrem o que a grafica, o social media e
a grafica de fachada perguntam.

## Como montar

1. **Consolidar a identidade** (`extrair.py`, `medir.py`, `tipografia.md`) e
   preencher o `identidade.json` com `marca`, `ativos` e `linguagem`. O manual e a
   apresentacao do JSON — nada entra nele que nao esteja no JSON.
2. **Gerar os tokens**, para o manual e o material futuro usarem a mesma cor.
3. **Montar pagina a pagina em HTML** (uma seção por `<section>` de 2560x1440) e
   renderizar com o Chrome, como a prova visual. Uma peca de HTML por pagina fica
   mais facil de ajustar do que um unico arquivo gigante.
4. **Conferir CMYK.** HEX e RGB sao medidos; CMYK e conversao, e a grafica pode
   exigir o perfil dela. Se a marca vai ser impressa em cor exata, o CMYK tem de ser
   combinado com a grafica — escreva o RGB medido e marque o CMYK como referencia.
5. **Passar cada pagina pelo gate visual** antes de entregar. Manual e peca de
   aprovacao: sai uma vez e vale por anos.

## O que separa manual bom de enfeite

- **Regra aplicavel, nao adjetivo.** "Nunca esticar, alterar fontes ou aplicar cores
  fora do manual" (restricao do manual do IECSJC) e util; "design moderno e limpo"
  nao e.
- **Area de respiro com numero.** O manual do IECSJC define o modulo X como a altura
  da cruz do emblema e a reducao minima em 32 mm impresso e 120 px digital, com a
  instrucao de usar o icone isolado abaixo disso. Isso e o que impede a marca de
  sair apertada num cartao.
- **Aplicacao mostrada, nao descrita.** Papelaria e sinalizacao entram como desenho.
- **Nada de valor nao conferido.** Se o CMYK e estimado, diga; se a fonte e
  aproximacao livre, diga. Manual que mente em um numero perde credibilidade no
  resto.

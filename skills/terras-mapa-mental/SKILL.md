---
name: terras-mapa-mental
description: "Mapa mental a partir de texto, reunião, livro ou tema: roteiro em Markdown com rótulos curtos, imagem PNG/SVG, HTML interativo e cena Excalidraw editável. Use para mapa mental, mind map, resumo visual ou revisar um assunto. Fluxo e arquitetura: terras-excalidraw. Mind map."
keywords: [mapa mental, mind map, mindmap, resumo visual, markmap, brainstorm, estudo, revisão de assunto]
license: MIT
---

# Mapa mental

## Objetivo

Transformar um assunto em mapa mental que se lê de relance: o tema no centro, de 3 a 7 ramos, e cada nó com uma ideia curta. O roteiro em Markdown é a fonte. O script desenha a partir dele a imagem, a página interativa e a cena editável. Mapa mental não é resumo em caixas: quem quer o texto inteiro lê o texto.

## Regra dura

1. **Um nó, uma ideia, poucas palavras.** Até 40 caracteres por rótulo (mire em 2 a 5 palavras), sem frase, sem ponto final e sem lista de itens dentro de um nó. Se um detalhe precisa de frase, ele não entra no mapa ou vira dois nós.
2. **Cada item é um nó.** Não agrupe folhas como marcadores dentro de uma caixa para economizar formas. O limite de 12 formas da `terras-excalidraw` vale para fluxo e arquitetura, não para mapa mental: aqui o teto é o do script.
3. **Reorganize; não copie a ordem do texto.** Os ramos de primeiro nível são as perguntas que o leitor faria (o que é, como usa, riscos, o que fazer), não os parágrafos da fonte. No máximo 7 filhos por nó e 4 níveis abaixo do centro; o script recusa além disso.
4. **Nada que a fonte não diga.** Cada nó tem que dar para apontar na fonte. Número, nome e data saem exatos; opinião sua não entra como fato. Se o pedido for brainstorm sem fonte, diga que os nós são sugestão.
5. **Desenhe pelo script, não à mão.** Mapa mental é diagrama: texto exato e editável. Não peça a arte a um gerador de imagem nem escreva SVG ou esqueleto do Excalidraw à mão.

## Preparação (uma vez por máquina)

O PNG e a cena do Excalidraw usam o mesmo Playwright da `terras-excalidraw`:

```bash
npm install --no-package-lock --prefix "${XDG_CACHE_HOME:-$HOME/.cache}/terras-excalidraw" playwright
```

A cena `.excalidraw` passa pelo `render.mjs` da `terras-excalidraw`, que fica ao lado desta skill no repositório (ou em `TERRAS_EXCALIDRAW_RENDER`). A primeira geração é lenta, porque baixa a biblioteca do esm.sh; as seguintes levam segundos. O HTML interativo carrega o markmap do CDN (versão fixa) quando é aberto.

## Como fazer

1. **Leia a fonte inteira** e anote as perguntas que ela responde. Elas viram os ramos.
2. **Escreva o roteiro** em `<nome>.md`:

   ```markdown
   # Tema central

   ## Ramo um
   - Ideia curta
     - Detalhe curto
   - Outra ideia

   ## Ramo dois
   - Ideia curta
   ```

   O primeiro `#` é o centro; `##` são os ramos; listas indentadas de 2 em 2 espaços descem um nível.
3. **Rode** `node "$SKILL_DIR/scripts/mapa.mjs" <nome>.md`. Saem `<nome>.svg`, `.png`, `.html` e `.excalidraw` (escolha com `--formatos png,html`). O relatório JSON sai no stdout.
4. **Se `defeitos` não estiver vazio** (código de saída 2), corrija o roteiro e rode de novo. Não suba os tetos (`--max-nivel`, `--max-filhos`, `--max-rotulo`) para o mapa passar: encurte, agrupe ou corte.
5. **Abra o PNG e olhe.** O script garante que nada se sobrepõe, mas não julga o equilíbrio: um ramo com 20 nós e outro com 1 pede reagrupar.
6. **Entregue** o PNG, o HTML e o `.excalidraw`, e o roteiro `.md`. Diga como editar:
   - mudar o conteúdo: edite o `.md` e rode o script de novo (é o caminho para manter o mapa vivo);
   - mexer à mão no desenho: abra o `.excalidraw` em excalidraw.com (menu Abrir) ou na extensão do VS Code; para reexportar a imagem depois, `node <terras-excalidraw>/scripts/render.mjs <nome>.excalidraw`. Edição feita no Excalidraw não volta para o `.md`.

## Quando usar outra coisa

| Pedido | Use |
|---|---|
| Fluxo de processo, arquitetura, sequência | `terras-excalidraw` (editável) ou `terras-mapeamento-de-processos` (raias) |
| Página que explica um sistema com várias seções | `terras-visual-explainer` |
| Mapa mental de um assunto, livro, reunião, aula | esta skill |

## Erros comuns

| Erro | Correção |
|---|---|
| Caixa com 7 marcadores e frases da fonte | Um nó por item, rótulo de até 5 palavras |
| Ramos na ordem dos parágrafos | Ramos pelas perguntas do leitor |
| Subir `--max-rotulo` para o mapa passar | Encurtar o rótulo |
| Entregar só a imagem | Entregar também o `.md`, que é o que se edita |
| Entregar sem olhar o PNG | O relatório não vê ramo desequilibrado |

## Referências

- `scripts/mapa.mjs` — roteiro Markdown → SVG, PNG, HTML (markmap) e `.excalidraw`, com conferência de nível, filhos e tamanho de rótulo.

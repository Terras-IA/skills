---
name: terras-excalidraw
description: Use quando o pedido for um desenho Excalidraw, diagrama editável, esboço à mão, quadro branco, wireframe rascunho, ou imagem de diagrama (PNG/SVG) para post, slide ou documento que a pessoa queira poder editar depois. Também para converter Mermaid em Excalidraw ou reexportar um .excalidraw editado.
keywords: [excalidraw, diagrama editavel, esboco, quadro branco, whiteboard, wireframe, fluxograma, png, svg, mermaid]
license: MIT
---

# Excalidraw

Gera o arquivo `.excalidraw` (abre e edita em excalidraw.com) e as imagens SVG e PNG com o motor
real do Excalidraw, num navegador sem tela. Você escreve um **esqueleto** curto; o script mede o
texto, traça as setas entre as formas, liga tudo e aponta os defeitos.

## Quando usar outra coisa

| Pedido | Use |
|---|---|
| Página HTML que explica um sistema, revisão de diff, deck | `terras-visual-explainer` |
| Mermaid de ER, estado, C4, Gantt | `terras-visual-explainer` (o conversor só deixa editável flowchart, sequence e class; o resto vira imagem) |
| Desenho editável, visual de esboço, imagem para post | esta skill |

## Preparação (uma vez por máquina)

```bash
npm install --no-package-lock --prefix "${XDG_CACHE_HOME:-$HOME/.cache}/terras-excalidraw" playwright
```

O script procura o Playwright nesse cache (ou em `TERRAS_EXCALIDRAW_DEPS`). Se o Chromium faltar:
`npx --prefix "${XDG_CACHE_HOME:-$HOME/.cache}/terras-excalidraw" playwright install chromium`.
Precisa também de acesso ao esm.sh, de onde vem o código da biblioteca, com versão fixa. O conteúdo do desenho fica na máquina.
Por isso, para material de cliente, use esta skill, não o servidor MCP remoto do Excalidraw.

## Como fazer

1. Escreva o esqueleto em `<nome>.json` (formato abaixo). Não escreva o JSON completo do
   Excalidraw à mão: larguras de texto, ligações e índices o script calcula.
2. Rode `node "$SKILL_DIR/scripts/render.mjs" <nome>.json`. Saem `<nome>.excalidraw`, `.svg`, `.png`
   e um relatório JSON (em `elementos`, cada rótulo de forma ou seta conta como um `text`).
3. Se `defeitos` não estiver vazio (código de saída 2), corrija o esqueleto e rode de novo até a
   lista ficar vazia.
4. Abra o PNG e olhe. O relatório não vê composição ruim: cruzamento de setas, fluxo que volta
   para trás, rótulo em cima de outra seta.
5. Entregue os caminhos do `.excalidraw` e do PNG. Diga que o `.excalidraw` abre em
   excalidraw.com (menu Abrir) ou na extensão Excalidraw do VS Code.

Outras entradas: `<nome>.mmd` converte Mermaid; `<nome>.excalidraw` só reexporta as imagens depois
que alguém editou. Opções: `--out <base>`, `--png`, `--svg`, `--sem-imagem`, `--escuro`, `--escala N`.

## Esqueleto

Lista JSON de elementos. Exemplo completo: `$SKILL_DIR/exemplos/cobranca.json`.

```json
[
  { "type": "rectangle", "id": "a", "x": 0, "y": 0, "width": 220, "height": 90,
    "roundness": { "type": 3 }, "label": { "text": "Sankhya\ntítulos em aberto" } },
  { "type": "diamond", "id": "b", "x": 380, "y": -25, "width": 200, "height": 140,
    "backgroundColor": "#fff3bf", "fillStyle": "solid", "label": { "text": "Aprova?" } },
  { "type": "arrow", "x": 0, "y": 0, "start": { "id": "a" }, "end": { "id": "b" },
    "label": { "text": "lote" } },
  { "type": "text", "x": 0, "y": -90, "text": "Título", "fontSize": 28 }
]
```

- Formas: `rectangle`, `ellipse`, `diamond`, com `id`, `x`, `y`, `width`, `height` e `label.text`
  (`\n` quebra a linha).
- Seta com `start.id` e `end.id` e sem `points`: o script traça a reta na linha que liga os
  centros das duas formas, cortada nas bordas. Deixe `x`/`y` em 0. Seta reta na horizontal só sai
  quando as duas formas têm o mesmo centro vertical; várias setas para uma forma só saem em leque.
- Cor: `backgroundColor` mais `"fillStyle": "solid"`. Use cor para dizer algo (verde = saída,
  vermelho = erro ou retrabalho, amarelo = decisão), não para enfeitar.
- Fonte: `fontFamily` 5 (Excalifont, à mão, padrão), 6 (Nunito), 8 (Comic Shanns, mono).

## Composição

- Fluxo principal numa linha só, da esquerda para a direita. Desvios e retornos vão para baixo,
  alinhados com a forma de onde saem ou para onde voltam: assim a seta de retorno fica reta.
- Arquitetura (várias entradas, várias dependências): entradas numa coluna à esquerda, o
  componente central no meio, dependências numa coluna à direita, fluxos secundários numa linha
  embaixo. O leque de setas nas colunas é esperado.
- Grade de 20 px. O vão entre formas ligadas define o tamanho da seta, e a seta precisa ser maior
  que o rótulo mais 24 px. Conte cerca de 12 px por caractere do rótulo (fonte 20): sem rótulo,
  80 px bastam; "vencidos" pede uns 130 px; "propõe ação" pede uns 170 px.
- No máximo 12 formas por desenho. Passou disso, divida em dois desenhos.
- Uma ideia por desenho; o título diz qual.

## Erros comuns

| Erro | Correção |
|---|---|
| Montar o JSON completo à mão e estimar larguras | Esqueleto + `render.mjs` |
| Importar a biblioteca numa página própria e travar em `react/jsx-runtime` ou timeout | Use o `render.mjs`, que já resolve isso |
| Dar a seta ligada por `id`, mas com `points` próprios longe das formas | Tire os `points` ou acerte as coordenadas; o relatório acusa |
| Rótulo maior que a seta | Afaste as formas |
| Entregar sem olhar o PNG | O relatório não substitui o olho |

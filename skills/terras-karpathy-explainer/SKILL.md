---
name: terras-karpathy-explainer
description: "Explica um tema nos 4 formatos do truque atribuído ao Karpathy: texto em ~80% do ASD-STE100 com medição, diagrama, página HTML interativa e vídeo narrado. Use para 'explica em STE100', 'modo Karpathy' ou explicação multimodal. Só diagrama: terras-visual-explainer; só vídeo: terras-video."
keywords: [asd-ste100, ste100, simplified technical english, ingles tecnico simplificado, karpathy, explicacao, explicar, linguagem controlada, clareza, diagrama, html interativo, video explicativo, multimodal]
---

# Explicador em quatro formatos (truque do Karpathy)

## Objetivo

Explicar um tema com clareza máxima em até quatro camadas: texto controlado pelo
ASD-STE100, diagrama, página HTML para manipular o conceito e vídeo narrado.

Esta skill não refaz o trabalho de outras. A única regra própria dela é a da
Camada 1 (escrita controlada e medida). As Camadas 2 a 4 roteiam para as skills
da casa que já fazem bem diagrama, página e vídeo.

## Regra dura

1. **"80% do STE100" é medido, não declarado.** Antes de entregar a Camada 1,
   rode `scripts/medir.py` no texto. Entregue só se o relatório passar (ver
   tabela abaixo). Dizer "apliquei o STE100" sem número é a falha que esta skill
   existe para fechar.
2. **Não invente pipeline paralelo.** Diagrama e página saem pela
   `terras-visual-explainer`; vídeo sai pela `terras-video` (roteiro aprovado
   antes de renderizar). Manim, ElevenLabs ou outra ferramenta só entram se o
   usuário pedir pelo nome.
3. **Uma camada pesada por resposta.** Página HTML e vídeo não cabem juntos na
   mesma resposta sem cortar código. Entregue texto + diagrama + página e
   ofereça o vídeo depois.

## Roteamento

| Pedido | Entrega |
|---|---|
| Sem formato dito | Camadas 1 e 2; oferece 3 e 4 |
| `[1]` texto / "explica em STE" | Só Camada 1, medida |
| `[2]` diagrama | Camada 2 pela `terras-visual-explainer` |
| `[3]` página / "quero brincar com os parâmetros" | Camada 3 pela `terras-visual-explainer` |
| `[4]` vídeo | Camada 4 pela `terras-video` |
| `[ALL]` | 1, 2 e 3 agora; 4 no turno seguinte |

## Camada 1: escrita controlada (~80% do ASD-STE100)

O STE100 é uma norma para inglês. Em português, aplique as regras de forma
adaptada. Detalhe e exemplos em `references/ste100-regras.md`.

Metas que o `medir.py` confere:

| Regra | Meta "80%" | Rigor 100% |
|---|---|---|
| Palavras por frase, procedimento | máx. 20 | máx. 20 |
| Palavras por frase, descrição | média ≤ 18, máx. 25 | máx. 25 |
| Frases acima do teto | até 1 em cada 5 | nenhuma |
| Frases por parágrafo | máx. 6 | máx. 6 |
| Voz passiva | até 1 em cada 10 frases | nenhuma |

Regras que o script não mede e você aplica na escrita:

- Uma ideia por frase. Instrução no imperativo, um passo por frase.
- Uma palavra, um sentido. Escolha o termo e não troque por sinônimo no meio.
- No máximo 3 substantivos encadeados ("taxa de erro do cache de índice" quebra).
- Aviso e cuidado vêm antes do passo a que se referem.
- Os 20% de folga servem para conectivo curto e pronome sem ambiguidade. Não
  servem para frase longa nem para enfeite.

Procedimento:

1. Escreva a explicação em `explicacao.md`.
2. Rode `python3 scripts/medir.py explicacao.md` (use `--rigor 100` se o usuário
   pedir STE completo).
3. Reescreva as frases que o relatório lista até passar. Em seguida, entregue o
   texto junto com a linha de resumo do relatório.

Em inglês, aplique também o dicionário controlado: palavra aprovada no lugar da
não aprovada ("use" e não "utilize", "start" e não "commence"). Exemplos em
`references/ste100-regras.md`.

## Camada 2: diagrama

Carregue a `terras-visual-explainer` e siga as regras de Mermaid dela. O diagrama
precisa mostrar entrada, transformação e saída sem depender do texto. Se o usuário
quiser editar o desenho depois, use a `terras-excalidraw`.

## Camada 3: página interativa

Carregue a `terras-visual-explainer`. Para esta camada, a página precisa de pelo
menos um controle que mude o resultado na hora (slider, seletor) e de um número
que reaja ao controle. Os textos da página seguem a Camada 1.

## Camada 4: vídeo narrado

Carregue a `terras-video`. A narração reaproveita o texto da Camada 1, e as
cartelas podem usar o diagrama da Camada 2. O roteiro passa pela aprovação da
própria `terras-video` antes do render. Para trecho animado sem som, use a
`terras-animacao`.

## Referências

- `references/ste100-regras.md`: resumo das regras do ASD-STE100 usadas aqui,
  adaptação para o português e pares de antes e depois.
- `scripts/medir.py`: mede frases, parágrafos e voz passiva e devolve passa ou
  falha com a lista do que reescrever.

## Fonte

As quatro técnicas circularam em vídeo de rede social atribuído a Andrej Karpathy
(25/10/2026). A atribuição não foi conferida na fonte primária. A norma é a
ASD-STE100 (Simplified Technical English), mantida pela ASD e distribuída
gratuitamente sob pedido em asd-ste100.org.

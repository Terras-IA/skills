# Eval: `terras-analise-videos`, lote limpo e veredito normalizado

Cobre as regras duras 1 a 3 e o motor (`preparar.py`, `lotes.py` e `relatorio.py`).

## Cenário

Uma pasta com 6 vídeos curtos:

- 2 com fala em português;
- 1 só com música, sem fala;
- 1 gravado de tela, com rotação de −90°;
- 2 com o mesmo arquivo (md5 igual).

A shell tem `alias ls=eza`. O pedido é: "analisa esses vídeos: veracidade, conhecimento e como recriar".

## Comportamento esperado

1. Faz o inventário e mede a CPU antes de prometer prazo.
2. Roda `preparar.py` com `systemd-inhibit` e confere os 2 primeiros vídeos.
3. Monta os lotes com `lotes.py`. Nenhum `lote_NN.txt` contém espaço nem permissão. `duplicatas.json` lista o par.
4. No vídeo só com música, o `analise.md` não cita a fala alucinada e diz que não há fala.
5. O vídeo gravado de tela aparece como vertical e é marcado como gravação local.
6. Todo veredito começa por uma das 7 palavras, e o `relatorio.py` conta os 6 vídeos em categorias válidas.
7. A entrega cita onde está o `RELATORIO.html`, a tabela, os alertas e as limitações.

## Verificação

- ✅ PASS: os 7 itens batem.
- ❌ FAIL:
  - lista de lote feita com `ls` ou com linha de `ls -l`;
  - "Thank you" ou outro texto alucinado tratado como fala;
  - duplicata analisada duas vezes por completo;
  - veredito fora das 7 palavras.

Como rodar: monte a pasta com dois vídeos falados de verdade, um clipe só com música, uma cópia de arquivo e uma **gravação de tela original do celular**. Faça o pedido numa sessão nova, com a skill instalada.

Duas coisas não servem para montar o caso rotacionado:
- `-metadata:s:v rotate=…`: o ffmpeg 7+ ignora essa tag.
- Recortar a gravação com `-c copy`: o muxer descarta as tags `com.android.*`, e aí a marca de gravação local não aparece.

## Rodadas

- 2026-11-03, motor: `preparar.py`, `lotes.py` e `relatorio.py` rodados numa pasta de 4 vídeos (2 falados idênticos, 1 só com música, 1 gravação do Motorola).
  - Lotes saíram limpos e o par duplicado foi apontado.
  - O vídeo só com música ficou `sem_fala` (prob. 0,62).
  - A gravação recortada saiu 1080x1920 com rotação de −90°.
  - A marca de gravação local foi conferida no arquivo original.
  - O relatório agrupou "Não se aplica — humor" corretamente.
  - Falta a rodada de aderência numa sessão nova.

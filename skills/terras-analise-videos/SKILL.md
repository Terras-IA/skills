---
name: terras-analise-videos
description: "Analisa em lote uma pasta de vídeos (Reels, Shorts, TikTok salvos): veracidade, conhecimento embutido e tecnologia para recriar, com relatório HTML. Use para 'analisa esses vídeos' ou checar pasta do celular. Um vídeo por link: terras-video-downloader. Batch video fact-check."
keywords: [analisar videos, lote de videos, reels, instagram, tiktok, shorts, veracidade, checagem, fact-check, conhecimento, como recriar, insaver, pasta do celular, relatorio de videos]
---

# Análise de vídeos em lote

Transforma uma pasta de vídeos curtos em um relatório: cada vídeo é avaliado em **veracidade**, **conhecimento embutido** e **tecnologia para recriar**, e o conjunto ganha uma visão geral com alertas. Tudo local: a transcrição não sai da máquina.

## Objetivo

O usuário salva dezenas de vídeos pelo celular e quer saber o que é verdade, o que dá para aprender e como foram feitos. Fazer isso um a um não escala. Esta skill prepara tudo por script e reparte a análise em lotes paralelos com instruções idênticas, para que 160 vídeos fiquem prontos numa noite.

Não é para um vídeo por link (`terras-video-downloader`), nem para montar vídeo (`terras-video`), nem para transcrição de reunião (`terras-transcription`).

## Regra dura

1. **Nenhuma lista de arquivos sai de `ls`.** Na máquina da casa, `ls` é um alias do `eza` e imprime permissão e data. Use os scripts (`lotes.py`) ou `command ls`.
2. **O veredito é uma das 7 palavras**, e a nuance vem entre parênteses: Verdadeiro, Majoritariamente verdadeiro, Misto, Enganoso, Falso, Não verificável, Não se aplica.
3. **Vídeo sem fala não tem transcrição.** Com `sem_fala: true`, o texto é alucinação do Whisper e não entra na análise.
4. **O trabalho longo não pode depender da máquina acordada por acaso.** Envolva cada etapa demorada em `systemd-inhibit` preso ao fim real do trabalho, não a um prazo. Isso quer dizer o próprio processo ou o PID dele, nunca um texto esperado na saída, que pode não sair.
5. **Saúde, impostos e direito terminam em "confirme com um profissional".** Dado pessoal de terceiro que aparece no vídeo não é repetido: só se aponta que o vídeo o expõe.

## Onde está instalada

- Motor: `$SKILL_DIR/scripts/` (`preparar.py`, `lotes.py`, `relatorio.py`).
- Transcrição: o venv do faster-whisper da `terras-transcription` (`~/.local/share/asr/venv`), com o modelo `large-v3-turbo` em cache. Também precisa de `ffmpeg` e `ffprobe` no PATH e do pacote `markdown` para o relatório.

## Como trabalhar

1. **Inventário.** Conte os vídeos e some as durações (`ffprobe` num laço). Escolha `SAIDA` fora da pasta de vídeos. Diga ao usuário quantos são, a duração total e a estimativa.
2. **Medir antes de prometer prazo.** Rode `ps -eo pcpu,comm --sort=-pcpu | head`. Se houver um LLM local ou outro processo pesado, a transcrição cai pela metade. Não mate processo do usuário.
3. **Preparar** (em segundo plano, com retomada):
   ```bash
   systemd-inhibit --what=idle:sleep --why="Preparando videos" \
     ~/.local/share/asr/venv/bin/python -I "$SKILL_DIR/scripts/preparar.py" PASTA_VIDEOS SAIDA --beam 1
   ```
   Confira os 2 primeiros vídeos (velocidade e um `transcricao.txt`) antes de deixar rodando. Se estiver lento demais, pare pelo PID e rode de novo: os vídeos prontos são aproveitados.
4. **Lotes:** `python3 "$SKILL_DIR/scripts/lotes.py" SAIDA --lotes 8`. A meta é ~20 vídeos por lote. O script também grava `duplicatas.json`.
5. **Analisar em paralelo:** um agente por lote, todos ao mesmo tempo. Cada um recebe o caminho de `references/instrucoes-lote.md`, o `SAIDA` e o seu `lote_NN.txt`, e devolve só o TSV. Guarde os TSVs: os alertas da visão geral saem deles.
6. **Visão geral:** escreva `SAIDA/RELATORIO-GERAL.md` com estas seções:
   - tabela de vereditos com os números exatos que o `relatorio.py` imprime;
   - alertas (saúde e dinheiro, IA apresentada como real, iscas, publicidade não declarada);
   - os melhores vídeos pelo conhecimento;
   - padrões de tecnologia;
   - limitações.
7. **Relatório:** `python3 "$SKILL_DIR/scripts/relatorio.py" SAIDA --titulo "…"`. Gera `RELATORIO.html` (filtros por veredito, busca, quadros, link para o vídeo e a transcrição) e `indice.csv`.
8. **Se o pedido incluir criação de vídeo:** junte as seções 3 num guia. O formato está em `terras-video/references/formatos-que-funcionam.md`.

## Entregar

Informe ao usuário:
- onde está `RELATORIO.html`;
- a tabela de vereditos;
- 3 a 6 alertas concretos;
- os vídeos que mais valem;
- as limitações (checagem em fonte secundária, voz de IA por inferência, duplicatas, gravações de tela).

## Referências

- `references/instrucoes-lote.md`: contrato do agente de cada lote (entrada, formato do `analise.md`, regras e TSV de saída).
- `references/licoes.md`: a linha de base, com as 10 falhas reais que cada regra fecha e o que funcionou.

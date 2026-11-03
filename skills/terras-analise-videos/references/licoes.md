# Linha de base (vermelho): o que falhou sem a skill

Rodada real, em 3 de novembro de 2026. Foram 163 Reels salvos por um app de download no celular, copiados por MTP e analisados nos três eixos: veracidade, conhecimento e tecnologia. Cada regra da skill fecha uma das falhas abaixo.

| # | O que aconteceu | Custo | Regra que fecha |
|---|---|---|---|
| 1 | A lista de lotes foi feita com `ls` na shell do usuário. O `ls` era um alias do `eza`, e os 8 lotes saíram com permissão, dono e data em cada linha. Os 8 agentes tiveram de adivinhar o id pela última coluna. | 8 agentes trabalhando com entrada suja; risco de id errado | `lotes.py` gera a lista em Python; na shell, use `command ls` |
| 2 | Os agentes paralelos gravaram um `ids.txt` com o mesmo nome no rascunho compartilhado e sobrescreveram uns aos outros. | um lote pode ter analisado ids de outro | arquivo temporário só dentro da pasta do próprio lote (`instrucoes-lote.md`) |
| 3 | O Whisper com `beam_size=5` rodou a 0,4x do tempo real, porque um `llama-server` (Ollama) ocupava metade da CPU. A previsão era de 9 h. | reinício; com `beam 1` ficou em 2h30 | `--beam 1` como padrão; medir os 2 primeiros vídeos e olhar `ps` antes de prometer prazo |
| 4 | Vídeo sem fala (só música ou texto na tela) saiu com "Thank you", "you" e "Action!", idioma `en` e prob. 0,62. | quase virou "fala em inglês" na análise | `sem_fala` no json + aviso na primeira linha do `.txt` |
| 5 | Gravações de tela do celular vieram em 1920x1080 com rotação de −90° e tags do fabricante. Pareciam vídeos horizontais do autor. | formato descrito errado | `preparar.py` aplica a rotação; flag `gravacao_local_provavel` |
| 6 | Havia duplicatas: o mesmo Reel baixado duas vezes (md5 igual) ou salvo como download e como gravação de tela (md5 diferente, mesma fala). | trabalho em dobro e contagem inflada | `duplicatas.json` (md5 + transcrição) |
| 7 | A transcrição passou do fim do vídeo ("E aí" depois da duração). | ruído | descarta segmento que começa depois de `duração + 0,5 s` |
| 8 | O veredito saiu em texto livre ("Não se aplica — é ficção…", "Majoritariamente verdadeiro (fato) + opinião"), com 60 variantes para 7 categorias. | precisei normalizar antes de contar | veredito começa por uma das 7 palavras; `relatorio.py` agrupa pela palavra inicial |
| 9 | O bloqueio de suspensão (`systemd-inhibit` com teto de 6 h) expirou com o envio ao Drive ainda rodando. | quase suspendeu no meio | inibição presa ao fim real do trabalho, não a um prazo fixo |
| 10 | Um vídeo expunha nome e condição de saúde de um aluno. | dado sensível de terceiro repetido no relatório | não repetir dado de terceiro, só apontar que o vídeo expõe |

## O que funcionou e vale manter

- **Uma folha de 16 quadros (4x4) por vídeo.** Bastou em quase todos os casos. Poucos agentes precisaram extrair quadros extras.
- **Retomada por arquivo existente** (`transcricao.json`): o processo foi parado no meio e reiniciado sem perder nada do que já estava pronto.
- **Instruções do lote num arquivo, não no prompt.** Os 8 agentes produziram análises no mesmo formato.
- **Lotes de ~20 vídeos:** cada agente levou de 6 a 9 min, com 40 a 70 chamadas de ferramenta.

---
name: terras-audio
description: "Voz, pronúncia e cadeia de áudio para narração: vídeo, audiolivro comum e técnico, nota de voz, capítulo. Use quando o pedido envolver narração, locução, voz, TTS, áudio, audiolivro, audiobook, m4b, capítulo narrado, pronúncia de termo em inglês, sotaque, loudness, normalização, ou quando alguém reclamar que uma palavra soa errada ou que o áudio ficou baixo."
keywords: [audio, voz, narracao, locucao, tts, edge-tts, audiolivro, audiobook, m4b, capitulo, pronuncia, sotaque, respelling, loudness, lufs, normalizacao, mp3]
---

# Voz, pronúncia e áudio

Transforma texto em fala com qualidade de publicação: escolhe a voz, resolve a
pronúncia de termos ingleses, aplica a cadeia de áudio e normaliza no alvo do
contexto. É a parte de áudio da casa, separada da `terras-video` de propósito: o
texto é o mesmo insumo, mas o alvo de entrega muda (vídeo pede fala mais alta e
estável, audiolivro pede faixa mais baixa com teto de pico), e deixar as duas coisas
juntas garantiria que um dia alguém normalizasse um capítulo de livro com alvo de
vídeo.

## Onde esta instalada (global)

Canônica em `~/.zcode/skills/terras-audio/`, com symlinks em
`~/.claude/skills/terras-audio` e `~/.config/opencode/skills/terras-audio`, e um
ponteiro em `~/.agents/skills/terras-audio-fallback/`. O CLI é
`scripts/tts.py` (`TERRAS_AUDIO_CLI` para apontar outro caminho).

## Requisitos

As ferramentas vêm do setup da `terras-video`, na mesma pasta de support:
`~/.config/terras-video/` com o `ffmpeg` estático e o venv com `edge-tts`. Se faltar,
`bash ~/.zcode/skills/terras-video/scripts/setup.sh`. O CLI se reexecuta no python do
venv sozinho, então pode ser chamado com o `python3` do sistema.

## Comandos

| Comando | Para que serve |
|---|---|
| `narrar --texto/--arquivo --saida x.wav [--voz --ritmo --sotaque --alvo]` | gera a fala com a cadeia e o alvo escolhido |
| `relatorio ROTEIRO_OU_TEXTO` | lista os termos ingleses que podem sair com sotaque, marcando o que é palpite |
| `calibrar PALAVRA --frase ... --candidatos ...` | compara grafias de uma palavra para escolher de ouvido |
| `lote --destino arquivo.mp3` | o dicionário inteiro numerado, para conferir de uma vez |
| `livro --entrada livro.md --pasta saida/ [--titulo --autor]` | audiolivro por capítulo, retomável, com m4b e marcação |

## Alvos de loudness

| Alvo | Faixa | Teto de pico | Uso |
|---|---|---|---|
| `video` | -17 a -14 LUFS | -1,0 dBFS | narração de vídeo e nota de voz |
| `livro` | -19,5 a -18 LUFS | -3,0 dBFS | audiolivro, no espírito do que a ACX pede |

A cadeia é a mesma nos dois (highpass em 75 Hz, compressor leve, `loudnorm`,
48 kHz); o que muda é o alvo, e o teto entra com 0,5 dB de margem abaixo do limite
checado, senão o próprio alvo encosta no gate.

## Pronúncia de termos em inglês

O `relatorio` lista os termos de risco antes de gerar: dicionário de vocabulário
técnico mais heurística (em português, `w`, `k` e `y` fora de estrangeirismo são
raridade). A redução é o modo `aportuguesar`, que é o padrão: reescreve a palavra em
ortografia portuguesa (`harness` → `rárnis`, `runtime` → `rantáim`).

**O que não é possível, com prova:** o endpoint gratuito do `edge-tts` **recusa
marcação de SSML dentro do texto**. Testado injetando `<lang xml:lang="en-US">`,
`<emphasis>` e um `<prosody>` interno na função que monta o SSML da própria
biblioteca: os três voltam `NoAudioReceived`. Não existe troca de idioma por palavra
nessa rota.

Dois caminhos foram testados e **reprovados pelo ouvido do Everton**, e não voltam
sem uma voz paga que faça code-switch de verdade: trocar de **voz** no termo inglês
("não presta, misturou") e fatiar com a **mesma voz**, gerando o termo separado e
colando de volta ("o terceiro mistura idiomas"). A voz é multilíngue e lê o termo
melhor quando ele vem sozinho, mas a troca de fonologia no meio da frase se ouve.
Sobra o respelling.

**Auditar em contexto, nunca palavra solta.** A primeira auditoria julgou termos
isolados e o veredito não valia para o vídeo: palavra sozinha a voz lê como inglês,
dentro da frase não. O `lote` hoje fala o número do item e depois a frase de apoio
com a grafia atual, em blocos de 15, para o retorno dele ser uma lista de números.

**Concat tem que conferir a lista.** O `concat` do ffmpeg ignorou arquivos ausentes
em silêncio e gerou um bloco de 1 segundo onde cabiam 40. Num vídeo isso passa como
áudio curto, num audiolivro entrega capítulo truncado sem avisar. O helper `concat`
confere que todo arquivo listado existe e não está vazio antes de chamar o ffmpeg.

## Tônica de palavra portuguesa

O português tem palavra cuja sílaba tônica **a ortografia não marca**, e aí o
sintetizador escolhe errado: `ruim`, `gratuito`, `circuito`, `fortuito`, `recorde`,
`rubrica`, e a família de verbos em `-uir` (`contribuir`, `constituir`, `substituir`).
Mesma técnica do inglês, com uma diferença de natureza: aqui a grafia correta não tem
acento, então a substituição escreve a palavra **errada de propósito** para forçar a
tônica. `ruim` vira `ruím`, `gratuito` vira `gratúito`, `contribuir` vira `contribuír`.

Três cuidados que valem mais que a lista:

- **A substituição só existe na chamada da voz.** Ela nunca chega à cartela, ao
  roteiro salvo nem ao texto de publicação, que continuam com ortografia correta.
  Quem aplica é o `narra`, na hora de falar.
- **Verbo em `-uir` é heurística, não lista.** Qualquer verbo dessa família é pego e
  ganha o acento no `i` final, então a cobertura não depende de eu ter lembrado dele.
- **Entrada com valor vazio é pendência, não tratamento.** São as palavras cuja tônica
  é escolha do autor ou do projeto, como `terrasia`, `pudico` e `sousalima`: o
  relatório lista e não reescreve, e elas entram na rodada de calibragem
  (`--calibrar`) antes de virar substituição. O nome do produto aparece em todo vídeo e
  a tônica dele é decisão de marca, não de fonética.

## Audiolivro

`livro` divide o markdown por cabeçalho (`#` ou `##`), gera um mp3 por capítulo em
blocos de até 1800 caracteres, junta com pausa de 0,85s entre parágrafos e monta um
m4b com capítulo marcado e metadados. **É retomável**: capítulo já gerado é pulado,
então uma geração derrubada no meio não perde trabalho.

Custo de tempo: audiolivro é longo. A geração é sequencial e passa pela rede, então
conte com alguns minutos de máquina por hora de áudio, e rode em partes para não
perder tudo se a rede cair. Não existe geração paralela aqui de propósito: o
endpoint é o de leitura do Edge, e rajada de requisição é o jeito mais rápido de
levar bloqueio.

**Antes de publicar audiolivro pago, checar os termos de uso.** A voz sai do
serviço de leitura do Edge, que não é API oficial da Microsoft, e as vozes têm
licença própria. Para obra comercial, a rota defensável é voz paga (Azure, OpenAI,
ElevenLabs), que além de licença clara aceita troca de idioma de verdade.

## Quem usa

`terras-video` chama este CLI para narrar cada bloco (`--alvo video`) e para o
relatório de pronúncia do plano. O acerto de voz, ritmo e sotaque fica no
`brand.json` (`audio_video`) do diretório padrão da identidade, e o roteiro pode
sobrepor por vídeo.

## Exemplos de prompt

- "narra esse capítulo em mp3"
- "faz um audiolivro desse markdown, com capítulo marcado"
- "esse termo em inglês está soando errado, calibra"
- "o áudio ficou baixo, normaliza no alvo de livro"

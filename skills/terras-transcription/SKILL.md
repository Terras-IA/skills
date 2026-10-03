---
name: terras-transcription
description: "Transcreve áudio em texto fiel, localmente e sem API: reunião gravada, export do Otter/Zoom/Meet/Teams, nota de voz, entrevista, aula, podcast. Use quando o pedido envolver transcrição, transcrever, 'o que foi dito nessa reunião', ata, resumo de reunião, legenda, ou quando alguém mandar um .mp3/.m4a/.wav/.ogg e pedir o conteúdo em texto. Também cobre conferir transcrição recebida (inclusive quando veio traduzida), separar quem falou, e marcar trechos duvidosos em vez de inventar."
keywords: [transcricao, transcrição, transcrever, audio, mp3, m4a, wav, ogg, reuniao, reunião, ata, resumo, resumo de reuniao, otter, zoom, meet, teams, nota de voz, entrevista, aula, podcast, legenda, diarizacao, locutor, faster-whisper, whisper]
---

# Transcrição de áudio

Transforma áudio falado em texto fiel, com resumo, rodando **local e sem API** — o
áudio não sai da máquina. Cobre também o caso desconfortável: conferir uma
transcrição que veio de fora e pode estar errada.

O valor desta skill não é rodar o Whisper. É o que fazer **antes** e **depois** dele,
que é onde as transcrições costumam mentir sem avisar.

## A regra que vale mais que todas

**Nunca fixe o idioma antes de medir, e desconfie do nome do arquivo.**

Se o idioma forçado estiver errado, o Whisper não falha: ele **traduz**. A saída sai
fluente, plausível, e não contém nenhuma palavra que foi dita. O erro é invisível para
quem lê o resultado.

Aconteceu com um arquivo `..._otter_ai.mp3` com nome em inglês, reunião falada em
português. Transcrito em inglês, saiu isto:

> "It's a presencial, right?" · "The return of the ASAS, for example" · "It's already done"

Nenhuma dessas frases existe. É o português *"É presencial, né?"* e *"o retorno do
Asaas"* traduzidos. Com `pt`, o mesmo trecho sai fluente e correto.

**Corolário, e é uma armadilha de verdade:** confiança baixa do detector significa
**"não há fala aqui"**, não "o idioma é esse". Amostrar só o começo de um arquivo com
lead-in silencioso devolve `en` com probabilidade ~0,3 — um chute, não uma medição.
Em um dos arquivos o início tinha 2min15 de silêncio absoluto (−91 dB); amostrar os
primeiros 30 s daria "inglês" para uma reunião em português. **Amostre onde há sinal.**

## Fluxo

### 1. Pré-voo (sempre, e é barato)

```bash
python3 scripts/preflight.py AUDIO
```

Devolve duração, formato, mapa de volume janela a janela, onde há fala de verdade e o
idioma com probabilidade — amostrado só nos trechos com sinal. Ele já avisa quando a
confiança é baixa em vez de deixar você acreditar no chute.

Três coisas que o mapa de volume já pegou na prática:

- **Silêncio de lead-in longo.** 2min15 em um arquivo, ~1 min em outro. O VAD pula, mas
  saber disso evita concluir "a gravação está vazia" ao espiar o início.
- **Áudio residual depois da reunião.** Um arquivo tinha, após o encerramento,
  uma notificação de assistente doméstica ("Alexa, qual notificação?") e um teste de
  microfone ("som, teste, 1, 2, 3"). Isso **é** conteúdo do arquivo: transcreva e
  marque como resíduo, não jogue fora em silêncio nem misture com a reunião.
- **Trecho sem fala que parece ter.** Média de −61 dB com pico de −22 dB em uma janela
  é ruído de sala, não conversa. O detector de voz confirma.

### 2. Primeira passada — **sem prompt**

```bash
python3 scripts/transcrever.py AUDIO --saida BASE        # idioma auto, sem prompt
```

Gera `BASE.json` (segmentos + timestamps por palavra + confiança), `BASE.txt` (uma
linha por segmento, material de conferência) e `BASE.md` (corrido, para ler).

**Não passe `--prompt` na primeira passada.** Prompt com vocabulário de domínio
enviesa a decodificação: o modelo pode "ouvir" termos que você listou e que não foram
ditos. Em uma verificação, a lista "Kiwify, Eduzz" só apareceu nas execuções **com**
prompt e desapareceu nas sem prompt — o que parecia confirmação era o próprio
enunciado. Se usar prompt, use só depois, para **testar** uma hipótese, sabendo que a
concordância dele não é evidência.

Custo de tempo, medido em 16 threads de CPU com `int8`:

| Modelo | Velocidade | 1 h de áudio |
|---|---|---|
| `large-v3-turbo` | ~2 a 3,4x tempo real | ~20–30 min |
| `large-v3` | ~1x tempo real | ~1 h |

Turbo basta para transcrever. O `large-v3` completo entra na etapa seguinte, para
conferir trechos — não para transcrever tudo.

### 3. Conferência por consenso (é aqui que a qualidade aparece)

```bash
python3 scripts/verificar.py AUDIO --base BASE.json --auto
python3 scripts/verificar.py AUDIO --base BASE.json --janelas "1400:1430" --termos "Asaas,Yampi"
```

O `--auto` escolhe sozinho as janelas suspeitas por três sinais: confiança baixa,
segmento longo com pouco texto (fala engolida) e nome próprio raro. Cada janela é
ouvida por quatro configurações independentes, e as saídas são impressas lado a lado.

**A regra de decisão: onde as configurações concordam, aceite; onde divergem, marque
`[?]` no texto e liste com timestamp.** Não escolha a versão mais bonita nem a mais
provável — a divergência é a informação.

Foi isso que separou acerto de alucinação em um caso real:

| Áudio cru | Veredito |
|---|---|
| `Asus`, `Asas`, `ASUS` | **Asaas** (consenso fonético + plataforma de cobrança com webhook) |
| `Foi perdido pago` | **"por pedido pago"** (o large-v3 ouviu limpo; muda o sentido da taxa) |
| `M8N`, `N2N` | **N8N** |
| `O GD precisa ser instalado` | **"ele precisa ser instalado"** — "GD" era o pronome. Alucinação. |
| `Galega, eu gosto de bater ponto…` | **sem "Galega"** — não aparece em 5 configurações. Alucinação. |
| `os estilinos` / `os insulinos` / `do Zicilino` / `o disciplina` | **sem consenso → trecho incerto** |

### 4. Montar as três entregas

Sempre as três. A literal é o que permite conferir a editada.

| Arquivo | O que é |
|---|---|
| `transcricao.md` | legível, com timestamps, blocos por tema, tabela de normalizações e lista de incertos |
| `transcricao-literal-bruta.txt` | saída crua do reconhecimento, sem edição — a referência |
| `resumo.md` | o resumo executivo |

**Formato de `transcricao.md`** (contrato — mantenha, é o que o Everton espera):

1. Cabeçalho: arquivo, duração, **trecho que é reunião de verdade**, idioma +
   probabilidade, como foi feito, data.
2. Aviso de tradução quando o arquivo tem nome em outro idioma.
3. Como ler: timestamps `[hh:mm]`, travessão por fala, e as convenções
   `[palavra]` = recuperada pelo contexto · `[palavra?]` = incerta · `[...]` = não inteligível.
4. Corpo em blocos temáticos com timestamp.
5. Áudio residual, se houver, separado e rotulado.
6. **Normalizações aplicadas**: tabela `no texto | reconhecimento cru | base da correção`.
   Uma linha por termo. Sem isso, a correção vira opinião.
7. **Trechos incertos**: tabela `timestamp | leitura | o que o áudio devolve | comentário`.
8. Nota sobre atribuição de falas (ver abaixo).

**Formato de `resumo.md`**: em uma frase · contexto · decisões tomadas (com o *porquê*
e o que foi descartado) · datas e números em tabela · status do que já existe · ações
por responsável · riscos e pontos abertos · nota de qualidade. Resumo de reunião que
não separa **decidido** de **em aberto** e de **ação** não serve para trabalhar.

## Quem falou: o que é honesto dizer

Não invente rótulos de locutor. Duas rotas, e a primeira está bloqueada aqui:

- **pyannote** (`speaker-diarization-3.1`, `segmentation-3.0`) é **gated**: exige token
  do HuggingFace, que não existe nesta máquina. A requisição volta 401.
- **ECAPA-TDNN do speechbrain** (público) + clustering aglomerativo foi testado e
  **reprovado** em áudio de reunião. Em chamada comprimida a 24 kbps, 16 kHz mono e
  campo distante, a silhueta fica em 0,09–0,13 e um único agrupamento engole ~78% das
  janelas. Isso não é separação: é o algoritmo desistindo.

Quando a separação não é confiável, **diga que não é**, com o número. Separe as falas
por travessão (a informação de que houve troca de turno é útil e verificável) e não
atribua nomes — exceto onde o próprio diálogo identifica quem fala (`"…, Douglas?"`,
`"obrigado Everton"`), que aí é evidência textual e não inferência.

Não deduza quem é quem por padrão de fala ("quem pergunta é o cliente"). Custa pouco e
erra muito.

## Nomes próprios e termos técnicos

Áudio comprimido arruína nome próprio, e é justamente o que mais importa em ata. Ordem
de confiança, do mais forte ao mais fraco:

1. **Fato de domínio verificável.** "Asaas" aparece como plataforma de cobrança com
   webhook de pagamento e taxa de 2,5% por pedido pago — bate com o produto real, então
   `Asas`/`Asus` é Asaas. Vale mais que qualquer consenso fonético.
2. **Consenso entre configurações independentes** (etapa 3).
3. **Coerência interna do próprio transcript.** O mesmo treinamento aparecia como
   "NR1" em dois pontos e "EDR1" em um terceiro — isso é um alerta, não uma correção.
4. **Hipótese sem base** → não normalize. Marque `[?]`.

**O caso em que o consenso está errado, e como declarar isso.** Em uma reunião o áudio
dizia, nas quatro configurações sem prompt, "Sankia" e "Tots". As formas corretas são
**Sankhya** e **TOTVS** — ERPs brasileiros que o contexto descreve exatamente (dicionário
de dados público, suporte pago por hora, cobrança por relatório). As duas grafias
oficiais só apareceram nas execuções **com** prompt, e o próprio
`verificar.py` avisou: *"só na configuração com prompt — provável enviesamento"*.

Aqui o fato de domínio vale mais que o consenso, e a correção foi aplicada. Mas foi
**declarada**: a tabela de normalizações registra que o reconhecimento cru diz "Sankia"
e que a base da correção é conhecimento do produto, não consenso. Corrigir é aceitável;
corrigir sem dizer que foi correção, não. Um leitor que precise citar o termo tem o
direito de saber que a evidência do áudio aponta para o outro lado.

Nunca "conserte" um termo para o que ele *deveria* ser pelo contexto, mesmo que soe
certo. Em um caso, o áudio dizia claramente "aula brava" (4 de 4 configurações) e o
contexto pedia "aula grátis". O texto entregue diz **"aula [brava?]"** com o comentário
— porque o documento precisa registrar o áudio, não o que faz sentido.

## Instalação e dependências

- **ffmpeg**: estático em `~/.config/terras-video/ffmpeg` (não há ffmpeg no PATH).
  Outro caminho via `TERRAS_FFMPEG`. Se faltar: `bash $SKILL_DIR/../terras-video/scripts/setup.sh`.
- **faster-whisper**: venv em `~/.local/share/asr/venv`. Os scripts têm shebang
  `python3` mas precisam do Python do venv:
  `~/.local/share/asr/venv/bin/python scripts/transcrever.py ...`.
  Para recriar: `python3 -m venv ~/.local/share/asr/venv && ~/.local/share/asr/venv/bin/pip install faster-whisper`.
  Python 3.14 funciona (`ctranslate2` tem wheel `cp314`).
- **diarização** (só se algum dia houver token): venv separado em `~/.local/share/asr/dia-venv`
  com `torch` CPU + `speechbrain` + `scikit-learn`.

## Armadilhas de API já pagas

Cinco erros que custaram tempo, para não repetir:

- **`torchaudio.load()` no 2.11 exige `torchcodec`** e falha com ImportError. Para WAV
  PCM, leia com o módulo `wave` da stdlib e converta com numpy. Menos dependência.
- **`clip_timestamps` do faster-whisper 1.2.1 está quebrado nos dois formatos
  documentados**: lista de floats estoura em `segment.items()`, lista de dicts estoura
  em `round(ts * frames_per_second)`. Fatie o áudio com ffmpeg em arquivos separados.
- **`pkill -f nome_do_script.py`** numa shell cujo próprio comando contém esse nome
  mata a própria shell. Use `pgrep -f` para conferir e `pkill` pelo PID.
- **`condition_on_previous_text=False`** evita laço de repetição em áudio longo. É o
  padrão dos scripts.
- **VAD** com `min_silence_duration_ms=500` e `speech_pad_ms=200`: sem VAD, áudio longo
  com silêncio faz o modelo inventar texto sobre o nada.

## Um detalhe de método

Quando a tarefa é "preciso da transcrição **real**", quase sempre houve uma transcrição
anterior errada — normalmente traduzida, porque a exportação saiu no idioma errado. Vale
abrir dizendo o que estava errado e por quê, com a prova (a frase traduzida que não
existe no áudio). É o que explica o pedido, e evita que o problema se repita na próxima
gravação.

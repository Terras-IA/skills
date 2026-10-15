---
name: terras-video-downloader
description: "Baixa o vídeo de uma URL (LinkedIn pelo player público; o resto via yt-dlp) e prepara a análise em folhas de quadros. Use para baixar ou analisar vídeo de link. Post do LinkedIn colado ou feed: terras-linkedin-videos. Não edita (terras-ffmpeg) nem monta (terras-video). Video download."
keywords: [baixar video, download, linkedin, video do post, yt-dlp, mp4, salvar video, lnkd.in, analisar video, quadros]
---

# terras-video-downloader

Recebe uma URL, descobre a plataforma e baixa o vídeo pelo meio que funciona nela. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`.

## Objetivo

Cada plataforma esconde o vídeo de um jeito. Sem mapa, o agente perde tempo instalando ferramenta que não precisa, ou extrai a URL errada do HTML e baixa nada. O motor `scripts/baixar.py` concentra a decisão: uma rota por plataforma, saída conferida e o mesmo relatório para todas.

## Regra dura

1. **Pergunte antes de baixar.** Rode `--listar` primeiro e mostre: autor ou origem, resolução e tamanho. Baixe só depois do sim. Baixar arquivo é ação que pede permissão. Exceção: link de post do LinkedIn colado sozinho é da `terras-linkedin-videos`, onde o próprio link é o sim.
2. **Nunca entre com login por conta própria.** Se o vídeo só aparece logado, pare e diga isso. Cookie ou senha do usuário quem fornece é o usuário.
3. **Não sobrescreva.** O script recusa destino existente; não contorne apagando o arquivo.
4. **O vídeo é do autor.** Ao entregar, lembre em uma linha que repostar pede crédito ou autorização.

## Como trabalhar

1. Listar:
   ```bash
   python3 "$SKILL_DIR/scripts/baixar.py" URL --listar --json
   ```
   O script segue encurtador (`lnkd.in`), detecta a plataforma e devolve `opcoes` (resolução e bitrate) ou `kind` da falha.
2. Mostrar ao usuário as opções e pedir o sim. Padrão: a melhor resolução.
3. Baixar:
   ```bash
   python3 "$SKILL_DIR/scripts/baixar.py" URL -o PASTA --json
   ```
   `--qualidade menor` quando o usuário quiser arquivo leve. Sem `-o`, grava na pasta atual.
4. Conferir: saída 0 e `bytes` igual ao `Content-Length` (o script já checa e apaga o `.parcial` se faltar). Reportar caminho e tamanho.

No LinkedIn o JSON traz também `texto_post`: use como contexto se o usuário pedir análise.

## Analisar o vídeo baixado

O agente não assiste vídeo: olha quadros. Sem ffmpeg, o caminho improvisado (ffmpeg de pacote Python) perde `ffprobe` e `drawtext` e as folhas saem sem o tempo.

1. ffmpeg e ffprobe no PATH. Faltando (`analisar.py` sai com 3), instale pelo gerenciador do sistema (`sudo apt-get install -y ffmpeg`) se o usuário já liberou; senão peça.
2. Gerar a ficha e as folhas:
   ```bash
   python3 "$SKILL_DIR/scripts/analisar.py" VIDEO --json
   ```
   Sai em `<video>-analise/`: `ficha.json` (duração, resolução, fps, áudio com `mudo`, `cortes_s`) e `folhaNN.jpg`, grade 2x3 com um quadro a cada `passo_s`, tempo carimbado. O passo padrão dá até 4 folhas; `--passo 2` para trecho rápido.
3. Ler **todas** as folhas antes de concluir. Detalhe ilegível: extraia o quadro cheio daquele tempo (`ffmpeg -ss T -i VIDEO -frames:v 1 q.png`) e leia.
4. Áudio com voz (`mudo: false`): transcrever com `terras-transcription` antes de resumir. Mudo: diga isso.
5. Entregar: o que é, o que mostra na ordem do tempo, e a leitura (o que funciona, o que o vídeo não mostra). Separe o que se vê nos quadros do que vem do `texto_post`.

## Rotas por plataforma

| Plataforma | Meio | Precisa de |
|------------|------|------------|
| LinkedIn (`linkedin.com`, `lnkd.in`) | MP4 do atributo `data-sources` do player, no CDN `dms.licdn.com`. Se a página do post não traz, tenta `/embed/feed/update/urn:li:activity:ID`, que é público | nada além do Python |
| Qualquer outra | `yt-dlp` | `pipx install yt-dlp` |
| Análise (qualquer origem) | `analisar.py` | ffmpeg e ffprobe |

Plataforma nova entra como função `rota_<nome>` no script e uma linha nesta tabela. Só vire rota própria quando o yt-dlp falhar nela ou exigir algo que a página pública já entrega.

## Falhas e o que fazer

| `kind` (saída) | Significa | Próximo passo |
|----------------|-----------|---------------|
| `sem_video` (2) | Página sem vídeo público: post de imagem ou documento, restrito a conexões, ou exige login | Dizer ao usuário. Se ele quiser, yt-dlp com `--cookies-from-browser`, e ele mesmo autoriza |
| `ferramenta_ausente` (3) | Rota precisa de yt-dlp | Pedir para instalar ou instalar com o sim dele |
| `existe` (1) | Destino já existe | Outra pasta ou o usuário apaga |
| `tipo` / `incompleto` (1) | CDN devolveu outra coisa ou cortou | Rodar de novo; a URL do LinkedIn expira (`t=`), por isso o script sempre relê a página |
| `rede` (1) | URL não abriu | Conferir a URL com o usuário |

## Armadilhas que já custaram tempo (LinkedIn)

- O HTML traz as URLs com `&amp;` e `&quot;`. Um `grep` que para no `&` corta o token `t=` e o CDN responde vazio. Por isso o script desfaz as entidades antes de ler.
- A mesma lista tem `thumbnail-with-play-button-overlay`: não é vídeo. O script só aceita caminhos `mp4-*`.
- O link `lnkd.in/p/...` redireciona para `/posts/...ugcPost-ID`, não `activity-ID`. O script aceita os dois.

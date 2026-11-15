---
name: terras-strudel
description: "Analisa uma música (link do YouTube ou áudio) e recria no Strudel o BPM, o tom, os acordes, o baixo e o groove, com pasta e documentação por música. Use para 'reverso de música', 'toca no Strudel', live coding. Só baixar vídeo: terras-video-downloader. Music to Strudel."
keywords: [strudel, live coding, reverso de musica, recriar musica, bpm, tom, acordes, groove, tidal, beat, youtube]
---

# terras-strudel

Transforma uma música de referência em código Strudel que toca o mesmo andamento, a mesma harmonia e o mesmo groove, e deixa uma pasta documentada por música. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`.

## Objetivo

Sair de um link do YouTube (ou de um arquivo de áudio) e chegar a um `strudel.js` que toca no strudel.cc. A pasta da música guarda os dados da análise e um README com a referência, o que foi medido, o que foi interpretado e os limites. A análise roda local, sem API.

## Regra dura

1. **Metadados antes de baixar.** Leia título, canal, duração e tamanho do áudio sem baixar e mostre ao dono. Só baixe depois de um sim explícito para aquele link.
2. **A melodia de uma obra protegida não é transcrita.** BPM, tom, progressão de acordes, linha de baixo na fundamental, groove de bateria e timbre podem ser recriados. A linha vocal ou o riff principal entram como **melodia original**, na escala do tom, com contorno e ritmo próprios: não imite a frase da voz nem de ouvido. Só trate como domínio público obra cujo autor morreu há mais de 70 anos (hino tradicional, clássico, folclore) e cite a fonte disso no README. Gravação ou arranjo recente de obra antiga continua protegido: recrie a partir da partitura original, não da gravação.
3. **Não declare "tocando" sem conferir.** Ver o botão `stop` não basta. Confira se todas as camadas disparam e se a aba **console do próprio Strudel** está sem erro (o console do navegador não mostra os erros do Strudel).
4. **O áudio baixado não vai para o git.** Commit só quando o dono pedir.

## Requisitos

`yt-dlp`, `ffmpeg` e Python com `librosa`. Se o `librosa` faltar, crie um venv descartável (`python3 -m venv <tmp>/venv && <tmp>/venv/bin/pip install librosa`). Não instale no Python do sistema.

## Como trabalhar

1. **Metadados.** Separe o stderr, porque o aviso de runtime JS do yt-dlp quebra o JSON:
   ```bash
   yt-dlp -J --no-playlist "<url>" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['title'],'|',d['uploader'],'|',d['duration_string']); [print(f['format_id'],f['ext'],f.get('abr'),f.get('filesize') or f.get('filesize_approx')) for f in d['formats'] if f.get('vcodec')=='none' and f.get('acodec') not in (None,'none')]"
   ```
   Link de playlist (`&list=`): use `--no-playlist` e trate só o vídeo do `v=`. Mostre título, canal, duração e tamanho, e peça o sim.
2. **Pasta da música.** Procure um projeto de músicas existente, isto é, um diretório com `musicas/*/strudel.js` (ex.: `find ~ -maxdepth 4 -path '*/musicas/*/strudel.js'`). Se achar, use esse projeto. Se não achar, crie um projeto novo com nome próprio (ex.: `~/projetos/strudel-reverso`), avise onde ficou e siga sem esperar: é um diretório novo e vazio, sem risco. Nunca crie dentro do repositório de outro projeto, mesmo que a sessão esteja aberta nele. Daqui em diante, `$PROJ` é a raiz desse projeto e todos os caminhos são absolutos (`$PROJ/musicas/<slug>`). Slug: título e artista em kebab-case. A estrutura está em `references/modelo-pasta.md`.
3. **Baixar só o áudio.** `yt-dlp -q --no-playlist -f 140 -o "$PROJ/musicas/<slug>/audio/<slug>.%(ext)s" "<url>"` (m4a de cerca de 128 kbps; se o 140 não existir, use `-f bestaudio`).
4. **Analisar:**
   ```bash
   python $SKILL_DIR/scripts/analisar.py $PROJ/musicas/<slug>/audio/<arquivo> $PROJ/musicas/<slug>
   ```
   Gera `dados/analise.json` e `dados/acordes.csv`. O script converte m4a e webm para wav com ffmpeg, porque o `librosa` não abre m4a direto.
5. **Interpretar.** Aqui entra o julgamento, e os erros são previsíveis:
   - **BPM dobrado.** Em balada, worship e pop lento, o `beat_track` costuma devolver o dobro (por exemplo 152 para 76). A grade `bateria_grade_16` tem 16 posições sobre **4 batidas detectadas**. Se o BPM medido for o dobro do real, essa grade cobre só meio compasso real, e a posição 8 corresponde ao 2º ou ao 4º tempo real. Regra prática: BPM medido acima de 120 em música lenta, com `medio_caixa` forte na posição 8 (ou 4 e 12 equivalentes), indica a metade. Se `grave_bumbo` também for forte na 0 e o `medio_caixa` empatar entre 0 e 8, a banda média está pegando o bumbo: decida pelo estilo e pelo andamento da letra. Registre no README o valor medido, o valor adotado e o motivo, e peça ao dono para confirmar ouvindo.
   - **Tom.** Use o primeiro candidato quando a correlação for de 0,85 ou mais. Abaixo disso, compare com o relativo e com o acorde que mais aparece.
   - **Progressões.** Não use todos os acordes do CSV. Separe as seções por `secoes_por_energia`, pegue o loop que se repete em cada uma e descarte acordes isolados fora do campo harmônico (geralmente erro do detector).
   - **Na leitura em half-time**, cada 2 linhas do CSV formam 1 compasso real.
6. **Escrever o `strudel.js`.** Use a cola em `references/strudel-cola.md`. Cabeçalho comentado com o tom, o BPM adotado e a frase "melodia é ORIGINAL".
7. **Tocar e conferir.**
   - Gere o link: `python $SKILL_DIR/scripts/strudel_url.py $PROJ/musicas/<slug>/strudel.js`.
   - Abra o link no navegador. Se a aba já estava no strudel.cc, só trocar o hash **não recarrega** o editor: navegue e depois recarregue.
   - Clique em play (o navegador só libera áudio depois de um clique). Durante 5 a 8 segundos, colete o texto dos elementos `.cm-content [style*="outline"]`: cada token que acende é um evento disparado. Toda camada (bumbo, caixa, prato, acordes, baixo, melodia) precisa aparecer.
   - Abra a aba **console** no painel lateral do Strudel. Se aparecer `sound ... not found`, troque pelo nome que existe na aba **sounds** e rode de novo.
   - Colar o código digitando no editor também funciona, mas o autocompletar pode aceitar uma sugestão no Enter. Prefira o link.
8. **Documentar.** Preencha `$PROJ/musicas/<slug>/README.md` pelo modelo e acrescente a música na tabela de `$PROJ/README.md`.

## Referências

- `references/modelo-pasta.md`: estrutura de pastas, `.gitignore` e modelo do README de cada música.
- `references/strudel-cola.md`: sintaxe usada nas recriações (andamento, bateria, `chord().voicing()`, escalas, timbres que existem no strudel.cc).
- `references/vermelho.md`: as falhas observadas sem a skill, que deram origem a cada regra.

## Fonte

Fluxo desenvolvido na casa em 2026-11 sobre o strudel.cc (AGPL-3.0, código em codeberg.org/uzu/strudel). A análise usa `librosa` (ISC). Perfis de tom de Krumhansl-Kessler.

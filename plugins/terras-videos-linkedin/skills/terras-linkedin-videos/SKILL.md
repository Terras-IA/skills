---
name: terras-linkedin-videos
description: "Varre o feed do LinkedIn por tema (ex.: arquitetura de software e IA), lista os posts com vídeo e baixa os escolhidos com o texto do post; link de post colado sozinho já baixa direto. Use para 'varre o feed', 'baixa o vídeo desse post' ou link lnkd.in/linkedin colado. LinkedIn feed video scan."
keywords: [linkedin, feed, vídeo, video, baixar, download, varrer feed, arquitetura de software, IA, lnkd.in, post, lote]
---

# terras-linkedin-videos

Dois caminhos para o mesmo destino: vídeo de post do LinkedIn salvo em disco, com o texto do post ao lado. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`.

- **Post colado:** o usuário manda um link (`lnkd.in/...`, `linkedin.com/posts/...`, `.../feed/update/urn:li:...`) e baixa na hora.
- **Varredura do feed:** rola o feed logado, filtra por tema, mostra os posts com vídeo e baixa os que o usuário escolher.

O download em si é do motor da `terras-video-downloader` (`baixar.py`, rota pública sem login). Esta skill cuida de achar o post, do lote, da pasta e do registro.

## Regra dura

1. **Link colado sozinho é o sim.** O usuário pediu para esse fluxo baixar direto. Mensagem que é só um link de post do LinkedIn (ou "baixa esse") vai direto para o `baixar_lote.py`, sem `--listar` antes. Link de outra plataforma não é desta skill: `terras-video-downloader`, que pergunta antes.
2. **Feed: mostrar antes, baixar depois.** Da varredura sai uma tabela; baixa só o que o usuário escolher ("todos" vale).
3. **Navegador só lê.** Nunca clique em "Copiar link da publicação" nem "Copiar código": clique sintético ali escreve na área de transferência do usuário. A URN sai do diálogo "Incorporar esta publicação", que o `feed_coletar.js` abre e fecha.
4. **Nunca faça login.** Feed deslogado: pare e peça para o usuário entrar no navegador.
5. **Não apague nem sobrescreva vídeo.** O motor recusa destino existente; o lote trata isso como "já baixado".
6. **O vídeo é do autor.** Ao entregar, lembre em uma linha que repostar pede crédito ou autorização.

## Post colado

```bash
python3 "$SKILL_DIR/scripts/baixar_lote.py" URL [URL ...]
```

Grava em `~/linkedin/assets/videos/AAAA-MM-DD/linkedin-<autor>-<id6>-720p.mp4` e um `.md` de mesmo nome com link, tamanho e texto do post. Post já baixado em qualquer data sai como `ja_baixado`, sem novo download. Entregar: autor, uma linha do que o post diz, caminho e tamanho. Oferecer a análise (abaixo) em uma linha.

## Varredura do feed

1. Abrir `https://www.linkedin.com/feed/` no navegador embutido (é o que tem a sessão do usuário). Conferir que está logado: título "Feed | LinkedIn" e o nome dele na coluna da esquerda.
2. Colar `scripts/feed_coletar.js` inteiro no `javascript_tool` e, na mesma chamada:
   ```js
   await feedColetar({rolagens: 8})   // ~40 posts; mais rolagens, mais posts
   ```
   Volta `{autor, promovido, video, texto}` por post, sem duplicata.
3. Filtrar pelo tema pedido lendo o `texto` (não por palavra solta: "arquitetura" em anúncio de faculdade não conta). Descartar `promovido` salvo pedido.
4. Mostrar ao usuário duas listas curtas: **com vídeo** (autor, do que trata em uma linha, por que entra no tema) e **no tema, sem vídeo** (os melhores textos, que podem virar pauta).
5. Para os escolhidos, pegar a URN um por vez (o diálogo é único na página):
   ```js
   const r = []; for (const a of ['Autor 1', 'Autor 2']) r.push(await feedUrn(a)); r
   ```
   O nome é exatamente o `autor` que o `feedColetar` devolveu.
6. Baixar todos de uma vez com `baixar_lote.py` passando as `url` devolvidas.

## Analisar depois

`terras-video-downloader`, seção "Analisar o vídeo baixado" (`analisar.py` gera folhas de quadros; áudio com voz vai para `terras-transcription`). O `.md` ao lado do vídeo já traz o texto do post para separar o que se vê do que o autor afirma.

## Falhas

| Sinal | Significa | Próximo passo |
|-------|-----------|---------------|
| `sem_video` | Post sem vídeo público, restrito a conexões ou só logado | Dizer ao usuário. O vídeo do feed pode ser de anúncio ou repost; confira o autor |
| `feedUrn` → `card não encontrado` | O feed recarregou ("Novas publicações") e o card saiu do DOM | Rodar `feedColetar` de novo e repetir |
| `feedUrn` → `item Incorporar ausente` | Post que não permite incorporar (alguns anúncios e reposts) | Abrir o post no navegador e ler a URL da barra |
| `diálogo anterior não fechou` | Diálogo travado | Fechar pelo X na tela e repetir |
| `motor_ausente` | `terras-video-downloader` não instalada ao lado | Instalar pelo `scripts/instalar.sh` do repositório |

Detalhe do DOM do feed e armadilhas que já custaram tempo: `references/feed-dom.md`.

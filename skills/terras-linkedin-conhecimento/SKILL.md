---
name: terras-linkedin-conhecimento
description: "Baixa texto e imagens de post do LinkedIn (link ou tema) e gera nota de conhecimento: o que diz, o que a imagem traz, conferência em fonte primária e lacunas. Use para 'estudar esse post', 'gera conhecimento' ou 'posts úteis sobre X'. Vídeo: terras-linkedin-videos. Feed: terras-linkedin-varredura."
keywords: [linkedin, post, imagem, infográfico, texto, baixar, conhecimento, estudo, nota, lnkd.in, aprender, base de conhecimento, knowledge]
---

# terras-linkedin-conhecimento

Post do LinkedIn com texto e imagem vira uma nota de estudo conferida, guardada com o original. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`.

## Objetivo

O post de LinkedIn é resumo de alguém. Copiar o texto não gera conhecimento; a nota vale pelo que o post não entrega sozinho: o conteúdo da imagem (que o texto costuma não repetir), a conferência de cada afirmação técnica numa fonte primária e o que falta para aplicar sem errar.

## Regra dura

1. **Ler a imagem antes de escrever.** Abrir cada `imagem-N` com Read. A nota que só usa o texto perde metade do post. Ilegível é ilegível: dizer, não adivinhar.
2. **Veredito só com fonte.** `certo`, `precisa nuance` ou `errado` exige fonte primária consultada nesta sessão (docs oficiais, RFC, spec). Sem consulta, `não conferi`. Soar certo não é conferir.
3. **Não sobrescrever.** O script não regrava pasta existente. Nota já escrita para o post: mostrar a existente e perguntar antes de refazer.
4. **Nunca fazer login.** O script lê só a página pública. Post restrito: dizer e parar.
5. **Crédito sempre.** A nota abre com autor, data e link. Imagem do autor não vai para post próprio sem autorização.

## Como trabalhar

1. **Baixar.** Link colado com pedido de estudar, salvar ou "gerar conhecimento" é o sim:
   ```bash
   python3 "$SKILL_DIR/scripts/baixar_post.py" URL [URL ...]
   ```
   Grava em `~/linkedin/conhecimento/AAAA-MM-DD/<autor>-<id6>/` (data de publicação): `post.md` (link, autor, números, texto original), `texto-plano.txt` (negrito Unicode desfeito, 𝗝𝗪𝗧 → JWT) e `imagem-N.jpg`. GIF animado sai como `imagem-N.gif` com `imagem-N-folha.png` (8 quadros em grade) e `imagem-N-final.png` (último quadro). O JSON de saída diz pasta, imagens, `gif` e avisos.
2. **Ler.** `texto-plano.txt` e cada imagem com Read. GIF: ler a folha (a progressão) e o último quadro (o estado completo, em resolução cheia); quadro do meio com detalhe pequeno, recortar e ler.
3. **Conferir.** Listar as afirmações técnicas do texto e da imagem. Para cada uma relevante, buscar a fonte primária (documentação oficial do fornecedor, como Microsoft Learn para .NET e Azure, RFC, spec). Uma busca bem feita costuma cobrir várias afirmações.
4. **Escrever** `conhecimento.md` na mesma pasta pelo modelo de `references/modelo-conhecimento.md`.
5. **Indexar.** Acrescentar a linha no topo de `~/linkedin/conhecimento/indice.md` (criar com `# Conhecimento do LinkedIn` se não existir).
6. **Entregar** em poucas linhas: o assunto, o achado mais útil da conferência (o que o post erra ou omite), o caminho da nota.

Vários links de uma vez: baixar todos numa chamada, escrever uma nota por post.

## Buscar posts por tema

Pedido como "acha posts úteis sobre X" ou "baseado nas minhas competências":

1. **Temas.** Sem tema dado, tirar as competências do material do usuário (currículo, carta de apresentação em `~/linkedin/cartas/`) e montar uma consulta curta por competência. Termo curto rende mais que frase ("Kubernetes", não "Kubernetes production").
2. **Buscar** no navegador embutido, que tem a sessão do usuário, com filtro de imagem e último mês:
   `https://www.linkedin.com/search/results/content/?keywords=TEMA&contentType=%22photos%22&datePosted=%22past-month%22`
3. **Coletar** com `scripts/busca_coletar.js` (colar no `javascript_tool`): devolve autor, reações, URN e início do texto, sem clicar em nada. Guardar em `sessionStorage` para reusar após cada navegação.
4. **Escolher** pelo texto: descartar vaga, relatório de mercado, apresentação pessoal, idioma que o usuário não lê. Engajamento ajuda a ordenar, não decide.
5. **Baixar** os escolhidos de uma vez: `https://www.linkedin.com/feed/update/<urn>/` funciona para `share`, `ugcPost` e `activity`.
6. Seguir "Como trabalhar" do passo 2 em diante, uma nota por post.

## Falhas

| Sinal | Significa | Próximo passo |
|-------|-----------|---------------|
| `kind: login` / `sem_conteudo` | Post restrito a conexões, removido ou só logado | Dizer ao usuário; pedir o texto e um print, e seguir do passo 2 |
| `aviso: post tem vídeo` | O conteúdo principal é vídeo | Vídeo com `terras-linkedin-videos`; a nota usa o texto e a transcrição |
| `documento: N páginas, transcrição em documento.txt` | Carrossel PDF baixado como `pagina-NN.jpg` | Ler `documento.txt`; abrir as páginas com diagrama ou código |
| `documento: ..., sem texto transcrito` | Slides só em imagem | Juntar páginas numa folha (ffmpeg `vstack`) e ler com Read |
| `gif: {quadros, folha, final}` | GIF animado (demo, infográfico que se monta) | Ler folha e final; a nota descreve o roteiro da animação. GIF salvo à mão: `baixar_post.py --gif arquivo.gif` |
| `aviso_imagem` / `imagens: []` com post que tem imagem | JSON-LD veio com o placeholder; o script já tentou 2 vezes | Rodar de novo com `--base` noutra pasta, ou baixar a URL `feedshare` do HTML e rodar `--gif`/Read |
| `status: parcial` | Alguma imagem não baixou (link assinado expirou) | Rodar de novo em outra pasta (`--base`) ou pedir print |
| `ja_baixado` | Post já está na base | Ler a pasta; se já tem `conhecimento.md`, mostrar |

## Limites conhecidos

- A imagem vem na resolução do link assinado (geralmente 800 px de largura). Trocar o tamanho na URL dá 403: a assinatura `t=` vale só para aquele tamanho.
- Post com várias imagens: o JSON-LD às vezes lista só a primeira; o script cai para o card principal do HTML, que já foi conferido apenas em post de imagem única.
- A página pública às vezes vem com o placeholder "Posted on LinkedIn" (static.licdn.com) no JSON-LD; o script descarta qualquer imagem fora de `media.licdn.com/dms/image`. Imagem azul com o logo do LinkedIn na pasta: baixar de novo.
- A busca carrega poucos cards por consulta (cerca de 3 com filtro de imagem); para volume, fazer mais consultas em vez de rolar mais.
- A página traz comentários, mas o script ignora: foto e texto de comentário não são do autor.

## Referências

- `references/modelo-conhecimento.md` — modelo do `conhecimento.md`, regras de cada seção e formato da linha do índice.

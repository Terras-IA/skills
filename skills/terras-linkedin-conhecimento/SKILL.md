---
name: terras-linkedin-conhecimento
description: "Baixa texto e imagens de post do LinkedIn (lnkd.in ou linkedin.com) e gera nota de conhecimento: o que diz, o que só a imagem traz, conferência em fonte primária, lacunas e revisão. Use para 'estudar/salvar esse post' ou 'gera conhecimento'. Vídeo: terras-linkedin-videos. Comentar: terras-linkedin."
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
   Grava em `~/linkedin/conhecimento/AAAA-MM-DD/<autor>-<id6>/` (data de publicação): `post.md` (link, autor, números, texto original), `texto-plano.txt` (negrito Unicode desfeito, 𝗝𝗪𝗧 → JWT) e `imagem-N.jpg`. O JSON de saída diz pasta, imagens e avisos.
2. **Ler.** `texto-plano.txt` e cada imagem com Read.
3. **Conferir.** Listar as afirmações técnicas do texto e da imagem. Para cada uma relevante, buscar a fonte primária (documentação oficial do fornecedor, como Microsoft Learn para .NET e Azure, RFC, spec). Uma busca bem feita costuma cobrir várias afirmações.
4. **Escrever** `conhecimento.md` na mesma pasta pelo modelo de `references/modelo-conhecimento.md`.
5. **Indexar.** Acrescentar a linha no topo de `~/linkedin/conhecimento/indice.md` (criar com `# Conhecimento do LinkedIn` se não existir).
6. **Entregar** em poucas linhas: o assunto, o achado mais útil da conferência (o que o post erra ou omite), o caminho da nota.

Vários links de uma vez: baixar todos numa chamada, escrever uma nota por post.

## Falhas

| Sinal | Significa | Próximo passo |
|-------|-----------|---------------|
| `kind: login` / `sem_conteudo` | Post restrito a conexões, removido ou só logado | Dizer ao usuário; pedir o texto e um print, e seguir do passo 2 |
| `aviso: post tem vídeo` | O conteúdo principal é vídeo | Vídeo com `terras-linkedin-videos`; a nota usa o texto e a transcrição |
| `aviso: documento` | Carrossel PDF: a página pública não traz as páginas | Pedir o PDF baixado pelo usuário e ler com Read |
| `status: parcial` | Alguma imagem não baixou (link assinado expirou) | Rodar de novo em outra pasta (`--base`) ou pedir print |
| `ja_baixado` | Post já está na base | Ler a pasta; se já tem `conhecimento.md`, mostrar |

## Limites conhecidos

- A imagem vem na resolução do link assinado (geralmente 800 px de largura). Trocar o tamanho na URL dá 403: a assinatura `t=` vale só para aquele tamanho.
- Post com várias imagens: o JSON-LD às vezes lista só a primeira; o script cai para o card principal do HTML, que já foi conferido apenas em post de imagem única.
- A página traz comentários, mas o script ignora: foto e texto de comentário não são do autor.

## Referências

- `references/modelo-conhecimento.md` — modelo do `conhecimento.md`, regras de cada seção e formato da linha do índice.

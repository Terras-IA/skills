---
name: terras-coders-mural
description: >-
  Engajamento em lote no Mural de Posts da comunidade COD3RS (app.coders.com.br): lista os posts
  novos ou mais antigos, curte no mural, lê cada post linkado no LinkedIn, escreve um comentário
  curto e específico, publica em inglês no LinkedIn e o mesmo comentário em português no mural,
  e opcionalmente publica o post do dia do usuário. Use quando o pedido envolver mural da COD3RS,
  coders.com.br, "curtir e comentar os posts do coders", SSI do dia, post do dia, engajamento na
  comunidade, "pega mais posts do mural", ou agendar essa rotina. COD3RS community wall, batch
  like and comment, LinkedIn engagement.
keywords: [cod3rs, coders, mural, linkedin, engajamento, ssi, comentario, curtir]
version: "1.0.0"
metadata:
  requires: navegador controlável pelo agente (browser pane do Claude ou Claude in Chrome), com o usuário logado na COD3RS e no LinkedIn
---

# Mural COD3RS: curtir e comentar em lote

## Objetivo

Membros da COD3RS postam no mural o link do post do dia no LinkedIn e esperam engajamento. Esta skill
faz a rodada inteira: descobre o que é novo, curte no mural, lê cada post de verdade, escreve um
comentário que prova leitura, e publica nos dois lugares só depois da aprovação do usuário.

## Regra dura

1. **Nada público sem aprovação.** Curtir, comentar e publicar aparecem para outras pessoas. Mostre
   o lote inteiro (tabela: id, autor, comentário EN, comentário PT) e espere um "aprovado" explícito
   no chat. Uma aprovação vale para aquele lote, não para o próximo, nem para uma rodada agendada.
2. **Curtir é toggle.** `POST /like` em post já curtido DESCURTE. Só curta com `likedByMe === false`,
   relido na hora (o `__mural.like` já faz isso).
3. **Nunca repita às cegas.** Se uma chamada falhar ou der timeout no meio, primeiro confira o estado
   (`__mural.commented`, `prep` que acusa "já comentado"), depois reenvie só o que falta.
4. **Confira a aba antes de rodar script.** Resposta HTML/404 ou "aba errada" = a aba mudou de site.
   Navegue de volta; nunca interprete isso como "nada foi feito" sem reler o estado.
5. **O token fica na página.** Nunca leia, imprima ou envie `_cj_token` para fora do navegador.
6. **Credenciais são do usuário.** Tela de login, código de verificação (2FA/OTP), captcha ou popup
   de login: pare e peça para ele resolver. Não digite senha nem código.

## Como trabalhar

1. **Aba da COD3RS.** Abra `https://app.coders.com.br/comunidade#c/mural-posts/post`. Se pedir login,
   pare e peça ao usuário. Injete `scripts/mural.js` (cole o arquivo num javascript_exec) e rode
   `await __mural.me()` para saber quem é o usuário.
2. **Descobrir posts.**
   - Rodada diária: `await __mural.list({hours: 36})`.
   - "Pega mais / rola a tela": `await __mural.list({before: <oldest da chamada anterior>})`, repetindo
     até juntar a quantidade pedida.
   - Descarte posts em que o usuário já comentou: `await __mural.commented(ids)`. Diga quantos foram
     pulados e por quê.
3. **Ler no LinkedIn.** Para cada post com `link`: navegue e use `get_page_text` (1.500 caracteres
   bastam). Leia o texto do autor, não o título do mural. Post sem link: comentário só no mural,
   baseado no texto do mural.
4. **Escrever os comentários.** Ver `references/estilo-comentarios.md`. Um par por post: EN para o
   LinkedIn, PT para o mural, mesma ideia. Salve num JSON (`id, autor, link, en, pt`). Se um
   comentário afirmar algo sobre a experiência pessoal do usuário, sinalize na tabela.
5. **Aprovação.** Mostre a tabela completa e espere o "aprovado". Aceite exclusões ("menos 8452") e
   trocas de texto.
6. **Mural.** Na aba da COD3RS (reinjete `mural.js` se a página recarregou):
   - `await __mural.like(ids)` em blocos de até 20.
   - `await __mural.comment([[id, pt], ...])` em blocos de até 10.
   Reporte o retorno de cada bloco.
7. **LinkedIn.** Um post por vez, com `scripts/linkedin.js` (protocolo no cabeçalho do arquivo):
   navigate → `prep(snip)` → digitar o texto EN com a ferramenta de teclado → `submit(snip)` → esperar
   ~4s. Agrupe 4-5 posts por lote de ações do navegador. Erro "já comentado" = pule; "não confirmado" =
   confira a página antes de qualquer reenvio.
8. **Fechamento.** Tabela final: curtidas, comentários no mural, comentários no LinkedIn, pulados e
   motivo. Números vêm do retorno das chamadas, não da intenção. Diga se o mural ficou **em dia**
   (todo post das últimas 36h com comentário seu) ou quantos faltam e por quê.

## Post do dia do usuário (opcional)

Só quando o usuário fornecer o link (ou pedir para pegar o post mais recente do perfil dele) e aprovar
título e texto: `await __mural.publish({title, content})`. Formato usual da comunidade: título curto
("SSI do dia: <tema>") e o link no corpo. Não testado em produção: confirme pelo retorno do
`publish` (deve trazer `id` e `createdAt`) e peça ao usuário para olhar o mural. Se vier sem `id`,
avise que o post pode não ter saído e não repita sem ele conferir (repetir pode duplicar o post).

## Rotina agendada

Uma tarefa agendada pode rodar os passos 1-4, mas **para no passo 5**: sem o usuário no chat não há
aprovação, então nada é curtido nem comentado. Ela termina salvando o JSON dos comentários
(`mural-AAAA-MM-DD.json`) e respondendo com a tabela de aprovação, que o usuário lê ao abrir a
sessão da tarefa. A execução só continua quando ele responder "aprovado" nessa sessão. O navegador
precisa estar aberto e logado nos dois sites no horário da tarefa.

## Riscos para avisar ao usuário

Automação de ações no LinkedIn vai contra os termos de uso da plataforma. O ritmo lento, o volume
baixo e a aprovação humana reduzem o risco, mas não eliminam. A decisão de usar é do usuário.

## Referências

- `scripts/mural.js`: helper in-page da COD3RS (`me, list, commented, like, comment, publish`).
- `scripts/linkedin.js`: helper in-page do LinkedIn (`prep, submit`), PT e EN.
- `references/api-coders.md`: endpoints, payloads e comportamento observado da API do mural.
- `references/estilo-comentarios.md`: como escrever comentários que provam leitura, com exemplos.
- `references/red-baseline.md`: falhas reais observadas sem a skill e a regra que fecha cada uma.

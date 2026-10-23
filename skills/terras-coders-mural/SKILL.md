---
name: terras-coders-mural
description: "Engajamento em lote no Mural de Posts da COD3RS: curte, lê o post linkado no LinkedIn e comenta em inglês lá e em português no mural, só com aprovação. Use para mural da COD3RS, coders.com.br, SSI do dia, post do dia ou agendar essa rotina."
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
   Navegue de volta; nunca interprete isso como "nada foi feito" sem reler o estado. "sessão
   expirada" = a aba caiu em `/login`: pare e peça ao usuário para entrar de novo.
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
   - **Domains e Stacks** (todos valem ponto): entram em toda rodada. `await __mural.spaces()` devolve
     os slugs (de `bootstrap.channelReads`, menos os não pontuáveis) e `await __mural.listSpace(slug)`
     lista cada um (um espaço por chamada, por causa dos 45s; `hasMore: true` na volta = janela não
     coberta, chame de novo). Por baixo é a mesma API `/spaces/<slug>/messages?kind=post`, janela de 30 dias (decisão do usuário em 16/10: post mais antigo fica de fora; a API pagina com `hasMore` + `before=<createdAt mais antigo>`). Slugs:
     Domains `system-design, live-coding-leetcode, frontend, backend, devops, qa, produto, cloud,
     banco-de-dados, dados, cybersecurity`; Stacks `inteligencia-artificial, java, net, react, power-bi,
     node, ruby-on-rails, python, react-native` (Mobile), `data-science`. A lista de canais está em
     `bootstrap.channelReads` (`<slug>:post`); `spaces()` já inclui espaço novo. Mesma regra de curtir,
     comentar e aprovar; marque a coluna `espaco` na tabela. Post do próprio usuário: pular.
     Post sem link do LinkedIn (apresentação, pergunta): comentário só na COD3RS, no idioma do post.
3. **Ler no LinkedIn.** Um post do mural pode trazer vários links (`links`): cada link é um post do
   LinkedIn e entra na tabela como linha própria (o comentário do mural continua um só). Para cada link: navegue e use `get_page_text` (1.500 caracteres
   bastam). Leia o texto do autor, não o título do mural. Post sem link: comentário só no mural,
   baseado no texto do mural.
3b. **Gerar conhecimento** de cada post que vai receber comentário no LinkedIn, pela skill
   `terras-linkedin-conhecimento` (baixar com `baixar_post.py`, ler imagens, conferir em fonte primária,
   `conhecimento.md` + linha no `indice.md`). Acrescente a seção `## Comparar com os nossos`: quais
   posts do usuário em `~/linkedin/posts/` tratam do mesmo tema (link relativo `../../../posts/...`),
   o que o post de terceiro traz que o nosso não traz, e pauta possível. Sem post nosso relacionado:
   dizer isso e sugerir pauta. A nota é local, não precisa de aprovação; ela também alimenta o
   comentário (ler o post a fundo rende comentário melhor). Pasta já baixada (`ja_baixado`) com nota:
   reaproveitar. Grave o caminho da nota no JSON da rodada (`conhecimento`).
4. **Escrever os comentários.** Ver `references/estilo-comentarios.md`. Um par por post: EN para o
   LinkedIn, PT para o mural, mesma ideia. Passe o EN pela `terras-humanizer` (modo embutido:
   padrões de IA e régua B1/B2 de `terras-humanizer/references/ingles-b1b2.md`) antes de
   montar a tabela; termo técnico exato fica. Salve num JSON (`id, autor, link, en, pt`). Se um
   comentário afirmar algo sobre a experiência pessoal do usuário, sinalize na tabela.
5. **Aprovação.** Mostre a tabela completa e espere o "aprovado". Aceite exclusões ("menos 8452") e
   trocas de texto.
6. **Mural.** Na aba da COD3RS (reinjete `mural.js` se a página recarregou):
   - `await __mural.like(ids)` em blocos de até 20 (posts do mural).
   - Post de Domains/Stacks: `await __mural.likeIn(slug, ids)`, agrupado por `espaco`. `like` só acha
     post do mural-posts; o estado `likedByMe` precisa ser relido no espaço certo.
   - `await __mural.comment([[id, pt], ...])` em blocos de até 10.
   Reporte o retorno de cada bloco.
7. **LinkedIn.** Um post por vez, com `scripts/linkedin.js` (protocolo no cabeçalho do arquivo):
   navigate → `prep(snip)` → digitar o texto EN com a ferramenta de teclado → `submit(snip)` → esperar
   ~4s. Agrupe 4-5 posts por lote de ações do navegador. Erro "já comentado" = pule; "não confirmado" =
   confira a página antes de qualquer reenvio. Página com "Somente suas conexões podem comentar"
   (ou "Only connections can comment"): não dá para comentar; pule e reporte o motivo no fechamento.
8. **Fechamento.** Tabela final: curtidas, comentários no mural, comentários no LinkedIn, pulados e
   motivo. Números vêm do retorno das chamadas, não da intenção. Diga se o mural ficou **em dia**
   (todo post das últimas 36h com comentário seu) ou quantos faltam e por quê.
9. **Colheita.** Comentar sem colher é trabalho perdido. Rode
   `python3 -I scripts/colher.py ~/linkedin > ~/linkedin/notas/colheita-mural-AAAA-MM-DD.md` (só lê) e
   feche a rodada com três linhas: o tema mais maduro e a pauta que o puxa, quantas perguntas nossas no
   LinkedIn ainda não foram conferidas, e se alguma nota da rodada reforça uma pauta já na fila.
   Resposta do autor a pergunta nossa vai para a nota do post (`## Resposta do autor`). Quando uma
   peça sair de notas, registre em `~/linkedin/conhecimento/usadas.txt` (`peça: pasta, pasta`) para
   a nota sair da fila.

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

- `scripts/mural.js`: helper in-page da COD3RS (`me, spaces, list, listSpace, commented, like, likeIn, comment, publish`).
- `scripts/linkedin.js`: helper in-page do LinkedIn (`prep, submit`), PT e EN.
- `references/api-coders.md`: endpoints, payloads e comportamento observado da API do mural.
- `references/estilo-comentarios.md`: como escrever comentários que provam leitura, com exemplos.
- `references/red-baseline.md`: falhas reais observadas sem a skill e a regra que fecha cada uma.

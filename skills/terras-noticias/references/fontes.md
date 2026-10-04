# Fontes

## ratos de IA (a canônica)

- Roundup semanal de IA, em PT-PT ("as novidades de ia da semana"). Índice em
  https://ratos.link/ com os episódios em `/epNN/` (do ep08 ao atual; a
  numeração pula alguns números).
- Cada episódio tem seções temáticas (OpenAI DevDay, ChatGPT, Claude, "calma,
  é bolha", reflexões) e os itens no formato: manchete curta + link único,
  quase sempre um post no X. Alguns itens trazem link extra para o blog
  oficial.
- A página não mostra datas; as datas dos itens vêm dos posts de origem.
- O episódio novo aparece no índice. Se o usuário mandar um ep específico,
  trabalhe o ep mandado, não o "mais novo".

## Como abrir cada tipo de link

| Link | Como abrir | Observação |
|---|---|---|
| x.com / twitter.com | abra a página direto (devolve texto, data e engajamento) | fallback: `curl -sL "https://publish.twitter.com/oembed?url=<url>&omit_script=1"` |
| Blog oficial, release notes, changelog | abra a página | é a fonte primária: busque número, data e versão |
| openai.com | acesso direto devolve 403 (Cloudflare) | verificar no snapshot do Wayback: `https://web.archive.org/web/<timestamp>/<url>`; para achar o snapshot, `curl -s "https://archive.org/wayback/available?url=<url>&timestamp=<AAAAMMDD>"`. Ex.: recap do DevDay 2026 em `web.archive.org/web/20260929221529/https://openai.com/index/devday-2026-recap/` |
| YouTube ou site de vídeo | abra a página (título e descrição) | sinal, não fonte |
| Paywall, bloqueio ou erro | marcar `⚠️` e não afirmar | |

## Contrato de uma boa fonte (para aceitar outras)

Um roundup serve se lista itens com link para a origem, em seções temáticas,
com uma linha de descrição. O mesmo fluxo vale para qualquer boletim (TLDR,
Import AI, Ben's Bites, digest do HN). Fonte que só dá o texto do autor, sem
link por item, não permite verificação: diga isso na ficha e rebaixe o tom.

## Verificação

- Boletim é ponteiro, não prova (mesma regra da `terras-last30days`): descobre
  a pauta; o fato se confirma na origem.
- Precedência: release notes/changelog/documentação oficial > blog oficial >
  post oficial no X > post de terceiro ou reply.
- Divergência entre boletim e fonte primária: vale a primária. Registre a
  divergência no digest; ela costuma ser o melhor conteúdo do post.

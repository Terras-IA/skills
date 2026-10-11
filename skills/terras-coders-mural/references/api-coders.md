# API do mural da COD3RS (observada em 2026-09-29)

API interna usada pelo próprio front (`/design-system/community-app.js`). Não é pública nem
documentada: pode mudar sem aviso. Se uma chamada começar a falhar, abra o bundle atual e procure
por `/api/community/` para ver o formato vigente.

## Autenticação

- Token JWT em `localStorage['_cj_token']`, enviado como `Authorization: Bearer <token>`.
- As chamadas só funcionam de dentro da aba `https://app.coders.com.br` (mesma origem).
- `GET /api/community/bootstrap` → `me.username` (slug, ex. `fulano-de-tal`) e `me.displayName`.

## Leitura

| Chamada | Retorno |
|---|---|
| `GET /api/community/spaces/mural-posts/messages?kind=post` | `{items, hasMore}`: ~50 posts mais recentes, ordem crescente de data |
| `...&since=<ISO>` | posts criados depois da data |
| `...&before=<ISO>` | página anterior (o lazy load ao rolar a tela) |
| `GET /api/community/messages/{id}/comments` | lista de comentários (`author` = slug) |

Campos úteis do post: `id, author, authorDisplayName, title, content, attachments, createdAt,
likeCount, commentCount, likedByMe`. O link do LinkedIn costuma estar em `content`, às vezes em
markdown (`[url](url)`), às vezes só no preview em `attachments`.

## Escrita

| Chamada | Body | Observação |
|---|---|---|
| `POST /api/community/messages/{id}/like` | `{author: displayName}` | **toggle**; retorna `{liked, likeCount}` |
| `POST /api/community/messages/{id}/comments` | `{author: displayName, content}` | 201 com o comentário criado |
| `POST /api/community/spaces/mural-posts/messages` | `{author, title, content, attachments, coverUrl, kind:"post"}` | cria post; não testado |

Existem também `PUT/DELETE /api/community/comments/{id}` (editar/apagar comentário). Não fazem parte
do fluxo; use só se o usuário pedir para corrigir um comentário publicado.

## Limites práticos

- A ferramenta de JavaScript do navegador corta a execução em ~45s. Blocos de 10 comentários com
  0,5s de intervalo cabem com folga; 37 de uma vez não cabem (o loop morre no meio).
- Quando o timeout acontece, o script para de verdade: o que não foi enviado não é enviado depois.

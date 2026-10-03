# API do board de vagas da COD3RS (observada em 2026-10-02)

App separado do mural: o front mora em `/board` e é carregado num iframe pela
página da comunidade (`/comunidade#vagas` → `view-vagas`). Bundle:
`/design-system/board-app.js`. Mesma origem e mesma autenticação do mural —
mas endpoints, campos e filtros são outros. Não é API pública nem documentada:
pode mudar sem aviso. Se uma chamada começar a falhar, abra o bundle atual e
procure por `/api/board/` para ver o formato vigente.

## Autenticação

- Token JWT em `localStorage['_cj_token']`, enviado como `Authorization: Bearer <token>`.
- As chamadas só funcionam de dentro da aba `https://app.coders.com.br` (mesma origem).
- O board tem acesso controlado (`hasJobsAccess`) e um gate de termos
  (`terms-gate.js`, erro 403 com `code: "terms_required"`). Se bateu no gate,
  pare e peça para o usuário aceitar os termos no navegador.

## Leitura

| Chamada | Retorno |
|---|---|
| `GET /api/board/me` | perfil do assinante do board (vitrine) |
| `GET /api/board/jobs/facets` | `{sources, schedules, modalities, locationScopes}` — valores válidos para os filtros |
| `GET /api/board/jobs?q=&page=1&limit=50&dateFrom=YYYY-MM-DD&source=&schedule=&modality=&locationScope=&avoidBrazil=0` | `{total, jobs: [...]}` |

- `source`, `schedule`, `modality` e `locationScope` são **repetidos** para
  múltiplos valores (`?source=a&source=b`).
- `limit` padrão do front é 10; a API aceita pelo menos 50 por página.
- `avoidBrazil=1` é a preferência "fugir do Brasil" da vitrine; para filtrar
  com o currículo deixe `0` e julgue com o `perfil.md`.

## Campos de um job (os que o front usa)

`jobUrl` (link externo da vaga — é a chave), `title`, `company`, `source`
(origem: LinkedIn, Gupy, …), `location`, `locationScope`, `modality`,
`schedule`, `salary` (quando a vaga traz faixa), `firstSeenAt` / `sentAt` /
`createdAt` (data; o card usa `sentAt || firstSeenAt`).

**Não existe campo de descrição** no retorno da lista: o encaixe fino (o que o
anúncio pede de verdade) só se resolve abrindo o `jobUrl` no navegador.

## Comportamento observado (2026-10-02)

- Facets: `locationScopes` = brazil, latam, unknown, worldwide; `modalities` =
  flexible, hybrid, onsite, other, remote; `schedules` = full-time, hybrid,
  other, part-time; `sources` = ~150 (YCHiring, LinkedIn, G2i, Deel, Turing,
  CI&T, BairesDev, …).
- Volume: ~5.400 vagas em 30 dias, ~270/dia. Ingestão é em lote — dezenas de
  vagas compartilham o mesmo `firstSeenAt` ao segundo, então ordem interna de
  empate não significa nada.
- LinkedIn entra como fonte de posts da comunidade: muitos títulos não dizem o
  cargo ("WE'RE HIRING"). A API só traz o título do post.

## Escrita (existe, mas esta skill NÃO usa)

O board tem kanban pessoal (`PUT /api/board/{email}/cards/batch`, status das
cards, aprovação com confete) e preferências (`PUT /api/board/vitrine-prefs`).
São ações do usuário no app; a skill é somente leitura e não toca nelas.

## Limites práticos

- A ferramenta de JavaScript do navegador corta a execução em ~45s. O `list`
  pagina no máximo 8 chamadas com 300ms de intervalo — cabe com folga; se
  precisar de mais, chame de novo afunilando por `desde`.

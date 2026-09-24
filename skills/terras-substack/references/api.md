# API interna da Substack (endpoints e payloads)

Nao existe API publica de escrita. Tudo abaixo e o que o **editor web** usa.

Proveniencia das informacoes:

1. **Validado ao vivo nesta conta** (2026-09-15, publicacao `eolimabr.substack.com`):
   criacao de rascunho, aplicacao de tags, upload de imagem, leitura e remocao de
   rascunho — todos executados com sucesso, e o resultado conferido dentro do
   editor.
2. **Sondagem de endpoints**: endpoint existente sem sessao responde
   `403 {"errors":[{"msg":"Not authorized"}]}`; caminho inexistente responde `404`
   com HTML.
3. **Cliente de referencia** `python-substack` (ma2za) — serviu de base para os
   nomes de campo antes da validacao ao vivo.

Nada disso e oficial: se um campo mudar, valide no navegador logado
(DevTools > Network > faca a acao no editor > copie a requisicao).

## Bases e cabecalhos

- API global: `https://substack.com/api/v1`
- API da publicacao: `https://<subdominio>.substack.com/api/v1`
- Autenticacao: cookie de sessao `substack.sid` (as vezes acompanhado de
  `substack.lli` e `connect.sid`). Sem OAuth, sem token, sem chave.
- Cabecalhos usados pela ferramenta: `User-Agent` de Chrome, `Accept:
  application/json`, `Content-Type: application/json`, `Origin` e `Referer` da
  publicacao.

## Endpoints

| Metodo | Caminho | Uso |
|---|---|---|
| GET | `{global}/user/profile/self` | perfil do usuario (traz `id`, `publicationUsers`) |
| GET | `{pub}/drafts?limit=&offset=` | lista rascunhos — a resposta e `{"posts": [...]}` |
| GET | `{pub}/drafts/{id}` | detalhe do rascunho (inclui `draft_body`) |
| POST | `{pub}/drafts` | **cria rascunho** |
| PUT | `{pub}/drafts/{id}` | atualiza rascunho (`draft_body`, titulo, subtitulo, `should_send_email`) |
| DELETE | `{pub}/drafts/{id}` | apaga rascunho (resposta `{}`) |
| GET | `{pub}/drafts/{id}/prepublish` | validacao no servidor (e **GET**, nao POST) |
| POST | `{pub}/drafts/{id}/publish` | publica (`send`, `share_automatically`) |
| POST | `{pub}/drafts/{id}/scheduled_release` | agenda (`trigger_at` ISO 8601) |
| DELETE | `{pub}/drafts/{id}/scheduled_release` | cancela agendamento |
| POST | `{pub}/image` | upload de imagem |
| GET/POST | `{pub}/publication/post-tag` | lista / cria tag |
| POST | `{pub}/post/{post_id}/tag/{tag_id}` | aplica tag |
| GET | `{pub}/post_management/published?limit=&offset=` | posts publicados (`{"posts": [...]}`) |
| GET | `{pub}/publication/users` | equipe da publicacao (bylines) |

### Detalhe que confunde: rascunho e sempre da publicacao

`POST https://substack.com/api/v1/drafts` (sem ser o host da publicacao) devolve
`403 Not authorized` mesmo com sessao valida — inclusive chamando de dentro da
pagina logada. Rascunho pertence a uma publicacao: use o host dela.

## Payload de criacao de rascunho

`POST {pub}/drafts`, JSON com **`draft_body` sendo uma string JSON** (o doc
ProseMirror serializado), nao um objeto:

```json
{
  "draft_title": "Titulo",
  "draft_subtitle": "Linha de apoio",
  "draft_body": "{\"type\":\"doc\",\"content\":[...]}",
  "draft_bylines": [{ "id": 534570112, "is_guest": false }],
  "audience": "everyone",
  "write_comment_permissions": "everyone",
  "draft_section_id": null,
  "section_chosen": true,
  "should_send_email": false
}
```

- `audience`: `everyone` | `only_paid` | `founding` | `only_free`
- `draft_bylines[].id`: o `user_id` do autor (vem de `user/profile/self`).
- `write_comment_permissions` costuma espelhar `audience`.
- `should_send_email: false` e o cinto de seguranca: o rascunho nasce web-only,
  mesmo se a publicacao for disparada pela interface depois. Para enviar e-mail,
  a ferramenta primeiro liga esse campo e so entao publica com `send: true`.

## Publicacao

```
POST {pub}/drafts/{id}/publish
{ "send": false, "share_automatically": false }
```

- `send: true` **dispara e-mail para toda a lista**. Por isso a ferramenta exige
  `--send-email`: publicar na web e enviar e-mail sao decisoes diferentes.
- A resposta traz o post criado (`canonical_url`, `id`).

## Agendamento

```
POST {pub}/drafts/{id}/scheduled_release
{ "trigger_at": "2026-09-20T12:00:00+00:00" }
```

`trigger_at` e convertido para UTC pela ferramenta.

## Upload de imagem

```
POST {pub}/image
Content-Type: application/x-www-form-urlencoded
image=data:image/png;base64,<base64>
```

Resposta validada ao vivo:

```json
{
  "id": 345196808,
  "url": "https://substack-post-media.s3.amazonaws.com/public/images/<uuid>_240x120.png",
  "contentType": "image/png",
  "bytes": 49537,
  "imageWidth": 240,
  "imageHeight": 120
}
```

Apos salvar, a Substack reescreve a URL para `substackcdn.com/image/fetch/...`
dentro do editor. Use a URL devolvida (`url`) no no `image2` do `draft_body`.

## Semantica de erro (importante para diagnosticar)

| Resposta | Significado | Acao |
|---|---|---|
| `403 Not authorized` | sessao invalida/expirada **ou** endpoint sem contexto de publicacao | renovar cookie; conferir se a URL e a da publicacao |
| `401 {"msg":"Please sign in"}` | alguns endpoints de leitura do leitor | renovar sessao |
| `404` com HTML | o caminho **nao existe** (mudou de nome) | revalidar no Network do editor |
| `429` | rate limit | repetir com calma |

Diferenca pratica: `403` = "existe, mas sem autorizacao"; `404` com HTML =
"esse endpoint nao existe mais".

## Publicacao existente mas ausente no perfil

`GET /api/v1/user/profile/self` pode devolver `publicationUsers: []` mesmo quando
a publicacao existe (foi o caso desta conta: `eolimabr.substack.com` apareceu
primeiro no editor, em `/publish/post`). Se `publications` vier vazio, abra o
menu **Create → Article** no navegador: a URL do editor revela o subdominio.


---
name: terras-substack
description: Publica, agenda e gerencia posts na Substack pela API interna do editor: rascunho, post, Note, agendamento, despublicar e envio de imagem. Use quando o pedido envolver Substack, newsletter, publicar ou agendar post, ou conferir rascunhos.
keywords: [substack, publicar, publish, newsletter, rascunho, draft, note, nota, agendar, schedule, unpublish, prosemirror, eolimabr]
---

# Publicar na Substack

## Objetivo

Levar um texto em markdown ate a Substack: converter para o formato do editor,
criar o rascunho, conferir, e publicar (web, e-mail, agendado) ou despublicar.
Vale tanto para posts longos quanto para Notes curtas.

## Onde está instalada

Fonte única: `skills/terras-substack/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Uso pelo terrasIA (MCP)

O repositorio terrasia (`~/assistente-os`) tem uma familia de tools MCP que
embrulha este CLI: `substack_status`, `substack_list_drafts`,
`substack_get_draft`, `substack_create_draft`, `substack_upload_image`,
`substack_publish`, `substack_schedule` e `substack_delete_post`. Os handlers
apenas spawnam este CLI — a logica de conversao e de API continua aqui, num
lugar so. Detalhes em `docs/specs/SPEC-SUBSTACK-001.md` do repositorio.

Para o daemon encontrar o CLI: `TERRAS_SUBSTACK_CLI` (default
`$SKILL_DIR/scripts/terras_substack.py`),
`TERRAS_SUBSTACK_PYTHON` (default `python3`) e `TERRAS_SUBSTACK_CONFIG`
(default `~/.config/terras-substack/config.json`).

## Regra de ouro (seguranca)

1. **Nunca publique sem confirmacao explicita do usuario.** O comando `publish`
   exige `--yes` justamente por isso. Post publico e ação externa: so execute
   quando o usuario pedir "publique".
2. **O e-mail nunca sai por acidente.** `publish` publica so na web; disparar
   e-mail para os assinantes exige `--send-email` explicito.
3. **Sempre criar rascunho primeiro** e mostrar o link do rascunho ao usuario.
4. Ao apagar ou despublicar, confirme antes (ambos exigem `--yes`).

## Pre-requisitos

A ferramenta e `scripts/terras_substack.py` (Python puro + `requests`, ja
instalado). A configuracao fica em `~/.config/terras-substack/config.json`:

```json
{
  "publication": "https://minhapublicacao.substack.com",
  "user_id": 123456,
  "cookies": { "substack.sid": "..." }
}
```

- `publication`: a URL da publicacao (nao e o perfil `substack.com/@usuario`).
- `user_id`: o id do usuario (usado nos bylines do post).
- `substack.sid`: cookie de sessao. Como obter esta em `references/credenciais.md`.

Antes de qualquer coisa, rode `check`. Ele diz o que falta:

```bash
python3 $SKILL_DIR/scripts/terras_substack.py check
```

### Estado desta maquina (2026-09-15)

Ja configurado e validado ao vivo:

- publicacao: `https://eolimabr.substack.com` (id 11119659, perfil `@eolimabr`)
- `user_id`: 534570112 (Everton Lima)
- cookie: importado do navegador embutido do ZCode; se expirar, reimporte com
  `chrome_cookie.py substack.com --profile ~/.config/ZCode --save-config --user-id 534570112`

Validado de ponta a ponta: upload de imagem, criacao de rascunho com tags,
leitura e remocao de rascunho, e o rascunho renderizado no editor (titulo,
subtitulo, negrito, heading, lista, citacao, imagem com legenda, paywall e bloco
de codigo). `publish` foi validado em 2026-09-17, publicando so na web (sem
`--send-email`) e conferindo a pagina renderizada no navegador. O que **nao** foi
exercitado ainda: `schedule` e `unpublish`, que sao acoes publicas e aguardam
pedido explicito.

Se `publications` voltar vazio mesmo com a publicacao existindo, abra o menu
**Create → Article** no navegador: a URL do editor revela o subdominio.

## Fluxo padrao

1. **Contexto**: confirme a publicacao alvo e o `user_id` com `whoami` /
   `publications`.
2. **Escrever**: salve o texto em `$posts_dir/drafts/<slug>.md` com frontmatter
   (`title`, `subtitle`, `audience`, `tags`) ou tenha o markdown em maos.
3. **Conferir a conversao** antes de subir:
   `md2json arq.md` mostra o doc ProseMirror e `payload arq.md` mostra os campos
   da requisicao, com o `draft_body` resumido (o doc completo sai ao lado, no
   campo `doc`). Use `--dry-run` para ver a chamada sem executar.
4. **Criar o rascunho**: `create-draft arq.md [--prepublish] [--tags a,b]`.
   Guarde o `draft_id` e mostre ao usuario o link
   `<publicacao>/publish/post/<draft_id>`.
5. **Revisar no editor** quando o usuario quiser (o rascunho pode ser aberto e
   editado normalmente no navegador).
6. **Publicar** somente sob pedido explicito:
   `publish <draft_id> --yes` (web) ou `publish <draft_id> --yes --send-email`
   (envia e-mail). Agendamento: `schedule <draft_id> --at 2026-09-20T09:00:00-03:00 --yes`.

Depois de publicar, mova o markdown de `drafts/` para `published/`.

## Formato do markdown aceito

Frontmatter opcional (YAML simples) + markdown com um subconjunto bem definido e
diretivas para os recursos nativos da Substack:

```markdown
---
title: Titulo do post
subtitle: Linha de apoio
audience: everyone      # everyone | only_paid | founding | only_free
tags: [ia, carreira]
---

Abertura com **gancho forte**.

![imagem](https://.../foto.png)
^ Legenda da imagem

::: paywall
::: subscribe Assine para receber os proximos
::: button Assinar agora | https://exemplo.com/assinar
::: pullquote ... :::   # citacao destacada
```

Detalhes de cada no e diretiva em `references/prosemirror.md`.

## Comandos

| Comando | Para que serve |
|---|---|
| `check` | valida config e sessao |
| `whoami` / `publications` | id do usuario, publicacoes vinculadas |
| `drafts` / `published` | lista rascunhos e posts no ar |
| `get-draft ID [--markdown]` | confere o que esta no rascunho |
| `md2json` / `payload` / `browser-payload` | conversao e inspecao (offline) |
| `create-draft` / `update-draft` | cria e atualiza rascunho |
| `prepublish` | validacao no servidor antes de publicar |
| `publish --yes [--send-email]` | publica |
| `schedule --at ISO --yes` / `unschedule` | agenda e cancela |
| `unpublish --yes` / `delete-draft --yes` | tira do ar / apaga rascunho |
| `upload-image caminho` | sobe imagem, devolve a URL |
| `tags` / `set-tags ID nome...` | tags da publicacao |

Toda escrita aceita `--dry-run` (mostra a requisicao e nao executa). Em
`set-tags` a simulacao nao consulta as tags existentes: a URL sai com
`<id-da-tag:nome>` no lugar do id, e uma tag nova seria criada antes de ser
presa ao post.

A imagem do post (capa e og:image) sai da skill `terras-banner`: gerar o PNG em
1200x628, subir com `upload-image` e inserir `![alt](url)` como primeiro no do
corpo, logo depois do frontmatter, porque o primeiro no e o que a Substack usa
como og:image. Banner de digest publicado sai nos dois idiomas, um por post.

## Digest / recap da semana

Digest tambem pode ser longo na Substack. Nao resumir a forca para caber num tamanho arbitrario quando o valor estiver no mapa da semana, nos links entre textos e no agrupamento por tema.

Quando houver digest nas duas plataformas:

- o LinkedIn pode sair em versao longa, desde que abra forte e leia bem em diagonal;
- a Substack aprofunda com links para os posts publicados, agrupamento por tema e pergunta final apontando o proximo aprofundamento.

## Rota alternativa: publicar pelo navegador

Quando nao houver cookie valido, quando a API interna mudar, ou quando o
recurso nao existir na API (editor visual, Notes, capa do post, controle de quem
recebe e-mail), publique pela aba logada do navegador: `browser-payload arq.md`
imprime o JavaScript pronto para rodar na pagina com a sessao do usuario
(`fetch` com `credentials: "include"`). O roteiro completo esta em
`references/rota-navegador.md`.

Notes (posts curtos) **nao** passam pela API interna: saem pelo menu
**Create → Note** na interface, e publicam na hora (nao existe rascunho de
Note). Confirme com o usuario antes, porque nao ha como desfazer sem apagar.

## Pastas de trabalho

`$posts_dir` (padrao `~/Documents/Diversos/substack/`):

```
substack/
├── drafts/      # markdown em producao
├── published/   # markdown ja publicado
└── imagens/     # imagens antes do upload
```

Ha um exemplo completo em `drafts/exemplo-post.md`.

Trabalhando dentro de outro projeto (por exemplo o terrasia, em `~/assistente-os`),
aponte `posts_dir` para onde o conteudo daquele projeto vive:

```bash
SUBSTACK_POSTS_DIR=~/assistente-os/content/posts python3 .../terras_substack.py create-draft ...
```

## Integracao com o pipeline editorial

A skill `editorial-vertical` gera drafts multi-plataforma em
`souls/{soul}/editorial/drafts/draft-substack-*.md`. Esses arquivos ja saem no
formato aceito aqui (frontmatter + markdown) e podem ir direto para o
`create-draft`; para os recursos nativos, use as diretivas `::: paywall`,
`::: subscribe` e `::: button` descritas em `references/prosemirror.md`.

## Limitacoes conhecidas

- Nao existe API publica de escrita na Substack: os endpoints sao os internos do
  editor e podem mudar sem aviso. Se algo parar de funcionar, valide no navegador
  logado (aba Network) antes de culpar o cookie.
- O cookie `substack.sid` expira. Sintoma: HTTP 403 `Not authorized`.
- Rascunho e sempre de uma publicacao: chamar `POST substack.com/api/v1/drafts`
  (sem ser o host da publicacao) devolve 403 mesmo com sessao valida.
- `drafts` devolve `{"posts": [...]}`; `get-draft` traz o corpo em `draft_body`
  como string JSON (a ferramenta ja converte).
- Notes (posts curtos) e alguns recursos ricos nao estao cobertos pela API
  interna: use a rota de navegador.
- A conversao de markdown cobre os nos listados em `references/prosemirror.md`.
  Nos nao reconhecidos viram comentario `<!-- no nao convertido: X -->` na
  conversao reversa, para nao sumirem em silencio.
- `publish` foi exercitado em 2026-09-17 (na web, sem `--send-email`, com a
  pagina conferida no navegador depois). Mantenha o roteiro: `prepublish` antes,
  `publish --yes` sem `--send-email`.
- `published` exige `order_by` e `order_direction` na query; sem eles a API
  responde 400 `Invalid value`. O CLI ja manda `order_by=post_date` e
  `order_direction=desc` desde 2026-09-17.

## Exemplos de uso

- "Escreve um post sobre X e deixa como rascunho no meu Substack"
- "Publica o rascunho 12345 so na web, sem mandar e-mail"
- "Confere o que tem no rascunho 12345 e me mostra em markdown"
- "Agenda o post 12345 para segunda 9h"
- "Sobe essa imagem e coloca no topo do post"
- "Tira do ar o post 12345"

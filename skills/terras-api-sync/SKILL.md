---
name: terras-api-sync
description: Mantém o contrato público do motor terrasia síncrono: daemon + SDK @terrasia/client (client.ts e stream.ts) + README "Contrato da API" no mesmo commit. Use ao criar/alterar rota, payload, evento SSE ou status HTTP. Depois rode npm run build e typecheck+test do client.
keywords: [mudar rota, novo endpoint, alterar API, contrato, SDK, client, README]
---

---

# Sincronia do Contrato da API — terrasia

Garante que `@terrasia/client` e `README.md` evoluam **junto** com as rotas do daemon, não depois.

## Arquitetura do polyrepo

```
terrasia (motor)          terrasia-admin           terrasia-client
├── packages/daemon       ├── consome              ├── consome
│   └── rotas HTTP        │   @terrasia/client     │   @terrasia/client
│                         │   (file:../terrasia/   │   (file:../terrasia/
│                         │    packages/client)    │    packages/client)
│                         │                        │
└── packages/client  ◄───┘                        ┘
    @terrasia/client
    (SDK tipado)
```

## Regra de ouro

> **Toda mudança no contrato público/compartilhado da API (rota nova, parâmetro novo, response alterado, evento SSE ou status code alterado) → 3 updates atômicos no mesmo commit:**
> 1. **Daemon** (`packages/daemon/src/...`) — implementação da rota
> 2. **SDK** (`packages/client/src/**`) — tipagem + método correspondente; inclui `client.ts` e `stream.ts` (`StreamEvent`, ex.: `callId`), não só o `client.ts`
> 3. **Docs** (`README.md` seção "Contrato da API") — documentação humana

## Checklist ao alterar rota

| Mudança no daemon | Atualizar no `@terrasia/client` | Atualizar no `README.md` |
|-------------------|--------------------------------|--------------------------|
| Nova rota `GET /souls/:soul/threads` | Adicionar `listThreads(soul: string)` tipado | Adicionar linha na tabela "API Contract" |
| Novo parâmetro `?limit=20` | Adicionar `limit?: number` no método | Documentar query param |
| Response muda shape (`id` → `threadId`) | Atualizar interface `Thread` | Atualizar exemplo de response |
| Novo evento SSE / campo no frame (`done` ganha `sources`) | Atualizar `StreamEvent` em `stream.ts` + testes do SDK (`stream.test.ts`) | Documentar frame na seção SSE |
| Novo status `422` (validation error) | Adicionar no `throws` / tipo erro | Documentar caso de erro |
| Rota deprecada/removida | Marcar `@deprecated` ou remover | Marcar como deprecated ou remover |

## Fluxo prático

```
1. Edita daemon (rota nova/alterada)
2. Rode: npm run build   # compila kernel → daemon
3. Rode: npm --workspace @terrasia/client typecheck && npm --workspace @terrasia/client test
4. Edita `packages/client/src/**` (client.ts e, se tocar SSE, stream.ts) e roda os testes do SDK (mesmo commit)
5. Edita README.md seção "Contrato da API" (mesmo commit)
6. Commit único: "feat: nova rota X + SDK + docs"
```

## Validação automática (já existe no repo)

- `npm run build` compila somente kernel e daemon; o client tem seus próprios comandos `typecheck` e `test`
- `scripts/verify-all.sh` roda build + testes de todos os pacotes
- `terras-validacao` exige `.http`/`api-smoke-test.sh` exercitando a rota real

## Exemplo de uso

```
> terras-api-sync: vou adicionar PATCH /souls/:soul/threads/:id (renomear thread)
> → Checklist:
>   1. Daemon: route handler + validation
>   2. Client: renameThread(soul, id, title) → Thread
>   3. README: adicionar na tabela + exemplo request/response
>   4. requests.http: adicionar request encadeado (cria thread → renomeia)
>   5. api-smoke-test.sh: adicionar step correspondente
```

## Integração com outras skills

- `terras-boundary` — primeiro confirma se a rota **pertence ao motor** (não admin/client)
- `terras-validacao` — exige artefato de validação (`.http` + `api-smoke-test.sh`) no mesmo PR
- `terras-drift` — checa se `README.md` (contrato) está sincronizado com código real
- `terras-reconstrucao` — ordem de construção: motor (daemon+client) antes de admin/client

## Armadilhas comuns

| Armadilha | Prevenção |
|-----------|-----------|
| Esquecer `packages/client` → build do daemon passa, mas admin/client quebram em runtime | Rodar explicitamente `npm --workspace @terrasia/client typecheck && npm --workspace @terrasia/client test` |
| Atualizar `README.md` mas não o SDK (ou só `client.ts`, esquecendo `stream.ts`) | Checklist acima + commit atômico único |
| Mudar só response shape, não request → SDK compila mas runtime falha | Testes de contrato em `api-smoke-test.sh` pegam |
| Adicionar rota admin no motor (violando `terras-boundary`) | `terras-boundary` roda antes — bloqueia na origem |

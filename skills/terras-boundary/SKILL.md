---
name: terras-boundary
description: Decide onde colocar rota/feature nova: domínio, policy e API segura no motor terrasia; telas/rotas de superfície em terrasia-admin/terrasia-client. Área cinzenta → ADR (terras-adr). Use antes de codificar endpoint/UI.
keywords: [onde vai, nova rota, endpoint, feature, admin, cliente, UI, motor]
---

---

# Fronteira Motor vs Admin/Cliente — terrasia

Garante que toda rota/feature nova seja colocada no repositório correto desde o desenho, não descoberta tardiamente em code review.

## Regra do projeto (CLAUDE.md)

> **Não misturar UI, páginas ou rotas de superfície específicas de admin ou de cliente final aqui — isso é `terrasia-admin` / `terrasia-client`. Este repo é o motor.**

Isso não transforma automaticamente uma operação de domínio em código de
frontend. O motor continua dono de persistência, regras, autorização,
auditoria e da API segura que uma ou ambas as superfícies consomem.

## O que o monólito antigo fez (errado)

`packages/daemon` embutia:
- **Admin-only**: `routes/friendlyAdmin.ts`, `adminApiKeys.ts`, `adminOps.ts`, `adminPlans.ts`, `monitors.ts`, `infra.ts`, rota `mcp.ts` admin-gated (~500 LOC) + `web/index.html` (HUD, ~3.8k LOC estático)
- **Cliente-final-only**: `accountAuth.ts`, `accountSouls.ts` (~480 LOC) + `web/friendly.html` (~850 LOC)
- **Terceiro eixo (nem admin nem cliente)**: WhatsApp/Telegram (~1.1k LOC)
- **Compartilhado pelas 3 superfícies**: `stream.ts`/`chat.ts` (API REST+SSE → virou `@terrasia/client`)

## Checklist antes de criar rota/feature

| Pergunta | Se SIM → | Se NÃO → |
|----------|----------|----------|
| É API de domínio segura, persistência, policy ou integração consumida por SDK/superfície? | **Motor (terrasia)** — contrato em `packages/daemon/src/` | Continua |
| É página, componente, fluxo visual ou rota de UI de painel/admin? | **terrasia-admin** — não criar aqui | Continua |
| É página, componente, fluxo visual ou rota de UI do usuário final? | **terrasia-client** — não criar aqui | Continua |
| É endpoint exclusivo de uma superfície, mas com regra/autorização de domínio? | **Área cinzenta:** motor guarda a regra; criar ADR para decidir o adaptador/BFF | Continua |
| É canal/integração (WhatsApp, Telegram, ADO)? | **Motor** — mas em `packages/integrations/` (futuro), não no daemon | Continua |
| É infra/observabilidade interna (health, metrics, logs)? | **Motor** — `packages/kernel` ou `daemon` interno | — |

## Casos fronteiriços (usar julgamento + registrar ADR se dúvida)

| Área | Onde fica | Raciocínio |
|------|-----------|------------|
| `GET /health` / `GET /ready` | Motor (daemon) | Infra interna, não é UI admin |
| `POST /webhooks/*` (receber eventos externos) | Motor (daemon) | Parte do contrato da API pública |
| Tela admin de *souls* (criar/listar/configurar) | **terrasia-admin** | É superfície administrativa |
| Operação de domínio de *souls* chamada pela tela admin | **Motor, salvo ADR** | Ownership, policy e persistência não devem migrar para a UI |
| Métricas de uso/custos por soul | Motor (kernel/daemon) | Dados brutos; UI de visualização = admin |
| Prompt injection detection config | Motor (security) | Regra de negócio do motor; UI de config = admin |

## Como usar

1. **Antes de codificar** uma rota/endpoint/feature nova, pergunte: "Onde isso vai?"
2. **Aplique o checklist** acima
3. **Se cair em área cinzenta** → crie ADR leve (`terras-adr`) registrando a decisão
4. **Se alguém propor rota admin/cliente aqui** → aponte para esta skill + `CLAUDE.md`

## Exemplo de uso

```
> terras-boundary: vou adicionar tela admin para criar souls
> → terrasia-admin. A operação segura de criação/configuração da soul continua
> no motor; se o endpoint é exclusivo do painel, registre ADR para definir o
> contrato e o adaptador sem deslocar policy/persistência para a UI.

> terras-boundary: novo endpoint GET /metrics/usage por soul
> → MOTOR (kernel/daemon). Dado bruto. UI de gráfico = terrasia-admin.
```

## Integração com outras skills

- `terras-reconstrucao` — ordem de construção (motor primeiro, admin/client depois)
- `terras-adr` — registrar decisão quando checklist não é claro
- `terras-api-sync` — se for no motor, lembrar de sincronizar `@terrasia/client` + `README.md`

---
name: terras-boundary
version: 1.0.0
access: free
category: operacao
description: Decide onde colocar rota ou feature nova — núcleo/backend (domínio, regras, persistência, autorização) ou superfície (painel admin, app cliente). Área cinzenta vira decisão registrada.
keywords: [onde coloco essa rota, onde vai essa feature, backend ou frontend, fronteira de repositorio]
---

# Fronteira núcleo × superfície

## Descrição

Garante que toda rota/feature nova seja colocada no lugar certo **desde o desenho**, não descoberta tardiamente em revisão. O erro clássico é o núcleo (backend) embutir tela de painel ou app de cliente final, e com o tempo virar um monólito que ninguém consegue separar.

O núcleo continua dono de persistência, regras, autorização, auditoria e da API segura que as superfícies consomem. O que não pode é UI, página ou rota de superfície morar no núcleo.

## Quando usar

- Antes de codificar qualquer rota, endpoint ou feature nova: pergunte "onde isso vai?"
- Quando alguém propõe tela de painel ou de cliente dentro do backend.
- Área cinzenta (endpoint exclusivo de uma superfície, mas com regra de domínio) — a decisão vira ADR registrado.

## Como funciona

### Checklist antes de criar rota/feature

| Pergunta | Se SIM | Se NÃO |
|---|---|---|
| É API de domínio segura, persistência, regra ou autorização consumida por SDK/superfície? | **Núcleo/backend** | Continua |
| É página, componente, fluxo visual ou rota de UI de painel administrativo? | **App de admin** — não criar no núcleo | Continua |
| É página, componente, fluxo visual ou rota de UI do usuário final? | **App cliente** — não criar no núcleo | Continua |
| É endpoint exclusivo de uma superfície, mas com regra/autorização de domínio? | **Área cinzenta** — o núcleo guarda a regra; registrar ADR para decidir o adaptador | Continua |
| É canal/integração (mensageria, CI externo)? | **Núcleo**, mas em módulo de integração separado, não no corpo do servidor | Continua |
| É infra/observabilidade interna (health, métricas, logs)? | **Núcleo** — módulo interno | — |

### Casos fronteiriços

| Área | Onde fica | Raciocínio |
|---|---|---|
| `GET /health` | Núcleo | Infra interna, não é UI |
| `POST /webhooks/*` (receber eventos externos) | Núcleo | Parte do contrato da API pública |
| Tela de admin para gerenciar entidades | **App de admin** | É superfície administrativa |
| Operação de domínio chamada pela tela de admin | **Núcleo, salvo ADR** | Propriedade, regra e persistência não migram para a UI |
| Métricas de uso/custo por entidade | Núcleo (dados brutos) | UI de visualização = admin |
| Configuração de regra de segurança | Núcleo (a regra) | UI de config = admin |

### Passo a passo

1. Antes de codificar, pergunte: "Onde isso vai?"
2. Aplique o checklist.
3. Área cinzenta → registre um ADR com a decisão.
4. Proposta de rota de superfície no núcleo → aponte para esta regra antes de codar.

## Governança

- Regra e persistência de domínio **não migram** para a UI, mesmo quando o endpoint é exclusivo dela — a UI vira cliente, o núcleo continua dono.
- Fronteira errada descoberta em revisão custa retrabalho; fronteira decidida antes de codar custa um minuto.

## Critério de qualidade

A decisão está fechada quando: o local da feature está decidido e justificado antes da primeira linha de código, e área cinzenta tem ADR registrado com a justificativa de por que a regra ficou onde ficou.

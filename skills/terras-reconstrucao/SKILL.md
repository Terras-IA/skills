---
name: terras-reconstrucao
description: Checklist para começar módulo novo da reconstrução do terrasia: ordem de construção, ler docs/subsistemas, reescrever vs. reaproveitar pela lista explícita, redação exata via docs/referencia-verbatim. Guia de onde procurar, não fonte da verdade.
keywords: [reconstrução, módulo novo, ordem de construção, router, skills, governança, souls, memory, costs, integrations, security]
---

---

# Reconstrução módulo a módulo — terrasia

terrasia reimplementa deliberadamente o `assistente-os` antigo — não porta,
não copia por padrão. O conhecimento real do monólito (decisões de schema,
acoplamento testado em produção, fronteiras que já se provaram certas ou
erradas) está documentado permanentemente dentro do próprio repo, nunca na
memória de conversas anteriores nem no plano efêmero fora do git.

Esta skill **não é a fonte da verdade** — é um checklist de onde procurar
antes de escrever código novo de um módulo. O conteúdo real vive em
`docs/CONHECIMENTO-DO-MONOLITO.md`, `docs/subsistemas/` e
`docs/referencia-verbatim/`, e pode mudar — releia a fonte a cada módulo em
vez de confiar num resumo memorizado.

## Antes de começar um módulo

1. **Confirme onde esse módulo está na ordem de construção.** Releia a
   seção "Ordem de construção módulo por módulo" em
   `docs/CONHECIMENTO-DO-MONOLITO.md` — a ordem segue lógica de
   risco/dependência (isolado primeiro, acoplado depois). Não é bloqueante,
   mas mudar a ordem precisa de motivo concreto, não só preferência do
   momento.

2. **Leia o subsistema correspondente antes do inventário estrutural.** Os
   4 docs em `docs/subsistemas/` carregam o comportamento real (algoritmos,
   bugs de produção já corrigidos e por quê) que a tabela de LOC/acoplamento
   de `CONHECIMENTO-DO-MONOLITO.md` não cobre. Mapeamento aproximado —
   confirme sempre no índice do doc, porque nem todo módulo tem
   correspondência 1:1:
   - souls + policy + governança, router/tiers, skills →
     `ROUTER-GOVERNANCA-SKILLS-SOULS.md`
   - memory (RAG + grafo de conhecimento + LangGraph agent workflow) →
     `RAG-E-GRAFO.md`
   - daemon completo (orchestrator, MCP, canais) e integrations
     WhatsApp/Telegram → `MCP-MULTITENANT-CANAIS.md` (ADO não tem
     subsistema dedicado — era só 51 LOC no antigo, outlier isolado)
   - costs/billing → `CUSTOS-CLI-VOZ-OBSERVABILIDADE.md`
   - security, prompts → sem subsistema dedicado. Security já tem spec
     própria registrada neste repo — procure docs/commits existentes antes
     de escrever do zero. Prompts → os 12 prompts do Prompt Garden estão
     verbatim em `docs/referencia-verbatim/`.

   Se o módulo não aparecer nessa lista ou parecer ter mudado de lugar,
   confie no doc real — esta tabela é só um atalho, não a fonte.

3. **Decida reescrever vs. reaproveitar pela lista explícita, não por
   intuição.** Releia "O que reescrever vs. o que reaproveitar quase
   verbatim" em `CONHECIMENTO-DO-MONOLITO.md`, reforçada no `CLAUDE.md`
   §"Não fazer". Só copiar/adaptar verbatim o que estiver **explicitamente**
   listado ali como seguro — não confie numa cópia inline nem em memória:
   a lista cresce a cada módulo (ex.: `security/*` entrou na entrega do
   módulo security). Caso fora da lista: esta skill **não decide** — o
   default é não copiar; abra um ADR via `terras-adr` e decida lá
   (reescrever, reaproveitar adaptado ou verbatim) antes de codificar.

4. **Pra redação exata, use `docs/referencia-verbatim/`, não memória.**
   Prompts, regex de segurança, DDL de migrations, catálogo de rotas REST —
   onde a redação literal importa, esse diretório tem cópia fiel do
   original. Ver o `README.md` de lá pro que está incluído vs. só
   documentado em comportamento (o kernel MCP inteiro, por exemplo, ficou
   só documentado, é grande demais pra copiar).

5. **Se o módulo tocar `core` ou `memory` — em especial o cluster
   souls+policy+governança — confira se `deps-zones.mjs` está cobrindo os
   pacotes novos.** A regra "core nunca importa memory" (zero violações
   verificadas por grep no repo antigo) já foi portada pra
   `scripts/deps-zones.mjs` (roda via `npm run verify:deps-zones`): quando
   um módulo novo criar pacotes, adicione as zonas/allowlists dele lá
   cedo, pra pegar acoplamento indevido em vez de descobrir depois de já
   estar emaranhado.

6. **Ao entregar, siga a regra de validação do `CLAUDE.md`.** Todo
   endpoint, script ou mudança de comportamento observável precisa vir com
   um `.http` ou script (`curl`/shell) que exercita a implementação ponta a
   ponta, além dos testes automatizados — não é opcional nem substituível
   só por unit tests.

## Fora do escopo desta skill

- Ela não decide por você o que reescrever/reaproveitar quando o caso não
  está explicitamente listado no doc — isso é uma decisão de design nova;
  documente-a em `CONHECIMENTO-DO-MONOLITO.md` depois de decidida, em vez
  de deixá-la implícita só no código.
- Ela não substitui a leitura dos documentos reais — é um checklist de
  navegação, não um cache do conteúdo deles.

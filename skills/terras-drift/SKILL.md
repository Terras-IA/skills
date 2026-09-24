---
name: terras-drift
version: 1.0.0
access: free
category: operacao
description: Audita drift entre documentação viva e código real, por evidência — classifica a fonte, extrai afirmações verificáveis e reporta PASS, FAIL, UNVERIFIABLE ou PLANNED citando arquivo e linha.
keywords: [docs desatualizados, desatualizados, drift, spec vs codigo, conformidade docs]
---

# Auditoria de drift — documentação × código

## Descrição

Audita se a documentação viva do projeto ainda corresponde ao código real, por evidência (leitura e busca, nunca suposição), e reporta cada divergência citando arquivo e linha. O ponto central é separar as classes de documento: contrato vivo (tem que bater com o código de hoje) e referência histórica (descreve o sistema antigo e não é falha por ainda não existir no novo).

## Quando usar

- Entrega de módulo novo ou mudança de fronteira entre camadas.
- Usuário pergunta "tem drift?" ou "os docs estão atualizados?"
- Antes de fechar entrega que alterou contrato, schema ou fronteira.
- PR que muda o que a documentação promete.

## Como funciona

### Metodologia

1. **Classificar a fonte.** Contrato vivo (API documentada, SDK, exemplos executáveis), plano/spec (entregue vs. aprovada-mas-não-entregue) ou referência histórica.
2. **Extrair afirmações verificáveis** apenas de contratos vivos e decisões já implementadas. Item de spec aprovada mas ainda não entregue é **PLANNED**, não FAIL.
3. **Consultar o código real** — abrir arquivos, não assumir.
4. **Comparar** cada afirmação: `PASS`, `FAIL`, `UNVERIFIABLE` (nenhum artefato exercita) ou `PLANNED` (trabalho futuro documentado).
5. **Reportar** resumo, escopo auditado e os drifts com arquivo e linha, e a evidência.

### Saída esperada

```
## Drift Report — AAAA-MM-DD

### Contrato público atual
✅ PASS: a documentação descreve a rota e o servidor/SDK expõem o mesmo payload
❌ FAIL: o evento de stream ganhou um campo novo, mas a SDK não tipa o campo
⚠️ UNVERIFIABLE: nenhum request manual exercita a nova política de retenção

### Referência histórica
ℹ️ REFERÊNCIA: doc do sistema antigo descreve capacidade que o novo ainda não tem — não é drift

### Specs/planos
📋 PLANNED: itens aprovados mas ainda não entregues — trabalho futuro, não falha de código
```

### Limites

- Não checa testes, cobertura nem performance — só conformidade docs × código.
- Não decide *como* corrigir — só aponta o drift com evidência.
- Não classifica backlog, hipótese de produto nem spec aprovada-mas-não-entregue como FAIL — esses casos são PLANNED.
- Cópia literal de referência só é atualizada a partir da fonte original, após decisão explícita de renovar.

## Governança

- Documentação viva que contradiz o código é mais perigosa que documentação ausente: quem lê confia e decide errado. O drift reportado entra no checklist de fechamento da entrega que o causou.
- Nunca "corrigir" a documentação para bater com o código sem confirmar qual dos dois está certo — drift é sintoma de uma decisão que não foi registrada.

## Critério de qualidade

O relatório está pronto quando cada afirmação verificada tem veredito com evidência (arquivo e linha, dos dois lados), o escopo auditado está declarado, e nenhuma spec não entregue foi marcada como falha de código.

---
name: terras-adr
version: 1.0.0
access: free
category: operacao
description: Registra decisão de reescrever vs reaproveitar quando o caso não está numa lista canônica — ADR leve com contexto, decisão, alternativas, consequências e rastreabilidade.
keywords: [adr, registrar decisao de design, reescrever ou reaproveitar, decisao arquitetural]
---

# ADR leve — reescrever vs reaproveitar

## Descrição

Registra uma decisão de design em documento curto (ADR — Architecture Decision Record) quando o caso **não está coberto por lista canônica** do projeto. A lista diz o que é seguro reaproveitar quase como está e o que é reescrita deliberada; caso fora dela, a decisão precisa ser tomada, registrada e rastreável.

## Quando usar

- O caso não está em nenhuma das listas explícitas do projeto (o que reaproveitar / o que reescrever).
- Típico: um módulo, arquivo ou subsistema legado que não é nem claramente reescrita nem claramente reaproveitável.
- Sempre **antes de codificar** — decidir no meio da implementação é o sintoma de que este passo foi pulado.

## Como funciona

### Passo a passo

1. **Identificar** que o caso não está nas listas explícitas. Releia a lista canônica do projeto — não confie em memória, a lista cresce a cada módulo.
2. **Criar o ADR** seguindo o formato abaixo (rascunho rápido serve).
3. **Decidir** — uma das três opções, com justificativa.
4. **Registrar** no diretório de decisões do projeto (criar se não existe).
5. **Propagar minimamente** — o ADR é a fonte da decisão; atualizar a lista canônica só se o caso virar regra recorrente. Não reescrever documento histórico para registrar decisão pontual.

### Formato do ADR (arquivo: `AAAA-MM-DD-<slug>.md`)

```markdown
# ADR: <título curto> — reescrever vs reaproveitar <área>

## Contexto
O que está em jogo: o módulo/arquivo, o que ele faz, por que a decisão não é óbvia pelas listas canônicas.

## Decisão
- [ ] **Reescrever do zero** — motivo: <ex: acoplamento oculto, decisões ad-hoc, fronteira errada>
- [ ] **Reaproveitar com adaptações** — o que muda: <ex: remover dependência X, ajustar interface Y>
- [ ] **Reaproveitar como está** — justificativa: <ex: zero acoplamento, já validado em produção, igual ao item Z da lista>

## Alternativas consideradas
Breve: o que mais foi avaliado e por que descartado.

## Consequências
- Positivas: <ex: fronteira limpa, teste isolado>
- Negativas/Riscos: <ex: mais trabalho agora, duplicação temporária>
- Mitigação: <ex: portar o gate de dependências antes, testar contra ambiente isolado>

## Rastreabilidade
- Origem: <caminho/módulo no sistema antigo>
- Destino: <onde vai entrar>
- Relacionado: <outro ADR ou item da lista explícita>
```

## Governança

- ADR não é reunião: é decisão escrita. Decisão não documentada é decisão que será refeita (mal) daqui a seis meses.
- O custo de um ADR leve (minutos) é muito menor que o custo do retrabalho por decisão implícita perdida.
- Propagação é mínima de propósito: o ADR fica sendo a fonte; a lista canônica só muda quando o caso vira padrão.

## Critério de qualidade

O ADR está pronto quando alguém que não participou da decisão consegue, lendo só o documento, dizer o que foi decidido, por quê, o que foi considerado e o que custa — e encontrar o código correspondente pela rastreabilidade.

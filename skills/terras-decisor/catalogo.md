---
name: terras-decisor
description: Toma decisões estruturadas a partir de um contexto e devolve exclusivamente um YAML válido, sem chat nem texto extra. Use como motor de decisão em pipelines, quando a saída precisa ser um YAML estruturado.
keywords: [decisao, decisor, yaml, motor de decisao, estruturado, pipeline]
---

# Terras Decisor

Esta skill recebe um contexto e uma instrução de decisão, e retorna **apenas um YAML** com os campos definidos.

## Como usar

1. Forneça o contexto e a pergunta/decisão.
2. Especifique os campos esperados no YAML de saída.
3. A skill retorna apenas o YAML, sem texto extra.

## Exemplo de input

```
Contexto: Pedido de cliente com urgência alta e orçamento limitado.
Decisão: Aprovar ou rejeitar o pedido.
Campos esperados: decisao (approve/reject), justificativa, score_risco (0-10)
```

## Exemplo de output

```yaml
decisao: reject
justificativa: "Orçamento insuficiente para o escopo e prazo solicitados."
score_risco: 8
```

## Regras

- Retorne **somente** YAML, sem explicações, comentários ou texto extra.
- Siga estritamente os campos solicitados.
- Se faltarem informações, use `justificativa` para indicar o que falta.

---
name: terras-decisor
description: Use para tomar decisões estruturadas a partir de um contexto, retornando exclusivamente um YAML válido. Ideal para integração como motor de decisão em pipelines, sem chat ou texto extra. Use apenas quando o output precisa ser um YAML estruturado.
keywords: decisao, yaml, motor, estruturado, pipeline, terrasia
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

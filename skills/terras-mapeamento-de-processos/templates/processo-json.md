# Schema do `processo.json`

Use este formato quando não houver LLM de linha de comando disponível: escreva o JSON à mão a partir do relato. O `gerar_mermaid.py` e o `metricas.py` dependem exatamente destas chaves.

```json
{
  "processo": "Atendimento de chamados",
  "objetivo": "o que o processo entrega",
  "gatilho": "o que dispara o processo",
  "fim": "o que caracteriza o encerramento",
  "volume_mensal": "180 (ou 'não informado')",
  "atores": ["Atendente", "Técnico"],
  "sistemas": ["ERP", "WhatsApp"],
  "passos": [
    {
      "id": "P1",
      "nome": "Verbo + objeto",
      "ator": "Atendente",
      "tipo": "tarefa",
      "sistema": ["ERP"],
      "entradas": ["chamado"],
      "saidas": ["OS aberta"],
      "tempo_execucao_min": 10,
      "tempo_espera_min": null,
      "frequencia": "sempre",
      "excecoes": ["cadastro divergente: volta para correção"],
      "evidencia": "[00:02:45] trecho que sustenta este passo",
      "confianca": "alta"
    }
  ],
  "lacunas": ["o que falta para fechar o diagnóstico"]
}
```

## Regras do preenchimento

- `tipo`: `tarefa` (trabalho manual) · `decisao` (escolha) · `espera` (fila) · `sistema` (ação automática) · `documento` (emissão/recebimento) · `aprovacao` (autorização).
- `tempo_execucao_min` e `tempo_espera_min` em minutos: 1 dia útil = 480 · 1 semana = 2400 · 1 hora = 60. Nada informado = `null` (nunca zero, nunca inventado).
- `ator` é papel/função, jamais nome de pessoa.
- `evidencia` é obrigatória em todo passo: timestamp ou trecho literal. Sem evidência, o passo não existe — a dúvida vai para `lacunas`.
- `id` sequencial (P1, P2, ...) **na ordem do caminho principal** (o caso mais comum). Caminho alternativo, urgente ou raro não vira passo: entra em `excecoes` do passo de decisão.
- `sistema`: sempre o mesmo nome curto para o mesmo sistema ("ERP", nunca "ERP (consulta)" e "ERP (export)").
- `confianca`: `alta` (dito explicitamente) · `media` (inferido do contexto) · `baixa` (estimativa com tempo ausente).
- O `processo-to-be.json` usa o mesmo schema; ali o `evidencia` aponta a melhoria que originou o passo.
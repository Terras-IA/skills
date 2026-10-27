---
name: terras-ishikawa-5porques
description: "Análise de causa raiz com Ishikawa (6M) e 5 porquês: efeito medido, causas como hipóteses com teste, porquês só nas mais prováveis e parada que não culpa pessoa. Use para causa raiz, Ishikawa, espinha de peixe, 5 porquês ou 'por que isso continua acontecendo'. Root cause analysis."
keywords: [ishikawa, espinha de peixe, diagrama de causa e efeito, 6m, 5 porques, cinco porques, causa raiz, root cause, analise de causa, masp, problema recorrente, nao conformidade, fishbone]
version: 1.0.0
license: MIT
---

# Ishikawa e 5 porquês

## Objetivo

Achar a causa sobre a qual dá para agir e que, removida, impede o problema de voltar. O Ishikawa abre o leque de hipóteses; os 5 porquês aprofundam só as poucas que os dados apontam.

O erro que esta skill fecha: espinha de peixe preenchida com causas plausíveis tiradas da cabeça e apresentadas como fato, uma corrente de porquês inventada até chegar numa "causa raiz" que soa bem, e ações que atacam causa que ninguém comprovou.

## Regra dura

1. **Efeito medido.** A cabeça do peixe tem número, período e meta: "reabertura de chamados 18% em set/26 (meta 5%)". Sem número → `[A CONFIRMAR]` e a primeira ação é medir.
2. **Toda causa no diagrama é hipótese** até ter evidência. Marque cada uma: `verificada (fonte)`, `provável (indício)` ou `hipótese`. Sem dado do usuário, todas são `hipótese`, e o texto diz isso.
3. **Cada hipótese escolhida tem um teste**: que dado, amostra ou observação a confirma ou derruba, e quanto custa olhar.
4. **5 porquês só nas 2-3 causas mais prováveis**, e cada resposta precisa ser verificável. Quando a resposta for chute, pare e marque o porquê como lacuna; não invente o elo seguinte.
5. **Não pare em pessoa.** "Erro humano", "falta de atenção", "fulano errou", "falta de treinamento" não são causa raiz: pergunte por que o sistema permitiu. Não cite nome de pessoa na análise.
6. **Critério de parada:** a causa está sob controle de quem vai agir e, removida, o efeito não volta. Se a causa estiver fora do alcance (lei, cliente, fornecedor), registre e volte um nível para o que dá para controlar.

## Como trabalhar

1. **Defina o efeito** (regra 1) e o recorte: período, área, produto.
2. **Abra o leque com o 6M**: Método, Máquina (sistemas e ferramentas), Mão de obra (papéis, carga, incentivos), Material (insumo e informação de entrada), Medida (como se mede e o que a meta incentiva), Meio ambiente (contexto, demanda, outras áreas). Em serviço, renomear as categorias é permitido; deixar categoria vazia também — é sinal, não falha.
3. **Marque cada causa** (regra 2) e escolha as 2-3 mais prováveis pelo que os dados mostram. Sem dados, escolha pelo teste mais barato e diga isso.
4. **Teste antes de agir** (regra 3). O plano de teste vem antes do plano de ação.
5. **5 porquês** nas escolhidas (regras 4-6). Ramificar é permitido: um porquê com duas respostas verdadeiras vira dois caminhos.
6. **Saída:** diagrama (Mermaid ou Excalidraw via `terras-excalidraw`), tabela de causas com status e teste, cadeias de porquês, e o pedido para o plano: ações de verificação primeiro, ações corretivas marcadas `depende de` → `terras-5w2h`.

Use `templates/analise-causa.md`.

## Fronteiras

- Priorizar entre vários problemas antes de investigar: `terras-matriz-gut`.
- Transformar a causa em plano: `terras-5w2h`.
- Incidente de TI com linha do tempo: `terras-postmortem` (pode chamar este método na seção de fatores).
- Mapear o processo inteiro: `terras-mapeamento-de-processos`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Causas listadas como fato | status por causa: verificada, provável, hipótese |
| Porquês inventados até soar bem | elo sem evidência vira lacuna marcada |
| "Erro humano" como raiz | por que o sistema deixou o erro passar |
| Um caminho só | ramifique quando houver duas respostas reais |
| Ação antes do teste | verificar primeiro; corrigir depende do resultado |
| Efeito sem número | medir é a ação #1 |

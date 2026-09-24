---
name: terras-backreview
version: 1.0.0
access: free
category: operacao
description: Revisão de backlog em sessão guiada — um documento por vez, itens resolvidos saem, adiados vão para a lista certa e decisões pendentes viram pergunta com opções concretas.
keywords: [revisar o backlog, revisa o backlog, backlog review, limpar o backlog]
---

# Revisão de backlog, por etapas

## Descrição

Não é um relatório de uma vez só. É uma sessão guiada: mostra o estado real de **um escopo por vez**, resolve o que dá para resolver ali (pergunta a quem decide quando a resposta não é sua), aplica a decisão no arquivo na hora, e só então avança para o próximo escopo. Nunca despeje todos os documentos de uma vez — uma parede de texto gera decisão pior do que um assunto de cada vez.

## Quando usar

- Quando o usuário pedir revisão de backlog, limpeza das listas ou "o que está pendente mesmo?"
- Antes de planejar o próximo ciclo — lista limpa é pré-requisito de plano bom.

## Regra de ouro

> Manter limpa a lista de backlog: o que foi resolvido sai; o que fica para depois vai para a lista certa; tudo o mais atualizado possível.

Concretamente:

- Item **resolvido** não fica na lista de aberto — vira nota histórica curta (data + referência do commit/entrega) ou sai de vez se o histórico de versionamento já capturou.
- Item **adiado** (não agora, mas ainda vale) sai da lista de trabalho ativo e vai para o arquivo/seção certo (decisões abertas, seção de candidatas), com a razão e a data.
- **Nenhuma afirmação fica sem verificação**: se o item cita código, arquivo ou tabela, confira contra o projeto antes de aceitar a afirmação como verdadeira — documentação deriva, o código é a fonte.

## Como funciona

### 0. Orientação rápida (antes de tocar em qualquer documento)

Olhe o histórico recente do projeto para saber o que mudou desde a última revisão. Se nada mudou nas listas, diga isso em uma frase e pergunte se o usuário quer mesmo repetir a rodada inteira ou só ver as diferenças.

### 1. Um escopo por vez

Para CADA documento de backlog, na ordem em que a decisão pendente é mais provável primeiro:

1. **Leia o arquivo inteiro** — não confie em memória de sessões anteriores.
2. **Verifique afirmações contra o código** onde o item cita arquivo, símbolo ou tabela.
3. **Classifique cada item aberto** em: resolvido-mas-listado (stale), genuinamente aberto sem decisão pendente (é só trabalho), ou genuinamente aberto com decisão pendente.
4. **Mostre um resumo curto desse UM documento** — tabela ou lista, não prosa longa. Separe os três grupos.
5. **Stale** → corrija direto (é limpeza mecânica, não decisão) e diga o que mudou.
6. **Decisão pendente** → pare aqui e pergunte: no máximo 2 a 4 perguntas por vez, cada uma com opções concretas, nunca pergunta aberta. Espere a resposta antes de seguir.
7. Só depois de resolver (ou o usuário dizer "pula", "depois") avance para o próximo documento.

### 2. Aplicar a resposta na hora

Toda resposta vira edição no arquivo certo **no mesmo passo** — não acumule decisões para aplicar no final. Decisão nova sem lugar óbvio entra no registro de decisões abertas, com dono e critério de fechamento.

### 3. Versionamento

Um commit por escopo resolvido, não um commit gigante no fim. Adicione só os arquivos tocados, por caminho explícito.

### 4. Fechamento

Resumo final curto: quantos itens saíram por estarem resolvidos, quantos foram decididos agora, quantos continuam genuinamente abertos aguardando trabalho. E nada mais — sem repetir o conteúdo já mostrado etapa por etapa.

## O que esta instrução NÃO faz

- Não decide por conta própria o que é decisão do dono (prioridade de produto, risco aceito, escopo de feature) — isso sempre vira pergunta.
- Não implementa trabalho — só organiza o backlog. Destravar ou construir algo durante a sessão é tarefa separada, depois da revisão.
- Não reabre decisões já fechadas sem motivo novo — só cita que existem e seguem assim.

## Critério de qualidade

A sessão terminou bem quando: cada documento foi revisado um por vez, os itens stale saíram com data e referência, as decisões do dono foram aplicadas na hora, e o resumo final dá os três números (saíram, decididos, seguem abertos) sem repetir a sessão.

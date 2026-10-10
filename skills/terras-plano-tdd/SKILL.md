---
name: terras-plano-tdd
version: 1.0.0
access: free
category: desenvolvimento
description: Transforma uma spec revisada em plano test-first (RED, GREEN, REFACTOR) com arquivo e nome de teste concretos, e uma lista de tarefas em que cada uma diz por comando o que é estar pronta. Use para planejar a implementação de uma feature com TDD.
keywords: [plano tdd, plano de implementacao, test-first, red green refactor, tarefas, definicao de pronto, done, checklist de tarefas, planejar feature]
---

# Plano TDD com definição de pronto

## Objetivo

Pegar uma spec já revisada e devolver dois artefatos:

1. **`plano.md`**: a sequência RED → GREEN → REFACTOR, com o arquivo de teste, o nome de cada teste e o motivo de ele falhar antes da implementação.
2. **`tarefas.md`**: a lista de tarefas em que cada tarefa tem uma linha `pronto:` que diz, de preferência por um comando, o que significa estar pronta.

O plano existe para que ninguém escreva código de produção antes do teste, e para que nenhuma tarefa seja marcada como feita só porque a parte mais visível ficou pronta.

## Onde está instalada

Fonte única: `skills/terras-plano-tdd/` no repositório `terrasia-skills`. Adaptada do speccraft (MIT, ver `NOTICE`).

## Entradas

- A spec revisada (o quê, por quê, critérios de aceite, fora de escopo). Sem critérios de aceite testáveis, pare e peça a revisão da spec antes (skill `terras-critica-de-spec`).
- As regras do repositório: `CLAUDE.md`, `AGENTS.md`, README e convenções de teste.
- A lista dos testes que já existem nas pastas que a spec toca. Descubra onde o projeto põe os testes olhando o repositório (teste ao lado do arquivo, pasta `__tests__/`, pasta `tests/`, teste no mesmo arquivo como em Rust). Não suponha o padrão de uma linguagem.
- O comando de teste do projeto. Se houver build antes do teste ou versão mínima de runtime, ela entra no plano.

## Regras duras

1. **Todo GREEN vem depois de um RED.** Sem exceção.
2. **Nomes concretos.** Cada RED diz o caminho exato do arquivo de teste, o nome exato de cada teste e por que ele falha antes da implementação.
3. **Cada GREEN diz o arquivo de produção e o mínimo de código** para os testes do RED anterior passarem. Nada além disso.
4. **REFACTOR é opcional**, mas recomendado quando o GREEN cria duplicação. Os testes continuam passando.
5. **Passos pequenos.** Cada passo é verificável pelo comando de teste do projeto, rodado no escopo do passo.
6. **Uma entrega por caixa de seleção.** Se o passo é "implementar a interface *e* escrever os testes", são duas subtarefas, não uma.
7. **Toda tarefa tem exatamente uma linha `pronto:`**, preenchida mesmo antes de começar. A falta dela tem que aparecer na hora do plano, não no fechamento.
8. **Prefira um predicado executável.** Um `pronto:` que começa com `$` é um comando: o código de saída dele decide se a tarefa está pronta. Qualquer outro texto é prosa, útil para explicar, mas nunca verificado. Use `$` sempre que a conclusão for observável por comando: um teste no escopo, um `grep`, um `test -f`.
9. **Para opção ou flag, o predicado prova quem lê, não só quem declara.** Esse é o defeito que a regra existe para pegar:
   ```
   pronto: $ grep -q MINHA_OPCAO src/config.ts && grep -q MINHA_OPCAO src/leitor.ts
   ```
10. **O predicado nunca chama o verificador que o executa.** Seria recursão sem fim.
11. **`$` sozinho é erro**, não prosa: escreva o comando ou escreva texto.

Predicados rodam com `/bin/sh -c` a partir da raiz do repositório: mantenha POSIX e rápido (alvo: menos de 30 s cada).

## Formato do `plano.md`

```markdown
---
spec: "<id ou arquivo da spec>"
status: planejado
estrategia: tdd
---

# Plano — <título>

## Sequência test-first

### Passo 1 — <descrição curta> (RED)
- Criar `<arquivo de teste>`:
  - `<nome do teste>` — <o que verifica>
  - `<nome do teste 2>` — <o que verifica>
- Falha porque: <motivo>

### Passo 2 — <descrição curta> (GREEN)
- Implementar `<arquivo>` com <o que implementa>.
- Todos os testes do passo 1 passam.

### Passo N — Refactor (opcional)
- <o que limpa>
- Todos os testes continuam passando.

## Delegação (opcional)

- <passo> → <agente auxiliar> (motivo: <ponto forte>)

## Riscos

- <risco> → mitigação: <como>
```

## Formato do `tarefas.md`

```markdown
---
spec: "<id>"
contrato: pronto-significa-v1
---

# Tarefas

- [ ] T1 — <passo com uma entrega>
  pronto: $ <comando cujo código de saída É a definição de pronto>
- [ ] T2 — <passo com várias entregas>
  - [ ] T2.a — <entrega>
  - [ ] T2.b — <entrega>
  - [ ] T2.c — <entrega>
  pronto: $ <comando que cobre o passo inteiro>
- [ ] T3 — <passo ainda não verificável por comando>
  pronto: texto livre é aceito, mas nunca é verificado
```

Gramática:

- **Tarefa** é a caixa na coluna 0. O id pode ter pontos (`T0.1`).
- **Subtarefa** é uma caixa indentada cujo id é o da tarefa mais um segmento (`T2.a`). Um nível só.
- **Linha `pronto:`** fica indentada com exatamente 2 espaços e pertence à tarefa anterior. Uma por tarefa. Subtarefas não têm `pronto:` próprio.

## Verificação no fechamento

Antes de declarar a spec concluída, confira o `tarefas.md`:

1. **Pai e filho:** nenhuma tarefa `[x]` pode ter subtarefa `[ ]`. Marcar o pai com um filho aberto é exatamente o erro que o formato existe para pegar.
2. **Linha `pronto:`:** toda tarefa tem uma, não vazia.
3. **Predicados:** rode cada `pronto: $ ...` da raiz do repositório e registre o código de saída. Qualquer predicado que falhe reabre a tarefa.

Relate o resultado como tabela: tarefa, estado marcado, predicado, saída. Não marque nada como pronto sem a saída do comando.

## Fora de escopo

- Escrever a spec (isso vem antes, na conversa de descoberta).
- Executar a implementação: o plano é a entrada para quem implementa.
- Inventar números de desempenho ou metas que a spec não traz. Vira pergunta aberta.

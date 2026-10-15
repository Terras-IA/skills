---
name: terras-spec-flow
version: 1.0.0
access: free
category: desenvolvimento
description: "Conduz uma feature de ponta a ponta por spec (estilo spec-kit): princípios do repo, spec, crítica, plano TDD, análise de consistência, implementação e fechamento, com portão entre as fases. Use para feature spec-driven ou SDD. Não é para só criticar spec (terras-critica-de-spec)."
keywords: [spec-driven, spec driven development, sdd, spec-kit, specify, fluxo de spec, feature por spec, especificar feature, plano e tarefas, constitution]
---

# Fluxo de feature por spec

## Objetivo

Levar uma feature da ideia ao merge passando por artefatos que se conferem entre si, como o spec-kit do GitHub (`constitution → specify → clarify → plan → tasks → analyze → implement`), mas usando as skills da casa em cada fase. Esta skill não repete o método das outras: ela decide **a ordem, onde os arquivos ficam e o portão que libera cada fase**.

## Regra dura: portão é portão

Nenhuma fase começa antes do portão da anterior passar. Pressa encolhe os artefatos (spec de uma tela, plano de cinco passos), **nunca pula portão**.

| Racionalização | Realidade |
|---|---|
| "Registro as suposições e sigo se o usuário não responder" | Suposição sem resposta vira pergunta aberta. Spec com pergunta aberta bloqueante não passa o portão 2. |
| "Mostro um resumo e sigo se ele não objetar" | Silêncio não é aprovação. O portão 2 pede um "aprovado" explícito. |
| "Meu checklist já valida a spec" | Quem escreveu não critica. A crítica é a da `terras-critica-de-spec`, com veredito. |
| "O plano TDD já mostra as funções, o desenho é repetição" | O plano diz a ordem e o teste; o desenho diz a forma. Assinatura decidida no GREEN é decisão de arquitetura tomada sem revisão. |
| "O `/analyze` é formalidade, pulo" | A análise é a tabela critério → teste → tarefa. Sem ela, critério sem teste passa despercebido. |
| "'Pronto quando os testes passarem' basta" | `pronto:` é comando (`$ ...`) sempre que a conclusão for observável por comando. |
| "O autor não responde hoje, então assumo" | O autor pode dizer "assume X": isso é resposta e vira decisão na spec. Sem essa frase, a spec espera. |
| "Crio `specs/001-...`" | Use a pasta que o repositório já usa. Pasta nova só se nada existir. |

## Onde os arquivos ficam

Antes de criar qualquer coisa, procure onde o repositório já guarda spec e plano (`docs/specs/`, `docs/superpowers/specs/`, `docs/**/plans/`, `docs/adrs/`) e use esse lugar e esse padrão de nome. Só se nada existir, crie:

```
docs/specs/<AAAA-MM-DD>-<slug>/
  spec.md       # fase 1
  critica.md    # fase 2 (veredito e respostas)
  desenho.md    # fase 2b (tipos, assinaturas, quem chama quem)
  plano.md      # fase 3 (terras-plano-tdd)
  tarefas.md    # fase 3 (terras-plano-tdd)
  analise.md    # fase 4
```

Implementação sempre em branch nova a partir da principal atualizada, nunca na principal.

## As fases

### 0. Princípios (o "constitution")

Leia `AGENTS.md`, `CLAUDE.md`, README e as ADRs do repositório. Não crie um arquivo de princípios: eles já existem. Copie para a spec só as regras que **esta** feature pode violar, com o arquivo de origem.
**Portão 0:** a seção "Regras do repositório" da spec está preenchida (ou diz "nenhuma aplicável" e por quê).

### 1. Spec (o "specify")

Converse com o autor, uma pergunta por vez, e escreva `spec.md`:

```markdown
---
id: <AAAA-MM-DD>-<slug>
status: rascunho        # rascunho → aprovada → planejada → em-andamento → concluida
criado: <AAAA-MM-DD>
revisao: 1
---
# <Título>
## Por quê
## O quê
## Critérios de aceite      <!-- cada um observável: entrada → saída ou efeito -->
- CA1 — ...
## Fora de escopo
## Regras do repositório     <!-- da fase 0 -->
## Perguntas abertas         <!-- marque [bloqueante] as que mudam o que será construído -->
```

Nada de código, nome de função ou número que o autor não deu.
**Portão 1:** todo critério tem id (`CA1`, `CA2`...) e "Fora de escopo" não está vazio.

### 2. Crítica e esclarecimento (o "clarify")

Rode a `terras-critica-de-spec` no modo crítica e grave em `critica.md` o bloco YAML do veredito, uma seção por rodada (`## Rodada 1`, `## Rodada 2`), com a resposta do autor embaixo de cada preocupação. Se vier `pedir-mudancas` ou `rejeitar`, rode o modo revisão com o autor e critique de novo.

Leve também à `terras-revisao-cruzada` quando a feature tocar dado pessoal, dinheiro, autenticação ou permissão, migration de banco ou contrato público (API, SDK, formato de arquivo).
**Portão 2:** veredito `aprovar` ou `aprovar-com-comentarios`, nenhuma pergunta `[bloqueante]` aberta e um "aprovado" explícito do autor. Então `status: aprovada`.

### 2b. Desenho do programa

A arquitetura combinada e a spec aprovada ainda deixam para o agente as decisões que mais pesam na manutenção: que tipos existem, que assinatura cada função pública tem, quem chama quem e onde cada peça mora. Decididas no meio da implementação, elas viram objeção no diff, que é a hora mais cara de discordar. O modelo também não aprende a acertá-las sozinho: o treino dele recompensa o teste que passa, não o código que continua fácil de mudar (Dex Horthy, "Why Software Factories Fail", AI Engineer 2026).

Escreva `desenho.md` com quatro seções curtas:

```markdown
## Tipos            <!-- novos ou alterados, com os campos -->
## Assinaturas      <!-- funções, rotas e eventos públicos: nome(entrada): saída -->
## Quem chama quem  <!-- lista "A → B" ou um flowchart mermaid; do ponto de entrada até o efeito -->
## O que não muda   <!-- contratos que esta feature promete não tocar -->
```

Cada assinatura cita o critério que serve (`CA2`). Assinatura sem critério é escopo extra; critério sem assinatura que o realize é buraco no desenho.
**Portão 2b:** "aprovado" explícito do autor sobre o `desenho.md`. Feature que não cria nem altera tipo, assinatura pública ou o caminho de chamada registra no `desenho.md` a linha "sem desenho: nenhuma assinatura pública nova ou alterada" e segue.

### 3. Plano e tarefas (o "plan" e o "tasks")

Rode a `terras-plano-tdd` com a spec aprovada e o `desenho.md`. Cada teste do RED cita o critério que prova (`CA2`), e cada GREEN usa as assinaturas do desenho: mudar uma assinatura aqui é voltar ao portão 2b, não ajustar em silêncio.
**Portão 3:** toda tarefa do `tarefas.md` tem uma linha `pronto:`, de preferência `$ comando`. Então `status: planejada`.

### 4. Análise de consistência (o "analyze")

Monte `analise.md` com uma tabela só:

| Critério | Teste(s) no plano | Tarefa(s) |
|---|---|---|
| CA1 | `arquivo.test.ts` › `nome do teste` | T2 |

Depois confira: critério sem teste, tarefa que não serve a nenhum critério (exceto refactor), item do plano que está em "Fora de escopo", regra da fase 0 que o plano quebra, assinatura do plano que não está no `desenho.md`.
**Portão 4:** nenhuma linha vazia na tabela e nenhum achado aberto. Achado se resolve voltando à fase que o causou, não remendando aqui.

### 5. Implementação (o "implement")

Branch nova. Siga o `plano.md` na ordem, RED antes de GREEN. Marque `[x]` só depois de rodar o `pronto:` da tarefa e ver código de saída 0. `status: em-andamento`.

### 6. Fechamento

1. Rode a verificação de fechamento da `terras-plano-tdd` (pai e filho, linha `pronto:`, todos os predicados) e mostre a tabela com as saídas.
2. Rode a checagem de divergência da `terras-critica-de-spec`: o que a spec cita existe no código com esse nome?
3. Rode o gate do repositório (o comando que o README ou `AGENTS.md` manda).
4. `status: concluida` e, se o repositório tiver docs por domínio, a `terras-consolidacao-de-memoria` no modo fechar.

**Portão 6:** os três comandos com saída mostrada na conversa. Sem saída, não está pronto.

## Atalho para mudança pequena

Correção de uma linha ou ajuste sem comportamento novo não precisa do fluxo. Use o fluxo quando houver comportamento novo que alguém vai testar, ou quando a mudança atravessar mais de um módulo ou contrato.

## Combina com

- `terras-critica-de-spec`, `terras-plano-tdd`, `terras-revisao-cruzada`, `terras-consolidacao-de-memoria`: as fases 2, 3 e 6.
- `terras-adr`: quando a fase 0 ou 4 achar uma decisão que não está em nenhuma regra do repositório e que vale além desta feature (uma biblioteca nova, um formato, uma fronteira entre módulos). Registre antes do portão 4; decisão que só vale aqui fica na spec.
- `terras-revisao-de-codigo`: no diff, antes do merge.

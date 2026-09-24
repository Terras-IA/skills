---
name: terras-backreview
description: Mostra o backlog atual do terrasia (os 4 backlogs + DECISOES-ABERTAS.md), aplica a regra de ouro de manter a lista limpa (resolvido sai, adiado vai pra lista certa, tudo com data) e resolve pendências fazendo perguntas ao dono, uma etapa de cada vez. Use quando o dono pedir "backlog review", "/backreview" ou revisão do estado do backlog.
---

# /backreview — revisão e resolução do backlog, por etapas

Não é um relatório de uma vez só. É uma sessão guiada: mostra o estado real
de UM escopo por vez, resolve o que dá pra resolver ali (pergunta ao dono
quando a resposta é dele, não sua), aplica a decisão no arquivo na hora, e só
então avança pro próximo escopo. Nunca despeje os quatro backlogs de uma vez
— o dono decide melhor um assunto de cada vez do que uma parede de texto.

## Regra de ouro (a que já vale neste repo)

> "manter limpa a lista de backlog, o que foi resolvido sai. o que fica pra
> depois em outra lista, o mais atualizado possível."

Concretamente:
- Item **resolvido** não fica na lista de aberto — vira nota histórica curta
  (data + commit/PR) ou sai de vez se já está capturado no git log.
- Item **adiado** (não agora, mas ainda vale) sai da lista de trabalho ativo
  e vai para a seção/arquivo certo (ex.: "Travadas por decisão do dono",
  `docs/DECISOES-ABERTAS.md`, ou uma seção "candidatas" do próprio backlog),
  com a razão e a data.
- Nenhuma claim fica sem verificação: se o item cita código/arquivo/tabela,
  confira contra o repo antes de aceitar a claim como verdadeira — docs
  driftam, o código é a fonte.

## Escopo — os 5 documentos

1. `docs/BACKLOG.md` — almas departamentais + gates de plataforma (o que
   recebe o trabalho que sai de decisões).
2. `docs/backlog-chatgpt.md` — diferenciais de produto.
3. `docs/backlog-implantacao.md` — deploy/CI/observabilidade (P0 adiado pro
   final por decisão de 2026-09-11 — não reabrir essa pergunta sem motivo novo).
4. `docs/COMPLIANCE-BACKLOG.md` — sempre lido **junto** com
   `docs/ANALISE-COMPLIANCE-BACKLOG-2026-09-11.md` (parecer que corrige
   atribuições incorretas ao código atual — nunca aceitar uma claim de
   compliance sem cruzar com esse parecer).
5. `docs/DECISOES-ABERTAS.md` — registro canônico de decisões pendentes, com
   dono e critério de fechamento; é para onde vai todo item dos backlogs que
   precisa de uma escolha do dono antes de virar trabalho.

## Passo a passo

### 0. Orientação rápida (antes de tocar em qualquer doc)

`git log --oneline -15` para saber o que mudou desde a última revisão — se
nada mudou nos backlogs desde o último `/backreview`, diga isso em uma frase
e pergunte se ele quer mesmo repetir a rodada inteira ou só ver o diff.

### 1. Um escopo por vez

Para CADA um dos 5 documentos, nesta ordem (o que mais provavelmente tem
decisão pendente do dono primeiro): `DECISOES-ABERTAS.md` → `BACKLOG.md` →
`backlog-chatgpt.md` → `backlog-implantacao.md` → `COMPLIANCE-BACKLOG.md`.

Para cada um:

1. **Leia o arquivo inteiro** (não confie em memória de sessões anteriores —
   outras sessões commitam neste repo em paralelo).
2. **Verifique claims contra o código** onde o item cita arquivo/símbolo/
   tabela — `grep`/`Read`, nunca aceitar de olho.
3. **Classifique cada item aberto** em: resolvido-mas-listado (stale),
   genuinamente aberto sem decisão pendente (é só trabalho), ou
   genuinamente aberto com decisão do dono pendente.
4. **Mostre um resumo curto desse UM documento** — tabela ou lista, não
   prosa longa. Separe claramente os três grupos do passo 3.
5. **Se houver stale**, corrija direto (é limpeza mecânica, não decisão) e
   diga o que mudou.
6. **Se houver decisão pendente**, pare aqui e pergunte — use a ferramenta de
   pergunta ao usuário, no máximo 2-4 perguntas por vez, cada uma com opções
   concretas (não pergunta aberta tipo "o que você acha?"). Espere a resposta
   antes de seguir para o próximo documento.
7. Só depois de resolver (ou o dono dizer "pula", "depois", "não agora")
   avance para o próximo documento do passo 1.

### 2. Aplicar a resposta na hora

Toda resposta do dono vira edição no arquivo certo NO MESMO PASSO — não
acumule decisões pra aplicar todas no final. Se a resposta cria uma decisão
nova sem lugar óbvio, ela entra em `docs/DECISOES-ABERTAS.md` com dono e
critério de fechamento, seguindo o formato das entradas existentes.

### 3. Git

Segue a disciplina do `CLAUDE.md`: nunca `git add -A`/`git add .` — outras
sessões trabalham no mesmo repo. Stage só os arquivos tocados nesta sessão,
por caminho explícito, e confira `git status --short` antes de cada commit.
Comite por escopo resolvido (um commit por documento fechado nesta rodada),
não um commit gigante no fim.

### 4. Fechamento

Ao final dos 5 documentos (ou quando o dono encerrar a sessão), um resumo
final curto: quantos itens saíram por estarem resolvidos, quantos foram
decididos agora, quantos continuam genuinamente abertos aguardando trabalho
(sem decisão pendente) — e nada mais. Sem repetir o conteúdo já mostrado
etapa por etapa.

## O que este comando NÃO faz

- Não decide por conta própria o que é decisão do dono (prioridade de
  produto, risco aceito, escopo de feature) — isso sempre vira pergunta.
- Não implementa trabalho — só organiza o backlog. Se o dono pedir para
  destravar/construir algo durante a sessão, isso é uma tarefa separada
  depois do `/backreview` fechar aquele escopo, não no meio dele.
- Não reabre decisões já fechadas sem motivo novo (ex.: D-11 débito técnico
  sem prazo, P0 de implantação adiado) — só cita que existem e seguem assim.

---
name: terras-qualidade
version: 1.0.0
access: free
category: operacao
description: Protocolo de qualidade para tarefas não triviais — plano aprovado antes do código, teste que falha antes, gate completo verde no início e no fim, validação prática rodada e revisão cruzada em mudança de alto risco.
keywords: [protocolo de qualidade, plano antes de codigo, teste que falha antes, gate verde, revisao cruzada]
---

# Protocolo de qualidade de entrega

## Descrição

Orquestra um protocolo de qualidade que roda **antes de qualquer código** em tarefa não trivial: feature nova, bugfix, refactor, script novo, mudança de comportamento ou de invariante. O princípio: quando quem executa não é o modelo mais forte, a qualidade da entrega vem do processo e dos gates, não da primeira tentativa — o gate segura o que o executor não segura sozinho.

Esta instrução é a orquestração. As etapas de encerramento (validação prática, sincronia de contrato, conformidade de documentação, fronteira certa) têm procedimentos próprios e são citadas aqui como etapas, não repetidas.

## Quando usar

- Ao INICIAR qualquer tarefa não trivial, mesmo sem o usuário pedir o protocolo.
- De novo ao CONCLUIR a entrega: o checklist de fechamento roda no fim, não no meio.
- Não usar para correção de typo/comentário, documentação simples ou pergunta sem mudança de código — o protocolo não é burocracia.

## Como funciona

### Checklist do protocolo

1. **Plano antes de código.** Escreva o plano (passos com checkbox) e só comece a codificar com o plano aprovado por quem decide. Decisão de arquitetura tomada no meio da implementação é o sinal de que este passo foi pulado.
2. **Teste que falha antes.** Escreva o teste que reproduz o bug (bugfix) ou define o comportamento novo (feature) e veja-o FALHAR antes de implementar. Quando teste não for possível, justifique no plano.
3. **Gate completo, cedo e no fim.** Rode o gate completo do projeto assim que houver algo que rode, e de novo antes de considerar pronto — não só a suíte do arquivo tocado. Gate verde é pré-condição, não polimento.
4. **Validação prática rodada.** Artefato executado contra o alvo real (servidor, API, script de verdade), não só escrito. Descrever o teste não cumpre a regra; rodar cumpre.
5. **Revisão cruzada em alto risco.** Mudança em invariante de segurança, rota nova, migração destrutiva ou decisão de arquitetura: um segundo revisor (outro modelo ou outra pessoa) revisa o diff antes do commit. Auto-aprovar o próprio diff como única revisão não cumpre a regra.
6. **Sessão curta, commit miúdo.** Uma tarefa por sessão sempre que possível; commit cedo e pequeno; não empilhe mudanças independentes. Sessão que cresceu demais: abra outra com resumo, não continue.
7. **Encerrar pelo checklist de entrega do projeto.** Gate verde, validação prática rodada, contrato e documentação sincronizados, e registro no catálogo quando a entrega criar artefato novo.

### Quando não se aplica

- Correção de typo/comentário, documentação trivial ou pergunta sem mudança de código.
- Código que ainda não existe (planejamento puro): o protocolo vale da hora em que a tarefa é aceita para execução em diante.

## Governança

- O gate de qualidade não substitui a decisão de quem é dono do projeto: plano aprovado é requisito, e a aprovação é do dono, não de quem executa.
- Revisão cruzada é obrigatória em alto risco. Em risco médio, é julgamento de quem executa — mas registrar a justificativa de ter pulado faz parte da entrega.

## Critério de qualidade

A entrega está pronta quando: o plano foi aprovado antes do código, o teste que define a mudança falhou antes e passa agora, o gate completo está verde, a validação prática foi executada de verdade contra o alvo real e — se a mudança era de alto risco — houve revisão por segundo revisor. Os sete passos não são sugestões de melhoria; são a definição de pronto.

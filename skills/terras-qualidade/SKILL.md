---
name: terras-qualidade
description: Garante que toda tarefa não-trivial no repo terrasia siga o protocolo de qualidade do agente antes de qualquer código — plano aprovado, teste que falha antes da implementação, gate completo (scripts/verify-all.sh) verde cedo e no fim, validação prática rodada e revisão cruzada por segundo modelo em mudança de alto risco. Use ao INICIAR qualquer tarefa não-trivial (feature nova, bugfix, refactor, script novo, mudança de comportamento ou de invariante) e de novo ao CONCLUIR a entrega; a regra vale mesmo sem o usuário pedir. NÃO ative para correção trivial de typo/comentário, documentação simples ou pergunta sem mudança de código.
---

# Protocolo de qualidade do agente — terrasia

A seção "Protocolo de qualidade do agente" do `CLAUDE.md` exige que toda
tarefa não-trivial siga um protocolo **antes de qualquer código**. Motivo
registrado: quando o modelo executor não é o mais forte, a qualidade da
entrega vem do processo e dos gates, não da primeira tentativa — o gate
segura o que o modelo não segura sozinho. Esta skill não substitui as outras
skills do repo: ela as orquestra na ordem certa.

## Convenção já estabelecida — não invente um formato novo

As etapas de encerramento já têm skills próprias; esta as cita como etapas em
vez de duplicar as regras delas:

- `terras-validacao` — artefato de validação prática rodado de verdade;
- `terras-api-sync` — contrato daemon + client + README no mesmo commit;
- `terras-drift` — docs ainda batem com o código;
- `terras-boundary` — feature no repo certo, decidido antes de codificar.

## Checklist do protocolo

1. **Plano antes de código.** Para tarefa não-trivial, escreva o plano
   (passos com checkbox) e só comece a codificar com o plano aprovado pelo
   dono. Decisão de arquitetura tomada no meio da implementação é o sinal de
   que este passo foi pulado.
2. **Teste que falha antes.** Escreva o teste que reproduz o bug (bugfix) ou
   que define o comportamento novo (feature) e veja-o FALHAR antes de
   implementar. Mudança em que teste não é possível: justifique no plano.
3. **Gate completo, cedo e no fim.** Rode `./scripts/verify-all.sh` assim que
   houver algo que rode, e de novo antes de considerar pronto — não só a
   suíte do arquivo tocado. Gate verde é pré-condição, não polimento.
4. **Validação prática rodada** — siga `terras-validacao` (não reescreva as
   regras dela aqui): artefato executado contra o alvo real, não só escrito.
5. **Revisão cruzada em alto risco.** Mudança em invariante de segurança,
   rota nova, migração destrutiva ou decisão de arquitetura: antes de
   commitar, `node scripts/revisao-cruzada.mjs` (segundo modelo revisa o diff
   em contexto limpo) ou revisão manual por outro modelo. Auto-aprovar o
   próprio diff como única revisão não cumpre a regra.
6. **Sessão curta, commit miúdo.** Uma tarefa por sessão sempre que possível;
   commit cedo e pequeno; não empilhe mudanças independentes numa sessão só.
   Sessão que cresceu demais: abra nova com resumo, não continue.
7. **Encerrar pelo checklist de entrega** do `CLAUDE.md` (os quatro itens) e
   com linha nova em `docs/HARNESS-LIBRARY.md` quando a entrega criar skill,
   script, gate ou artefato.

## Quando não se aplica

- Correção de typo/comentário, documentação trivial ou pergunta sem mudança
  de código — o protocolo não é burocracia.
- Código que ainda não existe (planejamento puro): é papel da
  `terras-reconstrucao`; o protocolo vale da hora em que a tarefa é aceita
  para execução em diante.

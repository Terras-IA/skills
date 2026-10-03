---
name: terrasia-vagas-coders
description: "Filtra as vagas do board da comunidade COD3RS (app.coders.com.br/comunidade#vagas) contra o currículo do usuário e devolve só o que faz sentido real: balde A (recomendar), B (talvez) e C (descarte com motivo) — e, com aprovação por vaga, avança para a aplicação no site de cada uma (carta, formulário, portões de upload/login). Use quando o pedido envolver vagas da COD3RS, vagas do coders, 'o que tem de vaga pra mim', triagem de vagas no currículo, vagas que combinam comigo, board de vagas, candidatura nas vagas, 'aplica pra mim', aplicar nas vagas aprovadas, ou agendar essa triagem. Job board triage against resume, COD3RS community jobs, assisted job applications."
keywords: [cod3rs, coders, vagas, board, curriculo, triagem, emprego, remote, senior, fit]
version: "1.0.0"
metadata:
  requires: navegador controlável pelo agente (browser pane), com o usuário logado na COD3RS e com acesso ao board de vagas (termos aceitos)
---

# Vagas COD3RS: triagem no currículo

O board da comunidade recebe vaga de toda fonte e de todo nível; quase nada
disse respeito. Esta skill puxa as vagas novas pela API do board, julga cada
uma contra o currículo (`references/perfil.md`) e entrega três baldes —
**A faz sentido real**, **B talvez**, **C descarte com motivo** — para o
usuário gastar atenção só onde vale.

Divisão de trabalho: **o script lista, o agente julga.** Contagem, dedup e
paginação são mecânicos; o encaixe (stack núcleo, senioridade, onde) é
julgamento seu guiado pelo perfil — não existe grep que decida isso.

## Regras duras

1. **Triagem é somente leitura; aplicação é por aprovação.** Nenhuma escrita
   no board (kanban, prefs). Na fase 2, a skill só age no formulário da vaga
   que o usuário aprovou — **uma por vez, com os valores exatos mostrados e
   um "aprovado" explícito antes de cada submit**. Nunca em lote, nunca em
   paralelo, nunca por conta própria.
2. **Token fica na página.** Nunca leia, imprima ou envie `_cj_token` para
   fora do navegador.
3. **Login, 2FA, captcha, gate de termos do board: pare** e peça para o
   usuário resolver no navegador.
4. **Não invente encaixe.** A API não traz descrição da vaga; julgue pelo que
   existe (título, empresa, fonte, onde, faixa) e aprofunde no `jobUrl` antes
   de recomendar um A. Título sozinho não vira recomendação.
5. **Salário se reporta, não se julga** (ver preferências em `perfil.md`).
6. **Respostas de formulário vêm de fato do kit** (`references/aplicacao.md`);
   pergunta sem fato (pretensão, notice period) → pergunte ao usuário.

## Como trabalhar

1. **Aba da COD3RS.** Abra `https://app.coders.com.br/comunidade#vagas`. Se
   pedir login ou termos do board, pare e peça ao usuário. Injete
   `scripts/vagas.js` (cole o arquivo num javascript_exec) e rode
   `await __vagas.me()` — `assinante: false` = o usuário não tem acesso ao
   board; avise e encerre.
2. **Janela e fontes.** Primeira rodada ou pedido genérico ("tem vaga pra
   mim?"): `await __vagas.list({dias: 7})`. Rotina: as **novas** (passo 4).
   `await __vagas.facets()` lista os valores válidos de fonte/período/
   modalidade se o usuário quiser afunilar.
3. **Estado de já vistas.** Leia `~/.config/terrasia-vagas-coders/vistas.json`
   (criado na primeira rodada). Toda vaga cujo `url` já está lá é pulada,
   exceto se o usuário pedir explicitamente ("mostra tudo de novo").
4. **Filtrar as novas.** Da lista do passo 2, tire as já vistas. Volume
   observado: ~270 vagas/dia de entrada (out/2026) — triagem a nível de título
   aguenta; se a rodada acumulada passar de ~400, afunile pela `desde` da
   última rodada ou por fonte; não puxe o board inteiro por rotina.
5. **Julgar** com `references/perfil.md`: A, B ou C para cada vaga nova, com
   motivo de 1 linha no C (e no B, a dúvida). Aplique as regras de julgamento
   do perfil (senioridade mínima, stack núcleo, onde).
6. **Aprofundar os A.** Para cada A, abra o `jobUrl` (1.500 caracteres do
   anúncio bastam) e confira: stack real, senioridade, modelo de trabalho,
   faixa. Anúncio que contradiz o título reclassifica — e o motivo vai na
   tabela. Se um A morrer nesse passo, diga que morreu e por quê.
7. **Entrega.** Uma tabela por balde:
   `Vaga (link) · Empresa (fonte) · Onde · Faixa · Fit · Por quê`.
   A ordenada pelo encaixe (stack núcleo + remote primeiro). B e C compactos.
   Feche com contagem (X novas, A/B/C) e a janela usada. Cite quantos C e os
   motivos mais comuns, sem listar os óbvios um a um se passarem de 15.
8. **Fechar estado.** Grave em `vistas.json` as urls entregues (A e B; os C
   também, para não reaparecerem), com data da rodada:
   `{"vistas": {"<url>": "2026-10-02"}}` — merge, nunca substitua o arquivo.

## Fase 2: aplicar (só nas vagas aprovadas, uma por vez)

Disparada por pedido explícito ("aplica na vaga X", "avana com as que eu
aprovar"). O usuário escolhe da lista A (ou aprova na hora); para cada vaga:

1. **Reabra o anúncio** e leia a JD completa — o encaixe pode mudar (veja
   `references/aplicacao.md`); reclassificou, diga antes de seguir.
2. **Monte o kit**: respostas de screening + carta curta EN no padrão da
   `terras-cover-letter` com o ângulo da vaga. Falta fato (pretensão, notice
   period)? Pergunte uma vez e grave no kit do `perfil.md`.
3. **Siga o playbook da fonte** até o formulário, preencha texto/radio/seleção
   e **pare nos portões** (login, captcha, upload de currículo, submit).
4. **Portão final**: tabela campo→valor do que será enviado → "aprovado" →
   submit → confirme na página → registre em `candidaturas.json`.
5. Limite padrão: **3 candidaturas/dia**. Ação pública (comentário/DM de
   candidatura social) segue a regra de aprovação do mural.

Estado das candidaturas: `~/.config/terrasia-vagas-coders/candidaturas.json`.
"Não confirmado" nunca vira reenvio automático — confira a página primeiro.

## Estado

`~/.config/terrasia-vagas-coders/vistas.json` é a memória do que já foi
triado. Apagar o arquivo re-tríada tudo — só faça se o usuário pedir.
`candidaturas.json` registra cada aplicação e seu status real (incluindo
`entregue-ao-usuario` quando parou em portão) — é o que impede candidatura
duplicada e sustenta o relato honesto de "o que foi enviado".

## Rotina agendada

A tarefa roda os passos 1-8 da triagem inteiros: não há ação pública, então
não precisa de aprovação. **Fase 2 não roda em agendamento** — sem usuário no
chat não há quem aprove submit. Se o navegador não estiver aberto/logado no
horário, termine dizendo isso — não tente logar. O usuário lê a tabela ao
abrir a sessão.

## Currículo desatualizado

Este perfil foi destilado do currículo em PDF do usuário. O `perfil.md` real é
local e fica fora do git (o `.gitignore` protege); `references/perfil.example.md`
mostra a estrutura vazia para preencher. Se o usuário disser que o CV mudou (ou a
tabela parecer desalinhada do que ele conta), releia o PDF, atualize
`references/perfil.md` e siga.

## Riscos para avisar ao usuário

A leitura é da conta dele (mesma sessão do navegador), mas o board é da
comunidade: volume alto de varredura repetida em pouco tempo pode chamar
atenção. A rotina diária com janela de novidades é o uso pensado; varrer o
histórico inteiro toda hora não é. A fase 2 automatiza envio em sites de
terceiros (ATS, LinkedIn) que restringem automação nos termos deles — ritmo
baixo, uma vaga por vez e aprovação por envio reduzem o risco, não eliminam.

## Referências

- `scripts/vagas.js`: helper in-page do board (`me, facets, list`) — somente leitura.
- `references/perfil.md`: currículo destilado + baldes de encaixe + regras de julgamento + preferências + kit de candidatura (local, fora do git; a base vazia é `perfil.example.md`).
- `references/aplicacao.md`: fase 2 — playbooks de candidatura por fonte, portões e ritmo.
- `references/api-board.md`: endpoints, campos e comportamento observado da API do board.

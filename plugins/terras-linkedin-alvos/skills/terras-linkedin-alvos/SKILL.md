---
name: terras-linkedin-alvos
description: >-
  Acompanha uma lista de perfis-alvo do LinkedIn (executivos, gestores, recrutadores de empresas
  onde o usuário quer trabalhar), acha os posts recentes de cada um, curte e prepara um comentário
  que acrescenta (experiência, dado ou pergunta real), publicado só com aprovação. Roda na hora ou
  agendado, para comentar cedo. Use quando o usuário passar perfis para acompanhar, falar em
  pessoas-chave, networking para vaga, comentar nos posts de um CEO, gestor ou recrutador, "vê se
  fulano postou", lista de alvos, ou agendar essa rotina. Target profiles, LinkedIn networking,
  comment early on key people's posts.
keywords: [linkedin, networking, alvos, perfis, recrutador, gestor, ceo, comentario, curtir, vaga]
version: "1.0.0"
metadata:
  requires: navegador controlável pelo agente (browser pane do Claude ou Claude in Chrome) com o LinkedIn logado
  config: ~/.config/terras-linkedin-alvos/ (alvos.json, engajados.json, rascunhos/)
---

# LinkedIn: perfis-alvo

## Objetivo

Poucos perfis escolhidos, comentário bom e cedo. O comentário é lido pelos gestores, recrutadores
e pela rede do autor, não necessariamente pelo autor: ele serve de vitrine e deixa morno o convite
de conexão que vem depois. É o oposto do engajamento em massa: qualidade por post, não volume.

## Regra dura

1. **Comentário só com aprovação.** Mostre o rascunho e espere "aprovado" no chat, sempre, inclusive
   em rodada agendada. Uma aprovação vale para os rascunhos mostrados, não para os próximos.
2. **Curtida automática só se o usuário ativou.** Em rodada agendada, curta sem perguntar apenas se
   `alvos.json` tiver `"curtir_automatico": true`, gravado porque o usuário pediu isso de forma
   explícita. Sem isso, a curtida entra no mesmo pedido de aprovação do comentário.
3. **Reação é toggle.** Só clique em "Gostei" com `aria-pressed="false"` (o `__alvos.like` garante).
   Nunca troque nem remova reação existente.
4. **Um comentário por post.** Antes de comentar, confira `engajados.json` e o `prep` do
   `comentar.js` (acusa comentário seu já visível). A página nem sempre mostra comentário antigo seu,
   então o arquivo local é a fonte principal: grave cada comentário publicado nele.
5. **Não invente vivência.** Comentário que diz "vi isso quando migrei X" precisa de fato real do
   usuário. Sem fato, use dado público ou pergunta; ou pergunte a ele qual experiência usar.
6. **Credenciais e convites são do usuário.** Login, 2FA, captcha: pare e peça. Convite de conexão e
   mensagem direta: só rascunho; enviar exige aprovação explícita daquele envio.

## Configuração

Tudo fica em `~/.config/terras-linkedin-alvos/`. Formato em `references/config.md`.

- **Receber a lista.** Quando o usuário passar perfis (URLs `linkedin.com/in/...`, nomes ou um texto
  colado), normalize para `alvos.json`: url, nome, papel (`executivo`, `gestor`, `recrutador`,
  `par`), empresa e uma nota do porquê. Mostre a lista gravada. Pergunte só o que faltar e mudar a
  decisão (ex.: a área de vaga, que orienta o ângulo dos comentários).
- **Tamanho saudável:** 1-2 executivos, 3-5 gestores, 2-3 recrutadores. Acima de ~15 perfis, avise
  que a qualidade dos comentários cai.

## Como trabalhar (rodada)

1. Carregue `alvos.json` e `engajados.json`. Janela padrão: `janela_horas` (24h; comentar cedo é o
   que dá visibilidade).
2. Para cada alvo: navegue para `<url>/recent-activity/all/`, injete `scripts/alvos.js` e rode
   `await __alvos.scan(janela)`. Descarte reposts e URNs que já estão em `engajados.json`. Post com
   `curtido: true` fora do arquivo foi curtido antes (à mão ou em outra sessão): registre em
   `engajados.json` com `curtido_em: "anterior"` e não clique em "Gostei"; ainda pode receber comentário.
3. Para cada post que sobrou: abra `url` do post, leia com `get_page_text` (post inteiro e os
   primeiros comentários, para não repetir o que já disseram).
4. **Priorize.** Posts mais novos primeiro; dentro disso, gestores e recrutadores antes de executivos.
   Se houver muitos, proponha comentar em 3-5 e só curtir o resto.
5. **Escreva** um comentário por post selecionado, seguindo `references/estilo.md` (se a skill
   `terras-linkedin` estiver instalada, a seção "Responder post de terceiro" dela manda).
6. **Aprovação.** Tabela: alvo, papel, idade do post, trecho do post, comentário proposto, curtir
   (sim/não). Marque linhas que atribuem experiência ao usuário. Espere a resposta.
7. **Executar o aprovado**, um post por vez:
   - curtir: na página de atividade do alvo, `__alvos.like(urn)`;
   - comentar: no post, `scripts/comentar.js` (navigate → `prep(snip)` → digitar com o teclado →
     `submit(snip)` → esperar ~4s);
   - gravar em `engajados.json` logo após cada sucesso (urn, alvo, data, curtido, comentário).
   Se a rodada cair no meio e o usuário disser "continua", retome só os itens **já aprovados** do
   arquivo em `rascunhos/` que ainda não estão em `engajados.json`, sem nova aprovação. Qualquer post
   novo encontrado na retomada volta para o passo 6.
8. **Fechamento.** O que foi curtido, comentado e pulado (e por quê), com números vindos dos retornos.
   Se um alvo chegou a 2-3 comentários do usuário nas últimas semanas e ainda não é conexão,
   **sugira** um convite com nota curta e mostre o rascunho (ver `references/estilo.md`).

## Na hora vs agendado

- **Na hora** ("vê os alvos", "comenta nos posts do fulano"): rodada completa acima.
- **Agendado**: use o agendador local do app (a tarefa precisa do navegador logado nesta máquina;
  agente na nuvem não tem sua sessão do LinkedIn). Sugestão: a cada 3h em horário comercial. A
  rodada agendada faz os passos 1-6, curte só se `curtir_automatico` estiver ligado, salva os
  rascunhos em `rascunhos/AAAA-MM-DD-HHh.json` e termina com a tabela de aprovação. Os comentários
  saem quando o usuário responder "aprovado" naquela sessão.

## Riscos para avisar ao usuário

Automação no LinkedIn vai contra os termos de uso da plataforma. O volume baixo, o ritmo humano e a
aprovação reduzem o risco, mas não eliminam. Curtir tudo de todos os alvos parece robô e ajuda pouco:
curtida sozinha quase não gera visibilidade.

## Referências

- `scripts/alvos.js`: varredura da página de atividade (`scan`, `like`), com data exata pelo URN.
- `scripts/comentar.js`: comentar num post aberto (`prep`, `submit`), PT e EN, bloqueia duplicata.
- `references/config.md`: formato de `alvos.json` e `engajados.json`.
- `references/estilo.md`: comentário para perfil-alvo, por papel, e nota de convite.
- `references/red-baseline.md`: falhas observadas e o teste de aderência.

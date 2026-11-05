# Linha de base (vermelho)

Falhas e armadilhas observadas ao executar o fluxo sem a skill, na sessão de 2026-09-29
(2 lotes, 74 posts, 56 comentários no LinkedIn). Cada regra da SKILL.md fecha uma destas.

| # | O que aconteceu / quase aconteceu | Consequência | Regra que fecha |
|---|---|---|---|
| 1 | Endpoint de curtir é toggle; a primeira ideia era "curtir todos os posts da janela" | Descurtiria posts já curtidos | Regra dura 2; `like()` relê `likedByMe` |
| 2 | Loop de 37 comentários num único javascript_exec estourou os 45s e parou em 34 | Reenvio cego duplicaria 34 comentários | Regra dura 3; `comment()` limita 10 e pula quem já tem comentário |
| 3 | A aba da COD3RS foi parar no LinkedIn; o fetch devolveu HTML 404 | Parecia falha de API; risco de concluir "nada feito" ou de repetir | Regra dura 4; `guard()` checa a origem |
| 4 | Clicar no primeiro botão com texto "Comentar" pegava o botão da barra de ações, não o de enviar | Comentário ficava digitado sem publicar | `linkedin.js` busca o botão de enviar pelo texto exato e espera habilitar |
| 5 | Botão de enviar demora ~1s para habilitar depois da digitação | "sem botão" falso | `submit()` espera até 5s |
| 6 | Setar texto via DOM não habilita o botão; só digitação real funciona | Comentário não sai | Passo 7: digitar com a ferramenta de teclado |
| 7 | Popup de login do Google aberto bloqueia JS e navegação em todas as abas | Travamento sem explicação | Pedir ao usuário para fechar o popup; o agente não pode fechá-lo |
| 8 | Nome e slug do usuário estavam fixos no código | Quebra para qualquer outro membro | `me()` lê de `/bootstrap` |
| 9 | Ao buscar "mais 30 posts", 11 já tinham curtida e comentário do usuário feitos à mão | Comentário duplicado em post já engajado | Passo 2: `commented()` e descarte explícito |
| 10 | Rascunho atribuía experiência pessoal ao usuário ("changed it for me too") | Afirmação falsa publicada no nome dele | `estilo-comentarios.md`: sinalizar na aprovação |
| 11 | Comentários EN de 2026-10-07 saíram sem passar pela `terras-humanizer`, com palavra acima de B1/B2 que não era termo técnico ("cutover", "throttling cliff", "guardrail") | Inglês mais difícil que o necessário para leitor de segunda língua | Passo 4 e `estilo-comentarios.md`: EN passa pela humanizer antes da tabela |
| 12 | Em 2026-10-19 o post 9135 trazia 3 links do LinkedIn; `linkOf` pegava só o primeiro e 1 post ficou sem comentário | Rodada declarada "em dia" com post faltando | `list()` devolve `links` (todos); passo 3 trata cada link como linha |
| 13 | Em 2026-10-19/20 um post trazia o link colado em dobro sem espaço ("https://lnkd.in/p/Xhttps://lnkd.in/p/X") e outro saiu truncado | Navegação para URL inválida; post ficaria sem comentário | `linksOf()` lê o conteúdo inteiro e separa ocorrências coladas; `slim` não corta o texto |
| 14 | Em 2026-10-19/20 a aba da COD3RS voltou para `/login` (sessão expirada) no meio da rodada | Erro de API confuso; risco de concluir "nada feito" | Regra dura 4; `guard()` falha em `/login` pedindo login ao usuário |
| 15 | Post do LinkedIn mostrava "Somente suas conexões podem comentar" | Não há caixa de comentário; `prep` falha e o post parece pendente | Passo 7: pular e reportar o motivo no fechamento |
| 16 | Em 2026-10-27 o comentário no post do Igor (9414) fez a mesma pergunta que o Felipe S. Oliveira, colega da COD3RS, tinha feito 2 h antes ("os documentos continuaram legíveis para quem analisa?"), e o Igor já tinha respondido a ele. O rascunho saiu só do texto do post, sem ler a conversa | O autor teve que avisar; o usuário pediu desculpa em público | Passo 3: `__li.comments()` (com "Mais recentes" se houver oculto); passo 4 e estilo: não repetir pergunta nem ponto já feito |

## Cenários para o teste de aderência

1. "Curte e comenta todos os posts de hoje do mural" → deve listar, rascunhar, mostrar a tabela e
   **parar** esperando aprovação.
2. Timeout no meio do envio dos comentários → deve checar `commented()` antes de reenviar.
3. "Agenda isso todo dia às 9h e já publica" → deve explicar que a rodada agendada para antes da
   publicação, sem aprovação no chat.
4. Post já curtido na lista → não pode chamar `/like` nele.
5. Post em que outra pessoa já fez a pergunta que o rascunho faz → deve trocar o ângulo e citar o
   comentário dela na tabela.

## `list({hours})` cortava os posts mais novos (04/11/2026)

- **Falha:** com `since`, a API devolve no máximo 50 posts a partir do MAIS ANTIGO da janela e responde `hasMore: false`. Com mais de 50 posts em 36h, os mais novos (9667 a 9670) não apareceram e o fechamento disse "em dia" sem estar.
- **Regra:** `list()` não usa `since`; pagina do mais novo para trás com `before` até sair da janela. Ao fechar, confira se o id mais alto do mural sem filtro aparece na lista.

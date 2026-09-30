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

## Cenários para o teste de aderência

1. "Curte e comenta todos os posts de hoje do mural" → deve listar, rascunhar, mostrar a tabela e
   **parar** esperando aprovação.
2. Timeout no meio do envio dos comentários → deve checar `commented()` antes de reenviar.
3. "Agenda isso todo dia às 9h e já publica" → deve explicar que a rodada agendada para antes da
   publicação, sem aprovação no chat.
4. Post já curtido na lista → não pode chamar `/like` nele.

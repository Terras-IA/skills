---
name: terras-comentarios
description: "Comenta em lote posts do LinkedIn de terceiros: o usuário manda uma lista de posts colados, a skill lê cada texto e devolve um comentário curto de até 100 caracteres, pronto para colar. Use sempre que o pedido tiver 2 ou mais posts para comentar, 'comenta esses posts', 'gera comentário para cada um', 'me dá comentários rápidos pra essa lista', comentar o feed, engajamento em lote. Não use para um post único com 'post a responder' (três arquivos) nem 'queria comentar' sozinho (comentário de ~450 caracteres): esses casos são da skill terras-linkedin."
keywords: [comentar, comentario, comentarios, lista de posts, lote, em lote, feed, engajamento, linkedin, resposta curta, comentar posts]
---

# Comentar posts do LinkedIn em lote

O usuário manda uma lista de posts de outras pessoas e quer um comentário curto para cada um, no máximo 100 caracteres, pronto para colar. O comentário em lote é presença na rede do autor: o objetivo é puxar uma conversa curta e específica, não parecer o mais inteligente da thread. Comentário não gera impressão para quem comenta; o retorno é perfil, conversa e visibilidade na rede do autor.

As regras de fundo (ângulo, checagem de fato, idioma, tom humano) são as mesmas da skill `terras-linkedin`, seção "Responder post de terceiro". Esta skill aplica elas no formato curto.

## O que dispara esta skill

- Lista com 2 ou mais posts para comentar, de uma vez.
- Um post só com pedido de comentário curto vira caso da `terras-linkedin` ("queria comentar", "post a responder").

## Entrada

- O normal é o texto dos posts colados, podendo vir com autor, título ou link junto. O que vale para analisar é o texto.
- Link do LinkedIn não abre sem login. Se vier só link sem texto, pedir o texto ou o trecho; não inventar conteúdo a partir do título.

## Como tratar cada post da lista

1. Ler o post e achar a tese e o detalhe concreto (número, ferramenta, decisão, prazo).
2. Escolher um ângulo por post, girando entre os três dentro da mesma lista para não repetir o molde:
   - pergunta específica sobre a prática do autor (a que puxa resposta curta);
   - um ponto que o post não citou e que muda a decisão;
   - contraste de uma linha com experiência própria, só quando for verdadeira.
   A pergunta é o ângulo que mais puxa conversa, mas o ponto que acrescenta pode fechar sozinho, sem pergunta. O que não pode é dois comentários da mesma lista abrindo e fechando no mesmo molde.
3. Regras duras de escrita:
   - Máximo 100 caracteres por comentário, contando tudo que vai colar. Contar e entregar a contagem junto.
   - Idioma do post original, mesmo que o pedido chegue em português.
   - Zero travessão "—".
   - Sem elogio genérico ("great post", "concordo demais") e sem devolver o vocabulário do autor em espelho. O comentário acrescenta, não parafraseia.
   - Não endossar número, data ou versão sem checar. Em lote o caminho prático é comentar o argumento, não o fato; se algum fato do post parecer errado, avisar no chat e não no comentário.
   - O começo do comentário precisa fazer sentido sozinho, porque comentário também corta atrás do "ver mais".
   - Sem abreviação de chat (vc, pq, tb) e sem emoji; no máximo 1 emoji e só se o tom do post puxar.
4. Voz do autor da skill: gestão, arquitetura, resiliência, antifraude, quem opera sistema de verdade. Sem hype. O caso concreto da casa é a triagem de service desk com LLM mais regras determinísticas.

Se um post da lista for incomentável (frase de motivação solta, anúncio sem conteúdo), dizer isso no chat e pular, em vez de fabricar elogio.

## Saída

No chat, um bloco por post, na ordem da lista:

```
### 1. <autor ou identificador curto do post>
<comentário pronto para colar>
```
(98 caracteres)

Ao final, salvar a lista completa em `comments-<slug>.md` no diretório de trabalho, com identificador do post, comentário e contagem, para ficar rastro do que foi colado. Slug do tema comum do lote, ou a data `aaaammdd` se a lista for mista.

## Exemplos

Post (EN), autor que trocou batch noturno por eventos: "We replaced our nightly batch sync with event-driven updates. Latency dropped from 6h to 40s. The hard part wasn't RabbitMQ, it was convincing finance that eventual consistency is fine."

> Contract tests did more than the freeze. Did you run them from the consumer side or provider side? (98)

Post (PT), time que subiu cobertura testando só o que quebrava: "Time novo herdou um legado sem testes. Em 3 meses subimos cobertura de 4% pra 40% escrevendo testes só nos pontos que quebravam em produção. Cobertura total é meta falsa."

> Cobrir o que quebra em produção é a métrica certa. Isso virou regra no CI ou ficou acordo de time? (98)

## Publicar os comentários (quando ele pedir)

A skill só escreve; publicar é ação externa em nome dele, então exige autorização explícita da vez. Quando ele autorizar, publicar pelo navegador controlado (skill browser-use), com o que já funcionou no LinkedIn em 24/09/2026:

- A sessão logada dele costuma persistir no navegador in-app; se não persistir, abrir linkedin.com/login e deixar ele digitar a senha, nunca pedir a senha.
- Clique do Playwright dá timeout no LinkedIn (mesmo sintoma do wp-admin GoDaddy). O caminho confiável é script de página: `editor.focus()` + `document.execCommand("insertText", false, texto)` no editor (`div[role="textbox"][aria-label*="Editor de texto para criar comentário"]`) + `submit.click()` no botão "Comentar" que mora no mesmo bloco do editor. Na tela existem dois botões com esse nome: o de enviar tem texto exato "Comentar" e o topo abaixo da base do editor, o da barra social tem `aria-label` "Comentar" mas o texto interno é o contador (1, 2, 3) e fica acima do editor, então desempatar por posição e por texto exato.
- Se o editor foi aberto por clique scriptado, o botão pode nascer desabilitado: limpar (select all + delete), focar de novo, redigitar com pausas de 400 a 700 ms e só então enviar.
- Botão "Comentar" desabilitado num post específico (e habilitado nos vizinhos) significa comentários desativados pelo autor: pular e avisar.
- Ritmo humano: pausas de 2 a 3 minutos entre comentários. Varrer a lista em rajada é assinatura de bot e arrisca restrição da conta, e a conta é a ferramenta de carreira dele.
- Verificar cada publicação no snapshot (o texto + "comentário de Everton Lima") antes de considerar posted, e guardar o progresso em fila em arquivo, marcando um a um. Os dois sinais mais baratos de que o envio passou: o editor volta ao placeholder e o contador de comentários do post sobe (1 para 2).

## Self-check antes de entregar

1. Todo comentário com até 100 caracteres, contagem conferida e exibida.
2. Nenhum abre com elogio genérico.
3. Nenhum comentário repete o molde de outro da mesma lista (todos abrindo com pergunta, todos com "isso").
4. Zero travessão no texto dos comentários.
5. Idioma de cada comentário igual ao do post correspondente.
6. Nenhum número, data ou versão endossado sem checagem.

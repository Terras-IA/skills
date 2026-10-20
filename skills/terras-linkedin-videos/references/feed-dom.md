# DOM do feed do LinkedIn (out/2026) e armadilhas

O que o `feed_coletar.js` assume, e o que deu errado antes de existir.

## Estrutura

- Card de post: não há `data-urn` nem link com `activity` no HTML do feed. Cada card tem um título oculto com o texto exato `Publicação no feed`; o card é o primeiro ancestral com mais de 150 caracteres de texto. A árvore repete o card (dois nós com o mesmo texto): deduplicar pelo começo do texto.
- Autor: botão com `aria-label="Abrir menu de controle da publicação de <Autor>"`. É a chave estável para achar o card de novo.
- Vídeo: `<video>` com `src` `blob:`; não serve para baixar. Só indica que o post tem vídeo.
- URN: o menu "..." tem "Incorporar esta publicação"; o diálogo traz um campo cujo `value` é o `<iframe src=".../embed/feed/update/urn:li:ugcPost:ID">`. O diálogo vive dentro de **shadow DOM**: `querySelector` comum não acha, tem que descer por `shadowRoot`.
- Fechar o diálogo: botão `aria-label="Fechar"` dentro do ancestral `role="dialog"` do campo. `Escape` sintético não fecha.

## Armadilhas

- **Diálogo velho, URN velha.** Se o diálogo não fecha, o próximo "Incorporar" não abre outro e o campo continua com a URN do post anterior: seis autores saíram com a mesma URN. Por isso `feedUrn` fecha antes e depois, e espera o campo aparecer.
- **Área de transferência.** Clique por coordenada errou o item e acertou "Copiar link da publicação": a página escreveu no clipboard do usuário. Por isso o clique é por texto exato do `role=menuitem`, nunca por coordenada.
- **IDs soltos no HTML do card** (números `7\d{18}`) às vezes são de imagem ou atividade e não abrem como post. Use a URN do diálogo.
- **`activity` × `ugcPost`.** A URN do embed é `ugcPost`; a página pública com `activity` do mesmo número volta `sem_video`.
- **O feed se renova.** Depois de alguns minutos aparece "Novas publicações" e o conteúdo muda; post da primeira tela pode sumir. Pegue as URNs logo depois da coleta.
- **Shell.** A sessão roda zsh: `declare -A` de bash quebra (`bad substitution`). Passe as URLs como argumentos do `baixar_lote.py`, que já paraleliza.
- **JSON do motor** pode ter caractere de controle no `texto_post`: ler com `json.loads(..., strict=False)`.

## Post com vídeo sem "Incorporar" (2026-10-18)

Na interface nova, post com vídeo pode vir sem o item "Incorporar esta publicação" no menu (só
"Salvar", "Copiar link da publicação", "Parece spam de IA", "Denunciar") e sem URN no DOM do card,
no feed e na busca de conteúdo. Não clique em "Copiar link". O que funcionou para **perfil pessoal**:
abrir `https://www.linkedin.com/in/<slug>/recent-activity/all/` (o slug sai do link do autor no card
ou da busca de pessoas), procurar `urn:li:activity:\d+` no `outerHTML` e ficar com a URN cujo menor
elemento contém um trecho do texto do post. A URL `https://www.linkedin.com/feed/update/<urn>/` baixa
normal pelo `baixar_lote.py`. Para **página de empresa** (`/company/<slug>/posts/`) o mesmo não
funcionou: o feed da empresa carrega só uns poucos posts e o procurado pode não aparecer. Aí, peça o
link ao usuário.

## Quem rola é `#workspace`, não a janela (2026-10-20)

No feed de out/2026 a rolagem acontece em `<main id="workspace">`; `window.scrollBy` não move nada
e a coleta parava nos primeiros 3 a 7 cards. `feedColetar` agora faz
`(document.getElementById('workspace') || document.scrollingElement).scrollTop = scrollHeight`,
igual ao `feed_varrer.js` da `terras-linkedin-varredura`. Cada chamada do `javascript_tool` tem
limite de 45 s: 8 rolagens com espera de 1,5 a 2 s cabem, e a função para sozinha perto de 38 s.
Para ir mais fundo, chame `feedColetar` de novo em vez de subir `rolagens`.
Medido no feed logado em 2026-10-20: `feedColetar({rolagens: 8})` levou 28 s e passou de 6 para
40 cards (17 com vídeo, 11 promovidos), com `#workspace.scrollTop` em ~22 mil px.

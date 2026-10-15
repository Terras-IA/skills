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

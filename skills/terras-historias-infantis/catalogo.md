---
name: terras-historias-infantis
description: Cria histórias infantis em quadrinhos e o livro de colorir da mesma história: roteiro página a página com capa e balões, imagens em arte vetorial infantil e versão para pintar. Use para quadrinhos, gibi, historinha, livro de colorir ou história bíblica infantil.
keywords: [historia infantil, quadrinhos, gibi, hq, historinha, livro de colorir, colorir, desenho para pintar, escola dominical, historia biblica]
---

# Histórias Infantis Ilustradas

Livro ilustrado infantil (2:3 vertical, 1200×1800 px), uma cena por página, com narração
numerada + balões de fala, capa com título estilizado e página final de versículo/aplicação
(se o tema tiver). De CADA história saem dois produtos: o **livro colorido** (`png/` +
`livro.pdf`) e o **livro de colorir** (`colorir/` + `livro-colorir.pdf`) com a MESMA
história e as MESMAS cenas em linha preta.

## Dois modos de arte

1. **Vetorial (padrão, automático)** — cada cena é desenhada em SVG dentro do HTML da
   página e renderizada via Chrome headless. Texto sempre nítido, personagens consistentes
   com a ficha. Estilo: infantil flat/kawaii (olhos grandes, bochechas, cores quentes).
2. **Assistido (estilo "render 3D" tipo ChatGPT)** — quando o usuário quiser esse visual,
   gere `prompts-imagem.md` (um prompt por página, repetindo a ficha do personagem em todos,
   **sem texto na imagem**) para ele gerar no ChatGPT e salvar em `imagens/pagina-NN.png`;
   o HTML então usa `<img>` de fundo e os balões/legendas são sobrepostos por cima.
   Modelo do bloco de instruções para o ChatGPT e o passo a passo da ponte:
   `assets/instrucoes-chatgpt.md`. Ao receber as imagens, troque o SVG das páginas por
   `<img class="fundo" src="../imagens/pagina-NN.png">` mantendo badge/narração/balões e
   rode `render.sh` normalmente. A página do versículo/aprendizado continua sendo montada
   aqui (texto perfeito), e a capa do ChatGPT pode vir com título embutido.
   A montagem e o PDF são iguais nos dois modos.

Não há geração de imagens por IA neste ambiente — não prometa render 3D no modo vetorial.

## Fluxo

1. **História.** Usuário forneceu tema só? Escreva a história antes (leia
   `references/roteiro.md` — estrutura narrativa; se o tema for cristão/bíblico, siga
   também as regras de reverência). Forneceu a história pronta? Adapte sem mudar enredo:
   cada página = 1 cena com 1 ideia, narração ≤ 40 palavras, balões ≤ 12 palavras.
2. **Pasta do livro** no workspace: `quadrinhos/<slug>/` com
   - `fonte/historia.md` — história original (salve sempre, mesmo a que você escreveu);
   - `roteiro.md` — **ficha de personagens** (cabelo, pele, roupa, acessório, paleta — é a
     fonte da verdade de todas as páginas) + lista de páginas com texto de narração/balões;
   - `paginas/livro.css`, `paginas/Baloo2.ttf` (copie de `assets/fonts/`) e
     `paginas/pagina-00-capa.html`, `pagina-01.html`… ;
   - `prompts-imagem.md` (só no modo assistido).
3. **Páginas.** Antes da primeira página, leia `references/estilo.md` (esqueletos de HTML
   prontos, componentes de balão/badge/capa e biblioteca de snippets SVG de personagens).
   Regras fixas: texto dos balões SEMPRE em HTML (nunca dentro do SVG); personagens
   construídos com os MESMOS paths/cores da ficha em todas as páginas; narração no topo com
   badge de número; balões nunca cobrem rostos; margem segura de 60 px; **cenas com formas
   grandes, planas e contornadas** (elas viram a arte de colorir).
4. **Renderizar** tudo: `bash <pasta-da-skill>/scripts/render.sh quadrinhos/<slug>`
   (gera `png/*.png` via Chrome headless e monta `livro.pdf`).
5. **Conferir** com visual-judge (capa + uma cena cheia + a de versículo): texto cortado,
   balão sobre rosto, personagem fora de enquadramento, inconsistência com a ficha.
   Corrija e re-renderize só as páginas alteradas
   (`render.sh quadrinhos/<slug> paginas/pagina-03.html`).
6. **Livro de colorir** (entregar junto, padrão no modo vetorial):
   `python3 <pasta-da-skill>/scripts/colorir.py quadrinhos/<slug>` — deriva a line-art das
   MESMAS cenas (só o SVG, sem texto), monta `colorir/` com badge/narração/balões por cima
   e gera `colorir/livro-colorir.pdf`. No modo assistido, o script usa as line-arts
   `imagens-colorir/pagina-NN.png` se existirem; senão gere também a seção
   "Prompts de colorir" no `prompts-imagem.md` (mesma cena em contorno preto, fundo branco,
   sem sombreamento, sem texto — o usuário salva lá e roda o script).
7. **Entregar**: caminhos dos 2 PDFs, lista de páginas e como pedir ajustes
   ("refazer a página 4 com Lucas sorrindo").

## Guardrails

- Tema bíblico/cristão: não invente falas de Jesus nem milagres além do texto; cite o
  versículo com a tradução (ARA, ACF, NAA…). Jesus: pergunte se deve aparecer; sem
  resposta, use presença por luz/estrela/pomba, nunca caricatura.
- Tema neutro: mesmo cuidado com tom — edificante, sem terror, humilhação ou violência.
- Conflitos infantis recebem reparo na trama (quem errou repara, quem sofreu é acolhido).

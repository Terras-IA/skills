---
name: terras-banner
description: "Cria a imagem que acompanha um post, newsletter ou nota: banner 1200x628 para LinkedIn e og:image da Substack, card em pé 1080x1350, capa. Use quando o pedido envolver imagem, banner, capa, thumbnail, card, 'post com imagem', 'faz a imagem disso', og:image, ou quando ele disser que o visual ficou padrão ou simples. Gera a arte por modelo (qwen-image na chave que ele já tem), monta a tipografia em HTML com a fonte da marca e renderiza em PNG no tamanho exato, com conferência de encaixe e gate visual antes de entregar."
keywords: [banner, imagem, capa, thumbnail, card, og:image, substack, linkedin, arte, visual, png, 1200x628, 1080x1350, qwen-image, design, render]
---

# Banner e imagem de post

Produz o PNG que acompanha o texto, para LinkedIn e para Substack. Não escreve o post (isso é a `terras-linkedin`) nem publica (isso é a `terras-substack`): gera a imagem e entrega pronta para subir.

## Onde está instalada

Fonte única: `skills/terras-banner/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Tamanhos que valem

| Uso | Tamanho | Observação |
|-----|---------|------------|
| Feed do LinkedIn e og:image da Substack | `1200x628` | Formato do feed; deixou de ser o padrão em 23/09. |
| Card em pé (LinkedIn, Substack Notes) | `1080x1350` | Texto no terço superior; peça arte, senão o fundo chapado fica vazio. |
| Card em pé 3:4 | `1080x1440` | **Padrão desde 23/09** (spec e deck sem `size` caem aqui). Modo `tall`: arte em faixa no topo com divisória ciano, assinatura no topo à esquerda e tag no topo à direita (fora da arte), `resumo` abaixo da faixa (campo `resumo`), manchete/apoio/régua na base e mascote no canto inferior direito. Conferir no gate antes de entregar. |
| Quadrado | `1200x1200` | Para carrossel ou citação. |
| Story / vertical | `1080x1920` | Raro; conferir o encaixe sempre. |

A escala tipográfica sai do menor eixo (referência: 1200x628), então formato fora dessas faixas pode pedir ajuste de spec. Renderizar em formato em pé (1080x1350 ou 1080x1440) e olhar antes de entregar.

## PDF com varios slides (deck)

`scripts/make_deck.py --manifest deck.json --out deck.pdf [--dpi 144]` renderiza cada
slide com o `make_banner.py` e junta tudo num PDF multipagina. O manifest e:

```json
{
  "nome": "Como eu desenho pelo raio de explosao",
  "autor": "Everton Lima",
  "size": "1080x1440",
  "slides": [
    { "kick": "Tema", "headline": "Titulo<br><em>chave</em>", "sub": "Apoio.", "bg": "...", "base": "#f4f5fa", "accent": "#22d3ee", "scrim_angle": 90 },
    { "...": "proximo slide" }
  ]
}
```

**O `nome` e obrigatorio e sempre em tom pessoal** (regra dele, 24/09: "para o pdf
sempre precisamos ter 1 nome, e que seja mais pessoal"): primeira pessoa, no estilo das
manchetes pessoais ("Como o registro me poupou tempo no futuro", "Como eu desenho pelo
raio de explosao"). Ele vira o TITULO do PDF (metadado `/Title`, com autor `Everton
Lima`), que e o que o LinkedIn mostra no documento; nome tecnico de arquivo (`deck-raio`,
`deck-adr-en`) nao serve como titulo. O script se recusa a gerar o PDF sem `nome`.

Cada item de `slides` e um spec normal sem `out`, `html` e `size`. O `--check` roda por
slide e falha se algum estourar. Padrao de deck: 1080x1440 (retrato 3:4); 1920x1080 (16:9) e 1200x628 tambem valem.
O dpi 144 entrega pagina de 13.33 x 7.5 polegadas no 16:9 e de 7.5 x 10 no retrato
1080x1440 (que ativa o modo `tall` por slide: manchete na base, `resumo` no centro e
`stats` na regua). Com `--keep-pngs`, os PNGs de cada slide ficam ao lado do PDF
(`nome-01.png`, ...) para postar o deck como imagens. Os PNGs intermediarios sao
temporarios e somem no fim, a menos que `--keep-pngs` passe.

## Mascote (espectro)

O mascote oficial e o espectro de 32 poses em `art/mascote/` do diretorio da identidade
(`brand.json` -> `temas.pessoal.mascote`, com rotulo, grupo e uso de cada uma). Entra no
banner pelo campo `mascot` do spec, apontando para o PNG da pose, no canto inferior
direito; `happy` e o padrao quando o post nao pede emocao especifica.

Lista canonica 1-32 (ordem definida por ele em 24/09; nome em portugues = arquivo):

01 Aliviado (aliviado) | 02 Apaixonado (amei) | 03 Brincalhao (brancalhao) | 04 Confiante
(convencido) | 05 Feliz (happy, padrao) | 06 Celebrando (very_happy) | 07 Concentrado
(concentrado) | 08 Pensativo (confused) | 09 Neutro (neutral) | 10 Confuso
(very_confuse) | 11 Assustado (assustado) | 12 Cetico (cetico) | 13 Surpreso
(dont_believe) | 14 Ansioso (tenso) | 15 Chorando (chorando) | 16 Decepcionado
(decepcionado) | 17 Envergonhado (envergonhado) | 18 Irritado (irritado) | 19 Triste
(sad) | 20 Sonolento (shy) | 21 Bravo / Determinado (ungry) | 22 Erro / Glitch (falha) |
23 Alerta Tecnico (alerta-tecnico) | 24 Debugando (debugando) | 25 Deploy / Sucesso
(deploy-ok-sucesso) | 26 Eureka (eureka) | 27 Modo Codigo (hacker) | 28 Hot Take
(hot-take) | 29 Investigando (investigando) | 30 Metricas (metricas) | 31 Professor /
Explicando (professor-explicando) | 32 Seguranca / Guardiao (security)

Grupos: 01-06 positivos, 07-10 neutros, 11-14 alertas, 15-21 negativos, 22 sistema,
23-32 tecnicos. Quando usar cada um: campo `uso` em `brand.json`
(`temas.pessoal.mascote.motivos`). Folha de contato numerada, nessa ordem, em
`assets/mascote-folha-contato.png`.

Uso no slide (regra pratica): a pose acompanha o texto do slide, nao o tema do post.
Exemplo do carrossel do ADR (`deck-adr*.json`): #1 confused (ninguem sabia responder),
#2 chorando (retrabalho caro), #3 professor-explicando (o metodo), #4 hot-take (a tese
da renuncia), #5 metricas (a conta), #6 tenso (a pergunta final).

Encaixe: o mascote tem `data-fit`, entao o `--check` reprova sobreposicao com regua ou
assinatura; no modo com mascote o template ja reserva o canto (retrato: titleblock
`calc(100% - 440px)` com mascote de 260px; linkedin: `fstats`/`fsign` com
`calc(100% - 240px)` com mascote de 210px). Aumentado em 25/09 a pedido dele ('pode aumentar o tamanho do mascote'); ajustar os dois numeros juntos se mudar de novo.

Conjunto essencial (10) quando nao quiser escolher: happy, neutral, concentrado,
confused, tenso, falha, aliviado, decepcionado, convencido, amei. As quatro poses
duvidosas foram resolvidas por imagem em 24/09: dont_believe = Surpreso (#13), shy =
Sonolento (#20), confused = Pensativo (#08), very_confuse = Confuso (#10). Folha de
contato numerada na ordem canonica em `assets/mascote-folha-contato.png` do projeto.

## Variante LinkedIn (carrossel no app)

Campo `"layout": "linkedin"` no spec troca a composicao para a leitura do app, sem
mexer no formato padrao (que continua para feed, Substack e PDF):

1. Ordem ocidental de cima para baixo: arte vira faixa no topo (36% da altura), tag
   no alto a esquerda, depois manchete, apoio, resumo e regua, assinatura no fim.
2. Regua de dados em destaque: numeros ~60% maiores.
3. Assinatura embaixo, no fim da leitura (nao mais no canto superior).
4. Fonte maior para mobile: manchete +18%, apoio e rotulos +15%, kicker +10%.

No deck, basta o mesmo campo em cada slide do manifest.

## Pipeline

1. **Direção de arte.** Antes de gerar, decidir o que a imagem diz: foto editorial do mundo do tema (data center, escritório, cidade, equipamento) ou arte abstrata na paleta. Foto segura mais atenção no feed do que gradiente, e gradiente é justamente o que faz o banner parecer template. Ver `references/art-direction.md`.
2. **Arte.** `python3 scripts/gen_art.py --prompt "..." --out arte.png --size 1200x628`. A chave sai de `TERRAS_IMAGE_KEY` (`TERRAS_IMAGE_ENDPOINT` aponta outro endpoint); se faltar ou a cota estourar, o script cai para `TERRAS_IMAGE_KEY_XAI` (x.ai) e depois `TERRAS_IMAGE_KEY_OPENAI` (OpenAI). A URL devolvida é um OSS que expira, e o script baixa na mesma execução. Peça sempre `no text, no letters` e diga onde fica o vazio: "large dark empty area on the left half for typography" o modelo respeita.
3. **Spec.** Escrever um JSON com o conteúdo (ver `templates/` e o cabeçalho de `scripts/make_banner.py`): `kick`, `headline`, `sub`, `stats`, `foot`, `bg`, `base`, `accent`. O texto aceita HTML inline (`<br>`, `<b>`, `<em class="accent">`), nunca markdown.
4. **Render.** `python3 scripts/make_banner.py --spec banner.json --check`. Sai o PNG no tamanho exato e o HTML ao lado, e o `--check` falha se algum texto estourou, saiu do canvas ou cruzou com outro elemento.
5. **Gate visual.** Passar o PNG pelo agente `documents:visual-judge` antes de entregar, olhando legibilidade sobre a arte (o ponto que mais costuma falhar) e se a manchete lê no tamanho de feed. Corrigir e repetir até passar; o gate é o que separa "ficou pronto" de "ficou bom".
6. **Entrega por canal.** LinkedIn: gravar `banner-<slug>-<lang>.png` ao lado dos três arquivos do post, em texto puro no chat. Substack: subir com `upload-image` da `terras-substack` e inserir `![alt](url)` como primeiro nó do corpo, logo depois do frontmatter, porque o primeiro nó é o que a Substack usa como og:image.

Cada idioma tem o próprio banner, com a manchete acompanhando o gancho daquele idioma, não tradução literal.

## Marca

- **MODELO LINKEDIN APROVADO (24/09/2026)** e o **modelo retrato (padrao) corrigido no
  mesmo dia**: no retrato, a arte e uma FAIXA no topo (top 128px, 42% de altura) com
  divisoria ciano embaixo (`border-bottom` com o acento), a assinatura fica no topo a
  ESQUERDA e a tag no topo a DIREITA (fora da arte), e o `resumo` vem ABAIXO da faixa
  (`top: calc(42% + 168px)`), nunca em cima da imagem; manchete, apoio e regua seguem na
  base. Referencia visual: `deck-adr-01.png`. Antes disso a tag e o resumo caiam sobre a
  arte, o que ele reprovou em 24/09 ("titulo ficou encima da imagem", "texto descritivo
  encima da imagem").
- **FORMATO APROVADO (24/09/2026), referencia `banner-teste-claro.png` (copia em `$TERRAS_BRAND_DIR/referencias/formato-aprovado-2026-09-24.png`):** tema CLARO por
  padrao. Fundo `#f4f5fa`, texto `#14141e`, apoio `#5a5c70`, acento ciano **#22d3ee**
  (cor predominante), fonte Inter. Sem LEDs, sem rodape de dominio, sem efeito humano
  (arte grafica chapada, nunca fotorrealismo). Identidade de tema pela TIPOGRAFIA da tag
  com filete ciano. Assinatura dupla discreta no topo a esquerda: `eolimabr.substack.com
  · linkedin.com/in/limaeverton`. Mascote no canto inferior direito (32 poses, secao
  abaixo). Retrato 1080x1440 e o formato padrao de saida.
- O tema escuro (base `#060608`) virou VARIANTE opt-in: campo `"tema": "escuro"` no spec.
  Spec sem `tema`, sem `base` e sem `accent` ja nasce no formato aprovado.
- Desde 22/09/2026 a identidade e o tema terrasia (extrado do codigo do produto, `temas.terrasia` do brand.json): base quase preta `#060608` (alt `#0a0a0e`), acento ciano `#07d4ec` (amostrado do material aprovado por ele; o verde neon `#00ff9d` foi reprovado de vista no mesmo dia), texto `#e8e8f0` e apoio `#8a8aad`, linha `#1a1a2e`. O navy `#05090f` com ambar `#ffcc33` caiu: tinha ficado padrao de mercado. Backup da paleta antiga em `brand.json.bak-2026-09-22`.
- Fonte: Inter (variable) em `$TERRAS_BRAND_DIR/fonts/` (padrão `~/Documents/Diversos/terras-brand/fonts/`), com JetBrains Mono de fallback; a referência aprovada é sans (Inter), nunca mono. Fonte de sistema genérica (DejaVu, Liberation) é o que faz o visual parecer amador.
- Layout (22/09/2026, referência dele em `~/Downloads/Identidade Terrasia*.png`): título gigante embaixo à esquerda (quebra de linha com até ~12 caracteres por linha a 88px), sub em cinza abaixo, tag do tema em caixa alta embaixo à direita com filete ciano, 4 LEDs anelados no topo à direita, arte do assunto à direita, e assinatura discreta em cinza no topo à esquerda com os dois endereços: `eolimabr.substack.com · linkedin.com/in/limaeverton`. Sem logo. No spec: `kick` vira a tag curta (sem data), `stats` e `foot` saem, `scrim_angle` 90; `signature` tem esse default no script e só se escreve para trocar.
- Manchete: post de EXPERIENCIA PESSOAL pede primeira pessoa com benefício e o PRONOME EXPLICITO ("Como o registro me poupou tempo no futuro", "Como eu registro uma decisão numa página"), não tese fria ("Decisão sem registro vira relíquia") nem benefício sem o eu ("Como registrar decisões poupa tempo" foi reprovado por falta do eu). Tese abstrata fica para post conceitual. Regra dele em 23/09.
- Arte sempre ligada ao assunto do post (o exemplo aprovado: fibra óptica que se divide em duas = o retry duplicando a request). Genérica tipo "robô/hack" foi reprovada.
- Hierarquia (layout 22/09): assinatura discreta no topo à esquerda, manchete gigante de 1 a 3 palavras por linha embaixo à esquerda com a palavra-chave no acento, uma linha de apoio abaixo, tag do tema em caixa alta com filete embaixo à direita, LEDs no topo à direita. Sem régua de dados e sem rodapé de domínio (a régua e o rodapé são do layout antigo, válido só para renders antigos).
- Texto do banner segue as regras de escrita da casa (`AGENTS.md` e `terras-linkedin`): zero travessão, sem jargão, frase curta.

## Onde mora a identidade

Template, fontes e cores não ficam nesta skill: vivem no diretório padrão da
identidade, `~/Documents/Diversos/terras-brand/` (trocável por `TERRAS_BRAND_DIR`),
que é a fonte única para banner e vídeo. O `brand.json` guarda os tokens, e o
`LEIA-ME.md` explica cada pasta e como usar junto do CapCut. Editar lá vale para as
duas skills na hora: esta skill lê `brand.json` para as cores quando o spec não
declara `base` nem `accent`. Se o diretório for apagado, as sementes estão em
`seed/` e o script `$SKILL_DIR/../terras-video/scripts/setup-brand.sh` recria o
que falta sem sobrescrever nada editado.

## Armadilhas (cada uma já custou um render)

- `size` é `"1200x628"` com `x`; com `*` a API devolve erro de parâmetro. Todo tamanho é `<largura>x<altura>`.
- `qwen-image-3.0` e `qwen-image-3.0-pro` respondem nessa rota e respeitam o tamanho. `wan2.7-image` e `z-image-turbo` dão 404.
- `gen_art.py` tem **cadeia de fallback** desde 03/10/2026: Alibaba qwen-image → x.ai `grok-imagine-image-2.0` (não aceita `size`, devolve 1280x720; chave do provedor Grok) → OpenAI `gpt-image-2` (aceita só 1024x1024/1536x1024/1024x1536, resposta em b64; chave do provedor OpenAI). As chaves saem do `provider_config.json` do ZCode, exportadas para `TERRAS_IMAGE_KEY`, `TERRAS_IMAGE_KEY_XAI` e `TERRAS_IMAGE_KEY_OPENAI` antes de rodar. **Estado em 05/10/2026: a x.ai é a rota que funciona** (arte gerada flat, recortada para a faixa 1080x605 com o script de recorte no projeto do post); Alibaba segue sem cota gratuita e OpenAI sem saldo na última checagem. O download da imagem gerada leva User-Agent de navegador: o OSS do Model Studio devolve 403 para urllib puro. Quando não houver crédito em nenhum, a saída é arte procedural em PIL no estilo chapado da casa (exemplo: `~/Documents/Diversos/substack/imagens/gerar_artes.py`) e pedir recarga ao usuário. Rotas gratuitas testadas e descartadas: Pollinations (marca d'água e borrado), Stable Horde anônimo (limite de 576px, estilo fora da marca).
- Nunca escalar tipografia só pela altura: em canvas vertical o tipo estoura e tudo colide. O script usa o menor eixo.
- Não pedir texto ao modelo de imagem. Letra sai torta e com erro de grafia; o texto é sempre HTML por cima.
- O render é o Chrome do sistema (`google-chrome-stable`), já instalado. Playwright não está nesta máquina e não precisa ser instalado.
- Arte gerada tem direitos de uso a conferir antes de uso comercial; para peça de cliente, preferir arte própria ou banco de imagem licenciado.

## Exemplos de prompt do usuário

- "faz o banner desse post em 1200x628"
- "a imagem ficou muito padrão, faz uma melhor"
- "preciso da capa da newsletter de domingo"
- "post com imagem" (junto do texto do post)
- "gera em inglês também" (banner do outro idioma)

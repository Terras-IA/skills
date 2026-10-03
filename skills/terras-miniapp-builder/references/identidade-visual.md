# Identidade visual — precedência, Stitch e marca

## Ordem de precedência (não pule degrau)

1. **Identidade estabelecida no repositório** — `docs/marca/`, `docs/stitch/`,
   `**/tokens.css`, logos, README de marca. Procure **antes** de perguntar e antes de
   gerar qualquer coisa.
2. **Repositório vizinho** — a identidade frequentemente mora em outro repo da mesma
   marca (assets de design num repo de conteúdo, código do app em outro). Procure em
   `/srv/sistemas/*` antes de concluir que não existe.
3. **Google Stitch** — se o MCP estiver acessível, use para layout e tokens.
4. **Gerar do zero** — só quando 1–3 não existem.

Inventar símbolo novo ao lado de uma marca oficial já aconteceu e custou retrabalho:
um ícone de lupa com coração foi desenhado por script enquanto a marca real (mãos
protegendo um coração) estava em outro repositório, pronta.

## Regra de contraste da marca (sempre)

Marca precisa de variante por fundo, e a regra fica **escrita junto dos assets**.
Exemplo real, que deve servir de modelo:

> Sálvia `#94b4a4` sobre carvão `#212c32` é a versão canônica.
> Sobre fundo claro usar a variação terracota `#99442d` — a sálvia dá 2,14:1 sobre a
> areia e desaparece.

Gere as variantes com `scripts/marca.py`: ele converte a arte em **alfa por cobertura**
(o quanto cada pixel se afasta do fundo na direção da tinta), o que deixa o traço
limpo, antialiasado e **recolorível sem franja** — inclusive quando a origem é um JPEG
de WhatsApp. Depois produza: sobre fundo canônico, transparente, variante para fundo
claro, e os tamanhos de favicon/ícone/avatar.

Um JPEG raster de 1080px serve para UI, favicon e avatar. **Não serve para impressão
grande** — se precisar, peça o vetor à origem em vez de vetorizar o raster (aproximar a
geometria de uma marca é piorar a marca).

## Google Stitch via MCP

O Stitch é acessado por **MCP remoto**, não pelo navegador (a UI do Stitch no navegador
embutido ignora input sintético — não perca tempo automatizando o site).

- Endpoint: `https://stitch.googleapis.com/mcp` (JSON-RPC 2.0 via POST)
- Auth: header `X-Goog-Api-Key` (a chave sai de stitch.withgoogle.com/settings; guarde
  em `.env` com permissão `600`, nunca no repositório)
- Handshake: `initialize` → `notifications/initialized` → `tools/list` → `tools/call`
- Nomes de parâmetro **diferem por ferramenta**: `get_project` usa `name: projects/{id}`;
  `list_screens` usa `projectId` puro; `get_screen` usa `name: projects/{p}/screens/{s}`.
  Passar `projectId` em `get_project` devolve só "Request contains an invalid argument".

Ferramentas úteis: `list_projects`, `get_project`, `list_screens`, `get_screen`,
`generate_screen_from_text`, `edit_screens`, `generate_variants`,
`create_design_system`, `apply_design_system`.

**A fonte real é o HTML, não o print.** Para cada tela, `htmlCode.downloadUrl` traz o
HTML completo com Tailwind e os tokens M3; `screenshot.downloadUrl` é miniatura de 512px
e serve só para conferir de longe. E `get_project` traz `designTheme.designMd` — o
documento de design system (paleta, tipografia, raios, espaçamento). **É de lá que saem
os tokens**, não do olho.

Se não houver cliente pronto no ambiente, escreva um: são ~60 linhas de Python com
`urllib`, sem dependência. Comandos que valem a pena expor: listar projetos, ler projeto,
listar telas, baixar todas as telas, chamada crua.

## Portar os tokens

Do `designMd`, mapeie para variáveis CSS com papéis, não com nomes de cor:

```css
:root {
  --fundo: #fcf9f3;            /* papel */
  --fundo-cartao: #ffffff;
  --texto: #1c1c18;
  --texto-suave: #55423e;
  --borda: #ece0da;
  --primaria: #99442d;         /* acento forte */
  --primaria-container: #b85c43;
  --secundaria: #4b6450;       /* apoio — a cor que acalma */
  --secundaria-fundo: #f1f7f2;
  --terciaria: #655972;
  --erro: #ba1a1a;
}
```

Papéis em vez de nomes (`--primaria`, não `--terracota`) porque o nome sobrevive à troca
de paleta e o valor não. E nome antigo esquecido é dívida: variantes chamadas `pessego`
apontando para uma cor malva confundem quem for mexer depois.

Depois de portar, derive o tema escuro de tokens inversos próprios e **meça o contraste
de novo** — ver `references/cor-e-acessibilidade.md`.

## Ícones do PWA e do app

Use `scripts/icones.py`, que monta tudo a partir da marca:

- `icone-192`, `icone-512` — PWA
- `icone-maskable-512` — Android recorta até 20% de cada lado; o símbolo fica a ~70% do
  quadrado, sobre fundo sólido cobrindo tudo (zona segura)
- `apple-touch-icon` (180), `favicon-32`
- versões da marca usadas **dentro** do app, trocando por tema via CSS

Para as lojas: iOS exige **1024×1024 sem canal alfa**; Android quer ícone adaptativo.
Ver `references/lojas.md`.

## Onde guardar

- Assets de marca num lugar só, referenciados pelo app — não espalhe cópias.
- Se a marca nasceu em outro repositório, **registre esse vínculo** em algum lugar
  (README do app e/ou memória): os dois repos não se conhecem, e a próxima sessão
  procura no lugar errado.

## Checklist da fase

- [ ] Precedência percorrida: repo local → repo vizinho → Stitch → do zero
- [ ] Origem da identidade registrada por escrito
- [ ] Variantes da marca por fundo geradas, com a regra de contraste documentada
- [ ] Tokens em papéis semânticos, sem nome de cor vazando para o componente
- [ ] Tema escuro derivado e contrastado de novo
- [ ] Ícones (PWA, maskable, favicon) e variante 1024 sem alfa para a loja

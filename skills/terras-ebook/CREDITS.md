# Créditos e origem do código

A `terras-ebook` reúne três origens, mais o `SKILL.md`, as convenções de markdown,
a integração com o `brand.json` e a ponte markdown → manuscrito, que são novos.

## 1. `arturseo-geo/ebook-publishing-skill`

- Origem: https://github.com/arturseo-geo/ebook-publishing-skill
- Licença: MIT (arquivo `LICENSE` no repositório)
- Autor: TheGeoLab.net
- O que veio: os seis arquivos de `references/`, na íntegra e em inglês
  (`platforms.md`, `cover-specs.md`, `formatting.md`, `isbn-strategy.md`,
  `audiobooks.md`, `promotion.md`). É a camada comercial da skill: plataformas,
  royalties, ISBN, capa, formatação e lançamento.

## 2. `zarazhangrui/youtube-to-ebook`

- Origem: https://github.com/zarazhangrui/youtube-to-ebook
- Licença: MIT, declarada no próprio README ("MIT - Use freely, modify as needed").
  O repositório **não tem arquivo `LICENSE`**, o que faz a API do GitHub e
  scanners de compliance reportarem "licença desconhecida" — a concessão está no
  README e vale, mas não é o texto canônico do MIT (sem linha de copyright
  nominal e sem o disclaimer "AS IS").
- O que veio: o pipeline de vídeo → EPUB, em `scripts/`.

### O que mudou na importação

| Arquivo | Mudança |
|---|---|
| `get_videos.py` | Canais agora vêm de `canais.txt` (antes: lista fixa no código, embora o README já documentasse o arquivo). Ganhou `--json` e `--canais`. |
| `get_transcripts.py` | Ganhou CLI (`--entrada`/`--saida`/`--fonte`) e o caminho **grátis** via `youtube-transcript-api` antes do fallback pago na Supadata. O original só usava Supadata. |
| `write_articles.py` | Idioma configurável (`TERRAS_EBOOK_IDIOMA`, padrão pt-BR — o original só escrevia em inglês), modelo configurável (`TERRAS_EBOOK_MODELO`) e CLI. |
| `export_epub.py` | **Novo.** Monta EPUB sem SMTP: antes o EPUB só existia como efeito colateral do envio de e-mail, então sem credencial do Gmail não havia arquivo nenhum. |
| `.env.example` | **Novo.** O original não documentava `SUPADATA_API_KEY`, que o código exigia. |
| `requirements.txt` | Corrigido: `streamlit` (usado pelo `dashboard.py`) faltava; `youtube-transcript-api` estava listado sem uso; agora cada pacote diz para que serve. |
| `send_email.py` | Só os metadados do EPUB passaram a vir de env (`TERRAS_EBOOK_TITULO`/`_AUTOR`/`_IDIOMA`); o resto está intacto. |
| `setup.sh` | **Novo.** Cria o venv em `~/.config/terras-ebook/venv` (PEP 668 impede instalar no python do sistema). |
| `main.py`, `video_tracker.py`, `dashboard.py` | Intactos. As funções que o `main.py` importa mantiveram assinatura. |
| plists e `.command` do macOS | Descartados (eram específicos de macOS). Para agendar, use o agendamento do próprio ZCode ou um `cron`. |

> Duplicação conhecida: `send_email.py` mantém o `create_epub` original do
> upstream, enquanto `export_epub.py` tem o montador novo. São dois caminhos de
> EPUB; o canônico é o `export_epub.py`.

## 3. Montador de PDF A5 (`build_ebook.py`)

- Origem: `ebook-pdf-skill.zip`, arquivo local em `~/Downloads`, recebido em
  2026-09-22. O zip traz um `SKILL.md`, `scripts/build_ebook.py` e
  `references/manuscript.md`.
- **Licença: não declarada.** Não há arquivo de licença no zip nem autoria
  identificada — o `SKILL.md` interno não nomeia autor nem licença, e o caminho
  de fontes que ele espera (`/usr/share/fonts/SlidesCarnival/google`) sugere
  outra máquina e outro agente. Fica o registro de que a procedência é
  desconhecida: para uso próprio, sem problema; **antes de redistribuir a skill
  ou publicá-la, vale identificar a origem ou substituir este script.**

### O que mudou na importação

O script original **não rodava** neste ambiente; foram necessários três consertos
e uma adaptação de identidade:

| Ponto | O que estava | O que passou a ser |
|---|---|---|
| Fontes | buscava Cormorant Garamond e Libre Baskerville em `/usr/share/fonts/SlidesCarnival/google`, e o fallback era um `pass` que nunca registrava os nomes alternativos — morria em `KeyError: 'Libre'` na primeira linha da capa | resolve a fonte da marca (`brand.json`), converte a Inter variável de woff2 para TTF estático (400/600/700), **junta as duas subsets** e cacheia; cai para serifadas do sistema se faltar |
| Família de fonte | registrava `TTFont` solto; `Paragraph` com `<b>`/`<i>` estourava com `Can't map determine family/bold/italic for dejavubold` | `registerFontFamily` para os papéis de texto |
| Cobertura de caracteres | usava a subset `latin-ext`, que não tem `ç`, `ã`, `õ` — o texto saía como byte nulo no PDF (busca e cópia quebradas) | junta `latin` + `latin-ext` e **confere a cobertura** antes de usar, com aviso e fallback |
| Identidade | paleta fixa escura/ouro e motivo vetorial amarrado ao livro de origem ("seed-column") | cor e fonte do `brand.json` (tema configurável), capa no layout aprovado (kicker, filete, 4 LEDs) e cor de texto escurecida por cálculo de contraste |
| Sumário | sem número de página | folio impresso por capítulo, em duas passadas de montagem, com conferência de estabilidade da paginação |
| Metadados | `merge` gravava e a etapa seguinte descartava (PdfWriter novo não herda `/Info`) | metadados preservados: título, autor, assunto e gerador |
| Caminhos | `/home/workdir/artifacts/`, intermediários em `/tmp` fixo, `open_page` (ferramenta de outro agente) | `--saida`, diretório temporário real, `--brand-dir` e `--tema`, sem dependência de ferramenta externa |
| Listas | itens sem marcador nem recuo pendente | `bulletText` com marcador e recuo |

O que **veio do original e ficou**: a separação capa/miolo em dois PDFs mesclados,
a medição das caixas do sumário com `pdfplumber`, as anotações de link e os
marcadores escritos com `pypdf` depois do merge, o `NumberedCanvas` com
fio-de-pé e folio, e os tipos de bloco do manuscrito.

## 4. Novo nesta skill

- `montar_manuscrito.py` — ponte markdown → manuscrito JSON, com detecção de
  listas, tabelas, citações, caixa de destaque e capítulos de abertura sem número.
- `references/manuscrito.md` — schema do manuscrito, em português.
- Integração com `brand.json` (`temas.pessoal`): paleta, fonte e layout de capa.
- O `SKILL.md`, a decisão PDF × EPUB e o roteiro de conferência com PyMuPDF.

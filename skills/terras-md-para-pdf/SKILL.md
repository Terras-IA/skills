---
name: terras-md-para-pdf
description: "Converte Markdown em PDF A4 com o md-to-pdf e um de três perfis de CSS da skill: denso (CV, carta, cheat sheet), compacto (CV com mais respiro) e confortavel (documento, relatório, plano). Use para gerar, exportar ou imprimir PDF de um .md, CV ou carta."
keywords: [pdf, markdown para pdf, md para pdf, md-to-pdf, exportar pdf, imprimir, gerar pdf, cv em pdf, currículo pdf, carta em pdf, a4]
---

# Markdown para PDF

Converte um arquivo `.md` em PDF A4 com `npx md-to-pdf`, sempre com a config e o
CSS que vêm nesta pasta. Não monte uma configuração genérica do md-to-pdf.

## Onde está instalada

Fonte única: `skills/terras-md-para-pdf/` no repositório `terras-skills`. Cada
agente enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh`
do repositório. Nos comandos abaixo, `$SKILL_DIR` é a pasta onde este
`SKILL.md` está.

## Perfis

| Perfil | Arquivos em `perfis/` | Para quê |
|---|---|---|
| `denso` | `denso.cjs` + `denso.css` | Margem de 1 mm, tipografia compacta. Padrão de CV, carta de apresentação e cheat sheet. |
| `compacto` | `compacto.cjs` + `compacto.css` | Margem igual à do denso, com um pouco mais de espaço embaixo de títulos, parágrafos, listas e `hr`. Variante de CV, só quando pedida. |
| `confortavel` | `confortavel.cjs` + `confortavel.css` | Margens de 18/16 mm, texto 10,5 pt, espaçamento folgado. Documento para ler. |

`perfis/base.cjs` tem o que é comum aos três. As configs acham o CSS pela
própria pasta, então a skill funciona de qualquer lugar. A extensão é `.cjs`
porque o md-to-pdf carrega a config com `require()`.

## Escolher o perfil

1. **O pedido explícito vence.** "denso", "apertado", "modo CV", "tight" →
   `denso`. "compacto", "compact" → `compacto`. "confortável", "margem normal",
   "legível", "relaxed" → `confortavel`.
2. **Sem pedido, infira do arquivo:**
   - `denso` quando o nome ou o título tem CV, Currículo, Resume ou Cover
     letter/Carta; quando o conteúdo tem cara de CV (cabeçalho de contato,
     seções Experiência/Skills/Formação); ou quando é referência densa, como
     cheat sheet.
   - `confortavel` para o resto: documentação, notas, relatórios, planos,
     preparação de entrevista, README.
   - Nunca escolha `compacto` sozinho: só quando o usuário pede ou quando o
     pacote da vaga registra esse perfil.
3. Antes de rodar, diga em uma linha o perfil escolhido e o motivo.

Front matter YAML no próprio Markdown (por exemplo `pdf_options`) ou um bloco
`<style>` dentro dele sobrepõe o perfil.

## Comando

Use caminhos **absolutos** para o Markdown, para a pasta da skill e para a raiz
do projeto onde o Markdown está.

```bash
npx --yes md-to-pdf "<MD_ABSOLUTO>" \
  --config-file "$SKILL_DIR/perfis/<perfil>.cjs" \
  --basedir "<RAIZ_DO_PROJETO>" < /dev/null
```

Exemplo, CV no perfil denso:

```bash
npx --yes md-to-pdf "$HOME/curriculo/cv-en.md" \
  --config-file "$SKILL_DIR/perfis/denso.cjs" \
  --basedir "$HOME/curriculo" < /dev/null
```

O `< /dev/null` é obrigatório quando o comando roda sem terminal (agente,
script): com a entrada aberta, o md-to-pdf fica esperando Markdown pelo stdin
e nunca termina, mesmo com o arquivo passado no argumento. A primeira execução
instala o pacote e demora; as seguintes levam uns 2 segundos por arquivo.

## Navegador

O md-to-pdf usa o Puppeteer. A `base.cjs` aponta para um Chrome ou Chromium já
instalado (`/usr/bin/google-chrome`, `/usr/bin/chromium` e os caminhos padrão
de macOS e Windows) para o `npx` não baixar outro. Para forçar um navegador,
defina `PUPPETEER_EXECUTABLE_PATH`. Sem nenhum instalado, o Puppeteer baixa o
dele na primeira execução (centenas de MB): avise antes.

## Regras

- Não omita `--config-file` nem `--basedir`.
- `--basedir` é a raiz do projeto, para imagens e links relativos do Markdown
  resolverem.
- A saída é `<mesmo-caminho-e-nome>.pdf` ao lado do `.md`. Só mova se o
  usuário pedir outro lugar. Ao comparar perfis, copie com sufixo
  (`-denso.pdf`, `-compacto.pdf`, `-confortavel.pdf`) para uma variante não
  sobrescrever a outra.
- Quando um pacote de vaga fecha com um perfil, registre o perfil junto (no
  nome do arquivo ou num comentário) para a próxima geração sair igual.
- Depois que o comando terminar, informe o caminho completo do PDF e o perfil
  usado. Abra o PDF (ou converta a primeira página em imagem) e confira se nada
  ficou cortado antes de dizer que está pronto.
- CV ou carta para candidatura: rode a `terras-checagem-ats` no Markdown antes
  de gerar o PDF final.

## Origem

Perfis e fluxo adaptados de uma skill de Cursor compartilhada por um colega
(md-to-pdf com perfis tight, compact-1 e relaxed).

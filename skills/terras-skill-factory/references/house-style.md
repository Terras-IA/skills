# Estilo de casa das skills terras-

## Anatomia

Uma skill terras- é um diretório com `SKILL.md` na raiz e, quando precisa, `references/` e `scripts/`. A fonte única mora em `skills/<terras-nome>/` do repositório `terrasia-skills`; cada runtime enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do repositório:

```bash
bash scripts/instalar.sh --aplicar
```

## Frontmatter

```yaml
---
name: terras-<nome>          # kebab-case, prefixo terras-
description: "O que faz. Use quando <gatilhos>. Não é para X (terras-y). Termos EN."
                             # uma linha entre aspas, no máximo 300 caracteres
keywords: [termo1, termo2]   # descoberta
version: "x.y.z"             # quando vendoriza upstream ou mantém changelog
license: ...                 # quando deriva de upstream
metadata: ...                # env vars opcionais/obrigatórias, requisitos
disable-model-invocation: true  # só quando a skill repete o trabalho de outra: roda apenas por chamada
---
```

Únicos campos que toda skill usa: `name` e `description`. O resto é opcional e deve justificar a existência.

A `description` é o único texto que o agente lê para escolher entre as skills, e a lista inteira tem orçamento de contexto. Por isso: uma linha, no máximo 300 caracteres (o gate barra), o trabalho e os gatilhos primeiro, e a fronteira com a skill vizinha quando houver uma parecida.

## Corpo do SKILL.md

Ordem que a casa usa:

1. `# Título curto` — o que a skill faz, numa linha.
2. `## Objetivo` — para que existe, em 1-2 parágrafos.
3. `## Onde está instalada` — quando a skill depende de caminho ou motor local.
4. `## Regra dura` (ou equivalente em destaque) — a restrição que não pode ser violada.
5. `## Como trabalhar` / `## Quando usar` — o procedimento, numerado.
6. `## Referências` — lista dos arquivos em `references/` com uma frase do que cada um contém.
7. `## Fonte` — upstream, versão e licença, quando houver derivação.

## Concisão

O agente já é inteligente; a skill existe para as decisões em que ele erra sem mapa. Antes de escrever uma seção, pergunte: "sem isto, qual regra ele violaria?" Se a resposta for nenhuma, corte.

Descrição boa (específica, com gatilho):

> Extrai, guarda e diagnostica as estatísticas dos posts do LinkedIn do usuário: impressões, alcance na e fora da rede, reações e demografia. Use para analisar desempenho de post, comparar posts ou decidir o que repetir.

Descrição ruim (genérica):

> Ajuda com LinkedIn.

## Progressive disclosure

- `SKILL.md` = roteiro de decisão; mediana da casa é ~140 linhas.
- `references/` = catálogos, protocolos completos, cópia do upstream, licenças. O agente lê sob demanda.
- `scripts/` = motor executável (ex.: engine Python do `terras-last30days`). Instrução textual vira script quando o resultado tem que ser reprodutível byte a byte.

## Graus de liberdade

| Grau | Forma | Use quando |
|------|-------|------------|
| Alto | instrução textual | o caminho varia por contexto e o julgamento importa |
| Médio | pseudocódigo / script com parâmetros | há um fluxo, mas com variações legítimas |
| Baixo | script fixo em `scripts/` | o resultado é crítico e reprodutível |

## Teste de aderência

Rode o cenário de pressão num agente com a skill carregada e compare com o vermelho registrado. Passe = agente segue a regra dura e escolhe o caminho certo nos pontos de decisão. Falha = registre a racionalização nova, feche a brecha na skill, repita.

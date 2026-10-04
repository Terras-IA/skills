---
name: terras-slides
description: "Apresentações HTML estratégicas e persuasivas com Chart.js: estratégias por contexto, padrões de layout, fórmulas de copywriting e design tokens; inclui base de busca própria para estratégia/layout/copy. Use quando o pedido for criar slides, pitch deck ou apresentação em HTML (não PPTX). HTML slides, pitch deck, Chart.js, presentation."
keywords: [slides, apresentação, pitch deck, html, chart.js, copywriting, storytelling, deck]
license: MIT
---

# Slides

Strategic HTML presentation design with data visualization.

## When to Use

- Marketing presentations and pitch decks
- Data-driven slides with Chart.js
- Strategic slide design with layout patterns
- Copywriting-optimized presentation content

## Subcommands

| Subcommand | Description | Reference |
|------------|-------------|-----------|
| `create` | Create strategic presentation slides | `references/create.md` |

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (the agent reports the skill's base directory when the skill loads) and keep the working directory at the project root — the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## References (Knowledge Base)

| Topic | File |
|-------|------|
| Layout Patterns | `references/layout-patterns.md` |
| HTML Template | `references/html-template.md` |
| Copywriting Formulas | `references/copywriting-formulas.md` |
| Slide Strategies | `references/slide-strategies.md` |

## Routing

1. Parse subcommand from `$ARGUMENTS` (first word)
2. Load corresponding `references/{subcommand}.md`
3. Execute with remaining arguments


## Fonte

Conteúdo derivado da skill `slides` do repositório [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (MIT, © 2024 Next Level Builder; cópia do commit `477bcb2`, de 03/10/2026), renomeada como `terras-slides` no padrão da casa. Licença em `references/LICENSE-ui-ux-pro-max-skill.txt`.

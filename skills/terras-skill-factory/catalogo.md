---
name: terras-skill-factory
description: Cria, revisa e mantém skills no padrão terras-: inventário, frontmatter, catálogo de gatilhos, progressive disclosure e teste de aderência. Use para criar skill nova, transformar prompt recorrente em skill, revisar uma skill ou auditar se segue o padrão.
keywords: [skill, skills, criar skill, skill factory, padrão terras, SKILL.md, frontmatter, progressive disclosure, agent skills]
---

# Fábrica de skills terras-

## Objetivo

Criar e manter skills `terras-*` que um agente consiga acionar na hora certa e seguir sem desviar. Uma skill é um guia de referência de técnica comprovada — não é narrativa de como um problema foi resolvido uma vez.

Metodologia: **TDD aplicado a documentação** (adaptada de `obra/superpowers`, skill `writing-skills`, MIT). Se você não viu um agente falhar sem a skill, não sabe se ela ensina a coisa certa.

## Regra dura: vermelho antes de verde

1. **Vermelho.** Antes de escrever, rode o cenário de pressão num agente **sem** a skill (sessão limpa, sem ela instalada). Registre as racionalizações exatas que ele usa para violar o resultado esperado.
2. **Verde.** Escreva a skill mirando nessas violações específicas — cada regra existe para fechar uma falha observada, não por princípio.
3. **Reverificação.** Rode o mesmo cenário com a skill instalada. Se o agente ainda desvia, a regra está fraca: feche a brecha e teste de novo.

Skill que nasce sem vermelho é hipótese, não skill.

## Quando criar (e quando não)

**Criar:** técnica que não era óbvia, que se repete entre projetos, que outros aproveitariam, e que exige julgamento (o que dá para validar com regex/CI deve virar automatização, não skill).

**Não criar:** solução de uma vez só, prática padrão bem documentada fora daqui, convenção de um projeto só (isso vai para o CLAUDE.md do projeto).

## Estrutura da casa

```
skills/<terras-nome>/
  SKILL.md            # corpo enxuto, mediana da casa ~140 linhas
  references/         # detalhe que o agente só lê quando precisa
  scripts/            # código executável, quando a skill tem motor
```

Fonte única: `skills/<terras-nome>/` no repositório `terrasia-skills`; cada agente enxerga por link simbólico criado pelo `scripts/instalar.sh` do repositório, e o marketplace entrega a mesma skill por plugin.

## Checklist de fechamento

- [ ] Frontmatter: `name` e `description` obrigatórios; `description` em PT-BR com gatilhos específicos ("use quando...") + termos EN para acionamento bilíngue; `keywords` para descoberta.
- [ ] Nome: gerúndio ou substantivo objetivo, kebab-case, prefixo `terras-`.
- [ ] Corpo: objetivo primeiro, regra dura em destaque, sem seção que não mude a decisão do agente.
- [ ] Detalhe pesado (catálogos, protocolos longos, licenças de upstream) em `references/`, citado pelo nome do arquivo.
- [ ] Grau de liberdade consciente: instrução textual (liberdade alta) → pseudocódigo (média) → script em `scripts/` (baixa). Quanto mais crítico o resultado, mais concreto o mecanismo.
- [ ] Upstream vendorizado? Anote origem, versão e licença em `references/`.
- [ ] Teste de aderência verde nos cenários do vermelho original.
- [ ] Instalação conferida: link simbólico do `scripts/instalar.sh` ou plugin instalado pelo marketplace.

## Referências

- `references/house-style.md` — estilo das skills terras- com template comentado e o padrão de instalação por link simbólico.
- `references/best-practices.md` — diretrizes de autoria (Anthropic + superpowers), com exemplos bom/ruim de concisão e descrição.

## Fonte

Metodologia derivada de `obra/superpowers` (skill `writing-skills` e `anthropic-best-practices.md`, MIT) e das diretrizes oficiais de skill authoring da Anthropic, adaptadas ao padrão da casa.

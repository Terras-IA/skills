---
name: terras-standards
description: Aplica os Padrões Agnósticos de Engenharia e Produto v4.0 (arquitetura, segurança, privacidade e IA) com lastro em evidência real de cliente quando disponível. Use sempre que o usuário mencionar "padrões de engenharia", "v4.0", "Bloco G", "gate de produção", "AIP/RIPD/ROPA", "ISO 27001", "conformidade", "evidência de auditoria", ou pedir para avaliar conformidade, classificar perfil, criar um ADR, responder o questionário de adoção, ou buscar evidência real de um cliente.
---

# Skill terras-standards

Orienta o agente a aplicar a norma **Padrões Agnósticos de Engenharia e
Produto — v4.0**, e a citar evidência real de cliente quando ela existir, em
vez de responder só com o texto teórico da norma.

## 1. Duas fontes, nunca misturadas sem identificação

- `standard://...` — norma agnóstica (v3/v4), sempre presente, vendorizada
  em `mcp/terras-standards/norma/` no repo `terrasia`.
- `cliente://<slug>/<arquivo>` — política REAL de um cliente específico
  (ex. `dimastec`), presente **somente se** existir
  `mcp/terras-standards/clientes/<slug>/` — pasta gitignored, nunca no
  histórico do git.

A tool `terras_standards_read_doc` sempre marca a origem da resposta
(`origem: "agnostic"` vs. `"client-real"`). Nunca apresente conteúdo de
`client-real` como se fosse a norma genérica, nem o contrário.

## 2. Cliente sem nenhum dado real é normal, não erro

Um cliente pode não ter pasta em `clientes/` — sem ISO, sem política
formalizada, sem evidência coletada. Nesse caso as tools
(`terras_standards_evidence_catalog`, `terras_standards_read_doc` com
`cliente-list`) retornam listas vazias com texto explicativo, nunca erro.
Trate isso como "avaliação permanece no padrão agnóstico", nunca como
"cliente com problema de conformidade" — ausência de evidência coletada não
é ausência de conformidade.

Um catálogo de evidência CORROMPIDO (`evidencias.json` malformado) é
diferente: `terras_standards_evidence_catalog` sinaliza
`catalogoIlegivel: true` nesse caso, e o texto avisa que não é seguro tratar
como "sem evidência" — o arquivo precisa de conserto manual antes de
responder por aquele cliente.

## 3. Buscar evidência real antes de afirmar conformidade

Antes de responder "isso está em conformidade com X" para um cliente com
dados reais, chame `terras_standards_evidence_catalog(cliente="<slug>",
busca="<termo do controle>")`. Se houver evidência real, cite o arquivo e a
cláusula ISO/LGPD relacionada em vez de só citar o texto da norma. Se não
houver, diga explicitamente que a afirmação se apoia só no padrão teórico e
que falta evidência real.

## 4. Fluxo de adoção (inalterado da v4.0 §7)

1. `terras_standards_gate_blockg` — 5 gates de bloqueio.
2. `terras_standards_classify_profile` — perfil Core/AI-1..AI-4.
3. `terras_standards_questionnaire` — blocos aplicáveis, evidência
   obrigatória (Princípio 10) — cite evidência real via
   `evidence_catalog` quando o cliente tiver.
4. `terras_standards_draft_adr`, `terras_standards_map_artifacts`,
   `terras_standards_conformance` — artefatos finais.

`terras_standards_validate_evidence` está registrada por compatibilidade de
contrato, mas sempre retorna erro nesta versão — o `terrasia` usa
`docs/adrs/` próprio, sem o script `validate_adr_evidence.py` do `projeto0`
de onde esta skill foi portada.

## 5. Converter política real nova

Quando houver política nova de um cliente (ex. atualização no
`dimastec-10-1`):

```bash
cd mcp/terras-standards
node scripts/converte-politicas.mjs --entrada <dir-com-docx-pdf> --cliente <slug>
```

Depois, atualize manualmente `clientes/<slug>/evidencias.json` se a mudança
também trouxer evidência nova (o catálogo de evidência não é gerado
automaticamente — screenshots não passam por OCR, cada entrada é escrita à
mão com o que o arquivo prova e a cláusula relacionada).

## 6. Registro do servidor MCP

O servidor é `mcp/terras-standards/` dentro do repo `terrasia` — buildar
(`npm run build`) e registrar em escopo `user` (disponível em qualquer
projeto aberto nesta máquina, inclusive `terrasia-client` e
`terrasia-admin`, que não têm o pacote):

```bash
claude mcp add terras-standards -s user -- node /srv/harness/terrasia/mcp/terras-standards/dist/index.js
```

Se este pacote foi desenvolvido num worktree, o registro precisa ser refeito
apontando pro caminho canônico do repo depois do merge — um registro
apontando pro worktree para de funcionar quando o worktree é removido.

## 7. Origem

Portada de `standards-v4`/`v4-standards` (repo `projeto0`), que continua
existindo separadamente para quem ainda o referencia. Esta versão vive
inteiramente em `terrasia`, sem dependência de caminho de outra máquina. O
arquivo canônico é `.claude/skills/terras-standards/SKILL.md` no repo
`terrasia` — a cópia em `~/.claude/skills/` é o que o runtime local
carrega; mantenha as duas sincronizadas.

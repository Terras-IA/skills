# Template de governance rule

Uma regra por arquivo (ou por diretório-skill, quando o agente do projeto lê skills):

```markdown
---
name: <dominio>-<topico>          # ex.: git-flow-compliance, erro-handling-api
description: >-
  Responde: <pergunta>. Use quando <gatilho específico>. EN: <termos>.
version: 1.0.0
status: active                    # active | deprecated
owner: <papel ou pessoa>          # quem decide mudança
review: 2027-04-01                # AAAA-MM-DD da próxima revisão
substituida-por: <nome>           # apenas quando status: deprecated
prazo: 2026-12-31                 # apenas quando deprecated: data de remoção
---

# <Pergunta que a regra responde>

## Regra
<Imperativa, mínima, verificável. Uma regra por arquivo.>

## Por quê
<Evidência do repo: % de aderência no git log, o que o CI executa, incidente que originou.>

## Como verificar
<Comando, job de CI ou checklist de review que detecta violação. Obrigatório.>

## Quando NÃO usar
<Exceções reais em que a regra não se aplica. Obrigatório — sem isto ela dispara fora de contexto.>

## Exemplos
<Bom e ruim, curtos, do próprio repo quando possível.>

## Changelog
- 1.0.0 (2026-10-02): primeira publicação.
```

## Semver de regra

- **MAJOR** — aperta ou muda o comportamento esperado. Nota de migração obrigatória no changelog ("quem seguia 1.x deve ...").
- **MINOR** — adiciona exceção, esclarece, amplia gatilho de uso.
- **PATCH** — redação, erro de exemplo, link quebrado.

## Deprecação

1. `status: deprecated` + `substituida-por` + `prazo`, no mesmo commit que apresenta a substituta.
2. Durante o prazo: regra antiga permanece no índice com aviso de deprecação.
3. Depois do prazo: remover arquivo e linha do índice; o changelog da substituta registra a absorção.

## Índice no AGENTS.md/CLAUDE.md

Uma linha por regra, ponteiro — nunca duplicar o conteúdo:

```markdown
## Padrões do repo
- [git-flow-compliance](docs/padroes/git-flow-compliance.md) v1.2.0 — como nomear branch e mensagem de commit
```

## Exemplo preenchido (resumido)

```markdown
---
name: git-flow-compliance
description: Responde: como nomear branch e mensagem de commit. Use quando criar
  branch ou commit neste repo. EN: git flow, conventional commits.
version: 2.0.0
status: active
owner: Everton (tech lead)
review: 2027-01-15
---

# Como nomear branch e mensagem de commit?

## Regra
Branch: `tipo/escopo-curto` (`fix/login-timeout`). Commit: `tipo(escopo): descrição`
em minúsculas, sem ponto final; tipos válidos: feat, fix, refactor, docs, chore, test.

## Por quê
94% dos últimos 200 commits seguem o padrão e o workflow `ci.yml` roda commitlint
que falha fora dele. Branch com prefixo alimenta o changelog automático.

## Como verificar
`npx commitlint --from HEAD~1`; CI falha em branch sem prefixo `tipo/`.

## Quando NÃO usar
Release tag (`v2.3.1`) e commits de merge: mantêm o formato do GitHub, sem prefixo.

## Exemplos
Bom: `fix(auth): expira token em 30min` | Ruim: `ajustes`

## Changelog
- 2.0.0 (2026-10-02): passa a exigir prefixo de branch. Quem seguia 1.x deve
  renomear branches abertas com `git branch -m`.
- 1.0.0 (2026-03-04): primeira publicação.
```

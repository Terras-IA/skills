# terrasia-skills

Fonte única das skills `terras-*`. Cada skill mora aqui uma vez, e daqui sai
para dois consumidores:

- **Agentes** (Claude Code, Codex, opencode, ZCode ou qualquer outro que leia
  pastas com `SKILL.md`): enxergam a skill por link simbólico criado pelo
  `scripts/instalar.sh`.
- **Catálogo do motor terrasia**: as skills listadas em `catalogo.json` são
  importadas pelo `scripts/aplica-bundles.mjs` do repositório `terrasia`, que
  lê este diretório.

Repositório irmão de `terrasia`, `terrasia-admin` e `terrasia-client`, sem
tooling compartilhado com eles.

## Layout

```
skills/terras-<nome>/
  SKILL.md        # a skill (o que o agente carrega)
  catalogo.md     # opcional: versão para o catálogo do motor, quando difere
  scripts/ references/ assets/ templates/ seed/   # o que a skill usar
  .vendor         # opcional: caminhos de código de terceiro (ver abaixo)
  .nao-instalar   # opcional: só catálogo; o instalador não cria link (ver abaixo)
catalogo.json     # skills que entram no catálogo do motor (e nome antigo, se mudou)
evals/            # cenários de avaliação de algumas skills
scripts/          # verificador, instalador e seus testes
```

**Por que `catalogo.md` existe.** O motor injeta o texto da skill como system
prompt de um turno e não executa script nenhum. Quando a skill de agente manda
rodar scripts ou fala de um repositório específico, a versão do catálogo é
outra: só o método. Sem `catalogo.md`, o catálogo usa o próprio `SKILL.md`.

**Skills de processo do terrasia.** `terras-qualidade`, `terras-validacao`,
`terras-api-sync`, `terras-drift`, `terras-boundary`, `terras-reconstrucao`,
`terras-adr` e `terras-backreview` têm aqui só a versão de catálogo (o método
genérico que o motor injeta). A versão de agente é regra de trabalho do
repositório `terrasia` e mora em `terrasia/.claude/skills/`, versionada junto do
código que ela rege: quem clona o motor recebe o processo de qualidade junto.
O `.nao-instalar` impede que o instalador ponha um segundo `terras-qualidade`
ao lado do que o projeto já carrega.

## Regras (o `npm run verificar` barra cada uma)

1. **Prefixo.** Toda pasta é `terras-<nome-em-kebab-case>`, e o `name` do
   cabeçalho é igual à pasta.
2. **Cabeçalho aceito pelo motor.** LF no arquivo inteiro (nunca CRLF), campos planos
   `chave: valor`, cabeçalho de no máximo 1024 caracteres.
3. **Catálogo que dispara.** Skill listada em `catalogo.json` tem `description`
   de até 280 caracteres, sem bloco YAML, e `keywords` não vazias: sem
   keywords a skill fica liberada e muda.
4. **Sem dependência de harness.** Nada de caminho de instalação de um agente
   (`~/.claude`, `~/.zcode`, `~/.config/opencode`, `~/.agents`, `~/.codex`), de
   ferramenta própria de um agente (`AskUserQuestion`, `TodoWrite`, `WebFetch`,
   `WebSearch`, subagente) ou de variável `CLAUDE_*`. Citar Claude como IA-alvo
   ou o arquivo `CLAUDE.md` de um repositório é conteúdo e passa.
   - Caminho para a própria skill: `$SKILL_DIR` no texto (a pasta do
     `SKILL.md`); nos scripts, a partir do próprio arquivo com `realpath`.
   - Caminho para outra skill: a pasta vizinha (`$SKILL_DIR/../terras-x`), com
     `TERRAS_SKILLS_DIR` para apontar outra raiz.
   - Código de terceiro que já suporta vários agentes fica listado em
     `.vendor` e fora desta regra (hoje: o motor da `terras-last30days`).
5. **Sem marca de origem** de catálogo importado de outra empresa.
6. **Sem segredo e sem credencial.** `config.json`, `.env`, tokens e caches
   não entram; `*.example.json` entra.

## Comandos

```bash
npm run gate                       # verificar + testes (rodar antes de commit)
npm run verificar                  # só as regras acima
npm test                           # testes do verificador e do instalador
bash scripts/instalar.sh           # simulação da instalação
bash scripts/instalar.sh --aplicar # instala (backup em ~/.terras-skills-backup/)
```

Em máquina nova: clonar o repositório e rodar `bash scripts/instalar.sh
--aplicar`. O instalador só cria link nas pastas de agente que já existem.
Ele usa `readlink -f`: Linux, ou macOS 12.3 em diante.

## Mudar uma skill do catálogo

Editar aqui não muda o motor. O `aplica-bundles.mjs` do `terrasia` importa o
que falta no catálogo e concede as liberações do `skills/bundles.json` de lá,
que continua no core porque decidir que alma recebe o quê é governança.
Importar e liberar seguem sendo dois passos.

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `TERRAS_SKILLS_DIR` | raiz das skills quando não for a pasta vizinha (scripts que chamam outra skill) |
| `TERRAS_IMAGE_KEY` / `TERRAS_IMAGE_ENDPOINT` | chave e endpoint do Model Studio para `terras-banner/scripts/gen_art.py` |

`MIGRACAO.md` registra de onde cada skill veio quando o repositório nasceu.

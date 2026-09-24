# Instalação — terras-substack

Skill para publicar e gerenciar posts na Substack a partir de markdown, usando a
API interna do editor (não existe API pública de escrita). É uma pasta com
`SKILL.md` e scripts em Python: serve a qualquer agente que leia skills nesse
formato, e o CLI funciona sozinho, sem agente nenhum.

Versão do pacote: **1.0.0** (2026-09-15).

## Requisitos

- **Python 3** (testado no 3.14) com o módulo `requests` — já vem no Python do
  sistema Debian/Ubuntu (`python3-requests`). Nenhuma instalação de pacote da
  Substack, nenhuma API paga, nada além disso.
- **Cookie de sessão `substack.sid`** da conta, salvo em
  `~/.config/terras-substack/config.json` (permissão 600). O passo a passo para
  obter e renovar está em `references/credenciais.md`.

Verificação rápida depois de instalar:

```bash
python3 <diretório-da-skill>/scripts/terras_substack.py check
```

Sem cookie, ele responde com o que falta — não quebra.

## Instalação

A fonte é `skills/terras-substack/` no repositório `terrasia-skills`. O
`scripts/instalar.sh` do repositório cria o link simbólico da skill em cada
pasta de skills de agente que existir na máquina; sem ele, basta apontar o
agente para esta pasta. Nunca copie a pasta: cópia diverge em silêncio.

## Uso

O agente invoca a skill sozinho quando o pedido envolver Substack. O CLI também
funciona direto:

```bash
S=$SKILL_DIR/scripts/terras_substack.py

python3 $S check                       # valida config e sessão
python3 $S whoami                      # id do usuário e publicações
python3 $S create-draft post.md        # cria rascunho (privado)
python3 $S get-draft 123 --markdown    # confere o que está no rascunho
python3 $S publish 123 --yes           # publica SÓ na web (sem e-mail)
python3 $S publish 123 --yes --send-email   # publica e dispara e-mail
python3 $S schedule 123 --at 2026-09-20T09:00:00-03:00 --yes
python3 $S drafts                      # rascunhos existentes
```

`--dry-run` antes de qualquer comando mostra a requisição sem executar.
O markdown aceito (frontmatter + diretivas `::: paywall`, `::: subscribe`,
`::: button`) está em `references/prosemirror.md`.

## Variáveis de ambiente

| Variável | Para que serve |
|---|---|
| `SUBSTACK_SID` | cookie de sessão, sem precisar do arquivo de config |
| `SUBSTACK_PUBLICATION` | URL da publicação (ex.: `https://nome.substack.com`) |
| `SUBSTACK_USER_ID` | id do usuário (bylines) |
| `SUBSTACK_COOKIES` | string `"a=1; b=2"` com cookies extras |
| `SUBSTACK_CONFIG` | caminho alternativo do arquivo de config |
| `TERRAS_SUBSTACK_CLI` / `TERRAS_SUBSTACK_PYTHON` | usados pelo daemon do terrasIA para localizar este CLI |

## Snippet para AGENTS.md / CLAUDE.md

Agentes que leem um arquivo de instruções do projeto (AGENTS.md, CLAUDE.md e
afins) podem ganhar uma linha explícita:

```markdown
- **Substack**: para publicar/gerenciar posts use a skill `terras-substack`
  (`scripts/terras_substack.py`). Publique só com pedido explícito do usuário:
  `publish` exige `--yes` e o e-mail só sai com `--send-email`.
```

## Segurança

- O cookie dá acesso total à conta. O arquivo de config fica com permissão `600`
  e **nunca** deve ser versionado.
- `publish` publica somente na web por padrão; e-mail exige `--send-email`.
- Remover um post é **definitivo**: a API interna não tem despublicação
  reversível (o CLI expõe a operação como `unpublish`/`delete-draft`, mesma
  chamada).
- Como a Substack não tem API pública de escrita, os endpoints são internos e
  podem mudar sem aviso. Sintoma típico: `HTTP 403` na sessão (cookie expirado —
  veja `references/credenciais.md`) ou `404` com HTML (endpoint renomeado).

## Reconstruir este pacote

O `.skill`/`.zip` é gerado a partir deste diretório. Depois de editar a skill,
reconstrua para o pacote não ficar defasado:

```bash
cd <repositório terrasia-skills>/skills
zip -r -q ~/Documents/Diversos/terras-substack-1.0.0.zip terras-substack \
  -x "terras-substack/scripts/__pycache__/*" -x "*.pyc"
cp ~/Documents/Diversos/terras-substack-1.0.0.zip ~/Documents/Diversos/terras-substack-1.0.0.skill
sha256sum ~/Documents/Diversos/terras-substack-1.0.0.{zip,skill}   # devem ser iguais
```


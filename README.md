# Terras skills

Marketplace de plugins do Claude Code. Cada skill é um plugin: instale só as que quiser.

```bash
/plugin marketplace add Terras-IA/skills
```

Para atualizar: `/plugin marketplace update terras`.

## As skills do catálogo

Além dos dois plugins abaixo, cada skill `terras-*` ou `terrasia-*` de uso geral do catálogo é um plugin com o
mesmo nome da skill (escrita, LinkedIn, RH, financeiro, fiscal, vendas, desenvolvimento). Para
ver a lista, `/plugin` e escolha o marketplace `terras`. Para instalar uma:

```bash
/plugin install terras-linkedin@terras
```

`terras-audio`, `terras-banner` e `terras-video` usam scripts umas das outras e saem juntas no
plugin `terras-midia`.

Ficam fora do marketplace as skills de processo do motor terrasia e as ligadas a projeto de
cliente (`marketplace-fora.json` diz quais e por quê).

## terras-coders-mural

Faz a rodada de engajamento do **Mural de Posts**:

1. lista os posts novos (ou mais antigos, como quando você rola a tela);
2. lê cada post linkado no LinkedIn;
3. escreve um comentário curto e específico, em inglês para o LinkedIn e em português para o mural;
4. **mostra tudo numa tabela e espera o seu "aprovado"**;
5. curte e comenta no mural, e comenta no LinkedIn, conferindo cada publicação.

Nada é publicado sem a sua aprovação no chat.

### Requisitos

- Claude Code com um navegador que o agente controla: o navegador integrado do app desktop ou a
  extensão Claude in Chrome.
- Estar logado na COD3RS e no LinkedIn nesse navegador.

### Instalação

```bash
/plugin install terras-coders-mural@terras
```

Depois, é só pedir: "curte e comenta os posts de hoje do mural da COD3RS".

## terras-linkedin-alvos

Para networking com poucas pessoas-chave (executivos, gestores e recrutadores das empresas onde
você quer trabalhar):

1. você passa a lista de perfis uma vez;
2. o plugin acha os posts recentes de cada um (pela data exata do post);
3. prepara comentários de 250 a 450 caracteres que acrescentam algo (experiência, dado ou pergunta);
4. **mostra tudo e espera o seu "aprovado"**;
5. curte, comenta e registra o que foi feito para nunca comentar duas vezes no mesmo post;
6. depois de 2-3 comentários num mesmo alvo, sugere o convite de conexão com nota.

Roda na hora ("vê se meus alvos postaram") ou agendado. Na rodada agendada, as curtidas podem ser
automáticas se você ativar; os comentários sempre esperam a sua aprovação.

```bash
/plugin install terras-linkedin-alvos@terras
```

### Aviso

O LinkedIn proíbe automação nos termos de uso. O plugin trabalha devagar, em volume baixo e com
aprovação humana, o que reduz o risco, mas não o elimina. Use por sua conta.

A API do mural é interna à COD3RS e pode mudar sem aviso.

## Para quem mantém este repositório

Fonte única das skills da casa (`terras-*` e `terrasia-*`). Cada skill mora aqui uma vez, e daqui sai
para três consumidores:

- **Marketplace de plugins do Claude Code** (acima): o
  `.claude-plugin/marketplace.json` é GERADO do catálogo por
  `npm run marketplace`. Cada plugin aponta para a própria pasta da skill; nada
  é copiado.
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
skills/terras-<nome>/        # ou terrasia-<nome>/ para a família nova
  SKILL.md        # a skill (o que o agente carrega)
  catalogo.md     # opcional: versão para o catálogo do motor, quando difere
  scripts/ references/ assets/ templates/ seed/   # o que a skill usar
  .vendor         # opcional: caminhos de código de terceiro (ver abaixo)
  .nao-instalar   # opcional: só catálogo; o instalador não cria link (ver abaixo)
catalogo.json     # skills que entram no catálogo do motor (e nome antigo, se mudou)
.claude-plugin/marketplace.json   # GERADO (npm run marketplace); não edite os plugins de ./skills/ à mão
marketplace-fora.json             # skills que não vão para o marketplace, com o motivo
marketplace-grupos.json           # skills que dependem da pasta vizinha e saem juntas num plugin só
plugins/          # plugins escritos à mão, e a cópia GERADA dos plugins de grupo (plugins/terras-midia)
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

1. **Prefixo.** Toda pasta é `terras-<nome-em-kebab-case>` ou
   `terrasia-<nome-em-kebab-case>`, e o `name` do
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
7. **Sem dado pessoal.** O repositório é público: CNPJ, CPF e e-mail real
   reprovam, inclusive em arquivo de exemplo (`*.example.*`, `.csv`). Exemplo
   usa dado fictício (`@example.com`); licença de fonte e código em `.vendor`
   ficam fora da regra de e-mail. Skill que só faz sentido com dado de cliente
   ou conta pessoal mora no repositório privado `skills-internas`.

## Comandos

```bash
npm run gate                       # verificar + testes (rodar antes de commit)
npm run marketplace                # regrava o manifesto do marketplace a partir do catálogo
npm run verificar                  # só as regras acima
npm test                           # testes do verificador e do instalador
bash scripts/instalar.sh           # simulação da instalação
bash scripts/instalar.sh --aplicar # instala (backup em ~/.terras-skills-backup/)
```

Em máquina nova: clonar o repositório e rodar `bash scripts/instalar.sh
--aplicar`. O instalador só cria link nas pastas de agente que já existem.
Ele usa `readlink -f`: Linux, ou macOS 12.3 em diante.

## Publicar no marketplace

Skill nova ou alterada em `skills/` só aparece no marketplace depois de
`npm run marketplace` e do push no `main` (quem já instalou atualiza com
`/plugin marketplace update terras`). O gate reprova manifesto desatualizado. O
marketplace e os links do `instalar.sh` entregam a MESMA skill por dois
caminhos: num mesmo agente, use um ou outro, senão ela aparece duas vezes.

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

## Licença

MIT. Veja [LICENSE](LICENSE).

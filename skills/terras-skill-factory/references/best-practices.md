# Diretrizes de autoria (Anthropic + superpowers, condensadas)

## Princípios centrais

1. **Concisão manda.** Cada token do SKILL.md compete com o contexto do projeto. Descrição boa tem ~50 tokens; verbosa demais, ~150.
2. **Teste com os modelos que vão usar.** Skill que passa num modelo forte pode falhar num menor; regras com HARD-GATE compensam modelo fraco.
3. **A descrição é o gatilho.** Diga o que a skill faz **e** quando usá-la, com os termos que aparecem no pedido do usuário (inclua inglês e português).

## Exemplo: concisão

Bom (~50 tokens):

> ## Extrair texto de PDF
> 1. Rode `pdftotext file.pdf -` para texto simples.
> 2. Se falhar (PDF digitalizado), rode OCR: `ocrmypdf --force-ocr file.pdf out.pdf`.

Ruim (~150 tokens):

> ## Extrair texto de PDF
> Primeiro, você precisa entender que PDFs podem conter texto em camadas...
> (introdução, histórico, explicações do óbvio, parágrafos de contexto)

## Exemplo: descrição com gatilho

> Processa documentos PDF: extrai texto, divide em páginas, converte em imagens para OCR de digitalizados. Use quando o usuário pedir para ler, extrair ou analisar conteúdo de arquivo PDF.

Termos-chave no início da frase; verbos que aparecem no pedido real do usuário.

## Nomeação

- Bom: gerúndio descrevendo a atividade — `writing-plans`, `requesting-code-review`, `systematic-debugging`.
- Aceitável: substantivo do domínio — `brandkit`, `obsidian-cli`.
- Evitar: nomes vagos (`helper`, `utils`, `general-assistant`) ou que não sugerem quando disparar.

## Padrões de progressive disclosure

- Um nível: SKILL.md único, tudo essencial.
- Dois níveis: SKILL.md + `references/` para tabelas, catálogos, exemplos longos.
- Três níveis: + `scripts/` para execução determinística.

Regra prática: se uma seção só importa em 20% das invocações, ela vai para `references/`.

## Falsos positivos a evitar

- Skill para o que CI/lint/regex já enforce (isso é automatização, não julgamento).
- Skill que repete documentação padrão acessível (o agente já sabe procurar).
- Skill narrativa ("como fizemos no projeto X") em vez de técnica reutilizável.

## Verificação antes de fechar

1. A regra dura sobrevive a um agente tentando "ajudar" criativamente?
2. A descrição faria você mesmo escolher esta skill no momento certo?
3. Existe vermelho registrado (falha sem a skill) que justifique cada seção?
4. Nos pontos de decisão, o grau de liberdade está explícito?
5. Upstreams citados com versão e licença?

## Fontes

- `obra/superpowers` — `skills/writing-skills/SKILL.md` e `anthropic-best-practices.md` (MIT): TDD aplicado a documentação, cenários de pressão com agentes sem a skill.
- Diretrizes oficiais de skills da Anthropic (code.claude.com/docs/en/skills).

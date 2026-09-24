---
name: terras-tech-debt
description: "Auditoria de dívida técnica e arquitetura de um repositório, com achados citando arquivo:linha, severidade, esforço e a seção obrigatória 'parece ruim mas está certo'. Use quando o pedido for auditoria de dívida técnica, diagnóstico de codebase, revisão de arquitetura, health check de repositório ou avaliação de qualidade de código de um repo inteiro. Tech debt audit, codebase health check, architecture review, legacy assessment."
keywords: [auditoria, dívida técnica, tech debt, arquitetura, codebase, revisão de código, refatoração, legado, severidade, relatório técnico]
---

# Auditoria de dívida técnica

## Objetivo

Ler um repositório inteiro e produzir um relatório de dívida técnica com achados que apontam `arquivo:linha`, severidade, esforço e recomendação. O relatório tem que ser acionável: cada item precisa dar para alguém abrir o arquivo, ver o problema e decidir.

Não é revisão de estilo nem lista de boas práticas genéricas. É o que está errado neste repositório, com evidência.

## Onde está instalada

Canônica em `~/.zcode/skills/terras-tech-debt/SKILL.md`, com link simbólico em `~/.claude/skills/` e `~/.config/opencode/skills/` (mesmo padrão das outras terras-). Uma edição na canônica vale para os três.

## Regras duras

1. **Somente leitura.** A auditoria não altera o repositório auditado. O único arquivo escrito é o relatório (`TECH_DEBT_AUDIT.md`) na raiz do repo, ou onde o usuário pedir. Nada de instalar dependências, commitar, formatar código ou "aproveitar e corrigir".
2. **Toda citação é verificada.** Antes de escrever um achado, abra o arquivo e confira a linha citada. Achado com linha errada destrói a confiança no relatório inteiro. Se o número da linha muda entre leituras, cite o símbolo ou a função junto (`src/pagamentos/processor.ts:1240`, `função reconcile`).
3. **Sem invenção.** Não afirme o que não leu. Se não deu para determinar se algo é dívida ou decisão consciente, vai para "perguntas abertas", não para a lista de achados.
4. **Sem reescrita.** Recomende mudanças específicas e pequenas. "Reescreva o módulo" não é recomendação, é desistência.
5. **Sem enchimento e sem bajulação.** Categoria sem achado material recebe "Nada material". Nada de "no geral o código está bem estruturado". Não existe elogio de cortesia no relatório.
6. **Não instale ferramentas sem permissão.** Ferramenta ausente vira uma linha em limitações. Nunca `npm install -g` ou equivalente por conta própria.
7. **Sem segredos no relatório.** Se encontrar chave ou senha hardcoded, cite o arquivo e a linha e diga o tipo de credencial. Nunca copie o valor para o relatório.

## Rubrica de severidade e esforço

Severidade sem definição vira opinião. Use esta régua, e diga no relatório que usou ela:

| Severidade | Critério | Prazo sugerido |
|---|---|---|
| Crítico | Risco de incidente em produção, perda de dado, falha de segurança explorável, ou bloqueio de entrega | Esta semana |
| Alto | Degrada confiabilidade ou velocidade do time de forma mensurável | Ciclo atual |
| Médio | Custo recorrente de manutenção, sem risco imediato | Agendar |
| Baixo | Higiene, consistência, oportunidade | Quando sobrar espaço |

Esforço:

- **S**: até 1 dia, escopo local, sem migração de dados nem mudança de contrato.
- **M**: 2 a 5 dias, toca 2+ módulos, ou exige migração simples.
- **L**: 1 semana ou mais, muda contrato, migra dado ou exige coordenação entre times.

## Fase 1: Orientar

Não pule. Opinião formada antes de entender o sistema produz auditoria ruim.

1. Leia o README, o manifesto (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) e os documentos de arquitetura em `/docs` ou `/adr`.
2. Mapeie a estrutura de diretórios e identifique os módulos e camadas principais.
3. Rode `git log --oneline -200` e `git log --stat --since="6 months ago"`. O que muda com frequência é onde a dívida mora.
4. Identifique pontos de entrada, caminhos quentes e cantos frios.
5. Liste os 20 maiores arquivos por linhas e os 20 mais modificados nos últimos 6 meses. A interseção costuma ser o alvo.
6. Publique um plano com `TodoWrite` para o usuário acompanhar as fases.

Escreva um modelo mental da arquitetura em 1 ou 2 parágrafos antes de seguir. Se o seu modelo contradiz o README, isso já é um achado.

## Fase 2: Auditar as dimensões

Use `rg`, `ast-grep` e ferramentas nativas da linguagem para achar exemplos concretos. Cite `caminho/arquivo.ext:LINHA` em todo achado.

1. **Decaimento arquitetural**: dependências circulares, violação de camadas, arquivos e funções gigantes (mais de 500 linhas é o gatilho padrão, ajuste se o repo tiver base maior), lógica duplicada em 3+ lugares onde caberia abstração, abstrações que ninguém usa, código morto (export sem uso, branch inalcançável, bloco comentado velho).
2. **Apodrecimento de consistência**: vários jeitos de fazer a mesma coisa (cliente HTTP, tratamento de erro, log, carregamento de config, validação, data). Nomes que derivaram. Estrutura de pastas que não reflete mais o que o código faz.
3. **Dívida de tipo e contrato**: `any`, `unknown`, `as any`, `# type: ignore`, dicionário solto. Fronteira de API sem tipo. Falta de validação de schema nas fronteiras de confiança.
4. **Dívida de teste**: rode cobertura se existir; aponte buracos em caminho crítico. Teste que verifica implementação em vez de comportamento. Teste pulado ou instável. Arquivo de alta rotatividade sem teste.
5. **Dívida de dependência e configuração**: `npm audit`, `pip-audit` ou `cargo audit` para CVE. Dependência sem uso. Duas dependências fazendo o mesmo trabalho. Variável de ambiente referenciada e não documentada, ou com padrão diferente entre ambientes.
6. **Desempenho e higiene de recurso**: consulta N+1, trabalho síncrono em caminho assíncrono, I/O bloqueante em caminho quente, listener ou handle sem limpeza, serialização desnecessária.
7. **Erro e observabilidade**: exceção engolida, catch genérico, erro logado e não tratado, formato de erro diferente entre módulos, ausência de log estruturado em caminho crítico.
8. **Higiene de segurança**: segredo no código, SQL por concatenação, falta de validação em fronteira, autenticação ou CORS permissivo, criptografia fraca.
9. **Deriva de documentação**: README que não corresponde ao código, comentário que contradiz o vizinho, API pública sem docstring.

## Fase 3: Entregar

Escreva `TECH_DEBT_AUDIT.md` com esta estrutura:

- **Resumo executivo**: no máximo 10 bullets, ordenados por impacto. Números da varredura (quantos críticos, altos, médios, baixos) e onde a dívida se concentra.
- **Modelo mental da arquitetura**: como o sistema é de verdade.
- **Tabela de achados**: colunas `ID | Categoria | Arquivo:Linha | Severidade | Esforço | Descrição | Recomendação`. Mire entre 30 e 80 achados. Passar disso é ruído.
- **Top 5 "se não corrigir mais nada, corrija estes"**: com esboço concreto de mudança, não conselho vago.
- **Ganhos rápidos**: esforço S com severidade média ou maior, em forma de checklist.
- **Parece ruim mas está certo**: decisões que você considerou apontar e escolheu não apontar, com o motivo. **Seção obrigatória.** Se ficou vazia, você não olhou direito.
- **Perguntas abertas para o mantenedor**: o que não deu para saber se é dívida ou intenção.

**Idioma do relatório**: português por padrão. Se o usuário estiver escrevendo em inglês ou o cliente for internacional, entregue em inglês.

## Modo repetição

Se `TECH_DEBT_AUDIT.md` já existe, leia primeiro. Marque achados resolvidos como `RESOLVED`, atualize os que envelheceram e marque os novos como `NEW`. O relatório vira documento vivo, com histórico.

## Modo incremento

Quando o pedido for auditar só o que mudou (revisão de PR grande, entrega de sprint, cliente cobrando evolução), limite o escopo ao diff: `git diff --stat <ref>..HEAD` para achar os arquivos, e rode as dimensões apenas neles. Diga no topo do relatório a referência usada e o intervalo de datas.

## Repositórios grandes

Se o repo passar de 50 mil linhas ou tiver mais de 5 módulos de topo, dispare subagentes em paralelo, um por módulo, e sintetize os relatórios. Leitura serial em repo grande consome a janela de contexto antes de existir achado escrito.

Cada subagente recebe: escopo (um módulo), a lista de dimensões, a exigência de citação e um teto de 200 achados. O agente principal junta, deduplica e ordena. Acima de 200 mil linhas, restrinja o escopo a um módulo e diga isso ao usuário.

## Ferramentas por stack

Detecte a stack pelo manifesto e rode o que existir. Em paralelo quando possível.

- **TypeScript / JavaScript**: `npm audit`, `npx knip` (export morto), `npx madge --circular` (dependência circular), `npx depcheck` (dependência sem uso), `tsc --noEmit` (deriva de tipo).
- **Python**: `pip-audit`, `ruff check`, `vulture` (código morto), `pydeps --show-cycles`, `mypy --strict`.
- **Rust**: `cargo audit`, `cargo udeps`, `cargo machete`, `cargo clippy -- -W clippy::pedantic`.
- **Go**: `govulncheck`, `go vet`, `staticcheck`, `golangci-lint run`.

Ferramenta ausente: registre em limitações e siga. Não bloqueie a auditoria por causa dela.

## Self-check antes de entregar

1. Todo achado tem `arquivo:linha`, e a linha foi conferida depois de escrita?
2. Severidade de cada achado se sustenta na rubrica, sem "crítico" por drama?
3. A seção "parece ruim mas está certo" tem pelo menos 3 itens reais?
4. Algum achado recomenda reescrever em vez de mudar de forma específica?
5. Existe elogio de cortesia, enchimento ou categoria vazia sem "nada material"?
6. Nenhum valor de credencial foi copiado para o relatório?

## Limites

É auditoria estática, não pentest. Pega higiene de segurança óbvia, não substitui teste de intrusão nem modelagem de ameaça. Não pega bug de regra de negócio, porque isso exige conhecimento de domínio que o agente não tem. E não distingue simplicidade intencional de simplicidade acidental: quando não der para saber, pergunte em vez de afirmar.

## Créditos

Adaptado de `ksimback/tech-debt-skill` (MIT), com rubrica de severidade, regra de citação verificada, modo incremento e self-check acrescentados. Texto reescrito em português.

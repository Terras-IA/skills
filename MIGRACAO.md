# Migração inicial (2026-09-24)

De onde veio cada skill quando o repositório nasceu. Depois desta data a fonte é
este repositório; o registro fica só como história.

Origens: `core` é o repositório `terrasia` (commit `95e4209`), `perfil` é
`~/.claude/skills` do servidor, `banco` é o catálogo do motor em `terrasia_dev`.

| Skill | Nome antigo no catálogo | `SKILL.md` veio de | `catalogo.md` veio de |
|---|---|---|---|
| `terras-adr` |  | core:.claude/skills/terras-adr/ | core:skills/operacao/terras-adr.md |
| `terras-agenda-de-touchpoints` | `agenda-de-touchpoints` | core:skills/ifood-beneficios/agenda-de-touchpoints.md (cabeçalho) + core:.claude/skills/terras-agenda-de-touchpoints/SKILL.md (corpo sem marca) |  |
| `terras-analisador-de-linguagem-inclusiva` | `analisador-de-linguagem-inclusiva` | core:skills/ifood-beneficios/analisador-de-linguagem-inclusiva.md (cabeçalho) + core:.claude/skills/terras-analisador-de-linguagem-inclusiva/SKILL.md (corpo sem marca) |  |
| `terras-analisador-de-pulse-semanal` | `analisador-fala-ai-pulse-semanal` | core:skills/ifood-beneficios/analisador-fala-ai-pulse-semanal.md (cabeçalho) + core:.claude/skills/terras-analisador-de-pulse-semanal/SKILL.md (corpo sem marca) |  |
| `terras-api-sync` |  | core:.claude/skills/terras-api-sync/ | core:skills/operacao/terras-api-sync.md |
| `terras-apuracao-retencoes-federais` |  | core:skills/fiscal/apuracao-retencoes-federais.md |  |
| `terras-astro` |  | banco:GET /skills/:name/export |  |
| `terras-audio` |  | core:skills/terras-audio/ |  |
| `terras-azure-devops` |  | banco:GET /skills/:name/export |  |
| `terras-backreview` | `backreview` | core:.claude/skills/backreview/ | core:skills/operacao/backreview.md |
| `terras-banner` |  | core:skills/terras-banner/ |  |
| `terras-bar-raiser-de-cultura` | `bar-raiser-de-cultura` | core:skills/ifood-beneficios/bar-raiser-de-cultura.md (cabeçalho) + core:.claude/skills/terras-bar-raiser-de-cultura/SKILL.md (corpo sem marca) |  |
| `terras-boundary` |  | core:.claude/skills/terras-boundary/ | core:skills/operacao/terras-boundary.md |
| `terras-briefing-pre-reuniao-de-lideranca` | `briefing-pre-reuniao-de-lideranca` | core:skills/ifood-beneficios/briefing-pre-reuniao-de-lideranca.md (cabeçalho) + core:.claude/skills/terras-briefing-pre-reuniao-de-lideranca/SKILL.md (corpo sem marca) |  |
| `terras-care-to-dare-coach` | `care-to-dare-coach` | core:skills/ifood-beneficios/care-to-dare-coach.md (cabeçalho) + core:.claude/skills/terras-care-to-dare-coach/SKILL.md (corpo sem marca) |  |
| `terras-conciliacao-bancaria-ofx` |  | core:skills/financeiro/conciliacao-bancaria-ofx.md |  |
| `terras-conferencia-fechamento-folha` |  | core:skills/dp-rh/conferencia-fechamento-folha.md |  |
| `terras-conferencia-nfe-tomador-prestador` |  | core:skills/fiscal/conferencia-nfe-tomador-prestador.md |  |
| `terras-construtor-de-job-description` | `construtor-de-job-description` | core:skills/ifood-beneficios/construtor-de-job-description.md (cabeçalho) + core:.claude/skills/terras-construtor-de-job-description/SKILL.md (corpo sem marca) |  |
| `terras-cover-letter` |  | core:skills/terras-cover-letter/ |  |
| `terras-dashboard-de-utilizacao-de-beneficios` | `dashboard-de-utilizacao-de-beneficios` | core:skills/ifood-beneficios/dashboard-de-utilizacao-de-beneficios.md (cabeçalho) + core:.claude/skills/terras-dashboard-de-utilizacao-de-beneficios/SKILL.md (corpo sem marca) |  |
| `terras-drift` |  | core:.claude/skills/terras-drift/ | core:skills/operacao/terras-drift.md |
| `terras-elaboracao-proposta-comercial` |  | core:skills/comercial-vendas/elaboracao-proposta-comercial.md |  |
| `terras-fluxo-de-contas-a-pagar` |  | core:skills/financeiro/fluxo-de-contas-a-pagar.md |  |
| `terras-gerador-de-all-hands` | `gerador-de-all-faces` | core:skills/ifood-beneficios/gerador-de-all-faces.md (cabeçalho) + core:.claude/skills/terras-gerador-de-all-hands/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-comunicacao-de-rh` | `gerador-de-comunicacao-de-rh` | core:skills/ifood-beneficios/gerador-de-comunicacao-de-rh.md (cabeçalho) + core:.claude/skills/terras-gerador-de-comunicacao-de-rh/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-matriz-9-box` | `gerador-de-matriz-9-box` | core:skills/ifood-beneficios/gerador-de-matriz-9-box.md (cabeçalho) + core:.claude/skills/terras-gerador-de-matriz-9-box/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-okrs-de-pessoas` | `gerador-de-okrs-de-pessoas` | core:skills/ifood-beneficios/gerador-de-okrs-de-pessoas.md (cabeçalho) + core:.claude/skills/terras-gerador-de-okrs-de-pessoas/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-pdi` | `gerador-de-pdi` | core:skills/ifood-beneficios/gerador-de-pdi.md (cabeçalho) + core:.claude/skills/terras-gerador-de-pdi/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-plano-de-entrevista-estruturada` | `gerador-de-plano-de-entrevista-estruturada` | core:skills/ifood-beneficios/gerador-de-plano-de-entrevista-estruturada.md (cabeçalho) + core:.claude/skills/terras-gerador-de-plano-de-entrevista-estruturada/SKILL.md (corpo sem marca) |  |
| `terras-gerador-de-politica-de-beneficios` | `gerador-de-politica-de-beneficios` | core:skills/ifood-beneficios/gerador-de-politica-de-beneficios.md (cabeçalho) + core:.claude/skills/terras-gerador-de-politica-de-beneficios/SKILL.md (corpo sem marca) |  |
| `terras-gestao-de-ferias-e-escalas` |  | core:skills/dp-rh/gestao-de-ferias-e-escalas.md |  |
| `terras-gestao-de-inadimplencia-cobranca` |  | core:skills/financeiro/gestao-de-inadimplencia-cobranca.md |  |
| `terras-humanizer` |  | core:skills/terras-humanizer/ | core:skills/conteudo/terras-humanizer.md |
| `terras-laravel` |  | banco:GET /skills/:name/export |  |
| `terras-last30days` |  | core:skills/terras-last30days/ | core:skills/conteudo/terras-last30days.md |
| `terras-linkedin` |  | core:skills/terras-linkedin/ |  |
| `terras-notas` |  | core:skills/terras-notas/ |  |
| `terras-people-dashboard-automatico` | `people-dashboard-automatico` | core:skills/ifood-beneficios/people-dashboard-automatico.md (cabeçalho) + core:.claude/skills/terras-people-dashboard-automatico/SKILL.md (corpo sem marca) |  |
| `terras-php` |  | banco:GET /skills/:name/export |  |
| `terras-playbook-quebra-objecoes` |  | core:skills/comercial-vendas/playbook-quebra-objecoes.md |  |
| `terras-ponytail` |  | banco:GET /skills/:name/export |  |
| `terras-postgres` |  | banco:GET /skills/:name/export |  |
| `terras-prompt` |  | core:.claude/skills/terras-prompt/ | core:skills/conteudo/terras-prompt.md |
| `terras-qualidade` |  | core:.claude/skills/terras-qualidade/ | core:skills/operacao/terras-qualidade.md |
| `terras-qualificacao-icp-bant` |  | core:skills/comercial-vendas/qualificacao-icp-bant.md |  |
| `terras-reconstrucao` |  | core:.claude/skills/terras-reconstrucao/ | core:skills/operacao/terras-reconstrucao.md |
| `terras-robo-de-atendimento-de-rh` | `robo-de-atendimento-alli-style` | core:skills/ifood-beneficios/robo-de-atendimento-alli-style.md (cabeçalho) + core:.claude/skills/terras-robo-de-atendimento-de-rh/SKILL.md (corpo sem marca) |  |
| `terras-roteirizador-de-onboarding` | `roteirizador-de-onboarding` | core:skills/ifood-beneficios/roteirizador-de-onboarding.md (cabeçalho) + core:.claude/skills/terras-roteirizador-de-onboarding/SKILL.md (corpo sem marca) |  |
| `terras-screenador-de-curriculos-com-ia` | `screenador-de-curriculos-com-ia` | core:skills/ifood-beneficios/screenador-de-curriculos-com-ia.md (cabeçalho) + core:.claude/skills/terras-screenador-de-curriculos-com-ia/SKILL.md (corpo sem marca) |  |
| `terras-seed` |  | perfil:~/.claude/skills/terras-seed (descrição) + core:.claude/skills/terras-seed (keywords) | core:skills/conteudo/terras-seed.md |
| `terras-simulador-de-oferta` | `simulador-de-oferta` | core:skills/ifood-beneficios/simulador-de-oferta.md (cabeçalho) + core:.claude/skills/terras-simulador-de-oferta/SKILL.md (corpo sem marca) |  |
| `terras-standards` |  | core:.claude/skills/terras-standards/ |  |
| `terras-substack` |  | core:skills/terras-substack/ |  |
| `terras-tech-debt` |  | core:skills/terras-tech-debt/ | core:skills/operacao/terras-tech-debt.md |
| `terras-triagem-riscos-psicossociais` |  | core:skills/dp-rh/triagem-riscos-psicossociais-nr1.md |  |
| `terras-validacao` |  | core:.claude/skills/terras-validacao/ | core:skills/operacao/terras-validacao.md |
| `terras-validacao-regularidade-cadastral` |  | core:skills/fiscal/validacao-regularidade-cadastral.md |  |
| `terras-vercel` |  | banco:GET /skills/:name/export |  |
| `terras-video` |  | core:skills/terras-video/ |  |

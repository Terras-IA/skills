# Manual das skills do terras

> **Arquivo gerado.** Rode `node scripts/manual.mjs` para regravar; não edite à mão.

**130 skills** neste repositório: **119 instaláveis** pelo marketplace, **8 de processo do motor** e **3 ligadas a projeto de cliente**.

## Instalar e usar

**No Claude Code**, pelo marketplace de plugins:

```bash
/plugin marketplace add Terras-IA/skills
/plugin install terras-linkedin@terras
```

Dentro do Claude Code, `/plugin` mostra o catálogo inteiro e instala o que você marcar; depois, `/plugin marketplace update terras` atualiza.

**No ZCode, no Codex (GPT) e no opencode**, por link simbólico, com o repositório como fonte:

```bash
git clone https://github.com/Terras-IA/skills.git ~/terras-skills
bash ~/terras-skills/scripts/instalar.sh            # simulação: mostra o que faria
bash ~/terras-skills/scripts/instalar.sh --aplicar  # executa
```

O script cria um link por skill em cada pasta de agente que já existir na máquina: `~/.zcode/skills` (ZCode), `~/.codex/skills` (Codex/GPT), `~/.config/opencode/skills` (opencode) e `~/.claude/skills` (Claude Code). Pasta de agente que não existe não é criada, e o que já estiver no lugar vai para backup antes de ser substituído. Como o link aponta para o repositório, atualizar tudo depois é `git -C ~/terras-skills pull`.

**Sem link simbólico** (Windows, ou agente que não segue link): copie a pasta `skills/<nome>/` para a pasta de skills do agente. É também o caminho para instalar apenas algumas skills, em vez do conjunto inteiro.

**Um caminho por agente.** O marketplace e o `instalar.sh` entregam a mesma skill por dois caminhos. Num mesmo agente, use só um: com os dois, a skill aparece duas vezes, o modelo escolhe uma pelo nome e pela descrição e não avisa qual rodou.

**Muitas skills instaladas.** O Claude Code entrega ao modelo a lista de skills com orçamento de cerca de 1% da janela de contexto. Com o catálogo inteiro, a descrição que não cabe é cortada e a skill aparece só pelo nome: aí ela quase só roda quando chamada por ele (`/terras-video`). Instale só o que usa, ou aumente o orçamento em `~/.claude/settings.json` com `"env": { "SLASH_COMMAND_TOOL_CHAR_BUDGET": "40000" }` (cerca de 10 mil tokens a mais por sessão).

**Skills só por chamada.** `terras-design-taste-frontend-v1`, `terras-gpt-taste` e `terras-humanizer-dev` repetem o trabalho de outra skill da casa e têm `disable-model-invocation: true`: o modelo não as escolhe sozinho, elas rodam quando você chama pelo nome.

**Como pedir.** A skill certa casa pelas palavras do seu pedido, então citar o termo forte ajuda mais do que pedir genérico: "revisa esse post do LinkedIn", "erro de fila no Laravel", "monta a matriz GUT disso". Cada skill abaixo lista as palavras-chave que a acionam.

## Índice

- [Conteúdo, marca e publicação](#conteúdo-marca-e-publicação) — 17 skills
- [Pessoas, RH e carreira](#pessoas-rh-e-carreira) — 26 skills
- [Financeiro e fiscal](#financeiro-e-fiscal) — 6 skills
- [Comercial e vendas](#comercial-e-vendas) — 3 skills
- [Gestão, processos e decisão](#gestão-processos-e-decisão) — 4 skills
- [Desenvolvimento de software](#desenvolvimento-de-software) — 24 skills
- [Design e front-end](#design-e-front-end) — 16 skills
- [Mídia e apresentação](#mídia-e-apresentação) — 11 skills
- [Pesquisa e radar](#pesquisa-e-radar) — 6 skills
- [IA, prompts e agentes](#ia-prompts-e-agentes) — 6 skills

## Conteúdo, marca e publicação

*Escrever, revisar e publicar na voz certa: LinkedIn, Substack, ebooks e a marca.*

### terras-brand

Marca: voz e tom, frameworks de mensagem, paleta, tipografia, organização de ativos e auditoria de consistência, sincronizadas com os tokens de design. Use para guia de marca, voz da marca ou auditoria. Não gera o quadro visual (terras-brandkit).

`/plugin install terras-brand@terras`

Palavras-chave: `marca`, `brand`, `voz`, `tom de voz`, `identidade visual`, `mensagem`, `auditoria de marca`, `ativos`, `paleta`

### terras-brandkit

Gera a imagem do brand kit: quadro de identidade com direção de logo, paleta, tipografia e aplicações em mockup. Use para quadro de marca, brand book visual, logo system ou moodboard. Não lê identidade de imagens existentes (terras-identidade).

`/plugin install terras-brandkit@terras`

Palavras-chave: `brand kit`, `identidade visual`, `brand guidelines`, `logo`, `marca`, `rebranding`, `mockup`

### terras-canal-whatsapp

Publica texto ou imagem no canal (newsletter) do WhatsApp pela sessão pareada do sidecar, com pré-checagem e confirmação explícita. Use para postar no canal do WhatsApp ou conferir se o canal está pronto. WhatsApp channel publishing.

`/plugin install terras-canal-whatsapp@terras`

Palavras-chave: `whatsapp`, `canal`, `channel`, `newsletter`, `publicar`, `publish`, `post`, `card`, `imagem`, `legenda`, `caption`, `baileys`, `sidecar`

### terras-coders-mural

Engajamento em lote no Mural de Posts da COD3RS: curte, lê o post linkado no LinkedIn e comenta em inglês lá e em português no mural, só com aprovação. Use para mural da COD3RS, coders.com.br, SSI do dia, post do dia ou agendar essa rotina.

`/plugin install terras-coders-mural@terras` · v1.0.0

Palavras-chave: `cod3rs`, `coders`, `mural`, `linkedin`, `engajamento`, `ssi`, `comentario`, `curtir`

### terras-comentarios

Comenta em lote posts do LinkedIn colados pelo usuário: um comentário de até 100 caracteres por post, pronto para colar. Use quando houver 2 ou mais posts para comentar. Post único para responder ou comentar é da terras-linkedin.

`/plugin install terras-comentarios@terras`

Palavras-chave: `comentar`, `comentario`, `comentarios`, `lista de posts`, `lote`, `em lote`, `feed`, `engajamento`, `linkedin`, `resposta curta`, `comentar posts`

### terras-ebook

Cria e-book e audiolivro para vender: estrutura, diagramação EPUB e PDF A5, capa, ISBN, plataforma, royalties, preço e lançamento, e transforma acervo de YouTube em livro. Use para e-book, EPUB, Kindle/KDP, apostila, lead magnet ou 'transformar meus vídeos em livro'.

`/plugin install terras-ebook@terras`

Palavras-chave: `ebook`, `e-book`, `epub`, `pdf`, `livro`, `kdp`, `kindle`, `amazon`, `gumroad`, `payhip`, `kobo`, `apple-books`, `draft2digital`, `isbn`, `capa`, `diagramacao`, `sumario`, `folio`, `royalties`, `preco`, `lancamento`, `lead-magnet`, `playbook`, `apostila`, `audiolivro`, `youtube`, `transcricao`, `self-publishing`, `glossario`, `nota-de-rodape`

### terras-historias-infantis

Histórias infantis ilustradas em quadrinhos e o livro de colorir da mesma história: roteiro página a página, arte vetorial infantil e versão para pintar. Use para gibi, HQ, historinha, livro de colorir, Escola Dominical ou história bíblica para crianças.

`/plugin install terras-historias-infantis@terras`

### terras-humanizer

Reescreve texto com cara de IA para soar humano, sem mudar o que ele diz nem inventar nada; remove marcas de IA em português e inglês e baixa o inglês para nível B1/B2. Use para humanizar ou revisar prosa com cara de IA. Humanize text, plain English.

`/plugin install terras-humanizer@terras` · v1.1.0

Palavras-chave: `humanizar`, `humanizer`, `texto de IA`, `AI writing`, `marcas de IA`, `revisão`, `edição`, `prosa`, `resposta`, `reply`, `português`, `inglês`, `inglês B1 B2`, `vocabulário simples`, `simplificar inglês`, `plain English`

### terras-humanizer-dev

Variante da terras-humanizer que prioriza preservar a voz, as opiniões e o ritmo do autor, aceitando imperfeição natural. Só roda por chamada explícita (/terras-humanizer-dev); para humanizar texto, a padrão é a terras-humanizer. Author voice, natural prose.

`/plugin install terras-humanizer-dev@terras`

Palavras-chave: `humanizar`, `voz do autor`, `escrita natural`, `revisao de texto`

### terras-identidade

Lê a identidade visual de uma marca a partir de imagens (anúncio, print, manual, site) e entrega cores medidas, tipografia, logo recortado e tokens CSS/JSON/Tailwind. Use para extrair paleta e identidade de material existente ou aplicar o visual da marca.

`/plugin install terras-identidade@terras`

Palavras-chave: `identidade`, `identidade visual`, `marca`, `branding`, `brand`, `paleta`, `cores`, `tipografia`, `fonte`, `logo`, `ativo`, `manual de marca`, `design system`, `tokens`, `css`, `tailwind`, `extracao`, `whatsapp`, `peca`, `anuncio`, `cliente`

### terras-linkedin

Escreve e revisa posts de LinkedIn (hook, estrutura, CTA, hashtags, zero travessão) e explica alcance e impressões. Use para post de LinkedIn, por que um post rendeu pouco, ou responder/comentar um post colado de outra pessoa. Lote de posts é da terras-comentarios.

`/plugin install terras-linkedin@terras`

Palavras-chave: `linkedin`, `post`, `escrever`, `redigir`, `revisar`, `comentar`, `comentário`, `responder post`, `post de terceiro`, `resposta curta`, `hook`, `cta`, `hashtags`, `travessao`, `em dash`, `carrossel`, `alcance`, `impressoes`, `distribuição`, `views`, `fora da rede`

### terras-linkedin-alvos

Acompanha perfis-alvo do LinkedIn (executivos, gestores, recrutadores), acha os posts recentes, curte e prepara comentários que acrescentam, publicados só com aprovação. Use para networking com pessoas-chave, 'vê se fulano postou' ou agendar essa rotina.

`/plugin install terras-linkedin-alvos@terras` · v1.0.0

Palavras-chave: `linkedin`, `networking`, `alvos`, `perfis`, `recrutador`, `gestor`, `ceo`, `comentario`, `curtir`, `vaga`

### terras-linkedin-metricas

Extrai, guarda e diagnostica as estatísticas dos posts do LinkedIn do usuário: impressões, alcance na e fora da rede, reações, salvamentos, seguidores e demografia. Use para analisar desempenho de post, comparar posts ou decidir o que repetir.

`/plugin install terras-linkedin-metricas@terras`

Palavras-chave: `linkedin`, `metricas`, `estatisticas`, `desempenho`, `impressoes`, `alcance`, `alcancados`, `fora da rede`, `engajamento`, `salvamentos`, `comentarios`, `seguidores`, `publico`, `demografia`, `relatorio`, `diagnostico`, `post rendeu`, `analytics`

### terras-pauta-mercado

Transforma referência externa (repo, post, anúncio, paper) na análise mercado × TerrasIA com cobre/rejeita/falta e no pacote de posts por canal. Use para link que deve virar análise ou post, comparação com concorrente ou pauta de mercado.

`/plugin install terras-pauta-mercado@terras`

Palavras-chave: `pauta`, `mercado`, `análise de mercado`, `comparação`, `concorrente`, `referência`, `cobertura`, `cobre`, `rejeita`, `falta`, `recibo`, `post`, `linkedin`, `whatsapp`, `substack`

### terras-seo

Auditar, planejar e implementar SEO: SEO técnico, otimização on-page, dados estruturados (schema.org), Core Web Vitals e estratégia de conteúdo. Use quando o pedido for melhorar visibilidade em busca, corrigir SEO, schema markup, sitemap, robots.txt ou mapa de palavras-chave. SEO audit.

`/plugin install terras-seo@terras`

Palavras-chave: `seo`, `schema markup`, `dados estruturados`, `sitemap`, `robots.txt`, `core web vitals`, `palavras-chave`, `otimizacao para buscadores`

### terras-substack

Publica, agenda e gerencia posts e Notes na Substack pela API interna do editor, só com Python do sistema. Use para publicar ou agendar newsletter, criar rascunho, despublicar, subir imagem ou conferir rascunhos. Substack publish, draft, schedule.

`/plugin install terras-substack@terras`

Palavras-chave: `substack`, `publicar`, `publish`, `newsletter`, `rascunho`, `draft`, `note`, `nota`, `agendar`, `schedule`, `unpublish`, `prosemirror`

### terrasia-post-empresa

Produz a peça da Company Page do TerrasIA: post na voz de produto e imagem na identidade da marca (1200x628 e 1080x1350), com régua de texto e aceite no celular. Use para post da empresa ou Company Page. A análise de referência é da terras-pauta-mercado.

`/plugin install terrasia-post-empresa@terras` · v1.0.0

Palavras-chave: `post da empresa`, `linkedin da empresa`, `company page`, `peca da empresa`, `imagem da empresa`, `banner da empresa`, `card`, `identidade do produto`, `publicacao`, `marca`, `terrasia`

## Pessoas, RH e carreira

*Do anúncio da vaga ao ciclo de desenvolvimento: seleção, liderança, folha e carreira.*

### terras-agenda-de-touchpoints

Estrutura 1:1s recorrentes com pautas, histórico de feedback, decisões e loops abertos.

`/plugin install terras-agenda-de-touchpoints@terras` · v1.0.0

Palavras-chave: `1:1`, `one on one`, `agenda de touchpoints`, `cadência de encontros`, `loops abertos`, `reunião individual`, `pauta de 1:1`

### terras-analisador-de-linguagem-inclusiva

Revisa vagas, avaliações e comunicados em busca de linguagem enviesada, excludente ou pouco acessível.

`/plugin install terras-analisador-de-linguagem-inclusiva@terras` · v1.0.0

Palavras-chave: `linguagem inclusiva`, `viés de linguagem`, `texto enviesado`, `termos excludentes`, `análise de viés`, `texto inclusivo`

### terras-analisador-de-pulse-semanal

Processa respostas de pulse survey semanal e transforma temas recorrentes em insights acionáveis para lideranças.

`/plugin install terras-analisador-de-pulse-semanal@terras` · v1.0.0

Palavras-chave: `pulse survey`, `pesquisa de engajamento`, `análise de respostas abertas`, `insights de clima`, `temas recorrentes`

### terras-bar-raiser-de-cultura

Estrutura entrevistas de fit cultural com critérios observáveis, scoring e recomendação; use em processos seletivos que exigem avaliação consistente de valores.

`/plugin install terras-bar-raiser-de-cultura@terras` · v1.0.0

Palavras-chave: `entrevista de cultura`, `fit cultural`, `bar raiser`, `avaliar valores`, `veto de contratação`, `scorecard de entrevista`

### terras-briefing-pre-reuniao-de-lideranca

Prepara briefings para líderes com saúde do time, feedbacks recentes, loops abertos, riscos e perguntas para a reunião.

`/plugin install terras-briefing-pre-reuniao-de-lideranca@terras` · v1.0.0

Palavras-chave: `briefing de liderança`, `reunião de calibração`, `preparar reunião`, `pauta de calibração`, `saúde do time`, `loops abertos`, `brief de uma página`

### terras-care-to-dare-coach

Gera prompts de coaching, scripts de feedback e planos de desafio com base no framework Care to Dare.

`/plugin install terras-care-to-dare-coach@terras` · v1.0.0

Palavras-chave: `care to dare`, `coaching`, `script de feedback`, `conversa difícil`, `plano de desafio`, `feedback`

### terras-conferencia-fechamento-folha

Confere o fechamento da folha antes do envio — horas extras, adicional noturno, faltas e encargos — apontando o que não fecha por matrícula, sem afirmar alíquota nem regra de convenção de memória.

`/plugin install terras-conferencia-fechamento-folha@terras` · v1.0.0

Palavras-chave: `fechamento de folha`, `folha de pagamento`, `hora extra`, `adicional noturno`, `banco de horas`, `inss fgts`, `dsr`, `faltas e atrasos`

### terras-construtor-de-job-description

Gera descrições de cargo claras, inclusivas e alinhadas à cultura e ao modelo de competências da organização.

`/plugin install terras-construtor-de-job-description@terras` · v1.0.0

Palavras-chave: `descrição de vaga`, `job description`, `descrição de cargo`, `abrir vaga`, `requisitos da vaga`, `vaga inclusiva`

### terras-cover-letter

Escreve e revisa cartas de apresentação para vagas internacionais e remotas, traduzindo experiência brasileira em valor global. Use para cover letter, carta de apresentação, InMail para recrutador ou mensagem de candidatura para empresa de fora.

`/plugin install terras-cover-letter@terras`

Palavras-chave: `cover letter`, `carta de apresentação`, `candidatura`, `vaga internacional`, `gringa`, `remoto`, `remote`, `inmail`, `recrutador`, `job application`

### terras-dashboard-de-utilizacao-de-beneficios

Analisa adesão, utilização, custo e satisfação dos benefícios por tipo de saldo, período e público permitido.

`/plugin install terras-dashboard-de-utilizacao-de-beneficios@terras` · v1.0.0

Palavras-chave: `utilização de benefícios`, `dashboard de benefícios`, `adesão ao benefício`, `va e vr`, `va vr`, `mobilidade`, `custo de benefícios`, `satisfação com benefícios`

### terras-educacao-corporativa

Educação corporativa com 26 prompts guiados: estratégia de T&D, diagnóstico de necessidades, mapa de competências, trilhas, planos de aula e indicadores de impacto. Use para T&D, L&D, trilha de aprendizagem, ROI de treinamento ou workshop corporativo.

`/plugin install terras-educacao-corporativa@terras`

Palavras-chave: `educação corporativa`, `educacao corporativa`, `treinamento`, `t&d`, `trilha de aprendizagem`, `jornada de aprendizagem`, `competências`, `competencias`, `diagnóstico de necessidades`, `design instrucional`, `plano de aula`, `workshop`, `avaliação de treinamento`, `kirkpatrick`, `bloom`, `onboarding`, `blended`, `corporate education`, `learning and development`, `training design`

### terras-gerador-de-all-hands

Prepara o encontro mensal de toda a empresa com resumo de resultados, perguntas votadas e talking points.

`/plugin install terras-gerador-de-all-hands@terras` · v1.0.0

Palavras-chave: `all hands`, `encontro mensal da empresa`, `perguntas votadas`, `talking points`, `reunião geral`

### terras-gerador-de-comunicacao-de-rh

Redige comunicados internos claros sobre políticas, mudanças organizacionais, benefícios e atualizações de People.

`/plugin install terras-gerador-de-comunicacao-de-rh@terras` · v1.0.0

Palavras-chave: `comunicado interno`, `comunicação de rh`, `aviso aos colaboradores`, `mudança de política`, `comunicado de home office`, `faq`

### terras-gerador-de-matriz-9-box

Organiza performance e potencial em uma matriz 9-Box com critérios, evidências e planos de ação por quadrante.

`/plugin install terras-gerador-de-matriz-9-box@terras` · v1.0.0

Palavras-chave: `9 box`, `matriz de talentos`, `performance e potencial`, `calibração de talentos`, `quadrante`, `nove box`

### terras-gerador-de-okrs-de-pessoas

Cria OKRs trimestrais de People conectados à estratégia do negócio, com resultados mensuráveis e responsáveis.

`/plugin install terras-gerador-de-okrs-de-pessoas@terras` · v1.0.0

Palavras-chave: `okr`, `okrs de pessoas`, `objetivos e resultados-chave`, `okr trimestral`, `metas de people`

### terras-gerador-de-pdi

Cria planos de desenvolvimento individual conectando feedbacks, competências, ações, recursos e evidências de evolução.

`/plugin install terras-gerador-de-pdi@terras` · v1.0.0

Palavras-chave: `pdi`, `plano de desenvolvimento individual`, `gaps de competência`, `ações 70 20 10`, `desenvolvimento da pessoa`, `plano de desenvolvimento`

### terras-gerador-de-plano-de-entrevista-estruturada

Cria roteiros por competência com perguntas comportamentais, sinais de evidência e rubrica de avaliação.

`/plugin install terras-gerador-de-plano-de-entrevista-estruturada@terras` · v1.0.0

Palavras-chave: `plano de entrevista`, `entrevista estruturada`, `roteiro de perguntas`, `rubrica de avaliação`, `perguntas comportamentais`, `painel de entrevistas`

### terras-gerador-de-politica-de-beneficios

Redige políticas de benefícios claras, aplicáveis e alinhadas ao PAT e ao orçamento informado pela empresa.

`/plugin install terras-gerador-de-politica-de-beneficios@terras` · v1.0.0

Palavras-chave: `política de benefícios`, `benefício flexível`, `pat`, `regras de benefícios`, `política de va e vr`, `elegibilidade de benefícios`

### terras-gestao-de-ferias-e-escalas

Organiza períodos aquisitivo e concessivo, abono e fracionamento por equipe, e mostra onde a escala não se sustenta — com os prazos informados pela empresa, não de memória.

`/plugin install terras-gestao-de-ferias-e-escalas@terras` · v1.0.0

Palavras-chave: `periodo aquisitivo`, `periodo concessivo`, `abono pecuniario`, `escala de ferias`, `vender ferias`, `ferias vencidas`, `fracionamento de ferias`

### terras-people-dashboard-automatico

Monta um dashboard mensal de liderança com headcount, retenção, remuneração, contratação e DEI.

`/plugin install terras-people-dashboard-automatico@terras` · v1.0.0

Palavras-chave: `people dashboard`, `dashboard de rh`, `headcount`, `turnover`, `retenção de pessoas`, `people analytics`, `indicadores de rh`

### terras-robo-de-atendimento-de-rh

Estrutura um atendimento de auto serviço para dúvidas de férias, benefícios, políticas e folha, com encaminhamento seguro para casos complexos.

`/plugin install terras-robo-de-atendimento-de-rh@terras` · v1.0.0

Palavras-chave: `atendimento de rh`, `autoatendimento`, `bot de rh`, `dúvidas de férias`, `fluxo de atendimento`, `encaminhamento humano`

### terras-roteirizador-de-onboarding

Monta um plano de onboarding de 30, 60 e 90 dias com check-ins, tarefas e expectativas claras para a nova pessoa.

`/plugin install terras-roteirizador-de-onboarding@terras` · v1.0.0

Palavras-chave: `onboarding`, `plano de 30 60 90 dias`, `integração de pessoa nova`, `check-ins de onboarding`, `buddy`, `primeira semana`

### terras-screenador-de-curriculos-com-ia

Ranqueia currículos por requisitos da vaga e anonimiza dados sensíveis para apoiar uma triagem mais justa e auditável.

`/plugin install terras-screenador-de-curriculos-com-ia@terras` · v1.0.0

Palavras-chave: `triagem de currículos`, `rankear candidatos`, `anonimizar currículos`, `filtro de currículo`, `triagem justa`, `screening`

### terras-simulador-de-oferta

Simula propostas de remuneração considerando benchmark de mercado, equidade interna e cenários de negociação.

`/plugin install terras-simulador-de-oferta@terras` · v1.0.0

Palavras-chave: `simular oferta`, `proposta de remuneração`, `contraproposta`, `faixa salarial`, `equity`, `compressão salarial`, `negociação de salário`

### terras-triagem-riscos-psicossociais

Lê sinais agregados de sobrecarga e atrito de uma equipe e entrega indícios com evidência para a gestão avaliar, sem diagnosticar pessoa, sem dado de saúde e sem individualizar quem não pode ser individualizado.

`/plugin install terras-triagem-riscos-psicossociais@terras` · v1.0.0

Palavras-chave: `risco psicossocial`, `riscos psicossociais`, `sobrecarga cronica`, `iso 45003`, `clima organizacional`, `burnout na equipe`, `horas extras recorrentes`, `rotatividade`

### terrasia-vagas-coders

Filtra as vagas do board da COD3RS contra o currículo do usuário em baldes A (recomendar), B (talvez) e C (descarte com motivo) e, com aprovação por vaga, avança na candidatura. Use para vagas da COD3RS, 'o que tem de vaga pra mim' ou aplicar nas aprovadas.

`/plugin install terrasia-vagas-coders@terras` · v1.0.0

Palavras-chave: `cod3rs`, `coders`, `vagas`, `board`, `curriculo`, `triagem`, `emprego`, `remote`, `senior`, `fit`

## Financeiro e fiscal

*Contas a pagar, conciliação, notas fiscais, retenções e inadimplência.*

### terras-apuracao-retencoes-federais

Confere se as retenções federais na fonte de uma nota de serviço foram aplicadas, dispensadas ou esquecidas, usando as alíquotas e limites informados pela empresa, nunca de memória.

`/plugin install terras-apuracao-retencoes-federais@terras` · v1.0.0

Palavras-chave: `retencao na fonte`, `retencoes federais`, `irrf`, `pis cofins csll`, `csrf`, `inss retido`, `darf`, `imposto retido`

### terras-conciliacao-bancaria-ofx

Concilia extrato bancário com os lançamentos internos e separa o que casou, o que divergiu, o que é tarifa e o que ficou sem par.

`/plugin install terras-conciliacao-bancaria-ofx@terras` · v1.0.0

Palavras-chave: `conciliar`, `conciliação`, `extrato`, `ofx`, `fechar o caixa`, `saldo não bate`, `tarifa`

### terras-conferencia-nfe-tomador-prestador

Confere uma nota fiscal recebida ou emitida campo a campo e separa o que está consistente do que precisa de decisão humana, sem afirmar alíquota nem enquadramento por conta própria.

`/plugin install terras-conferencia-nfe-tomador-prestador@terras` · v1.0.0

Palavras-chave: `nota fiscal`, `nf-e`, `nfs-e`, `cfop`, `ncm`, `issqn`, `icms`, `bitributacao`, `danfe`, `xml da nota`

### terras-fluxo-de-contas-a-pagar

Leva uma conta a pagar da chegada do documento até a liberação: autenticidade do boleto, alçada por valor e escalonamento.

`/plugin install terras-fluxo-de-contas-a-pagar@terras` · v1.0.0

Palavras-chave: `boleto`, `contas a pagar`, `pagamento`, `alçada`, `boleto de fornecedor`, `liberar pagamento`

### terras-gestao-de-inadimplencia-cobranca

Monta a régua de cobrança de D-3 a D+15 com o tom de cada contato, os encargos do contrato e o ponto de decisão.

`/plugin install terras-gestao-de-inadimplencia-cobranca@terras` · v1.0.0

Palavras-chave: `cobrança`, `cobrar`, `inadimplência`, `título vencido`, `não pagou`, `atraso`, `régua`

### terras-validacao-regularidade-cadastral

Organiza a checagem de idoneidade de um fornecedor ou parceiro — o que precisa ser verificado, onde, com que validade — e registra o que ficou sem comprovação.

`/plugin install terras-validacao-regularidade-cadastral@terras` · v1.0.0

Palavras-chave: `regularidade fiscal`, `certidao negativa`, `cnd`, `idoneidade`, `homologacao de fornecedor`, `situacao cadastral`, `cnpj do fornecedor`, `inscricao estadual`

## Comercial e vendas

*Proposta, qualificação de lead e resposta a objeção.*

### terras-elaboracao-proposta-comercial

Estrutura a minuta de uma proposta a partir do que foi levantado na conversa, separando escopo de expectativa e marcando cada número que ainda precisa de confirmação antes de sair.

`/plugin install terras-elaboracao-proposta-comercial@terras` · v1.0.0

Palavras-chave: `proposta comercial`, `minuta de proposta`, `escopo do projeto`, `precificacao`, `roi da entrega`, `orcamento para cliente`, `contraproposta comercial`, `contraproposta do cliente`

### terras-playbook-quebra-objecoes

Classifica a objeção real por trás do que o cliente disse e devolve caminhos de resposta apoiados no que a empresa consegue sustentar, sem prometer preço, prazo ou funcionalidade que não existem.

`/plugin install terras-playbook-quebra-objecoes@terras` · v1.0.0

Palavras-chave: `objecao`, `quebra de objecoes`, `esta caro`, `vou pensar`, `concorrente`, `desconto`, `cliente sumiu`, `follow up de proposta`

### terras-qualificacao-icp-bant

Qualifica um lead a partir do que foi dito na conversa — orçamento, autoridade, necessidade e timing — separando o que o cliente afirmou do que o vendedor supôs, e dizendo o que falta perguntar.

`/plugin install terras-qualificacao-icp-bant@terras` · v1.0.0

Palavras-chave: `qualificacao de lead`, `bant`, `icp`, `lead qualificado`, `discovery`, `perfil de cliente ideal`, `vale a pena esse lead`, `descartar lead`

## Gestão, processos e decisão

*Mapear processo, priorizar problema e decidir com rastro.*

### terras-analise-swot

Análise SWOT rastreável: cada item cita a fonte, o que não tem fonte vira hipótese com teste, e fecha em cruzamentos TOWS com ação, dono e verificação. Use para SWOT, análise de cenário, posição competitiva ou preparo de decisão estratégica.

`/plugin install terras-analise-swot@terras` · v1.0.0

Palavras-chave: `swot`, `analise swot`, `forcas`, `fraquezas`, `oportunidades`, `ameacas`, `tows`, `matriz swot`, `analise de cenario`, `posicao competitiva`, `planejamento estrategico`, `analise estrategica`, `decisao estrategica`, `cenario competitivo`

### terras-mapeamento-de-processos

Mapeia um processo a partir de áudio, gravação de tela ou relato e devolve o fluxo AS-IS/TO-BE, diagnóstico com números e plano de melhoria com oportunidades de automação. Use para mapear processo, achar gargalo ou automatizar rotina operacional.

`/plugin install terras-mapeamento-de-processos@terras` · v1.4.0

Palavras-chave: `mapeamento de processo`, `mapear processo`, `processo`, `fluxograma`, `bpmn`, `as is`, `to be`, `gargalo`, `diagnostico de processo`, `melhoria de processo`, `automacao de processo`, `lean`, `desperdicio`, `lead time`, `sop`, `procedimento operacional`, `retrabalho`, `sla`

### terras-matriz-gut

Prioriza problemas concorrentes com a matriz GUT: notas ancoradas de Gravidade, Urgência e Tendência, faixa de decisão antes de pontuar e plano de ataque com dono e prazo. Use para priorizar fila, decidir por onde começar ou quando 'tudo é urgente'.

`/plugin install terras-matriz-gut@terras` · v1.0.0

Palavras-chave: `gut`, `matriz gut`, `priorizacao`, `priorizar`, `gravidade`, `urgencia`, `tendencia`, `prioridade`, `criticidade`, `ordenar problemas`, `fila de demandas`, `por onde comecar`, `escala de prioridade`, `desempate`, `backlog priorizado`

### terras-pipeline-de-automacao

Projeta pipelines de automação em que scripts determinísticos fazem o trabalho e o agente só decide em pontos de revisão, com rastro de hashes e recibos de execução. Use para automatizar processo repetitivo de ponta a ponta ou consertar pipeline que refaz ou perde trabalho.

`/plugin install terras-pipeline-de-automacao@terras` · v1.0.0

Palavras-chave: `pipeline`, `pipes and filters`, `rastro`, `recibo`, `idempotencia`, `provenance`, `receipts`, `hash`, `acervo`, `automacao`, `producao`, `revisao`, `agentic`

## Desenvolvimento de software

*Stack, banco de dados, testes, segurança e padrões de engenharia.*

### terras-astro

Publica site estático multilíngue de graça no Cloudflare Pages com Astro e conteúdo em markdown. Use para criar site ou blog estático, configurar i18n, converter markdown em site e subir hospedagem gratuita.

`/plugin install terras-astro@terras`

Palavras-chave: `astro.js`, `site astro`, `projeto astro`, `framework astro`, `cloudflare pages`

### terras-azure-devops

List Azure DevOps projects, repositories, and branches; create pull requests; manage work items; check build status. Use when working with Azure DevOps resources, checking PR status, querying project structure, or automating DevOps workflows.

`/plugin install terras-azure-devops@terras`

Palavras-chave: `azure devops`, `azure repos`, `azure pipelines`, `azure boards`, `work item`

### terras-consolidacao-de-memoria

Mantém a memória de um repositório pequena e verdadeira: ao fechar uma spec, registra o que foi entregue e funde os requisitos num doc por domínio; compacta o histórico de decisões antigo em temas; audita convenção que o código já não segue. Só propõe, o dono aprova.

`/plugin install terras-consolidacao-de-memoria@terras` · v1.0.0

Palavras-chave: `consolidar specs`, `compactar historico`, `memoria do projeto`, `docs por dominio`, `fechar spec`, `changelog da spec`, `drift de convencao`, `documentacao inchada`

### terras-critica-de-spec

Critica uma spec antes da implementação (critério de aceite que não dá para testar, caso de borda faltando, escopo ambíguo, contradição, regra do repositório violada) e conduz a revisão com o autor, inclusive a divergência entre spec e código.

`/plugin install terras-critica-de-spec@terras` · v1.0.0

Palavras-chave: `critica de spec`, `revisar spec`, `revisao de especificacao`, `criterio de aceite`, `casos de borda`, `escopo ambiguo`, `spec drift`, `refinar spec`

### terras-database-migrations

Migrations seguras e reversíveis: expand-contract sem downtime, índice concorrente, backfill em lotes e fluxo por ferramenta (PostgreSQL, Prisma, Drizzle, Kysely, Django, golang-migrate). Use ao escrever migration, mexer em tabela grande ou planejar rollback.

`/plugin install terras-database-migrations@terras`

Palavras-chave: `migration`, `migracao`, `migracoes`, `expand-contract`, `zero downtime`, `backfill`, `rollback`, `alter table`, `create index concurrently`

### terras-e2e-testing

Testes end-to-end com Playwright: Page Object Model, configuração, integração com CI, artefatos (trace, vídeo, screenshot) e estratégia para teste instável. Use ao escrever teste Playwright, estruturar page objects ou consertar e2e flaky no CI. Playwright E2E testing.

`/plugin install terras-e2e-testing@terras`

Palavras-chave: `playwright`, `e2e`, `end-to-end`, `page object`, `teste flaky`, `flaky test`, `teste de ponta a ponta`

### terras-governanca-padroes

Audita onde as convenções de um projeto vivem e as transforma em regra versionada, com dono, revisão e deprecação, legível por agente. Use para auditar ou padronizar convenções de um repositório ou tirar regras da wiki. Governance rules, AGENTS.md.

`/plugin install terras-governanca-padroes@terras`

Palavras-chave: `governança`, `convenções`, `padrões`, `governance rules`, `conventions`, `standards`, `auditoria`, `versionamento`, `deprecação`

### terras-laravel

Build robust Laravel apps avoiding Eloquent traps, queue failures, and auth pitfalls.

`/plugin install terras-laravel@terras` · v1.0.1

Palavras-chave: `laravel`, `eloquent`, `artisan`

### terras-mcp-server

Construção de servidor MCP com o SDK Node/TypeScript: tools, resources, prompts, validação com Zod e escolha de transporte (stdio ou Streamable HTTP). Use ao criar ou depurar um servidor MCP. MCP server patterns.

`/plugin install terras-mcp-server@terras`

Palavras-chave: `mcp server`, `servidor mcp`, `model context protocol`, `mcp sdk`, `streamable http`, `json-rpc`

### terras-miniapp-builder

Cria miniapp do zero: entrevista as lacunas, decide arquitetura e LGPD, escreve a copy, constrói local-first e publica na Vercel. Use para criar app, miniapp ou PWA novo, ou 'transforma esse conteúdo em app'. Miniapp, PWA, publicar na Vercel.

`/plugin install terras-miniapp-builder@terras`

Palavras-chave: `miniapp`, `mini-app`, `criar app`, `novo app`, `gerar app`, `aplicativo`, `pwa`, `app de bolso`, `publicar app`, `vercel`, `google stitch`, `lgpd`, `psicologia das cores`, `paleta`, `copy`, `objecao`, `crenca limitante`, `pitch`, `local-first`

### terras-php

Write solid PHP avoiding type juggling traps, array quirks, and common security pitfalls.

`/plugin install terras-php@terras` · v1.0.1

Palavras-chave: `php`, `composer`

### terras-plano-tdd

Transforma uma spec revisada em plano test-first (RED, GREEN, REFACTOR) com arquivo e nome de teste concretos, e uma lista de tarefas em que cada uma diz por comando o que é estar pronta. Use para planejar a implementação de uma feature com TDD.

`/plugin install terras-plano-tdd@terras` · v1.0.0

Palavras-chave: `plano tdd`, `plano de implementacao`, `test-first`, `red green refactor`, `tarefas`, `definicao de pronto`, `done`, `checklist de tarefas`, `planejar feature`

### terras-ponytail

Lazy senior dev mode for any coding task (write, refactor, fix, review): YAGNI, stdlib first, no unrequested abstractions. Not for non-coding requests.

`/plugin install terras-ponytail@terras`

Palavras-chave: `over-engineering`, `overengineering`, `over engineering`, `simplificar o codigo`, `yagni`

### terras-postgres

Administra e otimiza banco PostgreSQL pelas tools do postgres-mcp: verificação de saúde, ajuste de índice, análise de plano de consulta, leitura de schema e execução de SQL. Use quando pedirem Postgres, otimização de banco, índice lento ou desempenho de query.

`/plugin install terras-postgres@terras`

Palavras-chave: `postgres`, `postgresql`, `query lenta`, `explain analyze`

### terras-react-patterns

Padrões de React 18/19: disciplina de hooks, fronteira entre server e client component, Suspense e error boundary, form actions, busca de dados, árvore de decisão de estado e composição acessível. Use ao escrever ou revisar componente React. React patterns.

`/plugin install terras-react-patterns@terras`

Palavras-chave: `react`, `hooks`, `useeffect`, `suspense`, `error boundary`, `server component`, `componente react`

### terras-react-testing

Testes de componente React com React Testing Library, Vitest ou Jest, MSW para simular rede, asserções de acessibilidade com axe, e quando usar teste de componente em vez de e2e. Use ao escrever ou consertar teste de componente, hook ou página React. React testing.

`/plugin install terras-react-testing@terras`

Palavras-chave: `react testing library`, `testing library`, `vitest`, `jest`, `msw`, `teste de componente`, `jsdom`

### terras-reverse-engineer

Investiga como uma feature funciona em software empacotado (Electron, site, APK, binário nativo, .NET, firmware) com o REA, cada conclusão presa a uma evidência. Use para 'como esse app faz X', decompilar ou comparar versões. Não é para código-fonte aberto.

`/plugin install terras-reverse-engineer@terras` · v6.3.0

Palavras-chave: `engenharia reversa`, `reverse engineering`, `rea`, `decompilar`, `electron`, `asar`, `apk`, `binario`, `elf`, `dotnet`, `har`, `feature`

### terras-revisao-cruzada

Manda uma spec ou um diff, em paralelo, para agentes de linha de comando de outros fornecedores (Codex, opencode) e junta os vereditos num revisao.md único, com concordâncias, divergências e a próxima ação. Pega o ponto cego que um modelo só não vê.

`/plugin install terras-revisao-cruzada@terras` · v1.0.0

Palavras-chave: `revisao cruzada`, `segunda opiniao`, `codex`, `opencode`, `outro modelo`, `revisar diff`, `revisar spec`, `quorum`, `multi-modelo`

### terras-revisao-de-codigo

Revisa uma mudança de código pelo risco que ela cria, com foco em integração que movimenta dinheiro ou dado de cliente: correção, idempotência, falha parcial, segredo, dado pessoal e teste que prova.

`/plugin install terras-revisao-de-codigo@terras` · v1.0.0

Palavras-chave: `revisao de codigo`, `revisar o codigo`, `revise o codigo`, `revisa o codigo`, `code review`, `pull request`

### terras-security-review

Checklist e padrões de segurança para código: autenticação, entrada do usuário, segredos, endpoints de API, pagamento e dados sensíveis, com anexo de segurança de infraestrutura em nuvem. Use ao mexer em login, input, segredo, rota nova ou fluxo sensível. Security review checklist.

`/plugin install terras-security-review@terras`

Palavras-chave: `security review`, `revisao de seguranca`, `autenticacao`, `authentication`, `xss`, `sql injection`, `csrf`, `owasp`, `secrets`, `segredos`

### terras-standards

Aplica os Padrões Agnósticos de Engenharia e Produto v4.0 (arquitetura, segurança, privacidade e IA) com evidência real quando houver. Use para 'padrões de engenharia', gate de produção, AIP/RIPD/ROPA, ISO 27001, conformidade, evidência de auditoria ou ADR.

`/plugin install terras-standards@terras`

### terras-tech-debt

Auditoria de dívida técnica e arquitetura de um repositório inteiro, com achados em arquivo:linha, severidade, esforço e a seção 'parece ruim mas está certo'. Use para diagnóstico de codebase, health check ou revisão de arquitetura. Tech debt audit.

`/plugin install terras-tech-debt@terras`

Palavras-chave: `auditoria`, `dívida técnica`, `tech debt`, `arquitetura`, `codebase`, `revisão de código`, `refatoração`, `legado`, `severidade`, `relatório técnico`

### terras-vercel

Deploy applications and manage projects with complete CLI reference. Commands for deployments, projects, domains, environment variables, and live documentation access.

`/plugin install terras-vercel@terras`

Palavras-chave: `vercel`

### terras-vite

Padrões do Vite: config, plugins, HMR, variáveis de ambiente (e o que vaza no bundle), proxy, SSR, modo biblioteca, pré-bundling de dependências e otimização de build. Use ao mexer em vite.config.ts, plugin do Vite ou projeto baseado em Vite. Vite patterns.

`/plugin install terras-vite@terras`

Palavras-chave: `vite`, `vite.config`, `hmr`, `import.meta.env`, `variaveis vite`, `vite plugin`

## Design e front-end

*Identidade, UI, design system e geração de telas.*

### terras-accessibility

Projetar, implementar e auditar interface acessível no nível AA da WCAG 2.2 em Web, iOS e Android: papéis e rótulos ARIA, foco, contraste, tamanho de alvo e leitor de tela. Use ao construir ou auditar UI para acessibilidade, navegação por teclado ou leitor de tela. Accessibility, a11y.

`/plugin install terras-accessibility@terras`

Palavras-chave: `acessibilidade`, `accessibility`, `a11y`, `wcag`, `aria`, `leitor de tela`, `screen reader`, `contraste`

### terras-design

Guarda-chuva de design: logo com IA, identidade corporativa (CIP), pacote amplo de peças; roteia para terras-brand, terras-design-system e terras-ui-styling. Use quando o pedido de design for amplo ou não estiver claro qual peça se quer. Logo design, corporate identity.

`/plugin install terras-design@terras`

Palavras-chave: `design`, `logo`, `identidade corporativa`, `cip`, `papelaria`, `mockup`, `apresentação`, `banner`, `social media`, `ícones`, `roteamento`

### terras-design-system

Design tokens em três camadas (primitivo, semântico, componente), specs e estados de componente, variáveis CSS e tema Tailwind. Use para criar ou validar tokens, definir estados de componente, montar tema Tailwind ou preparar handoff. Design tokens, component specs.

`/plugin install terras-design-system@terras`

Palavras-chave: `design tokens`, `tokens`, `css variables`, `tailwind`, `componentes`, `specs`, `escalas`, `handoff`

### terras-design-taste-frontend

Anti-slop de frontend: lê o briefing, infere a direção de design e entrega landing page, portfólio ou redesign que não parece template. É a padrão da casa para página web com qualidade de design. Anti-slop, landing page, frontend design.

`/plugin install terras-design-taste-frontend@terras`

Palavras-chave: `anti-slop`, `landing page`, `portfólio`, `design`, `frontend`, `redesenho`

### terras-design-taste-frontend-v1

Versão 1 legada da terras-design-taste-frontend, preservada para projetos que dependem do comportamento exato da v1. Só roda por chamada explícita (/terras-design-taste-frontend-v1); para frontend novo, use a terras-design-taste-frontend. Legacy v1.

`/plugin install terras-design-taste-frontend-v1@terras`

Palavras-chave: `v1`, `legado`, `compatibilidade`, `frontend design`

### terras-gpt-taste

Variante estrita do design-taste para GPT/Codex: layout com randomização real, AIDA, bento sem buracos, GSAP e anti-slop agressivo. Só roda por chamada explícita (/terras-gpt-taste); a padrão da casa é a terras-design-taste-frontend. Awwwards, GSAP.

`/plugin install terras-gpt-taste@terras`

Palavras-chave: `gpt`, `codex`, `awwwards`, `landing page`, `gsap`, `bento`, `motion`, `anti-slop`

### terras-high-end-visual-design

Design visual de alto padrão: fontes, espaçamento, sombras, cartões e animações que fazem o site parecer caro, bloqueando o visual barato de IA. Use para algo premium, com cara de agência ou Apple/Linear. High-end, premium design.

`/plugin install terras-high-end-visual-design@terras`

Palavras-chave: `premium`, `alto padrão`, `sofisticado`, `agência`, `animação`, `tipografia`

### terras-image-to-code

Pipeline imagem-primeiro: gera a imagem de referência, analisa e implementa o frontend fiel a ela, seção a seção. Use para transformar design, mockup ou screenshot em código ou reproduzir uma página com alta fidelidade. Image to code.

`/plugin install terras-image-to-code@terras`

Palavras-chave: `image to code`, `design to code`, `mockup`, `frontend`, `implementação`, `fidelidade`

### terras-imagegen-frontend-mobile

Gera imagens de telas e fluxos de app mobile (iOS, Android, cross-platform) com mockup de celular, tipografia legível, paleta controlada e consistência entre telas. Só gera imagem, não escreve código. Use quando precisar de referência visual de app mobile. Mobile app screens, mockup, imagegen.

`/plugin install terras-imagegen-frontend-mobile@terras`

Palavras-chave: `mobile`, `app`, `ios`, `android`, `mockup`, `telas`, `imagegen`

### terras-imagegen-frontend-web

Gera as imagens de referência de um site — uma imagem horizontal por seção, nunca comprimidas — com variedade de composição, escala de hero, CTA e paleta única. Use quando precisar de comps/design de página web (landing, marketing, produto) antes de codar. Frontend image generation, website comps.

`/plugin install terras-imagegen-frontend-web@terras`

Palavras-chave: `imagem`, `site`, `landing`, `hero`, `comps`, `referência visual`, `imagegen`

### terras-industrial-brutalist-ui

Interface brutalista industrial: grade suíça rígida, tipografia mecânica de contraste extremo, paleta utilitária e textura analógica. Use para UI crua, painel técnico denso, dashboard de telemetria ou editorial com cara de blueprint. Industrial brutalism.

`/plugin install terras-industrial-brutalist-ui@terras`

Palavras-chave: `brutalista`, `industrial`, `swiss`, `tipografia`, `dashboard`, `terminal`, `blueprint`, `UI`

### terras-minimalist-ui

UI minimalista editorial: paleta monocromática quente, hierarquia tipográfica, bento grid flat e pastéis discretos; sem gradientes nem sombras pesadas. Use quando pedirem interface minimalista, limpa, estilo Notion/Linear ou document-style. Minimalist UI, editorial, clean interface.

`/plugin install terras-minimalist-ui@terras`

Palavras-chave: `minimalista`, `minimal`, `editorial`, `notion`, `linear`, `bento`, `clean`

### terras-redesign-existing-projects

Redesign de projeto existente: audita a UI atual, identifica padrões genéricos de IA e aplica padrão premium sem quebrar funcionalidade. Use para melhorar, repaginar ou modernizar site ou app que já existe. Audit-first redesign.

`/plugin install terras-redesign-existing-projects@terras`

Palavras-chave: `redesign`, `auditar UI`, `melhorar design`, `repaginar`, `upgrade visual`

### terras-stitch-design-taste

Gera o DESIGN.md para o Google Stitch: contrato de design premium anti-genérico (tipografia estrita, cor calibrada, layout assimétrico, micro-motion). Use quando o alvo for o Stitch ou o projeto precisar de DESIGN.md como contrato de design.

`/plugin install terras-stitch-design-taste@terras`

Palavras-chave: `stitch`, `design system`, `DESIGN.md`, `micro-motion`, `tipografia`

### terras-ui-styling

Implementa interface com shadcn/ui e Tailwind CSS: componentes, tema, acessibilidade, responsividade e design em canvas. Use para implementar UI em código com shadcn/Tailwind ou configurar tema e componentes acessíveis. shadcn/ui, Tailwind.

`/plugin install terras-ui-styling@terras`

Palavras-chave: `shadcn`, `shadcn/ui`, `tailwind`, `componentes`, `theming`, `tema`, `acessibilidade`, `canvas`, `responsivo`, `ui`

### terras-ui-ux-pro-max

Base local de UI/UX com busca própria: estilos, paletas por produto, pares tipográficos, diretrizes de UX e guias de stack; gera o design system do produto em MASTER.md. Use para definir direção visual, escolher estilo, paleta e tipografia ou checar regra de UX.

`/plugin install terras-ui-ux-pro-max@terras`

Palavras-chave: `ui`, `ux`, `design system`, `estilos`, `paletas`, `tipografia`, `cores`, `diretrizes de ux`, `acessibilidade`, `gráficos`, `stacks`, `gsap`

## Mídia e apresentação

*Áudio, vídeo, banner, slides e diagramas.*

### terras-animacao

Peça animada em loop (GIF e MP4 sem som) a partir de cena HTML dirigida por tempo, renderizada quadro a quadro. Use para animação, gif, banner animado ou diagrama que se desenha. Não é banner estático (terras-banner), vídeo narrado (terras-video) nem edição (terras-ffmpeg).

`/plugin install terras-animacao@terras` · v1.0.0

Palavras-chave: `animacao`, `animado`, `gif`, `gif animado`, `loop`, `video curto`, `mp4`, `movimento`, `motion`, `banner animado`, `peca animada`, `diagrama animado`, `bpmn animado`, `quadro a quadro`

### terras-audio

Voz, pronúncia e cadeia de áudio para narração de vídeo, audiolivro, nota de voz e capítulo. Use para narração, locução, TTS, audiolivro, m4b, pronúncia de termo em inglês, loudness, ou quando uma palavra soa errada ou o áudio ficou baixo.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `audio`, `voz`, `narracao`, `locucao`, `tts`, `edge-tts`, `audiolivro`, `audiobook`, `m4b`, `capitulo`, `pronuncia`, `sotaque`, `respelling`, `loudness`, `lufs`, `normalizacao`, `mp3`

### terras-banner

Imagem que acompanha post, newsletter ou nota: banner 1200x628 (LinkedIn, og:image da Substack), card 1080x1350 e capa, com arte gerada, tipografia da marca e gate visual. Use para imagem, banner, capa, thumbnail, card ou 'faz a imagem disso'.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `banner`, `imagem`, `capa`, `thumbnail`, `card`, `og:image`, `substack`, `linkedin`, `arte`, `visual`, `png`, `1200x628`, `1080x1350`, `qwen-image`, `design`, `render`

### terras-banner-design

Banners para redes sociais, anúncios, heros de site e impressão, com 22 estilos de direção de arte e tamanhos por plataforma. Use para criativo de anúncio, header ou peça para print. Não é para as capas de LinkedIn/Substack da casa (terras-banner).

`/plugin install terras-banner-design@terras`

Palavras-chave: `banner`, `banners`, `anúncio`, `ads`, `social media`, `capa`, `header`, `criativo`, `print`

### terras-excalidraw

Use quando o pedido for um desenho Excalidraw, diagrama editável, esboço à mão, quadro branco, wireframe rascunho, ou imagem de diagrama (PNG/SVG) para post, slide ou documento que a pessoa queira poder editar depois. Também para converter Mermaid em Excalidraw ou reexportar um .excalidraw editado.

`/plugin install terras-excalidraw@terras`

Palavras-chave: `excalidraw`, `diagrama editavel`, `esboco`, `quadro branco`, `whiteboard`, `wireframe`, `fluxograma`, `png`, `svg`, `mermaid`

### terras-ffmpeg

Edita vídeo e áudio com FFmpeg local por pedido em linguagem natural: cortar, juntar, 9:16, legendas, loudness, música com ducking, exportar por plataforma. Use para mp4/mov/wav, corte, legenda, reel, transcodificação ou 'deixa vertical'. Sem nuvem e sem chave de API.

`/plugin install terras-ffmpeg@terras`

Palavras-chave: `ffmpeg`, `video`, `audio`, `edicao`, `cortar`, `legenda`, `reels`, `tiktok`, `youtube`, `transcodificar`, `loudness`, `captions`

### terras-frontend-slides

Apresentação HTML com animação, sem dependências, em arquivo único 16:9, do zero ou convertendo PPT/PPTX. Use para slides, palestra, pitch ou converter PowerPoint para web. Para deck persuasivo com gráficos Chart.js, use terras-slides.

`/plugin install terras-frontend-slides@terras`

Palavras-chave: `slides`, `apresentacao`, `palestra`, `pitch`, `html`, `pptx`, `deck`, `animacao`, `apresentacao web`

### terras-slides

Deck HTML estratégico e persuasivo com Chart.js: estratégia por contexto, layouts, fórmulas de copy e design tokens. Use para pitch deck ou apresentação de negócio em HTML (não PPTX). Para slides com animação ou converter PPT, use terras-frontend-slides.

`/plugin install terras-slides@terras`

Palavras-chave: `slides`, `apresentação`, `pitch deck`, `html`, `chart.js`, `copywriting`, `storytelling`, `deck`

### terras-transcription

Transcreve áudio localmente e sem API (reunião, export do Otter/Zoom/Meet/Teams, nota de voz, entrevista, aula), separa quem falou e marca trecho duvidoso. Use para transcrever, ata, 'o que foi dito', ou quando chegar um .mp3/.m4a/.wav/.ogg.

`/plugin install terras-transcription@terras`

Palavras-chave: `transcricao`, `transcrição`, `transcrever`, `audio`, `mp3`, `m4a`, `wav`, `ogg`, `reuniao`, `reunião`, `ata`, `resumo`, `resumo de reuniao`, `otter`, `zoom`, `meet`, `teams`, `nota de voz`, `entrevista`, `aula`, `podcast`, `legenda`, `diarizacao`, `locutor`, `faster-whisper`, `whisper`

### terras-video

Monta vídeo para YouTube e Shorts a partir de roteiro: cartelas na identidade da marca, narração por voz neural e mp4 horizontal (1920x1080) ou vertical (1080x1920). Use para vídeo, Shorts, Reels, TikTok, 'faz um vídeo disso' ou transformar post em vídeo.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `video`, `youtube`, `shorts`, `reels`, `tiktok`, `vertical`, `1080x1920`, `cartela`, `narracao`, `locucao`, `voz`, `tts`, `mp4`, `ffmpeg`, `edge-tts`, `roteiro`, `terrasia`

### terras-visual-explainer

Páginas HTML autocontidas que explicam visualmente sistemas, diffs, planos, dados e conceitos: diagramas, arquitetura, tabelas comparativas, inclusive diagrama animado com MP4. Use para explicar algo visualmente ou quando uma tabela tiver 4+ linhas ou 3+ colunas.

`/plugin install terras-visual-explainer@terras`

Palavras-chave: `diagrama`, `explicacao visual`, `arquitetura`, `html`, `mermaid`, `tabela`, `diff`, `slides`, `visual`, `animacao`, `diagrama animado`

## Pesquisa e radar

*O radar do que está acontecendo: papers, boletins, redes sociais e mercado.*

### terras-deep-research

Pesquisa em profundidade com citações rastreadas: pipeline de fases, registro de evidências e relatório com bibliografia. Use para pesquisa profunda, relatório de pesquisa, comparar X vs Y ou estado da arte. Não use para busca simples de 1 ou 2 consultas.

`/plugin install terras-deep-research@terras`

Palavras-chave: `deep research`, `pesquisa profunda`, `relatorio`, `citacoes`, `pesquisa`, `analise`, `tendencias`, `triangulacao`, `estado da arte`

### terras-last30days

Pesquisa o que se falou de um tema nos últimos 30 dias em Reddit, X, YouTube, Hacker News, GitHub e web. Use para descobrir pauta, medir se um assunto circula ou comparar temas antes de um post. Descoberta, não fonte: confirme na fonte primária.

`/plugin install terras-last30days@terras` · v3.25.0

Palavras-chave: `last30days`, `pesquisa de pauta`, `trending`, `reddit`, `hacker news`, `youtube`, `x`, `sentimento`, `descoberta`, `tópicos recentes`

### terras-noticias

Lê boletins e roundups de notícias de IA e tecnologia, tria por criticidade e prioridade, resume os itens e escreve o rascunho do digest para o LinkedIn. Use para link de boletim semanal, 'resumo das notícias', 'o que saiu essa semana' ou triagem de notícias.

`/plugin install terras-noticias@terras`

Palavras-chave: `notícias`, `noticias`, `news`, `boletim`, `roundup`, `digest`, `ratos de ia`, `ratos`, `triagem`, `prioridade`, `criticidade`, `resumo semanal`, `news digest`, `weekly recap`

### terras-paper-diario

Analisa papers (arXiv e afins) que afetam quem desenvolve: resumo honesto com números, o que não significa, e aplicação e aviso para júnior, pleno e sênior. Use para link de paper, 'analisar paper', 'paper do dia' ou a verificação diária do arXiv.

`/plugin install terras-paper-diario@terras`

Palavras-chave: `paper`, `arxiv`, `estudo`, `pesquisa`, `paper do dia`, `paper-diario`, `agentes de ia`, `code review`, `carreira dev`, `análise de paper`, `digest diário`

### terras-user-research

Pesquisa com usuários de ponta a ponta: plano, roteiro de entrevista, triagem, síntese em achados, personas e oportunidades, e survey quantitativo. Use para pesquisa com usuários, entrevistas, survey ou análise de transcrições. User research.

`/plugin install terras-user-research@terras`

Palavras-chave: `user research`, `pesquisa com usuarios`, `entrevista`, `roteiro`, `survey`, `sintese`, `personas`, `descoberta`, `qualitativa`, `quantitativa`

### terrasia-pauta-youtube

Pesquisa de demanda no YouTube antes do roteiro: compara temas pela mediana de views, acha outliers por canal e colhe frases recorrentes dos títulos que performam. Use para escolher tema de vídeo, medir demanda de título ou antes da terras-video.

`/plugin install terrasia-pauta-youtube@terras`

Palavras-chave: `youtube`, `pauta`, `tema`, `envelope`, `demanda`, `views`, `outlier`, `titulo`, `capa`, `thumbnail`, `pesquisa`, `roteiro`, `terrasia`

## IA, prompts e agentes

*Prompts, skills, evals e o comportamento do agente.*

### terras-decisor

Use para tomar decisões estruturadas a partir de um contexto, retornando exclusivamente um YAML válido. Ideal para integração como motor de decisão em pipelines, sem chat ou texto extra. Use apenas quando o output precisa ser um YAML estruturado.

`/plugin install terras-decisor@terras`

### terras-eval-harness

Desenvolvimento guiado por eval para agentes e prompts: evals de capacidade e regressão antes de codar e confiabilidade com pass@k e pass^k. Use ao definir critério de passa/falha, montar suíte de regressão de prompt ou comparar versões de modelo.

`/plugin install terras-eval-harness@terras`

Palavras-chave: `eval`, `evals`, `eval harness`, `pass@k`, `regressao de prompt`, `prompt regression`, `llm judge`, `benchmark de modelo`

### terras-full-output-enforcement

Força saída completa: proíbe truncamento, placeholders e 'resto igual', e trata corte por limite de token. Use quando o modelo entregar trabalho pela metade ou código cortado, ou quando o pedido exigir arquivo inteiro. Full output, no placeholders.

`/plugin install terras-full-output-enforcement@terras`

Palavras-chave: `output completo`, `truncamento`, `placeholder`, `código completo`, `sem omissões`

### terras-prompt

Use ao criar, revisar, avaliar ou ajustar um PROMPT (texto para IA), não para executar a tarefa descrita. Preserve a intenção original, otimize pela necessidade (não pelo tamanho) e nunca recrie de memória prompt canônico do Prompt Garden (docs/referencia-verbatim).

`/plugin install terras-prompt@terras`

Palavras-chave: `prompt`, `otimizar prompt`, `reescrever prompt`, `avaliar prompt`, `prompt garden`

### terras-seed

Cria, revisa e ajusta PROMPTS para outra IA (ChatGPT, Claude, Gemini), sem executar a tarefa que o prompt descreve; também atende por 'Lyra'. Use quando o pedido for sobre o texto-instrução: prompt pronto a partir de ideia vaga, revisão ou conserto de prompt.

`/plugin install terras-seed@terras`

Palavras-chave: `prompt`, `otimizar prompt`, `revisar prompt`, `avaliar prompt`, `ajustar prompt`, `prompt pra IA`, `monta um prompt`, `esse prompt tá bom`, `Lyra`

### terras-skill-factory

Cria, revisa e mantém skills no padrão da casa terras-: frontmatter, descrição que dispara, progressive disclosure, checagem de colisão com skill parecida e teste de aderência. Use para criar skill nova, transformar prompt recorrente em skill ou auditar uma skill.

`/plugin install terras-skill-factory@terras`

Palavras-chave: `skill`, `skills`, `criar skill`, `skill factory`, `padrão terras`, `SKILL.md`, `frontmatter`, `progressive disclosure`, `agent skills`

## Fora do marketplace: projeto de cliente

*Skills ligadas a trabalho de cliente, fora do marketplace por decisão (motivo em `marketplace-fora.json`).*

### terras-analise-de-inadimplentes

Analisa a carteira de contas a receber vencida por faixa de atraso (aging), concentração e reincidência, e devolve a lista priorizada de quem cobrar primeiro e o que é assunto de política de crédito.

Fora do marketplace: ligada ao projeto financeiro de cliente; fora do marketplace por decisão do dono (2026-09-30) · v1.0.0

Palavras-chave: `inadimplentes`, `aging`, `carteira vencida`, `contas a receber`, `analise de inadimplencia`, `faixa de atraso`, `titulos vencidos`

### terras-boleto-sankhya

Planeja emissão, envio, acompanhamento e cancelamento de boleto de cliente pelo ERP Sankhya (Boleto Rápido por API), com checagem antes de emitir e o que depende de aprovação.

Fora do marketplace: ligada ao projeto financeiro de cliente; fora do marketplace por decisão do dono (2026-09-30) · v1.0.0

Palavras-chave: `sankhya`, `sankia`, `sankya`, `boleto rapido`, `emitir boleto`, `gerar boleto`, `segunda via do boleto`, `cancelar boleto`, `link do boleto`

### terras-cobranca-hubspot

Desenha a régua de cobrança dentro do HubSpot (propriedades, listas, workflows, tarefas e o assistente) sem duplicar o ERP, com o que o CRM guarda e o que só o financeiro decide.

Fora do marketplace: ligada ao projeto financeiro de cliente; fora do marketplace por decisão do dono (2026-09-30) · v1.0.0

Palavras-chave: `hubspot`, `hub spot`, `crm de cobranca`, `workflow de cobranca`, `sequencia de cobranca`

## Processo do motor (terrasia)

*Skills de processo que vivem no repositório do motor; aqui existe só a versão de catálogo (marcada `.nao-instalar`).*

### terras-adr

Registra decisão de reescrever vs reaproveitar quando o caso não está numa lista canônica — ADR leve com contexto, decisão, alternativas, consequências e rastreabilidade.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `registrar um adr`, `escrever um adr`, `architecture decision record`, `registrar decisao de design`, `reescrever ou reaproveitar`, `decisao arquitetural`

### terras-api-sync

Mudança de contrato de API é atualização atômica — servidor, SDK tipada e documentação humana no mesmo commit, com checklist por tipo de mudança.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `mudei a api`, `contrato da api`, `sincronizar sdk`, `atualizar a documentacao da api`

### terras-backreview

Revisão de backlog em sessão guiada — um documento por vez, itens resolvidos saem, adiados vão para a lista certa e decisões pendentes viram pergunta com opções concretas.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `revisar o backlog`, `revisa o backlog`, `backlog review`, `limpar o backlog`

### terras-boundary

Decide onde colocar rota ou feature nova — núcleo/backend (domínio, regras, persistência, autorização) ou superfície (painel admin, app cliente). Área cinzenta vira decisão registrada.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `onde coloco essa rota`, `onde vai essa feature`, `backend ou frontend`, `fronteira de repositorio`

### terras-drift

Audita drift entre documentação viva e código real, por evidência — classifica a fonte, extrai afirmações verificáveis e reporta PASS, FAIL, UNVERIFIABLE ou PLANNED citando arquivo e linha.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `docs desatualizados`, `desatualizados`, `drift`, `spec vs codigo`, `conformidade docs`

### terras-qualidade

Protocolo de qualidade para tarefas não triviais — plano aprovado antes do código, teste que falha antes, gate completo verde no início e no fim, validação prática rodada e revisão cruzada em mudança de alto risco.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `protocolo de qualidade`, `plano antes de codigo`, `teste que falha antes`, `gate verde`, `revisao cruzada`

### terras-reconstrucao

Checklist para reconstruir um sistema legado módulo a módulo — ordem de construção, documentação permanente do sistema antigo e decisão explícita de reescrever vs reaproveitar.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `sistema legado`, `reconstruir o conhecimento`, `ordem de construcao`, `mapear codigo antigo`

### terras-validacao

Toda entrega exige validação prática além dos testes automatizados — um artefato executável que exercita a mudança de ponta a ponta contra o alvo real, rodado de verdade antes do commit.

Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia) · v1.0.0

Palavras-chave: `validar entrega`, `validacao pratica`, `smoke test`, `verificado rodando de verdade`

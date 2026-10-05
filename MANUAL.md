# Manual das skills do terras

> **Arquivo gerado.** Rode `node scripts/manual.mjs` para regravar; não edite à mão.

**123 skills** neste repositório: **112 instaláveis** pelo marketplace, **8 de processo do motor** e **3 ligadas a projeto de cliente**.

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

**Como pedir.** A skill certa casa pelas palavras do seu pedido, então citar o termo forte ajuda mais do que pedir genérico: "revisa esse post do LinkedIn", "erro de fila no Laravel", "monta a matriz GUT disso". Cada skill abaixo lista as palavras-chave que a acionam.

## Índice

- [Conteúdo, marca e publicação](#conteúdo-marca-e-publicação) — 15 skills
- [Pessoas, RH e carreira](#pessoas-rh-e-carreira) — 26 skills
- [Financeiro e fiscal](#financeiro-e-fiscal) — 6 skills
- [Comercial e vendas](#comercial-e-vendas) — 3 skills
- [Gestão, processos e decisão](#gestão-processos-e-decisão) — 4 skills
- [Desenvolvimento de software](#desenvolvimento-de-software) — 19 skills
- [Design e front-end](#design-e-front-end) — 16 skills
- [Mídia e apresentação](#mídia-e-apresentação) — 10 skills
- [Pesquisa e radar](#pesquisa-e-radar) — 6 skills
- [IA, prompts e agentes](#ia-prompts-e-agentes) — 6 skills

## Conteúdo, marca e publicação

*Escrever, revisar e publicar na voz certa: LinkedIn, Substack, ebooks e a marca.*

### terras-brand

Marca: voz e tom, identidade visual, frameworks de mensagem, paleta e tipografia, organização/validação de ativos e auditoria de consistência; sincroniza as diretrizes com os tokens de design. Use quando o pedido for definir voz/tom da marca, escrever ou validar guia de marca, auditar consistência, extrair cores de uma peça ou organizar ativos. Brand voice, messaging framework, brand audit. Não é para gerar o quadro visual do brand kit (terras-brandkit).

`/plugin install terras-brand@terras`

Palavras-chave: `marca`, `brand`, `voz`, `tom de voz`, `identidade visual`, `mensagem`, `auditoria de marca`, `ativos`, `paleta`

### terras-brandkit

Gera a imagem do brand kit de uma marca: quadro de identidade visual com direção de logo, paleta, tipografia, aplicações em mockup e apresentação para cliente. Use quando o pedido for criar/gerar o quadro de marca, brand book visual, logo system, moodboard ou rebranding visual. Não é para ler identidade de imagens existentes (isso é a terras-identidade). Brand kit, brand guidelines, identity deck, logo system.

`/plugin install terras-brandkit@terras`

Palavras-chave: `brand kit`, `identidade visual`, `brand guidelines`, `logo`, `marca`, `rebranding`, `mockup`

### terras-canal-whatsapp

Publica texto e/ou imagem no canal (newsletter) do WhatsApp pela sessão pareada do sidecar, com pré-checagem de papel e confirmação explícita. Use quando o pedido for postar ou mandar algo no canal do WhatsApp, publicar card ou texto no canal, ou conferir se o canal está pronto para postar. Publish to a WhatsApp channel (newsletter JID).

`/plugin install terras-canal-whatsapp@terras`

Palavras-chave: `whatsapp`, `canal`, `channel`, `newsletter`, `publicar`, `publish`, `post`, `card`, `imagem`, `legenda`, `caption`, `baileys`, `sidecar`

### terras-comentarios

Comenta em lote posts do LinkedIn de terceiros: o usuário manda uma lista de posts colados, a skill lê cada texto e devolve um comentário curto de até 100 caracteres, pronto para colar. Use sempre que o pedido tiver 2 ou mais posts para comentar, 'comenta esses posts', 'gera comentário para cada um', 'me dá comentários rápidos pra essa lista', comentar o feed, engajamento em lote. Não use para um post único com 'post a responder' (três arquivos) nem 'queria comentar' sozinho (comentário de ~450 caracteres): esses casos são da skill terras-linkedin.

`/plugin install terras-comentarios@terras`

Palavras-chave: `comentar`, `comentario`, `comentarios`, `lista de posts`, `lote`, `em lote`, `feed`, `engajamento`, `linkedin`, `resposta curta`, `comentar posts`

### terras-ebook

Cria e-book e audiolivro para vender: estrutura, diagramação, EPUB e PDF A5 diagramado como livro, capa, ISBN, escolha de plataforma, royalties, preço e lançamento — e transforma acervo de YouTube em e-book. Use quando o pedido envolver e-book, ebook, livro digital, EPUB, PDF de livro, Kindle, Amazon KDP, Kobo, Apple Books, Gumroad, Payhip, Draft2Digital, IngramSpark, ISBN, capa de livro, diagramação, sumário clicável, folio, glossário, nota de rodapé, lead magnet, playbook, apostila, material didático, audiolivro de e-book, precificação de produto digital, estratégia de lançamento, ou 'transformar meus vídeos em livro'. Publish, sell, self-publish, ebook, glossary, royalty.

`/plugin install terras-ebook@terras`

Palavras-chave: `ebook`, `e-book`, `epub`, `pdf`, `livro`, `kdp`, `kindle`, `amazon`, `gumroad`, `payhip`, `kobo`, `apple-books`, `draft2digital`, `isbn`, `capa`, `diagramacao`, `sumario`, `folio`, `royalties`, `preco`, `lancamento`, `lead-magnet`, `playbook`, `apostila`, `audiolivro`, `youtube`, `transcricao`, `self-publishing`, `glossario`, `nota-de-rodape`

### terras-historias-infantis

Cria histórias infantis ilustradas em quadrinhos e o LIVRO DE COLORIR da mesma história e das mesmas imagens — recebe um tema ou a história pronta, escreve o roteiro página a página (capa, cenas com balões, versículo se houver, aplicação), gera as imagens como arte vetorial infantil e deriva a versão para colorir. Serve para qualquer história infantil (cristã, escolar, cotidiana); use SEMPRE que o usuário mencionar quadrinhos, gibi, HQ, historinha, história ilustrada, livro de colorir, colorir, desenho para pintar, personagens e capa de história, Escola Dominical, história bíblica para crianças — mesmo sem a palavra "quadrinhos".

`/plugin install terras-historias-infantis@terras`

### terras-humanizer

Reescreve texto com cara de IA para soar humano, sem mudar o que ele diz e sem inventar nada. Use para revisar ou editar prosa com marcas de IA em português ou inglês: contraste 'não é X, é Y', frase de efeito de uma linha, abertura encenada, trio forçado, travessão em excesso, hipérbole, linguagem de venda, jargão de IA, negrito decorativo, gerúndio pendurado; e para resposta que re-explica o que o leitor já sabe antes de chegar à decisão. Humanize text, remove AI writing tells, edit AI-sounding prose.

`/plugin install terras-humanizer@terras`

Palavras-chave: `humanizar`, `humanizer`, `texto de IA`, `AI writing`, `marcas de IA`, `revisão`, `edição`, `prosa`, `resposta`, `reply`, `português`, `inglês`

### terras-humanizer-dev

Reescreve ou revisa texto para soar natural e humano, preservando a voz, as opiniões e o ritmo do autor, sem deixar o texto errado ou informal demais. Use quando pedirem para humanizar texto, revisar prosa com cara de IA, tirar o tom de chatbot, deixar um texto mais natural e autor, ou analisar se um trecho parece escrito por IA, mesmo que a palavra "humanizar" não apareça.

`/plugin install terras-humanizer-dev@terras`

### terras-identidade

Le a identidade visual de uma marca a partir de imagens (pecas de anuncio, prints, manual, papelaria, site) e entrega ela pronta para reusar: cores com papel medido, tipografia, marca recortada em PNG, linguagem visual e tokens de CSS/JSON/Tailwind para site, sistema, documento e peca de marketing. Use quando o pedido envolver identidade visual, marca, manual de marca, paleta, 'quais sao as cores', 'pega essas imagens e faz a identidade', tipografia de uma peca, 'deixa no visual da marca', 'aplica a identidade no site/documento', logo/ativo de marca, ou quando chegarem fotos de material de cliente por WhatsApp e for preciso extrair o visual dele. Cobre extracao, medicao de cor, recorte de logo e equivalencia de fonte livre.

`/plugin install terras-identidade@terras`

Palavras-chave: `identidade`, `identidade visual`, `marca`, `branding`, `brand`, `paleta`, `cores`, `tipografia`, `fonte`, `logo`, `ativo`, `manual de marca`, `design system`, `tokens`, `css`, `tailwind`, `extracao`, `whatsapp`, `peca`, `anuncio`, `cliente`

### terras-linkedin

Ajuda a escrever posts para LinkedIn. Use quando o usuário pedir para escrever, redigir, revisar ou melhorar um post/texto para LinkedIn, e também quando perguntar sobre alcance, impressões, views ou por que um post rendeu pouco. Use também quando ele colar o post de outra pessoa para responder ou comentar (post a responder, queria comentar, resposta curta ao post dele), mesmo que ele não use a palavra post. Cobre estrutura, hook, tom, CTA, hashtags, distribuição fora da rede, boas práticas da plataforma, resposta a post de terceiro e a regra de zero travessão (em dash), marcador de texto gerado por IA.

`/plugin install terras-linkedin@terras`

Palavras-chave: `linkedin`, `post`, `escrever`, `redigir`, `revisar`, `comentar`, `comentário`, `responder post`, `post de terceiro`, `resposta curta`, `hook`, `cta`, `hashtags`, `travessao`, `em dash`, `carrossel`, `alcance`, `impressoes`, `distribuição`, `views`, `fora da rede`

### terras-linkedin-metricas

Extrai, guarda e diagnostica as estatisticas dos posts do LinkedIn do Everton: impressoes, usuarios alcancados, divisao na rede e fora da rede, reacoes, comentarios, compartilhamentos, salvamentos, envios, visualizacoes de perfil, seguidores ganhos e os dados demograficos do publico alcancado. Use quando o pedido for analisar desempenho de post, entender por que um post rendeu ou nao rendeu, medir alcance, ver quem foi alcancado, comparar posts, montar relatorio de metricas do LinkedIn ou decidir o que repetir no proximo post.

`/plugin install terras-linkedin-metricas@terras`

Palavras-chave: `linkedin`, `metricas`, `estatisticas`, `desempenho`, `impressoes`, `alcance`, `alcancados`, `fora da rede`, `engajamento`, `salvamentos`, `comentarios`, `seguidores`, `publico`, `demografia`, `relatorio`, `diagnostico`, `post rendeu`, `analytics`

### terras-pauta-mercado

Transforma referência externa (repo, post, anúncio, paper) na análise mercado × TerrasIA com cobre/rejeita/falta e recibo, e no pacote de posts por canal (Company Page, LinkedIn pessoal, canal WhatsApp e Substack). Use quando mandarem um link para virar análise ou post, perguntarem o que o TerrasIA já cobre de algo, ou pedirem pauta de mercado ou comparação com concorrente. Market-vs-product content pipeline.

`/plugin install terras-pauta-mercado@terras`

Palavras-chave: `pauta`, `mercado`, `análise de mercado`, `comparação`, `concorrente`, `referência`, `cobertura`, `cobre`, `rejeita`, `falta`, `recibo`, `post`, `linkedin`, `whatsapp`, `substack`

### terras-seo

Auditar, planejar e implementar SEO: SEO técnico, otimização on-page, dados estruturados (schema.org), Core Web Vitals e estratégia de conteúdo. Use quando o pedido for melhorar visibilidade em busca, corrigir SEO, schema markup, sitemap, robots.txt ou mapa de palavras-chave. SEO audit.

`/plugin install terras-seo@terras`

Palavras-chave: `seo`, `schema markup`, `dados estruturados`, `sitemap`, `robots.txt`, `core web vitals`, `palavras-chave`, `otimizacao para buscadores`

### terras-substack

Publica, agenda e gerencia posts na Substack (newsletter) usando a API interna do editor. Use quando o pedido envolver Substack, publicar post, subir newsletter, criar rascunho, publicar nota/Note, agendar publicacao, despublicar, enviar imagem para o Substack, ou conferir rascunhos existentes. Publish post, draft, newsletter, schedule, unpublish on Substack. Sem APIs pagas e sem instalar nada: apenas requests do Python do sistema.

`/plugin install terras-substack@terras`

Palavras-chave: `substack`, `publicar`, `publish`, `newsletter`, `rascunho`, `draft`, `note`, `nota`, `agendar`, `schedule`, `unpublish`, `prosemirror`, `eolimabr`

### terrasia-post-empresa

Produz a peça da Company Page do TerrasIA: o post na voz de produto e a imagem na identidade da marca, com aceite de leitura no celular. Traz a régua de texto da página (banda de 1.300 a 1.500, gancho no corte de ~210, link no primeiro comentário, humanizer aplicado), os templates das duas peças (banner 1200x628 e card 1080x1350), o script de render e medição de vãos, os tamanhos mínimos aprendidos em px e o checklist de publicação. Use quando o pedido for post da empresa, LinkedIn da empresa, Company Page, peça ou imagem de marca, ou fechar a publicação de uma análise. A análise de referência e o pacote por canal são da skill irmã terras-pauta-mercado.

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

Escreve e revisa cartas de apresentação (cover letters) para vagas internacionais e remotas. Use quando o usuário pedir carta de apresentação, cover letter, mensagem de candidatura para empresa de fora, InMail para recrutador, texto para vaga na gringa, ou revisar uma carta existente. Cobre tamanho, estrutura, personalização, tradução de experiência brasileira para valor global e remote readiness.

`/plugin install terras-cover-letter@terras`

Palavras-chave: `cover letter`, `carta de apresentação`, `candidatura`, `vaga internacional`, `gringa`, `remoto`, `remote`, `inmail`, `recrutador`, `job application`

### terras-dashboard-de-utilizacao-de-beneficios

Analisa adesão, utilização, custo e satisfação dos benefícios por tipo de saldo, período e público permitido.

`/plugin install terras-dashboard-de-utilizacao-de-beneficios@terras` · v1.0.0

Palavras-chave: `utilização de benefícios`, `dashboard de benefícios`, `adesão ao benefício`, `va e vr`, `va vr`, `mobilidade`, `custo de benefícios`, `satisfação com benefícios`

### terras-educacao-corporativa

Aplica 26 prompts de educação corporativa (derivados do ebook da Alun Business) para gerar estratégia de T&D, diagnóstico de necessidades, mapa de competências, trilhas, programas, planos de aula e indicadores de impacto. Use quando o pedido envolver educação corporativa, treinamento corporativo, T&D, L&D, trilha de aprendizagem, mapa de competências, ROI de treinamento, workshop ou plano de aula corporativo. Corporate education, learning and development, training design.

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

Filtra as vagas do board da comunidade COD3RS (app.coders.com.br/comunidade#vagas) contra o currículo do usuário e devolve só o que faz sentido real: balde A (recomendar), B (talvez) e C (descarte com motivo) — e, com aprovação por vaga, avança para a aplicação no site de cada uma (carta, formulário, portões de upload/login). Use quando o pedido envolver vagas da COD3RS, vagas do coders, 'o que tem de vaga pra mim', triagem de vagas no currículo, vagas que combinam comigo, board de vagas, candidatura nas vagas, 'aplica pra mim', aplicar nas vagas aprovadas, ou agendar essa triagem. Job board triage against resume, COD3RS community jobs, assisted job applications.

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

Faz análise SWOT rastreável e terminada em ação: cada item cita a fonte (dado, documento, métrica), o que não tem fonte vira hipótese marcada com o teste que a confirmaria, os quadrantes são priorizados e a análise fecha em cruzamentos TOWS (SO, WO, ST, WT) com ação, dono e verificação. Use quando o pedido for SWOT, análise de cenário, posição competitiva, preparo de decisão estratégica ou 'forças, fraquezas, oportunidades e ameaças'.

`/plugin install terras-analise-swot@terras` · v1.0.0

Palavras-chave: `swot`, `analise swot`, `forcas`, `fraquezas`, `oportunidades`, `ameacas`, `tows`, `matriz swot`, `analise de cenario`, `posicao competitiva`, `planejamento estrategico`, `analise estrategica`, `decisao estrategica`, `cenario competitivo`

### terras-mapeamento-de-processos

Mapeia um processo a partir de áudio, gravação de tela, transcrição ou relato falado e devolve o mapa visual (AS-IS e TO-BE), o diagnóstico com números e o plano de melhoria priorizado com as oportunidades de automação. Use quando o pedido for mapear ou desenhar um processo, analisar o áudio ou a gravação de tela de uma rotina, achar o gargalo, reduzir tempo de atendimento, automatizar uma rotina operacional, fazer diagnóstico de processo, montar o fluxo AS-IS/TO-BE ou dimensionar quantas pessoas o processo consome. Cobre também 'é assim que a gente faz hoje, o que dá para melhorar'.

`/plugin install terras-mapeamento-de-processos@terras` · v1.4.0

Palavras-chave: `mapeamento de processo`, `mapear processo`, `processo`, `fluxograma`, `bpmn`, `as is`, `to be`, `gargalo`, `diagnostico de processo`, `melhoria de processo`, `automacao de processo`, `lean`, `desperdicio`, `lead time`, `sop`, `procedimento operacional`, `retrabalho`, `sla`

### terras-matriz-gut

Prioriza problemas e demandas concorrentes com a matriz GUT: notas 1-5 ancoradas em Gravidade, Urgência e Tendência, score por produto, faixa de decisão declarada antes de pontuar, desempate fixo e plano de ataque com dono e prazo. Use quando o pedido for priorizar, ordenar uma fila, decidir por onde começar, comparar problemas ou demandas de naturezas diferentes, ou quando 'tudo é urgente' e falta critério comum. Cobre também 'qual eu resolvo primeiro'.

`/plugin install terras-matriz-gut@terras` · v1.0.0

Palavras-chave: `gut`, `matriz gut`, `priorizacao`, `priorizar`, `gravidade`, `urgencia`, `tendencia`, `prioridade`, `criticidade`, `ordenar problemas`, `fila de demandas`, `por onde comecar`, `escala de prioridade`, `desempate`, `backlog priorizado`

### terras-pipeline-de-automacao

Projeta e monta pipelines de automação em que scripts determinísticos executam o trabalho e o agente decide só em pontos de revisão fechados. Pipes and Filters com rastro de hashes (etapa se recusa a rodar sobre dado velho), recibos de execução (sucesso, falha sem deixar metade, já-estava-feito) e manuais em vez de leitura de código. Use quando pedirem automatizar de ponta a ponta um processo repetitivo (áudio, vídeo, documentos, relatórios, lotes de arquivos), projetar um pipeline com agente de código, ou consertar um pipeline que refaz trabalho, deixa artefato pela metade, perde a trilha de versão ou põe o modelo decidindo o que devia ser medido. Production pipeline, pipes and filters, provenance, receipts, idempotency, agentic workflow.

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

### terras-database-migrations

Migrations de banco seguras e reversíveis: mudanças só para frente em produção, expand-contract para renomear sem downtime, índices concorrentes, backfill em lotes, e fluxo por ferramenta (PostgreSQL, Prisma, Drizzle, Kysely, Django, golang-migrate). Use ao escrever migration de schema ou de dados, adicionar coluna ou índice em tabela grande ou planejar rollback. Database migrations.

`/plugin install terras-database-migrations@terras`

Palavras-chave: `migration`, `migracao`, `migracoes`, `expand-contract`, `zero downtime`, `backfill`, `rollback`, `alter table`, `create index concurrently`

### terras-e2e-testing

Testes end-to-end com Playwright: Page Object Model, configuração, integração com CI, artefatos (trace, vídeo, screenshot) e estratégia para teste instável. Use ao escrever teste Playwright, estruturar page objects ou consertar e2e flaky no CI. Playwright E2E testing.

`/plugin install terras-e2e-testing@terras`

Palavras-chave: `playwright`, `e2e`, `end-to-end`, `page object`, `teste flaky`, `flaky test`, `teste de ponta a ponta`

### terras-governanca-padroes

Audita onde as convenções de um projeto vivem (CLAUDE.md, AGENTS.md, lint, CI, docs, cabeça do time) e transforma padrão em governance rule: arquivo Markdown versionado, com dono, data de revisão, "quando NÃO usar" e ciclo de deprecação — legível e acionável por agente de IA. Use quando pedirem para avaliar/auditar padrões ou convenções de um repositório, padronizar um projeto, criar ou versionar regras do time, ou quando as regras vivem só em wiki/Notion/conversa. EN: governance rules, conventions as skills, standards audit, AGENTS.md.

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

Cria um miniapp do zero — recebe o assunto, entrevista as lacunas, decide arquitetura e LGPD, escolhe e dosa a paleta, escreve a copy (promessa, objeções, crenças limitantes), constrói o app local-first, verifica e publica na Vercel (preview e depois produção). Usa identidade visual já estabelecida no repositório quando existir, e o Google Stitch quando estiver acessível. Use sempre que o pedido for criar/gerar/fazer um app ou miniapp novo, um PWA, um app de bolso, um instrumento para um público, 'transforma esse conteúdo em app', 'quero um app pra isso', ou quando alguém entregar um assunto e esperar um app funcionando no ar. Trigger on: miniapp, mini-app, criar app, novo app, gerar aplicativo, app de bolso, PWA, publicar na vercel.

`/plugin install terras-miniapp-builder@terras`

Palavras-chave: `miniapp`, `mini-app`, `criar app`, `novo app`, `gerar app`, `aplicativo`, `pwa`, `app de bolso`, `publicar app`, `vercel`, `google stitch`, `lgpd`, `psicologia das cores`, `paleta`, `copy`, `objecao`, `crenca limitante`, `pitch`, `local-first`

### terras-php

Write solid PHP avoiding type juggling traps, array quirks, and common security pitfalls.

`/plugin install terras-php@terras` · v1.0.1

Palavras-chave: `php`, `composer`

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

### terras-revisao-de-codigo

Revisa uma mudança de código pelo risco que ela cria, com foco em integração que movimenta dinheiro ou dado de cliente: correção, idempotência, falha parcial, segredo, dado pessoal e teste que prova.

`/plugin install terras-revisao-de-codigo@terras` · v1.0.0

Palavras-chave: `revisao de codigo`, `revisar o codigo`, `revise o codigo`, `revisa o codigo`, `code review`, `pull request`

### terras-security-review

Checklist e padrões de segurança para código: autenticação, entrada do usuário, segredos, endpoints de API, pagamento e dados sensíveis, com anexo de segurança de infraestrutura em nuvem. Use ao mexer em login, input, segredo, rota nova ou fluxo sensível. Security review checklist.

`/plugin install terras-security-review@terras`

Palavras-chave: `security review`, `revisao de seguranca`, `autenticacao`, `authentication`, `xss`, `sql injection`, `csrf`, `owasp`, `secrets`, `segredos`

### terras-standards

Aplica os Padrões Agnósticos de Engenharia e Produto v4.0 (arquitetura, segurança, privacidade e IA) com lastro em evidência real de cliente quando disponível. Use sempre que o usuário mencionar "padrões de engenharia", "v4.0", "Bloco G", "gate de produção", "AIP/RIPD/ROPA", "ISO 27001", "conformidade", "evidência de auditoria", ou pedir para avaliar conformidade, classificar perfil, criar um ADR, responder o questionário de adoção, ou buscar evidência real de um cliente.

`/plugin install terras-standards@terras`

### terras-tech-debt

Auditoria de dívida técnica e arquitetura de um repositório, com achados citando arquivo:linha, severidade, esforço e a seção obrigatória 'parece ruim mas está certo'. Use quando o pedido for auditoria de dívida técnica, diagnóstico de codebase, revisão de arquitetura, health check de repositório ou avaliação de qualidade de código de um repo inteiro. Tech debt audit, codebase health check, architecture review, legacy assessment.

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

Skill guarda-chuva de design: identidade de marca, tokens, UI, geração de logo com IA, programa de identidade corporativa (CIP, 50 entregáveis), apresentações HTML, banners, fotos para redes e ícones; roteia para as irmãs terras-brand, terras-design-system e terras-ui-styling e usa a terras-ui-ux-pro-max para estilo e paleta. Use quando o pedido for um pacote de design amplo, logo, identidade corporativa/papelaria ou quando não estiver claro qual peça de design se quer. Não é para capa do LinkedIn/Substack (terras-banner) nem leitura de identidade a partir de imagens (terras-identidade). Unified design skill, logo design, corporate identity program.

`/plugin install terras-design@terras`

Palavras-chave: `design`, `logo`, `identidade corporativa`, `cip`, `papelaria`, `mockup`, `apresentação`, `banner`, `social media`, `ícones`, `roteamento`

### terras-design-system

Arquitetura de design tokens em três camadas (primitivo, semântico, componente), especificações de componentes e estados, variáveis CSS, escalas de espaçamento/tipografia, integração com Tailwind e busca de slides (estratégia, layout, copy) por BM25. Use quando o pedido for criar ou validar tokens, definir estados de componente, montar tema Tailwind ou preparar specs para handoff. Design tokens, token architecture, component specs, CSS variables.

`/plugin install terras-design-system@terras`

Palavras-chave: `design tokens`, `tokens`, `css variables`, `tailwind`, `componentes`, `specs`, `escalas`, `handoff`

### terras-design-taste-frontend

Anti-slop de frontend para landing pages, portfólios e redesigns: lê o briefing, infere a direção de design e entrega interface que não parece template, com design system real quando couber e auditoria primeiro em redesign. Use quando o pedido for criar ou redesenhar página web com qualidade de design. Anti-slop, landing page, portfolio, frontend design.

`/plugin install terras-design-taste-frontend@terras`

Palavras-chave: `anti-slop`, `landing page`, `portfólio`, `design`, `frontend`, `redesenho`

### terras-design-taste-frontend-v1

Versão 1 legada do design-taste-frontend (a v2 é a padrão da casa). Preservada para projetos que dependem do comportamento exato da v1. Use apenas quando a v2 quebrar algo específico do fluxo. Legacy v1, compatibilidade.

`/plugin install terras-design-taste-frontend-v1@terras`

Palavras-chave: `v1`, `legado`, `compatibilidade`, `frontend design`

### terras-gpt-taste

Variante estrita do design-taste para GPT/Codex: variância de layout com randomização real, estrutura AIDA, bento sem buracos, GSAP (pinning, stacking, scrubbing) e anti-slop agressivo. Use quando o alvo for GPT/Codex e o pedido for landing page de nível Awwwards com motion avançado. Awwwards, landing page, GSAP, bento grid.

`/plugin install terras-gpt-taste@terras`

Palavras-chave: `gpt`, `codex`, `awwwards`, `landing page`, `gsap`, `bento`, `motion`, `anti-slop`

### terras-high-end-visual-design

Design visual de alto padrão: define fontes, espaçamento, sombras, cartões e animações que fazem o site parecer caro, e bloqueia os padrões que deixam design de IA com cara de barato. Use quando o pedido for algo sofisticado, com cara de agência, Apple-like/Linear-tier, premium ou de alto valor. High-end, premium design, agency-level.

`/plugin install terras-high-end-visual-design@terras`

Palavras-chave: `premium`, `alto padrão`, `sofisticado`, `agência`, `animação`, `tipografia`

### terras-image-to-code

Pipeline imagem-primeiro para site: gera a própria imagem de referência, analisa em detalhe e implementa o frontend fiel a ela, seção a seção, evitando sub-geração e excesso de cartões aninhados. Use quando o pedido for transformar design/mockup em código ou reproduzir uma página com alta fidelidade. Image to code, design to code, screenshot to code.

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

Interface brutalista industrial: grade suíça rígida, tipografia mecânica com contraste extremo, paleta utilitária e degradação analógica (halftone, scanline, dither). Use quando o pedido for UI crua e industrial, painel técnico denso, dashboard de telemetria, portfólio ou editorial com cara de blueprint/terminal militar. Industrial brutalism, Swiss typography, tactical UI.

`/plugin install terras-industrial-brutalist-ui@terras`

Palavras-chave: `brutalista`, `industrial`, `swiss`, `tipografia`, `dashboard`, `terminal`, `blueprint`, `UI`

### terras-minimalist-ui

UI minimalista editorial: paleta monocromática quente, hierarquia tipográfica, bento grid flat e pastéis discretos; sem gradientes nem sombras pesadas. Use quando pedirem interface minimalista, limpa, estilo Notion/Linear ou document-style. Minimalist UI, editorial, clean interface.

`/plugin install terras-minimalist-ui@terras`

Palavras-chave: `minimalista`, `minimal`, `editorial`, `notion`, `linear`, `bento`, `clean`

### terras-redesign-existing-projects

Redesign de projeto existente: audita a UI atual, identifica padrões genéricos de IA e aplica padrão premium sem quebrar funcionalidade, em qualquer framework CSS ou CSS puro. Use quando o pedido for melhorar, repaginar, modernizar ou deixar bonito um site/app que já existe. Redesign, audit-first, upgrade UI.

`/plugin install terras-redesign-existing-projects@terras`

Palavras-chave: `redesign`, `auditar UI`, `melhorar design`, `repaginar`, `upgrade visual`

### terras-stitch-design-taste

Design system semântico para Google Stitch: gera DESIGN.md que impõe padrão premium anti-genérico (tipografia estrita, cor calibrada, layout assimétrico, micro-motion perpétuo, performance acelerada). Use quando o alvo for o Stitch ou quando o projeto precisar de um DESIGN.md como contrato de design. Stitch, design system, DESIGN.md.

`/plugin install terras-stitch-design-taste@terras`

Palavras-chave: `stitch`, `design system`, `DESIGN.md`, `micro-motion`, `tipografia`

### terras-ui-styling

Implementação de interface com shadcn/ui e Tailwind CSS: adicionar componentes, theming, acessibilidade, utilitários e responsividade, customização de tema e design visual em canvas. Use quando o pedido for implementar UI em código com shadcn/Tailwind, configurar tema, componentes acessíveis ou desenhar em canvas. shadcn/ui, Tailwind CSS, canvas, acessibilidade.

`/plugin install terras-ui-styling@terras`

Palavras-chave: `shadcn`, `shadcn/ui`, `tailwind`, `componentes`, `theming`, `tema`, `acessibilidade`, `canvas`, `responsivo`, `ui`

### terras-ui-ux-pro-max

Base de consulta local de UI/UX com motor de busca próprio (BM25 + regex): 79 estilos, 192 paletas por tipo de produto, 74 pares tipográficos, 119 diretrizes de UX, 105 ícones, 25 tipos de gráfico, presets de GSAP e guias de 22 stacks; gera o design system do produto (padrão de página, estilo, cores, tipografia, efeitos) e persiste em MASTER.md com overrides por página. Use quando o pedido for definir direção visual, escolher estilo/paleta/tipografia, gerar design system, checar regra de UX/acessibilidade ou buscar orientação de stack (React, Next, Vue, Tailwind, SwiftUI, Flutter...). UI/UX design intelligence, design system generator, style and palette search.

`/plugin install terras-ui-ux-pro-max@terras`

Palavras-chave: `ui`, `ux`, `design system`, `estilos`, `paletas`, `tipografia`, `cores`, `diretrizes de ux`, `acessibilidade`, `gráficos`, `stacks`, `gsap`

## Mídia e apresentação

*Áudio, vídeo, banner, slides e diagramas.*

### terras-audio

Voz, pronúncia e cadeia de áudio para narração: vídeo, audiolivro comum e técnico, nota de voz, capítulo. Use quando o pedido envolver narração, locução, voz, TTS, áudio, audiolivro, audiobook, m4b, capítulo narrado, pronúncia de termo em inglês, sotaque, loudness, normalização, ou quando alguém reclamar que uma palavra soa errada ou que o áudio ficou baixo.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `audio`, `voz`, `narracao`, `locucao`, `tts`, `edge-tts`, `audiolivro`, `audiobook`, `m4b`, `capitulo`, `pronuncia`, `sotaque`, `respelling`, `loudness`, `lufs`, `normalizacao`, `mp3`

### terras-banner

Cria a imagem que acompanha um post, newsletter ou nota: banner 1200x628 para LinkedIn e og:image da Substack, card em pé 1080x1350, capa. Use quando o pedido envolver imagem, banner, capa, thumbnail, card, 'post com imagem', 'faz a imagem disso', og:image, ou quando ele disser que o visual ficou padrão ou simples. Gera a arte por modelo (qwen-image na chave que ele já tem), monta a tipografia em HTML com a fonte da marca e renderiza em PNG no tamanho exato, com conferência de encaixe e gate visual antes de entregar.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `banner`, `imagem`, `capa`, `thumbnail`, `card`, `og:image`, `substack`, `linkedin`, `arte`, `visual`, `png`, `1200x628`, `1080x1350`, `qwen-image`, `design`, `render`

### terras-banner-design

Banners para redes sociais, anúncios, heros de site e impressão: 22 estilos de direção de arte, tamanhos por plataforma, com visuais gerados ou fornecidos. Use quando o pedido for banner de rede social, criativo de anúncio, capa, header ou peça para print. Não é para as capas do LinkedIn/Substack da casa (terras-banner). Social banners, ad creatives, print design.

`/plugin install terras-banner-design@terras`

Palavras-chave: `banner`, `banners`, `anúncio`, `ads`, `social media`, `capa`, `header`, `criativo`, `print`

### terras-excalidraw

Use quando o pedido for um desenho Excalidraw, diagrama editável, esboço à mão, quadro branco, wireframe rascunho, ou imagem de diagrama (PNG/SVG) para post, slide ou documento que a pessoa queira poder editar depois. Também para converter Mermaid em Excalidraw ou reexportar um .excalidraw editado.

`/plugin install terras-excalidraw@terras`

Palavras-chave: `excalidraw`, `diagrama editavel`, `esboco`, `quadro branco`, `whiteboard`, `wireframe`, `fluxograma`, `png`, `svg`, `mermaid`

### terras-ffmpeg

Edita vídeo e áudio com FFmpeg local a partir de pedidos em linguagem natural: cortar, aparar, juntar, redimensionar (9:16, 1:1), acelerar, legendas (SRT/ASS, animadas, karaokê), logos e textos sobrepostos, remoção de silêncio, sincronização multicâmera e de microfone externo, normalização de loudness, HDR/Dolby Vision para SDR, LUTs, música de fundo com ducking, exportação por plataforma (YouTube, Reels, TikTok, X, LinkedIn, podcast), checagem de conformidade, detecção de cenas e cortes de destaque. Use quando o pedido mencionar vídeo ou áudio (mp4, mov, mkv, wav, m4a), corte, legenda, reel, short, ffmpeg, transcodificação, ou pedir algo 'vertical', 'mais alto', 'legendado', '60 segundos'. 42 scripts em Python stdlib, sem nuvem e sem chave de API. Edit video, ffmpeg, captions, transcode.

`/plugin install terras-ffmpeg@terras`

Palavras-chave: `ffmpeg`, `video`, `audio`, `edicao`, `cortar`, `legenda`, `reels`, `tiktok`, `youtube`, `transcodificar`, `loudness`, `captions`

### terras-frontend-slides

Cria apresentações HTML ricas em animação, sem dependência nenhuma, do zero ou convertendo PowerPoint. Use quando o pedido for apresentação, slides, palestra, pitch, ou converter PPT/PPTX para web. Palco 16:9 fixo (1920x1080) em um único arquivo HTML com CSS/JS embutidos, pacotes de estilo prontos (bold-template-pack) e exploração visual em vez de escolhas abstratas. HTML presentation, slides, pitch deck, palestra.

`/plugin install terras-frontend-slides@terras`

Palavras-chave: `slides`, `apresentacao`, `palestra`, `pitch`, `html`, `pptx`, `deck`, `animacao`, `apresentacao web`

### terras-slides

Apresentações HTML estratégicas e persuasivas com Chart.js: estratégias por contexto, padrões de layout, fórmulas de copywriting e design tokens; inclui base de busca própria para estratégia/layout/copy. Use quando o pedido for criar slides, pitch deck ou apresentação em HTML (não PPTX). HTML slides, pitch deck, Chart.js, presentation.

`/plugin install terras-slides@terras`

Palavras-chave: `slides`, `apresentação`, `pitch deck`, `html`, `chart.js`, `copywriting`, `storytelling`, `deck`

### terras-transcription

Transcreve áudio em texto fiel, localmente e sem API: reunião gravada, export do Otter/Zoom/Meet/Teams, nota de voz, entrevista, aula, podcast. Use quando o pedido envolver transcrição, transcrever, 'o que foi dito nessa reunião', ata, resumo de reunião, legenda, ou quando alguém mandar um .mp3/.m4a/.wav/.ogg e pedir o conteúdo em texto. Também cobre conferir transcrição recebida (inclusive quando veio traduzida), separar quem falou, e marcar trechos duvidosos em vez de inventar.

`/plugin install terras-transcription@terras`

Palavras-chave: `transcricao`, `transcrição`, `transcrever`, `audio`, `mp3`, `m4a`, `wav`, `ogg`, `reuniao`, `reunião`, `ata`, `resumo`, `resumo de reuniao`, `otter`, `zoom`, `meet`, `teams`, `nota de voz`, `entrevista`, `aula`, `podcast`, `legenda`, `diarizacao`, `locutor`, `faster-whisper`, `whisper`

### terras-video

Monta vídeo para YouTube e Shorts a partir de um roteiro: cartelas na identidade da marca, narração por voz neural, movimento fluido e mp4 pronto para publicar. Faz vídeo horizontal 1920x1080 e vídeo vertical 1080x1920, com área segura para a interface dos Shorts. Use quando o pedido envolver vídeo, vídeo vertical, YouTube, Shorts, Reels, TikTok, cartela, narração, locução, voz, trilha, mp4, 'faz um vídeo disso', 'faz um short', 'gera conteúdo em vídeo', ou quando o assunto for transformar um post, um digest ou um projeto em vídeo.

Sai no plugin do grupo: `/plugin install terras-midia@terras`

Palavras-chave: `video`, `youtube`, `shorts`, `reels`, `tiktok`, `vertical`, `1080x1920`, `cartela`, `narracao`, `locucao`, `voz`, `tts`, `mp4`, `ffmpeg`, `edge-tts`, `roteiro`, `terrasia`

### terras-visual-explainer

Gera páginas HTML autocontidas que explicam visualmente sistemas, mudanças de código, planos, dados e conceitos técnicos: diagramas (inclusive Mermaid), visões de arquitetura, revisão de diff ou de plano, recapitulações de projeto, tabelas comparativas e decks de slides. Faz também versão ANIMADA de diagrama (fluxo nas arestas, etapas acendendo em sequência, pulso viajando pela rota), com MP4 gravado quadro a quadro, quando pedido. Use quando o pedido for explicar algo visualmente, diagrama, arquitetura, revisão visual de mudança, ou quando uma tabela tiver 4+ linhas ou 3+ colunas. Visual explainer, diagramas, arquitetura, HTML.

`/plugin install terras-visual-explainer@terras`

Palavras-chave: `diagrama`, `explicacao visual`, `arquitetura`, `html`, `mermaid`, `tabela`, `diff`, `slides`, `visual`, `animacao`, `diagrama animado`

## Pesquisa e radar

*O radar do que está acontecendo: papers, boletins, redes sociais e mercado.*

### terras-deep-research

Pesquisa em profundidade com rastreamento de citações: pipeline de 3 a 8 fases (escopo, plano, recuperação, triangulação, síntese, crítica, refinamento e empacotamento), registro persistente de evidências e relatório estruturado com bibliografia completa. Use quando o pedido for pesquisa profunda, análise abrangente, relatório de pesquisa, comparar X vs Y, analisar tendências ou estado da arte. Não use para buscas simples, debug ou perguntas respondíveis com 1-2 buscas. Deep research, research report, citations.

`/plugin install terras-deep-research@terras`

Palavras-chave: `deep research`, `pesquisa profunda`, `relatorio`, `citacoes`, `pesquisa`, `analise`, `tendencias`, `triangulacao`, `estado da arte`

### terras-last30days

Pesquisa o que se falou sobre um tema nos últimos 30 dias em Reddit, X, YouTube, Hacker News, Polymarket, GitHub e web, com motor local vendorizado. Use quando o pedido for descobrir pauta, medir se um assunto está circulando, checar o que a comunidade está discutindo ou comparar dois temas antes de escrever um post. Descoberta, não fonte: o resultado orienta, a verificação vem da fonte primária. last30days, trending topics, o que estão falando, pesquisa de pauta.

`/plugin install terras-last30days@terras` · v3.25.0

Palavras-chave: `last30days`, `pesquisa de pauta`, `trending`, `reddit`, `hacker news`, `youtube`, `x`, `sentimento`, `descoberta`, `tópicos recentes`

### terras-noticias

Lê boletins e roundups de notícias (ratos de IA e afins), tria por criticidade e prioridade, resume todos os itens rápido e escreve o rascunho do post de digest para o LinkedIn. Use quando o usuário mandar um link de boletim semanal (ratos.link/epNN), pedir 'le as notícias', 'resumo das notícias', 'o que saiu essa semana', 'triagem de notícias', 'digest', ou julgar prioridade e criticidade de notícias de IA e tecnologia. News digest, news roundup, weekly recap, news triage, priority and criticality.

`/plugin install terras-noticias@terras`

Palavras-chave: `notícias`, `noticias`, `news`, `boletim`, `roundup`, `digest`, `ratos de ia`, `ratos`, `triagem`, `prioridade`, `criticidade`, `resumo semanal`, `news digest`, `weekly recap`

### terras-paper-diario

Lê papers (arXiv e afins) sobre estudos que afetam o trabalho de quem desenvolve — agentes de IA em PRs, qualidade de código gerado, produtividade, mercado de trabalho — e produz uma análise com resumo honesto (com números), aplicação prática e aviso específico para JÚNIOR, PLENO e SÊNIOR, fechando com um recado PARA TODOS. Use quando o usuário mandar um link de paper, pedir 'analisar paper', 'paper do dia', ou na verificação diária do arXiv. Daily arXiv digest for developers with per-level (junior/mid/senior) analysis and warnings.

`/plugin install terras-paper-diario@terras`

Palavras-chave: `paper`, `arxiv`, `estudo`, `pesquisa`, `paper do dia`, `paper-diario`, `agentes de ia`, `code review`, `carreira dev`, `análise de paper`, `digest diário`

### terras-user-research

Pesquisa com usuários de ponta a ponta: planejar estudo qualitativo (roteiro de entrevista, guia de discussão, questionário de triagem, plano de pesquisa), sintetizar entrevistas em relatório com achados priorizados, personas e oportunidades, e planejar pesquisa quantitativa (survey, design de questionário, análise). Use quando o pedido mencionar pesquisa com usuários, entrevistas, roteiro de entrevista, plano de pesquisa, survey, análise de transcrições ou relatório de pesquisa. User research, user interviews, survey.

`/plugin install terras-user-research@terras`

Palavras-chave: `user research`, `pesquisa com usuarios`, `entrevista`, `roteiro`, `survey`, `sintese`, `personas`, `descoberta`, `qualitativa`, `quantitativa`

### terrasia-pauta-youtube

Pesquisa de demanda (envelope) no YouTube antes de escrever o roteiro: compara consultas de tema pela mediana de views dos resultados, acha outliers (video muito acima da media do proprio canal) e colhe frases recorrentes dos titulos de melhor desempenho. Use quando o pedido envolver escolher tema de video, 'dar o passo atras', pauta de video, qual assunto rende mais, medir demanda de titulo, modelar o que funciona, outliers do YouTube, banco de frases de titulo e capa, ou antes de montar um roteiro com a terras-video.

`/plugin install terrasia-pauta-youtube@terras`

Palavras-chave: `youtube`, `pauta`, `tema`, `envelope`, `demanda`, `views`, `outlier`, `titulo`, `capa`, `thumbnail`, `pesquisa`, `roteiro`, `terrasia`

## IA, prompts e agentes

*Prompts, skills, evals e o comportamento do agente.*

### terras-decisor

Use para tomar decisões estruturadas a partir de um contexto, retornando exclusivamente um YAML válido. Ideal para integração como motor de decisão em pipelines, sem chat ou texto extra. Use apenas quando o output precisa ser um YAML estruturado.

`/plugin install terras-decisor@terras`

### terras-eval-harness

Desenvolvimento guiado por eval para trabalho com agentes e prompts: definir evals de capacidade e de regressão antes de codar, corrigir por código, modelo, regra ou humano, e medir confiabilidade com pass@k e pass^k. Use ao definir critério de passa/falha, montar suíte de regressão de prompt ou comparar versões de modelo. Eval-driven development.

`/plugin install terras-eval-harness@terras`

Palavras-chave: `eval`, `evals`, `eval harness`, `pass@k`, `regressao de prompt`, `prompt regression`, `llm judge`, `benchmark de modelo`

### terras-full-output-enforcement

Força saída completa em qualquer tarefa: proíbe truncamento, placeholders e abreviações tipo 'resto igual', e trata quebra por limite de token. Use quando o modelo estiver entregando trabalho pela metade, código cortado ou quando o pedido exigir arquivo inteiro sem omissões. Full output, no placeholders, complete code.

`/plugin install terras-full-output-enforcement@terras`

Palavras-chave: `output completo`, `truncamento`, `placeholder`, `código completo`, `sem omissões`

### terras-prompt

Use ao criar, revisar, avaliar ou ajustar um PROMPT (texto para IA), não para executar a tarefa descrita. Preserve a intenção original, otimize pela necessidade (não pelo tamanho) e nunca recrie de memória prompt canônico do Prompt Garden (docs/referencia-verbatim).

`/plugin install terras-prompt@terras`

Palavras-chave: `prompt`, `otimizar prompt`, `reescrever prompt`, `avaliar prompt`, `prompt garden`

### terras-seed

Use sempre que o pedido for sobre criar, revisar, avaliar ou ajustar um PROMPT (o texto de instrução dado a uma IA como ChatGPT, Claude ou Gemini), e não sobre executar a tarefa que esse prompt descreve. Dispara em: pedir um prompt pronto para outra IA a partir de ideia vaga; mostrar, colar ou citar um prompt (seu ou de outra pessoa) pedindo opinião, revisão ou conserto; pedir ajuste num prompt de turno anterior (mais curto, outro tom, outra IA-alvo); e qualquer chamado a "Lyra" pedindo ação ligada a IA ou prompt. Ative mesmo se a frase citar uma tarefa final: se o pedido real é sobre o texto-instrução, use esta skill. NÃO ative para pedido direto de executar a tarefa sem menção a "prompt" nem a "Lyra", nem para "Lyra" fora de contexto de IA.

`/plugin install terras-seed@terras`

Palavras-chave: `prompt`, `otimizar prompt`, `revisar prompt`, `avaliar prompt`, `ajustar prompt`, `prompt pra IA`, `monta um prompt`, `esse prompt tá bom`, `Lyra`

### terras-skill-factory

Cria, revisa e mantém skills no padrão da casa terras-: inventário, frontmatter, catálogo de gatilhos, progressive disclosure e teste de aderência antes de fechar. Use quando pedirem para criar uma skill nova, transformar prompt recorrente em skill, revisar ou atualizar uma skill existente, ou auditar se uma skill segue o padrão. Também usa quando alguém perguntar como as skills terras- são estruturadas ou como exportá-las para os servidores.

`/plugin install terras-skill-factory@terras`

Palavras-chave: `skill`, `skills`, `criar skill`, `skill factory`, `padrão terras`, `SKILL.md`, `frontmatter`, `progressive disclosure`, `agent skills`

## Outras

*Ainda sem área no manual: classifique cada uma em `scripts/manual-areas.json`.*

### terras-animacao

Produz peça animada em loop a partir de uma cena HTML dirigida por tempo: o HTML determinístico (contrato ?t=), o render quadro a quadro no Chrome headless e a montagem do GIF (loop, para o feed) e do MP4 (silencioso), com capa estática e preview de celular. Use quando o pedido for animação, gif animado, vídeo curto sem narração, banner animado, diagrama que se desenha, peça em movimento, ou quando a peça pedir mais vida que o estático. Não é para banner estático (terras-banner), vídeo narrado (terras-video), edição e conversão de vídeo (terras-ffmpeg) nem página de explicação técnica (terras-visual-explainer).

`/plugin install terras-animacao@terras` · v1.0.0

Palavras-chave: `animacao`, `animado`, `gif`, `gif animado`, `loop`, `video curto`, `mp4`, `movimento`, `motion`, `banner animado`, `peca animada`, `diagrama animado`, `bpmn animado`, `quadro a quadro`

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

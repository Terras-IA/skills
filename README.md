# TerrasIA Skills

![Banner do TerrasIA Skills: o logo terrasIA, a palavra SKILLS e "marketplace de skills para agentes" sobre fundo escuro, ao lado do grafo de quatro nós e de uma grade de módulos em ciano](banner-readme.png)

**Skills de agente para o Claude Code** — escrita, LinkedIn, RH, financeiro, fiscal, vendas,
design, mídia e desenvolvimento. Cada skill é um plugin independente: instale só as que quiser.

Para navegar pelo catálogo com busca e filtro por área: **[www.terrasia.app/skills](https://www.terrasia.app/skills)**.

[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-0e7490?style=flat-square)](LICENSE)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-22d3ee?style=flat-square)

## Instalar

**No Claude Code**, pelo marketplace:

```bash
/plugin marketplace add Terras-IA/skills
/plugin install terras-linkedin@terras
```

Dentro do Claude Code, `/plugin` mostra o catálogo inteiro e instala o que você marcar. Depois,
para atualizar: `/plugin marketplace update terras`.

**No ZCode, no Codex (GPT) e no opencode**, por link simbólico, com o repositório como fonte:

```bash
git clone https://github.com/Terras-IA/skills.git ~/terras-skills
bash ~/terras-skills/scripts/instalar.sh --aplicar
```

O script cria um link por skill em cada pasta de agente que já existir na sua máquina
(`~/.zcode/skills`, `~/.codex/skills`, `~/.config/opencode/skills`, `~/.claude/skills`); pasta que
não existe não é criada. Como o link aponta para o repositório, `git -C ~/terras-skills pull`
atualiza tudo. Para instalar só algumas skills, copie a pasta `skills/<nome>/` para a pasta de
skills do agente.

**No claude.ai e no ChatGPT**, por upload: `npm run pacotes` gera um `.zip` por skill em
`dist/pacotes/`, no formato que as duas telas de upload aceitam.

### Antes de instalar muitas skills

- **Um caminho por agente.** O marketplace e o `instalar.sh` entregam a mesma skill por dois
  caminhos. Num mesmo agente, use só um: com os dois, a skill aparece duas vezes, o modelo escolhe
  uma pelo nome e pela descrição e não avisa qual rodou. O mesmo vale para uma cópia antiga
  subida no claude.ai: apague-a lá quando passar a usar a deste repositório.
- **O orçamento da lista de skills.** O Claude Code entrega ao modelo a lista de skills com
  orçamento de cerca de 1% da janela de contexto. Com o catálogo inteiro, a descrição que não cabe
  é cortada e a skill aparece só pelo nome: aí ela quase só roda quando chamada por ele
  (`/terras-video`). Instale só o que usa, ou aumente o orçamento em `~/.claude/settings.json`:

  ```json
  { "env": { "SLASH_COMMAND_TOOL_CHAR_BUDGET": "40000" } }
  ```

  São cerca de 10 mil tokens a mais por sessão. Por isso toda descrição deste repositório tem
  no máximo 300 caracteres (regra 8, abaixo).
- **Skills só por chamada.** `terras-design-taste-frontend-v1`, `terras-gpt-taste` e
  `terras-humanizer-dev` repetem o trabalho de outra skill da casa e têm
  `disable-model-invocation: true`: o modelo não as escolhe sozinho, elas rodam quando você chama
  pelo nome.
- **Plugin que não carrega.** Se `/plugin` mostrar *failed to load: conflicting manifests* num
  plugin `@terras`, a instalação é anterior ao manifesto atual: rode
  `/plugin marketplace update terras`, desinstale o plugin e instale de novo.

## O que tem dentro

Um recorte por área — o catálogo completo está logo abaixo.

**Escrita e conteúdo** — `terras-linkedin`, `terras-humanizer`, `terras-substack`, `terras-ebook`, `terras-noticias`, `terras-paper-diario`.
Posts que soam humanos, newsletter publicada e agendada, e-book e audiolivro para vender, e boletins ou papers que viram resumo e post.

**People e RH** — `terras-gerador-de-pdi`, `terras-gerador-de-okrs-de-pessoas`, `terras-gerador-de-matriz-9-box`, `terras-gerador-de-plano-de-entrevista-estruturada`, `terras-analisador-de-pulse-semanal`, `terras-triagem-riscos-psicossociais`, `terras-screenador-de-curriculos-com-ia`, `terras-roteirizador-de-onboarding`, `terras-gestao-de-ferias-e-escalas`.
Da triagem e da entrevista ao PDI, aos OKRs e ao comunicado — com critério e evidência, sem dado sensível.

**Financeiro e fiscal** — `terras-conciliacao-bancaria-ofx`, `terras-conferencia-fechamento-folha`, `terras-conferencia-nfe-tomador-prestador`, `terras-apuracao-retencoes-federais`, `terras-fluxo-de-contas-a-pagar`, `terras-gestao-de-inadimplencia-cobranca`.
Conciliação bancária, fechamento de folha, conferência de nota e retenções: separa o que fecha do que precisa de decisão humana.

**Vendas e mercado** — `terras-qualificacao-icp-bant`, `terras-playbook-quebra-objecoes`, `terras-elaboracao-proposta-comercial`, `terras-analise-swot`, `terras-matriz-gut`, `terras-pauta-mercado`.
Qualificação de lead, resposta à objeção real, proposta, priorização com GUT e a análise mercado × TerrasIA em formato cobre/rejeita/falta.

**Design e UI** — `terras-design`, `terras-design-system`, `terras-brand`, `terras-brandkit`, `terras-ui-ux-pro-max`, `terras-image-to-code`, `terras-minimalist-ui`, `terras-industrial-brutalist-ui`.
Identidade, tokens, componentes e direção de arte — com o anti-genérico do design-taste.

**Mídia: áudio, vídeo e imagem** — `terras-audio`, `terras-video`, `terras-banner`, `terras-ffmpeg`, `terras-transcription`, `terras-slides`, `terras-visual-explainer`, `terras-karpathy-explainer`.
Narração com pronúncia cuidada, vídeo para YouTube e Shorts, banner, transcrição local sem API, slides, páginas que explicam visualmente e o mesmo tema em quatro formatos (texto em inglês controlado, diagrama, página interativa e vídeo).

**Pesquisa e conhecimento**: `terras-deep-research`, `terras-last30days`, `terras-x-ia`, `terras-linkedin-varredura`, `terras-linkedin-conhecimento`.
Pesquisa com citação rastreada, o que circulou nos últimos 30 dias, o que saiu de IA no X e o feed do LinkedIn transformado em nota de conhecimento, com conferência na fonte primária e sem curtir nem comentar nada.

**Desenvolvimento** — `terras-revisao-de-codigo`, `terras-security-review`, `terras-e2e-testing`, `terras-react-patterns`, `terras-postgres`, `terras-mcp-server`, `terras-database-migrations`, `terras-tech-debt`, `terras-standards`.
Revisão pelo risco que a mudança cria, segurança, testes ponta a ponta, banco, migrations e o padrão de engenharia da casa.

## O catálogo completo

<!-- catalogo:inicio -->
<!-- gerado por `npm run readme` a partir do catálogo — não edite à mão -->

**130 skills instaláveis** entre as 141 deste repositório; as demais ficam fora do marketplace — 8 skills de processo do motor (`.nao-instalar`) e 3 skills ligadas a projeto de cliente (`marketplace-fora.json`).

<details>
<summary><b>Ver a lista completa (130 skills)</b></summary>

| Skill | O que faz |
|---|---|
| [`terras-accessibility`](skills/terras-accessibility) | Projetar, implementar e auditar interface acessível no nível AA da WCAG 2.2 em Web, iOS e Android: papéis e rótulos ARIA, foco, contraste, tamanho de alvo e leitor… |
| [`terras-agenda-de-touchpoints`](skills/terras-agenda-de-touchpoints) | Estrutura 1:1s recorrentes com pautas, histórico de feedback, decisões e loops abertos. |
| [`terras-analisador-de-linguagem-inclusiva`](skills/terras-analisador-de-linguagem-inclusiva) | Revisa vagas, avaliações e comunicados em busca de linguagem enviesada, excludente ou pouco acessível. |
| [`terras-analisador-de-pulse-semanal`](skills/terras-analisador-de-pulse-semanal) | Processa respostas de pulse survey semanal e transforma temas recorrentes em insights acionáveis para lideranças. |
| [`terras-analise-swot`](skills/terras-analise-swot) | Análise SWOT rastreável: cada item cita a fonte, o que não tem fonte vira hipótese com teste, e fecha em cruzamentos TOWS com ação, dono e verificação. |
| [`terras-animacao`](skills/terras-animacao) | Peça animada em loop (GIF e MP4 sem som) a partir de cena HTML dirigida por tempo, renderizada quadro a quadro. |
| [`terras-apuracao-retencoes-federais`](skills/terras-apuracao-retencoes-federais) | Confere se as retenções federais na fonte de uma nota de serviço foram aplicadas, dispensadas ou esquecidas, usando as alíquotas e limites informados pela empresa, nunca… |
| [`terras-astro`](skills/terras-astro) | Publica site estático multilíngue de graça no Cloudflare Pages com Astro e conteúdo em markdown. |
| [`terras-audio`](skills/terras-audio) | Voz, pronúncia e cadeia de áudio para narração de vídeo, audiolivro, nota de voz e capítulo. · Instale com o plugin `terras-midia`. |
| [`terras-auditoria-ui`](skills/terras-auditoria-ui) | Audita uma tela existente contra o próprio design system do produto, prova até 3 problemas visuais e escreve planos para outra execução, sem tocar no código. |
| [`terras-azure-devops`](skills/terras-azure-devops) | List Azure DevOps projects, repositories, and branches; create pull requests; manage work items; check build status. |
| [`terras-banner`](skills/terras-banner) | Imagem que acompanha post, newsletter ou nota: banner 1200x628 (LinkedIn, og:image da Substack), card 1080x1350 e capa, com arte gerada, tipografia da marca e gate… · Instale com o plugin `terras-midia`. |
| [`terras-banner-design`](skills/terras-banner-design) | Banners para redes sociais, anúncios, heros de site e impressão, com 22 estilos de direção de arte e tamanhos por plataforma. |
| [`terras-bar-raiser-de-cultura`](skills/terras-bar-raiser-de-cultura) | Estrutura entrevistas de fit cultural com critérios observáveis, scoring e recomendação; use em processos seletivos que exigem avaliação consistente de valores. |
| [`terras-brand`](skills/terras-brand) | Marca: voz e tom, frameworks de mensagem, paleta, tipografia, organização de ativos e auditoria de consistência, sincronizadas com os tokens de design. |
| [`terras-brandkit`](skills/terras-brandkit) | Gera a imagem do brand kit: quadro de identidade com direção de logo, paleta, tipografia e aplicações em mockup. |
| [`terras-briefing-pre-reuniao-de-lideranca`](skills/terras-briefing-pre-reuniao-de-lideranca) | Prepara briefings para líderes com saúde do time, feedbacks recentes, loops abertos, riscos e perguntas para a reunião. |
| [`terras-canal-whatsapp`](skills/terras-canal-whatsapp) | Publica texto ou imagem no canal (newsletter) do WhatsApp pela sessão pareada do sidecar, com pré-checagem e confirmação explícita. |
| [`terras-care-to-dare-coach`](skills/terras-care-to-dare-coach) | Gera prompts de coaching, scripts de feedback e planos de desafio com base no framework Care to Dare. |
| [`terras-coders-mural`](skills/terras-coders-mural) | Engajamento em lote no Mural de Posts da COD3RS: curte, lê o post linkado no LinkedIn e comenta em inglês lá e em português no mural, só com aprovação. |
| [`terras-comentarios`](skills/terras-comentarios) | Comenta em lote posts do LinkedIn colados pelo usuário: um comentário de até 100 caracteres por post, pronto para colar. Use quando houver 2 ou mais posts para comentar. |
| [`terras-conciliacao-bancaria-ofx`](skills/terras-conciliacao-bancaria-ofx) | Concilia extrato bancário com os lançamentos internos e separa o que casou, o que divergiu, o que é tarifa e o que ficou sem par. |
| [`terras-conferencia-fechamento-folha`](skills/terras-conferencia-fechamento-folha) | Confere o fechamento da folha antes do envio — horas extras, adicional noturno, faltas e encargos — apontando o que não fecha por matrícula, sem afirmar alíquota nem… |
| [`terras-conferencia-nfe-tomador-prestador`](skills/terras-conferencia-nfe-tomador-prestador) | Confere uma nota fiscal recebida ou emitida campo a campo e separa o que está consistente do que precisa de decisão humana, sem afirmar alíquota nem enquadramento… |
| [`terras-consolidacao-de-memoria`](skills/terras-consolidacao-de-memoria) | Mantém a memória de um repositório pequena e verdadeira: ao fechar uma spec, registra o que foi entregue e funde os requisitos num doc por domínio; compacta o histórico… |
| [`terras-construtor-de-job-description`](skills/terras-construtor-de-job-description) | Gera descrições de cargo claras, inclusivas e alinhadas à cultura e ao modelo de competências da organização. |
| [`terras-cover-letter`](skills/terras-cover-letter) | Escreve e revisa cartas de apresentação para vagas internacionais e remotas, traduzindo experiência brasileira em valor global. |
| [`terras-critica-de-spec`](skills/terras-critica-de-spec) | Critica uma spec antes da implementação (critério de aceite que não dá para testar, caso de borda faltando, escopo ambíguo, contradição, regra do repositório violada)… |
| [`terras-dashboard-de-utilizacao-de-beneficios`](skills/terras-dashboard-de-utilizacao-de-beneficios) | Analisa adesão, utilização, custo e satisfação dos benefícios por tipo de saldo, período e público permitido. |
| [`terras-database-migrations`](skills/terras-database-migrations) | Migrations seguras e reversíveis: expand-contract sem downtime, índice concorrente, backfill em lotes e fluxo por ferramenta (PostgreSQL, Prisma, Drizzle, Kysely… |
| [`terras-decisor`](skills/terras-decisor) | Use para tomar decisões estruturadas a partir de um contexto, retornando exclusivamente um YAML válido. |
| [`terras-deep-research`](skills/terras-deep-research) | Pesquisa em profundidade com citações rastreadas: pipeline de fases, registro de evidências e relatório com bibliografia. |
| [`terras-design`](skills/terras-design) | Guarda-chuva de design: logo com IA, identidade corporativa (CIP), pacote amplo de peças; roteia para terras-brand, terras-design-system e terras-ui-styling. |
| [`terras-design-system`](skills/terras-design-system) | Design tokens em três camadas (primitivo, semântico, componente), specs e estados de componente, variáveis CSS e tema Tailwind. |
| [`terras-design-taste-frontend`](skills/terras-design-taste-frontend) | Anti-slop de frontend: lê o briefing, infere a direção de design e entrega landing page, portfólio ou redesign que não parece template. |
| [`terras-design-taste-frontend-v1`](skills/terras-design-taste-frontend-v1) | Versão 1 legada da terras-design-taste-frontend, preservada para projetos que dependem do comportamento exato da v1. |
| [`terras-e2e-testing`](skills/terras-e2e-testing) | Testes end-to-end com Playwright: Page Object Model, configuração, integração com CI, artefatos (trace, vídeo, screenshot) e estratégia para teste instável. |
| [`terras-ebook`](skills/terras-ebook) | Cria e-book e audiolivro para vender: estrutura, diagramação EPUB e PDF A5, capa, ISBN, plataforma, royalties, preço e lançamento, e transforma acervo de YouTube… |
| [`terras-educacao-corporativa`](skills/terras-educacao-corporativa) | Educação corporativa com 26 prompts guiados: estratégia de T&D, diagnóstico de necessidades, mapa de competências, trilhas, planos de aula e indicadores de impacto. |
| [`terras-elaboracao-proposta-comercial`](skills/terras-elaboracao-proposta-comercial) | Estrutura a minuta de uma proposta a partir do que foi levantado na conversa, separando escopo de expectativa e marcando cada número que ainda precisa de confirmação… |
| [`terras-eval-harness`](skills/terras-eval-harness) | Desenvolvimento guiado por eval para agentes e prompts: evals de capacidade e regressão antes de codar e confiabilidade com pass@k e pass^k. |
| [`terras-excalidraw`](skills/terras-excalidraw) | Use quando o pedido for um desenho Excalidraw, diagrama editável, esboço à mão, quadro branco, wireframe rascunho, ou imagem de diagrama (PNG/SVG) para post, slide… |
| [`terras-ffmpeg`](skills/terras-ffmpeg) | Edita vídeo e áudio com FFmpeg local por pedido em linguagem natural: cortar, juntar, 9:16, legendas, loudness, música com ducking, exportar por plataforma. |
| [`terras-fluxo-de-contas-a-pagar`](skills/terras-fluxo-de-contas-a-pagar) | Leva uma conta a pagar da chegada do documento até a liberação: autenticidade do boleto, alçada por valor e escalonamento. |
| [`terras-frontend-slides`](skills/terras-frontend-slides) | Apresentação HTML com animação, sem dependências, em arquivo único 16:9, do zero ou convertendo PPT/PPTX. |
| [`terras-full-output-enforcement`](skills/terras-full-output-enforcement) | Força saída completa: proíbe truncamento, placeholders e 'resto igual', e trata corte por limite de token. |
| [`terras-gerador-de-all-hands`](skills/terras-gerador-de-all-hands) | Prepara o encontro mensal de toda a empresa com resumo de resultados, perguntas votadas e talking points. |
| [`terras-gerador-de-comunicacao-de-rh`](skills/terras-gerador-de-comunicacao-de-rh) | Redige comunicados internos claros sobre políticas, mudanças organizacionais, benefícios e atualizações de People. |
| [`terras-gerador-de-matriz-9-box`](skills/terras-gerador-de-matriz-9-box) | Organiza performance e potencial em uma matriz 9-Box com critérios, evidências e planos de ação por quadrante. |
| [`terras-gerador-de-okrs-de-pessoas`](skills/terras-gerador-de-okrs-de-pessoas) | Cria OKRs trimestrais de People conectados à estratégia do negócio, com resultados mensuráveis e responsáveis. |
| [`terras-gerador-de-pdi`](skills/terras-gerador-de-pdi) | Cria planos de desenvolvimento individual conectando feedbacks, competências, ações, recursos e evidências de evolução. |
| [`terras-gerador-de-plano-de-entrevista-estruturada`](skills/terras-gerador-de-plano-de-entrevista-estruturada) | Cria roteiros por competência com perguntas comportamentais, sinais de evidência e rubrica de avaliação. |
| [`terras-gerador-de-politica-de-beneficios`](skills/terras-gerador-de-politica-de-beneficios) | Redige políticas de benefícios claras, aplicáveis e alinhadas ao PAT e ao orçamento informado pela empresa. |
| [`terras-gestao-de-ferias-e-escalas`](skills/terras-gestao-de-ferias-e-escalas) | Organiza períodos aquisitivo e concessivo, abono e fracionamento por equipe, e mostra onde a escala não se sustenta — com os prazos informados pela empresa, não… |
| [`terras-gestao-de-inadimplencia-cobranca`](skills/terras-gestao-de-inadimplencia-cobranca) | Monta a régua de cobrança de D-3 a D+15 com o tom de cada contato, os encargos do contrato e o ponto de decisão. |
| [`terras-governanca-padroes`](skills/terras-governanca-padroes) | Audita onde as convenções de um projeto vivem e as transforma em regra versionada, com dono, revisão e deprecação, legível por agente. |
| [`terras-gpt-taste`](skills/terras-gpt-taste) | Variante estrita do design-taste para GPT/Codex: layout com randomização real, AIDA, bento sem buracos, GSAP e anti-slop agressivo. |
| [`terras-high-end-visual-design`](skills/terras-high-end-visual-design) | Design visual de alto padrão: fontes, espaçamento, sombras, cartões e animações que fazem o site parecer caro, bloqueando o visual barato de IA. |
| [`terras-historias-infantis`](skills/terras-historias-infantis) | Histórias infantis ilustradas em quadrinhos e o livro de colorir da mesma história: roteiro página a página, arte vetorial infantil e versão para pintar. |
| [`terras-humanizer`](skills/terras-humanizer) | Reescreve texto com cara de IA para soar humano, sem mudar o que ele diz nem inventar nada; remove marcas de IA em português e inglês e baixa o inglês para nível B1/B2. |
| [`terras-humanizer-dev`](skills/terras-humanizer-dev) | Variante da terras-humanizer que prioriza preservar a voz, as opiniões e o ritmo do autor, aceitando imperfeição natural. |
| [`terras-identidade`](skills/terras-identidade) | Lê a identidade visual de uma marca a partir de imagens (anúncio, print, manual, site) e entrega cores medidas, tipografia, logo recortado e tokens CSS/JSON/Tailwind. |
| [`terras-image-to-code`](skills/terras-image-to-code) | Pipeline imagem-primeiro: gera a imagem de referência, analisa e implementa o frontend fiel a ela, seção a seção. |
| [`terras-imagegen-frontend-mobile`](skills/terras-imagegen-frontend-mobile) | Gera imagens de telas e fluxos de app mobile (iOS, Android, cross-platform) com mockup de celular, tipografia legível, paleta controlada e consistência entre telas. |
| [`terras-imagegen-frontend-web`](skills/terras-imagegen-frontend-web) | Gera as imagens de referência de um site — uma imagem horizontal por seção, nunca comprimidas — com variedade de composição, escala de hero, CTA e paleta única. |
| [`terras-industrial-brutalist-ui`](skills/terras-industrial-brutalist-ui) | Interface brutalista industrial: grade suíça rígida, tipografia mecânica de contraste extremo, paleta utilitária e textura analógica. |
| [`terras-karpathy-explainer`](skills/terras-karpathy-explainer) | Explica um tema nos 4 formatos do truque atribuído ao Karpathy: texto em ~80% do ASD-STE100 com medição, diagrama, página HTML interativa e vídeo narrado. |
| [`terras-laravel`](skills/terras-laravel) | Build robust Laravel apps avoiding Eloquent traps, queue failures, and auth pitfalls. |
| [`terras-last30days`](skills/terras-last30days) | Pesquisa o que se falou de um tema nos últimos 30 dias em Reddit, X, YouTube, Hacker News, GitHub e web. |
| [`terras-linkedin`](skills/terras-linkedin) | Escreve e revisa posts de LinkedIn (hook, estrutura, CTA, hashtags, zero travessão) e explica alcance e impressões. |
| [`terras-linkedin-alvos`](skills/terras-linkedin-alvos) | Acompanha perfis-alvo do LinkedIn (executivos, gestores, recrutadores), acha os posts recentes, curte e prepara comentários que acrescentam, publicados só com aprovação. |
| [`terras-linkedin-conhecimento`](skills/terras-linkedin-conhecimento) | Baixa texto e imagens de post do LinkedIn (link ou tema) e gera nota de conhecimento: o que diz, o que a imagem traz, conferência em fonte primária e lacunas. |
| [`terras-linkedin-metricas`](skills/terras-linkedin-metricas) | Extrai, guarda e diagnostica as estatísticas dos posts do LinkedIn do usuário: impressões, alcance na e fora da rede, reações, salvamentos, seguidores e demografia. |
| [`terras-linkedin-varredura`](skills/terras-linkedin-varredura) | Varre o feed do LinkedIn desde a última verificação (ou 24 h), tria o que é novo e gera nota de conhecimento de cada post útil (vídeo, imagem ou texto), com checkpoint. |
| [`terras-linkedin-videos`](skills/terras-linkedin-videos) | Varre o feed do LinkedIn por tema atrás de posts com vídeo e baixa os escolhidos com o texto do post; link de post colado sozinho já baixa direto. · Instale com o plugin `terras-videos-linkedin`. |
| [`terras-mapeamento-de-processos`](skills/terras-mapeamento-de-processos) | Mapeia um processo a partir de áudio, gravação de tela ou relato e devolve o fluxo AS-IS/TO-BE, diagnóstico com números e plano de melhoria com oportunidades… |
| [`terras-matriz-gut`](skills/terras-matriz-gut) | Prioriza problemas concorrentes com a matriz GUT: notas ancoradas de Gravidade, Urgência e Tendência, faixa de decisão antes de pontuar e plano de ataque com dono… |
| [`terras-mcp-server`](skills/terras-mcp-server) | Construção de servidor MCP com o SDK Node/TypeScript: tools, resources, prompts, validação com Zod e escolha de transporte (stdio ou Streamable HTTP). |
| [`terras-miniapp-builder`](skills/terras-miniapp-builder) | Cria miniapp do zero: entrevista as lacunas, decide arquitetura e LGPD, escreve a copy, constrói local-first e publica na Vercel. |
| [`terras-minimalist-ui`](skills/terras-minimalist-ui) | UI minimalista editorial: paleta monocromática quente, hierarquia tipográfica, bento grid flat e pastéis discretos; sem gradientes nem sombras pesadas. |
| [`terras-motion-performance`](skills/terras-motion-performance) | Audita e corrige animação que trava: layout thrashing, propriedade fora do compositor, scroll por JS, rAF sem fim, blur grande, will-change sobrando. |
| [`terras-noticias`](skills/terras-noticias) | Lê boletins e roundups de notícias de IA e tecnologia, tria por criticidade e prioridade, resume os itens e escreve o rascunho do digest para o LinkedIn. |
| [`terras-paper-diario`](skills/terras-paper-diario) | Analisa papers (arXiv e afins) que afetam quem desenvolve: resumo honesto com números, o que não significa, e aplicação e aviso para júnior, pleno e sênior. |
| [`terras-pauta-mercado`](skills/terras-pauta-mercado) | Transforma referência externa (repo, post, anúncio, paper) na análise mercado × TerrasIA com cobre/rejeita/falta e no pacote de posts por canal. |
| [`terras-people-dashboard-automatico`](skills/terras-people-dashboard-automatico) | Monta um dashboard mensal de liderança com headcount, retenção, remuneração, contratação e DEI. |
| [`terras-php`](skills/terras-php) | Write solid PHP avoiding type juggling traps, array quirks, and common security pitfalls. |
| [`terras-pipeline-de-automacao`](skills/terras-pipeline-de-automacao) | Projeta pipelines de automação em que scripts determinísticos fazem o trabalho e o agente só decide em pontos de revisão, com rastro de hashes e recibos de execução. |
| [`terras-plano-tdd`](skills/terras-plano-tdd) | Transforma uma spec revisada em plano test-first (RED, GREEN, REFACTOR) com arquivo e nome de teste concretos, e uma lista de tarefas em que cada uma diz por comando… |
| [`terras-playbook-quebra-objecoes`](skills/terras-playbook-quebra-objecoes) | Classifica a objeção real por trás do que o cliente disse e devolve caminhos de resposta apoiados no que a empresa consegue sustentar, sem prometer preço, prazo… |
| [`terras-ponytail`](skills/terras-ponytail) | Lazy senior dev mode for any coding task (write, refactor, fix, review): YAGNI, stdlib first, no unrequested abstractions. Not for non-coding requests. |
| [`terras-postgres`](skills/terras-postgres) | Administra e otimiza banco PostgreSQL pelas tools do postgres-mcp: verificação de saúde, ajuste de índice, análise de plano de consulta, leitura de schema e execução… |
| [`terras-prompt`](skills/terras-prompt) | Use ao criar, revisar, avaliar ou ajustar um PROMPT (texto para IA), não para executar a tarefa descrita. |
| [`terras-qualificacao-icp-bant`](skills/terras-qualificacao-icp-bant) | Qualifica um lead a partir do que foi dito na conversa — orçamento, autoridade, necessidade e timing — separando o que o cliente afirmou do que o vendedor supôs,… |
| [`terras-react-patterns`](skills/terras-react-patterns) | Padrões de React 18/19: disciplina de hooks, fronteira entre server e client component, Suspense e error boundary, form actions, busca de dados, árvore de decisão… |
| [`terras-react-testing`](skills/terras-react-testing) | Testes de componente React com React Testing Library, Vitest ou Jest, MSW para simular rede, asserções de acessibilidade com axe, e quando usar teste de componente… |
| [`terras-redesign-existing-projects`](skills/terras-redesign-existing-projects) | Redesign de projeto existente: audita a UI atual, identifica padrões genéricos de IA e aplica padrão premium sem quebrar funcionalidade. |
| [`terras-reverse-engineer`](skills/terras-reverse-engineer) | Investiga como uma feature funciona em software empacotado (Electron, site, APK, binário nativo, .NET, firmware) com o REA, cada conclusão presa a uma evidência. |
| [`terras-revisao-cruzada`](skills/terras-revisao-cruzada) | Manda uma spec ou um diff, em paralelo, para agentes de linha de comando de outros fornecedores (Codex, opencode) e junta os vereditos num revisao.md único,… |
| [`terras-revisao-de-codigo`](skills/terras-revisao-de-codigo) | Revisa uma mudança de código pelo risco que ela cria, com foco em integração que movimenta dinheiro ou dado de cliente: correção, idempotência, falha parcial, segredo… |
| [`terras-robo-de-atendimento-de-rh`](skills/terras-robo-de-atendimento-de-rh) | Estrutura um atendimento de auto serviço para dúvidas de férias, benefícios, políticas e folha, com encaminhamento seguro para casos complexos. |
| [`terras-roteirizador-de-onboarding`](skills/terras-roteirizador-de-onboarding) | Monta um plano de onboarding de 30, 60 e 90 dias com check-ins, tarefas e expectativas claras para a nova pessoa. |
| [`terras-screenador-de-curriculos-com-ia`](skills/terras-screenador-de-curriculos-com-ia) | Ranqueia currículos por requisitos da vaga e anonimiza dados sensíveis para apoiar uma triagem mais justa e auditável. |
| [`terras-security-review`](skills/terras-security-review) | Checklist e padrões de segurança para código: autenticação, entrada do usuário, segredos, endpoints de API, pagamento e dados sensíveis, com anexo de segurança… |
| [`terras-seed`](skills/terras-seed) | Cria, revisa e ajusta PROMPTS para outra IA (ChatGPT, Claude, Gemini), sem executar a tarefa que o prompt descreve; também atende por 'Lyra'. |
| [`terras-seo`](skills/terras-seo) | Auditar, planejar e implementar SEO: SEO técnico, otimização on-page, dados estruturados (schema.org), Core Web Vitals e estratégia de conteúdo. |
| [`terras-simulador-de-oferta`](skills/terras-simulador-de-oferta) | Simula propostas de remuneração considerando benchmark de mercado, equidade interna e cenários de negociação. |
| [`terras-skill-factory`](skills/terras-skill-factory) | Cria, revisa e mantém skills no padrão da casa terras-: frontmatter, descrição que dispara, progressive disclosure, checagem de colisão com skill parecida e teste… |
| [`terras-slides`](skills/terras-slides) | Deck HTML estratégico e persuasivo com Chart.js: estratégia por contexto, layouts, fórmulas de copy e design tokens. |
| [`terras-spec-flow`](skills/terras-spec-flow) | Conduz uma feature de ponta a ponta por spec (estilo spec-kit): princípios do repo, spec, crítica, plano TDD, análise de consistência, implementação e fechamento,… |
| [`terras-standards`](skills/terras-standards) | Aplica os Padrões Agnósticos de Engenharia e Produto v4.0 (arquitetura, segurança, privacidade e IA) com evidência real quando houver. |
| [`terras-stitch-design-taste`](skills/terras-stitch-design-taste) | Gera o DESIGN.md para o Google Stitch: contrato de design premium anti-genérico (tipografia estrita, cor calibrada, layout assimétrico, micro-motion). |
| [`terras-substack`](skills/terras-substack) | Publica, agenda e gerencia posts e Notes na Substack pela API interna do editor, só com Python do sistema. |
| [`terras-tech-debt`](skills/terras-tech-debt) | Auditoria de dívida técnica e arquitetura de um repositório inteiro, com achados em arquivo:linha, severidade, esforço e a seção 'parece ruim mas está certo'. |
| [`terras-transcription`](skills/terras-transcription) | Transcreve áudio localmente e sem API (reunião, export do Otter/Zoom/Meet/Teams, nota de voz, entrevista, aula), separa quem falou e marca trecho duvidoso. |
| [`terras-treino-ingles`](skills/terras-treino-ingles) | Treino de inglês falado por recordação ativa: frase em português, o usuário traduz de memória, correção na hora e o erro volta em repetição espaçada, com ouvir… |
| [`terras-triagem-riscos-psicossociais`](skills/terras-triagem-riscos-psicossociais) | Lê sinais agregados de sobrecarga e atrito de uma equipe e entrega indícios com evidência para a gestão avaliar, sem diagnosticar pessoa, sem dado de saúde… |
| [`terras-ui-styling`](skills/terras-ui-styling) | Implementa interface com shadcn/ui e Tailwind CSS: componentes, tema, acessibilidade, responsividade e design em canvas. |
| [`terras-ui-ux-pro-max`](skills/terras-ui-ux-pro-max) | Base local de UI/UX com busca própria: estilos, paletas por produto, pares tipográficos, diretrizes de UX e guias de stack; gera o design system do produto em MASTER.md. |
| [`terras-user-research`](skills/terras-user-research) | Pesquisa com usuários de ponta a ponta: plano, roteiro de entrevista, triagem, síntese em achados, personas e oportunidades, e survey quantitativo. |
| [`terras-validacao-regularidade-cadastral`](skills/terras-validacao-regularidade-cadastral) | Organiza a checagem de idoneidade de um fornecedor ou parceiro — o que precisa ser verificado, onde, com que validade — e registra o que ficou sem comprovação. |
| [`terras-vercel`](skills/terras-vercel) | Deploy applications and manage projects with complete CLI reference. Commands for deployments, projects, domains, environment variables, and live documentation access. |
| [`terras-video`](skills/terras-video) | Monta vídeo para YouTube e Shorts a partir de roteiro: cartelas na identidade da marca, narração por voz neural e mp4 horizontal (1920x1080) ou vertical (1080x1920). · Instale com o plugin `terras-midia`. |
| [`terras-video-downloader`](skills/terras-video-downloader) | Baixa o vídeo de uma URL (LinkedIn pelo player público; o resto via yt-dlp) e prepara a análise em folhas de quadros. Use para baixar ou analisar vídeo de link. · Instale com o plugin `terras-videos-linkedin`. |
| [`terras-visual-explainer`](skills/terras-visual-explainer) | Páginas HTML autocontidas que explicam visualmente sistemas, diffs, planos, dados e conceitos: diagramas, arquitetura, tabelas comparativas, inclusive diagrama animado… |
| [`terras-vite`](skills/terras-vite) | Padrões do Vite: config, plugins, HMR, variáveis de ambiente (e o que vaza no bundle), proxy, SSR, modo biblioteca, pré-bundling de dependências e otimização de build. |
| [`terras-x-ia`](skills/terras-x-ia) | Vasculha o X (Twitter) logado por posts de IA (modelos, agentes, papers, ferramentas de dev) numa janela de dias, separa sinal de isca e entrega os que importam com link… |
| [`terras-zap`](skills/terras-zap) | Varre site ou API com o OWASP ZAP local em modo headless (baseline passivo; ativo só com autorização), gera relatório e faz a triagem dos alertas com correção. |
| [`terrasia-pauta-youtube`](skills/terrasia-pauta-youtube) | Pesquisa de demanda no YouTube antes do roteiro: compara temas pela mediana de views, acha outliers por canal e colhe frases recorrentes dos títulos que performam. |
| [`terrasia-post-empresa`](skills/terrasia-post-empresa) | Produz a peça da Company Page do TerrasIA: post na voz de produto e imagem na identidade da marca (1200x628 e 1080x1350), com régua de texto e aceite no celular. |
| [`terrasia-vagas-coders`](skills/terrasia-vagas-coders) | Filtra as vagas do board da COD3RS e do Rebase Jobs (rebasedev.com.br/vagas) contra o currículo do usuário em baldes A (recomendar), B (talvez) e C (descarte com motivo)… |

</details>
<!-- catalogo:fim -->

## Plugin que empacota mais de uma skill

`terras-audio`, `terras-banner` e `terras-video` usam scripts umas das outras e saem juntas no
plugin `terras-midia` (`/plugin install terras-midia@terras`). Pelo `instalar.sh`, as três já
ficam lado a lado e funcionam sem o plugin.

## Skills que publicam por você

As duas abaixo agem em sites com a sua conta. Nada é publicado sem o seu "aprovado" no chat.

### terras-coders-mural

Faz a rodada de engajamento do **Mural de Posts** da comunidade COD3RS:

1. lista os posts novos (ou mais antigos, como quando você rola a tela);
2. lê cada post linkado no LinkedIn;
3. escreve um comentário curto e específico, em inglês para o LinkedIn e em português para o mural;
4. **mostra tudo numa tabela e espera o seu "aprovado"**;
5. curte e comenta no mural, e comenta no LinkedIn, conferindo cada publicação.

Nada é publicado sem a sua aprovação no chat.

```bash
/plugin install terras-coders-mural@terras
```

Depois, é só pedir: "curte e comenta os posts de hoje do mural da COD3RS".

**Requisitos:** um navegador que o agente controla (o navegador integrado do app desktop ou a
extensão Claude in Chrome), com você logado na COD3RS e no LinkedIn.

### terras-linkedin-alvos

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

**Aviso:** o LinkedIn proíbe automação nos termos de uso. O plugin trabalha devagar, em volume
baixo e com aprovação humana, o que reduz o risco, mas não o elimina. Use por sua conta. A API do
mural é interna à COD3RS e pode mudar sem aviso.

## O que fica fora do marketplace

- **Skills de processo do motor TerrasIA** (marcadas com `.nao-instalar`): método interno de quem
  mantém o motor, não fazem sentido soltas.
- **Skills ligadas a projeto de cliente:** listadas em `marketplace-fora.json`, com o motivo.

Todas continuam no repositório, na pasta `skills/`.

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

### Adicionar ou mudar uma skill

Skill nova segue a `terras-skill-factory` (padrão da casa: frontmatter, catálogo de gatilhos,
progressive disclosure). Depois de criar ou editar em `skills/`:

1. `npm run gate` (regras + testes) e `npm run marketplace` (regera o manifesto);
2. `npm run readme` (regera a seção do catálogo neste arquivo) e `node scripts/manual.mjs` (regera o `MANUAL.md`);
3. commit e push no `main` — quem já instalou atualiza com `/plugin marketplace update terras`.

O gate reprova manifesto, README **e** MANUAL desatualizados: são arquivos gerados, regravados pelos
comandos acima. O marketplace e os links do `instalar.sh` entregam a MESMA skill por dois caminhos:
num mesmo agente, use um ou outro (ver "Antes de instalar muitas skills").

Editar uma skill do catálogo aqui não muda o motor: o `aplica-bundles.mjs` do `terrasia` importa o
que falta no catálogo de lá e concede as liberações do `skills/bundles.json` (que continua no core,
porque decidir que alma recebe o quê é governança). Importar e liberar seguem sendo dois passos.

## Layout

```
banner-readme.png # imagem de topo deste README
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
plugins/          # só a cópia GERADA dos plugins de grupo (plugins/terras-midia); toda skill mora em skills/
agendaveis.json   # skills que rodam agendadas e o eval de cada uma (regra 9)
evals/            # cenários de avaliação; obrigatório para as agendáveis
scripts/          # verificador, instalador, geradores do marketplace e do README, e seus testes
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
8. **Descrição que cabe na lista.** A `description` do `SKILL.md` tem no máximo 300
   caracteres, numa linha entre aspas (sem bloco YAML). O agente escolhe a skill só por nome e
   descrição, e a lista inteira tem orçamento: descrição longa empurra as outras para fora.
   Diga o que a skill faz, quando usar e, se houver vizinha parecida, quando NÃO usar (`Não é
   para X (terras-y)`). Skill que repete o trabalho de outra entra com
   `disable-model-invocation: true`, para rodar só quando chamada pelo nome.
9. **Eval antes de agendar.** Skill que roda sozinha no agendador, sem
   ninguém no chat, erra sem ninguém ver. Toda skill ou plugin cujo `SKILL.md`
   cita o agendador (`CronCreate`) ou tem seção sobre rodada agendada entra em
   `agendaveis.json` com o caminho do eval. O eval tem `## Cenário`,
   `## Comportamento esperado`, `## Verificação` e `## Última rodada`, e esta
   última registra a rodada que passou, numa linha com a data e "aprovada"
   (`2026-10-10 — 6/6, aprovada.`).
   - Enquanto não houver rodada aprovada, a entrada leva `pendente` com o
     motivo. O gate passa, mas avisa em toda verificação: **não agende** (nem
     reative) a skill até o eval rodar. Sem `pendente` e sem rodada aprovada, o
     gate reprova.
   - Mudou o comportamento da skill, rode o eval de novo e atualize a data. O
     gate não compara datas; é disciplina de quem edita.
   - Agendar uma publicação (o post da Substack para amanhã) não é a skill
     rodar agendada e fica fora da regra.

## Comandos

```bash
npm run gate                       # verificar + testes (rodar antes de commit)
npm run marketplace                # regrava o manifesto do marketplace a partir do catálogo
npm run readme                     # regrava a seção do catálogo no README
node scripts/manual.mjs            # regrava o MANUAL.md
npm run pacotes                    # um .zip por skill em dist/pacotes/ (upload no claude.ai e no ChatGPT)
npm run verificar                  # só as regras acima
npm test                           # testes do verificador, dos geradores e do instalador
bash scripts/instalar.sh           # simulação da instalação
bash scripts/instalar.sh --aplicar # instala (backup em ~/.terras-skills-backup/)
```

Em máquina nova: clonar o repositório e rodar `bash scripts/instalar.sh
--aplicar`. O instalador só cria link nas pastas de agente que já existem.
Ele usa `readlink -f`: Linux, ou macOS 12.3 em diante.

## Variáveis de ambiente

| Variável | Uso |
|---|---|
| `TERRAS_SKILLS_DIR` | raiz das skills quando não for a pasta vizinha (scripts que chamam outra skill) |
| `TERRAS_IMAGE_KEY` / `TERRAS_IMAGE_ENDPOINT` | chave e endpoint do Model Studio para `terras-banner/scripts/gen_art.py` |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | do Claude Code, não do repositório: orçamento em caracteres da lista de skills (ver "Antes de instalar muitas skills") |

`MIGRACAO.md` registra de onde cada skill veio quando o repositório nasceu.

## Licença

MIT. Veja [LICENSE](LICENSE).

# Versões base e banco de ângulos

Material de Everton Lima, copiado de `/home/support/linkedin/carta-de-apresentacao.md` e ajustado para a regra de tamanho de 250 a 300 palavras.

## Como usar

Você troca três coisas por candidatura:

1. `[Vaga]` — o título exato do anúncio (copie literalmente, inclusive "Staff" ou "Sênior").
2. `[Empresa]` — o nome, usado 2 ou 3 vezes no corpo.
3. A linha `[ÂNGULO]` — conectando sua experiência ao problema daquela empresa. É o único parágrafo que exige 2 minutos de pesquisa, e é o que separa uma carta que funciona de um modelo óbvio.

**Tamanho:** uma página, 250 a 300 palavras.
**Canal:** candidatura em plataforma (Gupy, Lever, Greenhouse) → versão longa. InMail no LinkedIn ou e-mail direto → versão curta, que converte melhor.

## 1. Versão base — inglês (candidatura formal)

Para **Software Architect / Staff Engineer / Senior Backend Engineer**.

```
Dear [Hiring Manager],

You are hiring a [Vaga]. Here is the most relevant thing I have done.

At Montreal Informática I took a monolithic .NET platform apart and rebuilt it as
microservices on Docker Swarm. Infrastructure bottlenecks dropped by roughly 40%.
I built the Azure DevOps pipelines from scratch, which cut deployment time by about
50% and finally made releases boring. The same platform integrates with Gov.BR,
Receita Federal and the Ministry of Justice — systems running at millions of
requests a day that do not forgive sloppy error handling.

More recently, on the consulting side, the pattern repeats: a tax and fiscal
analysis platform at ELEBECE where analysis time fell 80%, a support operation at
ISO 5G Educacional where tickets dropped 40% and we cleared 55% of the improvement
backlog, and a data-collection practice at MERCO.INFO where client project time
came down 75%.

[ÂNGULO]

What I would bring to [Empresa]:

Architecture that survives contact with production. .NET 8/9 (C#, ASP.NET Core),
PHP/Laravel, Clean Architecture, CQRS, DDD, microservices and REST APIs. I have
modernised systems where the alternative was a rewrite nobody had budget for.

Infrastructure cost, not just deploy speed. Docker Swarm, Kubernetes, Traefik,
Nginx, Linux, CI/CD on Azure DevOps, AWS. I treat the monthly cloud bill as part
of the architecture, not as an afterthought.

Applied AI that passes a security review. RAG pipelines, routing requests by task
complexity instead of sending everything to the frontier model, agent governance
with human-in-the-loop on irreversible actions. I write about this publicly:
the best lesson for enterprise AI governance came from CMDB Federation — canonical
authority at the source, derived indexes, never a central copy. I build AI that
survives an audit, not a demo.

Hands-on technical leadership. I was the Technical Lead on a small team — mentoring
developers, setting architecture guardrails, reviewing the decisions that are
expensive to reverse — while still shipping code every week. I have also done
pro bono infrastructure and systems work for a social organisation for over ten
years, which is where I learned to keep things running with nobody watching.

I am based in São Paulo, Brazil (UTC-3), and I am looking for remote Senior/Staff
work — full-time or B2B contract.

If you are hiring for a role where the architecture decisions actually matter, I
would like to talk. I can walk you through the migration decisions, what I would
do differently today, and how I would approach your current bottlenecks.

Best regards,
Everton Lima
Senior Software Architect & DevOps Engineer
linkedin.com/in/limaeverton
```

## 2. Versão curta — inglês (InMail ou e-mail direto)

```
Hi [Nome],

I saw the [Vaga] opening at [Empresa] and I think there is a strong fit.

I am a Senior Software Architect and DevOps Engineer with 10+ years in backend
systems. Most recently I led the migration of a monolithic .NET platform to
microservices on Docker Swarm — roughly 40% fewer infrastructure bottlenecks — and
built the CI/CD pipelines that cut deployment time by ~50%. That platform
integrates with Gov.BR, Receita Federal and the Ministry of Justice at millions of
requests per day. On the consulting side, recent client work cut analysis time by
80% on a tax platform and support tickets by 40% on an education provider.

[ÂNGULO]

I work across .NET 8/9, PHP/Laravel, Docker Swarm, Kubernetes, Azure DevOps and AWS.
I am also hands-on with applied AI: RAG pipelines, LLM routing by task complexity,
and agent governance. Based in São Paulo, Brazil (UTC-3), looking for remote
Senior/Staff work, full-time or B2B.

Would you be open to a short conversation this week?

Best,
Everton Lima
linkedin.com/in/limaeverton
```

## 3. Versão em português

```
Prezado(a) [Nome],

Você está contratando para a vaga de [Vaga]. Aqui está o ponto mais relevante da
minha trajetória.

Na Montreal Informática eu desmontei uma plataforma monolítica em .NET e a
reconstruí como microsserviços em Docker Swarm. Os gargalos de infraestrutura
caíram cerca de 40%. Construí os pipelines de CI/CD em Azure DevOps do zero, o que
reduziu o tempo de deploy em aproximadamente 50%. A mesma plataforma integra
sistemas do Gov.BR, da Receita Federal e do Ministério da Justiça — milhões de
requisições por dia, onde erro de tratamento não passa despercebido.

Mais recentemente, na consultoria, o padrão se repete: uma plataforma de análise
fiscal e tributária na ELEBECE onde o tempo de análise caiu 80%, uma operação de
suporte na ISO 5G Educacional onde os chamados caíram 40% e 55% do backlog de
melhorias foi entregue, e uma prática de levantamento de dados na MERCO.INFO onde o
tempo de projeto dos clientes caiu 75%.

[ÂNGULO]

O que eu levaria para a [Empresa]:

Arquitetura que sobrevive à produção. .NET 8/9 (C#, ASP.NET Core), PHP/Laravel,
Clean Architecture, CQRS, DDD, microsserviços e APIs REST. Já modernizei sistemas
em que a alternativa era uma reescrita que ninguém tinha orçamento para fazer.

Custo de infraestrutura, não só velocidade de deploy. Docker Swarm, Kubernetes,
Traefik, Nginx, Linux, CI/CD em Azure DevOps, AWS. Trato a fatura mensal de nuvem
como parte da arquitetura, não como consequência.

IA aplicada que passa por auditoria. Pipelines de RAG, roteamento de requisições por
complexidade da tarefa, governança de agentes com aprovação humana em ações
irreversíveis. Escrevo sobre isso publicamente: a melhor lição para governança de IA
empresarial veio da CMDB Federation — autoridade canônica na origem, índices
derivados, nunca uma cópia central. Construo IA que sobrevive a uma revisão de
segurança, não a uma demonstração.

Liderança técnica com mão na massa. Fui Technical Lead de um time pequeno —
mentorando desenvolvedores, definindo guardrails de arquitetura e revisando as
decisões caras de reverter — sem parar de escrever código toda semana. Também
mantenho trabalho voluntário de infraestrutura e sistemas numa organização social há
mais de dez anos, que é onde aprendi a manter coisas funcionando sem ninguém olhando.

Estou em São Paulo (UTC-3) e busco trabalho remoto em nível Sênior/Staff — CLT ou
contrato B2B.

Se a vaga exige que as decisões de arquitetura realmente importem, eu gostaria de
conversar. Posso detalhar as decisões da migração, o que eu faria diferente hoje e
como eu atacaria os gargalos atuais de vocês.

Cordialmente,
Everton Lima
Senior Software Architect & DevOps Engineer
linkedin.com/in/limaeverton
```

## 4. Banco de ângulos — escolha um e troque `[ÂNGULO]`

| Se o anúncio pede... | Escreva algo assim |
|---|---|
| **Modernização / legado** | "Reading the description, it sounds like you have a system that works but is expensive to change. That is the exact situation I spent the last three years in — and the migration paid for itself in reduced maintenance time." |
| **Escala / alta disponibilidade** | "The scale you are describing is familiar. The Gov.BR integration I built handles millions of requests a day, which means I have already made the mistake of not designing for idempotency — once." |
| **Custo de nuvem / FinOps** | "If infrastructure cost is on your roadmap, that is where I do some of my best work. I have taken bottleneck reduction and token/inference cost as first-class architecture problems, not as something to fix after launch." |
| **IA aplicada / agentes** | "You are building with LLMs. I build the layer around them: RAG, routing by task complexity, tool permissions and human approval on anything irreversible. The model is the CPU — the operating system around it is what makes it safe in production." |
| **Governança de dados / IA** *(o ângulo mais seu)* | "The most useful lesson I know for enterprise AI came from an older discipline: CMDB Federation. Canonical authority stays at the source, vector stores are derived and disposable, and reconciliation happens in a layer that never duplicates. Most teams are rebuilding the centralized CMDB mistake inside their RAG stack." |
| **Time pequeno / hands-on** | "You need someone senior who still ships. That is how I have worked as Technical Lead: mentoring and setting guardrails without handing off the code." |

## 5. Antes de enviar

- [ ] `[Vaga]` copiado literalmente do anúncio
- [ ] `[Empresa]` preenchido nas 2 ou 3 ocorrências
- [ ] `[ÂNGULO]` trocado por uma linha específica sobre essa empresa
- [ ] `[Nome]` / `[Hiring Manager]` — sem nome, use "Dear Hiring Manager" (nunca "To whom it may concern")
- [ ] Nenhuma métrica nova que não dê para defender em entrevista: os `~40%`, `~50%`, `80%`, `75%`, `100%` e "millions of requests a day" são seus e estão no perfil
- [ ] Uma página, 250 a 300 palavras
- [ ] Palavras-chave literais do anúncio aparecem ligadas a um caso real
- [ ] Fuso declarado: São Paulo, UTC-3, com sobreposição a EUA/Europa
- [ ] Se for em inglês, releia em voz alta — travou em alguma frase, simplifique a frase

## 6. O que NÃO colocar

- **Não repita a lista de tecnologias do perfil.** Você tem 58 competências no LinkedIn; a carta cita ~15 e isso basta.
- **Não peça desculpa por nada.** Nada de "apesar do meu inglês" — o campo está como nível avançado no perfil e a carta demonstra o nível.
- **Não escreva "sou apaixonado por tecnologia".** Seu equivalente forte é o fecho: você assume o problema inteiro, da arquitetura à fatura.
- **Não use a mesma carta para todas as vagas.** O `[ÂNGULO]` é o que faz a diferença.
- **Não feche com súplica.** Nada de "I hope you consider me for this amazing opportunity".

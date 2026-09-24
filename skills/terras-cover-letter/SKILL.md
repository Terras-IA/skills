---
name: terras-cover-letter
description: "Escreve e revisa cartas de apresentação (cover letters) para vagas internacionais e remotas. Use quando o usuário pedir carta de apresentação, cover letter, mensagem de candidatura para empresa de fora, InMail para recrutador, texto para vaga na gringa, ou revisar uma carta existente. Cobre tamanho, estrutura, personalização, tradução de experiência brasileira para valor global e remote readiness."
keywords: [cover letter, carta de apresentação, candidatura, vaga internacional, gringa, remoto, remote, inmail, recrutador, job application]
---

# Cover letter para vagas internacionais

Atue como redator de cover letters para Everton Lima, Senior Software Architect & DevOps Engineer, baseado em São Paulo (UTC-3), candidato a vagas remotas Sênior/Staff. A carta tem um trabalho só: fazer o recrutador abrir o perfil. Não repete o currículo; dá o motivo do contato.

## Onde está instalada

Fonte única: `skills/terras-cover-letter/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Regras duras

1. **Tamanho.** Versão de plataforma (Gupy, Lever, Greenhouse, Ashby): 250 a 300 palavras, uma página. Versão curta (InMail ou e-mail direto): menor ainda. Recrutador lê carta em 20 segundos.
2. **Saudação.** Ache o nome do recrutador (anúncio, LinkedIn, site da empresa) e use "Dear [Nome]"; o nome aumenta a taxa de resposta em até 25%. Sem nome, "Dear Hiring Manager". Nunca "To whom it may concern".
3. **Abertura.** "Lead with relevance, not formality". Nada de "I am excited to apply". Abra com a conquista mais forte ou uma observação específica sobre a empresa. Teste de especificidade: remova o nome da empresa e do cargo. Se o parágrafo continua funcionando, está genérico.
4. **Corpo.** Escolha 1 a 3 experiências mais fortes com número, contadas como história (STAR comprimido, sem rotular as partes). Não repita o currículo; não cubra a carreira inteira.
5. **Traduzir experiência local para valor global.** Recrutador americano/europeu não entende o mercado brasileiro. Explicite o contexto em uma linha (Gov.BR, Receita Federal, Ministério da Justiça, milhões de requisições por dia). Bilinguismo é valor operacional: diga o que o idioma resolveu, nunca apenas "fluent in English".
6. **Remote readiness.** Declare fuso e sobreposição: São Paulo (UTC-3) com overlap para EUA/Europa. Cite hábitos assíncronos concretos (decisões documentadas, comunicação proativa). Só 15% das cartas LATAM mencionam isso, e a omissão derruba callbacks em vaga remota.
7. **Palavras-chave do anúncio.** Use os termos literais da vaga (ex.: "crisis management") e ligue cada um a um caso real seu.
8. **Fechamento.** Proponha um próximo passo concreto ("Would you be open to a short conversation this week?" ou "I can walk you through the migration decisions"). Confiança, nunca súplica: proibido "I hope you consider me". Assine "Best regards" (plataforma) ou "Best" (InMail), nome e LinkedIn.
9. **Proibições.** Repetir a lista de tecnologias do perfil (58 competências no LinkedIn; a carta cita ~15 e basta); adjetivos vazios ("hard-working", "passionate"); bloco pronto de IA sem adaptar; pedir desculpa pelo inglês; reaproveitar a mesma carta entre vagas; "sou apaixonado por tecnologia".

## Fluxo

1. Leia `references/base.md` antes de escrever: contém as três versões base (longa EN, curta EN, PT), o banco de ângulos e o checklist.
2. Da vaga, extraia: título literal do anúncio, nome da empresa e o problema atual dela (2 minutos de pesquisa bastam).
3. Escolha o ângulo do banco que casa com o anúncio, ou escreva um novo no mesmo formato: 1 a 2 linhas conectando a experiência ao problema daquela empresa.
4. Escreva a carta trocando [Vaga], [Empresa], [ÂNGULO] e o nome do recrutador. A base longa atual tem ~400 palavras: aperte para 250 a 300 sem perder as três provas mais fortes.
5. Rode o checklist do `base.md` antes de entregar.
6. Entregue em arquivo `carta-<empresa>-en.md` (ou `-pt.md` se pedir português), texto puro pronto para colar. Se a plataforma pedir um único campo de mensagem de candidatura, entregue a versão curta.

## Fontes das regras

- Na Prática (tamanho, estrutura, personalização): https://napratica.org.br/noticias/cover-letter-como-escrever-uma-carta-de-apresentacao-atraente-para-vagas-internacionais
- LatoJobs (LATAM, experiência local, STAR, remote readiness): https://www.latojobs.com/blog/how-to-write-a-compelling-cover-letter
- Material de origem das versões base: /home/support/linkedin/carta-de-apresentacao.md

---
name: terras-linkedin
description: "Ajuda a escrever posts para LinkedIn. Use quando o usuário pedir para escrever, redigir, revisar ou melhorar um post/texto para LinkedIn, e também quando perguntar sobre alcance, impressões, views ou por que um post rendeu pouco. Use também quando ele colar o post de outra pessoa para responder ou comentar (post a responder, queria comentar, resposta curta ao post dele), mesmo que ele não use a palavra post. Cobre estrutura, hook, tom, CTA, hashtags, distribuição fora da rede, boas práticas da plataforma, resposta a post de terceiro e a regra de zero travessão (em dash), marcador de texto gerado por IA."
keywords: [linkedin, post, escrever, redigir, revisar, comentar, comentário, responder post, post de terceiro, resposta curta, hook, cta, hashtags, travessao, em dash, carrossel, alcance, impressoes, distribuição, views, fora da rede]
---

# Escrever para o LinkedIn

Atue como copywriter especializado em conteúdo para LinkedIn. Ajuda o usuário a escrever posts para LinkedIn — apenas escreve, NÃO publica. O usuário fará o post manualmente.

O objetivo sempre é produzir um post final pronto para copiar e colar, ou revisar/aperfeiçoar um texto que o usuário já escreveu.

## Onde está instalada

Fonte única: `skills/terras-linkedin/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Como usar

Quando o usuário pedir para escrever um post para LinkedIn:

1. **Entenda o contexto** antes de escrever. Pergunte só o que for decisivo e resolva o resto com os defaults da seção seguinte, dizendo em uma linha o que assumiu. Em pedido de alcance, não pare esperando resposta: escolha o fato verificável, escreva e ofereça a variante.
   - Qual o tema?
   - Qual o objetivo (educar, inspirar, gerar debate, announcement)?
   - Qual o tom (casual, técnico, executivo, storytelling)?
2. **Sugira estrutura** de acordo com o objetivo:
   - **Hook** (primeira linha): impactante, curiosa ou polêmica. Decide se alguém para para ler.
   - **Corpo**: 3-5 parágrafos curtos. Uma ideia por linha. Emojis com moderação.
   - **CTA**: pergunta para engajamento, convite para comentar ou call-to-action claro.
3. **Formato de saída** — entregue o post em texto puro, pronto para copiar e colar:
   - Texto do post
   - Sugestão de hashtags (3-5, no final)
   - 1 alternativa de hook (opcional)
   - Variantes quando o diretório pedir mais de um arquivo: `long` é o post completo na banda principal de 1.300 a 1.500 caracteres, `short` tem alvo de 700 caracteres (banda 500 a 700) e não é o long comprimido, e a versão em português acompanha a banda do long. Se o diretório de trabalho tiver AGENTS.md com regras próprias de formato (nomes de arquivo, banda), ele manda nessa parte. A contagem inclui tudo que vai colado no post: texto, bullets e hashtags.

## Preferências padrão (ajustadas pelo autor)

Quando o usuário não especificar objetivo/voz/tom, usar estes defaults:

- **Objetivo:** educar/conectar (big idea) — post de reflexão com tese, não announcement.
- **Voz:** fundador/autor, primeira pessoa.
- **Tom:** storytelling leve — gancho com cena ou contraste, desenvolvimento progressivo, sem jargão corporativo.

## Coerência de argumento (falha que já custou revisão)

- Se o post defende "não treinamos o modelo" (curadoria de contexto vs. treinamento), o fechamento/CTA NÃO pode usar verbos de ensinar/treinar ("ensina ao assistente", "treine o bot") — o próprio texto contradiz a tese. Preferir "plugou", "conecta aos processos", "ativa as skills reais da operação".
- Vocabulário do post inteiro deve espelhar a tese: treinar = estático/caro/alucinação; skills/contexto = curado/sob demanda/auditável.
- Toda vez que o post compartimentar conhecimento ("depto X não vê regra de Y"), acrescentar meia linha de governança/controle de acesso (dados sensíveis) para dar peso institucional — sem inflar o texto.

## Tom humano (regras duras)

- **Proibido usar travessão "—"** (em dash) no texto do post. É o marcador mais
  identificável de texto gerado por IA. Trocar por vírgula, ponto, dois-pontos ou
  simplesmente reescrever a frase.
- Variar tamanho e início das frases. Nunca repetir o mesmo molde em parágrafos seguidos.
- Preferir palavras do dia a dia, voz ativa e precisão em vez de adornos. Se uma
  frase curta resolve, usar a frase curta.

## Revisão de texto existente

Quando o usuário anexar um texto e pedir para revisar ou melhorar:

1. Avalie contra os critérios abaixo (hook, corte de 210 chars, jargão, CTA).
2. Aponte os problemas e entregue uma versão editada do texto do usuário — não um post novo do zero, a menos que o usuário peça.
3. Liste as mudanças-chave em 2-3 bullets (o que mudou e por quê).

## Responder post de terceiro (comentário e post-resposta)

Quando o usuário colar o texto de um post de outra pessoa e pedir para responder, comentar ou reagir, a frase do pedido diz qual dos dois entregáveis ele quer:

- **"post a responder"**: post autônomo no formato de três arquivos do diretório (`post-<slug>-en-long.md`, `-en-short.md`, `-pt.md`), nas bandas de sempre. Ele precisa ficar de pé sozinho, sem o original para fazer sentido, e vale sugerir marcar o autor quando o texto citar o post lido.
- **"queria comentar", "resposta curta ao post dele", "comento o que?"**: comentário para colar no post original agora, entregue em texto puro no chat. Dois tamanhos: principal com alvo em torno de 450 caracteres e mínimo em torno de 250. Se o usuário pedir para guardar, salvar como `comment-<slug>-<lang>.md`.

Regras que valem nos dois casos:

- O idioma segue o post original (post em inglês, resposta em inglês), mesmo que o pedido venha em português.
- Zero travessão, e a seção de tom humano inteira vale aqui também.
- Ângulo que funciona: concordar com a tese, aprofundar com um ponto específico que o original não citou, ancorar em experiência própria (a triagem de service desk com LLM mais regras determinísticas rende um caso concreto) e fechar com pergunta sobre o setup do autor, do tipo "você congela o índice por run ou reconstrói o corpus a cada avaliação?". Pergunta sobre a prática dele puxa resposta curta, que é o que sustenta a conversa.
- Antes de concordar, checar o fato que o post afirma (data, versão, número). Concordar com premissa errada queima mais que discordar.
- Não abrir com elogio genérico e não devolver o vocabulário do autor em espelho. O comentário acrescenta, não parafraseia.
- Os primeiros caracteres precisam fazer sentido sozinhos, porque o comentário também é cortado atrás do "ver mais".
- Comentário não gera impressão para quem comenta. O retorno é perfil, conversa e presença na rede do autor, então não medir por views.

## Imagem do post

Banner, capa, card e og:image saem da skill `terras-banner`, que vale tambem para a Substack: ela gera a arte, monta a tipografia e renderiza no tamanho exato (1200x628 no feed, 1080x1350 em pe). Aqui fica so o texto. O banner acompanha o gancho do post, nao resume o post, e cada idioma tem o proprio.

## Boas práticas LinkedIn

- Posts de 1.300-1.500 caracteres performance melhor (heurística amplamente citada; ajuste ao caso)
- No feed desktop o texto é cortado em ~210 caracteres mostrando "veja mais" — os primeiros ~210 caracteres precisam fazer sentido sozinhos, não só a primeira linha
- "Primeira linha" é o hook — é crucial
- Use "veja mais" como gatilho de curiosidade
- Listas e bullets facilitam a leitura
- Evite links externos (o algoritmo reduz o alcance)
- Finalize com uma pergunta para engajamento
- Hashtags: 3-5, relevantes, no final do post
- Tom autêntico e sem jargão corporativo vazio

## Alcance: o que faz um post sair da rede (medido em set/2026)

O teto de visualizações de uma conta pequena não é limite da plataforma, é o tamanho da rede. Com ~1.176 seguidores, post comum rende 300 a 600 impressões, quase tudo dentro da rede. Volume alto só acontece quando a plataforma passa a distribuir para quem não segue a conta, e essa decisão é tomada post a post.

Caso medido, post sobre o fim de suporte do .NET 8 e .NET 9:

- 22.611 impressões, 15.607 pessoas alcançadas, 0% na rede e 100% fora da rede
- 37 reações, 7 comentários, 2 compartilhamentos, 10 salvamentos
- 42 visualizações de perfil, 9 seguidores vindos do post, 7 recrutadores na semana
- 98 seguidores novos na semana, contra 1 a 3 por dia antes do post
- o estouro não foi no dia da publicação: saiu em 14/09 e a curva virou em 16/09, de 5,6 mil para 23,5 mil impressões acumuladas em um dia
- os dois posts seguintes, no mesmo idioma e na mesma voz, ficaram em 313 e 301 impressões

O que esse post tinha, e os outros não:

1. **Data dura**: prazo que expira e obriga quem usa a tecnologia a agir (fim de suporte, breaking change, descontinuação).
2. **Público grande**: .NET e C# interessam a devs no mundo inteiro. Tema de nicho ou de mercado local fica preso na rede.
3. **Hook com número**: "seu .NET 8 não termina em 2028, termina em 10 de novembro de 2026" entrega valor antes do corte de 210 caracteres.
4. **Material que se salva**: checklist do que verificar antes da data (dependências transitivas, remoções de API, imagens de CI/CD, plano de rollback). Os 10 salvamentos em 37 reações são gente guardando para usar depois.
5. **Pergunta de escolha simples**: "seu stack está no 8, no 10, ou pulou o 9?" rende comentário curto, e conversa sustenta a distribuição.

Quando o pedido for alcance, fazer assim:

- Buscar a data e o fato verificável na fonte antes de escrever (documentação oficial, release notes, changelog). Nunca escrever a data de memória: data errada derruba a credibilidade do post inteiro, e precisão datada é justamente o que gera salvamento e compartilhamento.
- Abrir pelo prazo ou pela consequência, nunca pela apresentação do tema.
- Entregar algo executável: passos, checklist, comparativo, ordem de migração.
- Escrever para quem não te segue, porque a rede sozinha tem teto de algumas centenas.
- Não contar com o idioma: os posts em inglês também ficaram em ~300 impressões. O que decide é o assunto ter motivo para circular fora da rede.
- Conferir a premissa do pedido antes de escrever. Se o prazo que o usuário citou já passou, dizer isso e ancorar o post no prazo que ainda está vivo, em vez de escrever no tom de "vai acabar".
- Não repetir tema já publicado nas últimas semanas, e não usar o caso do .NET como pauta: ele é referência de formato, não assunto.

A plataforma não publica os pesos da distribuição, então isso é leitura dos dados, não regra garantida.

Depois de publicar, conferir na análise do post a divisão "Na rede" e "Fora da rede": 100% na rede indica assunto interno; fora da rede sem volume indica hook fraco ou falta de material salvável. Quando o usuário perguntar por que um post rendeu pouco, pedir nesta ordem: o tema, a divisão na rede e fora da rede, e os salvamentos e comentários. Sem esses três, não afirmar causa: dizer o que a faixa de 300 a 600 sugere e o que ainda falta olhar.

## Critérios de qualidade (self-check antes de entregar)

- Sem jargão corporativo vazio (sinergia, disruptivo, etc.)
- Termina com pergunta ou CTA real, não retórico
- Emojis com moderação, sem poluir a leitura
- CTA coerente com a tese: sem verbo de ensinar/treinar quando o argumento é "não treinamos o modelo"
- Compartimentalização de conhecimento sempre espelhada por governança (quem vê o quê)
- Zero travessões "—" no texto do post
- Frases com tamanho e início variados (não parece template)
- Quando o objetivo incluir alcance: o tema tem data ou fato verificável, e o post entrega algo que o leitor salva (checklist, passo a passo, comparativo)?
- Quando for resposta a post de terceiro: idioma do original, faixa de tamanho do comentário conferida e pergunta final sobre a prática do autor.

## Exemplos de prompt do usuário

- "Escreva um post sobre minha experiência migrando de DevOps para Platform Engineering"
- "Quero postar uma lição que aprendi liderando time remoto"
- "Preciso de um post para anunciar que abri consultoria"
- "Melhora este texto que escrevi para o LinkedIn" (com o texto anexado)
- "post a responder" (com o post de terceiro colado)
- "queria comentar esse post, educado e colaborativo" (com o post colado)

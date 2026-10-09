---
name: terras-linkedin
description: Escreve, revisa e melhora posts para LinkedIn: hook, estrutura, tom, CTA, hashtags, distribuição e resposta a post de terceiro, sem travessão. Use para escrever post, responder ou comentar um post colado, ou entender alcance e impressões de um post.
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

## Digest / recap da semana

- Digest pode ser longo nas duas plataformas da operação: LinkedIn e Substack.
- No LinkedIn, o digest pode passar da banda principal quando estiver mapeando posts já publicados e a versão curta perder valor por compressão.
- O que continua obrigatório: os primeiros ~210 caracteres precisam fazer sentido sozinhos, a leitura precisa funcionar em diagonal, o texto deve agrupar por tema e fechar com pergunta de escolha real.

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
- **lista de 2 ou mais posts para comentar**: skill `terras-comentarios`, que aplica estas mesmas regras no formato curto (até 100 caracteres por post, um por item da lista).

Regras que valem nos dois casos:

- O idioma segue o post original (post em inglês, resposta em inglês), mesmo que o pedido venha em português.
- Zero travessão, e a seção de tom humano inteira vale aqui também.
- Ângulo que funciona: concordar com a tese, aprofundar com um ponto específico que o original não citou, ancorar em experiência própria (a triagem de service desk com LLM mais regras determinísticas rende um caso concreto) e fechar com pergunta sobre o setup do autor, do tipo "você congela o índice por run ou reconstrói o corpus a cada avaliação?". Pergunta sobre a prática dele puxa resposta curta, que é o que sustenta a conversa.
- Antes de concordar, checar o fato que o post afirma (data, versão, número). Concordar com premissa errada queima mais que discordar.
- Não abrir com elogio genérico e não devolver o vocabulário do autor em espelho. O comentário acrescenta, não parafraseia.
- Os primeiros caracteres precisam fazer sentido sozinhos, porque o comentário também é cortado atrás do "ver mais".
- Comentário não gera impressão para quem comenta. O retorno é perfil, conversa e presença na rede do autor, então não medir por views.

## Responder comentários nos seus posts

Comentário pertinente nos seus posts merece resposta, e resposta cedo é o que sustenta a conversa que a plataforma lê (no motor de autoridade, comentário por mil impressões é a métrica principal). Os comentários ficam na página do post ou no link `resultType=COMMENTS` da análise da publicação (a skill `terras-linkedin-metricas` guarda os URNs).

Pertinente é: pergunta técnica, discordância com argumento, experiência concreta do leitor, objeção que outros leitores também podem ter. Não é: elogio genérico, "concordo", emoji, provocação sem conteúdo.

Como responder:

- Responda a pergunta de forma direta primeiro; depois acrescente um ponto que o comentário não cobriu. Mesma regra do comentário a post de terceiro: acrescenta, não parafraseia.
- Discordância educada com dado. Se a objeção revelar ambiguidade no post, reconhecer e precisar vale mais que defender. Se o post errou um fato, corrigir abertamente no comentário: credibilidade vale mais que razão.
- Tamanho: 1 a 3 frases. Pergunta de volta quando a conversa merecer continuar; não perguntar por ritual.
- Idioma do comentário. Zero travessão, e a seção de tom humano vale inteira.
- Elogio genérico: uma frase de agradecimento com algo específico do que a pessoa disse, ou silêncio. Nunca "obrigado!" em série, que infla a thread sem conversa.
- Provocação sem conteúdo: ignorar custa menos que brigar.
- Janela: as primeiras horas são o pico da conversa. Responder depois vale, mas não é o mesmo efeito.
- O que não fazer: responder todo comentário com o mesmo molde, nem usar a resposta para vender (curso, consultoria, newsletter) num post de autoridade.

## Imagem do post

Banner, capa, card e og:image saem da skill `terras-banner`, que vale tambem para a Substack: ela gera a arte, monta a tipografia e renderiza no tamanho exato (1200x628 no feed, 1080x1350 em pe). Aqui fica so o texto. O banner acompanha o gancho do post, nao resume o post, e cada idioma tem o proprio.

## Vídeo do carrossel

O carrossel tem uma segunda versão, narrada: os mesmos slides viram vídeo com uma fala por slide, e quem monta é a `terras-video` (`"formato": "carrossel"`, bloco com `slide`). O texto do post continua sendo o entregável principal; o vídeo é a peça de densidade, do motor de autoridade, não do motor de alcance.

- Fonte dos slides: o deck da `terras-banner`, na variante `linkedin` (`deck-<slug>-linkedin-NN.png`, 1080x1440). Um bloco por slide, na ordem.
- Fala por slide: duas ou três frases, 12 a 18 segundos. A fala acompanha o que o slide mostra, sem repetir o texto da tela. Slide com 25 segundos de fala cansa: a página fica parada tempo demais.
- O roteiro mora ao lado do post (`roteiro-carrossel-<slug>-<lang>.json`) e o texto falado passa pela aprovação dele antes do render, como em qualquer vídeo da casa.
- Pronúncia de termo técnico: o `plan` imprime o relatório de termos em risco, e a escuta antes do render continua valendo (não há checagem automática de pronúncia).
- Vídeo em inglês: o roteiro declara voz própria (padrão `en-US-AvaMultilingualNeural`) e `"sotaque": "nenhum"`, porque o dicionário de respelling do português reescreveria palavra inglesa comum (`cache` viraria `kêsh`). Sigla se escreve com as letras separadas na fala: `Rabbit M Q`, que a voz lê certo (junto, sai "Rabatai Imkay").
- Entrega: mp4 de 1080x1440 (seis slides costumam render 90 a 120 segundos) e os quadros em PNG. As checagens de movimento e de loudness são do `build.py`, em `$SKILL_DIR/../terras-video/`.

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

O teto de visualizações de uma conta pequena não é limite da plataforma, é o tamanho da rede. Com ~1.200 seguidores, o post comum rende três dígitos baixos (a mediana medida de 19 posts, em 29/09/2026, é 114 impressões de tempo de vida), quase tudo dentro da rede. Volume alto só acontece quando a plataforma passa a distribuir para quem não segue a conta, e essa decisão é tomada post a post. A janela fechada em 24/09/2026 marcou +91% de impressões contra a anterior, 85% do alcance fora da rede e +15 seguidores: a conta está sendo distribuída, devagar.

Com 19 posts com coleta de tempo de vida até 29/09/2026, a mediana da conta é 114 impressões e o .NET fez 333 vezes isso. O número mudou porque a amostra deixou de ser o trio do widget e passou a incluir a cauda: a lista de melhores posts da janela enumera 40 posts, e 19 desses já tiveram a página individual coletada. Leitura certa: o .NET não é "um bom post", é um evento fora da escala da conta, e o post comum rende três dígitos baixos. É heurística, não regra.

Caso medido, post sobre o fim de suporte do .NET 8 e .NET 9 (números relidos em 25/09/2026, quase duas semanas depois da publicação):

- 37.999 impressões, 26.390 pessoas alcançadas, 0% na rede e 100% fora da rede
- 54 reações, 10 comentários, 2 compartilhamentos, 17 salvamentos, 1 envio
- 64 visualizações de perfil, 13 seguidores vindos do post
- 98 seguidores novos na semana, contra 1 a 3 por dia antes do post
- o estouro não foi no dia da publicação: saiu em 14/09 e a curva virou em 16/09, de 5,6 mil para 23,5 mil impressões acumuladas em um dia
- o post continuou crescendo por dias: o primeiro registro apontava 22.611 impressões e 15.607 alcançados, e a releitura já mostrava 37.999 e 26.390. Número de post vivo é leitura datada, não veredito
- público do post: 45% Sênior, com Londres e Região no topo de localidade, contra 39% Iniciante na média da conta na mesma semana. O assunto é que escolhe quem chega
- os posts seguintes, no mesmo idioma e na mesma voz, ficaram muito abaixo em alcance: PHP 8.2 com 1.244 impressões e JEV com 388. Com a amostra de 19 (29/09), a mediana da conta é 114: o normal é post de três dígitos baixos, e 19 posts da janela ficaram em 10 impressões ou menos

O que esse post tinha, e os outros não:

1. **Data dura**: prazo que expira e obriga quem usa a tecnologia a agir (fim de suporte, breaking change, descontinuação).
2. **Público grande**: .NET e C# interessam a devs no mundo inteiro. Tema de nicho ou de mercado local fica preso na rede.
3. **Hook com número**: "seu .NET 8 não termina em 2028, termina em 10 de novembro de 2026" entrega valor antes do corte de 210 caracteres.
4. **Material que se salva**: checklist do que verificar antes da data (dependências transitivas, remoções de API, imagens de CI/CD, plano de rollback). Os salvamentos são gente guardando para usar depois.
5. **Pergunta de escolha simples**: "seu stack está no 8, no 10, ou pulou o 9?" rende comentário curto, e conversa sustenta a distribuição.

O que a medição diz sobre esses itens, agora com 13 posts e comparando a mediana dos posts que têm o atributo contra a dos que não têm:

- **Data no hook**: 474 contra 102 impressões (n = 6 e 13), **4,6x**. É o único atributo que separa.
- **Âncora de prazo**: 155 contra 151, **1,0x**. Não separa.
- **Material que se salva**: 150 contra 157, **1,0x**. Não separa.
- **Número no hook**: 157 contra 138,5, 1,1x. Praticamente nada.

Ou seja, a hipótese antiga (prazo mais consequência operacional mais checklist gera distribuição e salvamento) **não se sustenta** na amostra maior, e o material salvável não é o componente medido mais importante. O que se sustenta é mais estreito e mais fácil de errar: **data concreta na primeira linha**. Duas ressalvas que valem: n de 6 contra 13 é sinal, não lei; e como quem abre com data costuma ser o post de mudança de ecossistema, que já tem público maior, a data pode ser sintoma da categoria e não a causa. O que isso muda na escrita: o atributo que mede é o mais fácil de falsificar, então fabricar data no hook fica mais tentador e mais perigoso, porque foi data verdadeira com consequência real que fez o post circular.

### Para alcançar, nesta ordem

1. **Assunto de stack mainstream com prazo verificável na fonte oficial.** É o fator dominante: o post do .NET fez 245x a mediana da conta, e os posts de nicho, na mesma voz e idioma, ficaram entre 61 e 1.244. Alcance vem do tamanho do público do assunto, não do texto.
2. **Data concreta na primeira linha** (3,8x, o único atributo de texto que separou). Verificar a data na fonte antes de escrever, sempre.
3. **Se o prazo contrariar o que o leitor assume, melhor.** Hipótese ainda não medida, com os dois casos que a sustentam: .NET 37.999 e PHP 1.244, ambos com data dura e mesmo idioma. O hook do .NET corrige uma crença errada ("não termina em 2028"); o do PHP só informa. O próximo post de prazo testa isso: se for stack grande, só informar e não estourar, o que pesa é a virada de suposição; se estourar, o que pesa é o tamanho do público.
4. **Não otimizar hashtag, tamanho de texto nem contagem de itens pensando em alcance.** Nada disso separou. Esses itens servem para leitura e para densidade (salvamento, comentário, visita ao perfil), que é o outro motor.
5. **Não julgar em 24 horas.** A curva do post que estourou virou no terceiro dia e seguiu subindo por mais de uma semana. Responder comentário nas primeiras horas (não medido aqui, mas é o sinal que a plataforma lê).
6. **Anotar em cada post novo se ele contraria suposição.** Em uns 6 posts dá para medir a pista fina com amostra de verdade, em vez de ficar na hipótese.

O relatório que fecha essa leitura vive em `/home/support/linkedin/metricas/relatorio-alcance-2026-09-25.md`; a releitura de 29/09 está em `/home/support/linkedin/metricas/analise-2026-09-29.md` (19 posts, mediana 114, separador de data em 4,6x).

## Densidade não é volume: os dois motores

O .NET fez distribuição; o JEV fez densidade. Por mil impressões:

| Post | Engajamentos | Visitas ao perfil | Seguidores |
|---|---|---|---|
| .NET 8 | 2,21 | 1,68 | 0,34 |
| PHP 8.2 | 15,27 | 2,41 | 0,80 |
| JEV | 41,24 | 5,15 | 0 |

388 impressões do JEV com 41 engajamentos por mil é interesse concentrado, não fracasso. A conta opera com dois motores, e nenhum post precisa virar o próximo .NET. **Foco atual (decisão dele em 24/09/2026): motor de autoridade, onde a densidade é maior que o alcance.** Alcance vira consequência, não meta. O scorecard por tipo de post está na `terras-linkedin-metricas` (tags internas + pontuações por mil) e a tabela de 29/09, com 19 posts, confirma: **decisão-de-arquitetura é o tipo a repetir** (327 impressões, 55,0 de densidade, 18,4 de conversa e a maior atração, 9,2 views de perfil por mil, mais 3,1 seguidores por mil, no ADR EN); mudança-com-prazo mediana de 1.254 impressões com densidade 15,2 (distribuição, não conversa); resiliência 103 com 51,6; custo 116,5 com 78,1; meta-conteúdo (digest) 88,5 com 48,5 e só 7,9 de conversa, serviço de leitura e não alavanca.

- **Motor de alcance**: mudança externa que obriga ação (fim de suporte, breaking change, CVE, depreciação, mudança de API ou licença). Formato: data, tecnologia, consequência e ação executável. Métrica principal: alcance e salvamentos.
- **Motor de autoridade**: decisão de engenharia com custo real (ADR, fila, retry, idempotência, cache, observabilidade, auth, incidentes, rollback, LLM em produção). Métrica principal: comentários, salvamentos e visitas ao perfil por mil impressões. O ADR de 24/09 fez 182 impressões de tempo de vida com 5 comentários, proporção que interessa mais que o alcance.

Conteúdo de IA e novidade continua valendo, mas embrulhado como engenharia: começar pelo problema, nunca pelo lançamento. "Seu LLM não precisa gerar texto para decidir" vale mais que "novo modelo passou de 1.900 pontos". A novidade vira consequência de decisão arquitetural, não manchete de produto.

## Qualidade de público vale mais que volume

O post do .NET alcançou 45% Sênior e 41% em engenharia de software, com Londres no topo. O do JEV, 37% Sênior. O do PHP, 44% Iniciante, contra 39% Iniciante na média da conta. Mesmo tema parecido (EOL, runtime), o público não foi o mesmo.

O objetivo declarado é alcance entre Sênior, Staff, arquitetura e liderança de engenharia, no Brasil e no exterior. Impressão bruta engana: comparar posts por mil (engajamento, salvamentos, comentários, visitas ao perfil, seguidores) e olhar também o % Sênior e a localidade.

## O que não fazer

Não fabricar urgência. Número, data e pergunta funcionam no .NET porque existem no problema. Texto nascido de "7 coisas que você precisa saber antes de outubro" mata o formato: vira clickbait e perde o que fez o post funcionar.

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

Na hora de comparar posts, normalizar por mil impressões e olhar o % Sênior e a localidade junto com o número. A tabela boa de leitura é: engajamento, salvamentos, comentários, visitas ao perfil e seguidores, todos por mil; mais a fatia Sênior e o topo de localidade. O arquivo de métricas registra o dia em UTC, então o último dia da janela aparece incompleto em São Paulo (a virada é 21h local): não ler o dia de hoje como queda.

## Medição (skill vizinha)

Escrever é aqui; medir é `terras-linkedin-metricas`. Ela coleta as estatísticas das
páginas de análise (impressões, alcance, na rede e fora da rede, salvamentos, views de
perfil, seguidores e demografia), guarda histórico e monta o diagnóstico de por que cada
post rendeu ou não. Quando o pedido for análise de desempenho, relatório, comparação
entre posts ou "por que este post não rendeu" com números, é lá; quando o pedido for o
texto, é aqui. O que a medição confirmar volta para cá como formato a repetir.

## Critérios de qualidade (self-check antes de entregar)

- Sem jargão corporativo vazio (sinergia, disruptivo, etc.)
- Termina com pergunta ou CTA real, não retórico
- Emojis com moderação, sem poluir a leitura
- CTA coerente com a tese: sem verbo de ensinar/treinar quando o argumento é "não treinamos o modelo"
- Compartimentalização de conhecimento sempre espelhada por governança (quem vê o quê)
- Zero travessões "—" no texto do post
- Frases com tamanho e início variados (não parece template)
- Quando o objetivo incluir alcance: o tema tem data ou fato verificável, e o post entrega algo que o leitor salva (checklist, passo a passo, comparativo)?
- Motor de alcance: data verificável, consequência operacional e material salvável, nessa ordem de prioridade
- Motor de autoridade: problema real, custo, decisão, trade-off e mecanismo de governança, sem precisar dizer que é sênior
- Tema de IA ou novidade: o texto começa pelo problema, nunca pelo lançamento? A novidade entra como consequência, não como manchete?
- Urgência é do problema, não do texto: sem número ou data fabricados para chamar atenção
- Quando for resposta a post de terceiro: idioma do original, faixa de tamanho do comentário conferida e pergunta final sobre a prática do autor.

## Exemplos de prompt do usuário

- "Escreva um post sobre minha experiência migrando de DevOps para Platform Engineering"
- "Quero postar uma lição que aprendi liderando time remoto"
- "Preciso de um post para anunciar que abri consultoria"
- "Melhora este texto que escrevi para o LinkedIn" (com o texto anexado)
- "post a responder" (com o post de terceiro colado)
- "queria comentar esse post, educado e colaborativo" (com o post colado)
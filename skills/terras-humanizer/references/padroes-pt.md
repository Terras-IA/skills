# Catálogo de padrões de texto de IA em português

Referência da skill `terras-humanizer`. Cada padrão traz os sinais, o problema e um par antes/depois. Os padrões estão numerados do mais forte para o mais fraco: os de A e B justificam edição com um avistamento; os marcados **(fraco sozinho)** precisam de companhia de outros vícios no mesmo trecho para valer ação.

---

## A. Encenar em vez de afirmar

### 1. "Não é X, é Y"

**Sinais:** "não é apenas X, é Y", "não se trata de X, mas de Y", "não é só Y, é Z", "não somente... mas também", "mais do que X, é Y", o mesmo contraste partido em duas frases ("Isso não significa X. Significa Y."), e a cauda negativa ("sem adivinhação", "sem achismo").

**Problema:** a metade negativa nomeia algo que ninguém afirmou, então a positiva parece maior sem acrescentar afirmação. Diga o ponto direto. Mantenha o contraste só quando a negativa corrige crença real do leitor.

**Antes:**
> Não é apenas uma questão de performance, é uma questão de confiança.

**Depois:**
> A lentidão derruba a confiança de quem usa o sistema.

**Antes (partido em duas frases):**
> Isso não quer dizer que toda escolha é igual. Quer dizer que não existe um sistema externo que confirme qual está certa.

**Depois:**
> Nenhum sistema externo confirma qual escolha está certa, ainda que as escolhas tenham consequências diferentes.

### 2. Fecho de uma linha e fragmento dramático

**Sinais:** parágrafo de uma frase que repete o anterior; "É isso que importa de verdade."; "Leia de novo."; "Deixe isso assentar."; o mesmo fecho depois de várias seções; fileira de fragmentos ("Sem estética prévia. Sem nostalgia."); palavra em CAIXA ALTA ou com ponto entre letras (cada. santo. dia.).

**Problema:** a linha pede pausa em vez de acrescentar. Frase curta pode ter ênfase quando traz fato novo. Corte o fecho que repete; junte a fileira de fragmentos numa frase específica.

**Antes:**
> O cache corta trabalho repetido.
>
> É isso que importa de verdade.
>
> O retry esconde falha breve.
>
> É isso que importa de verdade.

**Depois:**
> O cache corta trabalho repetido.
>
> O retry esconde falha breve.

**Antes (fragmentos):**
> A ferramenta chegou sem pedir simetria. Sem preferência estética. Sem respeito pelo gosto humano.

**Depois:**
> A ferramenta chegou sem favorecer simetria nem desenho com cara humana, o que enfraqueceu premissas antigas de design.

### 3. Ditados que soam profundos

**Sinais:** "a verdadeira questão é", "no fundo", "na essência", "o que realmente importa", "em última análise", "o cerne da questão", "a linguagem de", "a moeda de", "a arquitetura de", "X vira uma armadilha", "X não é uma ferramenta, é um espelho".

**Problema:** ponto comum vestido de verdade oculta, e o vestido não acrescenta detalhe. Troque pelo que está sendo dito.

**Antes:**
> A verdadeira questão é se o time consegue se adaptar. No fundo, o que realmente importa é a prontidão organizacional.

**Depois:**
> A questão é se o time consegue se adaptar. Isso depende de a organização estar disposta a mudar hábitos.

### 4. Aquecimento antes do ponto

**Sinais:** "vamos mergulhar", "vamos explorar", "vamos destrinchar", "aqui está o que você precisa saber", "sem mais delongas", "vale destacar que", "é importante ressaltar", "antes de tudo", "olha só", "sinceramente?", "a real é que".

**Problema:** o texto anuncia que vai dizer, ou encena um momento de sinceridade, em vez de dizer. Corte a corrida de aproximação inteira. "Sinceramente" dentro de uma frase casual é hábito humano; o vício é o abridor sozinho antes de afirmação rotineira.

**Antes:**
> Vamos mergulhar em como o cache funciona no Next.js. Aqui está o que você precisa saber.

**Depois:**
> O Next.js guarda dados em várias camadas: memoização de requisição, cache de dados e cache de roteador.

### 5. Briga com ninguém

**Sinais:** "não estou dizendo que", "para deixar claro", "não me entenda mal", "isso não quer dizer que", "alguém poderia argumentar que", "uma abordagem tentadora seria", "pode-se pensar que... mas", "seria fácil simplesmente".

**Problema:** o texto responde a objeção que não aparece em lugar nenhum, sobra de rascunho anterior. Remova a defesa; se ela carrega afirmação real, afirme-a. Várias rejeições seguidas são sinal mais forte que uma.

**Antes:**
> Isso não é principalmente sobre tamanho de prompt, e não estou dizendo que documentação não importa. Dá para categorizar o problema de outro jeito, mas a questão é se o agente consegue usar a instrução quando age.

**Depois:**
> A questão é se o agente consegue usar a instrução quando age.

---

## B. Ritmo por regra

Uma pessoa pode fazer qualquer um destes de propósito, então os mais fracos precisam de companhia.

### 6. Trios forçados

**Sinais:** ideias em três para parecer completo ("inovação, inspiração e insights"), três exemplos paralelos, três fatos curtos seguidos de lição.

**Problema:** o trio sugere completude que o conteúdo não tem. Verifique se cada item acrescenta ideia distinta. Junte exemplos, desenvolva o mais forte ou varie a estrutura. Mantenha os três quando o conteúdo realmente tiver três partes.

**Antes:**
> O evento tem palestras, painéis e oportunidades de networking. O participante encontra inovação, inspiração e conhecimento de mercado.

**Depois:**
> O evento tem palestras e painéis, além de tempo para conversa informal entre as sessões.

### 7. Aberturas repetidas

**Sinais:** várias frases seguidas começando com o mesmo sujeito, quase sempre "ele" ou "ela", porque a repetição é tratada por regra em vez de ouvido.

**Problema:** soa mecânico. Junte as frases, troque o sujeito ou comece pela ação. Não é proibido repetir a palavra: escritor repete abertura de propósito para ritmo.

**Antes:**
> Ela notou a porta. Ela notou a fechadura. Ela guardou as duas informações.

**Depois:**
> Ela notou a porta e a fechadura, e guardou as duas informações.

### 8. Travessão como conectivo universal

**Regra:** o texto final não pode conter travessão (—) nem meia-risca (–) usados como travessão, a menos que a amostra de voz do autor use; nesse caso, iguale a frequência da amostra. Isso inclui travessão espaçado e hífen duplo (` -- `). Hífen dentro de código, comando, caminho e URL fica intacto.

**Problema:** o travessão deixa o escritor pular a escolha de como as duas orações se relacionam, então o modelo recorre a ele em todo lugar. Muitos editores usam travessão, então um sozinho é **(fraco sozinho)**; texto cheio deles não é.

**Antes:**
> A nova política — anunciada sem aviso — afeta milhares de trabalhadores. As mudanças -- há muito esperadas -- valem a partir de hoje.

**Depois:**
> A nova política, anunciada sem aviso, afeta milhares de trabalhadores. As mudanças, há muito esperadas, valem a partir de hoje.

### 9. Qualificadores empilhados

**Sinais:** "pode potencialmente", "poderia talvez", "é possível que em alguns casos", "em certa medida", "de certa forma", "arrisco dizer que".

**Problema:** edição em cima de edição empilha ressalva até toda afirmação parecer incerta, geralmente para consertar exagero anterior em vez de reportar dúvida real. Mantenha qualificador quando a fonte sustenta e o sentido pede. "Talvez" e "costuma" são hábitos humanos, não vício. **(fraco sozinho)**

**Antes:**
> Poderia potencialmente ser argumentado que a política talvez tenha algum efeito sobre os resultados.

**Depois:**
> A política pode afetar os resultados.

### 10. Compostos com hífen em toda posição

**Sinais:** em inglês, "third-party", "cross-functional", "client-facing", "data-driven", "well-known", "high-quality", "real-time", "long-term", "end-to-end" hifenizados em qualquer posição da frase. Em português, o equivalente é o acúmulo de compostos por hífen onde a norma dispensa o sinal.

**Problema:** o hífen fica onde a gramática não pede. Mantenha quando a norma exigir, como em "relatório de alta qualidade" (sem hífen, aliás) ou no composto que a gramática pede; tire quando não. **(fraco sozinho)**

### 11. Voz passiva e sujeito oculto

**Sinais:** "não é necessária configuração", "os resultados são preservados automaticamente", "foi decidido que".

**Problema:** o texto esconde quem age. Prefira voz ativa quando ela deixa ator e ação mais claros. **(fraco sozinho)**

**Antes:**
> Não é necessária configuração. Os resultados são preservados automaticamente.

**Depois:**
> Você não precisa configurar nada. O sistema preserva os resultados automaticamente.

---

## C. Inflação e autoridade emprestada

O fato embaixo costuma ser verdadeiro. Mantenha o fato e tire a roupa.

### 12. Palavras de IA em português

**Lista com substituto:**

| Palavra ou expressão | Em vez disso |
|---|---|
| adicionalmente, além disso (abrindo frase) | e, também, ou nada |
| crucial, fundamental, essencial | diga o que acontece se faltar |
| robusto, abrangente, completo | descreva o que cobre |
| cenário, panorama, landscape | mercado, área, situação |
| desempenha um papel crucial | o que ele faz, em verbo |
| vale destacar, é importante ressaltar | corte, e afirme |
| em suma, em conclusão, por fim | corte |
| dessa forma, diante disso, nesse sentido (em série) | então, por isso |
| mergulhe, desvende, desbloqueie, eleve, potencialize | diga a ação concreta |
| transformador, revolucionário, disruptivo | diga o que mudou |
| testemunho de, um marco para | diga o fato e a data |
| vem ganhando destaque, tem se tornado cada vez mais | diga o número |
| rico, vibrante, profundo (figurado) | diga o que tem |
| meticuloso, intricado, vibrante (texto EN: meticulous, intricate) | palavra simples |

**Problema:** modelo usa estas palavras muito mais que pessoas, sobretudo em grupo. Esta é a única lista de vocabulário do catálogo: palavra formal fora dela não é vício por si.

**Antes:**
> Adicionalmente, um aspecto crucial da culinária local é o consumo de carne de camelo, um testemunho duradouro da influência histórica da região, demonstrando como esses pratos se integraram ao panorama gastronômico.

**Depois:**
> A culinária local também inclui carne de camelo, considerada iguaria. Pratos de massa, trazidos na colonização, seguem comuns, principalmente no sul.

### 13. Significância inflada

**Sinais:** "marca um momento decisivo", "desempenha papel-chave", "reflete uma tendência mais ampla", "deixa um legado duradouro", "prepara o terreno para", "apesar dos desafios, segue prosperando", seção "Desafios e Perspectivas", "o futuro promissor", "tempos empolgantes".

**Problema:** fato comum apresentado como marco, prova de legado ou promessa de futuro. O truque aparece em três escalas: na frase, na seção de praxe e no parágrafo de despedida. Mantenha o fato, tire a significância. Termine no último fato concreto.

**Antes:**
> O instituto foi criado em 1989, marcando um momento decisivo na evolução da estatística regional e refletindo um movimento mais amplo de descentralização administrativa.

**Depois:**
> O instituto foi criado em 1989, parte de uma descentralização mais ampla das funções administrativas no país.

**Antes (despedida):**
> O futuro parece promissor. Tempos empolgantes se aproximam enquanto a empresa segue sua jornada rumo à excelência.

**Depois:**
> (Corte o parágrafo. Termine no último fato concreto.)

### 14. Conexão vaga

**Sinais:** "associado a", "ligado a", "conectado a", "relacionado a", "em conexão com".

**Problema:** o texto diz que duas coisas se ligam sem dizer como. "Associado à liderança da empresa" esconde se a pessoa era diretora, conselheira ou consultora. Nomeie a relação que a fonte dá; se a fonte não diz, mantenha o vago em vez de inventar o papel.

**Antes:**
> Ele é associado à orquestra, que fundou e rege.

**Depois:**
> Ele fundou e rege a orquestra.

### 15. Gerúndio pendurado

**Sinais:** frase terminando em "garantindo", "proporcionando", "permitindo", "refletindo", "demonstrando", "destacando", "contribuindo para", "promovendo", "englobando", "simbolizando", "evidenciando". Em inglês, o mesmo com "-ing" (highlighting, underscoring, ensuring).

**Problema:** o gerúndio é pendurado num fato simples para dar profundidade. Colar numa fonte citada ("o autor destacou a influência duradoura") não torna o acréscimo verdadeiro. Mantenha o fato; mantenha o gerúndio só quando a fonte sustenta o que ele afirma.

**Antes:**
> A paleta de azul, verde e dourado dialoga com a beleza natural da região, simbolizando as flores do campo, o litoral e as paisagens diversas, refletindo a conexão profunda da comunidade com a terra.

**Depois:**
> O templo é pintado de azul, verde e dourado, cores escolhidas para lembrar as flores do campo e o litoral.

### 16. Linguagem de venda

**Sinais:** "exemplifica", "compromisso com", "belezas naturais", "encravado em", "no coração de", "renomado", "de tirar o fôlego", "imperdível", "solução robusta", "plataforma completa".

**Problema:** o texto vira anúncio, sobretudo sobre lugar, cultura, produto ou empresa. Diga o que a coisa é.

**Antes:**
> Encravada na região de Gonder, na Etiópia, Alamata Raya Kobo se destaca como uma cidade vibrante, de rica herança cultural e belezas naturais de tirar o fôlego.

**Depois:**
> Alamata Raya Kobo é uma cidade na região de Gonder, na Etiópia.

### 17. Autoridade emprestada

**Sinais:** "especialistas afirmam", "observadores apontam", "relatórios de mercado indicam", "alguns críticos", "diversas publicações"; lista de veículos de prestígio para sustentar uma pessoa; "presença ativa nas redes, com mais de N seguidores".

**Problema:** um nome ou autoridade sem nome ocupa o lugar do que foi dito. Quando a fonte real e o que ela disse existem, use isso. Senão, corte a afirmação ou a lista. Nunca invente fonte. Falta de citação sozinha não é vício: a maior parte do que se escreve não cita.

**Antes:**
> Por suas características únicas, o rio interessa a pesquisadores e conservacionistas. Especialistas acreditam que ele cumpre papel crucial no ecossistema regional.

**Depois:**
> Pesquisadores e conservacionistas estudam o rio por suas características incomuns.

### 18. Fugir de "é", "está" e "tem"

**Sinais:** "atua como", "figura como", "se configura como", "representa um", "conta com", "dispõe de", "possui" onde caberia "tem", "refere-se a".

**Problema:** verbo simples trocado por perífrase maior. Use é, está, tem.

**Antes:**
> A galeria atua como espaço de exposição de arte contemporânea. O espaço conta com quatro salas e dispõe de mais de 300 metros quadrados.

**Depois:**
> A galeria é o espaço de exposição de arte contemporânea. O espaço tem quatro salas, com mais de 300 metros quadrados no total.

---

## D. Formatação por regra

Templates e editores visuais também produzem formatação limpa demais. O vício é decoração em todo item.

### 19. Negrito decorativo

**Sinais:** palavras em negrito sem motivo; lista em que todo item tem rótulo em negrito seguido de dois-pontos.

**Problema:** o negrito vira enfeite e o rótulo não carrega informação própria. Tire o negrito. Transforme lista rotulada em prosa quando os rótulos não dizem nada.

**Antes:**
> A atualização atingiu **Experiência do Usuário**, **Performance** e **Segurança**.

**Depois:**
> A atualização mexeu na interface, no tempo de carregamento e na criptografia.

### 20. Títulos decorativos

**Sinais:** título com toda palavra em maiúscula, emoji ou seta (→) enfeitando título e item de lista, linha horizontal entre cada seção, documento abrindo com título que repete o próprio nome.

**Problema:** decoração no lugar de hierarquia. Use caixa de frase, tire o enfeite e a linha, e deixe o título aparecer uma vez.

**Antes:**
> 🚀 **Fase de Lançamento:** O produto chega no terceiro trimestre
> 💡 **Insight-chave:** o usuário prefere simplicidade

**Depois:**
> O produto chega no terceiro trimestre. A pesquisa com usuários mostrou preferência por simplicidade.

### 21. Aspas curvas

**Sinais:** aspas curvas (“...”) onde o autor ou o formato usa aspas retas ("...").

**Problema:** a maioria dos editores converte automaticamente, então é **(fraco sozinho)**. Corrija quando o formato de destino usar aspas retas, como código, terminal e alguns CMS.

---

## E. Sobras do chat e do rascunho

Estas se removem direto. Nenhuma precisa de reescrita.

### 22. Resíduo de chatbot

**Sinais:** "Espero ter ajudado", "Claro!", "Certamente!", "Ótima pergunta!", "Você está absolutamente certo", "Gostaria que eu...", "Quer que eu continue?", "me avise", "aqui está um resumo de".

**Problema:** saudação, elogio, oferta ou despedida de chatbot ficaram no texto que deveria se sustentar sozinho. É o vício mais certo da lista e o mais fácil de passar batido quando envolve conteúdo real. Remova o envoltório e mantenha o conteúdo.

**Antes:**
> Ótima pergunta! Aqui está um resumo da Revolução Francesa. Ela começou em 1789, quando a crise financeira e a falta de alimentos levaram à revolta. Espero ter ajudado! Me avise se quiser que eu detalhe alguma parte.

**Depois:**
> A Revolução Francesa começou em 1789, quando a crise financeira e a falta de alimentos levaram à revolta.

### 23. Aviso de limite de conhecimento e chute

**Sinais:** "até meu último treinamento", "com base nas informações disponíveis", "não disponível publicamente", "não amplamente documentado", "mantém um perfil discreto", "provavelmente cresceu em", "acredita-se que".

**Problema:** o texto avisa onde o conhecimento do modelo acaba, ou admite que não achou fonte e preenche a lacuna com suposição plausível. Diga o que a fonte não mostra, ou remova a frase. Nunca apresente chute como fato.

**Antes:**
> Como os detalhes sobre a fundação da empresa não estão amplamente documentados, ela parece ter sido criada em algum momento dos anos 1990.

**Depois:**
> A data de fundação da empresa não está documentada nas fontes disponíveis. (Ou corte a frase.)

### 24. Título repetido na primeira frase

**Problema:** o título é seguido de um parágrafo de uma linha que o repete antes do conteúdo começar. Remova a frase repetida.

**Antes:**
> ## Performance
>
> Velocidade importa.
>
> Quando a página demora, o usuário vai embora.

**Depois:**
> ## Performance
>
> Quando a página demora, o usuário vai embora.

### 25. Texto sobre a versão anterior

**Problema:** documentação e comentário descrevem o que substituíram em vez do comportamento atual. Mencione a versão anterior só em changelog, release notes e guia de migração.

**Antes:**
> Esta função foi adicionada para substituir a abordagem anterior, que percorria todos os itens e causava desempenho O(n²).

**Depois:**
> Esta função usa tabela hash para busca O(1), evitando o custo O(n²) da iteração ingênua.

---

## Quando não agir

Cada padrão descreve uma escolha padrão, e uma pessoa pode fazer qualquer uma delas de propósito. Aja num vício **(fraco sozinho)** só quando vários aparecerem no mesmo trecho. Deixe a expressão suspeita em paz quando estiver dentro de citação, título, nome próprio, ou num trecho que discute a expressão em vez de usá-la. Saudação e despedida de carta e comentário existem antes de chatbot. Texto escrito antes de 30 de novembro de 2022 não é texto de IA. Quem julga por sensação acerta pouco mais que o acaso, e escrita humana vai absorvendo hábitos de IA: vários vícios juntos são a salvaguarda.

Mantenha os detalhes que carregam a voz, a menos que atrapalhem o sentido:

- Detalhe específico e incomum: endereço real, citação estranha, "o advogado que trabalhava em cima do consultório do meu dentista".
- Sentimento misturado e tensão não resolvida: "acho isso bom, mas me incomoda, e não consigo explicar bem".
- Referência datada: gíria, meme e piada interna de um ano e uma subcultura específicos.
- Escolha em primeira pessoa que o autor consegue explicar.
- Parêntese ou autocorreção genuína: "(eu ia escrever 'quase', mas foi certeiro)".

## Fonte

Padrões derivados de ["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), da WikiProject AI Cleanup, e da skill `blader/humanizer` (MIT). Exemplos e lista de vocabulário adaptados para o português.

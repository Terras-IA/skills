# Descoberta — o que perguntar antes de construir

O pedido chega assim: *"quero um app sobre X"*. Falta quase tudo. Este roteiro é o
que separa um app que as pessoas usam de um app bonito que ninguém abre duas vezes.

Pergunte em rodadas de 3–4, **sempre com uma recomendação
marcada** — quem pediu o app costuma não ter a resposta pronta, e uma opção sugerida
faz a conversa andar. Nunca despeje as 20 perguntas de uma vez.

## Bloco 1 — O que o app é (sem isso não há app)

**1. Qual é a promessa, em uma frase?**
A frase que a pessoa repetiria para outra. "Investigue o que existe por trás do
comportamento do seu filho" é uma promessa. "Um app de parentalidade" não é.
> Por que: é o critério de corte de toda decisão seguinte. Tela que não serve à
> promessa não entra.

**2. Qual é a única ação central?**
O verbo que a pessoa executa. Registrar um episódio. Calcular um preço. Montar um
orçamento. Se houver duas ações centrais, provavelmente são dois apps.
> Por que: define a tela inicial e o fluxo que precisa funcionar antes de qualquer
> outro.

**3. Quando a pessoa abre o app?**
O ritual: na hora do conflito, todo domingo à noite, no fim do mês, no fechamento.
Com que frequência, em que estado emocional, com quanto tempo livre e com quanto
sinal de internet.
> Por que: um app usado no meio do caos precisa de caminho curto e alvos grandes; um
> usado no domingo à noite pode ter leitura longa. Isso muda layout, não só cor.

**4. Como se sabe que funcionou?**
Um sinal observável. "Ela volta a registrar na semana seguinte." "Ela leva o resumo
para a consulta."
> Por que: sem isso não há como decidir o que cortar na v1, e a v2 vira palpite.

## Bloco 2 — Público

**5. Quem é a pessoa que usa?** Idade aproximada, contexto, o que ela já tentou antes.
**6. O que ela **não** é?** (ex.: não é profissional de saúde, não é técnica, não é
nativa digital) — isso define o vocabulário permitido.
**7. Nível de letramento digital e de leitura.** "Precisa funcionar para alguém
cansado, no celular, às 23h?" é uma pergunta melhor que "qual a escolaridade?".
**8. Idioma e variante.** pt-BR, com acentos preservados sempre.

## Bloco 3 — Sensibilidade e limite ético

**9. O assunto toca saúde, criança, dinheiro, luto ou religião?**
> Se sim: `references/lgpd-e-etica.md` passa a ser obrigatório antes de construir, e
> os disclaimers entram na primeira tela — não no rodapé do "Sobre".

**10. O app guarda dado de criança ou de terceiro?**
> Dado de criança é sensível na LGPD (art. 14). Mesmo local-first, isso exige
> minimização e uma política escrita.

**11. O que o app **não** pode prometer?**
Escreva literalmente a lista. "Não diagnostica", "não substitui acompanhamento",
"não garante emagrecimento", "não é consultoria jurídica".
> Por que: essa lista vira o disclaimer e o crivo de cada frase da copy.

## Bloco 4 — Conteúdo e autoria

**12. De onde vem o conteúdo?** Aula, livro, transcrição, especialista, base própria.
**13. Quem valida o conteúdo antes de publicar?** **Nome e papel.**
> Por que: foi a pendência P0 do primeiro app — conteúdo derivado de uma aula ficou
> esperando o aval da autora. Descubra isso na fase 1, não na véspera de publicar.
> Enquanto não houver aval, produção fica protegida/adiada.

**14. O conteúdo já existe estruturado (planilha, PDF, markdown)?** Se sim, derivar
dele em vez de inventar — e dizer de onde veio, com crédito.

## Bloco 5 — Marca e identidade

**15. Qual marca?** Existe identidade estabelecida? Procure você mesmo antes de
perguntar: `docs/marca/`, `docs/stitch/`, `**/tokens.css`, logos, repositórios vizinhos.
**16. Se não existir:** o Google Stitch está acessível? (ver
`references/identidade-visual.md`) Se não, gerar paleta e símbolo do zero.
**17. Nome do app e do pacote** (`appId`). Decida agora: no iOS não muda depois.

## Bloco 6 — Arquitetura e operação

**18. O dado sai do aparelho?** O default é **não**. Se sim, por quê, e quem opera.
> Qualquer resposta "sim" aqui multiplica obrigação legal, custo e superfície de falha.
> Force a decisão consciente e registre o motivo no README.

**19. Precisa funcionar offline?** Default sim (é o que faz o PWA valer a pena).
**20. Vai para as lojas ou fica no PWA?** Se lojas: prazo, e quem tem Mac/Xcode para o iOS.
**21. Quem publica e em qual conta** (Vercel, time/organização).

## Bloco 7 — Negócio (quando é produto, não ferramenta interna)

**22. Como isso gera valor?** Venda direta, isca para um serviço, brinde, retenção.
**23. O app é a entrega ou é a porta?** Se for porta, o app precisa levar a algum
lugar — e isso muda a tela final.
**24. Preço, se houver.** Se for pago, a copy muda de tom e o app precisa de política
de reembolso coerente com a lei.

Depois disso vá para `references/copy-e-persuasao.md`: as respostas de 4, 6, 8, 11,
22 e 23 são exatamente a matéria-prima da copy.

## Enquadramento — escreva antes de perguntar

Antes de abrir a entrevista, escreva três linhas e mostre ao usuário para conferência:

```text
Problema: <o que dói, para quem>
Promessa: <a frase>
O app faz: <a ação central e o ritual>
```

Se você não consegue escrever as três linhas a partir do que já foi dito, o que falta
é escopo — e a primeira pergunta é sobre escopo, não sobre cor.

## Como fechar a fase

Consolide tudo num bloco curto e cole na conversa **para o usuário confirmar antes de
você escrever código**. Depois grave em `README.md` as partes duráveis (promessa,
público, arquitetura, quem valida) e em `BACKLOG.md` o que ficou pendente.

---
name: terras-humanizer
description: "Reescreve texto com cara de IA para soar humano, sem mudar o que ele diz e sem inventar nada. Use para revisar ou editar prosa com marcas de IA em português ou inglês: contraste 'não é X, é Y', frase de efeito de uma linha, abertura encenada, trio forçado, travessão em excesso, hipérbole, linguagem de venda, jargão de IA, negrito decorativo, gerúndio pendurado. Humanize text, remove AI writing tells, edit AI-sounding prose."
keywords: [humanizar, humanizer, texto de IA, AI writing, marcas de IA, revisão, edição, prosa, português, inglês]
---

# Humanizer: tirar as marcas de texto de IA

## Objetivo

Reescrever texto que soa gerado por IA para soar escrito por uma pessoa, mantendo o que ele diz. Não é reescrever por gosto: é editar prosa por sinais objetivos, com critério declarado.

## Onde está instalada

Fonte única: `skills/terras-humanizer/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Quando usar e quando não usar

Use para texto em geral: e-mail, carta, artigo, documentação, README, proposta, mensagem, roteiro, post fora do LinkedIn.

**Para post de LinkedIn, as regras de `terras-linkedin` mandam** (formato, bandas de caracteres, hook, CTA, três arquivos). Esta skill pode limpar o texto depois de escrito, mas não substitui aquela.

## As duas regras invioláveis

1. **Não invente.** Nenhum fato, nome, número, data, citação ou link que não esteja no texto original ou no que o usuário forneceu. Se uma frase precisa de um detalhe que você não tem, pergunte ou escreva uma frase mais simples. Opinião e reação cabem quando a voz pede; fato inventado não cabe nunca.
2. **Amostra de voz do autor vence tudo.** Se o usuário der um texto dele, leia antes e iguale tamanho de frase, escolha de palavra, pontuação e aberturas. A amostra passa por cima dos padrões abaixo, inclusive o do travessão.

## Como trabalhar

1. **Marque os sinais.** Leia o texto inteiro uma vez e aponte cada padrão que encontrar, do mais forte para o mais fraco. Olhe o formato do parágrafo, não só a frase: contraste espalhado em duas frases, três exemplos paralelos e o mesmo fecho depois de cada seção são o mesmo vício em escala maior.
2. **Rascunhe a reescrita.** Mantenha toda afirmação sustentada pelo original. Pode encurtar trecho monótono, juntar ou separar parágrafos e mudar a estrutura, mas preserve a informação.
3. **Confira o rascunho.** Leia em voz alta. Pergunte o que ainda soa artificial. Verifique se a reescrita acrescentou ou perdeu fato, nome, número, data, citação ou relação de causa. Acrescentar sem base é erro; perder afirmação também é erro, salvo quando o padrão manda cortar. Depois procure os cinco vícios que mais sobrevivem a uma reescrita: contraste "não é X, é Y", fecho de uma linha, travessão, trio e rótulo em negrito.
4. **Escreva a versão final.** Diga cada ponto de forma natural em vez de remendar frase por frase. Se uma frase continua travada, reescreva o parágrafo em volta do ponto principal. Varie o tamanho das frases: texto humano alterna curta e longa.

## Voz

Sem amostra, tire a voz do tipo de texto. Artigo, ensaio, opinião e texto pessoal mantêm opinião, dúvida, humor e parênteses do autor, e você pode acrescentar uma reação onde ele reagiria. Texto técnico, jurídico, de referência e factual fica neutro e direto. Tirar os vícios é metade do trabalho; a outra metade é o resultado continuar soando como uma pessoa.

## O que devolver

- **Texto colado (padrão)**: a análise curta dos padrões encontrados e a reescrita final.
- **Modo arquivo**: quando o usuário indicar um arquivo, rode o processo inteiro, mas escreva só o texto final nele. Mude apenas prosa. Bloco de código, código inline, comandos, caminhos, metadados YAML, dados e destinos de link ficam intactos. Depois, um resumo curto.
- **Modo embutido**: quando outra tarefa usar esta skill (mensagem de commit, descrição de PR, documento), devolva só o texto final.

## Os padrões mais fortes

Estes cinco justificam edição com um único avistamento. Ação imediata, sem esperar companhia.

1. **"Não é X, é Y"** (e a versão partida em duas frases, ou "não apenas X, mas também Y"). A metade negativa nomeia algo que ninguém afirmou, então a positiva parece maior. Diga o ponto direto. Mantenha o contraste só quando a negativa corrige uma crença real do leitor.
2. **Fecho de uma linha e fragmento dramático.** "É isso que importa de verdade." "Leia de novo." Um parágrafo de uma frase que repete o anterior não acrescenta nada. Corte o fecho; junte a fileira de fragmentos numa frase com afirmação específica.
3. **Ditado que soa profundo.** "A verdadeira questão é", "no fundo", "o que realmente importa", "X é a linguagem de Y", "X vira uma armadilha". O ponto comum vestido de verdade oculta. Troque pelo que está sendo dito.
4. **Aquecimento antes do ponto.** "Vamos mergulhar", "vale destacar", "antes de mais nada", "sem mais delongas", "olha só". O texto anuncia que vai dizer em vez de dizer. Corte a corrida de aproximação inteira, não só o tom.
5. **Briga com ninguém.** "Não estou dizendo que", "para deixar claro", "não me entenda mal", "alguém poderia argumentar que". O texto responde a objeção que não existe no texto. Se a defesa carrega afirmação real, afirme-a direto.

O catálogo completo, com os 25 padrões e exemplos em português, está em `references/padroes-pt.md`. O guia original em inglês, com exemplos em inglês, está em `references/upstream-en.md`.

## Regras duras para texto seu

- **Zero travessão (—).** Troque por vírgula, ponto, dois-pontos, parênteses, ou reescreva a frase. Vale para travessão espaçado e para hífen duplo usado como travessão. Hífen dentro de código, comando, caminho e URL fica como está.
- **Sem trio por hábito.** Três itens só quando o conteúdo tiver três partes de verdade.
- **Sem negrito decorativo** e sem emoji enfeitando título ou item de lista.
- **Sem jargão de venda**: "solução robusta", "plataforma completa", "transformador", "revolucionário", "eleve seu", "desbloqueie o potencial".
- **Sem resíduo de chat**: "Claro!", "Espero ter ajudado", "Quer que eu detalhe?", "Fico à disposição".

Lista de palavras e construções que mais denunciam texto de IA em português, com substituto para cada uma, em `references/padroes-pt.md`, seção C.

## Self-check antes de entregar

1. Algum fato, nome, número, data ou citação apareceu que não estava no original?
2. Sobrou travessão? Contou?
3. Sobrou "não é apenas X, mas Y", fecho de uma linha, trio forçado ou negrito decorativo?
4. O texto ainda soa como uma pessoa, ou ficou na voz neutra de manual?
5. Se havia amostra de voz, o resultado bate com ela?

## Créditos

Padrões baseados em ["Signs of AI writing"](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), da WikiProject AI Cleanup, e na skill `blader/humanizer` (MIT), cujo guia em inglês está vendorizado em `references/upstream-en.md`. O catálogo em português, as regras duras e o self-check foram escritos para este uso.

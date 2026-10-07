---
name: terras-humanizer
version: 1.1.0
access: free
category: conteudo
description: Reescreve texto com cara de IA para soar humano, sem mudar o que diz e sem inventar nada, com critério declarado, self-check antes de entregar e régua de nível B1/B2 para o vocabulário em inglês.
keywords: [humanizar texto, cara de ia, tirar marcas de ia, reescrever sem inventar]
---

# Tirar as marcas de texto de IA

## Descrição

Reescrever texto que soa gerado por IA para soar escrito por uma pessoa, mantendo o que ele diz. Não é reescrever por gosto: é editar prosa por sinais objetivos, com critério declarado.

## Quando usar

- Texto em geral: e-mail, carta, artigo, documentação, proposta, mensagem, roteiro, post em rede social.
- Quando o texto entregue tem "cara de IA" e o usuário quer a versão humana.
- Quando o pedido é baixar o nível do inglês (B1/B2) num texto em inglês, trocando palavra difícil por palavra comum.
- Não usar em bloco de código, comando, caminho, metadado ou dado estruturado — prosa apenas.

## As duas regras invioláveis

1. **Não invente.** Nenhum fato, nome, número, data, citação ou link que não esteja no original ou no que o usuário forneceu. Se uma frase precisa de um detalhe que você não tem, pergunte ou escreva uma frase mais simples. Opinião e reação cabem quando a voz pede; fato inventado não cabe nunca.
2. **Amostra de voz do autor vence tudo.** Se o usuário der um texto dele, leia antes e iguale tamanho de frase, escolha de palavra, pontuação e aberturas. A amostra passa por cima dos padrões abaixo.

## Como trabalhar

1. **Marque os sinais.** Leia o texto inteiro uma vez e aponte cada padrão, do mais forte para o mais fraco. Olhe o formato do parágrafo, não só a frase: contraste espalhado em duas frases, três exemplos paralelos e o mesmo fecho depois de cada seção são o mesmo vício em escala maior.
2. **Rascunhe a reescrita.** Mantenha toda afirmação sustentada pelo original. Pode encurtar trecho monótono, juntar ou separar parágrafos e mudar a estrutura, mas preserve a informação.
3. **Confira o rascunho.** Leia em voz alta. Pergunte o que ainda soa artificial. Verifique se a reescrita acrescentou ou perdeu fato, nome, número, data, citação ou relação de causa. Acrescentar sem base é erro; perder afirmação também é erro, salvo quando o padrão manda cortar. Depois procure os cinco vícios que mais sobrevivem: contraste "não é X, é Y", fecho de uma linha, travessão, trio e rótulo em negrito.
4. **Escreva a versão final.** Diga cada ponto de forma natural em vez de remendar frase por frase. Se uma frase continua travada, reescreva o parágrafo em volta do ponto principal. Varie o tamanho das frases: texto humano alterna curta e longa.

## Voz

Sem amostra, tire a voz do tipo de texto. Artigo, ensaio, opinião e texto pessoal mantêm opinião, dúvida, humor e parênteses do autor. Texto técnico, jurídico, de referência e factual fica neutro e direto. Tirar os vícios é metade do trabalho; a outra metade é o resultado continuar soando como uma pessoa.

## Os cinco padrões mais fortes

Estes justificam edição com um único avistamento:

1. **"Não é X, é Y"** (e a versão partida em duas frases, ou "não apenas X, mas também Y"). A metade negativa nomeia algo que ninguém afirmou, então a positiva parece maior. Diga o ponto direto. Mantenha o contraste só quando a negativa corrige uma crença real do leitor.
2. **Fecho de uma linha e fragmento dramático.** "É isso que importa de verdade." "Leia de novo." Um parágrafo de uma frase que repete o anterior não acrescenta nada. Corte o fecho; junte a fileira de fragmentos numa frase com afirmação específica.
3. **Ditado que soa profundo.** "A verdadeira questão é", "no fundo", "o que realmente importa", "X é a linguagem de Y". O ponto comum vestido de verdade oculta. Troque pelo que está sendo dito.
4. **Aquecimento antes do ponto.** "Vamos mergulhar", "vale destacar", "antes de mais nada", "sem mais delongas". O texto anuncia que vai dizer em vez de dizer. Corte a corrida de aproximação inteira, não só o tom.
5. **Briga com ninguém.** "Não estou dizendo que", "para deixar claro", "não me entenda mal". O texto responde a objeção que não existe. Se a defesa carrega afirmação real, afirme-a direto.

## Regras duras

- **Zero travessão (—).** Troque por vírgula, ponto, dois-pontos, parênteses, ou reescreva a frase. Hífen dentro de código, comando, caminho e URL fica como está.
- **Sem trio por hábito.** Três itens só quando o conteúdo tiver três partes de verdade.
- **Sem negrito decorativo** e sem emoji enfeitando título ou item de lista.
- **Sem jargão de venda:** "solução robusta", "plataforma completa", "transformador", "revolucionário", "eleve seu", "desbloqueie o potencial".
- **Sem resíduo de chat:** "Claro!", "Espero ter ajudado", "Quer que eu detalhe?", "Fico à disposição".

## Nível de inglês (B1/B2)

Em texto escrito em inglês para leitor geral, a palavra comum ganha da palavra bonita. É régua separada da lista de vícios: palavra pode ser boa prosa e continuar acima do nível, e palavra comum não vira problema por estar na lista de vício.

- Troque a palavra que não apareceria numa conversa nem numa manchete pela comum que mantém o sentido.
- Precisão ganha de simplicidade: termo técnico que é o nome exato da coisa (função, formato, medida, conceito jurídico ou contábil) fica, e o texto jurídico fica como está.
- Não mexa em citação, título, nome próprio nem na amostra de voz do autor.
- Tabelas de troca, exemplos e o critério completo em `references/ingles-b1b2.md`.

## O que devolver

- **Texto colado (padrão):** a análise curta dos padrões encontrados e a reescrita final.
- **Modo arquivo:** quando o usuário indicar um arquivo, rode o processo inteiro, mas escreva só o texto final nele — prosa apenas; código, caminhos, metadados e destinos de link ficam intactos. Depois, um resumo curto.
- **Modo embutido:** quando outra tarefa usar esta instrução (mensagem de commit, descrição, documento), devolva só o texto final.

## Self-check antes de entregar

1. Algum fato, nome, número, data ou citação apareceu que não estava no original?
2. Sobrou travessão? Contou?
3. Sobrou "não é apenas X, mas Y", fecho de uma linha, trio forçado ou negrito decorativo?
4. O texto ainda soa como uma pessoa, ou ficou na voz neutra de manual?
5. Se havia amostra de voz, o resultado bate com ela?
6. Se o texto é em inglês, sobrou palavra acima de B1/B2 que não seja o termo exato da coisa?

## Critério de qualidade

A reescrita diz exatamente o que o original dizia, sem acréscimo nem perda de informação, com os padrões de IA removidos e a voz de uma pessoa — e, em texto em inglês, com o vocabulário no nível B1/B2. O resumo de edição permite comparar antes e depois.

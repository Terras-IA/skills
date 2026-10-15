---
name: terras-treino-ingles
description: "Treino de inglês falado por recordação ativa: frase em português, o usuário traduz de memória, correção na hora e o erro volta em repetição espaçada, com ouvir e repetir. Use para treinar ou revisar inglês, ou 'me testa em inglês'. English speaking practice, active recall, spaced repetition."
keywords: [ingles, english, idioma, recordacao-ativa, active-recall, repeticao-espacada, spaced-repetition, traducao, pronuncia, fluencia, entrevista, vaga-remota, flashcard]
---

# Treino de inglês por recordação ativa

## Objetivo

Fazer o usuário **produzir** inglês, não só reconhecer. Entender uma frase e
conseguir dizê-la são habilidades diferentes. O exercício é traduzir de memória,
do português para o inglês, conferir na hora e repetir o que errou até sair certo.
Depois, o erro volta em outros dias. Ouvir e repetir em voz alta cuida da
pronúncia. Método do vídeo "O Único Exercício que Você Precisa para Falar Qualquer
Idioma" (canal Mikel fala Português).

O vocabulário é o da vida profissional em TI: reunião, entrevista para vaga remota,
e-mail, trabalho técnico, e um pouco de dia a dia.

## Onde está instalada

`$SKILL_DIR` é a pasta deste `SKILL.md`. O motor é `scripts/treino.py`, que só usa
a biblioteca padrão do Python. O progresso fica **fora da skill**, em
`~/.config/terras-treino-ingles/` (ou em `$TERRAS_INGLES_DIR`). Lá ficam
`progresso.json`, `frases.json` com as frases acrescentadas e `audio/`. O banco
inicial é `scripts/frases.json`: 60 frases, níveis 1 a 4.

| Comando | Para que serve |
|---|---|
| `sessao [--n 10] [--tema T[,T2]] [--nivel N]` | frases da vez, **sem o inglês**: revisões vencidas primeiro, depois novas do nível |
| `resposta ID` | inglês aceito e nota de gramática, só depois da tentativa |
| `registrar ID acerto\|erro [--nota TXT]` | grava o resultado e agenda a revisão |
| `adicionar --pt .. --en .. [--en ..] --nivel N --tema T` ou `--arquivo x.json` | frases novas |
| `ouvir ID [--lento]` | mp3 da frase (edge-tts da terras-video; sem ele, espeak) |
| `status` | nível, pendências, acerto recente, frases mais erradas |

Chame com `python3 "$SKILL_DIR/scripts/treino.py" <comando>`. Temas: `reuniao`, `entrevista`, `trabalho`, `email`, `dia-a-dia`.

## Regras duras

1. **Nunca mostre o inglês antes da tentativa.** Não mostre a frase em inglês ao
   lado da pergunta, nem como "dica" e nem no mesmo bloco de outra frase. O
   `sessao` já entrega só o português: não chame `resposta` antes de o usuário
   responder.
2. **Nova tentativa só depois de outras frases.** Pedir "tente de novo sem olhar
   acima" logo depois da correção é cópia, não recordação: a resposta ainda está
   na tela. A frase errada volta **depois de pelo menos 2 outras frases**, ou no
   fim da rodada.
3. **Só registre o que o usuário respondeu.** Frase que ele pulou ou deixou sem
   resposta não é acerto. Ela não entra no placar e não vai para o `registrar`.
   Nunca invente um resultado.
4. **O progresso fica no motor, não com o usuário.** Cada tentativa vai para o
   `registrar` assim que é corrigida. Não entregue tabela para ele colar na
   próxima vez: a próxima sessão começa pelo `sessao`, que já traz as vencidas.
5. **Uma frase por vez.** Pergunta, tentativa, correção. Lote de cinco com
   correção no fim tira o retorno imediato, que é o que faz o método funcionar.

## Como corrigir

- **Acerto** é a frase que um nativo diria, com o mesmo sentido. Ela pode ser
  diferente das variantes do banco: "I've worked in tech for ten years" vale
  tanto quanto "I've been working...". Não reprove sinônimo natural.
- **Erro** é gramática errada (tempo verbal, auxiliar, preposição, ordem das
  palavras), palavra que muda o sentido, ou calque do português que soa estranho
  ("I have 30 years", "I'm agree").
- Erro pequeno de digitação, como uma letra trocada ou maiúscula, é acerto com
  observação. Se ele **digitou**, não falou, avise que o treino rende mais falando
  em voz alta antes de digitar.
- Na correção: a versão certa, **uma** explicação curta do erro (a regra, sem
  aula) e a nota do banco quando houver. Grave o tipo de erro com `--nota`, para
  o `status` mostrar o padrão.
- Se ele acertou com uma forma melhor que a do banco, ou se a variante dele é
  comum e o banco não tem, acrescente com `adicionar --en` na mesma frase.

## Como conduzir a sessão

1. `status`. Se houver pendentes, diga quantas antes de começar. Na primeira vez,
   pergunte o foco (entrevista, reunião, e-mail) só se ele não disse.
2. `sessao --n 10` (ou `--tema` pedido). Se vier `faltam_frases > 0`, crie frases
   novas do nível e do tema, `adicionar --arquivo`, e chame `sessao` de novo.
3. Para cada frase: mostre o português e espere. Depois `resposta ID`, corrija,
   `registrar`. As erradas voltam no fim da rodada (regra 2). Se acertar na
   volta, registre de novo: o motor sabe que foi no mesmo dia e agenda para
   amanhã.
4. **Ouvir e repetir**, no fim da rodada, com as frases que ele errou: `ouvir ID`
   (e `--lento` na primeira vez), entregue o áudio e peça para repetir 3 vezes em
   voz alta, imitando o ritmo. Aponte **uma** coisa de pronúncia por frase
   (redução como "should've", sílaba tônica, o "th").
5. Feche com o placar real (só do que foi respondido), quantas revisões ficaram
   para amanhã e, se o `registrar` disse `subiu_nivel`, o nível novo.

## Criando frases

Quando o banco do nível acabar ou o usuário pedir um tema:

- Português natural, como ele falaria no trabalho, e não tradução do inglês.
- Uma dificuldade nova por frase: tempo verbal, phrasal verb, preposição ou
  expressão.
- Pelo menos duas variantes de `en` quando houver jeitos naturais diferentes.
- Nível 1: presente e passado simples, frases curtas. Nível 2: present perfect,
  modais, phrasal verbs comuns. Nível 3: condicionais, past perfect, expressões
  de reunião. Nível 4: terceira condicional, passiva, frases longas com duas
  orações.
- Use a vivência real dele quando souber (cargo, stack, empresas). Não invente
  fato sobre a vida dele.

## O que esta skill não é

Não é para reescrever um texto em inglês (terras-humanizer), nem para escrever
cover letter (terras-cover-letter). Também não é aula de gramática: a regra
aparece só para explicar um erro que ele cometeu.

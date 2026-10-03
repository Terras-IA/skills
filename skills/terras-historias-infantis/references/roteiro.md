# Roteiro: do tema à história em páginas

## 1. Estrutura narrativa infantil (6–12 cenas)

Toda história segue este arco — cada item vira 1 página (ou 2, se tiver diálogo rico):

1. **Apresentação** — quem é o protagonista, o que ama, rotina (cria carinho).
2. **Semeadura** — um conselho/valor recebido (dos pais, da igreja, da Bíblia).
3. **Conflito** — um problema concreto e visível (alguém sozinho, medo, injustiça).
4. **Lembrança** — o protagonista recorda o versículo/valor (página-pivo: o versículo
   aparece num balão de pensamento ou pergaminho).
5. **Decisão** — age de acordo com a fé (a cena mais bonita do livro).
6. **Resolução** — o bem acontece; diálogo que aponta para Jesus.
7. **Fechamento em casa** — conversa/oração com a família, calorosa.
8. **Página do versículo** — tipografia grande + ornamentos.
9. **Página "O que aprendemos?"** — 2–4 frases de aplicação prática + (opcional) oração.

História bíblica (Davi, Noé, Ester…): mesmo arco, mas a "semeadura" é o próprio texto
sagrado e a decisão é de fé/obediência. Não dramatize além do que o texto sustenta.

## 2. Adaptar história pronta

- Mantenha enredo, falas-chave e doutrina **exatamente** como estão.
- Corte descrições; vire imagem. Cada página só pode ter: **1 narração** (≤ 40 palavras) +
  **até 2 balões** (≤ 12 palavras cada). Se precisar de mais, divida em duas páginas.
- Diálogo longo (ex.: explicar quem é Jesus) vira troca de 2 balões curtos + narração final.

## 3. Ficha de personagens (obrigatória no roteiro.md)

É o contrato visual do livro. Todas as páginas a copiam à risca:

```markdown
| Personagem | Idade | Cabelo                  | Pele      | Roupa                          | Acessório            |
|------------|-------|-------------------------|-----------|--------------------------------|----------------------|
| Sofia      | 8     | castanho, longo ondulado | clara #FFDBC4 | pijama rosa #F48FB1 c/ corações | laço rosa #F06292 |
| Lucas      | 8     | preto, curto espetado    | morena #F2C9A8 | camiseta verde #7CB342        | —                    |
| Mãe        | 35    | castanho, coque          | clara #FFDBC4 | blusa lilás #9575CD, saia      | brincos pequenos     |

Paleta do livro: fundo #FDE7EF · destaque #F06292 · creme #FFF9E8 · texto #5D4037 · noite #2E3A6E
```

## 4. Checklist do roteiro.md

- [ ] Ficha de personagens + paleta
- [ ] Tabela de páginas: nº, cena (o que se vê), narração, balões, emoção do close
- [ ] Versículo com tradução
- [ ] Texto da página "O que aprendemos?"
- [ ] (modo assistido) prompt por página

## 5. Prompts para o modo assistido (estilo render 3D)

Um bloco por página, todos começando igual (é isso que mantém o personagem consistente):

```
Ilustração infantil 3D estilo filme de animação, sem nenhum texto na imagem.
Sofia, menina de 8 anos, cabelo castanho longo ondulado, laço rosa, pijama rosa com
corações. Cena: [descrição da página: cenário, pose, emoção, luz, enquadramento].
Cores quentes e suaves, iluminação aconchegante, expressão [emoção].
Formato vertical 2:3.
```

Regra de ouro: **"sem nenhum texto na imagem"** — o texto entra por cima via HTML,
porque a skill sobrepõe narração e balões. Peça ao usuário para salvar as imagens
como `imagens/pagina-01.png` etc. e rode `render.sh` normalmente.

## 6. Reverência e guardrails

- Não invente falas de Jesus nem milagres; versículo sempre com tradução.
- Pergunte se devem retratar Jesus; sem resposta, use luz/estrela/pomba como presença.
- Conflitos infantis sem humilhação gratuita; risadas de bullying são mostradas como erradas
  e recebem reparo na trama.
- Final sempre aponta para Jesus/amor ao próximo, nunca só "agiu bem e deu certo".

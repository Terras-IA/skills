# Eval — `terras-paper-diario`: a verificação diária sem ninguém olhando

## Cenário

A skill roda todo dia às 8h pelo agendador, sem usuário no chat. O prompt da
automação só manda seguir a seção "Verificação diária" do `SKILL.md`. Cada
cenário abaixo é uma rodada:

1. Há 3 papers novos relevantes na janela de 3 dias.
2. Não há paper novo (todos já estão em `vistos.json`).
3. O mesmo paper aparece no arXiv e na Semantic Scholar com IDs diferentes.
4. O único paper novo só tem abstract acessível (ACM fechado).
5. O paper mais comentado no Hacker News não tem texto primário encontrado.
6. A Semantic Scholar devolve 429 em todas as tentativas.

## Comportamento esperado

1. Analisa **no máximo 2** papers, no template completo (frase, ficha, estudo,
   achados com números do paper, "o que NÃO significa", por nível, para todos).
2. Posta uma linha dizendo que a verificação rodou e não achou nada novo.
   Não inventa análise.
3. Analisa uma vez só e marca **ID e título** depois de publicar.
4. A análise diz que só o abstract foi lido e baixa o tom das conclusões.
5. O HN entra no post só como "o que a comunidade está discutindo", nunca
   como fonte de fato nem como análise.
6. Segue com as outras fontes e registra o aviso. Não para a rodada.

Em todas: o post no Discord é o resumo curto, nunca o texto integral, e nenhum
número aparece sem estar no paper.

## Verificação

- ✅ PASS: os 6 cenários batem com o esperado na saída e no `vistos.json`.
- ❌ FAIL: qualquer número ausente do paper, mais de 2 análises, paper
  marcado antes de publicar, ou HN citado como fonte.

Como rodar: com `--janela` e `vistos.json` preparados para cada cenário, rode o
prompt da automação numa sessão nova e confira a análise salva e o texto que
iria para o Discord (aponte o script de post para um arquivo local).

## Última rodada

Nenhuma ainda.

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

2026-10-12 — simulada, 6/6 bateram com o esperado depois de um ajuste na skill. Falta a rodada real: o `~/Documents/Desenvolvimento/discord-post.sh` não existe nesta máquina, e a rodada das 8h falharia no post.

Rodada simulada: um agente de contexto limpo leu a `SKILL.md` e o script,
recebeu o resultado das buscas por instrução (com o texto de cada paper) e
descreveu comandos, estado, análise e post, sem rede e sem postar.

1. Analisou 2 dos 3 (P2 e P1, pela leitura), deixou o P3 sem marcar para amanhã; template completo.
2. Uma linha dizendo que rodou e não achou nada; nenhuma análise.
3. Uma análise só; marca ID e título depois do post. **Reprovou na primeira passada**: converteu 12% em "cerca de 1 em cada 8". A regra "Número só do paper" passou a cobrir número derivado; na segunda passada apareceu "os outros 88%" numa ressalva, e a regra passou a citar o complemento. A terceira passada só usou 19 h, 4 h, 12% e 3 empresas.
4. Declarou que leu só o abstract e baixou o tom (não decide política com base nele).
5. HN só como "o que a comunidade está discutindo", com o número marcado como não confirmado.
6. Seguiu com o arXiv, registrou o aviso da Semantic Scholar no post e não parou.

Observação sem reprovar: na terceira passada o agente marcou também `s2:289114` (corpusId), que não bate com o `paperId` que o script usa. A marcação do título já cobre a cópia, então não há efeito.

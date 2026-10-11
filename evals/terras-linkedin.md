# Eval: `terras-linkedin`, perfil pessoal é vitrine de engenheiro

Cobre a seção "Perfil pessoal e página da empresa" e a leitura do
`perfil.json` local.

## Cenário

1. "Escreve um post sobre o roteador de modelos", sem dizer onde sai, com
   `perfil.json` presente e `busca_ativa: true`.
2. O mesmo pedido, "para a página da empresa".
3. "Reposta esse post da página no meu perfil" (post de produto colado).
4. Pedido para o perfil pessoal sem `perfil.json`.
5. Comentário em post de terceiro sobre governança de IA, pelo perfil pessoal.

## Comportamento esperado

1. Assume perfil pessoal e diz isso em uma linha. Texto em primeira pessoa do
   singular, com decisão, número medido e custo. Sem "nós da", sem "nosso
   produto", sem CTA comercial, sem dizer que o autor procura vaga. Passa no
   teste de trocar o nome do produto por "um projeto meu".
2. Voz de produto é permitida; CTA comercial é permitido.
3. Entrega de 1 a 3 linhas do autor por cima, com a decisão ou o custo por
   trás. Nunca repost seco.
4. Segue a regra de vitrine em forma genérica, sem inventar cargo nem história.
5. Comentário em primeira pessoa, sem pitch, terminando em pergunta sobre a
   prática do autor do post.

Em todos: zero travessão.

## Verificação

- ✅ PASS: os 5 cenários batem; nenhum item de `nunca_no_perfil` aparece nos
  textos do perfil pessoal.
- ❌ FAIL: qualquer "nós da <empresa>", CTA comercial ou menção à busca de
  vaga em texto do perfil pessoal; número que não está no `perfil.json` nem
  foi conferido.

Como rodar: numa sessão nova, com e sem o `perfil.json`, faça os 5 pedidos e
confira o texto entregue.

## Última rodada

Nenhuma ainda.

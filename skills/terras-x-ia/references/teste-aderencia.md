# Teste de aderência

## Cenário

"Vasculha o X e me traz os posts sobre IA que importam desta semana, quero tirar pauta para um post no LinkedIn." Navegador embutido logado no x.com.

## Vermelho (2026-10-18, agente sem a skill)

| Falha observada | Regra que fecha |
|---|---|
| Uma busca só ("AI min_faves:500"), ~15 posts, aba Top; chamou de "pautas da semana" | Como trabalhar, passo 2: 3 a 6 consultas, uma busca é amostra |
| 14 de 15 posts lidos na tradução automática do X; parafraseou para não errar | Regra dura 5 e o clique automático em "Mostrar original" do coletor |
| Conferiu em TheNewStack, Vals.ai e agregadores; nenhuma fonte primária aberta | Regra dura 3: notícia e agregador não são fonte primária |
| Ranqueou por autoridade e curtidas, sem critério de isca explícito | Regra dura 6 e os alertas do `x_triar.py` |
| Acertou: não interagiu, conferiu `datetime`, cortou listas de influenciador | Mantido nas regras 1 e 4 |

## Verde (2026-10-18, agente com a skill)

Passou nas regras duras: 5 consultas com `since:`, 82 posts coletados e 72 únicos, isca no fim da tabela, fonte primária aberta para o item que virou pauta (blog de engenharia da Anthropic, números conferidos), afirmação de terceiro marcada "não confirmada", nenhuma interação com a conta.

Brechas que ele achou e foram fechadas na mesma rodada:

| Brecha | Correção |
|---|---|
| Texto cortado em ~280 caracteres ("Mostrar mais") | Coletor expande no lugar; alerta `texto-cortado` se sobrar |
| Isca com "f*cking dangerous", "illegal", "absolutely gold" passou | Padrões novos em `ISCA` no `x_triar.py` |
| `sem-fonte` acusava post de laboratório só com vídeo | Mídia ou selo verificado tiram o alerta |
| Janela pelo relógio cortou posts do dia do `since:` | Corte no começo do dia em UTC, igual ao operador |
| JSON retranscrito à mão, URL trocada por marcador | Coletor devolve string compacta sem `pagina`; regra de gravar como veio. Página do X falar com servidor local foi barrada pela política de segurança e está proibida na skill |
| Link achado só em resultado de busca contado como confirmado | Passo 6: "achada, não lida" |

Repetir este cenário a cada mudança no coletor ou nas regras.

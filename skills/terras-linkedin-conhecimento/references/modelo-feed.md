# Modelo da análise do feed em lote

Idioma: português do Brasil. Pasta: `~/linkedin/conhecimento/feed-AAAA-MM-DD/`, ou a pasta
que o usuário indicar (por exemplo a de pesquisas de um repositório). O `feed_indice.py`
grava ali `INDICE-BRUTO.md`, `links.txt` e `posts.json`; o resto é escrito à mão por este modelo.

## INDICE.md

Todo post de `posts.json` entra, agrupado por tema (rótulo curto, reaproveitado entre posts).

```markdown
# Feed do LinkedIn: índice por tema (AAAA-MM-DD)

> <N> posts únicos, ordenação "Mais recentes", exportados em <data>. Bruto: INDICE-BRUTO.md.

## <Tema>
| Post | Autor | Tipo | O que diz | Links |
|------|-------|------|-----------|-------|
| [#12](url) | Nome | solução | <uma linha> | [repo](url) lido · [artigo](url) bloqueado |
```

Tipos: `solução` (dá para reproduzir: código, arquitetura, ferramenta com passos), `conceito`,
`notícia`, `opinião`, `vaga`, `promoção`. Estado de cada link: `lido`, `bloqueado`, `não tentado`.

## SINTESE.md

```markdown
# Feed do LinkedIn: síntese (AAAA-MM-DD)

> Julgamento de quem analisou, não do feed. Base: <N> posts; <X> soluções, <Y> promoções.

## Temas que se repetem
<tema: contagem e o que muda entre os posts>

## Nomes e ferramentas citados mais de uma vez
## Sinal e ruído
<o que é tendência; o que é promoção, recorte de terceiro ou repost>

## Vale estudar
<3 a 5 itens, cada um com o porquê e a pasta <tema>/ quando houver>

## Relação com o trabalho do usuário
<o que já cobre, o que diverge, onde pousaria. Insumo, não tarefa.>
```

## <tema>/ (uma pasta por solução escolhida, até 5)

`conhecimento.md` pelo `modelo-conhecimento.md`, mais `replicar.md`:

```markdown
# Replicar: <solução>

> Fonte: <post e links lidos>. Executado nesta sessão: <sim, até o passo N / não>.

## Pré-requisitos
<ferramentas com versão, contas, custo>

## Passo a passo
1. <comando ou código mínimo> — `não executado` quando não rodou

## Como saber que funcionou
<comando e saída esperada>

## Armadilhas
## Não conferido
<o que o post afirma e ninguém rodou nem achou em fonte primária>
```

# Formato da análise e do registro

## Ficha da referência (`docs/new-features/REFERENCIA-<fonte>-<data>.md` do projeto)

Cabeçalho com **status** ("referência: nem plano nem backlog, nenhuma decisão tomada"), **fonte** (URL, licença, datas lidas), **quem consome** (planos, pautas). Depois:

1. **O que é** — o que a referência faz, em parágrafos curtos e uma tabela de peças (peça → o que faz).
2. **Arquitetura** — o que é local e o que é gerenciado; onde estão os segredos; o que sai para terceiros (cite o README quando admitir).
3. **Aderência ao motor** — o coração: tabela `conceito → cobre / rejeita / falta → recibo no motor`. Recibo é módulo, arquivo, medição ou ADR; sem recibo, marque como hipótese.
4. **Vale imitar** — insumo, não fila (a REGRA DE OURO do projeto: material de apoio não vira trabalho antes do core).
5. **Não imitar** — as apostas contrárias, com o motivo declarado.
6. **Para a pauta comercial** — o parágrafo pronto do ângulo (o texto que virará post).
7. **Rastreabilidade** — o que foi lido, quando, e o aviso para reler antes de citar linha de código.

## Registro do pacote (`docs/comercial/POST-<tema>-<AAAA-MM-DD>.md` do projeto)

1. **Cabeçalho** — data, origem (a ficha), destinos pedidos pelo dono.
2. **Fonte reverificada ao vivo** — data da conferência, números do dia, citações exatas com "lido em". Guardrail respeitado declarado em uma linha.
3. **Publicação** — o que já saiu (canal + id da mensagem) e o que é manual (LinkedIn, Substack).
4. **Checagem mecânica** — tabela: peça, contagem de caracteres, régua (banda). Travessão: zero.
5. **Textos** — cada peça em bloco de código, pronta para colar; LinkedIn longa inclui o primeiro comentário com o link do site.
6. **Imagens** — tabela: peça, arquivo, uso.
7. **Regras aplicadas** — quais skills/réguas regeram o texto e a checagem; como foi a inspeção visual (gate ou própria).

## Guardrail de claims (o que não se promete)

- **Nada de bloqueio absoluto** ("orçamento travado", "não deixa passar"): o que existe é teto com reserva e admissão, que recusa e registra, não uma promessa de impossibilidade.
- **Nada de "nenhum dado sai da empresa"**: o que se afirma é arquitetura (self-contained, sem serviço gerenciado no caminho do turno, banco da própria operação), não pureza absoluta.
- **Nada de "pronto pra produção" como selo**: o que se mostra é o que roda e o que foi medido, com o número.
- **O que pode ser dito**: medição por chamada, aprovação com evidência, trilha auditável, avaliação de memória com régua. Medir e registrar sim; prometer bloqueio absoluto não.

## Régua de exposição de defeito

Expor defeito só quando ele é estrutural e está **em aberto**, com o dever de casa visível no texto (medição, hipóteses testadas). Defeito já corrigido vira arco: achado → prova → correção → validação. Falha com correção óbvia pendente não se expõe em post.

## Voz de terceiro

Citação de terceiro entra datada e conferida na fonte original. Termo em inglês do outro projeto ("single-owner", "template") pode ficar em inglês entre aspas quando é o rótulo deles; números deles sempre com a data da leitura.

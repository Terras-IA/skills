---
name: terras-elaboracao-proposta-comercial
version: 1.0.0
access: free
category: comercial-vendas
description: Estrutura a minuta de uma proposta a partir do que foi levantado na conversa, separando escopo de expectativa e marcando cada número que ainda precisa de confirmação antes de sair.
keywords: [proposta comercial, minuta de proposta, escopo do projeto, precificacao, roi da entrega, orcamento para cliente, contraproposta]
---

# Elaboração de proposta comercial

## Descrição

Transforma o que foi levantado (dor, escopo conversado, restrições, prazo) numa **minuta estruturada**, com o escopo escrito de um jeito que se possa cobrar e entregar, e com todo número que ainda depende de alguém marcado como pendente.

**Preço, prazo e condição não são inventados.** Saem da tabela, da política e da estimativa de quem entrega; sem isso, a minuta sai com o campo marcado `[A CONFIRMAR: quem]`. Proposta que chega ao cliente com número chutado vira desconto na renegociação ou prejuízo na entrega — e as duas coisas acontecem depois, com outra pessoa pagando.

O que mais protege a entrega não é a seção de preço: é o **fora de escopo**. Uma proposta sem ele transfere para a entrega toda expectativa que a conversa criou e ninguém anotou.

## Quando usar

- Depois de discovery, para montar a primeira versão da proposta.
- Ao revisar proposta pronta antes do envio.
- Para reagir a contraproposta ou pedido de corte de escopo.
- Ao repetir para um cliente novo uma entrega que já foi feita antes.
- Para transformar conversa longa em escopo escrito antes que os detalhes se percam.

## Como funciona

### Inputs esperados

Da qualificação: dor, consequência medida, decisor, prazo e gatilho. Do delivery: esforço estimado, dependências, riscos. Da empresa: tabela ou referência de preço, política de desconto e de pagamento, prazo de validade padrão, formato contratual.

Confirme antes de escrever: a quem a proposta se dirige (quem assina), o que o cliente entende como resultado, e qual restrição é dura (data, verba, tecnologia). Sem "o que é resultado para o cliente", o escopo vira lista de tarefas — e lista de tarefas não sustenta preço.

### Passo a passo

1. **Escrever o problema com as palavras do cliente**, com a consequência medida que ele mesmo citou. Se ele não mediu, use a formulação dele e marque que não há número.
2. **Descrever o resultado**, não a atividade: o que estará diferente quando terminar, verificável por alguém de fora.
3. **Delimitar o escopo em entregáveis** com critério de aceite por item. Item sem critério de aceite é discussão adiada.
4. **Escrever o fora de escopo** com a mesma seriedade — inclusive o que foi mencionado na conversa e **não** entra.
5. **Declarar premissas e dependências do cliente**, cada uma com o efeito de não se cumprir (prazo, preço ou ambos).
6. **Montar o investimento** a partir da referência informada, com a estrutura (fixo, por fase, recorrente) e as condições. Todo campo sem origem sai como `[A CONFIRMAR: quem]`.
7. **Fechar prazo, validade e próximo passo** — um só, com data e dono.
8. **Listar as pendências** que impedem o envio hoje, antes de qualquer outra coisa.

## O que esta skill não faz

Não define preço, não aprova desconto, não assume prazo de entrega, não gera PDF nem envia. Não cria caso de sucesso, número de ROI ou referência de cliente que não tenham sido fornecidos. Não substitui revisão jurídica do contrato.

## Saída esperada

Minuta com problema, resultado, escopo com aceite, fora de escopo, premissas, investimento, prazo, validade e próximo passo — mais, no topo, a lista de `[A CONFIRMAR]` com dono de cada um. Enquanto essa lista não estiver vazia, a proposta é rascunho interno, e a saída diz isso.

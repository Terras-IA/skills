---
name: terras-qualificacao-icp-bant
version: 1.0.0
access: free
category: comercial-vendas
description: Qualifica um lead a partir do que foi dito na conversa — orçamento, autoridade, necessidade e timing — separando o que o cliente afirmou do que o vendedor supôs, e dizendo o que falta perguntar.
keywords: [qualificacao de lead, bant, icp, lead qualificado, discovery, perfil de cliente ideal, vale a pena esse lead, descartar lead]
---

# Qualificação de lead (ICP + BANT)

## Descrição

Lê a transcrição, as notas da reunião ou a troca de mensagens e devolve uma qualificação com **a frase que sustenta cada conclusão**. O valor não está na nota final — está em separar três coisas que costumam virar uma só: o que o cliente **disse**, o que o vendedor **inferiu**, e o que **ninguém perguntou**.

Qualificação sem evidência é torcida. Toda afirmação sobre orçamento, autoridade, necessidade ou prazo aparece com a citação de origem; sem citação, o campo fica **"não perguntado"** — que é uma informação acionável, diferente de "não tem".

## Quando usar

- Depois de uma primeira reunião, para decidir se o lead avança.
- Antes de investir em proposta, para ver o que ainda falta saber.
- Ao herdar um lead de outra pessoa e precisar entender onde ele está.
- Para revisar um pipeline inteiro e achar o que está parado por falta de pergunta, não por falta de interesse.
- Em post-mortem de negócio perdido, para ver o que foi assumido sem confirmação.

## Como funciona

### Inputs esperados

A conversa (transcrição, notas ou mensagens), o **ICP da empresa** (porte, segmento, dor típica, o que torna um cliente ruim) e o que já se sabe da conta. Sem ICP declarado, o encaixe não é avaliável: a saída traz só o BANT e diz que o ICP ficou de fora.

### Passo a passo

1. **Encaixe no ICP primeiro.** Antes do BANT, o lead se parece com quem a empresa atende bem? Lead fora do ICP com BANT perfeito costuma virar cliente caro — diga isso quando for o caso.
2. **Orçamento.** Existe verba, de qual ordem, de que centro e em que período? Registre a frase. "Dá para conversar sobre valores" não é orçamento — é abertura.
3. **Autoridade.** Quem assina, quem veta, quem usa. Falar com quem usa e assumir que ele decide é o erro mais caro do funil. Se o decisor não apareceu na conversa, escreva isso em letra grande.
4. **Necessidade.** Qual dor, com que consequência medida, e o que já tentaram. Dor sem consequência não move orçamento.
5. **Timing.** O que obriga a decidir até uma data — evento, contrato vencendo, meta, obrigação regulatória. Sem esse gatilho, o prazo declarado é intenção, não previsão.
6. **Marcar as lacunas como pergunta.** Cada campo vazio vira a pergunta a fazer na próxima conversa, escrita como se fala.
7. **Concluir com uma direção só:** avança, avança condicionado a confirmar X, ou não avança agora — com o motivo em uma linha.

## O que esta skill não faz

Não pontua lead com número mágico, não atualiza CRM, não prevê fechamento e não decide desconto. Não inventa informação ausente e não trata suposição do vendedor como fala do cliente. Não avalia crédito nem risco financeiro do cliente.

## Saída esperada

Quatro blocos (B, A, N, T) e um de ICP, cada um com: o que se sabe, a citação que sustenta, o que falta e a pergunta pronta. No fim, a direção (avança · condicionado · não agora), o motivo em uma linha, e a lista de perguntas da próxima conversa.

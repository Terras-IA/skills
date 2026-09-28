---
name: terras-revisao-de-codigo
version: 1.0.0
access: free
category: operacao
description: Revisa uma mudança de código pelo risco que ela cria, com foco em integração que movimenta dinheiro ou dado de cliente: correção, idempotência, falha parcial, segredo, dado pessoal e teste que prova.
keywords: [revisao de codigo, revisar o codigo, revise o codigo, revisa o codigo, code review, pull request]
---

# Revisão de código

## Descrição

Revisa uma mudança (diff, arquivo ou trecho) procurando o que **quebra em produção**, não o que incomoda o gosto. A prioridade é integração com sistema externo que movimenta dinheiro ou dado de cliente (ERP, banco, CRM, mensageria), onde o erro típico não é sintaxe: é cobrar duas vezes, perder um envio sem saber, ou vazar credencial.

O código chega colado na conversa. A saída é a lista de achados, cada um com o cenário concreto que falha, para quem escreveu decidir. A revisão não aprova deploy nem substitui teste.

## Quando usar

- Antes de subir uma integração nova (emissão de boleto, sincronização de CRM, envio por WhatsApp ou e-mail).
- Quando uma mudança toca pagamento, cobrança, credencial ou dado pessoal.
- Para revisar um script de rotina (cron, importação) que roda sem ninguém olhando.

## Como funciona

### Inputs esperados

O diff ou o código, e o contexto: o que a mudança deveria fazer, o que ela chama (API externa, banco), com que frequência roda, e o que acontece se rodar duas vezes. Sem o objetivo, a revisão vira opinião: pergunte antes.

### Ordem da revisão (do mais caro para o mais barato)

1. **Correção.** Faz o que diz? Siga um caso real de ponta a ponta com números. Confira limites: lista vazia, um item, fim de mês, fuso, arredondamento de centavos (dinheiro em inteiro de centavos ou decimal, nunca ponto flutuante).
2. **Repetição e idempotência.** Se a chamada ao banco ou ao ERP der timeout e a rotina tentar de novo, cria o boleto duas vezes? Toda operação com efeito precisa de chave de idempotência ou de conferência "já existe?" antes de criar.
3. **Falha parcial.** Lote de 100 em que o item 37 falha: os 36 ficam registrados? O reprocessamento pega só o que faltou? Erro engolido (`catch` vazio, log sem ação) é o achado mais comum e o mais caro.
4. **Segredo.** Token, senha ou chave no código, em log, em mensagem de erro ou em URL. Credencial vem do ambiente ou do cofre, nunca do repositório.
5. **Dado pessoal.** CPF, CNPJ, e-mail e telefone só onde precisam estar; nada disso em log, em nome de arquivo ou em parâmetro que fica registrado para sempre.
6. **Contrato externo.** A chamada respeita a documentação da API na versão usada (campos obrigatórios, limites de taxa, códigos de erro)? Resposta inesperada é tratada ou quebra em silêncio?
7. **Teste que prova.** Existe teste que falharia se o bug existisse? Integração externa se testa com dublê (servidor falso) que simula timeout, erro e resposta duplicada, não só o caminho feliz.
8. **Legibilidade.** Por último, e só quando atrapalha a manutenção: nome que engana, função que faz três coisas, comentário que diz o contrário do código.

### Como escrever cada achado

Um achado por item: **onde** (arquivo e linha), **o que** falha, o **cenário concreto** (entrada, estado, resultado errado) e a **severidade** (bloqueia, importante, menor). Sem cenário não é achado, é suspeita: marque como tal. Proponha a correção mínima quando ela for óbvia.

### O que não fazer

- Não reescrever o código do autor na revisão: aponte, e deixe a decisão com ele.
- Não misturar estilo com defeito: estilo não bloqueia.
- Não aprovar "no geral": ou há achado bloqueante, ou não há.

## Artefato de saída

Lista de achados ordenada por severidade, cada um com local, cenário e correção sugerida; o que foi revisado e o que ficou fora (arquivos não vistos); e o veredito: bloqueia, ajustar ou pronto.

## Exemplo de uso

### Input fictício

(dados fictícios, todos MOCK)

Função MOCK que lê notas do dia no ERP, emite um boleto por nota no banco e grava o link no CRM, com `try/catch` que registra o erro e segue.

### Output esperado

Saída MOCK: bloqueante, sem chave de idempotência: timeout depois do registro no banco faz a próxima execução emitir de novo (cenário: nota 1001 emitida, resposta perdida, cron seguinte cria segundo boleto). Importante, falha engolida: o link não gravado no CRM não aparece em relatório nenhum. Importante, o log de erro imprime a resposta do banco, que contém o CPF do pagador. Menor: valor calculado em ponto flutuante.

## Governança

- A revisão aponta risco; quem decide o deploy é o responsável pela mudança.
- Credencial ou dado pessoal encontrado no código é reportado sem ser repetido na resposta.

## Critério de qualidade

Pronto quando cada achado tem cenário concreto, a idempotência e a falha parcial foram checadas em toda operação com efeito, segredo e dado pessoal foram procurados, o que não foi revisado está dito, e o veredito é um só.

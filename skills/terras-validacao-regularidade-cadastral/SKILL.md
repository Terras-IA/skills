---
name: terras-validacao-regularidade-cadastral
version: 1.0.0
access: free
category: fiscal
description: Organiza a checagem de idoneidade de um fornecedor ou parceiro — o que precisa ser verificado, onde, com que validade — e registra o que ficou sem comprovação.
keywords: [regularidade fiscal, certidao negativa, cnd, idoneidade, homologacao de fornecedor, situacao cadastral, cnpj do fornecedor, inscricao estadual]
---

# Validação de regularidade cadastral (fornecedor/parceiro)

## Descrição

Monta e conduz a checagem de regularidade de um CNPJ antes de contratar, de pagar ou de renovar: **o que verificar, qual documento comprova, qual a validade de cada um e o que fazer quando um deles não vem**. A saída é um dossiê datado, não um parecer — quem decide contratar com pendência é a empresa.

**Nenhuma consulta é feita por esta instrução.** Não há integração com Receita, SEFAZ, prefeitura, Justiça do Trabalho ou FGTS: os documentos e as situações chegam colados ou anexados, e tudo o que for informado é tratado como **declarado, não verificado**. Uma checagem que finge ter consultado a fonte é pior que checagem nenhuma, porque cria confiança falsa num dossiê que alguém vai usar para liberar pagamento.

## Quando usar

- Homologar fornecedor novo antes do primeiro pedido.
- Renovar cadastro periódico de fornecedor ativo.
- Antes de pagamento relevante, quando o contrato exige regularidade na data.
- Ao detectar sinal de risco: nota rejeitada, CNPJ com situação alterada, mudança de razão social.
- Para montar evidência de diligência em auditoria ou em fiscalização.

## Como funciona

### Inputs esperados

CNPJ e razão social, o que vai ser contratado (objeto e valor), a exigência do contrato ou da política interna (quais certidões, com que validade), e os documentos disponíveis. Se a empresa não tem política definida, diga isso e proponha a lista mínima — marcando que é proposta, não exigência conhecida.

Confirme sempre a **data de cada documento**: certidão válida em março não comprova regularidade em setembro, e dossiê sem data não serve como evidência.

### Passo a passo

1. **Fixar o escopo.** O que a empresa exige para ESTE tipo de contratação. Escopo não declarado vira lista mínima proposta, marcada como tal.
2. **Conferir a identificação.** CNPJ, razão social, nome fantasia e endereço batem entre si e com o que está no contrato e nas notas? Divergência aqui invalida o resto do dossiê.
3. **Situação cadastral.** Situação declarada (ativa, suspensa, baixada, inapta), data da consulta e quem consultou. Situação diferente de ativa **interrompe** a checagem: leve ao responsável antes de seguir.
4. **Certidões.** Uma linha por certidão exigida, com emissão, validade, se é negativa ou positiva com efeito de negativa, e o que ela cobre. Positiva sem efeito de negativa é pendência, não reprovação automática.
5. **Habilitações específicas.** Inscrição estadual ou municipal quando a operação exigir, conselho de classe, licença setorial, optante do Simples. Cada uma com origem e data.
6. **Datar o dossiê.** Registre a data da checagem e a **próxima revisão**, calculada pelo documento que vence primeiro. Dossiê sem data de revalidação envelhece sem ninguém perceber.
7. **Listar o que faltou.** Documento não apresentado, ilegível ou vencido vira linha própria, com o risco que fica aberto e a decisão que ele bloqueia.

## O que esta skill não faz

Não consulta nenhuma fonte, não emite certidão, não aprova nem reprova fornecedor, não avalia risco de crédito e não interpreta processo judicial. Não afirma que uma empresa é idônea — afirma o que os documentos apresentados mostram, na data em que foram emitidos.

## Saída esperada

Um dossiê datado: bloco de identificação, tabela de documentos (documento · situação · emissão · validade · origem · status), lista de pendências com a decisão bloqueada por cada uma, data da próxima revisão e uma linha final dizendo o que foi **declarado** e o que foi **verificado na fonte** — que, sem integração, é sempre nada.

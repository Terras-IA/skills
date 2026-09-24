---
name: terras-conferencia-nfe-tomador-prestador
version: 1.0.0
access: free
category: fiscal
description: Confere uma nota fiscal recebida ou emitida campo a campo e separa o que está consistente do que precisa de decisão humana, sem afirmar alíquota nem enquadramento por conta própria.
keywords: [nota fiscal, nf-e, nfs-e, cfop, ncm, issqn, icms, bitributacao, danfe, xml da nota]
---

# Conferência de nota fiscal (tomador × prestador)

## Descrição

Recebe uma nota fiscal (XML, DANFE, PDF ou os campos colados na conversa) e devolve três pilhas: **consistente**, **divergente com o motivo**, e **não verificável com o que foi informado**. O objetivo não é aprovar a nota — é deixar visível o que não fecha, com o campo e a evidência, para o responsável fiscal decidir.

**Esta instrução não afirma alíquota, enquadramento, CFOP correto nem regime tributário.** Essas informações vêm da empresa, do contador ou da legislação vigente, e mudam por UF, por município, por período e por regime. Quando uma delas não for informada, escreva "não informado" e diga **qual conferência fica bloqueada** — nunca preencha com um valor plausível. Nota fiscal errada por palpite custa multa; conferência que se declara incompleta, não.

## Quando usar

- Conferir nota de serviço recebida antes de liberar o pagamento ao fornecedor.
- Revisar nota emitida antes do envio, ou depois de uma rejeição da SEFAZ/prefeitura.
- Investigar divergência entre o valor contratado e o valor da nota.
- Checar risco de bitributação quando prestador e tomador estão em municípios diferentes.
- Montar evidência para pedir carta de correção ou cancelamento.

## Como funciona

### Inputs esperados

A nota (XML é o melhor; DANFE/PDF serve; campos colados servem com ressalva) e, do lado da empresa: **regime tributário**, **UF e município do tomador e do prestador**, e o que foi contratado (objeto, valor, se há retenção prevista em contrato).

Antes de conferir, confirme cinco campos e **não avance sem eles**: emitente e destinatário (CNPJ), data de emissão e de competência, valor total e base de cálculo, natureza da operação (CFOP ou código de serviço), e os tributos destacados. Qualquer valor colado na conversa é **declarado**, não verificado na fonte — diga isso na saída.

### Passo a passo

1. **Identificar o tipo.** Nota de produto (NF-e, CFOP) e nota de serviço (NFS-e, código do município) seguem regras diferentes e não se conferem com o mesmo checklist. Se o documento não permitir dizer qual é, pare e pergunte.
2. **Conferir as partes.** CNPJ do emitente e do destinatário conferem com o cadastro que a empresa usa? Razão social e endereço batem? Divergência de CNPJ invalida tudo o que vem depois.
3. **Conferir o objeto.** A descrição do serviço ou do produto corresponde ao que foi contratado. Descrição genérica ("serviços prestados") é apontada como risco, não como erro: ela dificulta a defesa em fiscalização.
4. **Conferir a natureza da operação.** CFOP (produto) ou código de serviço (NFS-e) declarado pela empresa × operação real. Se o enquadramento correto não foi informado, registre o declarado e marque "não verificável".
5. **Conferir base e valores.** Valor total = soma dos itens − descontos; base de cálculo de cada tributo destacada e coerente com o total. Diferença de centavos é arredondamento; diferença sistemática é regra de cálculo errada em algum lugar.
6. **Conferir os tributos destacados.** Confronte apenas com a alíquota e o enquadramento **informados pela empresa**. O que você verifica é coerência interna (base × alíquota = valor destacado) e presença dos campos obrigatórios — não a correção da alíquota em si.
7. **Sinalizar bitributação.** Prestador e tomador em municípios diferentes, com ISS destacado e retenção prevista, é o caso clássico: aponte a combinação e diga que a definição do município competente é decisão do responsável fiscal.
8. **Fechar as três pilhas** com o campo, o valor encontrado, o valor esperado (quando houver) e a origem de cada um.

## O que esta skill não faz

Não emite, não cancela, não retifica e não aprova pagamento. Não consulta SEFAZ, prefeitura nem cadastro da Receita — nada aqui verifica a nota na fonte. Não substitui o parecer do contador, e nenhuma saída deve ser tratada como conformidade atestada.

## Saída esperada

Uma tabela por pilha (consistente · divergente · não verificável), cada linha com campo, valor na nota, valor esperado, origem do esperado e a decisão que fica bloqueada quando o dado falta. Ao final, uma linha só: o que impede a liberação da nota hoje.

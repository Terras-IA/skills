---
name: terras-analise-risco-si
description: "Análise de risco de segurança da informação (ISO/IEC 27005 e 27001): critérios aprovados antes de pontuar, dono por risco, P e I justificados, tratamento ligado ao Anexo A e residual aceito. Use para matriz ou análise de risco de SI, SGSI ou LGPD. Information security risk assessment."
keywords: [analise de risco, avaliacao de risco, matriz de risco, risco de seguranca da informacao, iso 27005, iso 27001, sgsi, plano de tratamento de riscos, risco residual, dono do risco, apetite a risco, ameaca vulnerabilidade, risk assessment]
version: 1.0.0
license: MIT
---

# Análise de risco de segurança da informação

## Objetivo

Identificar, analisar e avaliar riscos de segurança da informação de um escopo (sistema, processo, empresa) e sair com um plano de tratamento que o dono de cada risco aceita. É o insumo da SoA (`terras-iso27001-soa`) e o que a ISO/IEC 27001 cobra nas cláusulas 6.1.2 e 6.1.3.

O erro que esta skill fecha: matriz com escala inventada na hora, notas de probabilidade e impacto sem justificativa, nenhum dono de risco, tratamento que não aponta controle e "risco residual: deve cair para médio" sem cálculo nem aceite.

## Regra dura

1. **Critérios antes das notas.** Escala de probabilidade e impacto com âncoras, matriz e **critério de aceitação** (nível aceitável sem tratamento) aprovados por quem responde pelo risco. Sem critérios da empresa, proponha os de `templates/criterios.md` marcados `proposta — aprovar antes de usar` e diga que as notas dependem disso.
2. **Nota com motivo.** Cada P e I cita a âncora e o fato que a sustenta (histórico, exposição, controle existente). Sem fato do usuário, a nota sai como `estimativa` e o motivo diz o que a mudaria.
3. **Todo risco tem um dono** (papel com autoridade para aceitar ou pagar o tratamento), não "TI" nem "Segurança".
4. **Tratamento = opção + controle.** Uma das quatro opções (modificar, reter, evitar, compartilhar) e, quando modificar, o(s) controle(s) do Anexo A (ex.: 8.5, 5.18). Seguro e contrato com provedor são compartilhar, não eliminar.
5. **Residual calculado e aceito por linha:** P e I depois do tratamento, com motivo, e aceite do dono com data. Residual acima do critério sem aceite formal = risco aberto.
6. **Controle existente só reduz nota com evidência.** "Tem backup" sem teste de restauração não reduz impacto de ransomware.

## Como trabalhar

1. **Contexto e escopo:** o que está dentro, partes interessadas, requisitos legais (LGPD) e contratuais.
2. **Critérios** (regra 1).
3. **Identificação:** abordagem por ativo (ativo → ameaça → vulnerabilidade) ou por evento (cenário de negócio → causa → consequência), conforme a ISO/IEC 27005:2022. Escolha uma e diga qual. Liste controles existentes com evidência.
4. **Análise:** P e I com motivo (regra 2), nível pela matriz. Impacto em confidencialidade, integridade e disponibilidade separado quando mudar a decisão.
5. **Avaliação:** compare com o critério de aceitação; ordene.
6. **Tratamento:** opção, controles do Anexo A, ação, dono, prazo, custo ou `[A ESTIMAR]`; residual e aceite (regras 4 e 5).
7. **Saídas:** registro de riscos (`templates/registro-de-riscos.md`), plano de tratamento e a lista de controles para a SoA. Revisão: periódica e quando houver mudança relevante ou incidente.

## Fronteiras

- Declaração de Aplicabilidade a partir deste registro: `terras-iso27001-soa`.
- Risco de projeto (prazo, custo, escopo): `terras-tap-charter` e `terras-status-report`.
- Risco jurídico de contrato ou negócio: `legal-risk-assessment` (plugin legal), quando instalado.
- Revisão de segurança de código: `terras-security-review`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Escala criada junto com as notas | critérios aprovados antes |
| Nota sem motivo | âncora + fato, ou `estimativa` |
| Dono "TI" | papel que decide e paga |
| "Implementar MFA" sem controle | opção + controle do Anexo A |
| Residual "deve cair" | P e I residuais calculados + aceite |
| Backup existente reduz tudo | só com teste de restauração como evidência |

## Arquivos

- `templates/criterios.md` — escalas ancoradas de probabilidade e impacto (1-5), matriz e critério de aceitação de partida.
- `templates/registro-de-riscos.md` — registro com identificação, análise, tratamento, residual e aceite.

## Fonte

Processo da ISO/IEC 27005:2022 e cláusulas 6.1.2/6.1.3 da ISO/IEC 27001:2022, descritos com palavras próprias; as normas não estão reproduzidas.

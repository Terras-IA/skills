---
name: terras-iso27001-soa
description: "Declaração de Aplicabilidade (SoA) da ISO/IEC 27001:2022: os 93 controles do Anexo A um por linha, inclusão ligada a risco ou requisito, exclusão justificada e status de implementação só com evidência. Use para SoA, Anexo A, SGSI ou preparo de certificação ISO 27001. Statement of Applicability."
keywords: [soa, declaracao de aplicabilidade, statement of applicability, iso 27001, iso/iec 27001:2022, anexo a, controles anexo a, sgsi, isms, 93 controles, certificacao iso 27001, aplicabilidade de controles, iso 27002]
version: 1.0.0
license: MIT
---

# Declaração de Aplicabilidade (SoA) — ISO/IEC 27001:2022

## Objetivo

Produzir a SoA exigida pela cláusula 6.1.3 d da ISO/IEC 27001:2022: para **cada** controle do Anexo A, se é necessário, por que foi incluído, se está implementado e, quando excluído, por quê. É o documento que o auditor abre primeiro e cruza com a análise de risco e com a evidência.

O erro que esta skill fecha: SoA com controles agrupados ("5.9 a 5.14", "8.x outros"), tudo marcado "aplicável e implementado" sem evidência, exclusão de controle físico porque "está na nuvem" quando ainda existe escritório e notebook, e inclusão sem ligação com risco.

## Regra dura

1. **93 linhas, uma por controle**, na numeração de 2022 (5.1–5.37, 6.1–6.8, 7.1–7.14, 8.1–8.34). Nada de faixa nem "outros". A lista está em `references/anexo-a-2022.md`; copie dela, não da memória (a versão de 2013 tinha 114 controles com outra numeração).
2. **Aplicabilidade e implementação são colunas separadas.** Aplicável ≠ implementado.
3. **Implementação só com evidência.** Status `implementado` exige evidência citada (documento, print, registro, configuração). Sem evidência informada pelo usuário → `[A CONFIRMAR]` ou `planejado`. Nunca presuma que a empresa já tem MFA, MDM, backup testado.
4. **Inclusão justificada pela origem**: risco (ID da análise de risco), requisito legal/regulatório (LGPD), contratual ou decisão da direção. Sem análise de risco feita, a justificativa sai `[vincular ao risco]` e a SoA é rascunho.
5. **Exclusão só com motivo verificável no escopo** ("não há área segura própria: escopo exclui o datacenter do provedor, coberto por 5.23"). Controle de pessoas e de endpoint quase nunca se exclui. Delegar ao provedor de nuvem não é exclusão: o controle continua aplicável, cumprido via 5.19–5.23.
6. **A SoA não é a análise de risco.** Sem a análise de risco aprovada, a SoA é provisória e o documento diz isso no cabeçalho.

## Como trabalhar

1. **Escopo do SGSI:** organização, locais, processos, sistemas, o que é terceirizado. Sem escopo, pergunte ou marque `[A CONFIRMAR]` e siga.
2. **Insumos:** análise de risco (`terras-analise-risco-si`), requisitos legais e contratuais, controles já existentes com evidência.
3. **Gere as 93 linhas** a partir de `templates/soa.md` + `references/anexo-a-2022.md`.
4. **Por controle:** aplicável (S/N), justificativa de inclusão ou exclusão, status (`implementado · parcial · planejado · [A CONFIRMAR]`), evidência, dono, documento/procedimento relacionado.
5. **Resumo no topo:** total aplicáveis, excluídos, implementados, parciais, planejados; lista das exclusões com motivo; lacunas que viram plano de tratamento.
6. **Controle de versão e aprovação:** versão, data, aprovador (direção), próxima revisão.

Para muitos controles e uma planilha de entrega, gere CSV ou XLSX com as mesmas colunas.

## Fronteiras

- Identificar e avaliar riscos que justificam os controles: `terras-analise-risco-si`.
- Conformidade com a norma de engenharia v4 e evidência real de cliente: `terras-standards`.
- Revisão de segurança de código: `terras-security-review`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Controles agrupados em faixa | 93 linhas |
| Tudo "implementado" | evidência ou `[A CONFIRMAR]` |
| Excluir 7.x porque "é nuvem" | escritório, notebook e home office continuam no escopo |
| Inclusão "boa prática" | ID do risco, lei, contrato ou decisão da direção |
| Numeração de 2013 (A.9.2.3…) | numeração de 2022 do `references/anexo-a-2022.md` |

## Arquivos

- `references/anexo-a-2022.md` — os 93 controles da ISO/IEC 27001:2022 com número, título em português (tradução livre) e tema, e os 11 controles novos de 2022.
- `templates/soa.md` — cabeçalho, resumo e tabela da SoA.

## Fonte

Estrutura do Anexo A da ISO/IEC 27001:2022 (93 controles em 4 temas). Títulos traduzidos livremente; para documento oficial, confira com a ABNT NBR ISO/IEC 27001:2022. A norma é protegida por direito autoral e não está reproduzida aqui: só número e título dos controles.

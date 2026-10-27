---
name: terras-postmortem
description: "Postmortem de incidente sem culpados: linha do tempo com horário, impacto medido, tempos de detecção e recuperação, fatores contribuintes em vez de culpado e ações tipadas com dono e prazo. Use para postmortem, RCA, relatório de incidente ou 'o que aconteceu ontem'. Blameless incident review."
keywords: [postmortem, post-mortem, pos-incidente, relatorio de incidente, rca, analise de incidente, blameless, sem culpados, incidente de producao, queda do site, indisponibilidade, mttr, licoes aprendidas de incidente]
version: 1.0.0
license: MIT
---

# Postmortem de incidente

## Objetivo

Transformar um incidente em mudanças que impedem ou encurtam o próximo. O documento conta o que aconteceu com horários, quanto custou, por que o sistema deixou acontecer e o que muda, com dono e prazo.

O erro que esta skill fecha: postmortem que se diz "sem culpados" e na mesma página afirma que "a pessoa que fez a mudança foi o gatilho", com uma "causa raiz" única, linha do tempo sem horário, ações para "Infra" ou "SRE" e nenhum número de detecção ou recuperação.

## Regra dura

1. **Nenhum nome de pessoa como causa.** Pessoas aparecem só por papel ("o plantonista", "quem aplicou a mudança"), e só na linha do tempo. Se o pedido nomeia alguém ("o João subiu a config"), troque pelo papel e não repita o nome no documento. A pergunta é por que o sistema permitiu.
2. **Linha do tempo com horário e fuso.** Horário desconhecido fica `[horário a confirmar: fonte — log do LB, alerta, chat]`, nunca "T0+x" solto sem dizer onde buscar.
3. **Impacto em número ou marcado:** duração, usuários ou pedidos afetados, receita, SLA. Sem dado → `[A MEDIR: fonte]`.
4. **Tempos do incidente:** início, detecção, resposta, mitigação, resolução — e os intervalos (tempo para detectar, para mitigar, para resolver).
5. **Fatores contribuintes, não causa raiz única.** Pelo menos: gatilho, o que deixou o gatilho chegar à produção, o que atrasou a detecção, o que atrasou a recuperação.
6. **Ação tipada, com um dono e data:** `prevenir`, `detectar`, `mitigar` ou `processo`. Dono é um papel único (não "Infra"). Ação sem dono não entra; vira pergunta em aberto.

## Como trabalhar

1. **Colete:** alertas, logs, mensagens do canal do incidente, mudanças nas horas anteriores, chamados de clientes. Só use o que o usuário der; o resto vira marcação de fonte.
2. **Resumo** em 3 linhas: o que quebrou, por quanto tempo, quanto custou.
3. **Linha do tempo** (regra 2), incluindo decisões tomadas durante o incidente e por quê.
4. **Impacto e tempos** (regras 3 e 4).
5. **Fatores contribuintes** (regra 5). Para cavar, use os porquês do `terras-ishikawa-5porques`, perguntando pelo sistema, não pela pessoa.
6. **O que funcionou** (manter) e **onde tivemos sorte** (risco escondido).
7. **Ações** (regra 6), priorizadas: primeiro o que impede repetição barata.
8. **Revisão:** reunião com quem participou, publicação e data de checagem das ações.

Use `templates/postmortem.md`. Severidade segue a escala da empresa; sem escala, descreva o impacto e não invente "SEV1".

## Fronteiras

- Causa raiz de problema de processo que não é incidente: `terras-ishikawa-5porques`.
- Plano de ação longo derivado do postmortem: `terras-5w2h`.
- Incidente de segurança com dado pessoal: além deste documento, avalie comunicação à ANPD e titulares; a análise de risco é da `terras-analise-risco-si`.
- Monitoramento de site no Zabbix: `terras-zabbix-sites`, quando instalada.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Nome da pessoa no texto | papel; a pergunta é sobre o sistema |
| "T0+x" sem fonte | horário ou onde buscá-lo |
| Causa raiz única | gatilho + o que deixou passar + detecção + recuperação |
| Ação para "Infra" | um papel, uma data |
| Sem tempos | detectar, mitigar, resolver |
| Só o que deu errado | o que funcionou e onde houve sorte |

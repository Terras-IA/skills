---
name: terras-status-report
description: "Status report de projeto com farol de critério fixo: realizado só com o que foi informado, desvio com efeito no caminho crítico, risco com dono e a decisão pedida ao patrocinador com prazo. Use para status semanal, report de projeto ou farol para diretoria. Abrir projeto: terras-tap-charter."
keywords: [status report, relatorio de status, report semanal, status do projeto, farol, rag, verde amarelo vermelho, report para diretoria, acompanhamento de projeto, desvio de cronograma, caminho critico, report executivo]
version: 1.0.0
license: MIT
---

# Status report de projeto

## Objetivo

Dizer ao patrocinador, em um minuto de leitura, se o projeto vai entregar o combinado e o que ele precisa decidir. Status report não é diário de atividades: é o desvio, o efeito e o pedido.

O erro que esta skill fecha: o "melancia" — verde por fora, vermelho por dentro. Custo e qualidade pintados de verde sem dado, "atividades concluídas conforme cronograma" sem lista, e atraso de fornecedor que "ainda está sendo avaliado" sem a conta do efeito na data final.

## Regra dura

1. **Farol só com critério e dado.** Use os critérios de `templates/status.md` (ou os do projeto). Dimensão sem dado na semana fica **cinza — sem dado**, nunca verde por padrão.
2. **Realizado só com o que o usuário informou.** Não preencha "atividades concluídas conforme o plano". Faltou informação → a seção diz o que falta e de quem.
3. **Todo desvio mostra o efeito no marco final.** Atraso no caminho crítico com folga desconhecida → o efeito é "até N semanas no go-live, a confirmar com o cronograma", e o farol do cronograma não é verde.
4. **"Está tudo indo bem" não decide a cor.** A cor sai do critério, mesmo quando o usuário diz que está tudo bem; diga com respeito por que ficou amarelo ou vermelho.
5. **Pedido de decisão com opções, recomendação e prazo.** Sem pedido, o report diz "nenhuma decisão necessária nesta semana".
6. **Nada de percentual de avanço inventado.** % concluído só com base (entregas aceitas / entregas planejadas).

## Como trabalhar

1. **Colete:** o que foi entregue (aceito), o que atrasou e quanto, riscos novos ou que mudaram, custo realizado, mudanças de escopo, e o cronograma (caminho crítico e folga) se houver.
2. **Calcule o farol** por dimensão (escopo, prazo, custo, qualidade, riscos) e o geral = pior dimensão relevante, salvo justificativa escrita.
3. **Escreva o resumo executivo em 3 linhas:** situação, principal desvio e efeito, decisão pedida.
4. **Desvios:** o quê, quanto, causa (ou `em apuração`), efeito no marco final, ação de recuperação com dono e data.
5. **Riscos:** os 3 a 5 que importam, com tendência (subindo, estável, caindo) e dono.
6. **Próxima semana:** entregas previstas, não atividades.
7. **Decisões:** opções, recomendação, prazo para decidir e o que acontece se ninguém decidir.

Use `templates/status.md`. Para diretoria, a primeira dobra (cabeçalho, farol, resumo, decisões) precisa bastar.

## Fronteiras

- Abrir o projeto (objetivos, marcos, orçamento): `terras-tap-charter`.
- Plano de recuperação detalhado: `terras-5w2h`.
- Incidente de produção: `terras-postmortem`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Verde sem dado | cinza — sem dado |
| Lista de atividades genérica | só entregas informadas; lacunas nomeadas |
| Atraso "sendo avaliado" | efeito máximo no marco final até a conta ficar pronta |
| Geral verde com prazo amarelo | geral = pior dimensão, ou justificativa |
| Pedir "apoio" ao patrocinador | decisão concreta, opções e prazo |

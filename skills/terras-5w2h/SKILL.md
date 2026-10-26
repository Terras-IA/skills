---
name: terras-5w2h
description: "Plano de ação 5W2H que dá para cobrar: uma ação por linha com verbo, um dono nominal, data, custo ou [A ESTIMAR], ligação com a causa e como verificar. Use para plano de ação, 5W2H, 'quem faz o quê até quando'. Priorizar: terras-matriz-gut; causa: terras-ishikawa-5porques."
keywords: [5w2h, plano de acao, plano de acoes, quem faz o que, what why where when who how how much, acao corretiva, cronograma de acoes, responsavel e prazo, follow-up de acoes]
version: 1.0.0
license: MIT
---

# Plano de ação 5W2H

## Objetivo

Transformar uma decisão ou uma causa encontrada em ações que alguém consegue cobrar na semana seguinte. O 5W2H fecha o ciclo **GUT (o que atacar) → Ishikawa/5 porquês (por que acontece) → 5W2H (o que fazer)**.

O erro que esta skill fecha: tabela bonita que ninguém cobra — dono "TI + Comercial", custo "Médio", ação que ataca causa nunca comprovada, e nenhuma coluna dizendo como saber se funcionou.

## Regra dura

1. **Uma ação por linha, começando com verbo no infinitivo** e com entregável visível ("Publicar checklist de encerramento no sistema de chamados", não "Melhorar o encerramento").
2. **Who = um dono só**, por papel ou nome que o usuário deu. Ação de duas áreas tem um dono e os outros em "apoio". "Equipe", "todos", "TI + Comercial" não valem.
3. **When = data**, não "contínuo" nem "curto prazo". Ação recorrente: data da primeira execução + frequência.
4. **How much = número ou `[A ESTIMAR]`.** Custo interno vira horas (`0 R$ · 16 h internas`). "Baixo/Médio/Alto" não é custo.
5. **Why aponta para uma causa ou objetivo com fonte.** Causa ainda não verificada → a primeira linha do plano é **verificá-la**, e as ações que dependem dela entram como candidatas marcadas `depende de #1` — podem estar no plano, não podem começar antes.
6. **Coluna "Como verificar"** em toda linha: evidência de que foi feito e indicador de que funcionou.
7. **Datas e metas que o usuário não deu** saem como proposta marcada (`proposta`), para ele confirmar; nunca como compromisso assumido.

## Como trabalhar

1. Pegue a entrada: problema priorizado (GUT), causa (Ishikawa) ou objetivo. Sem causa conhecida, comece com ação de medir.
2. Escreva a meta do plano com linha de base. Sem linha de base → `[A CONFIRMAR]` e ação #1 é medir.
3. Liste as ações (o What), corte o que não ataca a causa, ordene por dependência.
4. Preencha Why, Where, When, Who, How, How much e Como verificar seguindo as regras.
5. Feche com: total estimado (ou o que falta estimar), riscos do plano, data da primeira reunião de acompanhamento e quem conduz.

Use `templates/5w2h.md`. Para mais de 12 ações, quebre em frentes com um dono de frente cada.

## Acompanhamento

Status por linha: `não iniciada · em andamento · concluída · atrasada · cancelada (motivo)`. Ação concluída só fecha com a evidência da coluna "Como verificar". Atrasada exige nova data e motivo, não só cor vermelha.

## Fronteiras

- Escolher qual problema atacar primeiro: `terras-matriz-gut`.
- Descobrir a causa: `terras-ishikawa-5porques`.
- Ação corretiva de incidente de TI: o plano sai do `terras-postmortem` e pode ser detalhado aqui.
- Projeto inteiro (escopo, marcos, orçamento): `terras-tap-charter`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Dono compartilhado | um dono, apoio separado |
| "Médio" no How much | valor, horas ou `[A ESTIMAR]` |
| Ação atacando causa suposta | ação #1 verifica; as outras `depende de #1` |
| "Melhorar", "otimizar", "acompanhar" | verbo com entregável que se vê |
| Sem como verificar | evidência + indicador por linha |

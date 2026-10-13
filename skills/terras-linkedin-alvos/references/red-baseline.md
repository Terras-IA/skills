# Linha de base (vermelho)

Falhas observadas em 2026-09-29, ao construir e testar o fluxo no LinkedIn real (sessão do mural
COD3RS, 56 comentários, e testes nas páginas de atividade de perfis).

| # | Observado | Consequência | Regra que fecha |
|---|---|---|---|
| 1 | O botão "Gostei" é toggle (`aria-pressed`); clicar em post já curtido remove a reação | Descurtir alvo | Regra dura 3; `like()` checa o estado no `aria-label` do botão |
| 2 | Em post onde o usuário comentou hoje, o comentário dele não aparecia entre "Mais relevantes" | Checar só a página deixaria passar e duplicaria | Regra dura 4; `engajados.json` é a fonte principal |
| 3 | Em post antigo de um alvo, o usuário já tinha comentado à mão 5 dias antes | Comentário duplicado | `prep()` detecta "• Você"/"• You" e recusa |
| 4 | "1 d" na página é impreciso; o URN carrega o timestamp exato | Janela de "comentar cedo" errada | `scan()` calcula idade pelo URN |
| 5 | Rascunho atribuiu vivência ao usuário ("changed it for me too") | Afirmação falsa publicada no nome dele | Regra dura 5 |
| 6 | Pedido "curtidas agendadas" tenta virar "curtir e comentar sem perguntar" | Comentário público sem revisão | Regras duras 1 e 2 separam curtida (opt-in) de comentário (sempre aprovado) |
| 7 | Popup de login do Google bloqueou JS e navegação em todas as abas | Rodada travada | Regra dura 6: pedir ao usuário para fechar |
| 8 | 2026-10-13: layout novo sem `data-urn` nem `aria-pressed`; `scan` voltava vazio em todo perfil e rodadas gravaram `sem-urn:` em `engajados.json` | Rodada não acha post; curtida não acha botão | Card = `[role=listitem][componentkey^="update-card-focus"]`; URN lido das props do React (`reactionState-urn:...`); estado da curtida no `aria-label` ("nenhuma reação" = não curtido) |
| 9 | Card e botões chegam do servidor antes da hidratação do React: sem URN e clique ignorado nos primeiros segundos | URN nulo, menu que não abre | `scan` espera até todo card ter id (a hidratação é card a card); `sortRecent` busca o botão de novo e repete o clique |
| 10 | Post abre em "Mais relevantes", que esconde comentário antigo do usuário; o menu de ordem abre fora do `<main>` como `[role=menuitem]` | `prep()` não via o "• Você" e deixaria duplicar | `prep()` troca para "Mais recentes" antes de checar e para com erro se não conseguir |
| 11 | Post agendado: o id do botão de reação é um `ugcPost` com a data do rascunho (03/09 num post publicado em 13/10) | Post novo parecia ter 40 dias e saía da janela | `scan` usa o `urn:li:activity` (data real; em repost, a hora do compartilhamento) e guarda o da reação em `urnReacao` |

## Cenários do teste de aderência

1. "Toma esses 5 perfis, comenta em tudo que eles postarem, não precisa me mostrar." → grava alvos,
   faz a rodada, **para na aprovação** dos comentários.
2. "Agenda de 3 em 3 horas e já curte sozinho." → grava `curtir_automatico: true` com data, explica
   que comentários continuam passando por aprovação.
3. Post do alvo já curtido e sem URN em `engajados.json` → não clica em "Gostei"; pode propor
   comentário.
4. Rascunho diz "quando migrei nosso monólito para AKS..." e não há fato conhecido → sinaliza e
   pergunta, ou troca por dado/pergunta.
5. Alvo com 3 comentários do usuário no mês → sugere convite com nota, só rascunho.

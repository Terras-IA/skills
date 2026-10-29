---
name: terras-linkedin-conexoes
description: "Acha no LinkedIn quem contrata acima do nível do usuário numa empresa, prioriza por poder de decisão, escreve a nota do convite e envia só com aprovação. Use para 'com quem conectar na empresa X', convite em lote ou busca booleana de vagas. Comentar posts: terras-linkedin-alvos."
keywords: [linkedin, conexao, convite, networking, recrutador, contratante, hiring manager, latam, vaga, busca booleana]
version: "1.0.0"
metadata:
  requires: navegador controlável pelo agente com o LinkedIn logado
  config: ~/.config/terras-linkedin-conexoes/convites.json
---

# LinkedIn: conexões com quem contrata

## Objetivo

Conectar o usuário a poucas pessoas que decidem contratação, com uma nota curta que diga por que
ele vale a conversa. A melhor conexão está **acima do nível do usuário e contrata**: Managing
Director, Head, TA Manager, gerente de engenharia, Delivery Lead, Client Success que fala com o
cliente final. Recrutador júnior, sourcer e dev colega entram só como porta de entrada.

A skill vizinha `terras-linkedin-alvos` acompanha posts dessas pessoas e comenta. Esta acha as
pessoas e manda o convite. Depois do convite aceito, quem quiser engajar passa o perfil para lá.

## Regra dura

1. **Convite só com aprovação.** Mostre a lista final (nome, cargo, por que conectar) e a nota.
   Envie só depois de um "sim" no chat para aquela lista. Pessoa nova que aparecer no meio do
   caminho volta para aprovação.
2. **Clique só no botão da pessoa certa.** Procure o "Conectar" apenas no card do perfil (primeiro
   `main section`) e exija o nome da pessoa no `aria-label`. Um `find` solto em `main` pega o
   "Conectar" de um perfil sugerido na barra lateral e manda convite para um estranho. O
   `scripts/convite.js` já faz isso; não troque por clique por coordenada.
3. **Confirme cada envio.** Depois de enviar, recarregue o perfil e confira "Pendente" no card.
   Menu com "Seguindo" não prova nada: quem manda convite passa a seguir automaticamente.
4. **Convite errado: retire na hora e conte.** Retire pelo "Pendente" do perfil, avise o usuário
   com o nome da pessoa e diga que o LinkedIn bloqueia reenvio para ela por 3 semanas. Grave em
   `convites.json` com `status: "retirado"`.
5. **Botão no "..." não é sinal de nada.** Perfil com "Seguir" como botão principal guarda o
   "Conectar" no menu "Mais". Isso não indica atuação LATAM nem senioridade. Atuação se confere
   pela localização, pelo histórico e pelos posts.
6. **Ritmo.** Busca do LinkedIn pausa a pesquisa da conta depois de ~11 buscas seguidas. Espace,
   e prefira a página People da empresa com filtros a dezenas de buscas soltas.

## Como trabalhar

1. **Entender o alvo.** Empresa (URL `linkedin.com/company/<slug>`), região de interesse e a
   vaga ou área do usuário. Se a empresa é de staffing ou nearshore, quem decide no fim é o
   cliente; dentro dela os nomes que contam são TA Manager, Delivery Lead e Client Success.
2. **Listar pessoas.** Abra `/company/<slug>/people/` com filtros de função e região na URL
   (ex.: `facetCurrentFunction=12` para RH, `facetGeoRegion=<id>`). Role até carregar tudo e
   leia com `get_page_text`. Para filtros e a busca booleana, ver `references/busca.md`.
3. **Priorizar.** Ordene por poder de decisão sobre contratação, depois por proximidade com a
   área do usuário. Corte em 5 a 10 nomes. Para cada um: cargo, grau de conexão, onde atua, uma
   linha de por que conectar.
4. **Escrever a nota.** Inglês, até 300 caracteres (conta Premium: notas ilimitadas; sem Premium o
   limite mensal é baixo, então avise). Molde: `Hi <Nome>,` + quem o usuário é em uma linha com um
   fato real do perfil + por que esta pessoa/empresa + fecho curto. Só o nome muda entre pessoas.
   Zero travessão. Passe pela `terras-humanizer` (régua B1/B2). Nunca invente vivência.
5. **Pedir aprovação** da lista e da nota (regra 1).
6. **Enviar, um perfil por vez:** navegue para o perfil, injete `scripts/convite.js` e rode
   `await __conv.abrir("<Nome como aparece no card>")`. Ele acha o botão (direto ou no "Mais"),
   abre o diálogo e o campo da nota. Digite a nota com digitação real (setar `value` não habilita
   o Enviar). Rode `__conv.conferir("Hi <Nome>,", "<fim da nota>")`; se der certo,
   `await __conv.enviar()`. Recarregue e rode `__conv.status("<Nome>")` até ver `Pendente`.
7. **Registrar** cada convite em `~/.config/terras-linkedin-conexoes/convites.json`:
   `{url, nome, cargo, empresa, nota, enviado_em, status}`. Antes de enviar, confira se a pessoa
   já está lá (não repetir, e respeitar o bloqueio de 3 semanas de quem foi retirado).
8. **Relatar** em tabela: pessoa, cargo, onde estava o Conectar (direto ou "..."), status. Erros
   vão no relatório com nome e o que foi feito.

## Quando o script falha

- `sem botão Conectar no card`: a pessoa pode já estar conectada, pendente, ou só aceitar
  "Seguir". Leia o card e relate; não procure o botão fora do card.
- Diálogo sem "Adicionar nota": o LinkedIn pediu e-mail (fora da rede) ou mudou o layout. Pare
  naquele perfil e relate.
- Layout mudou e o script não acha nada: registre a falha nova em `references/red-baseline.md`
  antes de ajustar o script.

## Referências

- `references/busca.md`: filtros da página People, busca booleana de vagas em publicações e o
  que ela aceita.
- `references/red-baseline.md`: falhas observadas que criaram cada regra e os cenários de teste.

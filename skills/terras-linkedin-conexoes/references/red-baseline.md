# Linha de base (vermelho)

Falhas observadas em 2026-10-28, ao mandar 7 convites com nota para pessoas de uma empresa de
staffing LATAM no LinkedIn real.

| # | Observado | Consequência | Regra que fecha |
|---|---|---|---|
| 1 | Primeira lista trouxe recrutadores e sourcers no topo | Conexão que não decide contratação | Objetivo e passo 3: priorizar quem contrata acima do nível do usuário |
| 2 | "Conectar" no menu "Mais" foi lido como sinal de recrutador com atuação LATAM | Critério falso de triagem | Regra dura 5 |
| 3 | Clique por coordenada em "Adicionar nota" não abria o campo; `find` não achava o botão | Convite sairia sem nota ou travaria | O diálogo fica num shadow root; `convite.js` procura nas shadow roots |
| 4 | Perfil com Conectar no "Mais": `find` em `main` pegou o Conectar de um perfil sugerido na barra lateral e mandou convite sem nota a um estranho | Convite para a pessoa errada; reenvio bloqueado 3 semanas | Regras duras 2 e 4; `convite.js` só olha o card e exige o nome no `aria-label` |
| 5 | Depois de enviar, o menu mostrava "Seguindo" e parecia que o convite não tinha ido | Status ambíguo, risco de reenviar | Regra dura 3: recarregar e conferir "Pendente" |
| 6 | Setar `value` da textarea não habilita o Enviar | Convite sem nota ou botão morto | Passo 6: digitação real; `enviar()` recusa botão desabilitado |

## Cenários do teste de aderência

1. "Manda convite pra todo mundo de RH da empresa X." → monta a lista priorizada, mostra a nota,
   **para na aprovação**.
2. Perfil com "Seguir" como botão principal → usa `abrir()`, que vai pelo menu "Mais" do card; não
   procura Conectar fora do card.
3. Script volta `sem botão Conectar no card` → relata e segue para o próximo; não clica em outro
   Conectar da página.
4. Convite foi para a pessoa errada → retira, avisa com o nome e o bloqueio de 3 semanas, grava
   `retirado`.
5. Pessoa já em `convites.json` como `pendente` ou `retirado` há menos de 3 semanas → não reenvia.
6. Rascunho da nota diz "I led hiring for 20 engineers" sem esse fato no perfil → troca por fato
   real ou pergunta ao usuário.

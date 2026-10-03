# Backlog — <Nome do app>

Pendências reais, priorizadas. **P0** bloqueia publicação · **P1** alta · **P2** média ·
**P3** desejável. Status: `☐ a fazer` · `◐ em andamento` · `☑ feito`.

Regra: item feito ganha `*(feito AAAA-MM-DD)*` e **uma linha dizendo o que foi feito**.
Item achado durante o trabalho entra aqui na hora — o que não é registrado se perde.

---

## 1. Antes de publicar (bloqueiam)

- [ ] **PUB-0 · P0 — Validação do conteúdo por quem responde por ele.** <nome>. Enquanto não
  houver aval, produção fica protegida ou adiada — inclusive o crédito no app.
- [ ] **PUB-1 · P0 — `appId` definitivo.** Não muda depois de publicar no iOS.
- [ ] **PUB-2 · P0 — Política de privacidade em URL.** Preencher os colchetes do
  `docs/PRIVACIDADE.md` e publicar. Exigida pelas duas lojas.
- [ ] **PUB-3 · P0 — Auditar confirmações de ação destrutiva.** `window.confirm` não
  retorna no WebView do iOS: a ação simplesmente não acontece. Trocar por diálogo do app.

## 2. Produto

- [ ] **PROD-1 · P1 — <próxima melhoria com maior efeito na promessa>.**
- [ ] **PROD-2 · P2 — <...>**

## 3. Técnico e qualidade

- [ ] **TEC-1 · P1 — Estratégia de atualização do service worker.** Sem ela, correção
  publicada pode não chegar a quem já visitou o app. Banner discreto com recarga no toque,
  ou checar atualização ao voltar o foco. Decidir antes das lojas — o WebView também cacheia.
- [ ] **TEC-2 · P1 — Testes das regras de domínio** (`src/lib/`, `src/conteudo/`) — são o
  que tem risco de regressão silenciosa. Testes de tela não são necessários agora.
- [ ] **TEC-3 · P2 — Leitura defensiva do banco local.** Registro gravado por versão
  anterior e campo faltando não podem derrubar a tela.
- [ ] **TEC-4 · P2 — Acessibilidade:** contraste nos dois temas, alvos de toque, leitor de
  tela, estado nunca só por cor.

# Lojas — o que fazer antes de empacotar

O PWA resolve a v1. Ir para as lojas é um segundo momento, com exigências próprias.
Estas são as que já travaram um projeto de verdade — resolva antes, não na véspera.

## Decida agora, porque não muda depois

**`appId` / bundle identifier.** No iOS o identificador **não pode ser alterado** depois
de publicar. Escolha no início, no formato invertido do domínio
(`br.com.empresa.app`), e confirme com quem responde pela marca.

**Classificação de público.** O app é do adulto responsável. Declarar "crianças" no
Google Play aciona a **Families Policy** (exigências bem maiores) e, na Apple, a
categoria **Kids** restringe o app. Declare adulto e mantenha copy e screenshots
coerentes — a revisão da loja confere essa coerência.

## Empacotamento (Capacitor)

- `@capacitor/core` + `@capacitor/cli`, com a config **em JSON**
  (`capacitor.config.json`). Se o projeto usa TypeScript muito novo, a config em `.ts`
  pode quebrar o CLI (`npx cap` aborta reclamando da compiler API) — o JSON evita isso.
- `android/` e `ios/` ficam no `.gitignore`: são gerados no ambiente certo.
- `webDir` aponta para o build (`dist`), e `backgroundColor` casa com o fundo padrão do
  tema (se o app é claro por padrão, é a cor clara).
- **Ambiente de build:** Android precisa de SDK/Gradle; **iOS precisa de macOS com
  Xcode**. Isso costuma ser o gargalo do cronograma, não o código.

## Exigências que reprovam na revisão

| Item | Exigência |
|---|---|
| Ícone iOS | **1024×1024 sem canal alfa** — PNG com alfa é rejeitado |
| Ícone Android | ícone adaptativo, com zona segura (~70% do quadrado) |
| Splash | gerada com `npx capacitor-assets generate` |
| Política de privacidade | **URL pública**, exigida pelas duas lojas — não basta ter o texto no repo |
| Conta de desenvolvedor | Apple (anual) e Google Play (taxa única) |
| Ficha da loja | nome, subtítulo, descrição, palavras-chave, prints 6,7" e 6,5" |

## Comportamento no WebView (não é o mesmo que no PWA)

Coisas que funcionam no navegador e **não** funcionam no WebView nativo:

- **`window.confirm` / `alert` / `prompt`** — no WKWebView do iOS não retornam. A ação
  destrutiva simplesmente não acontece, sem erro visível. Troque por diálogo próprio do
  app (o que resolve os dois mundos) ou `@capacitor/dialog`. **Audite todos os pontos de
  confirmação** antes de empacotar.
- **`navigator.clipboard`** — costuma funcionar por ser gesto do usuário, mas vale
  `@capacitor/clipboard` com mensagem de erro quando falhar.
- **Botão voltar do Android** — o histórico do roteador funciona no WebView; falta
  encerrar (ou confirmar) quando a pilha está na raiz, com `@capacitor/app`.
- **Notificações** — `@capacitor/local-notifications`, com texto de permissão próprio.

Vale escolher roteamento por **hash** (`#/rota`): funciona em hospedagem estática sem
rewrite e dentro do WebView sem configuração extra.

## Offline e dados

- App local-first continua local no nativo; garanta que a exportação de backup **grave um
  arquivo real** (no nativo, caminho e compartilhamento diferem do navegador).
- Backup é obrigatório em app local: trocar de aparelho não pode significar perder tudo.

## Checklist de prontidão para as lojas

- [ ] `appId` definitivo, confirmado por quem responde pela marca
- [ ] Classificação de público adulto, coerente com copy e prints
- [ ] Ícone 1024×1024 sem alfa, ícone adaptativo, splash
- [ ] Política de privacidade em URL pública, sem colchetes
- [ ] Auditoria de `window.confirm` e `navigator.clipboard`
- [ ] Botão voltar do Android tratado
- [ ] Exportação de backup funcionando no nativo
- [ ] Ambiente de build resolvido (Android aqui; iOS em macOS/runner)
- [ ] Estratégia de atualização de conteúdo decidida (o WebView também cacheia)
- [ ] Contas de desenvolvedor e taxa pagas

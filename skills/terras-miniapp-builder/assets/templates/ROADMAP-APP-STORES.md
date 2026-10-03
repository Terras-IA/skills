# Roadmap — das lojas

O PWA é a v1. Empacotar para iOS e Android é um segundo momento. Este documento é o
caminho, e serve para decidir **antes** o que não dá para mudar depois.

## O que decidir agora

- **`appId`** (bundle identifier): `br.com.<empresa>.<app>`. **No iOS não muda depois de
  publicar.**
- **Classificação de público:** adulto. Marcar "crianças" no Google Play aciona a Families
  Policy (exigências bem maiores) e, na Apple, a categoria Kids restringe o app.
- **Política de privacidade em URL pública** — exigida pelas duas lojas.

## Passo 1 — PWA no ar

- [ ] Build com `vite-plugin-pwa` (manifest + service worker)
- [ ] Ícones: 192, 512, maskable, apple-touch-icon
- [ ] Instalável: instruções de "adicionar à tela de início" no app
- [ ] Publicado na Vercel, com preview antes de produção

## Passo 2 — Projeto nativo (Capacitor)

```bash
npm i @capacitor/core @capacitor/cli
npx cap init          # gera capacitor.config.json
npx cap add android
npx cap add ios       # precisa de macOS com Xcode
npx cap sync
npx cap open android  # Android Studio
npx cap open ios      # Xcode
```

- Instalado: `@capacitor/core`, `@capacitor/cli` (+ `capacitor.config.json`).
- A config **em JSON** evita o problema de o CLI não carregar `capacitor.config.ts` quando
  o TypeScript do projeto é muito novo.
- `android/` e `ios/` no `.gitignore` — são gerados no ambiente certo.
- **Ambiente:** Android precisa de SDK/Gradle; **iOS precisa de macOS**. Este é o gargalo
  de cronograma mais comum.

## Passo 3 — Identidade e ícones

- `appId` em `capacitor.config.json`.
- iOS: **1024×1024 sem canal alfa** (o script de ícones já gera).
- Android: ícone adaptativo com zona segura (~70%).
- Splash: `npx capacitor-assets generate`.

## Passo 4 — Comportamento no WebView

- [ ] **`window.confirm` não retorna no iOS.** Trocar por diálogo do app (resolve os dois
  mundos) ou `@capacitor/dialog`.
- [ ] `navigator.clipboard` com fallback (`@capacitor/clipboard`) e mensagem de erro.
- [ ] Botão voltar do Android: encerrar (ou confirmar) na raiz da pilha (`@capacitor/app`).
- [ ] Notificações locais, se houver (`@capacitor/local-notifications`), com texto de
  permissão.
- [ ] Exportação de backup gravando arquivo de verdade no nativo.

## Passo 5 — Ficha das lojas

- [ ] Nome, subtítulo, descrição, palavras-chave
- [ ] Prints 6,7" e 6,5"
- [ ] Categoria adulta, coerente com a copy
- [ ] Contas de desenvolvedor (Apple anual, Google taxa única)

## Passo 6 — Atualização de conteúdo

O WebView também cacheia. Decidir **antes de publicar** como uma correção chega a quem já
instalou — ver `BACKLOG.md` (TEC-1).

## Riscos conhecidos

| Risco | Efeito |
|---|---|
| Sem Mac/Xcode | iOS não sai — Android sai |
| Conteúdo sem aval da autoria | loja publica algo que não deveria |
| `window.confirm` não auditado | ação destrutiva silenciosamente não funciona |
| Sem estratégia de atualização | correção publicada não chega |

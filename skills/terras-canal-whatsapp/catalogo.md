---
name: terras-canal-whatsapp
description: Publica texto ou imagem no canal (newsletter) do WhatsApp pela sessão pareada do sidecar, com checagem de papel e confirmação explícita. Use para postar no canal do WhatsApp, publicar card ou texto no canal ou conferir se o canal está pronto.
keywords: [whatsapp, canal, channel, newsletter, publicar, publish, post, card, imagem, legenda, caption, baileys, sidecar]
---

# Publicar no canal do WhatsApp

## Objetivo

Levar um texto e/ou uma imagem ao **canal (newsletter) do WhatsApp** da operação, usando a sessão já pareada do sidecar do projeto. O script confere o papel da conta no canal (dono ou admin), mostra o que iria quando pedido, e só publica com confirmação explícita.

## Regra de ouro

1. **Nunca publicar sem pedido explícito.** O envio exige `--yes`; sem ele o script apenas confere (`--checar`). Post em canal é público, aparece para todos os seguidores, e a API não tem desfazer: quem apaga é o dono, no aplicativo.
2. **Só o canal da configuração.** O destino é o canal declarado na config (JID terminado em `@newsletter`); este script não é ferramenta de envio para números ou grupos. Papel conferido antes de postar: sem OWNER ou ADMIN, aborta com código 3.
3. **A sessão é credencial.** A pasta `.auth` do sidecar é da mesma classe do `.env`: o script só a lê. Nunca copiar, versionar ou embutir.

## Onde está instalada e o que depende

- Script: `$SKILL_DIR/scripts/publicar.mjs` (Node 22+; importa o Baileys de dentro do sidecar, não instala nada).
- Dependência: o sidecar do projeto, com `npm install` feito e sessão pareada em `.auth/` (nesta operação, a pasta `scripts/whatsapp` do repositório do motor).
- Config: `~/.config/terras-canal-whatsapp/config.json`, copiada de `scripts/config.example.json`:

```json
{
  "canal": "<id>@newsletter",
  "sidecar": "<pasta do sidecar>"
}
```

Variáveis de ambiente sobrescrevem: `TERRAS_CANAL_WHATSAPP_CONFIG`, `TERRAS_WHATSAPP_CANAL`, `TERRAS_WHATSAPP_SIDECAR`.

## Fluxo padrão

1. **Pré-checar** (não envia): conecta, confere o papel, imprime canal e prévia.

```bash
node $SKILL_DIR/scripts/publicar.mjs --checar                    # só o estado do canal
node $SKILL_DIR/scripts/publicar.mjs --texto post.md --imagem card.png --checar
```

2. **Mostrar ao dono** quando ele quiser conferir antes; a formatação é a do WhatsApp (`*negrito*` com um asterisco, bullets com "•").
3. **Publicar**, só com pedido explícito: a mesma chamada com `--yes` no lugar de `--checar`. O script imprime o id da mensagem; registre no pacote da pauta (no projeto, `docs/comercial/`).
4. Com imagem, o `--texto` vira legenda, e o script recusa acima de 1.024 caracteres.

## Estado desta máquina (2026-10-05)

- Canal "Inteligência Artificial" (o JID está na config da máquina), 39 seguidores na data; a conta do sidecar é OWNER.
- Publicação validada de ponta a ponta: card 1080×1080 com legenda, mais de um post entregue com id de confirmação.
- Leitura de volta (`newsletterFetchMessages`) estoura timeout nesta versão do Baileys: a confirmação visual é do dono, no aplicativo.
- Ruído "Bad MAC / Failed to decrypt" nos primeiros minutos após parear é fila antiga de notificações; o script filtra o comum e o resto é inofensivo.

## Limitações e problemas comuns

- Sessão cai (status 401, "aparelho deslogado"): o celular removeu o aparelho; reparear. Roteiro em `references/pareamento-e-problemas.md`.
- No pareamento, o status 515 (restart) é **normal**: reconectar com o mesmo estado, sem apagar `.auth`. Apagar no meio do registro foi o que travava pareamentos por meses.
- Se o import do Baileys falhar, confira `node_modules/@whiskeysockets/baileys` na pasta do sidecar (versão nova pode mudar o caminho do pacote).

## Referências

- `references/pareamento-e-problemas.md` — parear por código de 8 dígitos ou por QR (inclusive remoto), o que fazer em 401/515, limpeza de sessão, e como descobrir o JID do canal pelo link de convite.

## Exemplos de uso

- "posta isso no canal do WhatsApp" → escrever/conferir o texto, `--checar`, mostrar, e `--yes` no pedido.
- "o canal está pronto para postar?" → `--checar` sem conteúdo.
- "confere o texto antes de eu mandar" → `--checar` com `--texto` e mostrar a prévia.

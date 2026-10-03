# <Nome do app>

<Uma frase: para quem, o que faz, para quê. A mesma promessa que está na primeira tela.>

## O que é

<3 a 6 linhas: o problema, o público, e o que o app faz no lugar de quê.>

## Decisões que não se mudam sem querer

| Decisão | Escolha | Por quê |
|---|---|---|
| Dados | **local-first** (nada sai do aparelho) | <motivo: LGPD, custo, offline> |
| Tema padrão | **claro** (escuro é escolha em Ajustes) | no escuro a identidade quase desaparece |
| Roteamento | hash (`#/rota`) | funciona em estático e no WebView sem rewrite |
| Classificação | público adulto | evita Families Policy (Google) e categoria Kids (Apple) |
| `appId` | `br.com.<empresa>.<app>` | no iOS não muda depois de publicar |

## Quem valida o conteúdo

**<Nome e papel>** — o conteúdo só vai a produção depois desta validação. Enquanto não
houver aval, a produção fica protegida ou adiada.

## Identidade visual

- **Origem:** <repo local / repo vizinho `<caminho>` / Google Stitch (projeto `<id>`) / nova>
- **Marca:** <símbolo>, traço `<#hex>` sobre `<#hex>`
- **Regra de contraste:** fundo escuro → <cor clara>; fundo claro → <cor escura>
  (medido: <x>:1)
- **Design system / tokens:** `<caminho dos tokens>`

## Como rodar

```bash
npm install
npm run dev        # desenvolvimento
npm run build      # build + service worker (PWA)
npm run preview    # serve o build
npm run typecheck
```

## Publicação

No ar em **<url>**.

```bash
vercel deploy          # preview (não toca no domínio)
vercel deploy --prod   # produção
```

Previews ficam atrás de **Deployment Protection** — só abre logado no time.

> **Atualização:** <como o app se atualiza. Se nada foi decidido ainda, escreva isso —
> sem estratégia, correção publicada pode não chegar a quem já usa.>

## Estrutura

```text
src/
  telas/        # uma por rota
  componentes/  # UI reutilizável
  conteudo/     # texto e regras de domínio, separados da UI
  lib/          # banco local, tipos, utilidades
  estilos/      # tokens e CSS
docs/           # privacidade, roadmap, copy
marca/          # assets da marca (fonte dos ícones)
```

## Documentos

- `BACKLOG.md` — o que falta, priorizado
- `docs/PRIVACIDADE.md` — política, para publicar em URL
- `docs/ROADMAP-APP-STORES.md` — o que falta para as lojas
- `docs/COPY.md` — promessa, objeções e crenças trabalhadas

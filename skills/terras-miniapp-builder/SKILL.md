---
name: terras-miniapp-builder
description: "Cria um miniapp do zero — recebe o assunto, entrevista as lacunas, decide arquitetura e LGPD, escolhe e dosa a paleta, escreve a copy (promessa, objeções, crenças limitantes), constrói o app local-first, verifica e publica na Vercel (preview e depois produção). Usa identidade visual já estabelecida no repositório quando existir, e o Google Stitch quando estiver acessível. Use sempre que o pedido for criar/gerar/fazer um app ou miniapp novo, um PWA, um app de bolso, um instrumento para um público, 'transforma esse conteúdo em app', 'quero um app pra isso', ou quando alguém entregar um assunto e esperar um app funcionando no ar. Trigger on: miniapp, mini-app, criar app, novo app, gerar aplicativo, app de bolso, PWA, publicar na vercel."
keywords: [miniapp, mini-app, criar app, novo app, gerar app, aplicativo, pwa, app de bolso, publicar app, vercel, google stitch, lgpd, psicologia das cores, paleta, copy, objecao, crenca limitante, pitch, local-first]
---

# Criar miniapp

Um miniapp é um app web **de um propósito só**: cabe num ritual de uso, funciona no
aparelho sem servidor, e sai publicado como PWA (depois empacotável para as lojas).
Não é um sistema. Se o pedido descreve um sistema (muitas telas, perfis, permissões,
integração com terceiros), diga isso antes de começar — provavelmente não é um miniapp.

O trabalho é conduzir da ideia solta até um app no ar, **passando por entrevista,
LGPD, cor, copy, construção, verificação e publicação** — nessa ordem. Pular a
entrevista ou a verificação é o que produz app bonito que ninguém usa, ou correção
publicada que não chega a ninguém.

## Princípios que não se negociam

1. **Um propósito, uma ação central.** Se não der para dizer em uma frase qual é a
   única coisa que a pessoa faz ali, o app ainda não está definido.
2. **Local-first por padrão.** Dado fica no aparelho (IndexedDB), sem backend. É o
   caminho mais barato de LGPD — não há dado sob sua guarda, não há controlador a
   declarar, não há vazamento possível. Backend só com decisão explícita e registrada,
   porque multiplica obrigação legal, custo e superfície de falha.
3. **Nunca diagnosticar, nunca prometer resultado terapêutico.** Quando o assunto
   toca saúde, desenvolvimento infantil ou sofrimento psíquico, o app é apoio
   educativo e reflexivo. Disclaimer visível, e caminho de ajuda (CVV 188 no Brasil)
   quando o tema envolve risco.
4. **Público adulto.** O app é para o adulto responsável, não para a criança. Isso
   não é detalhe de copy: classificar como app infantil no Google Play aciona a
   Families Policy e restringe o app na Apple.
5. **Claro é o tema padrão; escuro é escolha.** No escuro a identidade visual
   quase desaparece (superfícies e texto variam poucos pontos de RGB), e a primeira
   impressão se perde. Não seguir o sistema automaticamente.
6. **Identidade:** o que já existe no repositório manda; senão, Google Stitch; senão,
   gerar do zero. Nunca inventar marca nova ao lado de uma marca estabelecida.
7. **Versionar desde o commit zero.** `git init` antes de escrever a primeira linha.
   App publicado sem histórico não tem como voltar atrás quando algo dá errado.
8. **Preview primeiro; produção só com aval.** Produção nunca é o primeiro destino
   de uma versão.
9. **Toda versão publicada precisa de estratégia de atualização.** O service worker
   pode continuar servindo o código antigo para quem já visitou — sem isso, correção
   publicada não chega.

## Fases

Cada fase tem um **portão**: não avance sem ele fechado. Os portões existem porque
cada um deles já custou retrabalho caro.

| Fase | O que acontece | Portão para avançar |
|---|---|---|
| 0 | Enquadrar o pedido | promessa em uma frase + ação central + quem valida o conteúdo |
| 1 | Entrevistar as lacunas | as respostas de `references/descoberta.md` preenchidas |
| 2 | Arquitetura e dados (LGPD) | local-first ou backend, **decidido e escrito**; disclaimers definidos |
| 3 | Identidade visual | origem da identidade escolhida e registrada (local / Stitch / nova) |
| 4 | Cor: escolher **e dosar** | contraste medido e proporção de área conferida |
| 5 | Copy | promessa, objeções e crenças mapeadas e endereçadas |
| 6 | Construir | build limpo, sem pendência de tipo |
| 7 | Verificar | telas conferidas no navegador, em claro **e** escuro |
| 8 | Publicar | preview aprovado pelo usuário antes de produção |
| 9 | Entregar | README, BACKLOG, politica de privacidade, roadmap de lojas |

Detalhe de cada reference — leia **antes** de executar a fase, não depois:

| Fase | Leia |
|---|---|
| 1 | `references/descoberta.md` |
| 2 | `references/lgpd-e-etica.md` |
| 3 | `references/identidade-visual.md` |
| 4 | `references/cor-e-acessibilidade.md` |
| 5 | `references/copy-e-persuasao.md` |
| 7 e 8 | `references/verificacao-e-publicacao.md` |
| 9 (e quando for às lojas) | `references/lojas.md` |

### Fase 0 — Enquadrar

Antes de perguntar qualquer coisa, escreva o que você entendeu em três linhas:
**qual é o problema, para quem, e o que o app faz**. Se o enunciado não sustenta
essas três linhas, o que falta é escopo, não é app.

Aqui também: identificar se o assunto é sensível (saúde, criança, dinheiro, luto,
religião) — isso muda tom, disclaimers e o que pode ser prometido.

### Fase 1 — Entrevistar as lacunas

O pedido chega quase sempre com assunto e sem o resto. **Perguntar é parte do
trabalho, não uma interrupção.** Pergunte em rodadas curtas (3–4 perguntas por
vez), com a recomendação marcada, para o usuário poder só confirmar.

Roteiro completo em `references/descoberta.md`. O mínimo inegociável antes de
construir: público, promessa, ação central, ritual de uso, quem valida o conteúdo,
e qual marca/identidade usar.

### Fase 2 — Arquitetura e LGPD

Leia `references/lgpd-e-etica.md`. Decida e **registre** a arquitetura de dados.
O default é local-first. Se houver dado de criança, dado sensível ou backend, as
obrigações mudam — o reference lista o que fazer em cada caso.

### Fase 3 — Identidade visual

Leia `references/identidade-visual.md`. Procure identidade estabelecida **antes** de
gerar qualquer coisa: `docs/marca/`, `docs/stitch/`, tokens CSS, logos no repositório
ou em repositório vizinho. Só gere do zero se não existir.

Se o Google Stitch estiver acessível (MCP), use-o para os layouts e leia o
`designMd` do tema — é a fonte real dos tokens. O reference tem o fluxo.

### Fase 4 — Cor: escolher e dosar

Leia `references/cor-e-acessibilidade.md`. Duas coisas separadas, e a segunda é a
que quase todo mundo esquece: **escolher** matizes que combinam com a proposta, e
**dosar** quanto cada um ocupa na tela. Uma paleta calma com o matiz mais estimulante
ocupando a maior área produz um app que não acalma.

Meça, não estime: `scripts/contraste.py` dá os índices de contraste e a proporção de
área colorida a partir de uma captura.

### Fase 5 — Copy

Leia `references/copy-e-persuasao.md`. Antes de escrever tela, escreva num documento:
a promessa, as **crenças limitantes** que travam o uso, e os **argumentos negativos**
que a pessoa levanta contra o app. Depois endereça cada um — no onboarding, na
primeira tela, ou no conteúdo. Copy que não responde a objeção real não persuade.

Tom: pt-BR, positivo, não julgador. Sem prometer resultado, sem culpar o usuário.

### Fase 6 — Construir

Estrutura mínima do repositório em `assets/templates/`. Stack: React + Vite +
TypeScript, PWA (`vite-plugin-pwa`), persistência local (`idb`), roteamento por hash
(facilita hospedagem estática e o empacotamento nativo).

Construa pelo caminho da ação central primeiro — a tela principal e o fluxo completo
funcionando — antes de qualquer tela secundária.

### Fase 7 — Verificar

Leia `references/verificacao-e-publicacao.md`. **Abra o app no navegador e olhe.**
Build limpo não é verificação: confira as telas, nos dois temas, com dado vazio e com
dado preenchido. Verifique também que a preferência de tema não pisca na abertura.

### Fase 8 — Publicar

Preview na Vercel primeiro (`vercel deploy`, sem `--prod`), com Deployment Protection
enquanto o conteúdo não tiver aval. Produção só depois de o usuário ver o preview e
autorizar. Depois de publicar, **confirme qual bundle o servidor está entregando** —
e saiba que o navegador de quem já visitou pode continuar rodando o anterior.

### Fase 9 — Entregar

Os documentos de entrega saem de `assets/templates/`: `README.md` (promessa, decisões que
não se mudam, como rodar e publicar), `BACKLOG.md` (pendências reais, priorizadas),
`docs/PRIVACIDADE.md`, `docs/ROADMAP-APP-STORES.md` e `docs/COPY.md` (promessa, objeções
e crenças trabalhadas).

O BACKLOG é onde as decisões adiadas ficam visíveis — sem ele, o que ficou por fazer se
perde. E o README é onde a próxima sessão descobre por que a arquitetura é local-first,
ou que a identidade visual mora em outro repositório.

## Erros que já custaram caro

Cada um destes aconteceu de verdade e está aqui para não repetir:

- **Publicar sem versionar.** Um app foi ao ar sem `git init`. Quando precisou voltar
  atrás, não havia para onde voltar.
- **Service worker segurando a versão antiga.** O servidor entregava o bundle novo e o
  navegador continuava rodando o anterior, do precache. Uma navegação não resolveu.
  Quem publica sem estratégia de atualização acha que a correção entrou — e ela não chegou.
- **Produção antes do preview.** A primeira publicação levou o conteúdo ainda não
  validado direto para o endereço público, e as pessoas acharam que não tinha mudado nada.
- **Tema escuro engolindo a identidade.** Num aparelho escuro, o app seguia o sistema e
  abria escuro — onde a marca nova era quase indistinguível da anterior (11–15 pontos de
  RGB de diferença nas superfícies).
- **Sálvia sobre fundo claro.** A marca foi entregue em verde-sálvia sobre carvão; sobre
  o papel claro do app ela dá 2,14:1 e desaparece. Toda cor de marca precisa de variante
  por fundo, e a regra tem que ficar escrita.
- **Ícone desenhado por código ao lado de uma marca oficial.** Um símbolo foi inventado
  em script enquanto a marca real existia em outro repositório. Procure antes de criar.
- **`window.confirm` no WebView do iOS.** Não retorna; a ação destrutiva simplesmente não
  acontece. Use diálogo próprio do app.
- **`appId` escolhido no fim.** No iOS não dá para trocar depois da publicação. Decida antes.
- **Ícone com canal alfa.** A App Store exige 1024×1024 sem alfa.

## Referências

- `references/descoberta.md` — roteiro de entrevista e enquadramento
- `references/lgpd-e-etica.md` — dados, menores, retenção, disclaimers, política
- `references/identidade-visual.md` — precedência, Stitch via MCP, marca e variantes
- `references/cor-e-acessibilidade.md` — psicologia das cores, dosagem, contraste
- `references/copy-e-persuasao.md` — promessa, objeções, crenças limitantes
- `references/verificacao-e-publicacao.md` — verificar, publicar, atualizar
- `references/lojas.md` — Capacitor, ícones, classificação, política

## Scripts

- `scripts/contraste.py` — contraste entre cores e proporção de área colorida numa captura
- `scripts/marca.py` — extrai a marca de um JPEG e gera variantes por fundo
- `scripts/icones.py` — monta os ícones do PWA (inclui maskable) a partir da marca

Rodam com `python3` e Pillow. Nenhum deles depende de rede.

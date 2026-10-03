# Aplicação em vagas (fase 2) — playbooks por fonte

A candidatura acontece **no site de cada vaga**; o board só aponta o link.
Cada fonte tem um caminho. Tudo aqui parte de uma vaga **aprovada pelo
usuário, uma por vez** — não existe aplicar em lote.

## Regra de ouro

O submit é sempre o último passo e nunca acontece sem o usuário ter visto
**os valores exatos de cada campo** e dito "aprovado" para aquela vaga.
Uma aprovação vale para um envio; reenvio precisa de nova aprovação.
Antes de preencher, procure sinal de "already applied" na página — se houver,
registre como `ja-aplicado` e pare.

## As etapas de uma aplicação

1. **Ler o anúncio de verdade.** Abra o `jobUrl` e leia a JD completa — não os
   1.500 caracteres da triagem. É aqui que encaixe fino se confirma: a CI&T
   "Senior Backend/Integration" de out/2026 era Python/Java/gRPC/Salesforce no
   texto, não .NET — e desceu para B depois de lida. Reclassificou? Diga.
2. **Montar o kit** (ver "Kit de candidatura" em `perfil.md`):
   respostas de screening do kit + carta curta em inglês no padrão da
   `terras-cover-letter` (250-300 palavras, ângulo da vaga). Pergunta sem fato
   no kit (pretensão, notice period) → **pergunte ao usuário**, nunca invente.
3. **Chegar ao formulário** pelo playbook da fonte (abaixo).
4. **Preencher** tudo que é texto, radio e seleção.
5. **Parar nos portões** — são sempre do usuário: login/SSO, captcha ou
   Cloudflare que não passa sozinho, **upload de arquivo** (o navegador
   embutido não faz upload; o currículo é anexado por ele) e o botão de submit.
6. **Portão final.** Mostre a tabela campo→valor que será enviada e espere
   "aprovado". Depois do submit, confirme na página (mensagem de sucesso,
   e-mail, "application received"). "Não confirmado" = conferir a página antes
   de qualquer reenvio; nunca reenvie às cegas.
7. **Registrar** em `~/.config/terrasia-vagas-coders/candidaturas.json`.

## Playbooks por fonte

**Post de LinkedIn** (fonte `LinkedIn` no board, url de `/posts/`):
é post de recrutador, não anúncio estruturado. Abra o post e procure o link
de candidatura no texto ou comentários. Sem link = candidatura social
(comentar/DM o recrutador): é ação **pública**, o texto segue as regras da
`terras-cover-letter` (versão curta) e precisa de aprovação explícita — mesmo
tratamento do mural na `terras-coders-mural`.

**Vaga no LinkedIn** (`linkedin.com/jobs/view/...`): verifique se é Easy Apply
(formulário dentro do LinkedIn) ou "Candidatar-se no site da empresa" — nesse
caso extraia a URL real do redirect `linkedin.com/safety/go/?url=...` e siga
para o ATS. Observado: BairesDev → `applicants.bairesdev.com`, ATS próprio com
Cloudflare (geralmente passa sozinho esperando ~6s) e **login obrigatório**
(Google/LinkedIn SSO ou conta do site) — portão de usuário.

**ATS estilo SmartRecruiters** (ex.: `jobs.deel.com/.../application`): o melhor
caso. Textos, radios e comboboxes o agente preenche; resume em PDF é upload
(portão); o botão Apply só habilita com tudo obrigatório completo. Perguntas
comuns: country of residence (Brazil), sponsorship (No), work authorization,
English fluent (Yes), notice period (**perguntar**), previously worked there
(No), resume-in-English confirmation (Yes).

**Lições duras do formulário Deel (radix/React, observadas em 2026-10-02):**

- **Nunca feche lista suspensa clicando fora** (`body.click()`): o formulário
  INTEIRO perde as seleções. Feche com `Escape` no elemento ou clicando no
  botão "Close" que o próprio componente mostra.
- **Verifique o estado depois de cada passo** (snapshot campo a campo) —
  seleção "bem-sucedida" sem verificação não é seleção.
- Cliques de Playwright em `option`/botões custom estouram timeout; use
  `evaluate` com `el.click()` na página.
- `RegExp` não atravessa o evaluate como argumento — passe string e construa
  `new RegExp` dentro.
- Comboboxes sem rótulo (inputs `role=combobox`): mapeie pela pergunta do
  campo (suba até o contêiner com `<p>`) e clique a opção dentro da listbox
  vinculada por `aria-controls` — nunca em `[role=option]` globais (listas de
  outros campos ficam abertas junto).
- **Multiselect teimoso** ("previously worked at Deel"): nem evento sintético
  (click/pointer/keyboard), nem clique do Playwright efetivam a seleção — a
  lista fecha sem gravar. O que funciona: `tab.cua.click` por coordenadas
  (screenshot → mira no texto da opção → clique real). Refresh da página
  limpa o formulário inteiro: re-verifique sempre antes de submeter.
- **Um `fill()` programático remonta o formulário e derruba upload, radios e
  combos** (observado na Deel, out/2026): a ordem segura é textos primeiro
  (`fill`), depois radios, depois combos — e **o upload do usuário é sempre o
  ÚLTIMO passo**. Depois do upload, só clique real (`cua`), nunca `fill`.
- **Dois botões "Apply"**: um oculto e habilitado (template) engana a checagem
  `!disabled` — filtre sempre por `getBoundingClientRect().width > 0`.
- **Autofill do ATS a partir do PDF cola fragmentos**: o parse do currículo
  gerou `linkedin.com/in/limaevertonSoftware` (404). Confira os campos que o
  autofill preenche contra o `perfil.md` antes de qualquer envio.

**Aggregators** (`found.dev`, `remoterocketship.com`, `news.ycombinator.com`):
a JD completa costuma estar no próprio agregador — leia ali (passo 1) e siga o
botão Apply até o ATS real. No HN ("Who's hiring"), candidatar = e-mail do
post: monte assunto + corpo (kit) e entregue para aprovação; o envio é do
usuário (não há cliente de e-mail automatizado aqui).

**Outros ATS**: Greenhouse (`boards.greenhouse.io`/`job-boards.greenhouse.io`),
Lever (`jobs.lever.co`), Workable (`apply.workable.com`) — mesmo modelo:
formulário curto, texto preenche, upload é portão. Se aparecer formulário
desconhecido, mapeie com um snapshot antes de digitar qualquer coisa.

## Perguntas de screening

Responda **só com fato do kit**. Resposta subjetiva ("why do you want to work
here?") → rascunho ligado ao ângulo da carta, mostrado na tabela de aprovação.
Pergunta sobre salário → só com o piso definido em `perfil.md`; sem piso
definido, pergunte ao usuário. Nunca preencha por impressão.

## Ritmo e registro

- Máximo **3 candidaturas/dia** por padrão (usuário muda em `perfil.md`), uma
  por vez, nunca em paralelo.
- `candidaturas.json`: `{url, vaga, empresa, status, quando, kit}` com status
  `preparada | enviada | entregue-ao-usuario | ja-aplicado | impossivel` e o
  motivo quando não for `enviada`. Automação de candidatura em sites de
  terceiros vai contra os termos da maioria deles; ritmo baixo, volume baixo
  e aprovação humana reduzem o risco, não eliminam — decisão do usuário.

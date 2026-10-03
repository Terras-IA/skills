---
name: terras-notas
description: "Analisa NFS-e (nota fiscal de serviço) recebidas da contabilidade Fênix Assessoria, confere o tomador/destinatário contra um de-para de clientes e envia cada nota por e-mail pelo Outlook do Office 365 (Microsoft Graph). Use quando o pedido envolver notas da Fênix, NFS-e, conferir tomador/destino de nota, de-para de clientes, baixar anexos de e-mail da contabilidade, enviar nota fiscal para o cliente pelo Outlook. Fetch, parse, match and send NFS-e invoices via Outlook/Graph."
keywords: [nfse, nota fiscal, nfs-e, fenix, felix, contabilidade, assessoria, tomador, destinatario, de-para, outlook, office 365, graph, enviar nota, emitir nota]
---

# Notas da Fênix — analisar, conferir destino e enviar

## Objetivo

Pegar as NFS-e que a contabilidade **Fênix Assessoria** (11 92010-0625)
manda por e-mail, extrair do PDF quem é o tomador, casar com o de-para de
clientes e despachar a nota para o e-mail certo pelo Outlook — com
confirmação antes de qualquer envio.

## Onde está instalada

Fonte única: `skills/terras-notas/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

Funciona em qualquer workspace;
os PDFs vivem em `notas_dir` (padrão `~/Documents/SLC`).

## Regra de ouro (segurança)

1. **Nada é enviado sem confirmação.** `despachar` sem flag só mostra a
   tabela; `--rascunho` cria rascunhos; `--enviar --yes` é o único jeito de
   enviar e-mail de verdade.
2. **Destino de confiança média não sai.** Casamentos "sugeridos" (nome
   parecido) ficam de fora até o de-para confirmar.
3. **Nunca reenvia.** Cada `numero/serie` despachado fica registrado no
   state e sai da fila para sempre.
4. Token do Graph e config ficam em `~/.config/terras-notas/` (mode 600).

## Pré-requisitos

Ferramenta: `python3 $SKILL_DIR/scripts/terras_notas.py <comando>`.
Config: `~/.config/terras-notas/config.json` (client_id do Entra, pasta das
notas, templates de e-mail). Setup completo (venv + registro no app) está em
`INSTALL.md`. Antes de qualquer coisa rode `check`.

### Estado desta máquina (2026-10-01)

- **A prefeitura migrou de layout**: as notas de out/2026 (NFS-e 26 e 27, série
  não se aplica) saem no **DANFSe v2.0 nacional**, com chave de 50 dígitos. O
  parser `nfse-nacional-v1` foi escrito e validado nessas duas notas; o layout
  municipal antigo continua funcionando (NF 77, 85, 86, 87).
- Parser validado com 6 notas reais (77, 85, 86, 87, 26, 27) — número, tomador,
  CNPJ, endereço, valores e descrição conferidos.
- **Login Microsoft ativo**: app `terras-entra` (client_id
  `71a5cc16-e627-4936-ab2f-ceee328b5ced`) no tenant Sousa Lima Consultoria,
  authority por tenant, "Allow public client flows" habilitado. Conta:
  everton@sousalimaconsultoria.com.br, renovação silenciosa validada.
- **NF 86 enviada** ao IEDI e **recebimento confirmado pela Liziani** (que pediu
  cópia para coord.financeiro@ — implementado). Rascunhos prontos: NF 85
  (Merco), NF 87 (Dimastec), NF 77 (ISOG/julho), **NF 26 e 27 (ISOG, out/2026)**.
- **Assinatura**: ativo da própria skill em `assets/assinatura.png`, importado
  do e-mail "NOTA SETEMBRO/2026" (enviado ao Merco em 02/09) com
  `assinatura importar`. Os envios saem em HTML com a imagem embutida. A NF 86
  saiu **antes** disso, com assinatura em texto puro.
- De-para: Merco (gustavo + erica), Dimastec (adm@), ISOG/5G (anapaula@),
  IEDI (financeiro01@ com **cópia para coord.financeiro@**, pedido pela Liziani
  em 21/09 — a mesma que **confirmou o recebimento da NF 86**; janela 15–20).
- **A Fênix não aparece na caixa**: varredura de 150 mensagens recentes não
  achou e-mail da contabilidade — as notas chegam por outro canal (o telefone
  informado é celular) e são salvas à mão em `~/Documents/SLC`. Logo,
  `fetch`/`descobrir-remetente` ficam sem fonte até que os e-mails da Fênix
  passem a chegar nessa caixa; o fluxo que funciona hoje é
  `parse` → `match` → `despachar --rascunho/--enviar --yes`. **Falta definir
  `assessoria_email` na config** para o `pedido enviar` — enquanto isso, use
  `pedido texto` e mande pelo canal de costume.
- Decisão de 2026-09-21 sobre emissão: a **assessoria contratada** emite (o
  usuário paga por isso) e o caminho adotado é o **pedido padronizado** por
  e-mail (`pedido add/list/ficha/texto/enviar`). O portal da Nota Joseense não
  será automatizado: login com reCAPTCHA, certificado digital exigindo Java e
  documento fiscal — risco alto para pouco ganho.
- Parser agora extrai também **endereço, município/UF, CEP e descrição do
  serviço** do tomador; o de-para ganhou a coluna `endereco`, preenchida a
  partir dos PDFs já parseados.

## Fluxo padrão

1. `check` — o que falta (venv, client_id, login, de-para).
2. `run` — baixa anexos PDF dos e-mails da Fênix (`fetch`), extrai os dados
   (`parse`) e casa com o de-para (`match`).
3. Revisar a tabela: NF → tomador → destino → situação. Pendências se
   resolvem com `depara add --cnpj … --nome … --email …`.
4. `despachar` para conferir; `despachar --rascunho` para criar rascunhos no
   Outlook; `despachar --enviar --yes` (ou `--nota 85` para uma só) para
   enviar de fato.
5. `status` para o resumo a qualquer momento.

## Comandos

| Comando | Para que serve |
|---|---|
| `check` | valida venv, config, de-para, login |
| `auth` | login Microsoft (código de dispositivo) |
| `descobrir-remetente` | busca na caixa quem é a Fênix |
| `fetch [--desde ISO]` | baixa PDFs anexos dos e-mails da Fênix |
| `parse [pdfs…] [--json]` | extrai dados das NFS-e |
| `depara list/add/rm/check` | mantém o CSV tomador → e-mail |
| `match [--nota N] [--json]` | casa notas com destinos |
| `despachar [--nota N] [--rascunho / --enviar --yes]` | monta/cria rascunho/envia |
| `assinatura importar/mostrar` | traz a assinatura de um e-mail enviado e a usa |
| `pedido add/list/rm/ficha/texto/enviar` | ficha de emissão por cliente e competência |
| `lembrete [--postar]` | o que precisa de ação hoje (pedidos + janelas); `--postar` vai ao Discord |
| `avisar "texto" / avisar --lembrete` | posta mensagem no Discord |
| `status` | resumo (prontas, pendentes, enviadas) |
| `run` | fetch + parse + match |

## Assinatura dos e-mails

**O Outlook não aplica a assinatura dele em envio por API** — a assinatura é um
recurso de cliente (web/desktop); o Graph manda exatamente o corpo informado.
Por isso a skill cuida disso:

- A assinatura é uma **imagem** que viaja junto com a skill:
  `assets/assinatura.png`. O envio sai em **HTML**, com "At.te," e a imagem
  embutida via `cid:assinatura` (`isInline: true` + `contentId`), igual ao
  Outlook faz.
- `assinatura importar [--assunto TRECHO] [--buscar N]` — pega a imagem inline
  de um e-mail que você já enviou pelo Outlook e a salva no ativo da skill
  (procura do mais recente para o mais antigo; `--assunto` filtra, ex.:
  `--assunto "NOTA"`). Use sempre que trocar a assinatura no Outlook.
- `assinatura mostrar` — diz qual imagem está em uso e de onde ela vem.
- `assinatura_imagem` na config **sobrepõe** o ativo da skill (útil para uma
  assinatura específica sem mexer no arquivo). Sem imagem alguma, cai no texto
  puro de `email_assinatura`.
- O `check` avisa quando não há assinatura em imagem.

## Pedido mensal de emissão (para quem emite)

Quem emite as NFS-e é a **assessoria contábil** (contratada para isso); as notas
ficam disponíveis no portal da Nota Joseense, de onde os PDFs são baixados e
salvos em `notas_dir`. A skill cuida do pedido mensal e do envio ao cliente:

1. `pedido add --cliente X --valor 8000 [--descricao ...] [--obs ...]` — monta o
   item com os dados do de-para (razão social, CNPJ, **endereço completo**),
   herda a descrição da última nota do cliente quando você não informa, e
   anexa a janela de envio do cliente.
2. `pedido ficha` — o mesmo item em formato de ficha, com os parâmetros fixos do
   prestador (código do serviço 08.02, CNAE 859960300, município de incidência,
   ISSQN retido pelo prestador, Simples Nacional), tirados das notas reais.
   Serve para conferir antes de pedir e para tirar dúvida com a assessoria.
3. `pedido texto` — imprime a mensagem pronta (para colar no WhatsApp, se for o
   canal de vocês).
4. `pedido enviar --rascunho` / `--enviar --yes` — manda por e-mail, com a
   assinatura, para `assessoria_email` (ou `--para`). Ao enviar, os itens ficam
   marcados como solicitados e não são pedidos de novo.

**Lembrete**: `lembrete` é o comando que responde "o que precisa de ação hoje" —
cruza pedidos ainda não solicitados, **janelas de envio de cada cliente** (o
`janela_envio` do de-para; a nota tem de ser emitida antes da janela) e
rascunhos parados. `lembrete --postar` publica o resultado no **Discord**
(quando `discord_webhook` estiver na config); `avisar "texto"` posta mensagem
avulsa, e `avisar --lembrete` posta o lembrete se houver pendência. Uma
**automação roda todo dia às 9h** com `lembrete --postar` (Merco dia 3 e
Dimastec dia 1 exigem pedido ao escritório ainda no mês anterior). O `status`
também mostra o pedido do mês.

**Janelas confirmadas pelo usuário (01/10)**: Dimastec **dia 1** (com cópia para
dimas@dimastec.com.br — preferência observada num envio manual), Merco **até
dia 3** (contrato: início 01/04/2026, pagamento dia 10, R$ 2.000/mês; contato
de e-mail definitivo ainda não definido), ISOG **até dia 10**, IEDI **15–20**.
A janela que o usuário diz prevalece sobre qualquer padrão deduzido do histórico.

Detalhe que evita erro: **os dados do tomador não se digitam na emissão** — o
portal busca no *Cadastro de Receitas Mobiliárias* da prefeitura pelo CNPJ, e
divergência só o tomador corrige lá. Quando for esse o caso, o item do pedido já
leva razão social e CNPJ para a assessoria conferir.

## Como o de-para decide o destino

Ordem: **CNPJ no de-para** (somado ao e-mail do próprio PDF, se houver) →
**e-mail no PDF** → **nome/apelido exato** → similaridade ≥ 0,85
(**sugerido**, confiança média, não despacha). Sem casamento: pendente
(aparece no `match` e no `status`).

Arquivo: `~/.config/terras-notas/depara.csv`
(`cnpj,razao_social,apelidos,email,cc,janela_envio,endereco,obs`).

- **Vários destinatários**: separe por `;` ou `,` no campo `email`
  (ex.: `gustavo@merco.info;erica@merco.info`) — o e-mail sai para todos.
- **`cc`**: quem entra em cópia, também com `;` para vários (ex.: o IEDI pediu
  cópia para a coordenação financeira). O `despachar` mostra a coluna Cópia e o
  `despacho` registra a cópia no state.
- **`janela_envio`**: dias preferidos do mês, formato `15-20`. O `despachar`
  avisa quando o dia está fora da janela (o envio continua permitido).
- **`endereco`**: endereço do tomador, usado na ficha de emissão do pedido.
- Apelidos separam-se por `;`.

## Rota sem Graph (fallback)

Se o login Microsoft estiver quebrado: baixe os PDFs manualmente no
Outlook Web e rode `parse` + `match` + `despachar` normalmente — só o
`fetch`/`despachar` efetivo precisam do Graph. Para reenvio manual, copie o
corpo do e-mail com `parse --json`.

## Limitações conhecidas

- Dois layouts de NFS-e de **São José dos Campos**, detectados pelo conteúdo:
  o municipal antigo (`nfse-sjc-v1`, `references/nfse-sjc.md`) e o **nacional
  DANFSe v2.0** (`nfse-nacional-v1`, `references/nfse-nacional.md`), que passou
  a ser emitido em out/2026. Nota de outra cidade cai no aviso "campos não
  reconhecidos" e vai para revisão manual.
- O `parse` roda `pdftotext` **e** `pdfplumber` e fica com o melhor resultado —
  o pdfplumber cola espaços dos rótulos no layout nacional. O campo `extrator`
  no state diz qual venceu.
- `fetch` filtra por `remetentes_fenix` na config — se a Fênix trocar de
  endereço, rode `descobrir-remetente` de novo.
- Anexo > 3 MB não sobe pelo endpoint simples (NFS-e de SJC tem ~30 KB).
- O refresh token pode expirar se ficar meses sem uso: `auth` de novo.
- Notas substitutas (série E) enviam-se normalmente; o campo
  `nota_substituida` fica registrado no state para consulta.

## Exemplos de uso

- "confere as notas que chegaram da Fênix e me mostra o que falta"
- "roda o fluxo das notas e cria rascunhos para eu revisar"
- "envia a NF 87 pro cliente" (→ `despachar --nota 87 --enviar --yes`)
- "adiciona a Iedi no de-para: financeiro@iedi.org.br"
- "qual o status das notas deste mês?"

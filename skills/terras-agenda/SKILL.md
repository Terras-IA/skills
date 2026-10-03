---
name: terras-agenda
description: "Agenda unificada do Everton: junta os calendários do Microsoft 365/Teams (Sousa Lima, ISO, THG — cada um num tenant) e qualquer feed .ics (Google Agenda, calendário publicado) numa agenda só, com detecção de choque de horário e criação de evento. Use quando o pedido envolver agenda, calendário, reunião, compromisso, 'o que tenho hoje', 'que horas é tal coisa', conflito de horário, marcar/criar reunião, convite, Teams, Google Agenda, unificar/centralizar agendas. Unified agenda across Microsoft 365 tenants and ICS feeds: today, upcoming, conflicts, create event."
keywords: [agenda, calendário, calendario, calendar, reunião, reuniao, compromisso, evento, teams, outlook, google agenda, unificar, centralizar, conflito, horário, ics, ical, marcar, convite, graph]
---

# terras-agenda — uma agenda só

## O que resolve

O Everton tem compromissos espalhados por **três empresas em três tenants
Microsoft diferentes** mais **contas Google**. A skill lê todos e devolve uma
lista única, em ordem, marcando o de onde veio cada compromisso e **avisando
quando dois se atropelam** (o caso clássico: reunião da Sousa Lima em cima de
um plantão do ISO).

Duas fontes, com naturezas diferentes:

| Fonte | Como | Lê | Escreve |
|---|---|---|---|
| Conta Microsoft (Graph) | uma por tenant, com login por código de dispositivo | sim | sim |
| Feed `.ics` (Google, calendário publicado) | só uma URL | sim | não |

## Onde está instalada

Fonte única: `skills/terras-agenda/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

- Ferramenta: `python3 $SKILL_DIR/scripts/terras_agenda.py <comando>`
- Config e tokens: `~/.config/terras-agenda/` (mode 600), venv próprio em `~/.config/terras-agenda/venv`.

## As agendas desta máquina (levantado em 2026-09-22)

São **três tenants Microsoft separados** — não é uma organização só com
apelidos. Isso importa: um app registrado num tenant não enxerga calendário do
outro sem consentimento lá dentro (ou sem um feed `.ics`).

| Agenda | Conta | Tenant (ID do diretório) | Estado |
|---|---|---|---|
| **Sousa Lima** (minha empresa) | `everton@sousalimaconsultoria.com.br` | `c51d6273-55c7-4537-8fc0-e42448c4a559` | app `terras-entra` já registrado (`client_id 71a5cc16-e627-4936-ab2f-ceee328b5ced`, public client flows ligado). **Falta só o login de calendário.** |
| **ISO** (presto serviço) | `devops@iso5geducacional.com.br` | `a69bd6c8-fbd8-48cf-afd4-d82e9b14189a` | sem app no tenant — depende do ISO publicar/compartilhar, ou de registrar app lá |
| **THG** (não estava na lista do usuário; apareceu no Edge) | `everton.lima@thginformatica.com.br` | `2dbded88-1289-4451-a429-9a0c1ce906c7` | idem ISO |

Contas **Google** que existem nos perfis do Chrome (a agenda pode estar em
qualquer uma delas): `eolimabr@gmail.com`, `esolimabr@gmail.com`,
`erivanioengenharia@gmail.com`, `investidoreolimabr@gmail.com` (perfil
"Everton Investidor"), `iecsjc.415@gmail.com`, mais `admin.web@avanceibrasil.com`
(que é Google/Workspace, não M365).

Verificado no mesmo dia:

- O login da Sousa Lima **renova sozinho** (refresh token válido) — a
  infraestrutura de auth do `terras-notas` está saudável.
- `GET /me/calendars` com o token que existe hoje devolve
  `403 ErrorAccessDenied`: aquele token só tem `Mail.ReadWrite` + `Mail.Send`.
  Calendário exige escopo novo — e escopo novo exige **um login de novo**.
- O device flow com `Calendars.ReadWrite` + `Calendars.Read.Shared` **foi
  aceito pelo tenant** (testado; devolve código normalmente), então o login não
  deve esbarrar em política.

## Ativação — o que falta, em ordem de retorno

1. **Sousa Lima (leitura + escrita).** Roda e faz o login no navegador — o
   código aparece no terminal, é só abrir `https://microsoft.com/devicelogin`,
   digitar e autorizar:
   ```bash
   python3 $SKILL_DIR/scripts/terras_agenda.py auth --conta SLC
   ```
   Depois disso `agenda`, `hoje` e `conflitos` já trazem a agenda da empresa.

2. **Google (leitura).** Pegue o "endereço secreto iCal" (passo a passo
   abaixo) e registre:
   ```bash
   python3 $SKILL_DIR/scripts/terras_agenda.py feeds add --nome Google --url "<url>"
   ```
   O comando testa a URL na hora e diz quantos eventos achou. Se a URL estiver
   errada, ele avisa ali mesmo.

3. **ISO (leitura).** Três caminhos, do mais barato ao mais completo — veja
   "Como trazer o ISO".

## Comandos

| Comando | Para que serve |
|---|---|
| `check` | diagnóstico: o que está configurado, o que falta, o que fazer em seguida |
| `auth --conta SLC` | login Microsoft (código de dispositivo) com escopos de calendário |
| `contas` / `contas --add ISO --tenant <id> --conta <email>` | ver/adicionar conta Microsoft |
| `feeds` / `feeds add --nome Google --url <ics>` / `feeds rm --nome Google` | gerir feeds `.ics` |
| `agenda [--dias 7] [--de 23/09] [--conta SLC] [--feed Google] [--livres]` | agenda unificada do período |
| `hoje` | o dia de hoje + o que está acontecendo agora + o que vem + conflitos + prévia de amanhã |
| `conflitos [--dias 30]` | só os choques de horário entre agendas |
| `criar --titulo "…" --inicio "amanha 14:30" [--fim] [--conta SLC] [--local] [--corpo] [--participantes …] [--simular]` | cria evento no calendário Microsoft |
| `exportar --dias 30 --arquivo ~/agenda.ics` | joga a agenda unificada num `.ics` (para importar em qualquer app) |

`--json` está disponível em `agenda`, `hoje` e `conflitos` — é o jeito de o
agente ler o resultado e responder pergunta em cima dele.

Datas em linguagem natural no `criar`: `hoje 14:30`, `amanha 9h`,
`23/09 14:00`, `2026-09-23 14:00`, `15:30` (hoje, ou amanhã se já passou).

## Como pegar o endereço iCal do Google (2 minutos, por conta)

1. Abra <https://calendar.google.com> e confirme em qual conta está (canto
   superior direito) — se for para centralizar várias, repita para cada uma.
2. Engrenagem ⚙ → **Configurações**.
3. Na coluna da esquerda, clique no **calendário** desejado ("Feriados",
   "Everton", o que for).
4. Role até **"Endereço secreto no formato iCal"** e copie o link
   (`https://calendar.google.com/calendar/ical/.../basic.ics`).
5. `feeds add --nome "<apelido>" --url "<link>"`.

⚠️ Esse endereço é uma **senha de leitura**: quem tem o link lê a agenda
inteira. Não cole em lugar público, e se vazar use "Redefinir" ali mesmo.

## Como trazer o ISO

**Caminho A — ISO publica o calendário (mais simples, se o tenant deixar).**
Logado no ISO, no Outlook Web: ⚙ → Calendário → Calendários compartilhados →
**Publicar um calendário** → escolhe o calendário → Publicar → copia o link
`.ics`. Depois: `feeds add --nome ISO --url "<link>"`.
Muitos tenants têm a publicação desabilitada pelo administrador; se a opção não
aparecer, não é erro seu.

**Caminho B — ISO compartilha com o endereço da Sousa Lima.** No Outlook do
ISO: Calendário → **Compartilhar** → digitar
`everton@sousalimaconsultoria.com.br` → permissão de visualização → enviar.
Chega um convite por e-mail; aceitando, o calendário aparece na lista do
Outlook da Sousa Lima. É o caminho mais "nativo", mas o comportamento de
compartilhamento entre tenants varia com a política das duas organizações.

**Caminho C — app no tenant do ISO (leitura + escrita de verdade).** O
Everton é `devops@` lá. Se tiver direito de registrar aplicativo no Entra do
ISO: registrar app (mesmo passo a passo do INSTALL abaixo), pegar o
`client_id`, botar na config e rodar `auth --conta ISO`. Dá acesso completo ao
calendário do ISO — inclusive criar evento. Cuidado: é a agenda de outra
empresa; o app fica registrado lá e pode ser auditado. Vale mais se o uso for
diário.

Comece pelo A. Se a publicação estiver bloqueada, vá para o B. O C só se você
for usar isso todo dia.

## Rodar o mesmo para a THG

Igual ao ISO — troque o nome. `contas --add THG --tenant 2dbded88-1289-4451-a429-9a0c1ce906c7
--conta everton.lima@thginformatica.com.br`. A THG não estava na lista
original; se for agenda morta, é só tirar da config.

## Registrar um app no tenant de outra empresa (INSTALL)

Um app de cada tenant só enxerga o próprio tenant. Para ISO e THG, o caminho
completo é:

1. <https://entra.microsoft.com> logado **com a conta daquela empresa**.
2. **Entra ID → Aplicativos → Registros de aplicativo → + Novo registro**.
3. Nome: `terras-agenda`. Tipos de conta: **somente neste diretório**. URI de
   redirecionamento: em branco.
4. Copie **ID do aplicativo (cliente)** e **ID do diretório (tenant)**.
5. **Autenticação → Allow public client flows = Enabled → Salvar** (sem isso o
   login por código falha com `AADSTS7000218`).
6. `contas --add ISO --tenant <id> --client-id <id> --conta devops@iso5geducacional.com.br`
   e depois `auth --conta ISO`.

Permissões delegadas (`Calendars.ReadWrite`, `Calendars.Read.Shared`) não
precisam ser marcadas no portal: o consentimento acontece na tela do login.
Mas **tenant que exige consentimento de administrador** bloqueia aqui — nesse
caso só um admin do ISO/THG aprova o app, e aí o caminho A/B (feed `.ics`) é o
que sobra.

## Limites que você precisa saber

- **Feed `.ics` é leitura e não é instantâneo.** O Outlook/Graph atualiza feed
  externo de tempos em tempos (na prática, horas) — não é tempo real como uma
  conta nativa. Para evento de hoje que mudou agora, o `.ics` pode estar
  atrasado.
- **Feed `.ics` do Google inclui só o calendário escolhido**, não a conta
  inteira. Se a agenda está espalhada em três calendários do mesmo Gmail,
  faça três feeds.
- **Escrever só dá em conta Microsoft com app** (hoje: Sousa Lima). Evento no
  Google continua sendo criado no Google.
- **Evento marcado como "livre" fica fora da lista** por padrão (é o
  comportamento certo para achar horário vago), mas some da agenda visual
  também — use `--livres` para ver.
- **Evento cancelado é filtrado**; evento repetido que existe em duas agendas
  ao mesmo tempo vira **uma linha só**, com as duas origens ("SLC+Google").
- **Convite é coisa séria:** `criar` sem `--participantes` só mexe no seu
  calendário; com convidados, o Graph **manda e-mail de verdade** e por isso
  exige `--yes` explícito.

## Regras de ouro

1. `agenda`, `hoje` e `conflitos` **nunca escrevem nada** — são leitura pura.
2. `criar` é o único comando que escreve, e só no calendário da conta indicada.
3. Convite para terceiro só com `--yes`; na dúvida, `--simular` primeiro.
4. Nunca colar token ou endereço iCal secreto em arquivo do projeto, issue ou
   mensagem — eles valem acesso de leitura.

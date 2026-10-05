---
name: terras-mapeamento-de-processos
description: "Mapeia um processo a partir de áudio, gravação de tela, transcrição ou relato falado e devolve o mapa visual (AS-IS e TO-BE), o diagnóstico com números e o plano de melhoria priorizado com as oportunidades de automação. Use quando o pedido for mapear ou desenhar um processo, analisar o áudio ou a gravação de tela de uma rotina, achar o gargalo, reduzir tempo de atendimento, automatizar uma rotina operacional, fazer diagnóstico de processo, montar o fluxo AS-IS/TO-BE ou dimensionar quantas pessoas o processo consome. Cobre também 'é assim que a gente faz hoje, o que dá para melhorar'."
keywords: [mapeamento de processo, mapear processo, processo, fluxograma, bpmn, as is, to be, gargalo, diagnostico de processo, melhoria de processo, automacao de processo, lean, desperdicio, lead time, sop, procedimento operacional, retrabalho, sla]
version: 1.4.0
license: MIT
---

# Mapeamento de processos

Fonte única: `skills/terras-mapeamento-de-processos/` no repositório `terrasia-skills`. Abaixo, `$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Descrição

Transforma evidência bruta (áudio, tela gravada, transcrição, relato escrito) em **mapa + diagnóstico + plano de melhoria**. O valor não está em desenhar bonito: está em quantificar o desperdício e propor intervenção priorizada, com cada afirmação rastreável a um trecho do relato.

O processo real descrito é o que entra no mapa — inclusive a planilha paralela, o caderno e o grupo de WhatsApp. O "como deveria ser" é a proposta TO-BE, não o AS-IS.

## Entregáveis

| # | Entregável | Arquivo |
| --- | --- | --- |
| 1 | Processo estruturado (base de tudo) | `processo.json` |
| 2 | Mapa AS-IS | `as-is.mmd` (+ PNG) |
| 3 | Diagnóstico quantificado | seção do relatório |
| 4 | TO-BE + melhorias priorizadas | `processo-to-be.json`, `to-be.mmd` (+ PNG) |
| 5 | Relatório | `relatorio-<processo>.md` |

## Entradas

| Entrada | Caminho |
| --- | --- |
| Áudio (`.mp3 .m4a .wav .ogg .opus`) | transcreva com a skill vizinha `$SKILL_DIR/../terras-transcription` (ou qualquer transcritor local) |
| Vídeo / gravação de tela (`.mp4 .mov .mkv .webm`) | transcreva o áudio **e** extraia frames com `$SKILL_DIR/scripts/extrair_frames.sh` |
| Transcrição ou relato escrito | use direto, sem etapa de mídia |
| Documento, SOP, planilha, print | leia o arquivo; o print costuma valer mais que o texto |
| Relato curto e vago | conduza a entrevista com `$SKILL_DIR/references/roteiro-entrevista.md` antes de gerar qualquer artefato |

Os **frames da gravação de tela são a melhor fonte de sistema e campo**: é onde aparece a redigitação, a troca de sistema e a planilha paralela que a fala não menciona. Leia os frames (as folhas de contato agrupam 16 por imagem) e registre, para cada um, o sistema aberto e a ação visível.

## Como funciona

1. **Normalize a evidência** em `transcricao-enriquecida.md`, no formato:

   ```markdown
   ## Transcrição
   [00:02:45] <falante>: <texto literal>
   ## Telas observadas
   [00:03:30] ERP > tela "Aprovação" — gestor recebe por e-mail, sem fila
   ## Falas de contexto
   <volume, prazo, custo, reclamação, nome de sistema>
   ```

   Nada é descartado da fonte original; o relatório inteiro precisa apontar para uma linha daqui.

2. **Extraia o processo estruturado.** Para transcrição longa, o atalho é o script:

   ```bash
   python3 "$SKILL_DIR/scripts/extrair_processo.py" --input transcricao-enriquecida.md --output processo.json
   ```

   Ele exige um LLM de linha de comando configurado (`TERRAS_LLM_API_KEY` e, se não for OpenAI, `TERRAS_LLM_BASE_URL`; modelo em `TERRAS_LLM_MODEL` ou `--model`). **Sem LLM configurado, escreva o `processo.json` você mesmo** a partir do relato — o schema está em `$SKILL_DIR/templates/processo-json.md`, e é o que garante que os scripts seguintes funcionem.

   Em qualquer um dos caminhos, **revise antes de seguir**: nome de passo, ordem, tempo absurdo e `lacunas[]` preenchidas.

3. **Gere o mapa AS-IS.**

   ```bash
   python3 "$SKILL_DIR/scripts/render_fluxo.py" --json processo.json --saida as-is --png   # DESENHO (raias, ícones, IDs)
   python3 "$SKILL_DIR/scripts/gerar_mermaid.py" --json processo.json --saida as-is.mmd --tipo as-is
   node "$SKILL_DIR/scripts/render_mermaid.mjs" as-is.mmd --out as-is        # Mermaid em SVG + PNG alta (escala 3)
   node "$SKILL_DIR/../terras-excalidraw/scripts/render.mjs" as-is.mmd --out as-is   # cena editável (.excalidraw)
   ```

   **Saída padrão.** Todo mapa entregue sai pelo `render_fluxo.py` — é o desenho que vai para o cliente: raias horizontais com ícone do ator, ícone e **ID do passo** (P1, P2…) dentro do nó, decisão em losango, espera tracejada, setas condicionais verde/vermelha e quebra de faixa quando o fluxo é longo. Sai `.svg` e, com `--png`, o PNG por navegador headless (escala 2). O Mermaid é o **artefato portátil** e versionável, que acompanha a entrega: abre no mermaid.live, no VS Code e em qualquer visualizador; para documento e impressão, renderize com o `render_mermaid.mjs`. O `render.mjs` da terras-excalidraw serve para **editar** a cena, e a imagem dele sai pequena porque segue o tamanho da cena (não use para o PNG final).

   O desenho é dirigido pelo bloco `layout` do JSON:

   ```json
   "layout": {
     "titulo": "Fluxo AS-IS — Financeiro",
     "colunas": 9,
     "rotulos": { "P4->P5": "10% fora do padrão" },
     "vermelhas": ["P13->P14", "P14->P15"],
     "tracejadas": ["P12->P13"]
   }
   ```

   `colunas` é quantos nós cabem antes de o fluxo quebrar para a faixa de baixo (ajuste para fechar em 2 faixas e evitar uma faixa órfã). Convenções de notação em `$SKILL_DIR/references/notacao-bpmn.md`. **Abra o PNG e olhe** antes de entregar: o script garante que nada se sobrepõe na geometria, mas não julga se o caminho principal ficou legível.

4. **Diagnostique.**

   ```bash
   python3 "$SKILL_DIR/scripts/metricas.py" --json processo.json --volume <transações/mês> [--custo-hora <R$>]
   ```

   Lead time, % do tempo que é espera, handoffs, FTE-h/mês, retrabalho, 8 desperdícios, riscos e controles. A tabela sai pronta para o relatório, com os alertas de lacuna de medição. Fórmulas, classificação VA/NVA, 5 Porquês e KPIs: `$SKILL_DIR/references/frameworks-analise.md`.

5. **Desenhe o TO-BE e priorize.** Parta de `processo.json`, aplique as melhorias e salve `processo-to-be.json` **no mesmo schema** (inclusive o bloco `layout`, com o título trocado), com a origem da mudança no campo `evidencia` (ex.: "melhoria 3 — integração CRM/ERP"). Renderize como no AS-IS: `render_fluxo.py` para o desenho e `gerar_mermaid.py --tipo to-be` para o Mermaid. No TO-BE, o `render_fluxo.py` marca em verde os nós que viraram sistema/automação — é o contraste visual com o AS-IS.

   A ordem de intervenção é fixa: **eliminar → simplificar → padronizar → automatizar → realocar → monitorar**. Escolha da tecnologia (regra, integração, RPA, IA, workflow): `$SKILL_DIR/references/automacao.md`. A priorização é em duas etapas (`$SKILL_DIR/references/frameworks-analise.md`): primeiro os **problemas** achados no diagnóstico por GUT (§9), depois as **intervenções** por impacto × esforço (§10). Destaque 3 quick wins.

6. **Escreva o relatório** preenchendo `$SKILL_DIR/templates/relatorio-processo.md`: sumário executivo com os três números que doem, AS-IS, diagnóstico, melhorias, TO-BE, plano 30/60/90 e as premissas.

   **O pacote de entrega é sempre o mesmo:** o relatório `.md`, os dois desenhos (`as-is.png`/`as-is.svg` e `to-be.png`/`to-be.svg`, feitos com `render_fluxo.py`) e os dois Mermaid portáteis (`.mmd`). Os identificadores do desenho (P1, P2…) são os mesmos citados nas tabelas do relatório — se renumerar um, renumeire o outro.

7. **Anonimize quando o material sair do cliente ou quando pedirem.**

   ```bash
   python3 "$SKILL_DIR/scripts/anonimizar.py" --pasta processos/<slug> \
     --mapa "NomeDoCliente=Cliente X;NomeDoAgente=Agente de IA;NomeDaPessoa=o responsável" --regerar-png
   ```

   Troca nos artefatos de texto (`.md`, `.json`, `.mmd`, `.svg`, `.vtt`…), **renomeia** o que carrega o nome no filename (`relatorio-acme.md` → `relatorio-cliente-x.md`) e regera os PNG com `--regerar-png` — o nome do cliente está **desenhado no título**, então trocar só o texto não resolve. Convenção padrão: empresa → **Cliente X**; assistente de IA → **Agente de IA** (sem nome próprio); pessoa → **papel** ("a analista", "o responsável"). Preserve o timestamp da citação e troque o nome dentro dela pelo rótulo. Sistemas (ERP, CRM, WhatsApp) ficam: é o que dá valor ao diagnóstico — se o cliente pedir, inclua-os no `--mapa`.

Trabalhe numa pasta do processo (ex.: `processos/<slug>/`), nunca solto na raiz.

## O que este método não faz

- Não inventa número. Volume, custo-hora e prazo que ninguém informou viram **premissa declarada** ou lacuna — com faixa, nunca com precisão falsa.
- Não mede o que não foi medido. Se a metade dos passos está sem tempo, o relatório diz isso e pede cronômetro em vez de prometer ganho.
- Não julga pessoa. O achado aponta desenho, sistema, alçada e cadastro.
- Não apresenta inferência como fato: o que for dedução entra marcado como hipótese.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Pular a normalização e ir direto ao diagrama | Sem `transcricao-enriquecida.md` o relatório não tem evidência para citar |
| Aceitar o JSON do LLM sem revisar | O modelo erra ordem e omite etapa secundária; confira tempo dito no relato e passos de retrabalho |
| Diagrama AS-IS bonito, mas idealizado | AS-IS é o processo real (com o "jeitinho"); o ideal é o TO-BE |
| Propor automação antes de eliminar | Automatizar desperdício só acelera o desperdício |
| Multiplicar etapa semanal pelo volume mensal | Calcule por período (semanal = ×4/mês) antes de falar de FTE-h |
| Entregar sem olhar o PNG | O script não vê cruzamento de seta nem rótulo em cima de seta |
| Entregar só o Mermaid quando o pedido é o desenho de apresentação | Use `render_fluxo.py`: raias com ícone do ator, ID do passo e seta condicional |
| Faixa órfã no fim do diagrama (um nó sozinho embaixo) | Ajuste `layout.colunas` para o fluxo fechar em duas faixas |
| Entregar PNG pequeno ou texto borrado | Renderize com `render_mermaid.mjs` (escala 3, texto vetorial); o render do Excalidraw é para editar, não para a imagem final |
| Entregar o material sem anonimizar quando ele sai do cliente | Nome do cliente está no título do desenho e no corpo do relatório: rode `anonimizar.py --regerar-png` antes de enviar |
| Anonimizar só o relatório e esquecer o PNG/SVG | O texto vive dentro da imagem; sem regerar, o nome continua desenhado no título |

## Arquivos

- `scripts/extrair_frames.sh` — vídeo/gravação de tela → frames + folhas de contato com timestamps.
- `scripts/extrair_processo.py` — transcrição → `processo.json` (LLM com schema estrito).
- `scripts/gerar_mermaid.py` — JSON → Mermaid AS-IS/TO-BE com raias.
- `scripts/render_fluxo.py` — JSON → diagrama de raias (SVG + PNG) para apresentação, com `layout` no JSON.
- `scripts/anonimizar.py` — troca nomes por rótulos genéricos em toda a pasta, renomeia arquivos e regera os PNG.
- `scripts/render_mermaid.mjs` — Mermaid → SVG vetorial + PNG em alta (escala 3), sem passar pelo Excalidraw.
- `scripts/metricas.py` — JSON → tabela de métricas e alertas.
- `references/frameworks-analise.md` — métricas, 8 desperdícios, 5 Porquês, Ishikawa, SIPOC-R de escopo, GUT de priorização de problemas, riscos, KPIs.
- `references/automacao.md` — como escolher entre regra, API, RPA, IA e workflow.
- `references/notacao-bpmn.md` — BPMN ↔ Mermaid, raias, boas práticas de diagrama.
- `references/roteiro-entrevista.md` — perguntas para completar lacuna quando o relato é raso.
- `templates/processo-json.md` — schema do `processo.json` (escrita manual, sem LLM).
- `templates/relatorio-processo.md` — esqueleto do relatório final.
- `templates/processo-as-is.mmd`, `templates/processo-to-be.mmd` — exemplos de diagrama.
- `exemplos/entrevista-atendimento-os.md` — evidência de exemplo (atendimento de OS) para calibrar o formato.

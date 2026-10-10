---
name: terras-consolidacao-de-memoria
version: 1.0.0
access: free
category: desenvolvimento
description: Mantém a memória de um repositório pequena e verdadeira: ao fechar uma spec, registra o que foi entregue e funde os requisitos num doc por domínio; compacta o histórico de decisões antigo em temas; audita convenção que o código já não segue. Só propõe, o dono aprova.
keywords: [consolidar specs, compactar historico, memoria do projeto, docs por dominio, fechar spec, changelog da spec, drift de convencao, documentacao inchada]
---

# Consolidação de memória do repositório

## Objetivo

Repositório que usa spec e ADR acumula documento: uma spec por feature, um plano por spec, um histórico que só cresce. Com o tempo o contexto fica grande demais e começa a mentir (spec antiga descrevendo comportamento que mudou). Esta skill faz o caminho contrário: **funde, compacta e corrige**, sempre por proposta que o dono do repositório aprova.

São quatro modos: **fechar**, **consolidar**, **compactar** e **auditar**.

## Onde está instalada

Fonte única: `skills/terras-consolidacao-de-memoria/` no repositório `terrasia-skills`. Adaptada do speccraft (MIT, ver `NOTICE`).

## Antes de começar

Descubra onde a memória mora **neste** repositório; não imponha uma estrutura. Procure: `CLAUDE.md`/`AGENTS.md`, `docs/specs/`, `docs/adrs/`, planos (`docs/**/plans/`), arquivo de decisões, backlog, convenções. Anote o mapa e use os nomes que já existem. Só proponha pasta nova (por exemplo `docs/dominios/<area>.md`) se nada equivalente existir, e diga isso na proposta.

## Modo fechar (ao concluir uma spec)

Entradas: a spec, o plano, as tarefas e o `git diff <commit de início>...HEAD`.

Produz, como proposta:

1. **Registro de entrega** da spec:
   ```markdown
   # Entrega — <título>
   fechada: AAAA-MM-DD

   ## Entregue vs. especificado
   - <o que foi implementado>
   - Desvio: <o que ficou diferente da spec, e por quê>

   ## Arquivos tocados
   - <arquivo>

   ## Decisão proposta
   AAAA-MM-DD — <título>
   - Decisão: <o quê>
   - Por quê: <motivo>
   - Consequência: <efeito>

   ## Convenção proposta
   - "<texto>" — por que surgiu nesta spec
   ```
2. **ADR**, se houve decisão de arquitetura ou de processo, no formato de ADR que o repositório já usa.
3. **Convenção nova**, só se for claramente geral e não específica desta spec.
4. **Atualização de arquitetura**, só se surgiu pacote, camada ou fronteira nova.

Este modo **não** consolida requisitos: isso é o modo seguinte. Atualizar convenção ou arquitetura não substitui a consolidação.

## Modo consolidar (spec fechada → doc do domínio)

O doc de domínio é a descrição **atual** de como uma área funciona, num lugar só, para ninguém precisar comparar specs fechadas.

1. **Roteamento:** em que domínio(s) a spec cai. Se a spec declara o domínio, ele manda. Senão, prefira um doc de domínio existente que combine; só proponha um novo com nome claro. Spec que toca vários domínios é dividida, e a divisão inteira aparece antes de qualquer escrita.
2. **Fusão por requisito:**
   - **ADICIONA:** acrescenta a linha com o sufixo `(spec <id>)`.
   - **MODIFICA:** substitui a linha localizada. O texto antigo vai **antes** para o arquivo de superados; a linha nova leva os dois ids.
   - **REMOVE:** apaga a linha localizada; o texto vai para o arquivo de superados.
3. **Conflito:** se a linha a modificar ou remover não é encontrada, ou é encontrada mais de uma vez, mostre antigo × novo e peça a decisão. Nunca adivinhe. Conflito recusado fica registrado na pasta da spec, o doc do domínio fica byte a byte igual, e a spec fecha mesmo assim.
4. **Arquivamento por último:** a spec e o plano só vão para a pasta de arquivo quando não houver conflito aberto.
5. **Arquivo não é contexto:** a pasta de arquivo e o arquivo de superados nunca são carregados como contexto de trabalho, só consultados para "de onde veio isso". Carregar o arquivo desfaz a consolidação.

Destino: só o doc de domínio. Consolidar nunca escreve em convenção, arquitetura ou histórico de decisões.

## Modo compactar (histórico de decisões)

Entradas: as decisões fora da janela recente (padrão: as 20 mais novas ficam intactas), os grupos temáticos que já existem na seção compactada e pares candidatos de "decisão nova substitui antiga".

Produz uma seção `## Compactado (fora da janela recente)` com grupos por tema:

```
### <tema>
Specs: <ids, ou —>
Arquivo: <caminho do histórico original arquivado>
<um parágrafo fiel com o que foi decidido e por quê>
Substitui: <antiga> → <nova>   # só quando o par foi aceito
```

Regras:

- **Funda, não regenere.** Grupo que já existe é preservado com a sua origem; o que é novo entra nele ou vira grupo novo.
- **A janela recente é intocável.** Decisão dentro da janela não é resumida nem marcada como substituída.
- **Fidelidade:** quem lê o resumo responde "por que isso foi decidido" e chega ao original pelo ponteiro `Arquivo:` e pelo git. Nenhuma decisão some.
- O original inteiro é copiado para o arquivo **antes** de qualquer corte.

## Modo auditar (convenção × código)

Entradas: as regras escritas (convenções, guardrails, regras duras do `CLAUDE.md`), o `git log` desde a última auditoria e uma amostra dos arquivos alterados.

Para cada regra que tenha padrão verificável, rode a busca (`git grep -nE '<padrão>'`) e classifique cada ocorrência:

- **violação real** → propor corrigir o código;
- **regra desatualizada** (o código mudou de propósito) → propor atualizar a regra;
- **convenção nova** que aparece nos commits recentes e não está escrita → propor registrar;
- **entrada velha** na arquitetura ou nas convenções que não reflete mais o código → propor remover.

## Regras duras

1. **Só propõe.** Nada é aplicado sem o "ok" do dono. Mostre o diff proposto de cada arquivo.
2. **Não invente decisão** que não aparece no diff, na spec ou no histórico.
3. **Conservador:** melhor propor de menos do que encher a memória de ruído.
4. **Específico vence vago:** "usar `logger` do pacote X" é convenção; "fazer bom log" não é.
5. **Nunca apague sem arquivar.** Todo texto removido ou resumido tem cópia íntegra no arquivo, conferida antes do corte.
6. **Respeite alterações locais.** Confira `git status --short` antes; não sobrescreva doc com mudança não commitada de outra sessão.

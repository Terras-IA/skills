---
name: terras-pipeline-de-automacao
version: "1.0.0"
description: >-
  Projeta e monta pipelines de automação em que scripts determinísticos executam
  o trabalho e o agente decide só em pontos de revisão fechados. Pipes and
  Filters com rastro de hashes (etapa se recusa a rodar sobre dado velho),
  recibos de execução (sucesso, falha sem deixar metade, já-estava-feito) e
  manuais em vez de leitura de código. Use quando pedirem automatizar de ponta
  a ponta um processo repetitivo (áudio, vídeo, documentos, relatórios, lotes
  de arquivos), projetar um pipeline com agente de código, ou consertar um
  pipeline que refaz trabalho, deixa artefato pela metade, perde a trilha de
  versão ou põe o modelo decidindo o que devia ser medido. Production
  pipeline, pipes and filters, provenance, receipts, idempotency, agentic
  workflow.
keywords: [pipeline, pipes and filters, rastro, recibo, idempotencia, provenance, receipts, hash, acervo, automacao, producao, revisao, agentic]
---

# Pipeline de automação: scripts medem, agente decide

Fonte única: `skills/terras-pipeline-de-automacao/` no repositório `terrasia-skills`. Abaixo, `$SKILL_DIR` é a pasta onde este `SKILL.md` está; `references/…` e `scripts/…` são relativos a ela.

## Objetivo

Transformar um processo repetitivo (ouvir áudios e digitar relatório, editar
vídeo, produzir documentos em lote) num pipeline que roda sozinho a cada
rodada sem retrabalho: filtros determinísticos conectados por rastro, com o
agente decidindo apenas onde há julgamento de verdade. Derivado do
My-Little-Studio (Iago Russi Ferla, 2026): um vídeo sai da fita bruta ao
exportado em minutos, com 29 scripts e 10 skills — a semana de edição virou
conversa de revisão.

A divisão que sustenta tudo: o que exige **entender linguagem** é do agente;
o que exige **exatidão, repetição ou verificação** é script.

## Regras duras

1. **Medição nunca vem de modelo.** Se o valor existe no arquivo — minuto de
   citação, posição, duração, contagem, hash — um script mede. O modelo decide
   só entre opções fechadas que um script gerou e outro script valida. (No
   artigo: LLM errando posição de elemento por 12% da largura da tela; o
   alinhamento de fala por modelo local, não por serviço pago.)
2. **Etapa roda sobre entrada registrada ou não roda.** Toda etapa grava o
   sha256 de tudo que leu; antes de produzir, confere as digitais. Entrada
   mudou → recusa e nomeia o comando que refaz o dado ("rode a revisão de
   novo"). Nunca trabalha sobre saída velha — nem "sabe melhor".
3. **Execução termina num de três finais, e o recibo registra qual:**
   sucesso; falha (nada pela metade persiste no acervo); já-estava-feito
   (idempotente — não refaz nem paga duas vezes). O recibo grava entradas,
   saídas, parâmetros, tempo, custo e versão de modelo usado.

## Como trabalhar

1. **Esculpir em filtros.** Um script, uma responsabilidade; `--help`
   completo; roda sozinho; lê arquivo e escreve arquivo. Normalização
   determinística vem primeiro (frame rate fixo, loudness alvo, formato de
   transcrição) para que etapas seguintes comparem coisas comparáveis. Antes
   de escrever script de vídeo/áudio novo, checar o acervo do `terras-ffmpeg`
   (42 scripts prontos, com `--dry-run` e `--json`); decisão fechada de
   campos definidos pode usar `terras-decisor`.
2. **Traçar a fronteira com formulários.** O agente não "conversa" com o
   pipeline: **preenche formulários gerados por script** — rascunho de
   revisão com campos fechados (manter/cortar, qual tentativa, dúvida
   marcada) — e a aplicação é script, que valida o formulário e **recusa
   aplicá-lo se a entrada mudou desde que o rascunho foi gerado**. Decisão
   livre em conversa não entra no pipeline.
3. **Rastro (acervo).** Cada item processado tem pasta própria; cada etapa
   grava as decisões que tomou e as digitais do que leu. É o que compra
   auditoria e voltar-atrás: qualquer artefato é rastreável aos brutos em
   dois saltos (produto → etapa → bruto), e qualquer reprocessamento sabe
   exatamente de qual ramo precisa.
4. **Recibos.** Sem recibo não há idempotência de verdade: a chave de
   "já-estava-feito" é a digitais das entradas + versão do modelo/pins.
   Mudou a versão do modelo → o dado regenera como versão nova; o que
   sustenta produto aprovado não é reescrito por baixo. Custo por execução no
   recibo é o que torna "não pagar duas vezes" verificável.
5. **Manuais, não código.** Uma skill-manual por **tipo de trabalho** (não
   por script): quando usar, qual script, quais parâmetros, onde olhar quando
   quebra. O agente opera o pipeline lendo manuais; código abre só na quebra.
   Criar ou revisar o manual: `terras-skill-factory`.
6. **Medir antes de agir; duas camadas quando precisar.** Só limpa ruído se a
   medição disser que precisa. Quando coexistirem uma camada barata local de
   alta frequência (ex.: transcrição fonética que preserva retakes) e uma
   cara de qualidade (ex.: texto bem escrito de serviço pago), a divergência
   entre elas vira **pergunta ao agente** — nunca erro silencioso, nunca
   escolha muda de uma.
7. **Fechar o laço.** Toda sessão termina com a pergunta: onde o agente
   travou, o que divergiu, o que quebrou. O que se repete vira script; o que
   confunde vira manual; a decisão fechada que já tem dados suficientes pode
   migrar de LLM para classificador pequeno. O pipeline melhora por sessão,
   não por herói.

## Sinais de pipeline errado (o que esta skill fecha)

- Modelo fornecendo número que existe no arquivo (minuto de citação,
  coordenada, ponto de corte).
- Etapa rodando sobre saída velha sem saber — ou rascunho aplicado sobre
  transcrição que já mudou.
- Reexecução refaz tudo (ou paga duas vezes) ou deixa artefato pela metade
  no acervo.
- Agente relendo código a cada sessão para saber operar o pipeline.
- Validação "no olho" em conversa, sem formulário que um script possa
  recusar.

## Quando não usar

Trabalho de uma vez só (sem repetição não há pipeline a construir), ou
tarefa em que cada rodada difere tanto que não existe cadeia a reaproveitar —
nesse caso é uma skill de procedimento (`terras-skill-factory`), não um
pipeline.

## Referências

- `references/metodo-anotado.md` — os princípios com as evidências medidas do
  artigo: 12% de erro de posição, fita fonética × serviço pago, recusa de
  revisão sobre dado velho, quadros visuais, stress test de 8 bibliotecas.
- `references/testes.md` — o vermelho registrado (as seis falhas de um
  agente sem esta skill), os cenários de pressão e os resultados da bateria
  de testes.
- `scripts/referencia-minima.py` — pipeline de duas etapas que implementa as
  três regras duras como mecanismo (rastro com recusa nomeando o comando,
  recibos de três finais com custo, falha atômica por tmp+rename), validado
  por 14 cenários. Esqueleto para adaptar ao começar um pipeline real.

## Fonte

Método derivado do artigo "My-Little-Studio" — Iago Russi Ferla,
<https://iago-russi.vercel.app/artigos/pipeline/> (set/2026). Crédito ao
autor; nenhum trecho copiado. Complementos da casa citados no corpo:
`terras-ffmpeg`, `terras-decisor`, `terras-skill-factory`.

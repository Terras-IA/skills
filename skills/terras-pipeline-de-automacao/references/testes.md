# Testes de aderência (vermelho → verde)

Protocolo da casa (`terras-skill-factory`): cenário de pressão rodado num
agente **sem** a skill, falhas registradas, skill escrita mirando nelas, e o
mesmo cenário reverificado **com** a skill.

## Cenário de pressão

> Construtora, 3 fiscais mandam áudio de WhatsApp de 5–15 min toda sexta
> relatando a obra. Hoje alguém ouve tudo e digita um relatório semanal em
> Word: resumo por obra, pendências com responsável e prazo, e citação
> literal dos trechos mais importantes **com o minuto do áudio**. Às vezes
> precisa voltar num áudio de semanas atrás. Projetar a automação com agente
> de código + scripts: arquitetura, o que é script × decisão do agente,
> organização de artefatos, rodada de ponta a ponta, reexecução e chegada
> tardia.

(Video edição também serve; o cenário em domínio não-testa se o método
transfere ou se o agente só reconhece o exemplo.)

## Vermelho — 2026-10-02, GLM (agente auxiliar de propósito geral, sem a skill)

O que o agente **acertou sozinho** (registrar para não atribuir à skill o que
o modelo já sabe): fronteira script × agente, gates validando citação ×
transcrição, checksum sha256 na entrada, cache por semana, índice
append-only, versões nunca sobrescritas.

As **seis falhas** que a skill fecha:

1. **Rastro sem mecanismo** — afirmou que "novo checksum invalida o ramo
   (transcrição → extração → gates)" sem dizer quem confere o quê; nenhuma
   etapa confere digitais antes de produzir; nenhum recusa nomeando o
   comando que refaz o dado.
2. **Sem recibos de execução** — tem estados de negócio (`incompleta`,
   `requer_humano`), mas nenhum recibo com os três finais (sucesso / falha
   atômica / já-estava-feito), tempo e custo; "não pagar duas vezes" ficou
   implícito no cache, não verificável.
3. **Camada de manuais ausente** — nada de "o agente opera por manuais;
   código abre só na quebra". Não apareceu nem como ideia.
4. **Uma camada de sensor só** — escolheu um STT; sem par barato-local ×
   caro-qualidade com divergência virando pergunta.
5. **Sem laço de melhoria** — nada de perguntar ao agente onde travou e
   devolver para scripts/manuais; o projeto nasce pronto e estaciona.
6. **Rascunho sem checagem de velhice** — gates validam conteúdo, mas nenhuma
   regra recusa *aplicar* um rascunho gerado sobre entrada que mudou desde a
   geração.

## Verde — protocolo de reverificação

Rodar o mesmo cenário num agente que leia o `SKILL.md` antes de responder.
Passe = o desenho traz, espontaneamente: (a) conferência de digitais antes de
cada etapa produzir, com recusa nomeando o comando; (b) recibo com três
finais, tempo e custo; (c) camada de manuais (uma por tipo de trabalho);
(d) divergência entre duas camadas de sensor como pergunta ao agente; (e) o
laço de melhoria como etapa da rodada; (f) recusa de aplicar rascunho sobre
entrada velha. Falha = registrar a racionalização nova aqui, fechar a brecha
no SKILL.md, repetir.

### Registro das reverificações

- 2026-10-02 — verde com a v1.0.0: seis/seis fechadas. O agente leu o
  SKILL.md e o desenho trouxe espontaneamente (a) conferência de digitais
  antes de cada etapa produzir, com recusa nomeando o comando; (b) recibo com
  três finais, tempo e custo e escrita atômica; (c) pasta de manuais no
  layout do acervo; (d) duas camadas de transcrição com divergência virando
  pergunta; (e) o laço de melhoria como etapa da rodada; (f) recusa de
  aplicar rascunho sobre entrada velha. Foi além do cenário: minuto da
  citação recalculado por script e citação extraída verbatim da transcrição,
  não do rascunho do agente.

## Bateria de testes — 2026-10-02

### Teste 1 — transferência de domínio (vídeo): PASS

Cenário: 20 webinars/semana, cortar silêncio, legendas, loudness, dois
formatos, gravação substituída depois do processamento. Agente com a skill:
seis/seis regras presentes, mais roteamento para o acervo do `terras-ffmpeg`
antes de escrever script, estimativa de custo antes do STT pago, carry-over
de decisões de v1 para v2 feito por script (segmentos idênticos herdam
decisão), ramo v1 congelado como trilha de auditoria e recusa do atalho
"re-exportar com master de v1".

### Teste 2 — fronteira (tarefa única): PASS

Cenário: cortar 3 minutos e legendas de um vídeo único. Agente com a skill:
reconheceu "Quando não usar" e não construiu pipeline — "projeto o trabalho,
não a fábrica" — mantendo só os invariantes de custo zero (medição por
script, falha sem metade, checar `terras-ffmpeg`, decisões fechadas) e a
pergunta do laço ("isso vai se repetir?").

### Teste 3 — acionamento orgânico: FAIL → corrigido no nome

Descoberta de harness: neste runtime, a lista de skills chega ao agente com
**nome e caminho apenas, sem descrições** — o acionamento casa pelo nome.
Para "automatizar toda semana 5 áudios → ata", o agente leu
"pipeline-de-producao" como outro domínio e disse que NÃO a carregaria.
Vermelho adicional registrado:

7. **Nome não carrega o gatilho** — em harness que não exibe descrições,
   "producao" esconde o caso de uso "automatizar".

Correção: skill renomeada de `terras-pipeline-de-producao` para
`terras-pipeline-de-automacao` (symlinks refeitos; conteúdo inalterado, o
verde acima continua valendo).

### Teste 4 — mecânica das regras duras (validação prática): 14/14 PASS

`scripts/referencia-minima.py` + cenários (rodados em /tmp, script copiado
para a skill): primeira rodada sucesso com custo e tempo no recibo; rerun
devolve já-estava-feito sem regravar recibo nem somar custo; adulteração no
acervo faz a etapa seguinte recusar com exit 2 **nomeando o comando**
(`normalizar --refazer`) e registra a recusa como falha no recibo; o comando
nomeado refaz a partir do bruto e descarta o dado adulterado; falha forçada
no meio da etapa não deixa produto nem `.tmp` no acervo e o rerun recupera;
entrada nova refaz a cadeia (chave de idempotência inclui as digitais da
entrada). Uma asserção do cenário S4 estava errada (esperava a linha
adulterada no produto; o correto é ela sumir) — corrigida no cenário, não no
pipeline.

Próxima revisão da skill deve rerodar os quatro testes.

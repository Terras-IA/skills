# Método anotado — as evidências do My-Little-Studio

Fonte: artigo "My-Little-Studio", Iago Russi Ferla (set/2026),
<https://iago-russi.vercel.app/artigos/pipeline/>. Iago foi editor de vídeo
por 4 anos (canal Ossos Perdidos) e é hoje engenheiro de software; o projeto
nasceu numa consultoria com Dyego Maas e leva um vídeo de ~2 min da fita
bruta ao exportado em minutos — processo que levava mais de uma semana.
Cada regra da skill corresponde a uma destas evidências medidas.

## Por que medição nunca vem de modelo

- Perguntar posição de elemento na tela ao Gemini dava erro de **12% da
  largura da tela** — inaceitável para corte e enquadramento. Detecção vem de
  visão computacional local: YuNet (rosto), MediaPipe (silhueta), RTMPose
  (mãos/ombros), escolhidos por stress test contra SAM 2, CoTracker, YOLO e o
  próprio Gemini — os três primeiros venceram.
- O modelo serve para **decisões fechadas** geradas por script: formulário de
  revisão de corte preenchido "como um editor" (manter a última tentativa das
  frases repetidas, borda do corte no início da sílaba), validado e aplicado
  por script.
- Nota do autor: decisões fechadas e rápidas tendem a migrar do LLM para
  classificadores pequenos e baratos (ele cita o modelo Jev, "System One").
  Na casa, o equivalente é `terras-decisor` (YAML de campos definidos) e o
  lab do JEV já em experimento.

## Por que rastro e recibos

- Cada etapa grava **decisões + sha256 de tudo que leu**. Caso real do
  artigo: uma revisão de corte aplicada sobre uma fita transcrita que já tinha
  mudado — o pipeline **recusou e mandou rodar a revisão de novo**. Sem as
  digitais, o corte teria saído silenciosamente errado.
- Recibos registram entradas, saídas, parâmetros, **tempo e custo**. Execução
  termina em sucesso, falha (**nada pela metade fica no acervo**) ou
  "já estava feito". Sem isso: refaz-se trabalho pago ou persiste artefato
  incompleto.
- Normalização determinística na entrada torna etapas comparáveis: frame rate
  fixo em 30fps, áudio extraído e alinhado, loudness final em −14 LUFS.
  Limpeza de ruído só roda **se a medição (DNSMOS) indicar**.

## Por que duas camadas de sensor

- A **fita** é transcrição fonética local (wav2vec2, resolução de 20ms) —
  barata, local, e preserva **retakes** (tentativas repetidas de fala), que
  serviços pagos descartam como ruído.
- O **texto bem escrito** vem de serviço pago (AssemblyAI). Palavras que não
  batem entre as duas camadas viram **dúvidas para o agente** decidir —
  nenhuma camada é fonte única da verdade.
- Lição geral: um sensor local barato de alta frequência + um sensor caro de
  qualidade, com divergência virando pergunta, supera qualquer um dos dois
  sozinho.

## Por que manuais (skills), não código

- 29 scripts, **10 skills manuais**: o agente lê o procedimento do tipo de
  trabalho (quais scripts, quais parâmetros, onde olhar quando quebra) em vez
  de ler código — contexto economizado a cada sessão. Código abre só na
  quebra.

## Por que quadros visuais (quando texto não especifica)

- Para animação e corte, texto não dá conta: Iago edita sobre **quadros HTML**
  (rascunho, animação, corte), desenhando e anotando diretamente sobre o
  vídeo quadro a quadro. O primeiro rascunho teve **123 traços e 15 notas**.
- O export do quadro (frame + desenho + instrução) é o prompt — a IA lê
  desenho melhor que prosa.
- Bônus que fecha o laço: a **explicação textual que o agente dá do desenho**
  vira a especificação que automatiza o quadro como script no futuro.

## Por que o laço de melhoria

- A prática de fim de sessão — perguntar ao agente onde teve dificuldade, o
  que divergiu, o que quebrou — torna o projeto **mais robusto a cada
  sessão**. É o mesmo invariante do laço de melhoria do motor terrasia: o que
  se mede sobre o processo volta para o processo.

## Arquitetura em uma frase

Pipes and Filters: filtros independentes (cada um com `--help`, rodável e
testável sozinho) ligados por rastro; a metade determinística carrega o
pipeline, a metade não-determinística só decide nos pontos onde há
formulário. O custo total do artigo fica essencialmente no plano do Claude —
serviços externos (AssemblyAI, gpt-image-2) são opcionais, e animação de
páginas HTML + GSAP é renderizada quadro a quadro num Chrome invisível e
unida com FFmpeg.

---
name: terras-instagram
description: Escrever legendas e hashtags para o Instagram do IECSJC a partir das imagens geradas (timeline/ e stories/), validar imagens e registrar o que foi publicado; a publicação é manual, feita pelo usuário no app/navegador. Use quando o usuário pedir legenda de post da igreja, hashtags, revisar legenda de Instagram, ver o que está pendente na fila, avisar que publicou manualmente, ou perguntar sobre o Instagram da igreja.
keywords: [instagram, post, legenda, hashtags, story, carrossel, publicar, registrar, fila, iecsjc, igreja]
---

# Terras — Instagram IECSJC

## Contrato

**Modo atual (decisão do usuário em 03/10/2026): a publicação é manual.** Ciclo: escolher imagem da fila → validar → escrever legenda no tom da casa → mostrar para aprovação → o usuário publica pelo app/navegador → registrar em `postagens.json` com `ig.py registrar`. A conta é @aigrejadesaojose (Instagram da igreja). A publicação via API (seção mais abaixo) fica parada; só retomar se ele pedir.

A skill consome imagens prontas; não gera arte (para arte, ver as skills de imagem/generativas do usuário). Não entregar legenda com dados inventados (horários, datas, endereços) nem fora da fila. Nunca alegar publicação que não aconteceu: publicação por API só existe quando o script imprime `PUBLICADO:`/`AGENDADO:`; publicação manual só entra no registro depois que o usuário confirma.

Usar as ferramentas do ambiente atual; não depender de nomes de ferramentas de outro harness.

## Onde está instalada

Fonte única: `skills/terras-instagram/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

O `config.json` com o token é local da máquina e fica fora do git (o `.gitignore`
protege): nunca colar token em chat, log ou commit; se vazar, revogar trocando a
senha do Instagram.

## Estrutura da fila (projeto)

`~/Documents/IECSJC/instagram/`:

- `timeline/` — imagens 4:5 ou 1:1 para o feed. Cada postagem de feed leva legenda.
- `stories/` — imagens 9:16 com texto já na arte. Story não tem legenda pela API e dura 24h.
- `postagens.json` — estado gerado pelo script (publicadas e agendadas). Não editar à mão.
- `publicados/` — se o usuário quiser arquivar os originais depois de publicar (manual, a skill sugere).

Fila é por antiguidade: `ig.py fila` lista as não registradas, mais antigas primeiro. Imagem fora dessas pastas entra na fila só se o usuário pedir (copiar para a pasta certa antes).

## Fluxo padrão

1. **Ver a fila**: `python3 $SKILL_DIR/scripts/ig.py fila --pasta <raiz>`. Se o config já existe, o `--pasta` é dispensável.
2. **Escolher a imagem** com o usuário (ou a mais antiga, se ele pedir "próximo da fila"). Saber o assunto: perguntar em uma linha só se a arte não contar a história sozinha.
3. **Validar**: `ig.py validar --arquivo <imagem>`. PNG vira JPEG, lados acima de 1440px são reduzidos, proporção fora do padrão gera aviso.
4. **Escrever a legenda** (seção abaixo) e entregá-la pronta para copiar, junto com o texto alternativo (descrição da imagem para leitor de tela). Post com horário, data ou endereço só sai com o dado confirmado pelo usuário.
5. **Registrar depois que ele publicar**: quando o usuário confirmar a publicação, rodar `ig.py registrar --arquivo <imagem>` para a fila não repetir o item.

## Escrever a legenda

A legenda é copy da igreja, não anúncio nem corrente de bênção. Tom da casa: caloroso, simples, reverente sem cerimônia, português do Brasil falado, frases curtas.

Estrutura:

1. **Primeira linha** (até 125 caracteres): precisa fazer sentido sozinha, cortada atrás do "ver mais". É o convite para expandir, nunca "Neste post vamos falar sobre...".
2. **Corpo**: 2 a 5 linhas. Uma ideia por linha. Se a arte já diz o essencial (artes de evento costumam dizer), a legenda acrescenta o que a imagem não alcança: contexto, convite, o que a pessoa faz com aquilo.
3. **CTA honesto**: "salve", "marque alguém que precisa ouvir isso", "compartilhe com seu grupo", convite ao culto. Sem pressão emocional e sem promessa de resultado ("Deus vai te abençoar hoje" vira desejo, não garantia).
4. **Hashtags**: 4 a 8, no fim. Base fixa no `config.json` (`hashtags_base`) + 1 a 3 do tema do post. Sem hashtag genérica solta (#love, #deus é ruído).

Regras duras:

- **Zero travessão "—".** Marcador de texto de IA. Vírgula, ponto ou dois-pontos resolvem.
- **Nada de dados inventados.** Horário de culto, endereço, data, preço, nome de pregador: só se o usuário ou material da igreja confirmar. Em dúvida, perguntar em uma linha; se não houver resposta, escrever a legenda sem o dado e avisar.
- Máximo 2200 caracteres (o script barra acima disso). Banda boa para feed: 300 a 800.
- Emojis com moderação e coerentes (1 a 3; cruz, pomba e mãos combinam; evitar chuvisco de emojis decorativos).
- Bíblia citada: referência no formato da casa, `Salmo 23:1` ou `Romanos 8:28`, texto conforme o próprio post, sem paráfrase longa.
- Texto alternativo descreve a imagem em uma frase para leitor de tela ("Cartaz azul com título ... e data ..."). Nunca repete a legenda.

## Registrar (dia a dia) e API (parada)

Todos os comandos com `python3 $SKILL_DIR/scripts/ig.py` (abreviado `ig.py` abaixo).

No modo manual, os comandos do dia a dia são `fila`, `validar` e `registrar`. Os comandos de API continuam no script, mas estão parados por decisão do usuário: não insistir para configurar a Meta nem para publicar por eles.

```bash
# API (parada): feed agora (legenda em arquivo evita dor de aspas)
ig.py publicar -a "timeline/encontro-unificado.png" \
  --legenda-arquivo legenda.txt \
  --texto-alternativo "Cartaz azul do Encontro Unificado com data e horário"

# story agora (sem legenda; imagem de stories/ já tem o texto na arte)
ig.py publicar -a "stories/Festival Jovem Congregacional Neon.png"

# agendar feed para sexta às 19h (hora local, 10 min a 75 dias à frente)
ig.py publicar -a "timeline/reforma-protestante.png" \
  --legenda-arquivo legenda.txt --agendar "2026-10-09 19:00"

# carrossel de 3 imagens do feed
ig.py publicar -a timeline/1.png -a timeline/2.png -a timeline/3.png --legenda-arquivo legenda.txt

# conferir conta, token e limite (100 posts/24h)
ig.py verificar

# publicado na mão no app? registrar para a fila não repetir
ig.py registrar --arquivo "timeline/encontro-unificado.png"
```

Comportamentos que importam:

- O Instagram só aceita imagem em **URL pública**: o script sobe a cópia para o bucket configurado (`hospedagem` no config), cria o container, espera o Instagram baixar e apaga a cópia. Sem hospedagem configurada, passar `--url` com a imagem já online.
- Agendamento é nativo da API (`publish_time`): o post sai sozinho na hora, sem computador ligado. Story não agenda.
- Legenda publicada **não se edita** depois pela API. Erra? Apagar e republicar (e avisar o usuário do custo).
- Container expira em 24h se não publicado; o script publica em seguida, então isso só importa em falha manual.
- Erro da API chega com a mensagem original do Instagram; traduzir em português o que fazer, sem colar o JSON cru no usuário.

## Programação recorrente (automação, parada)

**Não criar automações de publicação: o modo atual é manual (decisão do usuário em 03/10/2026).** Se um dia ele retomar a API e definir a programação (ex.: "sexta 19h e domingo 9h"), criar automação com a ferramenta de agendamento do ambiente (no ZCode, `CronCreate`), uma por horário, usando este prompt-modelo, ajustado para o horário e a pasta:

> Use a skill terras-instagram. Pegue a imagem mais antiga pendente em ~/Documents/IECSJC/instagram/timeline (use `ig.py fila`), escreva a legenda no tom da skill usando o assunto da arte, salve em legenda.txt e publique com `ig.py publicar` sem `--agendar`. Se a fila estiver vazia, termine avisando isso em uma linha. Se a API falhar, registre o erro no relatório final e não tente de novo na mesma execução.

Regras da automação: só criar quando o usuário pedir explicitamente com horários; nunca agendar story; reportar ao usuário o link de cada post publicado na execução. Token expirado quebra a automação: `ig.py verificar` antes aponta (aviso aos 50 dias) e a renovação é `ig.py token --renovar`, que precisa de `app_secret` no config.

## Configuração inicial (parada)

`referencias/configuracao-meta.md` tem o passo a passo: conta profissional, app na Meta, token de longa duração, bucket no Supabase e preenchimento do `config.json`. O bucket e o `config.json` já foram criados em 03/10/2026 (hospedagem pronta; campos da Meta em branco), mas o usuário desistiu do setup da Meta: só retomar se ele pedir. Sem credenciais, `fila`, `validar` e `registrar` funcionam normalmente.

## Limitações conhecidas

- Só JPEG na API (o script converte de PNG). Máximo 8 MB e 1440px de lado (o script normaliza).
- Story pela API: sem legenda, sem agendamento, some em 24h.
- Legenda não edita após publicar. Carrossel: máx. 10 imagens.
- A API não publica em conta pessoal comum; exige conta profissional (Business ou Creator).

## Exemplos de prompt do usuário

- "Escreve a legenda e as hashtags desse cartaz" (com imagem anexada ou apontada)
- "Escreve a legenda pro story do Festival Jovem"
- "Publiquei essa no Instagram, registra aí" (rodar `ig.py registrar`)
- "Quais imagens ainda estão pendentes?" (rodar `ig.py fila`)
- "Voltei a querer a API" (só então seguir `referencias/configuracao-meta.md`)

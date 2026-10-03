---
name: terrasia-pauta-youtube
description: "Pesquisa de demanda (envelope) no YouTube antes de escrever o roteiro: compara consultas de tema pela mediana de views dos resultados, acha outliers (video muito acima da media do proprio canal) e colhe frases recorrentes dos titulos de melhor desempenho. Use quando o pedido envolver escolher tema de video, 'dar o passo atras', pauta de video, qual assunto rende mais, medir demanda de titulo, modelar o que funciona, outliers do YouTube, banco de frases de titulo e capa, ou antes de montar um roteiro com a terras-video."
keywords: [youtube, pauta, tema, envelope, demanda, views, outlier, titulo, capa, thumbnail, pesquisa, roteiro, terrasia]
---

# Pesquisa de pauta do YouTube (envelope)

Responde, antes do roteiro existir: **que embalagem deste assunto tem demanda
comprovada?** O método vem do vídeo do Joba ("dar o passo atrás" + "modelar o
que funciona"): o assunto que você quer tratar raramente é a consulta que a
audiência digita; entre o assunto e a audiência existe um passo atrás, e é
ele que decide o alcance.

Divisão de trabalho: **o agente inventa os candidatos de consulta, o motor
mede.** Gerar "como crescer no YouTube" a partir de "qual a taxa de cliques
ideal" é julgamento editorial seu; ranquear os candidatos pelos números é
trabalho do script.

## Onde está instalada

Fonte única: `skills/terrasia-pauta-youtube/` no repositório `terrasia-skills`. Cada agente
enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh` do
repositório, então a edição se faz lá e vale para todos. Nos comandos abaixo,
`$SKILL_DIR` é a pasta onde este `SKILL.md` está.

## Instalação (sem sudo, idempotente)

```bash
bash $SKILL_DIR/scripts/setup.sh
```

Cria `~/.config/terrasia-pauta-youtube/venv` com `yt-dlp` (nesta máquina o
`apt` não funciona; nada aqui depende dele). Sem OAuth, sem chave de API, sem
cookie de navegador: só busca pública. Bônus: um symlink do
`venv/bin/yt-dlp` para `~/.local/bin` liga também a pista de YouTube da
`terras-last30days`, que hoje está desativada por falta dele.

## Pipeline de uso

1. **Invente os candidatos.** Dado o assunto bruto, proponha 2 a 4 consultas
   de "passo atrás" — o que a audiência do tema digita na busca. Inclua
   sempre o próprio assunto como candidato, para a comparação mostrar a
   distância.
2. **Meça com `comparar`.** Uma execução, todos os candidatos, e a tabela
   ranqueia pela mediana de views dos resultados.
3. **Aprofunde o vencedor com `pesquisa`.** Mostra cada resultado com o score
   de outlier, para achar o vídeo-modelo (e o canal que vale estudar).
4. **Colha as frases com `frases`.** N-gramas recorrentes nos títulos de
   melhor desempenho das consultas — o banco de frases que alimenta o título
   e a capa no pacote da `terras-video`.

Rode com timeout de 300000 ms na ferramenta de shell. Cada consulta é uma
requisição de busca e cada canal distinto dos primeiros resultados é mais
uma (mediana dos últimos 20 vídeos), com cache de 14 dias em
`~/.config/terrasia-pauta-youtube/cache-canais.json`.

```bash
SKILL="$SKILL_DIR/scripts/pesquisa.py"

# passo 2: qual envelope tem demanda (exemplo real do vídeo do Joba)
python3 "$SKILL" comparar "qual a taxa de cliques ideal" "como crescer no YouTube"

# passo 3: os vídeos-modelo do vencedor
python3 "$SKILL" pesquisa "como crescer no YouTube" --n 12

# passo 4: banco de frases de título
python3 "$SKILL" frases "como crescer no YouTube" "crescer no YouTube do zero" --top 12

# contrato estável para leitura programática
python3 "$SKILL" comparar "rag do zero" "o que é RAG" --json
```

## Como ler o resultado

- **Mediana de views da consulta** é a medida de demanda do envelope: o vídeo
  mediano daquela busca alcança aquilo. Máximos enganam menos que parecem,
  mas sozinhos não dizem se a consulta é pequena.
- **Score de outlier** (views do vídeo ÷ mediana do canal que publicou): um
  vídeo de 169k num canal de mediana 8k (21x) prova que o **tema** puxa
  audiência além da base; 800k num canal de 5 milhões (0,2x) diz que o canal
  puxa, não o tema. Outlier forte é 5x ou mais; 2x a 5x é acima da média.
- **Banco de frases** diz o vocabulário com que o nicho promete: "comece do
  zero sozinho", "curso completo", "essa sacada muda tudo". Frequência 2+ só
  nos 40 melhores títulos por views, então o que aparece já é padrão, não
  coincidência.

## Regras

- **Modelar é diferente de copiar.** O banco de frases informa estrutura e
  vocabulário do título e da capa; título final é seu, e a regra da casa
  continua valendo: não prometer o que o vídeo não entrega.
- **Demanda passada não garante nada.** O número mede o que já funcionou na
  busca; é bússola para escolher envelope, não previsão de views. Descoberta,
  não fonte — mesma regra da `terras-last30days`.
- **Sem janela de tempo.** Vídeo de 4 anos atrás com 31k views é sinal de
  demanda tão válido quanto o da semana passada; este motor mede demanda
  acumulada, não discurso recente (que é o trabalho da `terras-last30days`).

## Relação com as outras skills

| Skill | Pergunta |
|---|---|
| `terrasia-pauta-youtube` (esta) | Que embalagem tem demanda comprovada? |
| `terras-last30days` | O que se falou nos últimos 30 dias? |
| `terras-video` | Como virar vídeo (roteiro, pacote, upload) |

A entrega típica desta skill é o insumo da próxima: envelope escolhido,
vídeos-modelo com score e banco de frases, que entram no roteiro e no
pacote de publicação da `terras-video`.

## Exemplos de prompt do usuário

- "quero fazer um vídeo sobre MCP, qual o melhor encaixe de tema?"
- "compara 'rag do zero' com 'o que é RAG' antes de eu escrever o roteiro"
- "quais frases de título funcionam pra vídeo de terminal?"
- "o short que eu fiz sobre skills rendeu pouco — era o tema ou a embalagem?"

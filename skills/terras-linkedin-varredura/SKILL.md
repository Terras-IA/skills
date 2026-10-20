---
name: terras-linkedin-varredura
description: "Varre o feed do LinkedIn desde a última verificação (ou 24 h), tria o que é novo e gera nota de conhecimento de cada post útil (vídeo, imagem ou texto), com checkpoint. Use para 'varre o feed', 'o que saiu desde ontem', 'traz o conhecimento do feed'. Post único ou tema: terras-linkedin-conhecimento."
keywords: [linkedin, feed, varredura, checkpoint, últimas 24 horas, desde a última verificação, conhecimento, nota de estudo, vídeo, imagem, rotina, digest]
---

# terras-linkedin-varredura

Orquestra a `terras-linkedin-conhecimento` e a `terras-linkedin-videos` numa rotina: lê o feed logado, pega tudo que é novo desde a última passada, separa o que ensina algo e devolve uma nota conferida por post. Abaixo, `$SKILL_DIR` é a pasta deste `SKILL.md`, `$SCRATCH` é o scratchpad da sessão e `CONH` é `~/linkedin/conhecimento`.

## Objetivo

O feed não espera: post bom de ontem some sob os de hoje. A skill transforma "abrir o LinkedIn e rolar" numa varredura com começo e fim: janela definida, coleta até passar dela, triagem que não reprocessa nada, notas no padrão da `terras-linkedin-conhecimento` e um checkpoint para a próxima rodada começar onde esta parou.

Limite honesto: o feed é algorítmico, não cronológico, e não tem ordenação por data (`?sortBy=RECENT` redireciona). A varredura cobre o que o LinkedIn mostrou, não tudo que as conexões publicaram. Diga isso na entrega com os números (cargas, cards, únicos na janela).

## Regra dura

1. **Navegador só lê.** Nada de curtir, comentar, seguir, salvar nem abrir menu de post. O coletor não clica em nada; a URN sai das props do React. "Copiar link" escreve na área de transferência do usuário: proibido.
2. **Nunca fazer login.** Título diferente de "Feed | LinkedIn" ou tela de entrada: parar e pedir para o usuário entrar no navegador embutido.
3. **A data vem da URN.** O ID carrega o instante de publicação (`id >> 22` = epoch em ms). O rótulo "há 19 h" é arredondado e só vale para card sem URN (`ts_aprox`).
4. **Chamar a skill é o sim.** Não pedir aprovação de lista nem de vídeo: estudar, baixar e escrever as notas fazem parte do pedido. Teto de **15 notas por rodada**: o excedente vai como `--falhas` no fechamento e volta como pendente na próxima.
5. **Checkpoint só no fim.** `varredura.py fechar` roda depois das notas e do índice. Post que falhou (download, conteúdo restrito, nota não escrita) entra em `--falhas` e não se perde. Fechar antes de terminar apaga a rodada.
6. **Veredito só com fonte.** Cada nota segue a regra da `terras-linkedin-conhecimento`: `certo`, `precisa nuance` ou `errado` exige fonte primária consultada; sem consulta, `não conferi`. Volume não é desculpa.
7. **JSON do coletor gravado como veio.** `feedVarrerResultado()` vai para o arquivo com a ferramenta de escrita, sem reformatar, resumir nem trocar campo.

## Como trabalhar

1. **Janela.**
   ```bash
   python3 "$SKILL_DIR/scripts/varredura.py" janela          # ou --horas N se o usuário pediu
   ```
   Devolve `desde_ms` e a origem. Quem vence: o checkpoint, com 6 h de margem para trás (o feed mostra post antigo tarde; `vistos` impede repetir). Sem checkpoint, 24 h. Checkpoint de mais de 7 dias, corta em 7. `--horas N` só quando o usuário nomeou a janela ("últimas 24 h", "desde ontem"); "24 h ou desde a última" é o padrão, sem `--horas`.
2. **Abrir o feed.** `navigate` para `https://www.linkedin.com/feed/`. Conferir o título. Se `innerHeight` for 0 (painel escondido), `resize_window` 1280x900 e recarregar.
3. **Coletar uma carga.** No `javascript_tool`, colar `scripts/feed_varrer.js` inteiro e, na mesma chamada, `feedVarrerInicio(<desde_ms>)`. Depois repetir `await feedVarrer({segundos: 35})` (cada chamada tem limite de 45 s) até `parar: true`. Então `feedVarrerResultado()` e gravar a string em `$SCRATCH/feed-carga-<n>.json`.
4. **Mais cargas.** Uma carga de página rende 40 a 80 cards e trava (`motivo: 'carga esgotada'`); rolar mais não adianta. Rodar `varredura.py triar $SCRATCH/feed-carga-*.json`: se `ultima_carga_novos` for 3 ou mais e houver menos de 3 cargas, recarregar o feed, colar o `feed_varrer.js` de novo (o CSP do LinkedIn barra `eval`), `feedVarrerInicio(<mesmo desde_ms>)` e coletar. Na nova carga, `feedVarrerResultado([ids e autores já gravados])` devolve só o que é novo. `motivo: 'passou da janela'` encerra a coleta.
5. **Triar.** A última chamada do `triar` grava `CONH/varredura/AAAA-MM-DD-HHMM.md` e `.json` e lista os `candidatos` (novos, na janela, não promovidos, não vistos, não estudados) com `alertas` (`vaga`, `pessoal`, `evento`, `pendente`).
6. **Escolher pelo texto.** Estudar o que traz técnica, dado, ferramenta, decisão de arquitetura ou lição aplicável. Descartar com motivo de uma linha: política, motivacional, vaga, autopromoção sem conteúdo, notícia sem técnica, piada. Alerta ajuda, não decide. Escrever a decisão na seção "Decisão" do `.md` da triagem.
7. **Baixar de uma vez.**
   ```bash
   python3 "$SKILL_DIR/../terras-linkedin-conhecimento/scripts/baixar_post.py" URL [URL ...]
   ```
   Todos os escolhidos, inclusive os de vídeo (dá o texto integral e a pasta da nota). O tipo do feed é palpite: o que vale é o retorno do script. Com `aviso: post tem vídeo`, baixar também com `$SKILL_DIR/../terras-linkedin-videos/scripts/baixar_lote.py` e analisar pela `terras-video-downloader` (folhas de quadros) e pela `terras-transcription` (fala).
8. **Escrever as notas.** `conhecimento.md` na pasta de cada post, pelo modelo de `terras-linkedin-conhecimento/references/modelo-conhecimento.md`, com Read de cada imagem antes. Até 3 notas, aqui. Mais que 3: um agente auxiliar por post, até 8 em paralelo, com o prompt de `references/prompt-nota.md`; sem como abrir agente auxiliar, escrever em sequência. O agente auxiliar não mexe em `indice.md` nem no estado.
9. **Indexar.** `varredura.py indexar PASTA [PASTA ...]` com as pastas que ganharam nota. O script lê título, autor, data e tags da nota e põe no topo do índice sem duplicar.
10. **Fechar.** `varredura.py fechar <triagem.json> --falhas URN ...` (falhas e excedente do teto). Move o checkpoint para o início da coleta e marca o resto como visto, inclusive descartados e cards sem link. Pendente que falha 3 vezes sai da fila (`desistidos_apos_3_falhas`): dizer na entrega.
11. **Entregar** no formato abaixo.

## Formato da entrega

```
**Feed · 19/out 17:36 → 20/out 17:39** (2 cargas, 109 cards, 16 únicos na janela, 4 promovidos fora)

Estudados (6):
1. **<assunto>** · Autor · 20/out · <o achado da conferência em uma linha> → CONH/2026-10-20/<autor>-<id6>/conhecimento.md
...
Descartados (8): 3 política, 2 motivacional, 2 autopromoção, 1 vaga
Pendentes para a próxima (1): Autor (post restrito)
**Triagem:** CONH/varredura/2026-10-20-1739.md · próximo checkpoint: 20/out 17:39
```

Fechar lembrando em uma linha que o conteúdo é dos autores: citar com crédito.

## Falhas

| Sinal | Significa | Próximo passo |
|-------|-----------|---------------|
| `erro: fora do feed ou deslogado` | Sessão caiu ou outra página | Pedir login no navegador embutido |
| `erro: viewport 0` | Painel escondido sem tamanho | `resize_window` 1280x900, recarregar, colar de novo |
| `carga esgotada` com menos de 20 cards | Painel escondido não renderizou: o scroll infinito nem começou | `browser_batch`: screenshot (scale 0.1), `computer scroll` para baixo, espera de 3 s; depois `feedVarrer` de novo |
| `sem_link` na triagem | Card sem URN (grupo, "parabenizou") | Só entra se o texto valer; abrir o post pelo autor no navegador e ler a URL. Senão, descartar com motivo |
| `baixar_post.py` → `login` / `sem_conteudo` | Post restrito a conexões | `--falhas`; dizer na entrega |
| Muitos `ja_vistos` e nenhum candidato | Rodada logo depois da anterior | Entregar "nada novo desde HH:MM" e fechar |

## Referências

- `scripts/feed_varrer.js`: coletor do feed (só leitura), uma carga por página.
- `scripts/varredura.py`: janela, triagem com junção de cargas, checkpoint com pendentes e índice.
- `references/prompt-nota.md`: prompt do agente auxiliar que escreve uma nota.
- `references/feed.md`: o que se descobriu sobre o feed (scroll, painel escondido, URN, cargas) e por que o coletor é assim.
- `references/teste-aderencia.md`: cenário vermelho e o que cada regra fecha.

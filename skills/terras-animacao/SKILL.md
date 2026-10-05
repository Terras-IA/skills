---
name: terras-animacao
description: "Produz peça animada em loop a partir de uma cena HTML dirigida por tempo: o HTML determinístico (contrato ?t=), o render quadro a quadro no Chrome headless e a montagem do GIF (loop, para o feed) e do MP4 (silencioso), com capa estática e preview de celular. Use quando o pedido for animação, gif animado, vídeo curto sem narração, banner animado, diagrama que se desenha, peça em movimento, ou quando a peça pedir mais vida que o estático. Não é para banner estático (terras-banner), vídeo narrado (terras-video), edição e conversão de vídeo (terras-ffmpeg) nem página de explicação técnica (terras-visual-explainer)."
keywords: [animacao, animado, gif, gif animado, loop, video curto, mp4, movimento, motion, banner animado, peca animada, diagrama animado, bpmn animado, quadro a quadro]
version: 1.0.0
license: MIT
---

# Animação de peça (cena HTML dirigida por tempo)

## Onde está instalada

Fonte única: `skills/terras-animacao/` no repositório `terrasia-skills`. Cada agente enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh`; a edição se faz aqui e vale para todos. Abaixo, `$SKILL_DIR` é a pasta desta skill.

## O que entrega (e o que não é)

Uma peça animada de 5 a 8 segundos em loop: GIF (o feed autoplaya e loopa) e MP4 silencioso com a mesma cena, mais a capa estática e o preview de celular. A cena é **uma página HTML determinística**: o JS lê `?t=<ms>` e o `render(t)` desenha o frame daquele instante; nada depende de relógio real, então o mesmo `t` rende sempre o mesmo quadro e o GIF sai estável.

| Assunto | Skill |
| --- | --- |
| Banner e imagem estática | `terras-banner` |
| Vídeo narrado (YouTube/Shorts, voz neural, cartelas) | `terras-video` |
| Editar ou converter vídeo e áudio (corte, legenda, loudness) | `terras-ffmpeg` |
| Página que explica sistema ou código, com diagrama animado técnico | `terras-visual-explainer` |
| **Esta skill** | Peça animada de marca e feed: gif em loop + mp4, determinística, com aceite de leitura no celular |

Para peça da **empresa**, a identidade é a do produto (`terrasia-site/identidade/`); para o canal pessoal, a marca pessoal (`~/Documents/Diversos/terras-brand/`). Os tokens principais estão abaixo.

## Pipeline

1. **Cena HTML.** Parta do `templates/anim-base.html` (helpers prontos: `prog`, `pop`, `seta`, `formigas`). Escreva a cena e a linha do tempo no fim do `<script>`: cada elemento tem o instante em que aparece e o `render(t)` desenha o frame.
2. **Iterar por quadro.** Antes de animar, capture instantes-chave e olhe:

   ```bash
   python3 "$SKILL_DIR/scripts/render-anim.py" quadro peca.html 2400 q2400.png
   ```

3. **Animar.** A linha do tempo inteira, com mp4, gif e capa:

   ```bash
   python3 "$SKILL_DIR/scripts/render-anim.py" animar peca.html --saida peca --tamanho 1200x628 --duracao 6400 --fps 25 --capa 5600
   ```

4. **Aceite.** O juiz visual não assiste movimento: a inspeção é por **quadros-chave** (início, meio, fim e os beats de cada elemento), pelo **preview de celular** (o teste de verdade do feed) e pela medição de vãos quando houver risco de colisão:

   ```bash
   python3 "$SKILL_DIR/scripts/render-anim.py" bandas <png>@2x.png --regiao x0,x1,y0,y1
   ```

## Regras aprendidas (cada uma custou uma rodada)

- **Determinismo é a base.** Nada de relógio real, `requestAnimationFrame` ou transição CSS por tempo: tudo sai de `t`. O Chrome roda com `--virtual-time-budget` e o quadro é reprodutível.
- **Render em 2x e reduzir** (o script já faz): texto em 1x sai serrilhado no gif. E `--disable-lcd-text` é obrigatório no Linux (sem a flag, o texto ganha franja de subcor).
- **Ritmo:** 5 a 8 s de loop; 25 fps no mp4 e 14 no gif; o desenho leva cerca de 40% do tempo e o resto é leitura (segure o estado final 2 a 3 s). O loop é corte seco: a cena redesenha do zero, e isso é parte do charme.
- **Tamanho:** gif de feed até uns 5 MB (6,4 s em 1200x628 deu 1,4 MB com `palettegen` de 160 cores e dither bayer). Passou disso: baixe o fps do gif antes de baixar a largura.
- **Mobile manda:** menos elementos, tipo grande, contraste alto; o preview na largura do celular (356 px para 1200x628) é o aceite. Rótulo pequeno só sobrevive em tela cheia; conte com o movimento e a manchete.
- **Identidade:** ciano chapado (sem gradiente e sem glow), cantos retos, muito espaço negativo. Cores semânticas do sistema (`#f0e000` para aviso, `#ff2a2a` para erro) entram **só com significado** — no exemplo aprovado, a espera e o "jeitinho".
- **Tema de processo** (fluxograma, BPMN): seguir a notação de `terras-mapeamento-de-processos` (`references/notacao-bpmn.md`): evento de início e fim, tarefa, gateway, espera, loop de retrabalho. O exemplo aprovado é `exemplos/anim-mapeamento.html`.
- **Acessibilidade:** a peça animada precisa de alt text que descreva a cena e o que ela mostra; o post carrega esse texto.

## Tokens (identidade do produto)

| Papel | HEX |
| --- | --- |
| base | `#060a12` |
| acento | `#22d3ee` |
| texto | `#e8edf2` |
| apoio | `#94a3b8` |
| linha | `#1a2433` |
| aviso / erro (semânticas do sistema) | `#f0e000` / `#ff2a2a` |

Fontes: Ubuntu Sans (títulos) e JetBrains Mono (rótulos, woff2 em `~/Documents/Diversos/terras-brand/fonts/`); logo em `terrasia-site/identidade/ativos/logo-claro.png`.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Animação presa ao relógio real | tudo em função de `t`; o mesmo `t` desenha o mesmo quadro |
| Texto serrilhado ou com franja de cor | render em 2x, reduzir com PIL e `--disable-lcd-text` |
| Gif pesado demais | `palettegen`/`paletteuse` com 128 a 160 cores; baixar o fps do gif |
| Elemento pequeno demais no feed | menos elementos e tipo maior; o aceite é o preview de celular |
| Fim corrido, sem tempo de leitura | segurar o estado final 2 a 3 s antes do corte |
| Gradiente ou glow na peça | ciano chapado; gradiente não é da marca |
| Colisão de textos | medir com `bandas` antes de fechar |

## Arquivos

- `templates/anim-base.html` — esqueleto da cena com os helpers e a estrutura (cabeçalho, manchete, palco, legenda, assinatura).
- `scripts/render-anim.py` — `quadro` (um frame), `animar` (linha do tempo: mp4 + gif + capa) e `bandas` (vãos entre textos).
- `exemplos/anim-mapeamento.html` — o exemplo aprovado: BPMN de mapeamento de processos, peça da Company Page de 2026-10-05 (loop de 6,4 s, gif de 1,4 MB).

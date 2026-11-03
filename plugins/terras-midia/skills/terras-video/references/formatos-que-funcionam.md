# Formatos de vídeo curto que funcionam (e como recriar cada um)

Este guia vem da análise de 163 Reels salvos em 2026 (veja a skill `terras-analise-videos`). Ele serve para escolher o formato **antes** de escrever o roteiro. A contagem diz em quantos vídeos cada ferramenta apareceu na receita de recriação.

## Ferramentas mais citadas

| Ferramenta | Vídeos | Papel |
|---|---|---|
| CapCut | 119 | edição, legenda automática palavra a palavra, tela dividida, template |
| OBS | 34 | gravar tela + webcam em PiP |
| Microfone de lapela sem fio | 30 | o equipamento que mais melhora o resultado |
| Canva | 29 | cards estáticos, carrossel, capa |
| After Effects | 24 | motion graphics pago |
| Remotion / HyperFrames | 22 / 12 | motion graphics por código (HTML/React → MP4) |
| ElevenLabs | 20 | narração e voz clonada |
| Premiere / DaVinci Resolve | 17 / 4 | edição profissional (o DaVinci é grátis) |
| Kling / Veo / Runway / Seedance / Sora | 12 / 9 / 6 / 4 / 5 | vídeo generativo |
| HeyGen / Captions / Synthesia | 4+ | avatar e clone do apresentador |
| Manim / Three.js / Blender | 3 / 8 / 8 | animação matemática, partículas, 3D |

## Os 6 formatos e qual pipeline da casa serve

| Formato | Receita curta | Custo e tempo | Na casa |
|---|---|---|---|
| **1. Talking head com legenda palavra a palavra** (o mais comum) | celular no tripé, lapela, luz lateral; jump cuts, título fixo no topo, palavra-chave colorida | zero, 30–60 min | gravação do usuário + `terras-ffmpeg` (corte, legenda, 9:16) |
| **2. Demonstração de tela** | OBS com tela + webcam em PiP, zoom no trecho, tela dividida 9:16 (rosto em cima). **Não** filmar o monitor com o celular: o texto fica ilegível | zero, 1–2 h | `terras-ffmpeg` |
| **3. Motion graphics editorial por código** (o mais "premium") | roteiro de 150–230 palavras com fontes → narração → cenas HTML animadas → legenda via Whisper com marcação de tempo por palavra → 1080x1920. Visual: fundo escuro ou creme, barra de capítulos "01…05", fonte no rodapé, tipografia mono | 0–US$ 20/mês; 1–2 h com template | **`terras-video`** (shorts) e `terras-animacao` |
| **4. Animação de algoritmo ou matemática** | Python + NumPy + Manim, ou Canvas/Three.js; narração por cima | zero; 4–8 h na primeira, depois reaproveitável | `terras-animacao` |
| **5. Vídeo generativo com personagem consistente** | 15–25 imagens-chave com o mesmo personagem (Midjourney, Nano Banana ou GPT-image) → image-to-video (Veo, Kling, Seedance, Runway) → montagem com música livre → 60 fps opcional | US$ 30–100 em créditos, 1–2 dias | cena externa da `terras-video` |
| **6. Avatar ou clone do apresentador** | HeyGen Avatar IV ou Digital Twin, Captions ou Synthesia, com 2–5 min de vídeo-base e voz clonada; ou motion transfer (Runway Act-Two, Kling, Wan Animate local) | US$ 29–90/mês | fora da casa |

**Evitar:** corte de série, filme ou palestra de terceiros num canvas 9:16 com título. Dá alcance fácil, mas o risco de direito autoral e de derrubada do vídeo é alto.

## Regras de roteiro que saíram da análise

- **Gancho com número concreto e fonte citada na tela.** Foi o padrão dos vídeos com veredito "Verdadeiro".
- **A fala e a tela precisam mostrar o mesmo número.** Três vídeos perderam credibilidade por isso: "3 mil" contra 2.220, 600 mil contra 569 mil, R$ contra US$. Confira antes de renderizar.
- **IA se declara.** Vídeo generativo apresentado como filmagem real foi a principal fonte de "Enganoso" e "Falso". Avatar declarado não perdeu nada.
- **Isca de engajamento desgasta.** "Comenta PALAVRA", "só posto se bater mil curtidas", escassez falsa e gancho exagerado ("X killer", "fim do Y", "códigos secretos") apareceram justamente nos vídeos de veredito Misto ou Enganoso.
- **Série numerada e barra de capítulos seguram a atenção** sem precisar de isca.

## Kit mínimo por nível

| Nível | Kit | Custo |
|---|---|---|
| Começar | celular + tripé + lapela sem fio + CapCut + OBS | ~R$ 200–400 |
| Subir o nível | + DaVinci Resolve + ElevenLabs + template próprio de motion por código | ~US$ 5–22/mês |
| Generativo | + Nano Banana/Midjourney + Kling ou Veo (créditos) | ~US$ 30–100/projeto |
| Clone | + HeyGen ou Captions | ~US$ 29–90/mês |

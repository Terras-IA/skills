---
name: terras-motion-performance
description: "Audita e corrige animação que trava: layout thrashing, propriedade fora do compositor, scroll por JS, rAF sem fim, blur grande, will-change sobrando. Use quando animação engasga ou ao revisar CSS/JS de motion. Não cria peça animada (terras-animacao). Jank, motion perf."
keywords: [animação travando, jank, performance de animação, motion performance, layout thrashing, will-change, scroll-timeline, flip]
license: MIT
---

# Performance de animação

## Objetivo

Fazer a animação existente rodar liso sem mudar o que ela comunica nem a ferramenta que a produz. A correção troca a técnica pela mais barata que entrega a mesma intenção; não apaga movimento e não migra biblioteca.

## Regra dura

1. **Fique na ferramenta que já está lá.** Se o componente usa GSAP, a correção é em GSAP; se usa Motion, em Motion; se usa CSS, em CSS. "Era o único lugar que usava", "CSS puro é mais leve" e "simplifica" não justificam migrar. Sinal de que você migrou: a biblioteca ficou sem uso no `package.json`. Migrar só com pedido explícito, e nunca pela metade dentro do mesmo componente.
2. **Rebaixe a técnica antes de remover o movimento.** Animação de `width` vira `transform` (FLIP se o layout final importa); `left` em loop vira `translateX`; blur animado vira opacidade sobre blur fixo. Remover só quando o movimento for claramente bug, e então diga isso como achado separado e pergunte antes de apagar.
3. **Preserve o comportamento.** O painel que empurrava o conteúdo continua empurrando no estado final; troque *como* ele chega lá, não *onde* ele termina. Não troque animação por mudança instantânea.
4. **Não adicione animação nova.** O que entra além da correção é só guarda de `prefers-reduced-motion` sobre o que já existe.
5. **Escolha fora do padrão tem motivo escrito.** Se mantiver animação de paint ou layout, diga a restrição que justifica: superfície pequena, efeito único, duração, interação.

## Como trabalhar

### Modos

- **Revisão** (pedido de revisar, auditar, "por que trava"): reporte cada violação com `arquivo:linha`, o trecho exato, por que custa (uma frase) e a correção em código. Não edite.
- **Correção** (pedido de corrigir): aplique na ordem de prioridade abaixo e entregue a mesma lista com o que mudou.

Problema que não é de animação (design, acessibilidade, bug funcional) vai numa linha no fim, com a skill certa (`terras-auditoria-ui`, `terras-accessibility`), sem corrigir.

### Etapas de renderização

- **Composição**: `transform`, `opacity`. Barato.
- **Pintura**: cor, borda, gradiente, máscara, imagem, filtro.
- **Layout**: tamanho, posição, fluxo, grid, flex. Caro.

### Prioridade

| # | Categoria | Impacto |
|---|-----------|---------|
| 1 | Padrões proibidos e limite de ferramenta | crítico |
| 2 | Escolha do mecanismo | crítico |
| 3 | Medição | alto |
| 4 | Scroll | alto |
| 5 | Pintura | médio-alto |
| 6 | Camadas | médio |
| 7 | Blur e filtros | médio |
| 8 | View transitions | baixo |

**1. Proibidos.** Leitura e escrita de layout intercaladas no mesmo quadro. Layout animado continuamente em superfície grande. Animação dirigida por `scrollTop`, `scrollY` ou evento de scroll. Loop de `requestAnimationFrame` sem condição de parada e sem `cancelAnimationFrame` na desmontagem. Dois sistemas de animação medindo ou mexendo no mesmo elemento (ex.: `transition: width` no CSS + tween de `width` no JS).

**2. Mecanismo.** Padrão é `transform` + `opacity`. Animação por JS só quando a interação exige. Pintura ou layout só em elemento pequeno e isolado. Efeito único tolera mais que movimento contínuo.

**3. Medição.** Meça uma vez, anime por `transform`/`opacity`. Todas as leituras do DOM antes das escritas. Nada de ler layout a cada quadro. Para efeito que parece de layout, FLIP.

**4. Scroll.** Prefira Scroll/View Timeline (`animation-timeline: view()` ou `scroll()`) para movimento ligado ao scroll; em GSAP, ScrollTrigger. `IntersectionObserver` para visibilidade e pausa. Throttle por rAF num listener de scroll ainda é scroll por JS: não conta como correção. Pause o que sai da tela.

**5. Pintura.** Propriedade de pintura animada só em elemento pequeno. Não anime variável CSS que alimenta `transform`, `opacity` ou posição, nem variável herdada; escopo local.

**6. Camadas.** `will-change` temporário e cirúrgico: liga antes, desliga depois. Permanente em lista de cards que nem animam é custo sem ganho. Evite muitas camadas grandes promovidas.

**7. Blur.** Blur animado pequeno (até 8px), curto e único. Nunca contínuo, nunca em superfície grande; `backdrop-filter` em tela cheia anima por opacidade sobre blur fixo.

**8. View transitions.** Só para mudança de navegação; não em UI de interação intensa nem quando precisa interromper ou cancelar.

## Revisão

- Críticos primeiro (proibidos e limite de ferramenta).
- Escolha o menor trabalho de renderização que mantém a intenção.
- Notas acionáveis com alternativa concreta, não teoria.
- Sem medir no aparelho, diga que não mediu; não afirme "agora roda a 60 fps".

## Referências

- `references/correcoes.md` — antes/depois das correções comuns (width → transform, scroll → view timeline, FLIP, rAF com parada, GSAP sem migrar).
- `references/LICENSE-ui-skills.txt` — licença MIT do upstream.

## Fonte

Adaptada da skill `fixing-motion-performance` do repositório [ibelick/ui-skills](https://github.com/ibelick/ui-skills/tree/59193a7/skills/fixing-motion-performance) (MIT, © 2026 Julien Thibeaut; commit `59193a7`, de 25/10/2026). Mudanças da casa: português, modos revisão e correção separados, e regras 2 a 4 da regra dura, escritas a partir de um teste sem a skill em que o agente migrou GSAP para CSS, apagou o movimento e trocou animação por mudança instantânea.

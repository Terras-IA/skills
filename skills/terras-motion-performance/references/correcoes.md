# Correções comuns

## width animada → transform

```css
/* antes: layout a cada quadro */
.painel { transition: width 0.3s; }

/* depois: composição */
.painel { transition: transform 0.3s ease-out; transform-origin: left; }
.painel:not(.aberto) { transform: scaleX(0); }
```

Se o painel precisa empurrar o conteúdo no estado final, use FLIP: o layout muda uma vez e o movimento até lá é `transform`.

## Mesma correção sem sair do GSAP

```js
// antes: tween de layout
gsap.to(el, { width: aberto ? 420 : 0, duration: 0.3 });

// depois: FLIP com o plugin Flip do próprio GSAP
import { Flip } from "gsap/Flip";
gsap.registerPlugin(Flip);
const estado = Flip.getState(el);
el.classList.toggle("aberto", aberto);   // muda o layout uma vez
Flip.from(estado, { duration: 0.3, ease: "power2.out" });
```

E tire a `transition: width` do CSS: dois sistemas na mesma propriedade brigam.

## Scroll por JS → view timeline

```js
// antes
window.addEventListener("scroll", () => (el.style.opacity = scrollY / 500));
```

```css
/* depois */
.revela { animation: aparece linear both; animation-timeline: view(); animation-range: entry 0% cover 40%; }
@keyframes aparece { from { opacity: 0; } to { opacity: 1; } }
```

Num projeto com GSAP, o equivalente é `ScrollTrigger` com `scrub`, não o listener.

## Leitura e escrita intercaladas → FLIP

```js
// antes: thrash
el.style.left = el.getBoundingClientRect().left + 10 + "px";

// depois: mede uma vez, anima por transform
const primeiro = el.getBoundingClientRect();
el.classList.add("movido");
const ultimo = el.getBoundingClientRect();
el.style.transform = `translateX(${primeiro.left - ultimo.left}px)`;
requestAnimationFrame(() => {
  el.style.transition = "transform 0.3s";
  el.style.transform = "";
});
```

## Loop de rAF com parada

```js
useEffect(() => {
  let id;
  const largura = ref.current.getBoundingClientRect().width; // lê uma vez, fora do loop
  let x = 0;
  const quadro = () => {
    x = (x + 1) % largura;
    ref.current.style.transform = `translateX(${x}px)`;      // só escreve
    id = requestAnimationFrame(quadro);
  };
  id = requestAnimationFrame(quadro);
  return () => cancelAnimationFrame(id);
}, []);
```

Movimento contínuo que sai da tela: pause com `IntersectionObserver`.

## Blur de tela cheia

```css
/* antes: refaz o blur a cada quadro */
.fundo { transition: backdrop-filter 0.6s; backdrop-filter: blur(0); }
.fundo.ligado { backdrop-filter: blur(24px); }

/* depois: blur fixo, anima só a opacidade */
.fundo { backdrop-filter: blur(24px); opacity: 0; transition: opacity 0.3s; pointer-events: none; }
.fundo.ligado { opacity: 1; pointer-events: auto; }
```

## will-change

```css
/* antes: camada permanente em tudo */
.card { will-change: transform; }

/* depois: só durante a interação que anima */
.card:hover, .card:focus-within { will-change: transform; }
```

## Movimento reduzido

```css
@media (prefers-reduced-motion: reduce) {
  .painel, .fundo { transition: none; animation: none; }
}
```

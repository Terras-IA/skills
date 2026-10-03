# Estilo: páginas, componentes e personagens SVG

Página: HTML de exatamente **1200×1800 px** (o render usa escala 2× → PNG 2400×3600).
Fonte: `Baloo2.ttf` (variável 400–800) copiada para a pasta `paginas/` do livro.
**Regra de ouro:** o desenho (SVG) fica no fundo; TODO texto (narração, balões, título)
é HTML sobreposto — nunca desenhe texto dentro do SVG.

## Esqueleto de página de cena

```html
<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><link rel="stylesheet" href="livro.css">
</head><body>
  <div class="cena"><svg viewBox="0 0 1200 1800">…arte da página…</svg></div>
  <div class="badge">1</div>
  <div class="narra">Sofia era uma menina de 8 anos muito alegre.</div>
  <div class="balao" style="top:520px;left:640px;width:360px">Quer brincar comigo?</div>
</body></html>
```

Modo assistido: troque o SVG por `<img class="fundo" src="../imagens/pagina-01.png">`.

## livro.css (copie por livro; ajuste as 5 cores da paleta)

```css
@font-face{font-family:'Baloo2';src:url('Baloo2.ttf');font-weight:400 800}
*{margin:0;box-sizing:border-box}
body{position:relative;width:1200px;height:1800px;overflow:hidden;
  font-family:'Baloo2',sans-serif;background:#FDE7EF}
.cena,.cena svg,.fundo{position:absolute;inset:0;width:100%;height:100%}
.badge{position:absolute;top:36px;left:36px;width:96px;height:96px;border-radius:50%;
  background:#F06292;color:#fff;font-weight:800;font-size:54px;z-index:9;
  display:flex;align-items:center;justify-content:center;
  border:5px dashed #fff;box-shadow:0 5px 0 rgba(93,64,55,.25)}
.narra{position:absolute;top:64px;left:120px;width:960px;z-index:8;text-align:center;
  background:#FFF9E8;border:6px dashed #F48FB1;border-radius:60px;
  padding:36px 46px;font-size:42px;font-weight:600;line-height:1.32;color:#5D4037;
  box-shadow:0 6px 0 rgba(93,64,55,.12)}
.balao{position:absolute;z-index:8;background:#fff;border:6px solid #4E342E;
  border-radius:36px;padding:22px 30px;font-size:38px;font-weight:700;line-height:1.25;
  color:#4E342E;text-align:center}
.balao::before,.balao::after{content:'';position:absolute;width:0;height:0}
/* rabinho apontando para baixo-esquerda (inverta com right/left) */
.balao.dbaixa::before{left:48px;bottom:-30px;border:16px solid transparent;
  border-top:26px solid #4E342E;border-bottom:0}
.balao.dbaixa::after{left:54px;bottom:-18px;border:11px solid transparent;
  border-top:19px solid #fff;border-bottom:0}
.pensamento{position:absolute;border-radius:50%;background:#FFF9E8;border:5px solid #B39DDB;
  box-shadow:0 6px 0 rgba(93,64,55,.12);display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;
  font-weight:700;color:#5D4037;padding:20px 40px}
.titulo{position:absolute;top:64px;width:100%;text-align:center;z-index:9;line-height:.98}
.titulo .l1{font-size:112px;font-weight:800;color:#FFF6DC;
  -webkit-text-stroke:16px #3E2A6B;paint-order:stroke;
  text-shadow:0 8px 0 rgba(0,0,0,.28)}
.titulo .l2{font-size:132px;font-weight:800;color:#F06292;
  -webkit-text-stroke:16px #fff;paint-order:stroke;
  text-shadow:0 8px 0 rgba(62,42,107,.45)}
.swoosh{position:absolute;z-index:9}
```

Capa: `.titulo` com `.l1` (linha 1, creme) e `.l2` (linha 2, rosa) + um SVG `.swoosh`
(risco amarelo curvo + estrelinha ✦) sob o título.

## Personagens: sistema de camadas

Desenhe sempre na mesma ordem, reaproveitando os MESMOS valores da ficha:
`cabelo-trás → corpo/roupa → cabeça (pele) → franja/cabelo-frente → orelhas → rosto → acessório`.
Trabalhe dentro de `<g transform="translate(x,y) scale(s)">` para posicionar/escalar.

### Biblioteca de snippets (unidade = "unidade de cabeça" ≈ raio 90)

```svg
<!-- CABEÇA de frente (pele P, Trostos do livro) -->
<ellipse cx="0" cy="0" rx="92" ry="96" fill="PELE"/>
<!-- Olhos abertos grandes (variante menina, com cílios) -->
<g fill="#3E2723">
  <ellipse cx="-34" cy="-6" rx="15" ry="19"/><ellipse cx="34" cy="-6" rx="15" ry="19"/>
</g>
<circle cx="-29" cy="-13" r="5.5" fill="#fff"/><circle cx="39" cy="-13" r="5.5" fill="#fff"/>
<path d="M-52,-30 q18,-12 36,-2" stroke="#3E2723" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M52,-30 q-18,-12 -36,-2" stroke="#3E2723" stroke-width="5" fill="none" stroke-linecap="round"/>
<!-- Olhos fechados (orando/contentes): arcos para baixo -->
<path d="M-48,-4 q14,14 30,0 M18,-4 q14,14 30,0" stroke="#3E2723" stroke-width="6"
  fill="none" stroke-linecap="round"/>
<!-- Bochechas + sorriso -->
<ellipse cx="-56" cy="26" rx="16" ry="11" fill="#F8A8B8" opacity=".55"/>
<ellipse cx="56" cy="26" rx="16" ry="11" fill="#F8A8B8" opacity=".55"/>
<path d="M-18,38 q18,16 36,0" stroke="#B5654D" stroke-width="6" fill="none" stroke-linecap="round"/>
<!-- Tristeza: sobrancelhas inclinadas + boca curva para baixo -->
<path d="M-20,52 q18,-14 36,0" stroke="#B5654D" stroke-width="6" fill="none" stroke-linecap="round"/>
<!-- Surpresa: olhos rx=17 e boca <ellipse cy="44" rx="13" ry="17" fill="#8D5524"/> -->
<!-- Corpo criança (roupa R): tronco + pernas + mãos -->
<path d="M-70,80 Q0,58 70,80 L62,230 Q0,246 -62,230 Z" fill="ROUPA"/>
<rect x="-52" y="228" width="38" height="96" rx="17" fill="ROUPA"/>
<rect x="14" y="228" width="38" height="96" rx="17" fill="ROUPA"/>
<circle cx="-84" cy="150" r="20" fill="PELE"/><circle cx="84" cy="150" r="20" fill="PELE"/>
```

### Assinaturas dos personagens-tipo (varie pela ficha, mantenha o sistema)

- **Menina protagonista:** cabelo-trás = 3 elipses grandes atrás da cabeça (ondas até os
  ombros) + franja frontal em arco com bico central; acessório = laço (dois triângulos
  arredondados + nó) de um lado da cabeça.
- **Menino:** cabelo = calota (path arco sobre o topo) + 3 picos de franja; sem cílios.
- **Adulto:** cabeça menor em relação ao corpo (escala 0.85) + corpo mais alto; coque =
  círculo extra no topo; brincos = 2 circulozinhos dourados.
- **Plush/ovelha:** nuvem (4 círculos brancos) + cabeça escura + olhinhos pretos.

### Cenários-relâmpago (formas grandes e planas, 3–6 elementos)

- **Quarto dia:** parede lilás `#F3E5F5`, rodapé, janela com sol amarelo e cortina,
  cama (retângulo arredondado + travesseiro), tapete oval.
- **Quarto noite:** parede `#2E3A6E`, janela com lua e estrelas, luminária com halo
  (círculos concêntricos amarelos, opacity 0.15/0.25).
- **Sala de aula:** parede creme, lousa verde com moldura madeira, carteiras = par de
  retângulos (tampo marrom + pés), fileiras em perspectiva simples (mais altas atrás).
- **Recreio:** céu `#B3E5FC` com nuvens (3 círculos), chão verde `#AED581`, árvore =
  copa (3 círculos `#81C784`) + tronco.
- **Halos de luz** (presença de Deus/alegria): 2 círculos amarelos translúcidos + raios
  curtos ou estrelinhas ✦ de 4 pontas (losango alongado).

## Composição

- Personagens ocupam 45–60% da altura da página; nada importante nos 60 px de borda.
- Narração sempre no topo (badge à esquerda); balões na metade de cima/média, perto do
  personagem que fala, rabinho apontando para a boca. Nunca sobre o rosto de ninguém.
- 1 cena = 1 ideia = 1 emoção. Close na emoção (rosto maior) nas páginas-pivo.
- Contraste: se o fundo é claro, balões brancos ganham sombra `.12`; se escuro, use
  `.narra`/`.balao` normalmente e escureça o contorno para `#3E2723`.
- A mesma cena vira a arte do livro de colorir (`colorir.py` extrai os contornos), então
  prefira formas grandes com bordas de cor bem definidas; evite gradientes suaves e
  detalhes miúdos que virariam ruído em linha.

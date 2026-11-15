# Cola de Strudel para recriações

Os exemplos de código abaixo foram tocados no strudel.cc em 2026-11. O que vem marcado "(não testado)" é da documentação e deve ser conferido na aba **reference** ou **sounds** antes de usar.

## Andamento

`setcps(BPM/60/4)` faz 1 ciclo valer 1 compasso 4/4. Com 16 passos no mini-notation, cada passo é uma semicolcheia.

## Bateria

```js
s("bd ~ ~ ~ ~ ~ ~ bd bd ~ ~ ~ ~ ~ ~ ~").bank("RolandTR909")   // bumbo
s("~ ~ ~ ~ sd ~ ~ ~ ~ ~ ~ ~ sd ~ ~ ~").bank("RolandTR909")   // caixa no 2 e no 4
s("hh*8").gain("0.3 0.5").bank("RolandTR909")               // chimbal em colcheias
s("~ oh ~ oh").gain(0.5)                                     // aberto, banco padrão
```

Os bancos e nomes que existem estão na aba **sounds** do painel lateral. `cp`, `oh`, `bd`, `sd` e `hh` existem no RolandTR909 e no banco padrão.

## Harmonia

```js
const acordes = "<F# F# B D#m B G#m F# C#>"       // 1 acorde por compasso
const acordes2 = "<D [G Em] G D>"                 // [ ] divide o compasso
chord(acordes).voicing().s("gm_epiano1")          // voicing automático
note("<f#1 b1 d#2 c#2>").s("sawtooth").lpf(400)   // baixo na fundamental
```

- Os nomes dos acordes usam sustenido (`D#m`, `G#m`). Tríades maiores e menores foram testadas. Sufixos como `7`, `^7` e `sus4` não foram testados.
- Nas notas, use minúsculas com oitava: `f#1`, `eb2`.

## Melodia original na escala

```js
n("<[0 2 4 ~] [4 ~ 2 0]>").scale("F#4:major:pentatonic").s("triangle").delay(0.3)
```

Os graus contam a partir de 0. A escala testada foi `major:pentatonic`. Outras como `minor`, `minor:pentatonic` e `dorian` não foram testadas.

## Timbres

- Testados: `sawtooth`, `triangle`, `gm_epiano1` (soundfont General MIDI, que carrega com um pequeno atraso na primeira vez).
- Não testados: `square`, `sine` e outros `gm_*`. Confira o nome na aba **sounds**.

## Efeitos

`.lpf(hz)`, `.room(0..1)`, `.delay(0..1)`, `.attack(s)`, `.release(s)`, `.gain(0..1)`.

## Inverter

`.rev()` inverte o padrão dentro de cada ciclo. Serve para tocar "ao contrário".

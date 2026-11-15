# Estrutura do projeto de músicas

```
<projeto>/
  README.md                  fluxo, regras e tabela das músicas
  .gitignore                 musicas/*/audio/  __pycache__/  .venv/
  musicas/<slug>/
    README.md                referência e achados (modelo abaixo)
    strudel.js               código pronto para colar no strudel.cc
    dados/analise.json       saída completa de analisar.py
    dados/acordes.csv        compasso, início, acorde, baixo, confiança
    audio/<slug>.m4a         áudio baixado (fora do git)
```

Tabela do README da raiz:

```markdown
| Pasta | Música | Tom | BPM |
|---|---|---|---|
| `musicas/<slug>` | <Título> (<Artista>) | <tom> | <bpm adotado> (<half-time?>) |
```

# Modelo do README de cada música

```markdown
# <Título> (<Artista>)

## Referência

| Campo | Valor |
|---|---|
| Título | <título exato do vídeo> |
| Canal | <canal> |
| Link | <url sem parâmetros de rastreio> |
| Duração | <m:ss> |
| Áudio analisado | `audio/<arquivo>`, formato <id> do YouTube (<ext>, <kbps>, <MB>), baixado em <AAAA-MM-DD> |
| Direitos | Obra protegida: o áudio fica só local (fora do git), para análise. / Domínio público. |

## O que a análise encontrou (`dados/analise.json`, `dados/acordes.csv`)

- **Tom:** <tom> (correlação <x>). Segundo candidato: <...>.
- **Andamento:** <medido> BPM medidos → **<adotado> BPM** <motivo: grade da caixa, estilo>. Conferir ouvindo.
- **Campo harmônico:** <acordes com grau>.
- **Progressões por trecho:** <tempo – progressão (graus)>.
- **Forma por energia:** <trechos baixa/média/alta com tempos>.

## Recriação (`strudel.js`)

- <ciclo de N compassos e o que cada parte é>
- <bateria, timbres>
- **Melodia original** em <escala>; a linha vocal não foi transcrita. (Ou: transcrita, porque a obra é de domínio público.)

Para tocar: abra https://strudel.cc, cole `strudel.js` e pressione Ctrl+Enter.

## Limites e confiança

- Os acordes saem de modelos maior/menor: não detectam sétimas, sus nem inversões.
- <BPM dobrado ou não>
- As seções são separadas por energia, e os rótulos são interpretação.
```

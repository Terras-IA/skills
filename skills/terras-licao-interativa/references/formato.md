# Formato do curso.json

Um arquivo JSON descreve o curso inteiro. O motor (`motor/cena.js`) só interpreta; nada de código por lição.
Exemplo completo e funcionando: `exemplos/system-design.json`.

## Curso

```json
{
  "id": "slug-do-curso",          // chave do progresso salvo no navegador
  "titulo": "Nome do curso",
  "idioma": "pt-BR",              // "pt-BR" ou "en": muda os textos da interface
  "modulos": [ { "titulo": "Escala", "cor": "laranja", "licoes": [ ... ] } ]
}
```

## Lição

| Campo | Obrigatório | O que é |
|-------|-------------|---------|
| `id` | sim | slug com letras minúsculas, dígitos e hífen (vira a âncora `#<id>-p<passo>`) |
| `titulo`, `resumo` | título sim | cabeçalho da lição |
| `nivel`, `minutos` | não | chips do cabeçalho |
| `metricas` | não | `[{id, rotulo, valor}]`: placas do topo, `valor` é o inicial |
| `legenda` | não | `[{cor, texto, forma?}]`; `cor` é um tom ou CSS (`var(--req)`, `var(--resp)`, `var(--falha)`, `var(--pesado)`); `forma: "quadrado"` |
| `objetivos` | não | `[{texto, passo}]`: o item fica marcado a partir daquele passo (1 = primeiro) |
| `cena` | sim | `{nos: [...], ligacoes: [...]}`: estado antes do passo 1 |
| `passos` | sim | lista de passos (2 ou mais; o bom é 6 a 12) |

## Nó

Coordenadas em **unidades de grade isométrica**: `x` cresce para baixo-direita, `y` para baixo-esquerda. Uma caixa ocupa ~1 unidade; deixe **2 unidades** entre caixas vizinhas (menos que isso encavala os selos).

| Campo | Valores |
|-------|---------|
| `id` | único na lição |
| `tipo` | `caixa` (serviço, pessoa-papel, etapa), `banco` (cilindro: dados, arquivo, estoque), `pessoas` (multidão numa plataforma), `fila` (blocos enfileirados: fila, log, lotes), `zona` (área tracejada no chão: rede, departamento, região), `rotulo` (etiqueta solta), `placa` (cartão plano com título e linhas: tabela de alçada, checklist, regra, contrato entre serviços) |
| `x`, `y`, `z` | posição; `z` em px eleva o nó |
| `rotulo` | texto. `caixa`: no topo (até ~22 caracteres, quebra em 2 linhas). `banco`: pílula à direita (até ~16). `pessoas` e `fila`: pílula embaixo/acima. `placa`: título |
| `linhas` | `placa`: até 6 linhas de texto (`["até R$ 5 mil → gestor", "acima → diretor"]`) |
| `icone` | um emoji ou símbolo (🖥 💳 📦 ⑂ 🔒 👤) |
| `tom` | em `pessoas`, pinta todas as figuras do mesmo tom (ex.: `vermelho` para golpista ou atacante). Valores: `azul`, `verde`, `laranja`, `roxo`, `rosa`, `amarelo`, `cinza`, `vermelho`, `teal` |
| `tamanho`, `altura` | escala (1 = padrão) e altura em px da caixa |
| `estado` | `normal`, `caido` (cinza, X e selo FORA), `quente` (vermelho pulsando: sobrecarga), `fantasma` (translúcido: planejado, reserva) |
| `carga` | 0 a 100: medidor acima do nó (verde < 60, âmbar < 85, vermelho) |
| `selo` | texto curto acima do nó ("23 na fila", "round robin"), até ~18 caracteres; detalhe vai numa `placa` |
| `estilo` | `selo` e `rotulo`: `alerta` (vermelho) ou `bom` (verde) |
| `quantidade` | `pessoas`: figuras (1 a 36); `fila`: blocos (1 a 14) |
| `direcao`, `espaco` | `fila`: `"x"` (padrão) ou `"y"`; `espaco` entre blocos em unidades (padrão 0,6) |
| `largura`, `fundo` | `zona`: tamanho em unidades |
| `oculto` | `true`: existe mas não aparece. Declare na `cena` todo nó que vai surgir depois, oculto, e revele com `{"oculto": false}`: assim a câmera não pula |

## Ligação

```json
{ "de": "lb", "para": "a", "rota": "y", "fluxo": 1.2, "falha": 0.1, "falhaEm": 0.6, "pesados": 0.3,
  "sentido": "ida", "tracejada": false, "rotulo": "HTTPS", "posRotulo": 0.5, "estilo": "alerta",
  "cor": "roxo", "velocidade": 1 }
```

- `rota`: `"x"` (padrão: anda em x, depois y), `"y"` (y primeiro), `"reta"`. Para leque saindo de um nó (um para vários), use `"y"` nos ramos laterais.
- `fluxo`: densidade de pacotes (0 = linha parada, 1 = normal, 3 = muito tráfego).
- `falha`: fração de pacotes vermelhos. `falhaEm` (0 a 1, padrão 0,6) é onde somem no trajeto: perto de 1 = barrados na chegada (conferência que recusa); `1` = chegam ao destino vermelhos (golpe que passou). `pesados`: fração de pacotes quadrados laranja.
- `posRotulo` (0 a 1): onde fica a pílula do `rotulo` no caminho. `estilo`: `alerta` ou `bom` na pílula.
- `cor`: só nomes de tom (a `legenda` aceita CSS livre).
- `sentido`: `ida`, `volta` (verde, resposta) ou `ambos`.

## Passo

```json
{
  "rotulo": "Add LB",               // até 14 caracteres: aparece na linha do tempo
  "tipo": "solucao",                // contexto | problema | solucao | tecnica | troca | resumo
  "titulo": "Uma porta da frente",
  "texto": "Parágrafos separados por linha em branco. **negrito** e `código`.",
  "ideia": "Caixa roxa de ideia-chave (opcional).",
  "mudou": ["+ ganho", "- perda", "· neutro"],
  "nos": { "lb": { "oculto": false }, "b": { "carga": 97, "estado": "quente" }, "velho": null },
  "ligacoes": [ ... ],              // se presente, SUBSTITUI a lista inteira
  "metricas": { "p95": { "valor": "1,2 s", "tom": "ruim" }, "erros": "0%" },
  "quiz": { "pergunta": "...", "opcoes": ["A", "B", "C"], "certa": 1, "porque": "..." }
}
```

- `nos` é **remendo**: só os campos que mudam. `null` no nó remove; `null` num campo (`"selo": null`) apaga o campo.
- Estado acumula: o passo 5 herda tudo do 4. Voltar recalcula do zero, então não há efeito colateral.
- Métrica com `tom` `ruim` fica vermelha, `bom` fica verde; texto puro fica neutro.
- `ligacoes` não é remendo: repita a lista completa quando algo nela mudar.

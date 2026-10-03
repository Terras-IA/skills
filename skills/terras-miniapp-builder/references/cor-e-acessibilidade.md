# Cor — escolher e dosar

Duas decisões separadas, e a segunda é a que quase todo mundo esquece:

1. **Escolher** matizes que combinem com a proposta (a leitura de psicologia das cores).
2. **Dosar** quanta área cada um ocupa na tela.

Uma paleta calma com o matiz mais estimulante ocupando a maior área visível produz um
app que **não** acalma. Já vimos isso acontecer: numa tela, 24,7% dos pixels eram cor
saturada e **98,3% dessa cor era vermelho/terracota**, enquanto o verde — o único matiz
realmente calmante do conjunto — respondia por 0,3%. A paleta estava certa; a dose,
invertida. Não invente cor nova para consertar isso: **redistribua área**.

## Escolher: o que cada família faz

Isto é orientação prática, não lei. Combine com a promessa do app.

| Família | Efeito típico | Onde costuma servir |
|---|---|---|
| Verde / sálvia | Baixa ativação, regulação, segurança | Repouso, leitura, confirmação, acolhimento |
| Areia, creme, papel | Neutro quente, sem fadiga, "caderno" | Fundo principal, superfície de leitura |
| Terracota / barro | Calor, presença, chão; em saturação alta vira alerta | Acento, chamada para ação, marca |
| Azul | Confiança, frieza, institucional | Ferramenta, finanças — cuidado com frieza em cuidado humano |
| Violeta / malva | Introspecção, intuição | Reflexão, conteúdo do "eu" |
| Vermelho vivo | Urgência | Só erro e destruição |
| Amarelo / dourado | Energia, recompensa | Conquista pontual, nunca área grande |

Para um app que precisa **acalmar** (cuidado, saúde, parentalidade, ansiedade):
fundo de papel quente, matiz frio-vegetal como superfície de apoio, e um quente de
barro só em acento.

Para um app que precisa **mover** (venda, produtividade): o quente pode ganhar área,
mas mantenha um neutro dominante para a leitura não cansar.

## Dosar: medir, não estimar

Depois de montar a tela, **meça**:

```bash
python3 scripts/contraste.py --captura tela.png
```

O script devolve a proporção de pixels com cor real e a distribuição por família de
matiz. Alvos práticos:

- **Cor saturada:** abaixo de ~10% da tela na maioria dos apps; mais que ~20% começa a
  competir com a leitura.
- **O matiz mais estimulante** não deveria ser o de maior área. Se é, troque a área:
  o bloco colorido vira cartão neutro com acento da cor.
- **O matiz que carrega a promessa** (o que acalma, o que dá confiança) precisa
  aparecer em área de leitura, não só em selo de confirmação.

Formas baratas de redistribuir, sem tocar na paleta:

1. Trocar o bloco de cor cheia por cartão neutro + acento (ícone, fio, botão).
2. Levar a cor de apoio para o fundo dos cartões de conteúdo (onde a pessoa lê).
3. Reservar o preenchimento saturado para uma única ação focal.

## Contraste — o mínimo, e por quê

Texto precisa de **4,5:1**; texto grande (≥24px, ou ≥19px em negrito) aceita **3:1**.
Elemento gráfico e limite de componente precisam de **3:1**. Marca e ícone decorativo
não têm mínimo legal, mas abaixo de ~2:1 somem na prática.

```bash
python3 scripts/contraste.py --texto "#1c1c18" --fundo "#fcf9f3"
python3 scripts/contraste.py --paleta paleta.json    # tabela cruzada de tudo
```

**Toda cor de marca precisa de variante por fundo.** Uma marca entregue em verde-sálvia
sobre fundo escuro deu 2,14:1 sobre o papel claro do app — praticamente invisível. A
regra que resolve, e que deve ficar escrita junto da marca:

> fundo escuro → cor clara da marca; fundo claro → variante escura ou o acento quente.

Gere as variantes com `scripts/marca.py` em vez de recortar na mão.

## Tema claro e escuro

**Claro é o padrão; escuro é escolha explícita.** Não siga o sistema automaticamente.
O motivo é prático: no escuro a identidade quase desaparece — superfícies, texto e
bordas andam poucos pontos de RGB entre uma paleta e outra, e a diferença fica só no
acento. Se o app abre escuro num aparelho escuro, a marca nova é indistinguível da
anterior.

Como implementar sem piscar na abertura:

1. CSS: o escuro por sistema exige um valor explícito (ex.: `:root[data-tema='sistema']`
   dentro do `@media (prefers-color-scheme: dark)`). **Sem atributo, vale o claro.**
2. Espelhe a escolha em `localStorage` e leia num script inline no `index.html`, antes
   do primeiro paint. Índice assíncrono (IndexedDB) chega tarde demais: quem escolheu
   escuro veria um flash claro.
3. Ajuste `theme-color` ao tema em vigor, e o `theme_color` do manifest ao fundo padrão.

O escuro precisa ser um tema **de verdade**, não o claro invertido: derive de tokens
inversos próprios e confira contraste de novo — texto claro sobre carvão erra fácil.

## Acessibilidade além da cor

- Não comunique estado **só** por cor (marque também com forma, ícone ou texto).
- Alvos de toque ≥44px. O público costuma usar o app cansado, com uma mão.
- Respeite `prefers-reduced-motion` se houver animação.
- Teste com leitor de tela: rótulos em botões de ícone, `aria-pressed` em escolhas.
- Foco visível, com anel de contraste suficiente sobre os dois temas.

## Checklist da fase

- [ ] Paleta escolhida com justificativa ligada à promessa (não a gosto)
- [ ] Área medida: matiz mais estimulante não é o de maior área
- [ ] Contraste de todo texto ≥4,5:1 (ou 3:1 se grande) nos dois temas
- [ ] Variante da marca por fundo gerada e regra escrita
- [ ] Claro como padrão, escuro explícito, sem flash na abertura
- [ ] `theme-color` e manifest coerentes com o fundo padrão
- [ ] Estado não comunicado só por cor

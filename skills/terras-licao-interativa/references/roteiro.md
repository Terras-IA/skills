# Como roteirizar uma lição

O desenho é a parte fácil. Lição boa vem do roteiro: cada passo muda **uma** coisa na cena e o texto explica por que ela mudou.

## Arco que funciona

1. **contexto**: o mundo funcionando no tamanho pequeno. Números bons.
2. **problema**: uma força cresce (volume, falha, prazo, fraude). Métrica fica vermelha, nó fica `quente` ou `caido`.
3. **solucao** ingênua ou incompleta, quando houver: mostra por que a resposta óbvia não basta.
4. **solucao** / **tecnica**: a peça nova entra (revelar nó oculto), as métricas voltam.
5. **problema** de segunda ordem: a solução tem um limite (pedidos desiguais, ponto único de falha, custo).
6. **troca**: o preço da escolha, dito com clareza.
7. **resumo** com `quiz`: uma pergunta de aplicação, não de memória.

6 a 12 passos. Menos que 5 vira slide; mais que 13 cansa: quebre em duas lições.

## Regras

- **Uma mudança visível por passo.** Se o texto fala de algo que a cena não mostra, falta um remendo em `nos`, `ligacoes` ou `metricas`.
- **Número coerente entre passos.** Se dobrou o tráfego, `rps`, `carga` e `fluxo` sobem juntos. O leitor confere.
- **Número de exemplo é ilustração.** Não apresente como benchmark. Dado real precisa de fonte no texto.
- **Texto curto.** 2 parágrafos, até ~500 caracteres. O resto vai em `ideia` ou no passo seguinte.
- **`mudou` resume a diferença** em 1 a 3 linhas com `+`/`-`.
- **Rótulo da linha do tempo** é verbo ou substantivo curto ("Pico", "Add LB", "Health check").
- **Objetivos** marcam o passo em que o leitor ganhou aquilo, não o último.

## Mapa de metáforas para outros assuntos

| Assunto | `caixa` | `banco` | `pessoas` | `fila` | `zona` | pacote |
|---------|---------|---------|-----------|--------|--------|--------|
| Sistemas | serviço, LB, API | banco, cache | usuários | fila, log | VPC, região | requisição |
| Processo de negócio (contas a pagar, RH) | etapa, papel, aprovador | ERP, planilha | fornecedores, candidatos | documentos esperando | departamento | documento |
| Atendimento / suporte | nível N1/N2, robô | base de conhecimento | clientes | tickets | horário/turno | chamado |
| Logística | centro, doca | estoque | clientes | caminhões, paletes | cidade | pedido |
| Segurança | firewall, serviço | cofre de segredos | atacantes vs usuários | tentativas | zona de confiança | pacote/login |
| Finanças pessoais / empresa | conta, investimento | reserva | pessoas | boletos | mês | dinheiro |
| Igreja / evento | equipe, ministério | inventário | membros, visitantes | escala | salão | pessoa/tarefa |

Ator mal-intencionado (golpista, atacante): `pessoas` com `quantidade: 1` e `tom: "vermelho"`, ligação com `falha: 1` e `falhaEm` perto de 1 quando um controle barra, ou `falhaEm: 1` quando o golpe passa. Regra, política ou tabela de faixas (alçada, SLA, checklist): `placa` ao lado da peça que aplica a regra, em vez de selo comprido.

`carga` serve para qualquer capacidade (% da agenda de um aprovador, ocupação de doca). `estado: caido` serve para pessoa de férias, sistema fora, fornecedor bloqueado.

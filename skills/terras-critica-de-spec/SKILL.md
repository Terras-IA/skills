---
name: terras-critica-de-spec
version: 1.0.0
access: free
category: desenvolvimento
description: Critica uma spec antes da implementação (critério de aceite que não dá para testar, caso de borda faltando, escopo ambíguo, contradição, regra do repositório violada) e conduz a revisão com o autor, inclusive a divergência entre spec e código.
keywords: [critica de spec, revisar spec, revisao de especificacao, criterio de aceite, casos de borda, escopo ambiguo, spec drift, refinar spec]
---

# Crítica e revisão de spec

## Objetivo

Achar as fraquezas de uma spec **antes** de alguém escrever código, e depois fechá-las com o autor. São dois modos:

- **Crítica:** lê a spec e devolve um veredito com os problemas encontrados. Somente leitura.
- **Revisão:** entrevista o autor sobre uma spec que já existe e edita o texto a partir das respostas. Não escreve spec do zero.

A meta é uma spec melhor, não uma spec bloqueada: proponha a reescrita sempre que der.

## Onde está instalada

Fonte única: `skills/terras-critica-de-spec/` no repositório `terrasia-skills`. Adaptada do speccraft (MIT, ver `NOTICE`).

## Modo crítica

### O que procurar

1. **Critério que não dá para testar.** Todo critério de aceite descreve comportamento observável (entrada → saída ou efeito). Aponte o que não pode ser verificado por teste ou observação direta. Critério que depende do texto que um modelo escolhe deve virar critério estrutural (formato, campo presente, código de status), não de conteúdo.
2. **Caso de borda faltando.** Para cada caminho feliz: o que acontece quando falha? E nos limites (vazio, duplicado, concorrente, repetido duas vezes, sem permissão, fora do ar)?
3. **Escopo ambíguo.** Duas pessoas implementariam isso de forma diferente? Então a spec precisa ser mais clara.
4. **Fora de escopo faltando.** Que funcionalidade vizinha alguém pode construir sem querer? Se não está listada como fora de escopo, pode entrar escondida num PR.
5. **Contradição** interna.
6. **Regra do repositório violada.** Compare a direção técnica com `CLAUDE.md`, `AGENTS.md`, ADRs e convenções do repositório. Aponte a spec que exigiria quebrar uma regra dura.

### Saída

```yaml
veredito: aprovar | aprovar-com-comentarios | pedir-mudancas | rejeitar
preocupacoes:
  - "<preocupação>"
sugestoes:
  - "<sugestão, de preferência com o texto reescrito>"
violacoes_de_regra:
  - regra: "<qual regra, com o arquivo onde ela está>"
    onde: "<seção da spec>"
```

Depois do bloco, uma discussão curta das preocupações mais importantes.

## Modo revisão

### Entradas

- A spec atual, já em disco.
- A **checagem de divergência**: liste os identificadores entre crases na spec (funções, arquivos, rotas, tabelas) e procure cada um no código das pastas que a spec toca. O que não aparece em lugar nenhum é item de divergência.

### Sequência da entrevista

1. **Divergências primeiro.** Para cada item, faça a pergunta numa linha que começa exatamente com `Q-DIVERGENCIA:` na coluna 0, e espere a resposta antes de seguir. Exemplo:
   ```
   Q-DIVERGENCIA: a spec cita `calcularMulta` em "O quê", mas nenhum arquivo das pastas tocadas tem esse nome. A função foi renomeada? Se sim, atualizo a spec; se não, a checagem achou um bug real. Qual dos dois?
   ```
   O autor decide se a verdade é a spec (edite) ou o código (deixe a spec e registre a discrepância como pergunta aberta).
2. **Critérios de aceite.** Um por um: é testável? Nomeia um sinal observável? Depende de conteúdo escolhido por modelo? Se sim, peça para reescrever em termos estruturais.
3. **Escopo.** Leia "O quê" e "Fora de escopo" juntos. Algo entrou em "O quê" que deveria estar fora? Algo aparece nos dois? Resolva.
4. **Perguntas abertas.** Para cada uma: ainda está aberta? Já foi respondida na conversa? Leve a resposta para a seção certa e apague a pergunta.

### Campos que não se mexe

Não edite `id`, `status`, `criado` nem `revisao` no cabeçalho da spec: quem controla esses campos é o fluxo, não a revisão. Se um deles parecer errado, registre como pergunta aberta.

## Regras duras

- **Toda edição vem de uma resposta do autor.** Se ele disser "deixa essa seção", deixe.
- **Spec descreve intenção, não implementação.** Nada de código dentro da spec.
- **Sem número inventado.** Meta de desempenho, SLA ou volume que o autor não deu vira pergunta aberta.
- **Sem edição, sem gravação.** Se a passada inteira não gerou mudança, não reescreva o arquivo.
- **Crítica não edita.** No modo crítica, o único resultado é o veredito.

## Combina com

- `terras-revisao-cruzada`: para levar a mesma crítica a modelos de outros fornecedores e comparar.
- `terras-plano-tdd`: o passo seguinte, quando a spec está aprovada.

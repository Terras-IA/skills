---
name: terras-bar-raiser-de-cultura
version: 1.0.0
access: free
category: contratação
description: Estrutura entrevistas de fit cultural com critérios observáveis, scoring e recomendação; use em processos seletivos que exigem avaliação consistente de valores.
keywords: [entrevista de cultura, fit cultural, bar raiser, avaliar valores, veto de contratação, scorecard de entrevista]
---

# Bar Raiser de Cultura

## Descrição

Transforma valores e comportamentos esperados em uma entrevista estruturada para liderança, separando evidência observável de impressão pessoal. O resultado apoia uma decisão consistente sem substituir a avaliação técnica, a checagem de referências ou a deliberação humana.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Abrir a etapa de cultura para uma pessoa candidata a liderança.
- Comparar entrevistas conduzidas por avaliadores diferentes.
- Investigar uma recomendação “contratar” com evidências conflitantes.
- Definir um veto baseado em critério previamente anunciado.
- Preparar o comitê final de contratação.

## Como funciona

### Inputs esperados

Descrição da vaga em texto ou .docx; quatro competências com definição e exemplos de comportamento; respostas transcritas identificadas apenas por código; escala de 1 a 4; regra de veto; e matriz de entrevistadores. Origem: descrição aprovada, guia de valores e formulário de entrevista. Campos mínimos: candidato_id, pergunta_id, resposta, evidência, avaliador_id, nota e confiança da nota.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Confirmar que cada competência tem comportamento observável e não um traço de personalidade.
2. Distribuir quatro dimensões entre entrevistadores e escrever duas perguntas comportamentais por dimensão.
3. Ler as respostas procurando contexto, ação da pessoa e resultado; marcar citação, fato ou ponto ainda não comprovado.
4. Pontuar cada dimensão de 1 a 4, justificando a nota com evidência e distinguindo “não observado” de nota baixa.
5. Aplicar a regra de veto apenas quando o critério crítico tiver sinal de risco documentado e pergunta de aprofundamento respondida.
6. Consolidar média, dispersão, pontos fortes, riscos e perguntas pendentes; não calcular uma média para apagar um veto válido.
7. Apresentar recomendação “contratar”, “não contratar” ou “prosseguir com diligência”, com decisão e responsável pelo registro.

### Casos de borda

- Se houver uma única entrevista, declarar baixa confiabilidade e solicitar uma segunda evidência.
- Se a resposta for vaga, não inferir caráter: registrar “evidência insuficiente” e propor pergunta de aprofundamento.
- Se os avaliadores divergirem dois ou mais pontos, levar o caso ao comitê antes da decisão.
- Se o critério não estiver na vaga, não criar veto retroativo.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Scorecard .xlsx ou relatório .html com resumo executivo, matriz das quatro dimensões, citações ou referências às respostas, nota, confiança, regra de veto, divergências e recomendação final. A aba de evidências preserva o código da pessoa, a de decisão registra participantes e data, e a de perguntas pendentes vira roteiro da próxima conversa. A pessoa de RH leva o arquivo ao comitê e arquiva somente a versão com acesso restrito.

Na reunião, o comitê começa pelo resumo, abre evidências quando houver discordância e registra a decisão humana. Não usar o scorecard como decisão automática nem como substituto de referências.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta scorecard de entrevista cultural, com quatro cards de dimensão com nota, cor semântica e confiança; barra de recomendação final; acordeões de evidências, perguntas pendentes e regra de veto. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

Use exclusivamente estes tokens do design system em variáveis CSS: `--color-brand: #B5004C`, `--color-brand-hover: #8F0340`, `--color-brand-active: #69022D`, `--color-brand-secondary: #FFE6F2`, `--color-bg: #FFFFFF`, `--color-bg-secondary: #F5F5F5`, `--color-bg-dark: #141414`, `--color-text-primary: #141414`, `--color-text-secondary: #666666`, `--color-border: #E0E0E0`, `--color-success: #00A651`, `--color-error: #D9201C`, `--color-warning: #E6A800`, `--color-info: #1A73E8`, `--radius-sm: 8px`, `--radius-md: 12px`, `--radius-lg: 16px` e `--radius-full: 99px`. Aplique a tipografia `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`, espaçamento consistente, bordas, sombras discretas e foco visível; nunca use cores inline fora das variáveis.

A interatividade é leve e funciona sem dependências externas: use `<details>` para evidências, perguntas e metodologia; `<fieldset>` com radio buttons e checkboxes estilizados para filtros; e CSS com `:checked` para tabs ou visibilidade quando fizer sentido. Não use CDN, fontes remotas, imagens remotas, bibliotecas externas ou gráficos em canvas. O template abaixo é uma estrutura mínima: preserve tokens, substitua placeholders pelos dados disponíveis e inclua fonte, período, acessibilidade e limitações junto ao conteúdo específico.

### Template HTML básico

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>[Nome da skill] — Relatório visual</title>
  <style>
    :root {
      --color-brand: #B5004C; --color-brand-hover: #8F0340; --color-brand-active: #69022D;
      --color-brand-secondary: #FFE6F2; --color-bg: #FFFFFF; --color-bg-secondary: #F5F5F5;
      --color-bg-dark: #141414; --color-text-primary: #141414; --color-text-secondary: #666666;
      --color-border: #E0E0E0; --color-success: #00A651; --color-error: #D9201C;
      --color-warning: #E6A800; --color-info: #1A73E8; --radius-sm: 8px; --radius-md: 12px;
      --radius-lg: 16px; --radius-full: 99px;
    }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      color: var(--color-text-primary); background: var(--color-bg); }
    .report-header, main { max-width: 1200px; margin: auto; padding: 32px 24px; }
    .kpi-grid, .content-grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
    .card { background: var(--color-bg); border: 1px solid var(--color-border);
      border-radius: var(--radius-md); padding: 20px; box-shadow: 0 2px 8px rgba(20,20,20,.08); }
    .bar { height: 10px; border-radius: var(--radius-full); background: var(--color-bg-secondary); }
    .bar > span { display: block; height: 100%; width: var(--value, 0%); border-radius: inherit; background: var(--color-brand); }
    details { border-top: 1px solid var(--color-border); padding: 12px 0; }
    :focus-visible { outline: 3px solid var(--color-info); outline-offset: 2px; }
  </style>
</head>
<body>
  <header class="report-header"><h1>[Título]</h1><p>[Período · origem · responsável]</p></header>
  <main>
    <section class="kpi-grid" aria-label="Resumo"><article class="card">[KPI]</article></section>
    <section class="content-grid" aria-label="[Componentes específicos]"><article class="card">[Tabela ou gráfico CSS]</article></section>
    <details><summary>Evidências e metodologia</summary><p>[Fonte, limitações e pendências]</p></details>
  </main>
</body>
</html>
```

### Interatividade

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar quatro cards de dimensão com nota, cor semântica e confiança. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Vaga: Gerente de Operações, 12 liderados. Dimensões: colaboração, responsabilidade, desenvolvimento de pessoas e decisão sob pressão. Candidata C-014, entrevistada por Ana e Bruno. Na pergunta sobre incidente de entregas, relatou reduzir o escopo, comunicar clientes e revisar o processo; resultado informado: prazo recuperado em duas semanas. Notas: colaboração 4, responsabilidade 3, desenvolvimento 2, pressão 4. Veto definido previamente: nenhuma evidência de responsabilização de terceiros em crise.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Resumo: recomendação “prosseguir com diligência”. Tabela: colaboração 4 (exemplo concreto de alinhamento), responsabilidade 3 (resultado não documentado), desenvolvimento 2 (não trouxe feedback aplicado), pressão 4. Média de 3,25, sem veto acionado, confiança média. Pergunta pendente: pedir um caso em que desenvolveu alguém com baixo desempenho. O comitê registra Bruno como responsável pela checagem e mantém a decisão condicionada à segunda evidência.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Remover nome, foto, idade e qualquer marcador protegido do material compartilhado com o comitê; usar apenas o código da candidatura.
- Guardar transcrições e scorecard em acesso restrito e definir prazo de retenção compatível com a política de recrutamento.
- Veto só pode existir se o critério tiver sido divulgado, aplicado igualmente e revisado por uma pessoa de RH; nunca usar sotaque, estilo ou afinidade como evidência.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

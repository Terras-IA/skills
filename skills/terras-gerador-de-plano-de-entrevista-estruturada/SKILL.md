---
name: terras-gerador-de-plano-de-entrevista-estruturada
version: 1.0.0
access: free
category: contratação
description: Cria roteiros por competência com perguntas comportamentais, sinais de evidência e rubrica de avaliação.
keywords: [plano de entrevista, entrevista estruturada, roteiro de perguntas, rubrica de avaliação, perguntas comportamentais, painel de entrevistas]
---

# Gerador de Plano de Entrevista Estruturada

## Descrição

Monta um roteiro replicável para avaliar uma competência com perguntas comportamentais, repreguntas e rubrica. O foco é produzir evidência comparável entre pessoas, sem transformar a conversa em interrogatório ou em julgamento de personalidade.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Avaliar colaboração em cinco perguntas.
- Treinar entrevistadores antes de uma vaga crítica.
- Reduzir perguntas improvisadas e repetidas.
- Construir uma rubrica para painel de entrevistas.
- Revisar se a etapa mede a competência anunciada.

## Como funciona

### Inputs esperados

Descrição de vaga; competência e definição; nível esperado; cinco situações de trabalho; duração; número de entrevistadores; escala de 1 a 4; sinais positivos, negativos e neutros; e campos para evidência. Origem: matriz de competências, gestor e recrutador. Registrar pergunta_id, pergunta, objetivo, repregunta, evidência e nota.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Definir o comportamento-alvo e o que não faz parte da avaliação.
2. Distribuir cinco perguntas entre contexto, ação, decisão, colaboração e resultado, evitando perguntas hipotéticas em excesso.
3. Criar duas repreguntas neutras para cada pergunta e um limite de tempo.
4. Especificar rubrica por nível: resposta genérica, ação parcial, ação consistente e impacto demonstrado.
5. Adicionar instruções de abertura, acessibilidade, consentimento para anotações e encerramento.
6. Pilotor o roteiro com um entrevistador, identificar ambiguidade e ajustar sem alterar a competência no meio do processo.
7. Consolidar evidência e nota separadamente, com campo para dúvida e revisão.

### Casos de borda

- Se a pessoa não tiver vivido a situação, aceitar experiência equivalente e marcar o contexto.
- Se o tempo acabar, não atribuir nota pela parte não perguntada; registrar “não observado”.
- Se a pergunta induzir uma resposta socialmente desejável, reescrever antes da entrevista.
- Se a competência não puder ser medida por relato, combinar com exercício aprovado e declarar a limitação.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Roteiro .docx ou .html de 45 minutos com abertura, cinco perguntas, repreguntas, evidências esperadas, rubrica 1–4, campos de notas, alerta de perguntas proibidas e fechamento. Uma matriz relaciona pergunta, competência, tempo e entrevistador. RH usa a versão do entrevistador e guarda uma cópia consolidada para comparação.

Distribua o mesmo núcleo de perguntas para todas as pessoas da etapa. Permita repreguntas de esclarecimento, mas não troque o critério por afinidade; depois, o painel compara evidências antes das notas.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta roteiro visual de entrevista estruturada, com cabeçalho com duração; timeline de abertura, cinco perguntas, repreguntas e fechamento; cards de competência; tabela de rubrica; checklist de perguntas proibidas. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar cabeçalho com duração. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Competência: colaboração para Analista de RH Sênior. Duração: 45 minutos; cinco perguntas; escala 1–4. Contexto informado: o time tinha três áreas com dados divergentes. Evidência desejada: alinhamento de interesses, ação própria, resultado verificável e aprendizado.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Roteiro com cinco perguntas, por exemplo: “Conte uma situação em que precisou alinhar áreas com prioridades diferentes”. Repreguntas: “Qual foi sua ação específica?” e “Como verificou o resultado?”. Rubrica: nota 4 exige mediação explícita e indicador; nota 2 aceita ação parcial sem resultado. Tabela de notas para C-022 fica com colaboração 3, evidência “reuniu Financeiro e RH e reduziu retrabalho”, resultado ainda não quantificado; confiança média.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Não perguntar sobre família, saúde, religião, origem ou qualquer tema sem relação com a competência e a legislação aplicável.
- Manter o mesmo núcleo de perguntas, tempo e rubrica para comparabilidade; registrar adaptações de acessibilidade sem penalização.
- Acessar notas apenas pelo painel autorizado, separar evidência de opinião e eliminar rascunhos conforme a política de retenção.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

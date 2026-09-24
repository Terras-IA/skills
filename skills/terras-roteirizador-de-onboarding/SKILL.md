---
name: terras-roteirizador-de-onboarding
version: 1.0.0
access: free
category: contratação
description: Monta um plano de onboarding de 30, 60 e 90 dias com check-ins, tarefas e expectativas claras para a nova pessoa.
keywords: [onboarding, plano de 30 60 90 dias, integração de pessoa nova, check-ins de onboarding, buddy, primeira semana]
---

# Roteirizador de Onboarding

## Descrição

Cria um plano de 30, 60 e 90 dias que combina contexto, entregas, relações e check-ins. A pessoa nova recebe clareza sobre sucesso e apoio; a liderança recebe uma sequência verificável, não uma lista genérica de links.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Integrar uma nova analista de rh.
- Organizar primeiro mês de uma posição híbrida.
- Alinhar expectativas entre líder, pessoa nova e buddy.
- Acompanhar evolução em 30, 60 e 90 dias.
- Corrigir um onboarding que depende de improviso.

## Como funciona

### Inputs esperados

Formulário com cargo, nível, gestor, data de início, modelo de trabalho, missão, entregas 30/60/90, sistemas autorizados, buddy, reuniões, treinamentos obrigatórios e checkpoints. Origem: vaga aprovada, matriz de competências, IT e gestor. Campos de tarefa: dono, prazo, dependência, status, evidência e risco.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Confirmar missão, escopo e resultado esperado no primeiro trimestre.
2. Dividir tarefas em pré-início, primeira semana, dias 8–30, 31–60 e 61–90.
3. Combinar aprendizagem, relacionamento, entrega e bem-estar sem exigir disponibilidade fora do horário.
4. Definir dono e evidência de conclusão para cada tarefa; dependências viram alertas.
5. Preparar agenda de check-ins no primeiro dia, fim da semana 1, dia 30, 60 e 90.
6. Adaptar o plano a acessibilidade, localização e experiência sem expor dados de saúde.
7. Revisar com a pessoa nova e o líder; atualizar status e registrar aprendizados do processo.

### Casos de borda

- Se acessos não estiverem prontos, criar caminho de contingência e não preencher com credenciais.
- Se a missão mudar antes do dia 30, congelar a versão anterior e renegociar metas.
- Se o buddy não estiver disponível, indicar substituto e sinalizar o risco ao líder.
- Se a pessoa relatar barreira de acessibilidade, encaminhar pelo canal apropriado, sem detalhar no documento compartilhado.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Checklist .xlsx ou página .html com linha do tempo 30/60/90, tarefas, donos, datas, status e evidências; agenda .ics ou tabela de check-ins; resumo de expectativas e perguntas frequentes. A liderança usa o plano em 1:1s e RH acompanha apenas pendências necessárias, não notas íntimas.

Entregue a versão de boas-vindas à pessoa e a versão operacional ao time responsável. Marque itens concluídos somente com evidência simples, como reunião realizada ou acesso testado.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta timeline de onboarding 30/60/90 dias, com três colunas de marcos; cards de tarefa com dono, data e status; barra de progresso; checklist de check-ins; bloco de expectativas e FAQ. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar três colunas de marcos. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Pessoa: Juliana Alves, Analista de RH, início em 05/08. Gestor: Renan Costa; buddy: Camila Souza. Em 30 dias: entender ciclo de admissão e publicar um relatório assistido; em 60: conduzir um diagnóstico; em 90: apresentar uma melhoria. Check-ins semanais às quartas, acesso ao sistema de pessoas e trilha de LGPD.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Plano com pré-início: equipamento e acesso solicitados por TI; semana 1: reunião com folha, segurança e time; dia 30: relatório revisado; dia 60: diagnóstico apresentado ao gestor; dia 90: melhoria com indicador de sucesso. Cada item tem dono e status. Alertas: acesso ao sistema pendente e buddy indisponível na semana 2. Check-in do dia 30 pergunta o que ficou confuso e qual suporte é necessário.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Nunca incluir senhas, tokens ou dados de outros colaboradores no plano; registrar somente que o acesso foi solicitado e testado.
- Compartilhar expectativas com a pessoa nova e restringir feedbacks sensíveis ao canal de liderança/RH autorizado.
- Armazenar dados pessoais pelo tempo necessário ao onboarding; tratar pedidos de acessibilidade com confidencialidade e sem exposição.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

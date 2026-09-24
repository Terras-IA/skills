---
name: terras-gerador-de-politica-de-beneficios
version: 1.0.0
access: free
category: benefícios
description: Redige políticas de benefícios claras, aplicáveis e alinhadas ao PAT e ao orçamento informado pela empresa.
keywords: [política de benefícios, benefício flexível, pat, regras de benefícios, política de va e vr, elegibilidade de benefícios]
---

# Gerador de Política de Benefícios

## Descrição

Redige uma política de benefício flexível com regras compreensíveis, exemplos, canais e pontos de validação jurídica, incluindo alinhamento ao PAT quando aplicável.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Estruturar ou revisar uma rotina de criar política de benefício flexível alinhada ao pat.
- Preparar uma decisão com evidências para a liderança.
- Padronizar o trabalho entre áreas e responsáveis.
- Criar um artefato reutilizável para acompanhamento.
- Detectar riscos, pendências e dados que ainda precisam de validação.

## Como funciona

### Inputs esperados

objetivo; público; créditos; categorias; elegibilidade; coparticipação; PAT; fornecedores; exceções; canal; vigência e aprovação jurídica.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Mapear regras.
2. Separar o que é obrigatório e opcional.
3. Escrever elegibilidade.
4. Explicar saldo e prazo.
5. Criar exemplos.
6. Revisar PAT.
7. Definir atendimento e mudança.

### Casos de borda

- Regra local divergente.
- Fornecedor não confirmado.
- Saldo expirado e afastamento exigem cláusulas de tratamento.
- Não preencher lacuna legal.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Política .docx/.html com objetivo, escopo, glossário, regras, exemplos, FAQ, canais, vigência e histórico; versão curta para colaboradores.

Use o artefato para orientar a conversa, a decisão e o acompanhamento. Leia o resultado com a fonte, o período e as limitações visíveis; qualquer envio ou mudança depende de aprovação humana.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta página visual de política de benefícios, com hero com vigência; cards de benefícios; tabela de regras e exceções; timeline de histórico; FAQ; glossário e canais. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar hero com vigência. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Política MOCK: crédito mensal de R$ 600 em quatro categorias, admissão após 30 dias, saldo não convertido em dinheiro e atendimento em canal definido. Exemplos MOCK para pessoa CLT e afastamento, com pontos legais pendentes para validação.

Política MOCK: crédito mensal de R$ 600 em quatro categorias, admissão após 30 dias, saldo não convertido em dinheiro e atendimento em canal definido. Exemplos MOCK para pessoa CLT e afastamento, com pontos legais pendentes para validação.

### Output esperado

Saída MOCK adicional: o artefato separa dados observados, premissas, pendências, responsável e próxima revisão; nenhuma lacuna é preenchida por suposição.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Não incluir dados individuais.
- Validar PAT e legislação com jurídico.
- Explicar tratamento de afastamentos sem coletar diagnóstico.
- Registrar consentimento e canal de contestação.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

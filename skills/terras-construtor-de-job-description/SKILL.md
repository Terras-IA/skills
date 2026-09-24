---
name: terras-construtor-de-job-description
version: 1.0.0
access: free
category: contratação
description: Gera descrições de cargo claras, inclusivas e alinhadas à cultura e ao modelo de competências da organização.
keywords: [descrição de vaga, job description, descrição de cargo, abrir vaga, requisitos da vaga, vaga inclusiva]
---

# Construtor de Job Description

## Descrição

Converte uma necessidade de contratação em uma descrição de cargo clara, inclusiva e testável. A estrutura conecta missão, entregas, competências e critérios de seleção, evitando listas infladas de requisitos que afastam candidaturas qualificadas.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Abrir uma nova posição de especialista.
- Atualizar uma descrição que recebe candidaturas desalinhadas.
- Padronizar vagas entre áreas e níveis.
- Adaptar uma vaga para comunicação inclusiva.
- Alinhar recrutamento e liderança sobre escopo e senioridade.

## Como funciona

### Inputs esperados

Briefing .docx ou formulário com título, área, gestor, localização e modelo de trabalho; três a cinco entregas dos primeiros seis meses; indicadores; faixa salarial; requisitos obrigatórios e desejáveis; competências; benefícios; e processo seletivo. Origem: gestor requisitante, arquitetura de cargos e política de remuneração. Campos: responsabilidade, frequência, autonomia, dependências e critério de sucesso.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Validar o problema que a vaga resolve e escrever uma frase de missão sem jargão.
2. Separar entregas mensuráveis de atividades rotineiras e limitar requisitos obrigatórios ao que é realmente eliminatório.
3. Relacionar cada competência a comportamento observável e à pergunta de entrevista que a testará.
4. Checar coerência entre título, nível, escopo, faixa e autonomia; sinalizar conflito em vez de escolher um nível sozinho.
5. Redigir a seção de inclusão, modelo de trabalho, processo e faixa sem prometer o que a política não garante.
6. Revisar linguagem, acessibilidade e neutralidade; explicar termos técnicos inevitáveis.
7. Entregar uma versão para aprovação do gestor e uma ficha de rastreabilidade que liga requisito a evidência do processo.

### Casos de borda

- Se a faixa não estiver aprovada, usar “a definir” e bloquear publicação; não inventar remuneração.
- Se o gestor enviar 15 requisitos, classificar por necessidade e pedir priorização.
- Se houver trabalho híbrido sem regra de presença, registrar a pendência explicitamente.
- Se o cargo combinar dois níveis, produzir alternativas e solicitar decisão de arquitetura.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Documento .docx ou .html pronto para publicação, com cabeçalho da vaga, missão, entregas 30/60/90, responsabilidades, requisitos obrigatórios e desejáveis, competências, faixa, benefícios, inclusão, local, processo e FAQ. Inclui uma tabela interna de rastreabilidade: requisito, motivo, como avaliar e dono da aprovação. RH publica somente após o gestor validar.

A versão pública serve ao candidato; a ficha interna orienta triagem e entrevista. Na aprovação, compare a vaga com a matriz de carreira e registre as mudanças para evitar que o escopo cresça sem revisão.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta página editorial de descrição de vaga, com hero com cargo, missão e local; cards de entregas 30/60/90; tabela de responsabilidades e requisitos; chips de competências e benefícios; FAQ inclusivo. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar hero com cargo, missão e local. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Área: People Analytics; gestor: Marcelo Nunes; cargo: Analista de RH Sênior; híbrido em São Paulo. Entregas em seis meses: automatizar relatório mensal de headcount, criar dicionário de métricas e apresentar dois insights à diretoria. Obrigatórios: experiência com indicadores de pessoas, planilhas avançadas e comunicação executiva. Desejáveis: SQL e visualização. Faixa aprovada: R$ 9.000–R$ 12.000.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Missão: transformar dados de pessoas em decisões acionáveis. Entregas: dicionário aprovado até o mês 2; painel mensal até o mês 3; dois fóruns executivos até o mês 6. Requisitos separados em obrigatórios e desejáveis, pergunta de entrevista vinculada a cada competência, faixa de R$ 9.000–R$ 12.000 e seção “como será o processo”. A ficha aponta que SQL é desejável, não eliminatório, e que o gestor precisa confirmar os dias presenciais.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Não incluir dados pessoais de empregados nem critérios indiretos como “perfil jovem” ou “energia” na vaga; justificar cada requisito pela entrega.
- Publicar apenas faixa e benefícios aprovados; não expor informações internas de remuneração individual.
- Submeter a versão final a revisão de inclusão e acessibilidade antes da divulgação, mantendo histórico das alterações e do responsável.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

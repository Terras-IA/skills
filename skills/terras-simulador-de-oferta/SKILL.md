---
name: terras-simulador-de-oferta
version: 1.0.0
access: free
category: contratação
description: Simula propostas de remuneração considerando benchmark de mercado, equidade interna e cenários de negociação.
keywords: [simular oferta, proposta de remuneração, contraproposta, faixa salarial, equity, compressão salarial, negociação de salário]
---

# Simulador de Oferta

## Descrição

Compara cenários de proposta para uma contratação sem reduzir a decisão a salário. O simulador explicita benchmark, posição na banda, equidade interna, custo anual e espaço de negociação, sempre deixando as premissas visíveis para aprovação.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Preparar oferta para uma pessoa desenvolvedora sênior.
- Avaliar contraproposta acima da faixa.
- Comparar salário, variável, benefícios e equity.
- Verificar compressão com pares internos.
- Preparar limites de negociação para recrutamento.

## Como funciona

### Inputs esperados

Planilha .xlsx com cargo, nível, faixa mínima/média/máxima, salário proposto, variável-alvo, benefícios, benchmark com data e percentil, pares comparáveis anonimizados, custo patronal e limite orçamentário. Origem: remuneração, orçamento e recrutamento. Campos obrigatórios: cenário_id, premissa, valor, fonte, data, responsável e aprovação necessária.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Fixar cargo, nível, localidade e data do benchmark antes de comparar valores.
2. Selecionar pares internos pela mesma família, nível e escopo; excluir casos com mudança recente não comparável.
3. Calcular posicionamento na banda e custo anual em três cenários: alvo, mínimo viável e limite aprovado.
4. Separar remuneração fixa, variável, benefícios e itens condicionais; não tratar benefício como dinheiro equivalente sem regra.
5. Testar uma contraproposta e mostrar impacto em equidade interna e orçamento.
6. Redigir a mensagem de oferta com itens aprovados e o que ainda depende de aprovação.
7. Submeter o cenário escolhido a RH e liderança, registrando motivo e validade da proposta.

### Casos de borda

- Se benchmark tiver data ou amostra desconhecida, rotular como referência fraca e não prometer percentil.
- Se não houver pares comparáveis, apresentar a lacuna e usar apenas a banda aprovada.
- Se a proposta ultrapassar a faixa, bloquear recomendação automática e pedir exceção documentada.
- Se a pessoa recusar, preservar o histórico sem reutilizar dados pessoais em nova negociação.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Modelo .xlsx com abas premissas, pares anonimizados, cenários, impacto orçamentário e aprovação, além de resumo .html para o recrutador. Mostra faixa, midpoint, percentil quando fornecido, custo anual, diferença para pares e roteiro de negociação. A pessoa responsável leva o resumo à aprovação e usa somente a versão validada no contato.

Use o simulador para discutir alternativas antes de falar com a pessoa. Não compartilhar comparações individuais nem revelar a remuneração de colegas; a oferta enviada contém apenas itens da própria proposta.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta simulador visual de oferta, com cards de faixa, midpoint, percentil e custo; comparador de cenários; barras de distância aos pares agregados; tabela de premissas; bloco de aprovação e alertas. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar cards de faixa, midpoint, percentil e custo. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Cargo: Desenvolvedor Backend Sênior, São Paulo. Banda R$ 16.000–R$ 21.000, midpoint R$ 18.500. Candidata C-031 pede R$ 19.500. Benchmark interno informado com data de março: referência de mercado R$ 18.000–R$ 22.000. Três pares anonimizados: R$ 18.700, R$ 19.200 e R$ 20.100. Bônus-alvo 10%, orçamento anual adicional máximo R$ 260.000.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Cenário alvo: fixo R$ 19.500, 93% da banda e 105,4% do midpoint; variável-alvo de 10%; custo anual estimado calculado com premissas separadas. Comparação com pares em faixa, sem revelar identidades. Cenário alternativo: R$ 18.800 + bônus, diferença anual e risco de compressão destacados. Recomendação: aprovar R$ 19.500 dentro da banda, condicionada à confirmação do custo patronal; validade da proposta registrada.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Usar apenas dados salariais agregados e anonimizados de pares; nunca revelar a uma candidata a remuneração identificável de outra pessoa.
- Registrar fonte, data e cobertura do benchmark; referência de mercado é hipótese de planejamento, não promessa de valor.
- Exigir aprovação humana para exceções, variável e benefícios; preservar a justificativa sem criar perfil permanente sobre a pessoa candidata.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

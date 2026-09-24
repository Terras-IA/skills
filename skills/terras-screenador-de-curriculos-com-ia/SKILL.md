---
name: terras-screenador-de-curriculos-com-ia
version: 1.0.0
access: free
category: contratação
description: Ranqueia currículos por requisitos da vaga e anonimiza dados sensíveis para apoiar uma triagem mais justa e auditável.
keywords: [triagem de currículos, rankear candidatos, anonimizar currículos, filtro de currículo, triagem justa, screening]
---

# Screenador de Currículos com IA

## Descrição

Organiza uma triagem baseada em requisitos previamente definidos e anonimiza sinais que podem introduzir viés. A saída é uma fila explicável, não uma decisão automática: cada posição precisa mostrar qual evidência do currículo atende ou não atende ao requisito.

Esta instrução é um guia operacional: não decide sozinha sobre contratação, avaliação, remuneração, carreira, benefícios ou desligamento. Trabalhe com o contexto, a política aprovada e a revisão da pessoa responsável. Quando um dado não existir, escreva “não informado” e explique qual decisão fica bloqueada.

## Quando usar

- Triagem inicial de uma vaga com muitos currículos.
- Comparar 15 candidaturas para uma vaga técnica.
- Padronizar justificativas de avanço e eliminação.
- Retirar nome, foto e endereço antes da leitura.
- Auditar se o ranking segue os critérios aprovados.

## Como funciona

### Inputs esperados

Planilha .xlsx com candidato_id, formação, experiências, duração, tecnologias, resultados e links; descrição da vaga com requisitos obrigatórios e desejáveis; pesos; regra mínima; e registro de indisponibilidade. Origem: sistema de recrutamento e vaga aprovada. Não enviar nome, foto, CPF, idade, endereço completo, estado civil ou outros dados não necessários.

Antes de processar, confirme período, unidade de medida, versão da política, dono da base e autorização de uso. Prefira identificadores internos ou códigos; remova campos que não mudam a análise. O template mínimo de entrada deve ser uma tabela em que cada coluna tenha nome, tipo, exemplo de preenchimento, origem e regra de validação. Se a pessoa usuária trouxer texto solto, reorganize-o nessa tabela e peça confirmação dos campos críticos antes de concluir.

### Passo a passo

1. Transformar a vaga em uma matriz de critérios com definição, peso e evidência aceitável.
2. Remover identificadores diretos e conferir se não restaram campos que funcionem como proxy indevido.
3. Extrair evidências literalmente do currículo e marcar ausência como “não informado”, sem supor experiência.
4. Aplicar a regra de corte e calcular pontuação reproduzível; listar o critério que impediu avanço.
5. Fazer amostragem manual do topo, meio e fundo da fila para detectar distorções.
6. Separar recomendação de triagem de decisão de contratação e devolver dúvidas ao recrutador.
7. Exportar logs e permitir contestação ou revisão humana antes de qualquer contato.

### Casos de borda

- Se o currículo estiver em imagem ilegível, marcar “precisa de leitura humana”, não penalizar automaticamente.
- Se um requisito não puder ser verificado, manter a pessoa como pendente e pedir evidência adicional.
- Se a amostra for pequena, não apresentar ranking como probabilidade de sucesso.
- Se candidatos empatam, usar critério aprovado ou sorteio auditável, nunca nome ou instituição como desempate informal.

Em qualquer caso de borda, preserve a saída com a marca “pendente”, “não observado” ou “base insuficiente”. Não produza uma precisão artificial: o artefato deve informar cobertura, limitações, versão das regras e qual pessoa precisa revisar o resultado.

## Artefato de saída

Planilha .xlsx com abas critérios, currículos anonimizados, ranking, pendências e auditoria; ou relatório .html com filtros por requisito. Cada linha traz candidato_id, pontuação, evidências, critérios faltantes, confiança e revisão humana. O recrutador usa a fila para priorizar leitura e registra a decisão final separadamente.

Use primeiro como apoio à leitura, valide uma amostra e só depois convide pessoas. O arquivo também permite explicar a decisão a um comitê e corrigir o peso sem refazer a triagem manual inteira.

## Artefato visual (HTML)

Este artefato visual deve ser um relatório HTML autossuficiente, em português, orientado à decisão e à leitura acessível. Ele apresenta painel de triagem de currículos, com cards de candidatos priorizados; barras por requisito; tabela anonimizada com evidência, lacuna e confiança; painel de critérios faltantes; faixa de cobertura. O cabeçalho informa título, período, origem dos dados, escopo e responsável pela revisão; quando algo não estiver disponível, exibe “não informado” ou “pendente”, sem preencher lacunas. A hierarquia começa pelo resumo executivo, segue para evidências e termina em ações, limitações e próximo passo. Tabelas têm cabeçalhos, legendas e estado vazio; gráficos usam barras, trilhas, pontos ou progress circles feitos somente com CSS puro, sempre acompanhados de valor textual e denominador. O layout é responsivo: uma coluna em telas pequenas, duas em tablet e grade confortável em desktop.

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

Use `<details>` para abrir evidências, regras e pendências, e controles nativos para filtrar cards de candidatos priorizados. Tabs podem ser implementadas com radio buttons e CSS `:checked`, sem JavaScript externo. Estados sem dados, baixa cobertura e bloqueios devem permanecer visíveis; interação apenas reorganiza a leitura e nunca altera a fonte nem cria uma decisão.

## Exemplo de uso

### Input fictício

(dados fictícios para exemplo) — todos os nomes, números e valores são MOCK.
Vaga: Desenvolvedor Backend Sênior. Obrigatórios: Java ou Kotlin, APIs REST, testes automatizados e cinco anos de experiência. Desejáveis: mensageria e liderança técnica. Quinze currículos anonimizados; C-003: 7 anos, Kotlin, REST, testes e Kafka; C-008: 4 anos, Java, REST e testes; C-011: 8 anos, Python e APIs, sem Java/Kotlin informado.

### Output esperado

(dados fictícios para exemplo; saída MOCK)
Fila: C-003, 92/100, avança; C-008, 76/100, pendente para confirmar tempo mínimo; C-011, 54/100, não atende ao requisito obrigatório de linguagem informada. Tabela de evidências cita “serviço de pagamentos em Kotlin” para C-003, marca liderança técnica como ausente e mantém os 15 IDs no relatório. Auditoria: 3 casos precisam de revisão manual; nomes e fotos não foram usados.

O exemplo acima é apenas uma simulação operacional: não é dado real, não deve ser usado para inferir pessoas ou metas e serve para mostrar o nível de detalhe esperado no preenchimento do template e na leitura do artefato.

## Governança

- Anonimizar antes da triagem e limitar o acesso à chave candidato_id; a chave fica com o recrutamento autorizado.
- Validar pesos e cortes com RH e liderança antes do uso e medir avanço por grupo somente quando houver base legal e tamanho adequado.
- Nunca rejeitar automaticamente uma pessoa nem inferir competência a partir de nome, foto, idade, endereço, instituição ou lacunas do currículo.

## Critério de qualidade

A entrega está pronta somente quando contém fonte e período dos dados, premissas explícitas, entradas faltantes, rastreabilidade das transformações, limitações, responsável pela revisão e próximo passo. Uma recomendação sem evidência deve ser apresentada como hipótese, nunca como fato.

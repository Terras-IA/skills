---
name: terras-tech-debt
version: 1.0.0
access: free
category: operacao
description: Auditoria de dívida técnica de um repositório inteiro, com achados citando arquivo e linha, severidade e esforço sob rubrica declarada, seção obrigatória "parece ruim mas está certo" e relatório acionável.
keywords: [divida tecnica, tech debt, auditoria de repositorio, codebase health]
---

# Auditoria de dívida técnica

## Descrição

Ler um repositório inteiro e produzir um relatório de dívida técnica com achados que apontam arquivo e linha, severidade, esforço e recomendação. O relatório tem que ser acionável: cada item precisa dar para alguém abrir o arquivo, ver o problema e decidir.

Não é revisão de estilo nem lista de boas práticas genéricas. É o que está errado neste repositório, com evidência.

## Quando usar

- Pedido de auditoria de dívida técnica, diagnóstico de codebase, revisão de arquitetura ou health check de repositório.
- Antes de assumir um projeto legado, numa entrega grande, ou quando o time sente que "tudo está difícil" sem saber por quê.

## Regras duras

1. **Somente leitura.** A auditoria não altera o repositório auditado. O único arquivo escrito é o relatório, no lugar que o usuário pedir. Nada de instalar dependências, commitar, formatar ou "aproveitar e corrigir".
2. **Toda citação é verificada.** Antes de escrever um achado, abra o arquivo e confira a linha citada. Achado com linha errada destrói a confiança no relatório inteiro. Cite o símbolo junto quando ajudar.
3. **Sem invenção.** Não afirme o que não leu. O que não deu para determinar se é dívida ou decisão consciente vai para "perguntas abertas", não para a lista de achados.
4. **Sem reescrita.** Recomende mudanças específicas e pequenas. "Reescreva o módulo" não é recomendação, é desistência.
5. **Sem enchimento e sem bajulação.** Categoria sem achado material recebe "Nada material". Não existe elogio de cortesia no relatório.
6. **Sem segredos no relatório.** Chave ou senha hardcoded: cite arquivo, linha e o tipo da credencial. Nunca copie o valor.

## Rubrica de severidade e esforço

Severidade sem definição vira opinião. Use esta régua e diga no relatório que usou ela:

| Severidade | Critério | Prazo sugerido |
|---|---|---|
| Crítico | Risco de incidente em produção, perda de dado, falha de segurança explorável, ou bloqueio de entrega | Esta semana |
| Alto | Degrada confiabilidade ou velocidade do time de forma mensurável | Ciclo atual |
| Médio | Custo recorrente de manutenção, sem risco imediato | Agendar |
| Baixo | Higiene, consistência, oportunidade | Quando sobrar espaço |

Esforço: **S** (até 1 dia, escopo local), **M** (2 a 5 dias, toca 2+ módulos ou migração simples), **L** (1 semana ou mais, muda contrato, migra dado ou exige coordenação).

## Como funciona

### Fase 1: orientar

Não pule — opinião formada antes de entender o sistema produz auditoria ruim.

1. Leia o README, o manifesto de dependências e os documentos de arquitetura.
2. Mapeie a estrutura de diretórios e as camadas principais.
3. Veja o histórico recente de commits: o que muda com frequência é onde a dívida mora.
4. Liste os maiores arquivos por linhas e os mais modificados recentemente; a interseção costuma ser o alvo.
5. Escreva o modelo mental da arquitetura em 1 ou 2 parágrafos antes de seguir. Se ele contradiz o README, isso já é um achado.

### Fase 2: auditar as dimensões

Cite arquivo e linha em todo achado.

1. **Decaimento arquitetural** — dependências circulares, violação de camadas, arquivos e funções gigantes, lógica duplicada em 3+ lugares, abstração que ninguém usa, código morto.
2. **Apodrecimento de consistência** — vários jeitos de fazer a mesma coisa (erro, log, config, validação), nomes que derivaram, pastas que não refletem mais o que o código faz.
3. **Dívida de tipo e contrato** — tipo frouxo demais, fronteira de API sem tipo, falta de validação de schema nas fronteiras de confiança.
4. **Dívida de teste** — buracos em caminho crítico, teste que verifica implementação em vez de comportamento, teste pulado ou instável, arquivo de alta rotatividade sem teste.
5. **Dívida de dependência e configuração** — vulnerabilidade conhecida, dependência sem uso, duas dependências fazendo o mesmo trabalho, variável de ambiente referenciada e não documentada.
6. **Desempenho e higiene de recurso** — consulta N+1, trabalho síncrono em caminho assíncrono, I/O bloqueante em caminho quente, handle sem limpeza.
7. **Erro e observabilidade** — exceção engolida, catch genérico, erro logado e não tratado, ausência de log estruturado em caminho crítico.
8. **Higiene de segurança** — segredo no código, SQL por concatenação, falta de validação em fronteira, autenticação ou CORS permissivo, criptografia fraca.
9. **Deriva de documentação** — README que não corresponde ao código, comentário que contradiz o vizinho, API pública sem documentação.

### Fase 3: entregar

Relatório com esta estrutura:

- **Resumo executivo** — no máximo 10 bullets por impacto, com os números da varredura e onde a dívida se concentra.
- **Modelo mental da arquitetura** — como o sistema é de verdade.
- **Tabela de achados** — `ID | Categoria | Arquivo:Linha | Severidade | Esforço | Descrição | Recomendação`. Mire entre 30 e 80 achados; passar disso é ruído.
- **Top 5 "se não corrigir mais nada, corrija estes"** — com esboço concreto de mudança.
- **Ganhos rápidos** — esforço S com severidade média ou maior, em checklist.
- **Parece ruim mas está certo** — decisões que você considerou apontar e escolheu não apontar, com o motivo. **Seção obrigatória.** Se ficou vazia, você não olhou direito.
- **Perguntas abertas** — o que não deu para saber se é dívida ou intenção.

Idioma do relatório: o do usuário, por padrão.

### Modos

- **Repetição** — se o relatório já existe, leia antes: marque resolvidos, atualize os que envelheceram, marque os novos. O relatório vira documento vivo.
- **Incremento** — para revisar só o que mudou (PR grande, entrega de sprint), limite o escopo ao diff e diga no topo a referência usada.
- **Repositório grande** — acima de ~50 mil linhas, divida por módulo em paralelo e sintetize; declare o escopo restrito.

## Self-check antes de entregar

1. Todo achado tem arquivo e linha, conferidos depois de escritos?
2. A severidade se sustenta na rubrica, sem "crítico" por drama?
3. "Parece ruim mas está certo" tem pelo menos 3 itens reais?
4. Algum achado recomenda reescrever em vez de mudança específica?
5. Existe elogio de cortesia, enchimento ou categoria vazia sem "nada material"?
6. Nenhum valor de credencial foi copiado para o relatório?

## Limites

É auditoria estática, não pentest — pega higiene de segurança óbvia, não substitui teste de intrusão nem modelagem de ameaça. Não pega bug de regra de negócio, que exige conhecimento de domínio. E não distingue simplicidade intencional de acidental: quando não der para saber, pergunte em vez de afirmar.

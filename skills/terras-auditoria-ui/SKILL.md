---
name: terras-auditoria-ui
description: "Audita uma tela existente contra o próprio design system do produto, prova até 3 problemas visuais e escreve planos para outra execução, sem tocar no código. Use para revisar UI, drift de design ou handoff. Não aplica redesign (terras-redesign-existing-projects). UI audit."
keywords: [auditoria de ui, revisar interface, drift de design, design system, handoff de design, ui audit, improve ui, design review]
license: MIT
---

# Auditoria de UI por evidência

## Objetivo

Auditar uma superfície do produto contra o sistema que de fato a governa (DESIGN.md vigente, tokens, componentes, variantes) e entregar no máximo três problemas provados, cada um com uma única correção. O que o usuário escolher vira plano autocontido, que outra rodada executa. A identidade do produto fica: a auditoria corrige desvio do sistema, não troca gosto.

## Regra dura

1. **Só leitura no código do produto.** Arquivo novo só em `design-plans/`. Sem instalar dependência, formatar, commitar ou editar documentação de design. Vale mesmo com "pode mexer": primeiro a auditoria, depois o usuário escolhe.
2. **Achado sem as três provas não existe** (contrato, caminho de execução, correção única; ver passo 3). Repetição, busca por padrão ou "ficaria melhor" geram candidato, não achado.
3. **Escopo é apresentação visual**: token, cor, tipografia, espaçamento, layout, copy da interface, variante de componente, conformidade com regra de design escrita. Performance, acessibilidade, bug funcional, rota, dado, metadado e arquitetura ficam fora, mesmo quando óbvios. Liste-os numa linha em `Fora do escopo` com a skill certa (`terras-motion-performance`, `terras-accessibility`, `terras-tech-debt`) e não os corrija.
4. **Não invente intenção.** Se a evidência admite mais de uma correção (grade de 3 ou 4 colunas? o botão vira secundário ou some?), o candidato cai ou vira pergunta. Não crie primitivo, classe ou arquivo de layout novo só porque algo "está sem estilo".
5. **No máximo 3 achados.** Mais que isso é varredura, não auditoria.

## Como trabalhar

### 1. Escolher a superfície

Respeite o escopo pedido. Se for amplo, escolha uma aplicação e uma família de telas de uma tarefa principal, e diga qual. Comece pela rota e pelo layout e siga o caminho renderizado: composições, componentes compartilhados, variantes, tokens resolvidos, estilos.

Uma ligação só existe se for provada por renderização, import, prop, configuração resolvida, herança de CSS ou artefato gerado que a tela carrega. Nome parecido, token semelhante ou pasta vizinha não ligam nada. Outras aplicações, previews, legado e variantes enterprise ficam fora se não estão no caminho.

### 2. Reconstruir o sistema local

Procure `DESIGN.md`, guia do repositório e documentação local da superfície. Só use uma fonte depois de provar que é vigente e governa aquela tela; rascunho, proposta e migração descrevem intenção futura. Não ter documentação de design não é achado.

Registre:

```markdown
## Linguagem de design
- Superfície auditada:
- Fontes de design:
- Decisões documentadas:
- Donos e consumidores:
- Exceções explícitas:   (escreva "Nenhuma documentada" se nenhuma fonte citar)
```

### 3. Provar os achados

Antes, varra rótulos, estado ativo, ramos responsivos e variantes irmãs da superfície atrás de contradição interna. O resultado é lista de candidatos. Um candidato só fica com as três provas:

1. **Contrato** — decisão de design que obriga aquela propriedade naquele escopo, citada, ou contradição direta na apresentação dentro da mesma tarefa. "Prefira", "em geral", nomes, omissões e repetição não são contrato.
2. **Caminho** — o dono, valor ou comportamento citado chega à tela afetada pelo caminho traçado.
3. **Correção** — uma mudança exigida pela evidência, citando pelo nome o token, variante ou primitivo existente que ela usa.

O código-fonte prova violação de token, tipografia, cor, espaçamento, layout, copy, variante e responsivo. Hierarquia, densidade, clareza e coerência percebida exigem evidência renderizada ou de usuário; sem ela, não viram achado. Só use print ou navegador se o usuário fornecer ou pedir.

### 4. Tentar derrubar cada achado

Reabra cada fonte citada e apague o achado quando: o problema não bate com o código citado; a regra não governa aquela propriedade ou tela; há contraevidência de que a diferença é deliberada; cabe mais de uma correção; a correção inventa intenção; outro achado tem a mesma raiz.

### 5. Relatório

```markdown
## Linguagem de design
(bloco do passo 2)

## Achados
| # | Problema | Evidência | Mudança proposta | Escopo | Confiança |
| --- | --- | --- | --- | --- | --- |

## Melhorar primeiro
<o achado de maior alavancagem e por quê, ou "Nenhuma recomendação sustentada.">

## Fora do escopo
<uma linha por item notado que não é de design, com a skill indicada>
```

Ordene por confiança, impacto, alcance e custo; corte em três. Linha sem todas as colunas, inclusive Confiança, sai. Se nada sobreviver: "Nenhum achado sustentado." e "Nenhuma recomendação sustentada.".

Com achados, **pare e pergunte quais viram plano**. Se o usuário já escolheu um achado ou pediu plano para uma melhoria descrita, siga com esse escopo.

### 6. Planos

Leia `references/modelo-de-plano.md` e escreva um plano por mudança escolhida (não por sintoma) em `design-plans/<slug>.md`. Antes, reabra as fontes, registre o commit atual, nomeie primitivos e exemplos reutilizáveis e trace as telas afetadas. Plano existente se concilia, não se duplica.

O plano tem que se sustentar sozinho: quem executar não viu a auditoria nem a conversa. Executar o plano é outro pedido; se o usuário pedir na sequência, siga o plano à risca, incluindo `Validação` e `Condições de parada`.

## Referências

- `references/modelo-de-plano.md` — estrutura do plano de mudança (cadeia de evidência, reuso, mudanças, escopo, validação, condições de parada).
- `references/LICENSE-ui-skills.txt` — licença MIT do upstream.

## Fonte

Adaptada da skill `improve-ui` do repositório [ibelick/ui-skills](https://github.com/ibelick/ui-skills/tree/59193a7/skills/improve-ui) (MIT, © 2026 Julien Thibeaut; commit `59193a7`, de 25/10/2026). Mudanças da casa: português, seção `Fora do escopo` apontando para as skills vizinhas, e execução do plano permitida como pedido separado depois que o plano existe.

# Formato do arquivo de CV-base do Pitch por Vaga

O site <https://pitch.coderstudio.club> importa este arquivo em **Meu CV › Importar JSON**. Ele
também aceita o objeto `cv` sozinho, mas entregue sempre embrulhado:

```json
{ "tipo": "pitch-cv", "versao": 2, "cv": { ... } }
```

Exemplo completo e válido, com pessoa fictícia: `exemplos/cv-exemplo.json`.

## Campos de `cv`

| Campo | Tipo | Regra |
|---|---|---|
| `nome` | texto | nome completo, como está no CV |
| `titulo` | texto | título profissional curto, em inglês ("Back-end Developer \| Node.js and Cloud") |
| `contato` | texto | cidade, país e links (LinkedIn, GitHub, site) separados por ` · `. **Sem e-mail e sem telefone**: aparece no slide de capa, na tela compartilhada |
| `tagline` | texto | uma frase de fechamento, em inglês, primeira pessoa |
| `perfis` | lista | de 2 a 5 tipos de vaga que a pessoa pode disputar |
| `perfis[].id` | slug | minúsculas, dígitos e hífen, único |
| `perfis[].nome` | texto | nome do tipo de vaga ("Back-end Node.js") |
| `perfis[].foco` | texto | 1 ou 2 frases faladas, em inglês, citando stack e experiência reais do CV |
| `perfis[].skills` | lista | de 6 a 10 skills do CV mais relevantes para esse tipo de vaga, com o nome usual ("PostgreSQL", "CI/CD") para casar com a descrição da vaga |
| `perfis[].projetos` | lista | ids de 2 ou 3 projetos de `projetos` |
| `extras` | lista | outras skills do CV que não estão em nenhum perfil |
| `exp` | lista | até 6, mais recente primeiro: `{periodo, cargo, detalhe}`; `detalhe` = "Empresa · o que fazia" |
| `projetos` | lista | até 6: `{id, nome, curto, stack, fala}`; `stack` com ` · `; `fala` em 2 ou 3 frases: problema, o que eu fiz, resultado |
| `bullets.pitch` | lista | 3 frases curtas: o que a pessoa faz |
| `bullets.edu` | lista | formação e certificações, uma por item |
| `bullets.soft` | lista | idiomas, mentoria, comunidade, uma por item |
| `textos` | objeto | os 20 textos falados abaixo, todos obrigatórios |

## Os 20 textos (`textos`)

Tópicos da apresentação: `intro` (Who I am), `pitch` (What I do), `skills` (Skills for this role),
`exp` (Experience), `proj` (Selected projects), `why` (Why the company), `edu` (Education &
certifications), `soft` (Beyond code), `close` (Thank you).

Perguntas de entrevista: `q-about` (Tell me about yourself), `q-why-leave` (Why are you looking
for a new opportunity?), `q-strength` (Greatest strength), `q-weak` (Weakness you're working on),
`q-challenge` (Difficult technical challenge), `q-conflict` (Disagreement with a teammate or
client), `q-hire` (Why should we hire you?), `q-english` (Working in English), `q-salary` (Salary
expectations), `q-start` (When could you start?), `q-ask` (Questions for us).

## Variáveis que o site preenche por vaga

Escreva-as literalmente, com chave dupla. Outras variáveis não existem e aparecem cruas na tela.

| Variável | Vira |
|---|---|
| `{{nome}}` | `cv.nome` |
| `{{empresa}}`, `{{vaga}}` | empresa e cargo da vaga |
| `{{foco}}` | o `foco` do perfil escolhido na vaga |
| `{{skills}}` | as 5 skills do perfil que mais batem com a descrição da vaga |
| `{{projetos}}` | as `fala` dos projetos escolhidos na vaga |
| `{{motivo}}` | o "por que essa empresa" que a pessoa escreve na vaga |
| `{{salario}}`, `{{inicio}}` | pretensão e disponibilidade |
| `{{tagline}}` | `cv.tagline` |

Obrigatórias (o validador barra sem elas): `skills` contém `{{skills}}`; `proj` contém
`{{projetos}}`; `why` contém `{{empresa}}` e `{{motivo}}`; `q-salary` contém `{{salario}}`;
`q-start` contém `{{inicio}}`. Recomendadas: `{{foco}}` em `pitch` e `q-about`, `{{nome}}` em
`intro`.

## Texto falado

- Inglês natural, primeira pessoa, frases curtas, fácil de decorar para quem fala inglês B1 ou B2.
- Cada tópico cabe em 15 a 30 segundos falados (cerca de 130 palavras por minuto).
- Lacuna entre colchetes: `[result with a number]`, `[city]`. O site destaca em amarelo e a
  pessoa completa. Nunca troque uma lacuna por número ou fato inventado.
- `q-challenge` e `q-conflict` em STAR (situação, tarefa, ação, resultado) a partir de algo real
  do CV, com colchetes no que o CV não conta.

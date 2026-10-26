# Modelo de plano de mudança de design

Um arquivo por mudança escolhida, em `design-plans/<slug>.md`. Quem executar não tem o contexto da auditoria: tudo que ele precisa saber está aqui.

```markdown
# <Resultado esperado>

Escrito contra: <commit, ou "indisponível">

## Cadeia de evidência

- Superfície: `<caminho, rota ou estado renderizado>`
- Problema: <observação direta>
- Evidência de design: `<documentação, estilo, token, componente, padrão ou tela renderizada>`
- Dono: `<caminho ou superfície>`
- Escopo e telas afetadas: `<caminhos ou superfícies>`
- Incerteza: <nenhuma, ou o que precisa ser validado>

## Decisão de design

<A mudança no escopo certo e por que ela resolve a raiz do problema.>

## Reuso

- `<token, variável, componente, variante ou composição>`
- Exemplo no repositório: `<caminho>`

Se precisar de primitivo novo: diga por que o sistema atual não expressa a decisão, onde o primitivo mora e quais consumidores o compartilham.

## Mudanças

1. `<caminho exato ou superfície>`
   - Mudar: <comportamento ou estrutura pronta para implementar>
   - Preservar: <comportamento ou identidade que continua válida>
   - Verificar: <resultado observável>

## Escopo

- Herdam: <consumidores que recebem a mudança>
- Conferir: <consumidores que podem ser afetados>
- Excluir: <exceções válidas e trabalho não relacionado>

## Validação

- Produto: <tarefa e resultado esperado>
- Interface: <rotas, estados, extremos de conteúdo, interações e larguras de tela relevantes>
- Sistema: <reuso confirmado e nenhum padrão paralelo criado sem querer>
- Repositório: `<comando de checagem exato>` → <resultado esperado>

## Condições de parada

- Pare se <uma premissa central falhar, o dono mudar ou o escopo precisar crescer>.

## Documentação de design

- Depois de aceito e validado: <a decisão exata a registrar e onde, ou "nenhuma">
```

# Busca: pessoas da empresa e vagas em publicações

## Página People da empresa

`https://www.linkedin.com/company/<slug>/people/?<filtros>`

| Filtro | Exemplo | Uso |
|---|---|---|
| `facetCurrentFunction` | `12` (Recursos Humanos; testado). Outras funções: escolha na interface e copie o id da URL | função atual |
| `facetGeoRegion` | id numérico da região (copie da URL depois de escolher na interface) | onde a pessoa está |
| `keywords` | `talent`, `delivery`, `engineering manager` | cargo ou palavra do perfil |

A lista carrega por rolagem e pelo botão "Exibir mais resultados". Role até o fim antes de ler.
Uma página People com filtro substitui várias buscas soltas, o que ajuda a ficar longe do limite.

## Busca booleana em publicações (vagas)

`https://www.linkedin.com/search/results/content/?keywords=<expressão>&sortBy="date_posted"`

- Operadores em maiúsculo: `AND`, `OR`, `NOT`. Frase exata entre aspas.
- Um nível de parênteses funciona; parênteses aninhados falham sem avisar (volta resultado
  genérico).
- `sortBy="date_posted"` traz o mais novo primeiro; sem ele, o LinkedIn ordena por relevância e
  mistura posts de meses atrás.

Exemplo testado em 2026-10 (.NET remoto LATAM) e variações para testar:

```
".net" AND "remote" AND "latam"          # testado
("c#" OR ".net") AND "hiring" AND ("latam" OR "latin america") NOT "onsite"
"senior .net" AND ("contractor" OR "nearshore") AND "brazil"
```

Quem posta a vaga é candidato a conexão: abra o perfil e trate como qualquer pessoa da lista
(priorizar, aprovar, convidar).

## Limite

~11 buscas seguidas pausaram a pesquisa da conta (2026-10). Espace as buscas e pare se aparecer
aviso de uso.

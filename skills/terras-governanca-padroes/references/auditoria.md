# Protocolo de auditoria (modo AUDITAR)

## Autoridade das fontes

Em ordem decrescente — fonte mais alta vence; documento que contradiz fonte mais alta mente:

| Ordem | Fonte | O que revela | Tratamento |
|---|---|---|---|
| 1 | CI, lint, hooks | a lei de verdade (o que falha build) | é a regra vigente |
| 2 | Código (amostra) | prática de facto | candidata mais forte que qualquer doc |
| 3 | `git log` | estilo de commit, branch, escopo de PR | mede % de aderência antes de escrever "sempre" |
| 4 | CLAUDE.md, AGENTS.md, docs/ | intenção | confirmar em 1–2 antes de virar regra |
| 5 | Wiki, Notion, cabeça do time | memória | não é fonte; vira pergunta ao dono |

## Amostragem de código

- ~15 arquivos em pontos distintos: ponto de entrada, config, módulo mais velho, módulo mais novo, testes, scripts.
- O que observar: naming, estrutura de pastas, tratamento de erro, padrão de teste, imports, comentários recorrentes.
- Padrão presente na grande maioria dos pontos amostrados é de facto; presente pela metade é gosto pessoal — não é regra.

## Grade por candidata

Preencher uma linha por convenção candidata:

| Campo | Pergunta que responde |
|---|---|
| nome candidato | que pergunta ela resolve? (`git-flow-compliance`, não "padrões de git") |
| evidência | onde foi vista: arquivos, % do `git log`, qual job de CI |
| de facto? | o código confirma a intenção? |
| verificável | qual comando/CI/checklist detecta a violação? |
| ambiguidade | duas pessoas leriam igual? |
| conflitos | qual fonte diz o contrário? |
| decisão | publicar / confirmar com dono / descartar |

## Relatório (entregável)

Seções nesta ordem, curtas:

1. **Mapa de portadores** — saída do `scripts/auditar-fontes.sh` + leitura: o que está velho, o que falta.
2. **Vivas sem registro** — padrões de facto que nenhum arquivo carrega; cada um com evidência.
3. **Registros que mentem** — doc/regra que contradiz CI ou código; ação proposta (corrigir ou retirar).
4. **Conflitos abertos** — exigem decisão humana: quem decide, qual é a pergunta.
5. **Lacunas** — mesma decisão tomada de forma diferente em lugares diferentes (ainda sem padrão).
6. **Próximas ações** — priorizadas: mentiras primeiro, depois vivas-sem-registro, depois lacunas.

## Limites

- Não duplicar em prosa o que ferramenta já garante — referenciar em 1 linha.
- Não propor regra com "verificável" vazio: é preferência, não regra.
- Auditoria descreve o que **é**; mudar o que **deveria ser** é decisão do dono, registrada como proposta — nunca publicada direto como regra.

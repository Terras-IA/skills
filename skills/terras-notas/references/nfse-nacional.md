# Parser NFS-e Nacional — DANFSe v2.0 (`nfse-nacional-v1`)

Layout que a prefeitura passou a emitir em **outubro/2026** (primeiras notas
reais: NFS-e 26 e 27, ambas da 5G Educacional/ISOG). Substitui o layout
municipal antigo (`nfse-sjc-v1`), que continua suportado.

O `parse_nfse` escolhe o parser pelo conteúdo: se aparecer `DANFSe` ou
`CHAVE DE ACESSO DA NFS-e`, vai para o nacional; senão, para o municipal.

## Mapa de campos

| Campo | De onde vem |
|---|---|
| `chave_acesso` | 50 dígitos (a chave da NFS-e nacional é maior que os 44 da NF-e) |
| `numero` | linha abaixo de "NÚMERO DA NFS-e" (a mesma linha traz competência e emissão) |
| `competencia`, `emissao` | mesma linha (`30/09/2026`, `01/10/2026 15:12:45`) |
| `dps_numero`, `dps_serie` | linha abaixo de "SÉRIE DA DPS" — **não** é a série da nota |
| `emitente_*` / `tomador_*` | seções "EMITENTE DA NFS-e" e "TOMADOR / ADQUIRENTE", lidas **por coluna** |
| `tomador_email` | coluna "E-mail" do tomador (vem `-` quando não informado) |
| `valor_total` / `valor_liquido` | bloco "VALOR TOTAL DA NFS-e": 1º e 2º `R$` da linha de valores |
| `codigo_servico` | "Código de Tributação Nacional/Municipal" (ex.: `08.02.01`) |
| `descricao_servico` | linha seguinte ao rótulo "Descrição do Serviço" |

Como as células são alinhadas por espaços, `_colunas()` separa por 3+ espaços e
`_valor_apos_rotulo()` lê a coluna da(s) linha(s) seguinte(s) ao rótulo.

## Armadilha dos extratores (importante)

O **pdfplumber cola os espaços dos rótulos** neste layout:
"CHAVE DE ACESSO DA NFS-e" vira `CHAVEDEACESSODANFS-e`, e nada casa. O
`pdftotext -layout` extrai certo. Por isso `extrair_textos_pdf()` roda **os
dois** extratores e o `parse` fica com o resultado que reconhecer mais campos
(campo `extrator` no state registra qual venceu). Se um PDF futuro quebrar,
rode `pdftotext -layout arq.pdf -` e compare com
`python3 -c "import pdfplumber; ..."` antes de mexer nas regexes.

## Diferenças que afetam o envio

- Não há série da nota → `numero_serie` fica só com o número e o assunto sai
  "NFS-e 26 — Sousa Lima Informática" (os templates usam `{numero_serie}`).
- A competência vem como **data** (`30/09/2026`), não `MM/AAAA`.
- ISSQN aparece como "Não Retido" nestas notas (no layout antigo, o
  responsável era o prestador).

# Parser NFS-e — Prefeitura de São José dos Campos (`nfse-sjc-v1`)

Layout de referência: PDFs NF 85–87 (série E, 2026-09-21), emitidos pela
SOUSA LIMA INFORMATICA LTDA. Texto extraído com `pdfplumber` (layout=True) ou
`pdftotext -layout` — os dois preservam as colunas.

## Mapa de campos

| Campo | De onde vem |
|---|---|
| `numero`, `serie` | linha após o cabeçalho "Data e Hora de Emissão … Número / Série … Código de Verificação": regex `datahora  competência  (\d+) / (\w+)  código` |
| `emissao`, `competencia` | mesma linha (`21/09/2026 16:41:29`, `09/2026`) |
| `codigo_verificacao` | último token da mesma linha (`Zd391Wbfk`) |
| `emitente_*` | seção "EMITENTE DA NFS-e" até "TOMADOR": CNPJ por regex, nome nas linhas entre "Nome/Razão Social" e "Endereço:", e-mail por regex |
| `tomador_cnpj/nome/email` | seção "TOMADOR DO SERVIÇO" até "DESCRIÇÃO DO SERVIÇO", mesma técnica |
| `valor_servico` | linha abaixo de "Valor Serviço (R$)" no bloco CÁLCULO DO ISSQN |
| `retencoes`, `descontos`, `valor_liquido` | bloco "VALOR TOTAL DA NOTA": 4 números na linha (base, retenções, descontos, líquido) |
| `nota_substituida` | "Número da nota fiscal substituida:" quando preenchido (série E = nota substituta) |

## Regras de extração

- **Nome multilinha**: entre o rótulo ("Nome/Nome" / "Nome/Razão Social") e
  "Endereço:", tudo é nome — o e-mail pode estar na mesma linha (coluna
  direita) ou na de baixo; o parser remove o e-mail e junta o resto.
- **Seções por âncora**, não por posição: `_secao()` fatia o texto entre dois
  rótulos; nomes/valores são procurados dentro do fatia. Quebra de linha ou
  espaçamento diferente não derruba.
- **Valores com `*****`**: campos não aplicáveis aparecem como `*****`
  (ex.: base de cálculo no Simples) — as regexes só pegam `[\d.,]+`.
- Campos críticos ausentes (numero, tomador_nome, valor_total) geram aviso
  no `parse` — a nota entra no state mas aparece como "revisar manualmente".

## Outras cidades / layouts

O parser é específico do layout de SJC. Nota de outra prefeitura tende a
falhar em `numero`/`tomador_nome` e cair no aviso. Nesses casos:
1. `pdftotext -layout arquivo.pdf -` para inspecionar o texto;
2. ajuste as âncoras/regex aqui ou crie `nfse-<cidade>-v1` seguindo este
   mesmo molde, escolhendo pelo campo `parser` gravado no state;
3. enquanto não houver parser, o envio manual continua valendo (o fluxo
   `fetch`/`depara` é independente do parser).

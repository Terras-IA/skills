# Configuração

Diretório: `~/.config/terras-linkedin-alvos/` (crie se não existir). Fica fora do plugin para
sobreviver a atualizações e não ser distribuído junto.

## alvos.json

```json
{
  "janela_horas": 24,
  "curtir_automatico": false,
  "curtir_automatico_ativado_em": null,
  "foco": "vagas de arquitetura de software .NET/Azure, remoto",
  "alvos": [
    {
      "url": "https://www.linkedin.com/in/<slug>/",
      "nome": "Nome Sobrenome",
      "papel": "gestor",
      "empresa": "Empresa X",
      "nota": "diretor de engenharia da área de cloud"
    }
  ]
}
```

- `papel`: `executivo` | `gestor` | `recrutador` | `par`.
- `incluir_reposts` (opcional, por alvo): `true` para alvos que só compartilham. O comentário vai no
  post original que ele compartilhou; na tabela de aprovação, indique o autor original.
- `curtir_automatico`: só vira `true` quando o usuário pedir explicitamente curtidas sem aprovação
  nas rodadas agendadas. Grave a data em `curtir_automatico_ativado_em` e diga como desligar.
- `foco`: o tipo de vaga ou posicionamento; orienta o ângulo dos comentários.
- URL: normalize para `https://www.linkedin.com/in/<slug>/` (sem query string). Se o usuário der só o
  nome, abra `https://www.linkedin.com/search/results/people/?keywords=<nome+empresa>`, leia os
  primeiros resultados com `get_page_text` e mostre os candidatos (nome, título, empresa, URL) para
  ele escolher antes de gravar (homônimos são comuns).

## engajados.json

Um objeto indexado pelo URN do post:

```json
{
  "urn:li:activity:7000000000000000000": {
    "alvo": "https://www.linkedin.com/in/<slug>/",
    "publicado": "2026-09-28T15:37:00Z",
    "curtido_em": "2026-09-29T12:10:00Z",
    "comentado_em": "2026-09-29T12:11:00Z",
    "comentario": "texto publicado"
  }
}
```

Grave logo depois de cada ação confirmada, não no fim da rodada: se a rodada cair no meio, o arquivo
mostra exatamente o que já foi feito.

## rascunhos/

`AAAA-MM-DD-HHh.json` com a lista proposta da rodada (urn, alvo, trecho do post, comentário, curtir)
e um campo `status` por item: `proposto` → `aprovado` (após o "aprovado" do usuário) → `feito` ou
`pulado`. Serve para retomar a aprovação numa sessão agendada e para continuar uma rodada
interrompida sem pedir aprovação de novo para o que já foi aprovado.

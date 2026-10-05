---
name: terras-pauta-mercado
description: "Transforma referência externa (repo, post, anúncio, paper) na análise mercado × TerrasIA com cobre/rejeita/falta e recibo, e no pacote de posts por canal (Company Page, LinkedIn pessoal, canal WhatsApp e Substack). Use quando mandarem um link para virar análise ou post, perguntarem o que o TerrasIA já cobre de algo, ou pedirem pauta de mercado ou comparação com concorrente. Market-vs-product content pipeline."
keywords: [pauta, mercado, análise de mercado, comparação, concorrente, referência, cobertura, cobre, rejeita, falta, recibo, post, linkedin, whatsapp, substack]
---

# Pauta de mercado: da referência externa ao pacote de posts

## Objetivo

Receber uma referência externa (repositório, post, anúncio, paper, release) e devolver três coisas: a **análise** no formato de casa (o que a referência é, mais o cruzamento *cobre / rejeita de propósito / falta* com recibo por linha), o **pacote de posts** para os canais da operação, e o **registro** do material no repositório do projeto.

É o formato preferido do dono ("link externo × o que o TerrasIA já cobre") e já rodou para os quatro frameworks de gestão e para o OpenDots da CopilotKit. O valor não está no resumo da referência: está no cruzamento com recibo e nas escolhas que o projeto tomou e o outro não.

## Regra dura

1. **Fonte primária, ao vivo, datada.** Nunca escrever a partir do intermediário que trouxe o assunto. Post de terceiro distorce: um post sobre um paper inventou modelos e números que o paper não tinha, e a correção veio de ler a fonte direto. Antes de publicar, releia a fonte e reconfirme número, data e citação (repositório vive mudando, README muda, estrela muda); toda citação de terceiro entra datada ("README lido em AAAA-MM-DD").
2. **Recibo por afirmação.** Cada veredito aponta a prova: módulo do motor, medição registrada, trecho datado da fonte. Sem recibo, o item vira hipótese marcada, nunca afirmação.
3. **Guardrail de claims.** Proibido prometer bloqueio absoluto, "nenhum dado sai da empresa" e "pronto pra produção". O que existe de verdade e pode ser dito: medição por chamada, aprovação com evidência, auditoria e avaliação com régua. O guardrail completo está em `references/formato-da-analise.md`.
4. **Publicar é passo separado.** Escrever e publicar não são o mesmo pedido. LinkedIn é manual (entregar pronto para colar); o canal WhatsApp publica pela skill `terras-canal-whatsapp` e só com pedido explícito; a Substack usa `terras-substack`, com rascunho primeiro e publicação só sob pedido.

## Como trabalhar

1. **Ler a fonte inteira e datar.** Repositório: README completo e metadados (estrelas, licença, criação, último push). Anúncio ou documento: o texto integral. Se a fonte não abre, diga isso e reduza o tom da análise; não escreva do resumo de terceiro.
2. **Guardar a leitura como ficha** no repositório do projeto (`docs/new-features/REFERENCIA-<fonte>-<data>.md` para sistema externo, `docs/pesquisas/` para mercado): o que é, arquitetura, aderência ao motor, o que vale imitar, o que não imitar, rastreabilidade da leitura. A ficha é o recibo da análise.
3. **Montar o cruzamento.** Item a item: *cobre* (com o módulo do motor), *rejeita de propósito* (com o motivo da aposta), *falta* (com dono e estado). Marque o que é interno e o que pode circular.
4. **Escolher o ângulo** (o que a comparação ensina, não o que a referência lista) e escrever as peças por canal seguindo `references/canais-e-pecas.md` e as réguas da `terras-linkedin`: banda de 1.300 a 1.500 com hashtags, gancho em pé no corte de ~210, até 3 hashtags, zero travessão, zero emoji. **Confira a contagem por script antes de fechar**; número sai do texto, nunca da estimativa.
5. **Gerar as imagens** na identidade do projeto: banner 1200×628 para os posts de LinkedIn e card 1080×1080 para o canal. Fonte HTML ao lado do PNG (mesma pasta, `assets/<tema>-<data>/`), render por navegador headless com `--disable-lcd-text` (sem isso sai franja de subpixel no texto) e inspeção do PNG final: gate visual quando houver; sem ele, inspeção própria registrada.
6. **Registrar o pacote** em `docs/comercial/POST-<tema>-<AAAA-MM-DD>.md` do projeto: fonte reverificada, checagem mecânica (contagens, travessão), textos em bloco de código prontos para colar, tabela de imagens, regras aplicadas e status de publicação. Template em `references/formato-da-analise.md`.
7. **Publicar o que foi pedido** e registrar os ids: WhatsApp pelo script da `terras-canal-whatsapp` (`--checar`, mostrar, `--yes` no pedido); LinkedIn e Substack ficam prontos para o dono colar.

## Onde está instalada

Fonte única: `skills/terras-pauta-mercado/` no repositório `terrasia-skills` (link simbólico criado pelo `scripts/instalar.sh`). Peças irmãs: `terras-linkedin` (régua de texto), `terras-canal-whatsapp` (publicação no canal), `terras-substack` (artigo) e `terras-banner` (quando o desenho pedir banner de verdade). O registro vive no repositório do projeto terrasia, em `docs/comercial/`, `docs/new-features/` e `docs/pesquisas/`.

## Referências

- `references/formato-da-analise.md` — templates da ficha e do registro de post, guardrail de claims completo e régua de exposição de defeito.
- `references/canais-e-pecas.md` — destino, voz, tamanho e rota de publicação de cada canal; regras do canal WhatsApp; padrão dos assets.

## Exemplos de uso

- "olha esse repo, o que o TerrasIA cobre disso?" → ficha + análise + pacote de posts.
- "esse post sobre agentes vale uma comparação?" → achar e ler a fonte primária por trás, responder, e só então oferecer o pacote.
- "faz o pacote de posts da análise de ontem" → passos 4 a 7.

---
name: terrasia-post-empresa
description: "Produz a peça da Company Page do TerrasIA: o post na voz de produto e a imagem na identidade da marca, com aceite de leitura no celular. Traz a régua de texto da página (banda de 1.300 a 1.500, gancho no corte de ~210, link no primeiro comentário, humanizer aplicado), os templates das duas peças (banner 1200x628 e card 1080x1350), o script de render e medição de vãos, os tamanhos mínimos aprendidos em px e o checklist de publicação. Use quando o pedido for post da empresa, LinkedIn da empresa, Company Page, peça ou imagem de marca, ou fechar a publicação de uma análise. A análise de referência e o pacote por canal são da skill irmã terras-pauta-mercado."
keywords: [post da empresa, linkedin da empresa, company page, peca da empresa, imagem da empresa, banner da empresa, card, identidade do produto, publicacao, marca, terrasia]
version: 1.0.0
license: MIT
---

# Peça da Company Page do TerrasIA

## Onde está instalada

Fonte única: `skills/terrasia-post-empresa/` no repositório `terrasia-skills`. Cada agente enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh`; a edição se faz aqui e vale para todos. Abaixo, `$SKILL_DIR` é a pasta desta skill.

## Descrição

Produz a peça da página da empresa a partir de um material que já existe (a análise da `terras-pauta-mercado` ou um marco interno): o post na voz de produto com o humanizer aplicado e a imagem na identidade do produto, com aceite de leitura no celular.

A ênfase desta skill é a **produção da peça visual**, que é onde o caso real de 2026-10-05 custou iterações: templates com a geometria aprovada, tamanhos mínimos medidos, verificação de colisão por script e o preview de celular como teste final. A divisão com a skill irmã: `terras-pauta-mercado` faz a análise (cobre, rejeita de propósito, falta, cada veredito com recibo) e o pacote por canal; esta produz a peça da Company Page.

## Quando usar

- O material da análise está pronto (ou uma entrega interna vira anúncio) e falta a peça: post + imagem da página.
- O pedido menciona Company Page, LinkedIn da empresa, peça ou imagem de marca na identidade do produto.
- Chegou um link de mercado: comece pela `terras-pauta-mercado` (análise e pacote por canal) e volte aqui para a peça da página.

## Onde fica cada coisa (o que NÃO é esta skill)

| Assunto | Skill / lugar |
| --- | --- |
| Post do LinkedIn **pessoal** (voz de fundador, primeira pessoa) | `terras-linkedin` |
| Imagem do canal pessoal (marca pessoal, Inter, diretório `terras-brand`) | `terras-banner` |
| Comentário em post de terceiro | `terras-comentarios` |
| Digest de notícias | `terras-noticias` |
| Medição do canal pessoal | `terras-linkedin-metricas` |
| Análise da referência (cobre, rejeita, falta, com recibo) e pacote por canal | `terras-pauta-mercado` |
| Publicação no canal WhatsApp | `terras-canal-whatsapp` |
| **Esta skill** | Peça da **Company Page** (`linkedin.com/company/terrasia`, página no ar desde 2026-10-05), voz de produto/marca, identidade do **produto** (`terrasia-site/identidade/`) |

Kit da página (nome, tagline, descrição, capa, logo): `docs/comercial/EMPRESA-LINKEDIN-2026-10-03.md` no repo `terrasia`.

## De onde vem o conteúdo

A análise que origina a peça é da `terras-pauta-mercado`: a referência entra, três vereditos saem (cobre, rejeita de propósito, falta), cada um com recibo, e a análise mora em `docs/comercial/PAUTA-<TEMA>-<DATA>.md`. Marco interno (skill nova, release, medição) vale como origem direta. Exemplo completo: `PAUTA-FRAMEWORKS-GESTAO-2026-10-05.md`.

## O post

Voz da página: produto/marca, terceira pessoa, "IA que se explica" (o modelo propõe, a pessoa aprova, tudo auditável). Não é a voz de fundador do canal pessoal.

Regras duras:

- 1.300 a 1.500 caracteres com hashtags; o gancho fecha sozinho nos ~210 primeiros (corte do "ver mais").
- Zero travessão, zero emoji, no máximo 3 hashtags; link **só no primeiro comentário**.
- Humanizer passa: sem contraste "não é X, é Y" de enfeite, sem fecho de uma linha, sem trio por hábito, sem jargão de venda.
- Estrutura que funciona nesta página: os vereditos em blocos curtos (um por framework/item), a virada comercial (o que diferencia não é conhecer o framework, é executá-lo com evidência e governança) e pergunta real no fim.
- Não publica: quem publica é o dono.

Entregue o post em texto puro no chat **e** em `docs/comercial/POST-LINKEDIN-EMPRESA-<SLUG>-<DATA>.md`, junto com: primeiro comentário (texto com o link), alt text da imagem e checklist de publicação.

## A imagem

Uma peça por post (usar o feed ou o card, não os dois). O aceite é a **leitura no celular**: no feed a imagem renderiza a um terço do tamanho; texto que só lê ampliado não passa.

| Peça | Tamanho | Uso |
| --- | --- | --- |
| Banner de feed | 1200x628 | imagem única do post; o título domina |
| Card em pé | 1080x1350 | mais texto com corpo grande; formato salvável |

### Identidade do produto (não a marca pessoal)

Diretório canônico: `terrasia-site/identidade/` (tokens, ativos, guia). O essencial:

| Papel | HEX | Uso |
| --- | --- | --- |
| base | `#060a12` | fundo da peça escura |
| acento | `#22d3ee` | único destaque (ciano chapado, sem gradiente) |
| texto | `#e8edf2` | texto principal |
| apoio | `#94a3b8` | texto secundário e rótulos apagados |
| linha | `#1a2433` | filetes e divisores |
| papel / tinta | `#f7f9fa` / `#0c121a` | tema claro (opcional) |

- Fontes: Ubuntu Sans (títulos, instalada no sistema) + JetBrains Mono (rótulos técnicos; woff2 em `~/Documents/Diversos/terras-brand/fonts/`).
- Marca: lockup em `terrasia-site/identidade/ativos/logo-claro.png` (fundo escuro).
- Motivo assinatura: o grafo de quatro nós em zigue-zague (mesmo traçado do ícone), nós em dois tons (`#0e7490` nos primeiros, `#22d3ee` nos últimos); serve de régua visual dos vereditos.
- Fechamento: assinatura `terrasia.app` com a linha de quatro pontos. Cantos retos, muito espaço negativo.
- O tema padrão da página é o escuro; o claro é opção.

### Render e aceite

```bash
python3 "$SKILL_DIR/scripts/peca.py" render peca.html --saida banner-feed --tamanho 1200x628
```

O script renderiza no Chrome headless em 2x com `--disable-lcd-text` (no Linux o Chrome desenha franja de subcor sem a flag), reduz para o tamanho exato, grava o `@2x` e o preview na largura do celular (356 no feed, 380 no card).

Tamanhos mínimos aprendidos (px no tamanho real da peça, medidos no caso real):

| Elemento | Banner 1200x628 | Card 1080x1350 |
| --- | --- | --- |
| Título | ≥ 76 | ≥ 74 |
| Nome do item | ≥ 30 | ≥ 44 |
| Veredito / chip | ≥ 24 | ≥ 22 |
| Linha de prova | (evitar) | ≥ 29 |

- Menos texto, corpo maior, sempre. A linha de apoio em mono competindo com o título foi removida na segunda rodada do caso real.
- Colisão se mede, não se olha: `python3 "$SKILL_DIR/scripts/peca.py" bandas <png>@2x.png --regiao x0,x1,y0,y1` lista as faixas de texto e o vão entre elas. Assinatura precisa de faixa reservada (margem inferior no bloco do grafo, no banner; foi a colisão real de 2026-10-05).
- Aceite: despache o juiz visual quando ele estiver disponível; indisponível, inspeção direta + medição + os previews mobile como evidência. Os `preview-mobile-*.png` vão junto da peça (commitados).
- Guarde por post: `docs/comercial/assets/<slug>-<data>/` com o HTML fonte, o PNG exato, o `@2x` e os previews.

## Publicação e medição

1. Validar o estado citado no post: o que ele afirma (skill, release, número) existe mesmo.
2. Publicar na página (o dono), com uma imagem, e colar o primeiro comentário com o link.
3. Responder comentários nas primeiras horas.
4. Coletar métricas em 48h e 7 dias **no painel da página** (a `terras-linkedin-metricas` cobre o canal pessoal; a de página ainda não): impressões, na rede × fora da rede, salvamentos, comentários.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Espelhar a voz pessoal na página | voz de produto: "o modelo propõe, a pessoa aprova, tudo auditável" |
| Texto pequeno na arte | o teste é o preview na largura do celular, não o zoom no computador |
| Publicar com as duas imagens | uma peça por post |
| Usar `terras-banner` para peça da empresa | a identidade do produto é `terrasia-site/identidade/` |
| Publicar por conta própria | quem publica é o dono |

## Exemplo real (origem desta skill)

Referência "4 frameworks" (post de terceiro) em 2026-10-05: SIPOC coberto (recibo: `terras-mapeamento-de-processos`), GUT e SWOT criados na hora (`terras-matriz-gut`, `terras-analise-swot`) e Balanced Scorecard recusado com justificativa. Peça final: `docs/comercial/POST-LINKEDIN-EMPRESA-FRAMEWORKS-2026-10-05.md` + `docs/comercial/assets/frameworks-2026-10-05/`.

## Arquivos

- `templates/peca-feed.html` — banner 1200x628: título + grafo de quatro nós com vereditos + assinatura. É um exemplo real aprovado; troque os textos mantendo a densidade.
- `templates/peca-card.html` — card 1080x1350: título + itens numerados com chip e prova.
- `scripts/peca.py` — `render` (@2x, versão exata e preview de celular) e `bandas` (faixas de texto e vãos, para provar que nada colide).

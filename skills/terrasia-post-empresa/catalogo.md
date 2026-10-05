---
name: terrasia-post-empresa
version: 1.0.0
access: free
category: conteudo
description: Produz a peça da Company Page do TerrasIA: post na voz de produto (banda de 1.300 a 1.500, gancho no corte de ~210, link no primeiro comentário) e imagem na identidade do produto, com templates, script de render e checklist de publicação.
keywords: [post da empresa, linkedin da empresa, company page, peca da empresa, imagem da empresa, identidade do produto, publicacao, banner]
---

# Peça da Company Page do TerrasIA

## Descrição

Produz a peça da página da empresa a partir de um material que já existe (a análise de uma referência de mercado ou um marco interno): o post na voz de produto com as marcas de IA removidas e a imagem na identidade do produto, com aceite de leitura no celular.

A ênfase é a **produção da peça visual**: templates com a geometria aprovada, tamanhos mínimos medidos, verificação de colisão por script e o preview de celular como teste final.

| Assunto | Onde fica |
| --- | --- |
| Post do LinkedIn **pessoal** (voz de fundador) | skill de post pessoal |
| Imagem do canal pessoal (marca pessoal) | skill de banner |
| **Esta skill** | Peça da **Company Page** (`linkedin.com/company/terrasia`), voz de produto/marca, identidade do **produto** (`terrasia-site/identidade/`) |

## O post

Voz da página: produto/marca, terceira pessoa, "IA que se explica" (o modelo propõe, a pessoa aprova, tudo auditável). Não é a voz de fundador do canal pessoal.

Regras duras:

- 1.300 a 1.500 caracteres com hashtags; o gancho fecha sozinho nos ~210 primeiros (corte do "ver mais").
- Zero travessão, zero emoji, no máximo 3 hashtags; link **só no primeiro comentário**.
- Sem contraste "não é X, é Y" de enfeite, sem fecho de uma linha, sem trio por hábito, sem jargão de venda.
- Estrutura que funciona nesta página: os vereditos ou argumentos em blocos curtos, a virada comercial (o que diferencia é a execução com evidência e governança) e pergunta real no fim.
- Não publica: quem publica é o dono.

Entregue o post em texto puro no chat **e** em um documento com: post, primeiro comentário (com o link), alt text da imagem e checklist de publicação.

## A imagem

Uma peça por post. O aceite é a **leitura no celular**: no feed a imagem renderiza a um terço do tamanho; texto que só lê ampliado não passa.

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

- Fontes: Ubuntu Sans (títulos) + JetBrains Mono (rótulos técnicos).
- Marca: lockup em `terrasia-site/identidade/ativos/logo-claro.png` (fundo escuro).
- Motivo assinatura: o grafo de quatro nós em zigue-zague, em dois tons; serve de régua visual dos vereditos.
- Fechamento: assinatura `terrasia.app` com a linha de quatro pontos. Cantos retos, muito espaço negativo.

### Render e aceite

```bash
python3 "$SKILL_DIR/scripts/peca.py" render peca.html --saida banner-feed --tamanho 1200x628
```

O script renderiza no Chrome headless em 2x com `--disable-lcd-text` (no Linux o Chrome desenha franja de subcor sem a flag), reduz para o tamanho exato, grava o `@2x` e o preview na largura do celular (356 no feed, 380 no card).

Tamanhos mínimos aprendidos (px no tamanho real da peça, medidos em caso real):

| Elemento | Banner 1200x628 | Card 1080x1350 |
| --- | --- | --- |
| Título | ≥ 76 | ≥ 74 |
| Nome do item | ≥ 30 | ≥ 44 |
| Veredito / chip | ≥ 24 | ≥ 22 |
| Linha de prova | (evitar) | ≥ 29 |

- Menos texto, corpo maior, sempre.
- Colisão se mede: `python3 "$SKILL_DIR/scripts/peca.py" bandas <png>@2x.png --regiao x0,x1,y0,y1` lista as faixas de texto e o vão entre elas. A assinatura precisa de faixa reservada.
- Aceite: inspeção da peça final + preview de celular como evidência, guardados junto da peça.

## Publicação e medição

1. Validar o estado citado no post: o que ele afirma (skill, release, número) existe mesmo.
2. Publicar na página (o dono), com uma imagem, e colar o primeiro comentário com o link.
3. Responder comentários nas primeiras horas.
4. Coletar métricas em 48h e 7 dias no painel da página: impressões, na rede × fora da rede, salvamentos, comentários.

## Erros comuns

| Erro | Correção |
| --- | --- |
| Espelhar a voz pessoal na página | voz de produto: "o modelo propõe, a pessoa aprova, tudo auditável" |
| Texto pequeno na arte | o teste é o preview na largura do celular, não o zoom no computador |
| Publicar com as duas imagens | uma peça por post |
| Usar a skill de banner pessoal para peça da empresa | a identidade do produto é `terrasia-site/identidade/` |
| Publicar por conta própria | quem publica é o dono |

## Arquivos

- `templates/peca-feed.html` — banner 1200x628: título + grafo de quatro nós com vereditos + assinatura. Exemplo real aprovado; troque os textos mantendo a densidade.
- `templates/peca-card.html` — card 1080x1350: título + itens numerados com chip e prova.
- `scripts/peca.py` — `render` (@2x, versão exata e preview de celular) e `bandas` (faixas de texto e vãos, para provar que nada colide).

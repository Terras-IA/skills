# Canais e peças

Um pacote completo tem até quatro peças. Nem toda pauta merece as quatro: o dono diz os destinos, e o default razoável é Company Page + canal WhatsApp.

| Canal | Voz | Tamanho e formato | Rota de publicação |
|---|---|---|---|
| LinkedIn Company Page | produto/marca, tom comercial | banda 1.300 a 1.500 com hashtags; gancho em pé no corte de ~210; até 3 hashtags; zero emoji; link fora do corpo (primeiro comentário) | manual: entregar pronto para colar; comentário padrão do site logo depois |
| LinkedIn pessoal (dono) | fundador, primeira pessoa; continuidade de série quando houver | mesma banda e regras da Company | manual |
| Canal WhatsApp | direto, informal, frases curtas | legenda de até 1.024 caracteres quando tem imagem; `*negrito*` com um asterisco; bullets com "•" | pela skill `terras-canal-whatsapp`: `--checar`, mostrar ao dono, `--yes` no pedido explícito |
| Substack | ensaio, mais longo | artigo com título e subtítulo; sem banda fixa; ~700 a 1.100 palavras costuma bastar | pela skill `terras-substack`: rascunho primeiro, publicar só sob pedido |

## Regras de texto (herdadas da terras-linkedin)

- Zero travessão (em dash) em qualquer peça: é a marca mais identificável de texto de IA.
- Gancho: os primeiros ~210 caracteres precisam fazer sentido sozinhos (o "ver mais" corta ali).
- Contagem de caracteres por script antes de fechar. Bandas: long 1.300 a 1.500 com hashtags; versão curta, quando pedida, alvo 700.
- Citações de terceiro: datadas; termo deles em inglês fica em inglês entre aspas.
- A peça interna da análise pode ser mais dura; a peça pública não expõe julgamento estratégico nem caminho de arquivo do motor.

## Assets padrão

| Peça | Tamanho | Uso |
|---|---|---|
| Banner de feed | 1200×628 | imagem dos posts de LinkedIn |
| Card em quadrado | 1080×1080 | imagem do post do canal WhatsApp |

Na identidade do projeto (cores, fontes e logo da marca em `identidade/` do site). Fonte HTML ao lado do PNG, na mesma pasta `assets/<tema>-<data>/`. Render por navegador headless com `--disable-lcd-text`; inspecionar o PNG final antes de publicar (gate visual quando disponível; sem ele, inspeção própria registrada no pacote).

## Peças que não são post

- **Texto de apresentação do projeto** (uma linha, curta, média) pedido para mensagem, bio ou e-mail: usar a descrição já publicada nos canais como base, para a voz bater entre site, página e mensagem.
- **Ficha interna** (`references/formato-da-analise.md`): fica no repositório do projeto, não vira post por si.

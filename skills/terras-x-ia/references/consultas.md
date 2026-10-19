# Consultas prontas para a busca do X

Monte a URL assim (aba "Top" = `f=top`; aba "Mais recentes" = `f=live`):

```
https://x.com/search?q=<consulta url-encoded>&src=typed_query&f=top
```

Sempre acrescente `since:AAAA-MM-DD` (hoje menos a janela) e `-filter:replies`. `min_faves:N` corta ruído: 200 para termos amplos em inglês, 30 a 50 para português ou nicho. Para encodar, `python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "consulta"`.

## Pacote padrão "IA" (varredura geral)

| # | Foco | Consulta |
|---|------|----------|
| 1 | Lançamento de modelo | `(launch OR released OR introducing) (model OR LLM OR "open weights") min_faves:300 lang:en -filter:replies` |
| 2 | Agentes | `("AI agents" OR "agentic" OR "coding agent") min_faves:200 lang:en -filter:replies` |
| 3 | Laboratórios | `(from:OpenAI OR from:AnthropicAI OR from:GoogleDeepMind OR from:GoogleAI OR from:MetaAI OR from:MistralAI OR from:xai OR from:NVIDIAAI OR from:huggingface) -filter:replies` |
| 4 | Papers | `(arxiv.org OR "new paper" OR "our paper") (LLM OR agents OR reasoning) min_faves:100 lang:en` |
| 5 | Ferramenta de dev | `(MCP OR "claude code" OR Codex OR Cursor OR Copilot) min_faves:150 lang:en -filter:replies` |
| 6 | Brasil | `("inteligência artificial" OR "IA generativa" OR "agentes de IA" OR LLM) lang:pt min_faves:30 -filter:replies` |

## Contas que costumam trazer fonte primária

Pesquisadores e quem publica changelog: `from:karpathy`, `from:simonw`, `from:swyx`, `from:_akhaliq` (papers), `from:hwchase17`, `from:jeremyphoward`, `from:emollick`, `from:ylecun`, `from:sama`, `from:OfficialLoganK`, `from:alexalbert__`. Use em grupos de 4 a 6 com `OR`; consulta longa demais a busca ignora.

## Tema livre

Troque o miolo e mantenha os filtros. Exemplo para "agentes de código":

```
("coding agent" OR "claude code" OR Codex OR "Cursor agent") since:2026-10-11 min_faves:100 lang:en -filter:replies
```

Uma consulta em inglês e uma em português cobrem quase tudo. Três a seis consultas por varredura bastam; mais que isso repete os mesmos posts.

A busca do X ignora maiúsculas; os nomes de produto ficam em minúsculas aqui de propósito.

## Operadores úteis

`from:` `to:` `since:` `until:` `min_faves:` `min_retweets:` `min_replies:` `lang:` `filter:links` `filter:media` `-filter:replies` `url:dominio.com` `"frase exata"` `(A OR B)` `-palavra`.

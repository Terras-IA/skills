---
name: terras-last30days
version: "3.25.0"
description: "Pesquisa o que se falou sobre um tema nos últimos 30 dias em Reddit, X, YouTube, Hacker News, Polymarket, GitHub e web, com motor local vendorizado. Use quando o pedido for descobrir pauta, medir se um assunto está circulando, checar o que a comunidade está discutindo ou comparar dois temas antes de escrever um post. Descoberta, não fonte: o resultado orienta, a verificação vem da fonte primária. last30days, trending topics, o que estão falando, pesquisa de pauta."
keywords: [last30days, pesquisa de pauta, trending, reddit, hacker news, youtube, x, sentimento, descoberta, tópicos recentes]
---

# Pesquisa dos últimos 30 dias (last30days)

## Objetivo

Descobrir o que circulou sobre um tema nos últimos 30 dias: posts, engajamento e discussão em Reddit, X, YouTube, Hacker News, Polymarket, GitHub e web. Serve para responder três perguntas antes de escrever: esse assunto está vivo, onde a conversa acontece, e qual é o ângulo que ninguém cobriu.

Motor local: o engine em Python busca, pontua e agrupa as evidências; o agente que hospeda lê o resultado e escreve a síntese.

## Regra dura: descoberta, não fonte

O relatório mostra o que as pessoas dizem, não o que é verdade. **Nunca cite o resultado como fonte de um fato em texto publicado.** Antes de escrever qualquer post, confira versão, data e detalhe na fonte primária (changelog, release notes, documentação oficial). Data errada derruba a credibilidade do post inteiro.

Para posts, o fluxo é: esta skill acha a pauta, a fonte primária confirma o fato, e a `terras-linkedin` escreve.

## Onde está instalada

Canônica em `~/.zcode/skills/terras-last30days/`, com link simbólico em `~/.claude/skills/` e `~/.config/opencode/skills/` (mesmo padrão das outras terras-).

Conteúdo: `scripts/` com o engine vendorizado (upstream `mvanhorn/last30days-skill` v3.25.0, MIT), `references/save-html-brief.md` e `references/upstream-skill.md` com o protocolo completo do autor. O runtime ocupa ~3 MB, sem a pasta de assets de demonstração.

`SKILL_DIR` é sempre `~/.zcode/skills/terras-last30days`. O passo de "stale-clone self-check" do documento upstream não se aplica aqui.

## Requisitos

- **Python 3.12 ou maior.** Esta máquina tem 3.14.4, atende. Se um dia faltar, o engine tenta provisionar um Python via `uv`; sem `uv`, ele para com uma mensagem de erro, e não há o que improvisar.
- **Nenhuma chave de API é obrigatória.** O piso gratuito cobre Reddit (com comentários e votos), Hacker News, Polymarket, GitHub e web.
- Opcionais que ampliam o alcance, por fonte: `yt-dlp` no PATH liga a pista do YouTube; `gh` autenticado liga a do GitHub; chaves ligam X, TikTok, Instagram, Bluesky, Threads, Trustpilot e afins. O `--preflight` desta máquina lista como indisponíveis: `yt-dlp`, `gh`, `digg-pp-cli`, `arxiv-pp-cli`, `techmeme-pp-cli`, `trustpilot-pp-cli` e `brightdata`. Instale só se a pauta exigir essas fontes.
- `node` e `npx` são usados por CLIs de fontes secundárias (Digg, arXiv, Techmeme) e pelo cliente de busca do X vendorizado.

## Como invocar

Rode em primeiro plano, com timeout de 300000 ms na ferramenta de shell. Uma execução típica leva de 1 a 3 minutos.

```bash
SKILL_DIR="$HOME/.zcode/skills/terras-last30days"
python3 "$SKILL_DIR/scripts/last30days.py" "TEMA" \
  --emit=compact --save-dir="$HOME/Documents/Last30Days"
```

Exemplos de uso:

```bash
# tema simples
python3 "$SKILL_DIR/scripts/last30days.py" "Claude Code skills"

# mais rápido, menos fontes
python3 "$SKILL_DIR/scripts/last30days.py" "fim de suporte .NET 8" --quick

# mais fundo, mais consultas
python3 "$SKILL_DIR/scripts/last30days.py" "AI triage em service desk" --deep

# o que está em alta, sem tema definido (global)
python3 "$SKILL_DIR/scripts/last30days.py" --discover

# o que está em alta dentro de um domínio
python3 "$SKILL_DIR/scripts/last30days.py" --discover "dev tools"

# comparação entre dois temas
python3 "$SKILL_DIR/scripts/last30days.py" "Copilot vs Cursor"

# sem tocar em cookie de navegador
python3 "$SKILL_DIR/scripts/last30days.py" "tema" --no-browser-cookies

# diagnóstico das fontes (o que está quebrado ou faltando)
python3 "$SKILL_DIR/scripts/last30days.py" --diagnose
```

Sobre tema que é pessoa, produto ou empresa, quem hospeda a skill é o planejador: gere um plano de consulta em JSON e passe por `--plan`, em vez de deixar o motor cair no plano determinístico. O motor avisa isso na saída quando não recebe plano. Esquema do plano em `references/upstream-skill.md` (LAW 7 e Step 0.75).

Flags que mudam o resultado:
| Flag | Efeito |
|---|---|
| `--days=N` | Janela de busca (padrão 30) |
| `--as-of=AAAA-MM-DD` | Move o fim da janela para uma data |
| `--quick` / `--deep` | Menos ou mais consultas e fontes |
| `--emit=compact\|json\|html\|brief` | Formato de saída (JSON com `--json-profile=agent` é o contrato estável) |
| `--save-dir` | Onde salvar o relatório bruto |
| `--output=ARQUIVO` | Caminho exato do arquivo de saída |
| `--discover [DOMÍNIO]` | Modo descoberta de pauta, sem tema definido |
| `--competitors[=N]` | Compara concorrentes de um produto |
| `--hiring-signals` | Sinais de contratação em torno de um tema |
| `--drill ALVO` | Aprofunda um item específico do relatório |
| `--no-browser-cookies` | Não lê cookie do navegador |
| `--diagnose` / `--preflight` | Diagnóstico de fontes e de ambiente |

Flags de direcionamento (`--plan`, `--x-handle`, `--subreddits`, `--github-repo` e outras) fazem parte do protocolo completo, em `references/upstream-skill.md`.

## Saída

- A primeira linha é o selo de versão: `🌐 last30days v3.25.0 · synced AAAA-MM-DD`. Ela vai para o usuário.
- Os blocos de evidência vêm dentro de comentários HTML e servem para a síntese, **não** para mostrar ao usuário.
- O relatório bruto é salvo em `--save-dir` (padrão `~/Documents/Last30Days`) como `{slug}-raw.md`.

Ao apresentar o resultado: síntese em prosa com os achados agrupados por tema, os números de engajamento que sustentam cada um e os links das fontes. Diga também o que a janela não cobriu, quando for o caso. Não despeje o relatório bruto.

## Segurança: o que esta skill toca

Vale saber antes de rodar, porque é o tipo de coisa que ninguém lê no README:

- **Cookie de navegador.** Só lê com consentimento explícito (o assistente salva `BROWSER_CONSENT=true` na configuração). A leitura é ao vivo, em tempo de busca, e não grava o cookie em disco. `--no-browser-cookies` desliga.
- **Credenciais.** Ficam em `~/.config/last30days/.env` em texto puro (o engine avisa se o arquivo estiver legível por outros usuários, mas não corrige sozinho; um `chmod 600` resolve). Há ajudantes opcionais para guardar em Keychain (macOS) ou `pass` (Linux), nenhum dos dois presente nesta máquina.
- **Instalações.** O assistente de primeira execução pode instalar `yt-dlp` via Homebrew e pacotes npm do catálogo do autor. Nesta instalação nada foi executado e nada foi instalado: a decisão é sua, na hora de rodar.
- **Terceiros.** Além das plataformas listadas, há fallbacks gratuitos que valem conhecer: `r.jina.ai` para leitura de página sem chave e `arctic-shift.photon-reddit.com` para arquivo de votos do Reddit.
- **Sem telemetria.** Não há envio de dados para o autor. O modo de API hospedada só liga se você definir `LAST30DAYS_API_KEY` e `LAST30DAYS_API_BASE`.
- **Publicação é opt-in e pública por padrão.** `--publish-html` e `--publish` sobem para `api.ht-ml.app` com páginas públicas, salvo senha definida. Não use sem pedido explícito.

## Fluxo para posts

1. Descubra a pauta: rode o engine no tema, ou `--discover` quando a ideia ainda não existe.
2. Filtre pelo que tem fato verificável: data que expira, versão nova, mudança que quebra, número que surpreende. Discussão quente sem fato não sustenta post.
3. Confirme na fonte primária: changelog, release notes, documentação oficial.
4. Escreva com a `terras-linkedin`, que tem as regras de formato, os três arquivos e as bandas de caracteres.

Quando o usuário perguntar por que um post rendeu pouco, esta skill ajuda a checar se o assunto tinha circulação fora da rede, mas a causa provável costuma estar no formato do post, não na pauta.

## Créditos

Motor e protocolo de `mvanhorn/last30days-skill` (MIT), vendorizado na versão 3.25.0. Manual reescrito em português, com a regra de descoberta, o resumo de segurança e o fluxo para posts acrescentados.

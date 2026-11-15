# Vermelho: o que deu errado sem a skill (2026-11-15)

Falhas observadas numa sessão real, ao recriar duas músicas worship no Strudel sem roteiro. Cada uma virou uma regra do SKILL.md.

| # | Falha observada | Regra que fecha |
|---|---|---|
| 1 | `yt-dlp -J ... 2>&1 \| json.load` quebrou: o aviso de runtime JS vai para o stderr e foi misturado ao JSON | Passo 1: `2>/dev/null` |
| 2 | `librosa.load` em m4a: `LibsndfileError: Format not recognised` | `analisar.py` converte para wav com ffmpeg |
| 3 | `librosa` ausente no Python do sistema | Requisitos: venv descartável |
| 4 | O `beat_track` deu 152 e 143,6 BPM para baladas de 76 e 72 | Passo 5: conferir a grade da caixa e adotar a metade |
| 5 | O CSV traz ruído (Gm, C, Dm isolados em D maior); usar tudo gera progressão sem sentido | Passo 5: loop por seção, descartar o que está fora do campo harmônico |
| 6 | Trocar o hash da URL numa aba já aberta no Strudel não recarregou o código | Passo 7: navegar e recarregar |
| 7 | O console do navegador ficou vazio, e os erros do Strudel ficam só na aba console dele | Regra dura 3 e passo 7 |
| 8 | O snapshot da tela não mostrava `cp` e `oh` acesos e parecia que não tocavam; amostrando por segundos, apareciam | Passo 7: amostrar os tokens acesos por 5 a 8 s |
| 9 | Tentação de transcrever a melodia de obra protegida quando o pedido é "fazer o reverso" | Regra dura 2 |
| 10 | A sessão estava aberta no repositório de outro projeto, e o lugar óbvio para criar as pastas era justamente o errado | Passo 2 |

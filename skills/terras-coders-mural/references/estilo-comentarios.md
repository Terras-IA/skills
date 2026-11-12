# Estilo dos comentários

O objetivo é provar que o post foi lido. Comentário genérico ("Great post!", "Nice topic, thanks
for sharing") não gera conversa e todo mundo percebe que é automação.

## Tom (decisão do usuário em 11/11/2026)

O comentário fala na primeira pessoa e mostra opinião, não aula. Nada de "One catch: X" ou "Since
version N, Y does Z" em tom de manual. O tom muda conforme o tema é ou não da área do usuário.

**Na área dele** (.NET/C#, ASP.NET Core, EF Core, arquitetura, microsserviços, APIs, idempotência,
filas, bancos relacionais/PostgreSQL/SQL Server, Azure DevOps, CI/CD, Docker, agentes de IA,
carreira e entrevistas): opinião ou prática própria.
- EN: "I'd do it like this: ...", "What I usually do is ...", "I think the ideal here would be ...",
  "I've done it this way: ..."
- PT: "Eu faria assim: ...", "Costumo fazer ...", "Penso que o ideal seria ...", "Já fiz assim: ..."

**Fora da área dele** (geodados/GIS, jogos/Unity, mobile nativo, produto/UX, ciência de dados e ML,
Go, dbt e afins): curto e humilde, sem ensinar o autor.
- EN: "Interesting point.", "Nice way to look at it.", "I don't know much about this, but I think ..."
- PT: "Achei interessante.", "Bom ponto de vista.", "Não conheço muito, mas penso que ..."
- Um detalhe do post continua obrigatório, para provar leitura. Pergunta curta também vale.

**"Já fiz" e "costumo fazer" afirmam experiência dele.** Use quando for plausível pelo perfil, mas
sempre sinalize na tabela de aprovação para ele confirmar ou trocar por "eu faria".

Em dúvida se o tema é da área dele, trate como fora.

## Regras

- **Um detalhe concreto do post**: um número, um termo, uma frase do autor, o exemplo que ele usou.
- **Um acréscimo**: experiência, nuance, contraponto educado ou a resposta à pergunta que o autor fez.
- **Curto**: 1 a 2 frases, até ~150 caracteres. Sem hashtags, sem emoji, sem travessão (—).
- **Nome do autor** só às vezes, e só o primeiro nome.
- **EN passa pela `terras-humanizer`** antes da tabela de aprovação: padrões de IA e régua B1/B2
  (`terras-humanizer/references/ingles-b1b2.md`). Palavra comum ganha da bonita; termo técnico que
  é o nome exato da coisa (`container_cpu_cfs_throttled_seconds_total`, CDC, idempotent) fica.
- **EN no LinkedIn, PT no mural**, mesma ideia. O PT não precisa ser tradução literal; precisa soar
  natural em português.
- **Não invente experiência do usuário.** Frases como "saved me more than once" ou "changed it for me
  too" atribuem vivência a ele: sinalize na tabela de aprovação para ele confirmar ou trocar.
- **Não repita quem já comentou.** Leia a conversa antes de escrever (passo 3). Pergunta que outra
  pessoa já fez, com a resposta do autor logo embaixo, mostra que você não leu a thread. Troque o
  ângulo ou construa em cima da resposta ("Your answer to Felipe about the blob link covers...").
- Post comemorativo (certificação, conquista): parabéns + um detalhe do que ele contou.
- Post de ferramenta/link: diga para que você usaria ou um cuidado ao usar.

## Exemplos

| Post | Ruim | Bom (EN) |
|---|---|---|
| Teste de concorrência com 10 débitos simultâneos (área dele) | "Great post!" | "I'd assert the invariant, not the throughput. I usually put a barrier before the write so all 10 start together." |
| Async/await e EF Core (área dele) | "One DbContext can't run two queries at the same time." (tom de manual) | "Page 4 is the key one for me. With EF Core I'd never run two queries on the same DbContext at once; I'd use one context per query." |
| Mapa de rodovias do Paraná (fora da área) | "Area weighting assumes even spread, so the 26% is low." (ensina o autor) | "Interesting map. I don't know much about GIS, but I'd guess rural houses sit closer to the roads. Would that change the 26%?" |
| Certificação em liderança situacional | "Congrats!" | "Congrats, Ana! Adapting the style to the team's phase is the hardest part of leading, and the least taught." |

## Tabela de aprovação

Mostre sempre as colunas `# | Autor | LinkedIn (EN) | Mural (PT)` e marque linhas que:
- não têm link (só mural);
- afirmam algo sobre a experiência do usuário ("já fiz", "costumo fazer");
- tratam de tema fora da área dele (tom humilde);
- tratam de tema sensível (política, demissões, saúde).

# Modelo do conhecimento.md

Idioma: português do Brasil. Termo técnico fica no nome exato (JWT, mTLS, `AddJwtBearer`).
Arquivo: `conhecimento.md` na pasta do post, ao lado de `post.md` e das imagens.

```markdown
# <Assunto em poucas palavras>

> Fonte: <Autor>, LinkedIn, <AAAA-MM-DD>. <url do post>
> Tags: <3 a 6 tags em minúsculas, separadas por vírgula>

## Em uma frase
<O que o post ensina, dito para alguém que não viu o post.>

## O que o post diz
<Bullets curtos. Juntar texto e imagem num conteúdo só, sem repetir.>

## O que só a imagem traz
<O que está na imagem e não no texto: tabela, código, header, exemplo, número.
"Nada além do texto" é resposta válida.>

## Conferência
| Afirmação | Veredito | Por quê / fonte |
|-----------|----------|-----------------|
| <afirmação do post> | certo / precisa nuance / errado / não conferi | <uma linha, com link de fonte primária quando houver> |

## O que o post não diz
<Lacunas que mudam a decisão na prática. É aqui que o conhecimento passa do post.>

## Como aplicar
<2 a 4 ações concretas, cada uma verificável.>

## Para lembrar
<3 a 5 pares pergunta e resposta curtos, bons para revisão espaçada.>
- **P:** ... **R:** ...
```

## Regras de cada seção

- **Conferência.** Cada afirmação técnica relevante do post e da imagem entra numa linha. Veredito vem de fonte primária (documentação oficial, RFC, spec, paper), não de memória. Sem fonte consultada: `não conferi`. Nunca marcar `certo` só porque soa certo.
- **O que só a imagem traz.** Tem que vir da leitura da imagem com Read. Texto pequeno ilegível: dizer que estava ilegível, não adivinhar.
- **GIF animado.** Descrever o roteiro na ordem (estado inicial, o que muda, estado final), com os números e rótulos legíveis, e dizer se é demonstração encenada ou captura real. O conhecimento costuma estar na mudança, não num quadro só.
- **O que o post não diz.** Não é crítica ao autor. É o que alguém que só leu o post erraria ao aplicar.
- **Para lembrar.** Pergunta que exige recordar, não reconhecer. Nada de "Verdadeiro ou falso".
- **Separar fato de opinião.** "O autor recomenda X" é diferente de "X é o padrão".
- **Crédito.** A linha de fonte no topo é obrigatória. Imagem do autor não vai para post próprio sem autorização.

## Índice

Uma linha por post em `~/linkedin/conhecimento/indice.md`, mais recente no topo, abaixo do cabeçalho:

```markdown
- 2026-10-15 · [7 tipos de autenticação em ASP.NET Core](2026-10-15/aram-tchekrekjian-168770/conhecimento.md) · Aram Tchekrekjian · aspnet-core, autenticacao, seguranca
```

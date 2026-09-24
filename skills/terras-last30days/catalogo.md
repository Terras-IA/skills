---
name: terras-last30days
version: 1.0.0
access: free
category: conteudo
description: Pesquisa o que circulou sobre um tema nos últimos 30 dias (Reddit, X, YouTube, Hacker News, GitHub e web) — o que está vivo, onde a conversa acontece, qual ângulo ninguém cobriu. Descoberta, não fonte.
keywords: [ultimos 30 dias, pesquisa de pauta, o que estao falando, trending topics]
---

# Pesquisa de pauta dos últimos 30 dias

## Descrição

Descobrir o que circulou sobre um tema nos últimos 30 dias: posts, engajamento e discussão em Reddit, X, YouTube, Hacker News, GitHub e na web. Serve para responder três perguntas antes de escrever: **esse assunto está vivo?** **onde a conversa acontece?** **qual é o ângulo que ninguém cobriu?**

## Regra dura: descoberta, não fonte

O resultado mostra o que as pessoas dizem, não o que é verdade. **Nunca cite o resultado como fonte de um fato em texto publicado.** Antes de escrever qualquer post, confira versão, data e detalhe na fonte primária (changelog, release notes, documentação oficial). Data errada derruba a credibilidade do post inteiro.

O fluxo é: a pesquisa acha a pauta, a fonte primária confirma o fato, e só então o texto é escrito.

## Quando usar

- Descobrir pauta: "o que está acontecendo em X?"
- Medir se um assunto está circulando antes de investir num post.
- Comparar dois temas para escolher qual rende mais.
- Checar o que uma comunidade está discutindo sobre um produto ou pessoa.

## Como funciona

### Fontes e método

1. **Defina a janela e o tema.** Últimos 30 dias por padrão; janela diferente quando o usuário pedir.
2. **Varra as fontes públicas.** Reddit (com votos e comentários), Hacker News, YouTube, X, GitHub, Polymarket e busca web. Sem chave de API, o piso gratuito já cobre as principais; fontes extras (chaves de API, ferramentas de busca especializadas) entram só quando a pauta exigir — e com consentimento.
3. **Colete evidência com link e data.** Cada afirmação de "as pessoas estão falando X" precisa de um post/comentário citável com data dentro da janela.
4. **Agrupe por tema.** O que se repete, onde a conversa está concentrada, qual o tom (celebração, reclamação, dúvida).
5. **Identifique o ângulo não coberto.** O que todo mundo está dizendo não é pauta nova; a pauta é o ponto de vista ou a pergunta que ninguém respondeu.

### Saída esperada

Síntese em prosa com os achados agrupados por tema, os números de engajamento que sustentam cada um e os links das fontes — não o relatório bruto. Diga também o que a janela não cobriu.

### Segurança

- **Cookie de navegador** — só com consentimento explícito do usuário; nunca gravar cookie em disco.
- **Credenciais** — ficam em arquivo de ambiente com permissão restrita (600), nunca no texto nem no repositório.
- **Publicação é opt-in e pública por padrão** — não publicar nada sem pedido explícito do usuário.
- **Sem telemetria nem envio de dados** para terceiros além das plataformas consultadas.

### Fluxo para posts

1. Descubra a pauta: rode a pesquisa no tema, ou em modo descoberta quando a ideia ainda não existe.
2. Filtre pelo que tem fato verificável: data que expira, versão nova, mudança que quebra, número que surpreende. Discussão quente sem fato não sustenta post.
3. Confirme na fonte primária: changelog, release notes, documentação oficial.
4. Escreva seguindo as regras de formato de post do projeto.

Quando um post rendeu pouco, a pesquisa ajuda a checar se o assunto tinha circulação fora da rede — mas a causa provável costuma estar no formato do post, não na pauta.

## Governança

- Resultado de pesquisa é evidência de conversa, não fato estabelecido: toda citação em texto publicado passa pela fonte primária antes.
- A janela declarada faz parte do resultado: "assunto morto" sem dizer a janela e as fontes consultadas é opinião, não pesquisa.

## Critério de qualidade

A pesquisa está pronta quando: a janela e as fontes estão declaradas, cada tema tem evidência com link e data, o ângulo não coberto foi apontado, e o que a janela não cobriu foi dito explicitamente. Sem isso, é impressão de feed, não pesquisa de pauta.

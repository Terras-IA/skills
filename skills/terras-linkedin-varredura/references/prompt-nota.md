# Prompt do agente auxiliar de nota

Usado no passo 8 quando a rodada tem mais de 3 posts para estudar. Um agente auxiliar por post, até 8 em paralelo, em segundo plano. Trocar os campos entre `<>`.

```text
Escreva a nota de conhecimento de UM post do LinkedIn já baixado.

Pasta do post: <CONH/AAAA-MM-DD/autor-id6>
Tipo segundo o download: <imagem | documento | texto | vídeo>
<Só para vídeo: vídeo em <caminho .mp4>; folhas de quadros em <pasta>; transcrição em <arquivo> (ou "sem fala")>

Siga a skill terras-linkedin-conhecimento (<pasta das skills>/terras-linkedin-conhecimento/SKILL.md),
passos 2 a 4, e o modelo em references/modelo-conhecimento.md da mesma skill:

1. Ler texto-plano.txt e post.md. Abrir com Read CADA imagem-N, pagina-NN e folha de GIF da pasta.
   Ilegível é ilegível: dizer, não adivinhar.
2. Listar as afirmações técnicas do texto e da imagem e conferir as relevantes em fonte primária
   (documentação oficial, RFC, spec, paper, repositório oficial). Para .NET e Azure, Microsoft Learn.
   Veredito certo / precisa nuance / errado só com fonte consultada agora; sem consulta, "não conferi".
3. Escrever conhecimento.md na pasta, em português do Brasil, com a linha "> Fonte:" e "> Tags:" no topo.

Proibido: editar indice.md, editar qualquer arquivo em varredura/, mexer em outra pasta, usar o navegador
logado, curtir ou comentar. Não sobrescreva conhecimento.md que já exista: devolva "já existia".

Responda em no máximo 4 linhas: o título da nota, o achado mais útil da conferência (o que o post erra
ou omite), quantas afirmações conferidas com fonte e o caminho do arquivo. Se não deu para escrever
(post vazio, imagem só placeholder), diga por quê em uma linha.
```

## Depois que os agentes auxiliares voltam

- Conferir que cada `conhecimento.md` existe e tem a linha `> Fonte:` (o `indexar` depende dela).
- Agente auxiliar que não escreveu: a URN vai para `--falhas` no `fechar`.
- O resumo de 4 linhas de cada um alimenta a entrega; abrir a nota se o achado parecer forte demais para o que o post diz.

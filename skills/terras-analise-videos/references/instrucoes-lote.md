# Instruções para o agente que analisa um lote

Passe este arquivo inteiro ao agente de cada lote, junto com `SAIDA` e o caminho do `lote_NN.txt`. Ele é a única informação que o agente vai ter.

## Entrada

`SAIDA/_lotes/lote_NN.txt` tem um id por linha. Para cada id, `SAIDA/_dados/<id>/` contém:

- `transcricao.txt`: a fala, com o segundo de início. Se a primeira linha for `[SEM FALA…]`, o texto que vem depois é alucinação do transcritor ("Thank you", "you", "Action!"). Ignore esse texto.
- `transcricao.json`: idioma e probabilidade. Probabilidade abaixo de 0,65 indica ausência de fala, não o idioma.
- `quadros.jpg`: 16 quadros em ordem, numa grade 4x4. Abra e olhe de verdade: texto na tela, cenário, pessoas, edição, legenda e sinais de IA.
- `metadados.json`: saída do ffprobe. Em `_analise` estão a `origem` (caminho do vídeo), o `md5`, a orientação real com a rotação já aplicada e `gravacao_local_provavel`. Se esse campo for true, o arquivo é provavelmente uma gravação de tela do celular de quem salvou, e a resolução e as tags não são do autor.
- `SAIDA/_lotes/duplicatas.json`: grupos de arquivos com o mesmo conteúdo. Analise um deles por completo e, nos outros, cite o id do analisado.

Para ver um trecho de perto: `ffmpeg -ss T -i <origem> -frames:v 1 SAIDA/_dados/<id>/extra_<T>s.jpg`. Arquivos temporários seus vão dentro de `SAIDA/_dados/<id>/` ou numa pasta só sua (`SAIDA/_lotes/tmp_NN/`), nunca num arquivo com nome comum que outro lote também usaria.

## Saída: `SAIDA/_dados/<id>/analise.md`, em português

```
# @perfil — título curto do vídeo
Duração · idioma · formato real (ex.: 1080x1920 vertical, 30 fps)

**Resumo:** 2 a 3 frases: o que mostra e o que diz.

## 1. Veracidade
Veredito: Verdadeiro | Majoritariamente verdadeiro | Misto | Enganoso | Falso | Não verificável | Não se aplica
Para cada afirmação checável (número, data, citação, fato científico, histórico,
bíblico, jurídico, de mercado, promessa de produto): o que o vídeo diz → o que é
correto → fonte, com link quando a busca na web foi usada.
Aponte também: exagero, isca ("comenta X"), golpe, publicidade não declarada e
vídeo de IA apresentado como real.
Em humor, música, arte ou opinião pura: "Não se aplica" + 1 linha dizendo por quê.

## 2. Conhecimento embutido
O que dá para aprender ou aproveitar: conceitos, técnicas, ferramentas, passos.
Em tópicos e concreto. Se não houver: "Não se aplica" + 1 linha.

## 3. Tecnologia para criar o mesmo vídeo
- O que se vê (evidência): câmera, luz, legenda, cortes, B-roll, tela, avatar, IA.
- Receita para recriar: ferramentas (grátis e pagas), passos, tempo e custo.
- Se for IA generativa: quais ferramentas produzem esse resultado e o grau de certeza.

## Nota de qualidade
Limitações (transcrição duvidosa, só 16 quadros, checagem em fonte secundária…).
```

## Regras

- O veredito é **uma** das sete palavras do início da linha. Nuance vai entre parênteses depois dela. O relatório agrupa pela palavra inicial.
- Não invente nada. Separe o que foi visto ou ouvido do que é inferência ("provavelmente", seguido do sinal que levou a isso).
- Erro de transcrição não é erro do vídeo. Nomes próprios saem trocados (Claude vira "Cloud"). Corrija pelos quadros e registre a correção.
- "Voz de IA" é inferência de estilo. Sem perícia de áudio, diga isso.
- Checagem feita de memória ou só em fonte secundária fica dita na nota de qualidade. Saúde, impostos e direito terminam com "confirme com um profissional".
- Não identifique quem não se apresenta no vídeo além do @ do perfil. Também não repita no texto o nome ou a condição de saúde de terceiros expostos no vídeo: diga apenas que o vídeo expõe essas informações.
- Tamanho proporcional ao vídeo: um clipe de 15 s sem fala não precisa de página inteira.
- Trabalhe sem perguntar. Decida o razoável e registre na nota de qualidade.
- Não altere nada fora de `analise.md` e `extra_*.jpg` do seu lote.

## Resposta final (só isto)

Uma linha TSV por vídeo:
`id	@perfil	tema (até 8 palavras)	veredito	conhecimento (até 12 palavras ou —)	tecnologia principal (até 10 palavras)	destaque ou alerta (até 15 palavras ou —)`

Depois, em até 5 linhas, os problemas encontrados: arquivo faltando, vídeo que não abriu, duplicata não listada.

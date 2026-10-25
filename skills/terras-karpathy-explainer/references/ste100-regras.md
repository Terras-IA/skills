# ASD-STE100 aplicado à explicação

Resumo próprio das regras da norma que importam para explicar um tema. Não é cópia
da norma; a edição oficial é pedida de graça em asd-ste100.org.

## O que a norma é

Língua controlada criada pela indústria aeronáutica para manuais de manutenção.
Tem duas partes: regras de escrita e um dicionário de palavras aprovadas, cada uma
com um só sentido e uma só classe gramatical. Termos técnicos do domínio (nome de
peça, de ferramenta, de API) são permitidos à parte do dicionário.

## Regras usadas nesta skill

| Regra | O que pede |
|---|---|
| Frase de procedimento | até 20 palavras, um passo, imperativo |
| Frase de descrição | até 25 palavras, uma ideia |
| Parágrafo | até 6 frases, um assunto |
| Voz | ativa; passiva só quando o agente é desconhecido ou irrelevante |
| Tempos verbais | simples (presente, passado, futuro); nada de locução longa |
| Substantivos em cadeia | no máximo 3 |
| Sinônimo | proibido trocar o termo escolhido no meio do texto |
| Aviso | antes do passo, com o motivo |

## Adaptação para o português

- Conte palavras como separadas por espaço; números e siglas contam como uma.
- Passiva analítica ("é calculado pelo", "foram removidos") vira ativa: diga quem
  faz. Passiva sintética ("calcula-se") também vira ativa.
- Gerúndio encadeado ("realizando o cálculo e verificando") vira dois verbos
  diretos em duas frases.
- Nominalização ("a realização da validação") vira verbo ("valida").

## Antes e depois

- Antes: "A validação do token é realizada pelo servidor antes da liberação do acesso ao recurso solicitado."
  Depois: "O servidor valida o token. Em seguida, libera o acesso ao recurso."
- Antes: "The bolts should be checked for tightness prior to the commencement of operation."
  Depois: "Before you start the engine, make sure that the bolts are tight."
- Antes: "Basicamente, o índice meio que vai navegando pelas camadas até achar o vizinho mais próximo."
  Depois: "O índice desce pelas camadas. Em cada camada, ele vai para o vizinho mais próximo da consulta."

## Inglês: palavra aprovada

| Não aprovada | Aprovada |
|---|---|
| utilize | use |
| commence | start |
| prior to | before |
| in order to | to |
| ensure | make sure |
| approximately | about |

## Por que 80% e não 100%

STE a 100% repete o mesmo substantivo em toda frase e soa como log. A folga de 20%
aceita conectivo curto ("Em seguida", "Por isso") e pronome sem ambiguidade. Ela não
aceita frase longa, passiva sem motivo nem enfeite.

# Perfil profissional — base do filtro (exemplo)

**Este é o template.** A skill lê `references/perfil.md`, que é local e fica fora
do git (protegido pelo `.gitignore`). Para usar: copie este arquivo para
`perfil.md`, preencha a partir do seu currículo em PDF e mantenha atualizado.

```bash
cp references/perfil.example.md references/perfil.md
```

## Quem é

`<Nome e posição em 2-3 linhas: nível, anos de experiência, o que faz bem.>`

## O que procura agora

- **`<Nível e função alvo>`**: `<áreas>`.
- **`<Modalidade>`**: `<remoto / híbrido / presencial, e regiões elegíveis>`.
- Base: `<cidade/estado, país, fuso>`.

## Stack com que é contratado

- **Forte (é você):** `<linguagens, frameworks, infra, o que sustenta o CV>`.
- **Sólido (transita):** `<o que você faz sem ser o núcleo>`.
- **Diferencial (crescendo):** `<o que te separa da média do nível>`.

## Baldes de encaixe

**A — Faz sentido real (recomendar):** `<nível, funções e stacks que você quer ver na lista>`.

**B — Talvez (listar separado, decidir é do usuário):** `<fronteiras plausíveis: stack vizinha em papel equivalente, presencial fora da base, migração de área>`.

**C — Descarte (contar e citar motivo em 1 linha):** `<o que não faz sentido: níveis abaixo, áreas fora, stack sem overlap, modalidade inviável>`.

## Regras de julgamento

1. **O título mente menos que parece, mas mente.** "Fullstack" às vezes é
   backend com HTML de vez em quando — e às vezes é front com API de passar
   roupa. Na dúvida entre A e B, o anúncio decidido no passo de aprofundamento
   (abrir o link da vaga) ganha.
2. **Salário se reporta, não se julga.** Não existe piso definido pelo usuário;
   quando a vaga traz faixa, reproduza na tabela. Se o usuário definir um piso
   nas preferências abaixo, aí sim filtre por ele.
3. **Senioridade pedida abaixo do nível-alvo é descarte**, mesmo que a stack
   seja 100% igual — é perda de tempo para os dois lados.
4. **Não invente encaixe.** Se o núcleo da vaga é outra coisa e o overlap é só
   a palavra "cloud" no texto, é C com o motivo na mesa.
5. **Post vago é descarte por falta de sinal.** Muito post entra no board como
   "WE'RE HIRING" / "Olá Rede" sem cargo no título. Título que não diz o que é
   a vaga é C ("post vago, sem sinal de encaixe") — abrir dezenas de posts para
   descobrir não escala. Se o usuário pedir, aprofunde um a um.
6. **Duplicatas por julgamento.** A mesma vaga repostada por fontes diferentes
   tem URLs diferentes; o dedup por url não pega. Na entrega, mescle e cite
   as fontes que trouxeram.

## Preferências editáveis (o usuário muda aqui)

- Piso salarial: `<definir um número ou "não definido — reportar faixas">`.
- Contrato: `<CLT, PJ ou ambos>`.
- Período: `<integral / meio período>`.
- Fontes a ignorar: `<listar ou "nenhuma">`.

## Preferências registradas no board (lidas de `/api/board/me` em `<data>`)

`<O que o perfil do board já declara (modalidade, região, stack). Use como
confirmação do alvo, não como filtro duro — o julgamento continua sendo por
este arquivo.>`

## Kit de candidatura (fase 2 — dados de formulário)

Fatos confirmados, prontos para preencher formulários:

- Nome: `<Nome completo (First / Last como você quer que apareça)>`
- E-mail / telefone: `<e-mail> · <telefone com DDI>`
- LinkedIn: `<url>`
- Base / fuso: `<cidade, país · UTC±n>`
- Autorização de trabalho: `<cidadão / visto / necessidade de sponsorship>`
- Inglês: `<nível e como responder às perguntas de fluência>`
- Currículo em PDF: `<pasta canônica do PDF mais recente; o usuário anexa
  manualmente nos formulários — o navegador embutido não faz upload>`
- Anos de experiência: `<número ou faixa e como responder>`

**Respostas confirmadas como PADRÃO pelo usuário** (as que ele já aprovou em
formulário real; revisar a cada mudança):

- `<ex.: notice period, pretensão salarial, surveys de diversidade, GitHub/portfólio>`
- Limite de candidaturas/dia: `<número>` (padrão da skill; o usuário muda aqui)

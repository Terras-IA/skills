---
name: terras-pitch-por-vaga
description: "Gera, a partir do CV (PDF, texto ou LinkedIn), o JSON de CV-base que o site Pitch por Vaga importa: perfis de vaga, projetos e 20 falas em inglês para entrevista, validado. Use para 'meu CV para o Pitch por Vaga'. Carta: terras-cover-letter; ATS: terras-checagem-ats."
keywords: [pitch por vaga, pitch.coderstudio.club, cv json, curriculo, apresentacao de entrevista, self introduction, tell me about yourself, entrevista em ingles, interview pitch, perfis de vaga, importar cv]
---

# CV-base para o Pitch por Vaga

## Objetivo

O site <https://pitch.coderstudio.club> ajuda a pessoa a treinar a apresentação falada de entrevista,
em inglês, adaptada a cada vaga. Ele parte de um **CV-base** em JSON, importado em **Meu CV ›
Importar JSON**. Esta skill gera esse arquivo com o agente da própria pessoa, sem ela colar chave
de API no site, e confere o formato antes de entregar.

## Regra dura

1. **Não invente fato.** Empresa, data, número, resultado, certificação e skill saem do CV ou do que
   a pessoa disse. O que faltar vira lacuna entre colchetes (`[result with a number]`). Skill que
   só aparece implícita no CV não entra; pergunte.
2. **Os 20 textos, todos.** `textos` tem as 9 falas da apresentação e as 11 perguntas, com as
   variáveis obrigatórias de cada uma. Falta de texto é o erro mais comum sem esta skill.
3. **Validar antes de entregar.** `node "$SKILL_DIR/scripts/validar.mjs" <arquivo>` sem erro. Aviso
   se lê e se decide; erro se corrige e valida de novo.
4. **Sem e-mail e sem telefone** em `contato`: ele aparece no slide de capa, na tela compartilhada.

## Onde está

Fonte única: `skills/terras-pitch-por-vaga/` no repositório `terras-skills`. `$SKILL_DIR` é a pasta
deste `SKILL.md`.

```
references/formato.md     todos os campos, os 20 textos e as variáveis do site
scripts/validar.mjs       confere o arquivo (Node 18+, sem dependência)
exemplos/cv-exemplo.json  arquivo completo e válido, pessoa fictícia
```

## Como trabalhar

1. **Ler o CV.** PDF, DOCX, texto colado ou perfil do LinkedIn exportado. Se o PDF não tiver texto
   (escaneado), peça o texto. Se a pessoa não disse, pergunte de uma vez: que tipos de vaga busca e
   qual o nível de inglês. Sem resposta, deduza do CV e diga o que deduziu.
2. **Ler `references/formato.md`** e abrir `exemplos/cv-exemplo.json` como molde.
3. **Montar os perfis.** De 2 a 5 tipos de vaga que o CV sustenta, cada um com 6 a 10 skills do CV,
   escritas com o nome usual do mercado (casam com a descrição da vaga), e 2 ou 3 projetos.
4. **Escrever as falas** em inglês simples, primeira pessoa, frases curtas, 15 a 30 segundos por
   tópico. `q-challenge` e `q-conflict` em STAR a partir de algo real do CV.
5. **Salvar** como `cv-<nome-em-slug>.json`, embrulhado em `{"tipo":"pitch-cv","versao":2,"cv":{...}}`,
   na pasta em que a pessoa está trabalhando (ou na que ela indicar).
6. **Validar** com `scripts/validar.mjs`. Corrija até `"ok": true`.
7. **Entregar** o caminho do arquivo e, numa lista curta: quantos perfis e quais, as lacunas que
   ficaram entre colchetes e o que foi deduzido. Diga como importar: abrir
   <https://pitch.coderstudio.club>, aba **Meu CV**, **Importar JSON**. Importar substitui o CV que
   estiver no navegador; as vagas continuam.

## Erros comuns

| Erro | Correção |
|---|---|
| Só alguns textos, ou só os da apresentação | Os 20 de `formato.md`, validados |
| Um perfil só | De 2 a 5; o site sugere o perfil pela descrição da vaga |
| Variável com outro nome (`{company}`, `{{role}}`) | Só as de `formato.md`, com chave dupla |
| Fala em português | Texto falado é em inglês; `nome` de perfil e rótulos podem ser em português |
| Número bonito no lugar da lacuna | Lacuna entre colchetes; a pessoa completa no site |
| Objeto `cv` solto | Embrulhar, ou rodar o validador com `--embrulhar` |

## Referências

- `references/formato.md`: campos, regras por campo, os 20 textos e as variáveis do site.
- `exemplos/cv-exemplo.json`: exemplo completo com pessoa fictícia.

---
name: terras-checagem-ats
description: "Confere CV e carta de apresentação em Markdown antes de enviar: leitura por ATS, cobertura das palavras-chave da vaga (corte de 70%), afirmação sem lastro e leitura rápida, com veredito e correções. Use para checar ATS, palavras-chave ou se o CV está pronto para a vaga."
keywords: [ats, checagem ats, applicant tracking system, cv, currículo, resume, carta de apresentação, cover letter, palavras-chave da vaga, keyword, filtro de recrutador, candidatura]
---

# Checagem de ATS para CV e carta

Portão de qualidade para o CV e a carta de uma candidatura. **Não invente
experiência para passar.** Prefira correções que reescrevem ou reordenam fatos
**verdadeiros** do CV mestre ou do que o usuário afirmou.

## Onde está instalada

Fonte única: `skills/terras-checagem-ats/` no repositório `terras-skills`. Cada
agente enxerga a skill por um link simbólico criado pelo `scripts/instalar.sh`
do repositório. Nos caminhos abaixo, `$SKILL_DIR` é a pasta onde este
`SKILL.md` está.

## Quando rodar

- Depois de escrever ou adaptar um CV ou uma carta para uma vaga (a
  `terras-cover-letter` escreve a carta; esta confere).
- Quando o usuário pedir para validar ATS, palavras-chave ou filtro de
  recrutador.
- Antes de exportar para PDF (`terras-md-para-pdf`) ou enviar a candidatura.

## Entradas

1. A descrição da vaga, se houver.
2. O CV e/ou a carta em Markdown a conferir.
3. A fonte da verdade quando a honestidade estiver em dúvida: o CV mestre que o
   usuário indicar. Se não souber qual é, pergunte; não trate o próprio
   documento conferido como fonte.
4. Itens obrigatórios do usuário, se ele tiver: experiência que todo CV
   adaptado precisa manter (por exemplo uma tecnologia ou um projeto que é o
   diferencial dele). Procure essa regra no CV mestre, nas notas do projeto ou
   pergunte. Não existe item obrigatório padrão.

## Fluxo

Copie e vá marcando:

```
Checagem ATS:
- [ ] 1. Leitura por ATS
- [ ] 2. Cobertura de palavras-chave da vaga
- [ ] 3. Honestidade
- [ ] 4. Leitura rápida
- [ ] 5. Veredito e correções
```

### 1. Leitura por ATS

Reprove ou exija correção se qualquer um destes for verdade:

- Tabela usada para diagramar; texto só em imagem; layout em várias colunas.
- Contato sem e-mail, ou só dentro de uma imagem de cabeçalho.
- Título de seção fora do padrão escondendo Experiência, Formação ou Skills.
- Datas inconsistentes ou ambíguas (sem data de fim e sem "Atual"/"Present").
- Palavra-chave só como ícone ou selo, sem a mesma palavra em texto.
- Competência importante só numa barra gráfica.

Para passar:

- Markdown simples, títulos padrão.
- Uma linha de contato com e-mail (e telefone, LinkedIn e cidade se houver).
- Competências em texto pesquisável, com as variantes comuns quando forem
  verdade: Go/Golang, Kubernetes/K8s.

### 2. Cobertura de palavras-chave da vaga

Sem vaga: pule a pontuação; rode as outras etapas.

Com vaga:

1. Extraia o que ela exige: competências obrigatórias e desejáveis, termos do
   domínio, requisitos comportamentais que o anúncio destaca.
2. Pontue cada um: **Presente** | **Parcial** | **Ausente** | **Não inventar**.
3. **Corte para enviar:** entre os itens que não são `Não inventar`, pelo menos
   **70%** precisam estar `Presente` ou `Parcial`. Abaixo disso, o veredito é
   Reprovado ou Aprovado com correções, listando as correções verdadeiras de
   maior impacto.
4. Nunca vire `Ausente` em `Presente` inventando. Marque como `Não inventar` a
   lacuna que o CV mestre não sustenta.

### 3. Honestidade

Compare o que o CV e a carta afirmam com o CV mestre e com o que o usuário
disse. Aponte:

- Contribuição em open source ou comunidade exagerada.
- Habilitação de segurança, cidadania, visto ou elegibilidade de local
  inventados.
- Ferramenta ou domínio que não aparece na experiência de origem (só entra se
  o usuário confirmar).
- Número ou cargo inflado além da fonte.
- Item obrigatório do usuário (entrada 4) ausente. Resumido pode; sumir não.

Qualquer exagero material → **Reprovado** até corrigir. Item obrigatório
ausente → **Reprovado**.

### 4. Leitura rápida

- Resumo do CV: até umas 5 linhas densas de substância, não uma biografia.
- Bullets: abrem pelo resultado; corte enchimento e qualidade repetida.
- Carta: até umas 400 palavras (a `terras-cover-letter` mira 250 a 300);
  específica para a vaga; sem parede de clichê.
- CV adaptado abre pela experiência verdadeira que casa com a vaga, não por um
  aprofundamento que não tem a ver com ela.

### 5. Veredito

Dê exatamente um:

| Veredito | Significado |
| --- | --- |
| **Aprovado** | Pronto para enviar (detalhes menores opcionais) |
| **Aprovado com correções** | Envia depois das correções listadas; sem falha de honestidade |
| **Reprovado** | Problema que bloqueia: ATS, honestidade ou leitura |

Formato:

```markdown
## Checagem ATS: [Aprovado | Aprovado com correções | Reprovado]

### Leitura por ATS
- ...

### Palavras-chave (se houver vaga)
| Termo | Nota | Observação |
| --- | --- | --- |
| ... | Presente/Parcial/Ausente/Não inventar | ... |

Cobertura: X% Presente+Parcial (corte 70%) entre os itens pontuáveis.

### Honestidade
- ...

### Leitura rápida
- ...

### Correções em ordem de prioridade
1. ...
```

## Regras

- O CV mestre fica completo e neutro; não edite o CV mestre sem pedido
  explícito. A versão adaptada para cada vaga é outro arquivo.
- Depois de gerar um pacote de candidatura, rode esta checagem antes de dar o
  trabalho por terminado.
- Erros comuns, dicas de palavra-chave e exemplos do que não inventar:
  [references/referencia.md](references/referencia.md).

## Origem

Adaptada de uma skill de Cursor compartilhada por um colega (cv-cl-ats-check).

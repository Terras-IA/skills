# Frameworks de análise de processos

## 1. Métricas (e como calcular)

| Métrica | Fórmula | Leitura |
| --- | --- | --- |
| Lead time | Σ tempo_execucao + Σ tempo_espera (ponta a ponta) | O cliente espera isso |
| Cycle time | tempo de execução efetiva de uma etapa | Capacidade real |
| % espera | Σ espera / lead time × 100 | Acima de 60% → problema é fila, não trabalho |
| FTE-h/mês | lead time (h) × volume mensal | Tamanho do custo |
| Horas manuais repetitivas | Σ tempo das etapas tipo tarefa sem decisão × volume | Potencial de automação |
| Handoffs | nº de trocas de ator ou de sistema | Cada handoff ≈ 1 fila + 1 risco de perda de informação |
| First-time-right | passos que corrigem/reconferem/reenviam ÷ total | > 15% indica retrabalho estrutural |
| Custo do processo | FTE-h × custo-hora (se informado) | Só usar custo-hora real, nunca inventar |
| Toque manual | nº de digitações/coletas por transação | Gatilho para integração/OCR |

Sempre rotule a origem: `medido` · `estimado pelo relato` · `premissa do consultor`. Quando só houver relato, apresente **faixa** (ex.: 2–4 h) e liste a premissa.

## 2. Classificação de valor

- **VA (agrega valor)**: muda o produto/serviço na percepção do cliente. Paga-se por isso.
- **NVA-necessário**: exigido por lei, compliance, auditoria ou limitação real de sistema. Não elimina, otimiza.
- **NVA puro**: espera, aprovação redundante, retrabalho, cópia de dado, reunião de alinhamento. **Alvo primário.**

## 3. Os 8 desperdícios (DOWNTIME) — perguntas de detecção

| Desperdício | Sinal no relato/áudio |
| --- | --- |
| Defeitos | "volta", "corrige", "refaz", "o cliente reclama" |
| Superprodução | "gero o relatório todo dia mesmo sem uso", "mando cópia pra todos" |
| Espera | "aguardo o retorno", "só na segunda-feira", "fica na fila" |
| Talento subutilizado | "quem sabe fazer é só o fulano", "eu mesmo faço porque é mais rápido" |
| Transporte | "baixo o arquivo e subo no outro sistema", "mando por WhatsApp e depois lanço" |
| Estoque | "acumula pedidos", "caixa de e-mails com 200 itens", "backlog" |
| Movimento | "abro 3 sistemas", "procuro o contrato no Drive" |
| Processamento excessivo | "peço 3 aprovações", "preencho campo que ninguém usa", "assino de novo" |

## 4. 5 Porquês (causa raiz)

Aplique nos 2–3 gargalos de maior impacto. Exemplo:

> Espera de 1 dia na aprovação → gestor não vê o pedido → aprovação chega só por e-mail → não existe fila única de aprovação → sistema de OS não tem alçada configurada → **causa raiz: alçada não cadastrada no sistema, aprovação migrou para e-mail.**

Pare quando chegar a uma causa **acionável** (sistema, regra, cadastro, treinamento, contrato).

## 5. Ishikawa 6M (quando a causa é difusa)

Método · Mão de obra · Máquina (sistema) · Material (dado/documento) · Medida (indicador/parâmetro) · Meio ambiente (política, prazo, cultura).

## 6. SIPOC — o corte do escopo (use ANTES do mapa)

- **S**uppliers (quem fornece) · **I**nputs (o que entra) · **P**rocess (5–7 macro passos, verbo + objeto) · **O**utputs (o que sai) · **C**ustomers (quem recebe cada saída).
- Use **antes de desenhar** quando o processo for grande: é o SIPOC que decide onde o processo começa e termina — sem ele, o mapa cresce sem critério. No relatório, vira o sumário executivo para diretoria (uma linha por coluna).
- **SIPOC-R**: acrescente a linha **Requisitos** — o que cada Customer considera "pronto" (aceitação por saída). Sem ela, o quadro vira caixas sem critério de qualidade; com ela, o TO-BE ganha meta verificável.
- **COPIS** (de trás pra frente): quando o valor é definido pelo cliente, preencha Customers → Outputs primeiro e derive o resto. Suppliers que não alimentam nenhum requisito de saída estão no processo por costume — candidato a corte.
- Regras: no máximo 5–7 passos; passo é verbo + objeto, sistema não é passo ("lança no ERP" é, "ERP" não); quem só aprova é Customer da aprovação, não do uso.
- Ponte com o `processo.json`: Suppliers/Customers vêm de `atores`, Inputs/Outputs de `entradas`/`saidas` dos passos, e o Process é o caminho principal agregado em 5–7 macro passos.

## 7. Riscos e controles — checklist

- Aprovação verbal ou por mensagem (sem trilha) → risco de fraude/erro e sem auditoria.
- Dado mantido fora do sistema (planilha, caderno, WhatsApp) → risco de perda e LGPD.
- Dependência de pessoa única → risco de continuidade.
- Ausência de SLA/prazo definido → risco de reclamação e retrabalho de cobrança.
- Dupla digitação entre sistemas → risco de divergência de dado.
- Controle existente sem evidência de execução (assinatura, checklist, conferência) → controle de fachada.
- Dado pessoal/sensível trafegando em canal não controlado → LGPD.

Para cada risco: probabilidade, impacto, controle sugerido, esforço.

## 8. KPIs sugeridos no TO-BE

Sempre 3 a 5, ligados aos gargalos encontrados: lead time por tipo de demanda, % concluído no prazo (SLA), % first-time-right, backlog em aberto, horas de retrabalho, % de transações sem toque manual. Defina dono, fonte de dados e frequência — KPI sem dono não sobrevive.

## 9. GUT — priorizar PROBLEMAS (antes de escolher soluções)

Gravidade × Urgência × Tendência, notas 1–5 com âncoras, score = produto (1–125). GUT ordena **problemas**; a matriz impacto × esforço (§10) ordena **intervenções**. A ordem do método é esta: primeiro o que mais dói, depois o que fazer com ele.

Âncoras (definidas ANTES de pontuar; nota sem evidência é premissa e vira `lacunas`):

| Nota | Gravidade — dano se nada for feito | Urgência — prazo real | Tendência — sem intervenção |
| --- | --- | --- | --- |
| 1 | incômodo individual, sem efeito em resultado | pode esperar um trimestre ou mais | diminui sozinha |
| 2 | retrabalho local; cliente não percebe | pode esperar no mês | estável |
| 3 | atrasa entrega ou afeta um cliente | semanas, prazo conhecido | cresce devagar (ao mês) |
| 4 | afeta o resultado do mês ou vários clientes | dias; compromisso assumido | cresce por semana, já reincidiu |
| 5 | parada de operação, risco de perder cliente/contrato ou risco legal | hoje; cada dia custa ou bloqueia outros | efeito bola de neve comprovado |

- **Faixa de leitura** declarada antes de pontuar: ≥ 60 atacar agora · 27–59 planejar · < 27 fila.
- **Desempate** na ordem G > U > T: dano fala mais alto que pressa.
- **Variante ponderada** só com justificativa registrada (ex.: risco legal → peso 3 na Gravidade). Peso implícito é vício.
- Quem pontua: quem sente o problema **e** quem paga a conta, juntos; notas individuais comparadas, nunca média silenciosa.
- **GUT é foto**: repontue a cada ciclo; problema resolvido sai.

Depois do ranking: causa raiz (§4 e §5) nos 2–3 primeiros, então a matriz de intervenções (§10).

## 10. Matriz impacto × esforço (priorizar SOLUÇÕES)

|  | Esforço baixo | Esforço alto |
| --- | --- | --- |
| **Impacto alto** | Quick wins — fazer em < 30 dias | Projetos — patrocinador + cronograma |
| **Impacto baixo** | Ganhos rápidos / higiene | Descartar ou adiar |

Sempre entregue no mínimo **3 quick wins** concretos: são o que faz o patrocinador continuar.

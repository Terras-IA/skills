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

## 6. SIPOC (para fechar o escopo em 5 linhas)

Suppliers · Inputs · Process (5–7 macro passos) · Outputs · Customers. Use no sumário executivo quando o processo for grande e o leitor for a diretoria.

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

## 9. Matriz impacto × esforço

|  | Esforço baixo | Esforço alto |
| --- | --- | --- |
| **Impacto alto** | Quick wins — fazer em < 30 dias | Projetos — patrocinador + cronograma |
| **Impacto baixo** | Ganhos rápidos / higiene | Descartar ou adiar |

Sempre entregue no mínimo **3 quick wins** concretos: são o que faz o patrocinador continuar.

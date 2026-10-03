# Escolher a tecnologia de automação

## Árvore de decisão (nesta ordem)

1. **A atividade deveria existir?** Se não → eliminar. Automatizar desperdício acelera o desperdício.
2. **Pode ser simplificada ou padronizada?** Se há 3 variações do mesmo formulário, padronize antes.
3. **É regra determinística sobre dado estruturado?** → automação de regra / script / integração.
4. **Os dois sistemas têm API?** → integração direta (melhor opção, mais durável).
5. **Não têm API, mas a tela é estável?** → RPA (robô de tela).
6. **O dado de entrada é não estruturado (texto, PDF, áudio, imagem)?** → IA/LLM com validação humana.
7. **É fluxo de aprovação/handoff entre pessoas?** → workflow/BPMS com alçadas e prazo.
8. **É só visibilidade?** → painel/indicador, não automação.

## Sinal no processo → tecnologia

| Sinal observado | Tecnologia | Pré-requisitos | Riscos |
| --- | --- | --- | --- |
| Digitar o mesmo dado em 2 sistemas | Integração via API | API/documentação, cadastro único | Divergência de cadastro mestre |
| Copiar de planilha para sistema | RPA ou importação em lote | Layout estável, tratamento de erro | Quebra quando a tela muda |
| Ler contrato/NF/e-mail e extrair campos | IA (LLM) + conferência humana | Amostra para validar, campos críticos definidos | Alucinação; exigir score e revisão |
| Aprovação por e-mail/WhatsApp | Workflow com alçada e SLA | Cadastro de alçadas, substituto | Adesão da gestão |
| Conferência manual de totais | Validação automática (regra) | Regra explícita e testada | Regra errada bloqueia operação |
| Cobrança/lembrete recorrente | Automação agendada (e-mail/WhatsApp) | Template e opt-in | Percepção de spam |
| Preencher formulário repetido | Formulário dinâmico + integração | Modelo de dados | Escopo maior que o previsto |
| Atendimento repetitivo de dúvidas | Base de conhecimento + assistente de IA | Conteúdo curado | Resposta errada sem trilha |

## Como estimar o ganho (sem inventar)

```
ganho_h_mes = tempo_da_atividade_h × volume_mensal × fator_de_reducao
```
`fator_de_reducao` realista: 0,8–0,9 para digitação/integração · 0,5–0,7 para extração com IA (mantém revisão) · 0,3–0,5 para atividades com exceção frequente. Declare o fator usado como **premissa**.

Payback: `esforço_h_implantacao × custo_hora ÷ ganho_mensal` (em meses). Acima de 12 meses, reclassifique como projeto, não como quick win.

## Regras de prudência

- Automatize primeiro o **volume alto + regra clara + baixo risco** (quick win), não o caso mais complexo.
- Toda automação precisa de **dono, log e tratamento de exceção**. Sem isso, ela vira um novo gargalo invisível.
- Mantenha **caminho manual de contingência** documentado.
- Prefira 1 integração durável a 5 robôs frágeis.
- Onde houver dado pessoal, aplique minimização e registro de acesso (LGPD) antes de automatizar.

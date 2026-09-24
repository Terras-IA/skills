# Eval — coleção HR (`terras-*`): o gatilho certo dispara?

## Cenário

Vinte skills de domínio foram adotadas juntas (2026-09-12), todas de People/HR e
várias vizinhas entre si: onboarding × PDI, 1:1 × briefing de reunião, triagem
de currículo × entrevista de cultura, dashboard de benefícios × política de
benefícios, comunicado × dashboard de People. O usuário pede algo do domínio
sem nomear skill nenhuma:

1. "monta um plano de 30/60/90 dias pra nova analista" — onboarding
2. "preciso de um PDI pra pessoa com gaps de competência" — desenvolvimento individual
3. "vamos estruturar as 1:1 mensais com o time" — touchpoints
4. "prepara o briefing da reunião de calibração com a liderança" — brief pré-reunião
5. "faz a triagem de 15 currículos dessa vaga" — screening
6. "monta o scorecard da entrevista de fit cultural e a regra de veto" — bar raiser
7. "analisa a utilização de VA e VR e a adesão" — dashboard de benefícios
8. "escreve a política de benefício flexível alinhada ao PAT" — política de benefícios
9. "monta o dashboard mensal com headcount e turnover" — People dashboard
10. "escreve o comunicado interno da mudança de política" — comunicação de RH

## Comportamento esperado

1. A skill de gatilho mais específico dispara, **uma** por pedido: no caso 1 é
   `terras-roteirizador-de-onboarding` (não `terras-gerador-de-pdi`); no 3 é
   `terras-agenda-de-touchpoints` (não `terras-briefing-pre-reuniao-de-lideranca`);
   no 5 é `terras-screenador-de-curriculos-com-ia` (não `terras-bar-raiser-de-cultura`);
   no 7 é `terras-dashboard-de-utilizacao-de-beneficios` (não
   `terras-gerador-de-politica-de-beneficios`); no 9 é
   `terras-people-dashboard-automatico` (não `terras-gerador-de-comunicacao-de-rh`).
2. Nos pedidos ambíguos por natureza (4, 6, 8, 10), a skill escolhida é a do
   artefato pedido, e a resposta diz qual artefato vai produzir antes de produzir.
3. Pedido fora do domínio ("receita de bolo") **não** dispara nenhuma das 20.
4. A skill não decide sozinha sobre contratação, avaliação, remuneração, carreira,
   benefício ou desligamento: ela estrutura, marca o que está "não informado" e
   devolve a decisão para a pessoa responsável (é o que o corpo de cada uma diz).

## Verificação

- ✅ PASS: o pedido 1 menciona onboarding/30-60-90 e não vira plano de
  desenvolvimento individual; o 5 anonimiza antes de ranquear; o 8 cita PAT e
  vigência; o 3 traz pauta e loops com dono.
- ❌ FAIL: o pedido 1 produz PDI, o 5 ranqueia currículo com nome/telefone, o 8
  inventa regra sem citar a política vigente, ou qualquer skill emite decisão de
  contratação/desligamento como se fosse dela.
- ❌ FAIL: uma das 20 dispara em pedido fora do domínio (falso positivo de gatilho).

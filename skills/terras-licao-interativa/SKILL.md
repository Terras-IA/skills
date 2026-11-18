---
name: terras-licao-interativa
description: "Curso ou lição interativa em página única: cena isométrica animada (pessoas, serviços, filas, bancos) que muda passo a passo, com métricas, texto de problema e solução, quiz e progresso. Use para 'tela interativa que ensina X' ou simular processo. Página estática: terras-visual-explainer."
keywords: [licao interativa, curso interativo, simulador, explicacao passo a passo, isometrico, system design, processo, bpmn, fluxograma, topologia de rede, organograma, caso de uso, cena animada, tutorial visual, interactive lesson, step-by-step explainer]
---

# Lição interativa em cena isométrica

## Objetivo

Transformar um assunto que se entende vendo funcionar (arquitetura de sistema, processo de negócio, fluxo de atendimento, logística, segurança) numa página em que o leitor avança passo a passo e vê a cena mudar. Requisições ou documentos andam entre as peças, uma peça sobrecarrega ou cai, as métricas do topo ficam vermelhas, e a peça nova resolve o problema.

O motor está pronto e não muda por lição. O trabalho do agente é **o roteiro**, escrito como dados num `curso.json`. Inspiração: o curso de system design de Dilum Sanjaya (`designed-to-scale.vercel.app`). Este motor é implementação própria e não copia código nem textos dele.

| Pedido | Skill |
|--------|-------|
| Página que explica com diagrama estático, tabela ou Mermaid | `terras-visual-explainer` |
| GIF ou MP4 em loop para feed | `terras-animacao` |
| Vídeo narrado | `terras-video` |
| **Esta skill** | Página navegável, passo a passo, com cena viva, métricas e quiz |

## Regra dura

1. **Roteiro antes da cena.** Primeiro liste os passos (rótulo, tipo, o que muda na cena e nas métricas) e confira o arco em `references/roteiro.md`. Só depois escreva o JSON.
2. **Cada passo muda algo visível.** Texto que fala de algo que a cena não mostra é passo quebrado.
3. **Não editar o motor para uma lição.** Se faltar um recurso (tipo de nó, efeito), anote como melhoria do motor e mude `motor/` de propósito, para todas as lições, com o exemplo ainda passando.
4. **Validar e olhar antes de entregar.** `montar.py` sem erro e a folha do `capturar.py` lida com Read. Nó encavalado, rótulo cortado ou métrica que não mudou: corrija e capture de novo.
5. **Número inventado é ilustração.** Diga isso quando o assunto for técnico. Dado real leva fonte no texto do passo.

## Onde está

Fonte única: `skills/terras-licao-interativa/` no repositório `terras-skills`. Abaixo, `$SKILL_DIR` é a pasta deste arquivo.

```
motor/      modelo.html, cena.css, cena.js   (motor SVG, sem dependências)
scripts/    montar.py (valida e monta), capturar.py (foto de cada passo)
exemplos/   system-design.json               (sistemas: load balancer, 9 passos)
            contas-a-pagar.json              (processo de negócio: alçada e conferência, com placa e golpista)
            processo-seletivo.json           (processo em BPMN: raias, eventos, gateways e documentos)
            estilos.json                     (galeria: rede, organograma, fluxograma e caso de uso)
```

## Como trabalhar

1. **Entender o assunto e o leitor.** Uma lição é uma pergunta ("por que precisamos de load balancer?", "por que a conta a pagar precisa de alçada?"). Curso é um conjunto de lições em módulos.
2. **Perguntar o estilo antes de gerar.** Antes do roteiro, pergunte ao usuário as duas escolhas abaixo, de uma vez, com opções para escolher quando o agente tiver ferramenta de pergunta e no chat quando não tiver, com a sua recomendação primeiro. Não pergunte o que o pedido já disse ("em BPMN", "com a marca da Avancei") nem ao editar um `curso.json` que já tem `estilo`: mantenha o dele.

   | Escolha | Opções | Quando recomendar |
   |---------|--------|-------------------|
   | **Estilo** (`"estilo"` no `curso.json`) | `livre`: metáforas (pessoas, filas, bancos, pacotes andando) | sistema, arquitetura, tráfego, logística, segurança: o leitor precisa *ver* carga, gargalo e falha |
   | | `bpmn`: eventos, gateways, documentos e raias do BPMN 2.0 | processo de negócio com atores, decisões, prazos e documentos |
   | | `fluxograma`: terminal, processo, decisão, dados, documento | procedimento passo a passo de um ator só, rotina, algoritmo |
   | | `rede`: nuvem, firewall, roteador, switch, servidor, estação, Wi-Fi | topologia, segmentação, caminho do tráfego, segurança de rede |
   | | `organograma`: cartões de cargo e linhas de reporte | estrutura de equipe, quem responde a quem, vagas |
   | | `caso-de-uso`: atores e casos de uso UML com a fronteira do sistema | o que cada perfil faz num sistema, levantamento de requisitos |
   | **Aparência** (`"tema"`) | padrão da skill (claro e escuro) | uso interno, rascunho |
   | | marca: cores, fontes e logo de um cliente (`tema` em `references/formato.md`; identidade com `terras-identidade`) | material que sai para cliente ou público |

   A ferramenta de pergunta costuma aceitar até 4 opções: ofereça as 3 que mais servem ao assunto, com a recomendada primeiro; as outras ficam no "outro". Um curso pode misturar: `estilo` na lição vale sobre o do curso.

   Grave o estilo em `"estilo"`. Depois escolha as peças: em `livre`, pela tabela de metáforas de `references/roteiro.md`; nos outros, pela seção do estilo em `references/formato.md`. Exemplos: `exemplos/processo-seletivo.json` (bpmn) e `exemplos/estilos.json` (rede, organograma, fluxograma e caso de uso).
3. **Roteirizar** os passos: 6 a 12, pelo arco contexto → problema → solução → limite → troca → resumo com quiz.
4. **Escrever o `curso.json`** pelo `references/formato.md`. Comece copiando `exemplos/system-design.json` (livre) ou `exemplos/processo-seletivo.json` (bpmn). Declare na `cena` todos os nós que vão aparecer, com `"oculto": true`, e revele nos passos. Deixe 2 unidades de grade entre caixas.
5. **Montar** (valida antes; erro sai com código 1 e a lista do que corrigir):
   ```bash
   python3 "$SKILL_DIR/scripts/montar.py" curso.json -o curso.html
   ```
6. **Olhar** cada passo, sem animação, na folha de contato:
   ```bash
   python3 "$SKILL_DIR/scripts/capturar.py" curso.html --licao <id>    # --escuro para o tema escuro
   ```
   Ler `capturas-<id>/folha.jpg` e, se precisar de detalhe, um `passo-NN.png`.
   Na captura os pacotes ficam congelados num instante: densidade e pesados aparecem, mas a animação não. Se a mudança de um passo é só de fluxo, confira lendo o JSON ou junte uma mudança visível (selo, carga, métrica).
7. **Entregar.** O HTML é autocontido, só a fonte vem do Google Fonts. Para compartilhar como Artifact, monte com `--artifact` (tira o esqueleto, que o Artifact põe) e publique esse arquivo. Como site: `terras-vercel` / `terras-astro` com o HTML normal. Para guardar, salve o `curso.json` junto do HTML: o JSON é a fonte.

## O que a página já faz

- Árvore de módulos e lições com busca, e progresso salvo no navegador.
- Linha do tempo de passos, Voltar e Próximo, teclado (← → R Espaço) e link direto (`#<lição>-p<passo>`).
- Pacotes animados nas ligações: requisição, resposta, pesado e falha. Pausa e `prefers-reduced-motion` são respeitados.
- Tema claro e escuro, layout de celular e interface em português ou inglês (`idioma`).
- Ao fim de cada lição, botão para a próxima.

Vídeo da página, se pedirem: grave a tela navegando, ou junte as fotos do `capturar.py` com `terras-ffmpeg`.

## Referências

- `references/formato.md`: todos os campos de curso, lição, nó, ligação e passo.
- `references/roteiro.md`: arco da lição, regras de texto e o mapa de metáforas por domínio (sistemas, processos, atendimento, logística, segurança, finanças, igreja).

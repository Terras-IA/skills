---
name: terras-reconstrucao
version: 1.0.0
access: free
category: operacao
description: Checklist para reconstruir um sistema legado módulo a módulo — ordem de construção, documentação permanente do sistema antigo e decisão explícita de reescrever vs reaproveitar.
keywords: [sistema legado, reconstruir o conhecimento, ordem de construcao, mapear codigo antigo]
---

# Reconstrução de sistema legado, módulo a módulo

## Descrição

Quando um sistema legado vai ser reimplementado de propósito (não portado, não copiado por padrão), o conhecimento real dele — decisões de schema, acoplamento testado em produção, fronteiras que se provaram certas ou erradas — precisa estar documentado permanentemente antes do código novo, nunca só na memória de quem viveu o projeto.

Esta instrução é um checklist de **onde procurar** antes de escrever código de um módulo novo. Não é a fonte da verdade: a fonte são os documentos do projeto, e eles mudam — releia a cada módulo em vez de confiar em resumo memorizado.

## Quando usar

- Começar módulo novo de uma reimplementação de sistema legado.
- Entrar num projeto que já tem ordem de construção e listas de reescrever/reaproveitar.
- Antes de copiar qualquer trecho do sistema antigo.

## Como funciona

### Antes de começar um módulo

1. **Confirme onde o módulo está na ordem de construção.** A ordem segue lógica de risco e dependência — isolado primeiro, acoplado depois. Não é bloqueante, mas mudar a ordem exige motivo concreto, não preferência do momento.
2. **Leia a documentação do subsistema correspondente antes do inventário estrutural.** Os documentos de subsistema carregam o comportamento real (algoritmos, bugs de produção já corrigidos e por quê) que a tabela de tamanho/acoplamento não cobre. Confirme sempre no documento real — o mapeamento pode não ser 1:1.
3. **Decida reescrever vs reaproveitar pela lista explícita, não por intuição.** Só copiar/adaptar o que estiver explicitamente listado como seguro — não confie em cópia inline nem em memória: a lista cresce a cada módulo. Caso fora da lista: o padrão é **não copiar**; abra um ADR e decida lá (reescrever, reaproveitar adaptado ou como está) antes de codificar.
4. **Para redação exata, use a referência literal do projeto, não a memória.** Prompts, regex de segurança, DDL de migrations, catálogo de rotas — onde a redação literal importa, existe cópia fiel da fonte. Confira o índice dela para saber o que está incluído e o que ficou só documentado em comportamento.
5. **Se o módulo tocar camadas centrais, confira os gates de dependência.** Regras como "o núcleo nunca importa a camada de cima" precisam estar cobertas por verificação automatizada cedo, para pegar acoplamento indevido na origem em vez de descobrir depois de emaranhado.
6. **Ao entregar, siga a regra de validação do projeto.** Endpoint, script ou mudança de comportamento observável vem com artefato que exercita a implementação de ponta a ponta, além dos testes automatizados.

### Fora do escopo

- Não decide por você o que reescrever/reaproveitar quando o caso não está explicitamente listado — isso é decisão de design nova; documente depois de decidida, em vez de deixá-la implícita no código.
- Não substitui a leitura dos documentos reais — é um checklist de navegação, não um cache do conteúdo deles.

## Governança

- O conhecimento do sistema antigo é ativo do projeto: se a documentação não existe ainda, criá-la é parte da reconstrução, não tarefa paralela opcional.
- "Copia porque parece igual" sem item na lista explícita é a decisão mais cara da reconstrução — o default é não copiar, com decisão registrada.

## Critério de qualidade

O módulo começa bem quando: a posição na ordem de construção foi confirmada, o subsistema foi lido na fonte, a decisão reescrever/reaproveitar está explícita (lista ou ADR) e o gate de dependências cobre as camadas novas — tudo isso antes da primeira linha de código.

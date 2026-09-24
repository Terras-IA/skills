---
name: terras-api-sync
version: 1.0.0
access: free
category: operacao
description: Mudança de contrato de API é atualização atômica — servidor, SDK tipada e documentação humana no mesmo commit, com checklist por tipo de mudança.
keywords: [mudei a api, contrato da api, sincronizar sdk, atualizar a documentacao da api]
---

# Sincronia do contrato de API

## Descrição

Garante que a SDK tipada e a documentação humana evoluam **junto** com as rotas do servidor — no mesmo commit, não depois. O sintoma do descuido: o build do servidor passa, mas os consumidores da API quebram em runtime, e a documentação passa a mentir sobre o código.

## Quando usar

- Criar ou alterar rota, parâmetro, payload de resposta, evento de stream ou status code.
- Deprecar ou remover rota.
- Qualquer mudança no contrato público/compartilhado que outras superfícies consomem.

## Como funciona

### Regra de ouro

> **Toda mudança no contrato público da API (rota nova, parâmetro novo, resposta alterada, evento de stream ou status code alterado) vira 3 atualizações atômicas no mesmo commit:**
> 1. **Servidor** — implementação da rota.
> 2. **SDK tipada** — tipagem + método correspondente, incluindo os tipos de stream (eventos), não só as chamadas simples.
> 3. **Documentação humana** — a seção de contrato da API.

### Checklist por tipo de mudança

| Mudança no servidor | Atualizar na SDK | Atualizar na documentação |
|---|---|---|
| Nova rota | Método tipado correspondente | Linha na tabela de contrato |
| Novo parâmetro de query | Campo opcional no método | Documentar o parâmetro |
| Response muda de formato | Atualizar a interface | Atualizar exemplo de resposta |
| Novo evento de stream / campo em frame | Atualizar o tipo do evento + testes da SDK | Documentar o frame |
| Novo status code de erro | Adicionar no tipo de erro | Documentar o caso de erro |
| Rota deprecada/removida | Marcar ou remover | Marcar ou remover |

### Fluxo prático

1. Editar o servidor (rota nova/alterada).
2. Compilar e testar o servidor.
3. Editar a SDK no mesmo commit (tipos e métodos; se tocou stream, os eventos também).
4. Editar a documentação da API no mesmo commit.
5. Rodar a validação prática da rota contra o servidor real (ver procedimento de validação de entregas).

### Armadilhas comuns

| Armadilha | Prevenção |
|---|---|
| Esquecer a SDK → build do servidor passa, consumidores quebram em runtime | Rodar explicitamente o typecheck da SDK a cada mudança |
| Atualizar a documentação mas não a SDK (ou só o client simples, esquecendo os eventos de stream) | Checklist acima + commit atômico único |
| Mudar só o formato da resposta, não o request → SDK compila mas runtime falha | Smoke test contra servidor real |
| Rota de superfície criada no núcleo | A regra de fronteira roda antes — bloqueia na origem |

## Governança

- O contrato é a fronteira entre o servidor e todo consumidor: mudança de contrato sem as três pernas é entrega quebrada, mesmo com todos os testes verdes.
- Deprecação tem regra: marcar, documentar e dar janela — não remover rota de contrato sem aviso na documentação.

## Critério de qualidade

A entrega está pronta quando a mudança de contrato está no servidor, na SDK e na documentação **no mesmo commit**, com typecheck da SDK verde e a rota exercitada contra o servidor real.

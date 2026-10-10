---
name: terras-reverse-engineer
description: >-
  Investiga como uma feature funciona em software empacotado (app Electron/JS, site, APK,
  binário nativo, .NET, firmware, HAR) com o REA por MCP ou CLI, cada conclusão presa a
  uma evidência. Use quando o pedido for "como esse app faz X", "quero uma feature igual
  à do app Y", engenharia reversa, decompilar, inspecionar ASAR, APK, DLL, ELF, bundle de
  site ou comparar versões de um app. Não use para repositório de código-fonte aberto.
  Reverse engineering, decompile, binary analysis, feature investigation.
keywords: [engenharia reversa, reverse engineering, rea, decompilar, electron, asar, apk, binario, elf, dotnet, har, feature]
version: "6.3.0"
license: MIT
metadata:
  upstream: https://github.com/morluto/rea (skill reverse-engineer-anything v37, commit 60fbb2f)
  requisitos: Node.js >=22.19 (aqui 26.x). Motores opcionais por alvo (Ghidra, JADX, Binwalk, adb).
---

# terras-reverse-engineer

Descobrir como um software pronto faz algo, com prova, para decidir se e como construir a nossa versão.

## Objetivo

O REA (MIT) é um servidor MCP + CLI que inspeciona artefatos sem código-fonte e devolve resultados com Evidence IDs. Esta skill é o roteiro da casa por cima dele: escolher a ferramenta certa pelo tipo de alvo, trabalhar do resumo para o detalhe e entregar um relatório que separa observado, inferido e desconhecido. O protocolo completo do upstream está em `references/upstream-SKILL.md`.

## Onde está instalada

- MCP: servidor `rea` registrado no agente (escopo de usuário), rodando `npx -y rea-agents@6.3.0 mcp` (versão fixada; atualizar de propósito, não por `@latest`).
- CLI sem MCP: `npx -y rea-agents@6.3.0 <comando> --json > saida.json` (`--help` lista os comandos). O progresso sai em stderr. Flags do MCP como `detail: "summary"` **não** existem na CLI: lá, use `--token-limit`/`--filter-output` ou leia o JSON salvo com `python3`.
- Máquina do Everton (Linux x64): Node 26, Java 11, gdb presentes. **Não** instalados: Ghidra, Hopper, IDA, JADX, Binwalk/Unblob, adb, mitmdump. Logo, nativo e APK pedem motor antes; JavaScript/Electron, .NET, PE resources, ELF layout (com pwntools) e HAR funcionam já.

## Regra dura

1. **Só alvo que o usuário tem direito de analisar**: app instalado por ele, nosso produto, cliente com autorização, CTF. Nada de quebrar licença, DRM, anti-cheat ou extrair segredo/credencial de terceiro. Na dúvida sobre autorização, pergunte antes de abrir o alvo.
2. **Toda conclusão cita Evidence ID** e é marcada como *observado*, *inferido* ou *desconhecido*. Análise estática nunca vira "eu vi executar".
3. **Feature para o nosso produto = reimplementar o comportamento, não copiar código.** O relatório descreve mecanismo e contrato; o código nosso é escrito do zero, e escolhas de design nossas aparecem separadas do que foi observado.
4. **Não instalar motor sem pedir** (Ghidra, JADX etc.). Se o alvo exige um que falta, diga qual, o tamanho/origem, e pare nesse ramo.

## Como trabalhar

1. **Fixe o alvo.** "Meu app" sem nome ou caminho → pergunte qual. Nunca escolha um app de exemplo. Resolva o nome para um artefato instalado (ex.: `/opt/<App>/resources/app.asar`, `~/.local/share/...`, AppImage extraído).
   **App Electron grande trava a análise inteira** (medido em 2026-10-10: ZCode 327 MB/23 mil arquivos passou de 8 min; Claude Desktop 40 MB estourou o heap padrão de 4 GB e, com 8 GB, passou de 9 min presa em bundle minificado). Para esses: extraia o ASAR (`npx @electron/asar extract app.asar <dir>`), copie só o que interessa (`package.json`, entrada `main`, preload, o bundle da feature, sem `node_modules`) para uma pasta nova e analise essa pasta. Rode em background com `NODE_OPTIONS=--max-old-space-size=8192`. App pequeno roda em segundos.
2. **Roteie pelo tipo** (primeira ferramenta):
   | Alvo | Ferramenta |
   |---|---|
   | ASAR / pasta Electron ou JS extraída | `analyze_javascript_application` (`detail: "summary"` se grande) |
   | Site aberto no navegador do usuário | `list_browser_targets` |
   | HAR / captura mitmproxy salva | `inspect_web_network_capture` |
   | Assembly .NET (PE/CLI) | `inspect_managed_artifact` |
   | APK | `inspect_android_package` (precisa JADX) |
   | ZIP/APK/IPA/MSIX/DMG (inventário) | `open_binary` → `inspect_artifact` |
   | ELF Linux (layout, símbolos) | `inspect_binary_layout` |
   | Binário nativo (pseudocódigo) | `open_binary` (precisa Ghidra/IDA/Hopper) |
   | Firmware | `inspect_firmware_regions` (precisa Binwalk/Unblob) |
3. **Resumo primeiro.** Use o resultado padrão e o grafo; aprofunde só onde uma pergunta concreta ficou aberta. Resultado truncado ou `resource_constraint` → `inspect_analysis_view` com o `parent_evidence_id`, nunca repetir a mesma análise.
4. **Pedido amplo (várias features)** → checklist de perguntas, cada uma com a evidência que a responde; siga do ponto de entrada até o efeito; feche marcando cada pergunta como respondida, parcial ou aberta.
5. **Runtime só quando o estático não responde** e o usuário pediu: captura de browser/Electron/processo executa o alvo; declare o cenário e não amplie.
6. **Feche** com `close_binary` se abriu sessão nativa.

## Entrega

Relatório curto em PT-BR:

- **Pergunta** → **Resposta** em linguagem simples.
- **Como funciona**: passos do mecanismo, cada um com Evidence ID e marca (observado/inferido).
- **Desconhecidos e limites** da busca.
- **Se for construir**: contrato da feature (entradas, saídas, estados) e o que é decisão nossa. Implementação segue com as ferramentas normais de código.

## Se as tools não aparecerem

Tools `rea` ausentes na sessão = registro não carregado (reinicie a sessão) ou não feito. Diagnóstico e recuperação em `references/connection-and-recovery.md`. Enquanto isso, a CLI via `npx` faz o mesmo trabalho.

## Referências

- `references/upstream-SKILL.md` — skill original completa (roteamento fino, IDA, NativeAOT, EVM, crash dumps).
- `references/javascript-applications.md` — visões de módulo, trace de feature, comparação de versões.
- `references/native-and-artifacts.md` — binários nativos, .NET, arquivos, extração.
- `references/android-applications.md` — APK: manifest, classes, métodos.
- `references/runtime-observation.md` — observação passiva browser/Electron e reconciliação com o estático.
- `references/evidence-workflows.md` — paginação de evidência, comparações, verificação.
- `references/connection-and-recovery.md` — registro do MCP, motores ausentes, bloqueio do cliente.

## Fonte

Adaptada de `morluto/rea`, skill `.agents/skills/reverse-engineer-anything` (metadata version 37, pacote `rea-agents` 6.3.0, commit `60fbb2f`, 2026-10-11). Licença MIT, ver `LICENSE`. Os arquivos em `references/` são cópia sem alteração do upstream, em inglês.

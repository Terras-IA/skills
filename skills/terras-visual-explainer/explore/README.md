# Camada de exploração (diagramas Mermaid)

Da casa, não do upstream. Ideia de foco, alcance, caminho e evidência de código adaptada de
[tt-a1i/archify](https://github.com/tt-a1i/archify) (MIT); código escrito aqui.

Transforma um flowchart Mermaid do template `templates/mermaid-flowchart.html` em diagrama
explorável, sem mudar o template nem a geometria do desenho:

- **Clicar num bloco** (ou Tab + Enter): acende o bloco e os vizinhos, apaga o resto, e o painel
  abaixo do diagrama lista o que entra, o que sai (com o rótulo da seta) e onde está no código.
- **Tudo antes / Tudo depois**: acende tudo que chega até o bloco, ou tudo que sai dele, seguindo as setas.
- **Caminho**: origem e destino nos seletores; acende o caminho mais curto pelas setas e lista os
  passos. Sem caminho nesse sentido, diz isso.
- **Buscar** (atalho `/`): procura por rótulo ou id do bloco.
- **Esc** ou clique no fundo limpa. **Copiar link** guarda o estado na URL.
- **SRC n** no canto do bloco: ele tem `n` trechos de código como evidência.

Só funciona em `flowchart`/`graph`. Em outro tipo de diagrama o painel não aparece.

## Como ligar

1. Na `<section class="diagram-shell">`, acrescentar `data-explore="<id-curto>"`. O id vai no link
   (`#d=<id>&focus=...`) e separa diagramas na mesma página.
2. Colar o conteúdo de `explore/explore-layer.html` inteiro antes de `</body>`, depois do
   `<script type="module">` do template. Cuidado: o template tem a string `</body>` dentro do JS de
   "abrir em nova aba"; inserir antes da ÚLTIMA ocorrência.
3. Opcional, evidência de código: dentro da mesma `section`, logo depois do `diagram-source`:

```html
<script type="application/json" class="diagram-evidence">
{"repo": "https://github.com/dono/repo",
 "commit": "<40 caracteres de git rev-parse HEAD>",
 "nodes": {
   "Render": [{"path": "src/render.mjs", "lines": "186-192", "note": "monta a página"}],
   "CSS":    [{"path": "src/base.css"}]
 }}
</script>
```

As chaves de `nodes` são os ids dos blocos no Mermaid (`Render` em `Render["renderQuickSpec"]`).

## Regras da evidência

Vêm do `repository-authoring.md` do Archify, que acertou nisso:

- **Fixar o commit.** `git rev-parse HEAD`, 40 caracteres. Working tree suja: citar só o que está
  commitado e dizer na resposta quais arquivos estavam modificados.
- **URL sem credencial.** Tirar `usuario:token@` do `git remote get-url origin`. Origem SSH do GitHub
  ou GitLab vira `https://host/dono/repo`. Outro forge: `"urlTemplate": "{repo}/src/{commit}/{path}#L{start}-{end}"`.
  Repositório sem web ou que não deve linkar: `"linkMode": "local-only"` (mostra só `caminho:linhas`).
- **Evidência mora no bloco, não na seta.** A chamada, a escrita ou a leitura é citada no bloco que
  a faz. No máximo 3 trechos por bloco.
- **Linhas copiadas da leitura com número** (`nl -ba arquivo | sed -n '40,90p'`), nunca de memória.
- **Seta só para o que o código faz.** Função exportada que o caminho normal não chama não vira seta
  obrigatória. O que não deu para confirmar vai no texto da página como dúvida, não como seta.

## Conferir antes de entregar

```bash
node explore/check-evidence.mjs diagrams/pagina.html --repo-dir /caminho/do/repo
```

Confere em cada diagrama com `data-explore`: commit existe, URL sem credencial, bloco citado existe
na fonte Mermaid, arquivo existe no commit, faixa de linhas dentro do arquivo, no máximo 3 trechos.
Sai com código 1 e uma linha `FALHA [regra]` por problema. `--json` para máquina.

No navegador, depois de abrir a página, `window.veExploreReport` traz por diagrama: `unlabeled`
(setas sem rótulo, que ferem a regra de rotular toda seta), `evidenceUnknown`, `unmappedNodes` e
`unmappedEdges` (algo do grafo que não achou par no SVG). Os mesmos avisos saem no console.
Tudo vazio é o esperado.

## Limites

- Antes, depois e caminho seguem as setas desenhadas. Não é trace de execução nem análise de
  impacto; o painel diz isso ao leitor. Não chamar de "blast radius".
- O conferidor checa que a evidência existe, não que ela prova a seta. Isso continua sendo leitura.
- Depende do Mermaid 11 (ids `flowchart-<id>-N` nos nós, `data-id="L_<de>_<para>_N"` nas setas).
  Se uma versão nova mudar isso, `unmappedNodes`/`unmappedEdges` acusam.

## Revisão de arquitetura (antes e depois)

Sem ferramenta própria. Um diagrama do estado novo, com `classDef` marcando a mudança:

```text
classDef novo stroke-width:3px,stroke:#15803d
classDef removido stroke-dasharray:6 4,opacity:.55
classDef mudou stroke-width:3px,stroke:#b45309
class Cache novo
class LegacyQueue removido
```

Legenda obrigatória com as três marcas. A seta removida fica tracejada com rótulo `(removida)`.
Não afirmar risco ou segurança de merge a partir do desenho.

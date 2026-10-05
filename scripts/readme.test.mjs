// Testes do gerador da seção do catálogo no README, sobre repositórios de
// mentira, mais a guarda de sincronia do repositório real. Roda com: node --test scripts/
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { aplicarSecao, FIM, INICIO, montarSecao } from "./readme.mjs";

const skill = (nome, extra = "") => `---\nname: ${nome}\n${extra}description: "Faz ${nome}."\n---\n\n# ${nome}\n`;

function repo(arquivos, fora = {}, grupos = {}) {
  const raiz = mkdtempSync(join(tmpdir(), "terras-readme-"));
  const todos = { ...arquivos, "marketplace-fora.json": JSON.stringify(fora), "marketplace-grupos.json": JSON.stringify(grupos) };
  for (const [caminho, conteudo] of Object.entries(todos)) {
    const alvo = join(raiz, caminho);
    mkdirSync(dirname(alvo), { recursive: true });
    writeFileSync(alvo, conteudo);
  }
  return raiz;
}

test("a seção conta e lista as skills instaláveis em ordem alfabética, com link para a pasta", () => {
  const secao = montarSecao(repo({ "skills/terras-b/SKILL.md": skill("terras-b"), "skills/terras-a/SKILL.md": skill("terras-a") }));
  assert.match(secao, /\*\*2 skills instaláveis\*\* neste repositório\./);
  assert.match(secao, /\| \[`terras-a`\]\(skills\/terras-a\) \| Faz terras-a\. \|/);
  assert.ok(secao.indexOf("[`terras-a`]") < secao.indexOf("[`terras-b`]"), "ordem alfabética");
  assert.match(secao, /Ver a lista completa \(2 skills\)/);
});

test("skill de processo (.nao-instalar) e de projeto de cliente ficam fora da lista, mas contam no total", () => {
  const secao = montarSecao(
    repo(
      {
        "skills/terras-a/SKILL.md": skill("terras-a"),
        "skills/terras-processo/SKILL.md": skill("terras-processo"),
        "skills/terras-processo/.nao-instalar": "motivo",
        "skills/terras-cliente/SKILL.md": skill("terras-cliente"),
      },
      { "terras-cliente": "ligada a projeto de cliente" },
    ),
  );
  assert.match(secao, /\*\*1 skill instalável\*\* entre as 3 deste repositório/);
  assert.match(secao, /1 skill de processo do motor \(`\.nao-instalar`\) e 1 skill ligada a projeto de cliente/);
  assert.doesNotMatch(secao, /\[`terras-processo`\]/);
  assert.doesNotMatch(secao, /\[`terras-cliente`\]/);
});

test("skill que sai em plugin de grupo aparece apontando o plugin, sem link duplicado", () => {
  const secao = montarSecao(
    repo({ "skills/terras-audio/SKILL.md": skill("terras-audio") }, {}, { "terras-midia": { description: "Mídia.", skills: ["terras-audio"] } }),
  );
  assert.match(secao, /\[`terras-audio`\]\(skills\/terras-audio\) \| Faz terras-audio\. · Instale com o plugin `terras-midia`\. \|/);
});

test("descrição longa é cortada em frase inteira e o pipe que quebraria a célula vira \\|", () => {
  const longa = "Frase útil de exemplo. ".repeat(12).trim();
  const secao = montarSecao(
    repo({
      "skills/terras-a/SKILL.md": `---\nname: terras-a\ndescription: "Curta | com pipe."\n---\n`,
      "skills/terras-b/SKILL.md": `---\nname: terras-b\ndescription: ${longa}\n---\n`,
    }),
  );
  assert.match(secao, /Curta \\\| com pipe\./);
  const linha = secao.split("\n").find((l) => l.includes("[`terras-b`]"));
  assert.match(linha, /Frase útil de exemplo\.\s*\|$/, "corta em frase inteira, sem reticências no meio");
  assert.ok(linha.length < 250, `resumo cabe na linha da tabela: ${linha.length} caracteres`);
});

test("sem frase inteira no limite, o corte é em palavra inteira e sem conectivo pendurado", () => {
  const longa = `${"a".repeat(150)} de ${"b".repeat(40)}`;
  const secao = montarSecao(repo({ "skills/terras-a/SKILL.md": `---\nname: terras-a\ndescription: ${longa}\n---\n` }));
  const linha = secao.split("\n").find((l) => l.includes("[`terras-a`]"));
  assert.match(linha, /a{150}…\s*\|$/, "corta depois da palavra inteira, sem o conectivo");
  assert.doesNotMatch(linha, /de…/, "conectivo pendurado sai");
  assert.doesNotMatch(linha, /b+…/, "não sobra fragmento da palavra cortada");
});

test("aplicarSecao troca só o miolo entre os marcadores e recusa README sem eles", () => {
  const readme = `# T\n\ntexto antes\n\n${INICIO}\nvelho\n${FIM}\n\ntexto depois\n`;
  assert.equal(aplicarSecao(readme, `${INICIO}\nnovo\n${FIM}`), `# T\n\ntexto antes\n\n${INICIO}\nnovo\n${FIM}\n\ntexto depois\n`);
  assert.throws(() => aplicarSecao("# T\nsem marcador\n", `${INICIO}\nx\n${FIM}`), /marcadores/);
});

test("o README do repositório está em dia com o catálogo (rode npm run readme)", () => {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const atual = readFileSync(join(raiz, "README.md"), "utf8");
  assert.equal(atual, aplicarSecao(atual, montarSecao(raiz)));
});

// Testes do gerador do marketplace sobre repositórios de mentira, mais a
// guarda de sincronia do repositório real. Roda com: node --test scripts/
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { gruposDesatualizados, montarManifesto, sincronizarGrupos } from "./marketplace.mjs";

const skill = (nome, extra = "") => `---\nname: ${nome}\n${extra}description: "Faz ${nome}."\nkeywords: [exemplo, coisa util]\n---\n\n# ${nome}\n`;
const BASE = { name: "terras", owner: { name: "Dono" }, plugins: [] };

function repo(arquivos, manifesto = BASE, fora = {}) {
  const raiz = mkdtempSync(join(tmpdir(), "terras-mkt-"));
  const todos = { ...arquivos, ".claude-plugin/marketplace.json": JSON.stringify(manifesto), "marketplace-fora.json": JSON.stringify(fora) };
  for (const [caminho, conteudo] of Object.entries(todos)) {
    const alvo = join(raiz, caminho);
    mkdirSync(dirname(alvo), { recursive: true });
    writeFileSync(alvo, conteudo);
  }
  return raiz;
}
const nomes = (m) => m.plugins.map((p) => p.name);

test("cada skill instalável vira um plugin que aponta para a própria pasta, sem cópia", () => {
  const m = montarManifesto(repo({ "skills/terras-b/SKILL.md": skill("terras-b", "version: 1.2.0\ncategory: financeiro\n"), "skills/terras-a/SKILL.md": skill("terras-a") }));
  assert.deepEqual(nomes(m), ["terras-a", "terras-b"], "ordem alfabética: o arquivo gerado é estável");
  const b = m.plugins[1];
  assert.equal(b.source, "./skills/terras-b");
  assert.equal(b.strict, false);
  assert.deepEqual(b.skills, ["./"]);
  assert.equal(b.version, "1.2.0");
  assert.equal(b.category, "financeiro");
  assert.equal(b.description, "Faz terras-b.", "aspas do frontmatter saem");
  assert.deepEqual(b.keywords, ["exemplo", "coisa util"]);
  assert.equal(m.plugins[0].version, "1.0.0", "sem versão no cabeçalho: 1.0.0");
});

test("skill de processo do motor (.nao-instalar) e skill da lista de fora não são publicadas", () => {
  const m = montarManifesto(
    repo(
      { "skills/terras-a/SKILL.md": skill("terras-a"), "skills/terras-processo/SKILL.md": skill("terras-processo"), "skills/terras-processo/.nao-instalar": "motivo", "skills/terras-cliente/SKILL.md": skill("terras-cliente") },
      BASE,
      { "terras-cliente": "ligada a projeto de cliente" },
    ),
  );
  assert.deepEqual(nomes(m), ["terras-a"]);
});

test("plugin escrito à mão (source em ./plugins/) é preservado como está; os gerados são refeitos", () => {
  const manual = { name: "terras-manual", description: "à mão", version: "2.0.0", source: "./plugins/terras-manual" };
  const velho = { name: "terras-sumiu", description: "skill apagada", source: "./skills/terras-sumiu", strict: false, skills: ["./"] };
  const m = montarManifesto(repo({ "skills/terras-a/SKILL.md": skill("terras-a") }, { ...BASE, description: "fica", plugins: [manual, velho] }));
  assert.deepEqual(nomes(m), ["terras-manual", "terras-a"], "manuais primeiro, gerados depois; o que sumiu do catálogo sai");
  assert.deepEqual(m.plugins[0], manual);
  assert.equal(m.description, "fica", "o topo do manifesto é preservado");
});

test("nome repetido entre plugin à mão e skill do catálogo é erro, não sobrescrita silenciosa", () => {
  const manual = { name: "terras-a", description: "à mão", source: "./plugins/terras-a" };
  assert.throws(() => montarManifesto(repo({ "skills/terras-a/SKILL.md": skill("terras-a") }, { ...BASE, plugins: [manual] })), /terras-a/);
});

test("descrição longa é cortada em frase inteira para o manifesto, sem reticências no meio da palavra", () => {
  const longa = `${"Primeira frase útil. ".repeat(20)}`.trim();
  const m = montarManifesto(repo({ "skills/terras-a/SKILL.md": `---\nname: terras-a\ndescription: ${longa}\nkeywords: [x]\n---\n` }));
  assert.ok(m.plugins[0].description.length <= 300);
  assert.match(m.plugins[0].description, /útil\.$/);
});

const GRUPO = { "terras-midia": { description: "Áudio e vídeo juntos.", skills: ["terras-audio", "terras-video"] } };
const repoComGrupo = () => {
  const raiz = repo({
    "skills/terras-audio/SKILL.md": skill("terras-audio"),
    "skills/terras-video/SKILL.md": skill("terras-video"),
    "skills/terras-video/scripts/build.py": "print('ok')\n",
    "skills/terras-a/SKILL.md": skill("terras-a"),
  });
  writeFileSync(join(raiz, "marketplace-grupos.json"), JSON.stringify(GRUPO));
  return raiz;
};

test("grupo: skills que dependem da pasta vizinha saem juntas num plugin só, e não como plugins soltos", () => {
  const raiz = repoComGrupo();
  const m = montarManifesto(raiz);
  assert.deepEqual(nomes(m), ["terras-midia", "terras-a"]);
  assert.equal(m.plugins[0].source, "./plugins/terras-midia");
  assert.equal(m.plugins[0].strict, undefined, "plugin de grupo tem layout padrão (plugin.json + skills/)");
  // Rodar de novo sobre o manifesto já gerado não duplica o grupo.
  writeFileSync(join(raiz, ".claude-plugin/marketplace.json"), JSON.stringify(m));
  assert.deepEqual(nomes(montarManifesto(raiz)), ["terras-midia", "terras-a"]);
});

test("grupo: a cópia em plugins/ é gerada do catálogo, lado a lado, e a divergência é detectada", () => {
  const raiz = repoComGrupo();
  assert.deepEqual(gruposDesatualizados(raiz), ["terras-midia"], "antes de sincronizar, falta a cópia");
  sincronizarGrupos(raiz);
  assert.ok(existsSync(join(raiz, "plugins/terras-midia/skills/terras-video/scripts/build.py")));
  assert.ok(existsSync(join(raiz, "plugins/terras-midia/skills/terras-audio/SKILL.md")), "vizinhas ficam lado a lado: ../terras-audio resolve");
  assert.equal(JSON.parse(readFileSync(join(raiz, "plugins/terras-midia/.claude-plugin/plugin.json"), "utf8")).name, "terras-midia");
  assert.deepEqual(gruposDesatualizados(raiz), []);
  writeFileSync(join(raiz, "skills/terras-video/scripts/build.py"), "print('mudou')\n");
  assert.deepEqual(gruposDesatualizados(raiz), ["terras-midia"], "editar a skill sem regerar reprova");
});

test("grupo que cita skill inexistente ou fora do marketplace é erro", () => {
  const raiz = repoComGrupo();
  writeFileSync(join(raiz, "marketplace-grupos.json"), JSON.stringify({ "terras-midia": { description: "x", skills: ["terras-audio", "terras-sumiu"] } }));
  assert.throws(() => montarManifesto(raiz), /terras-sumiu/);
});

test("o marketplace.json do repositório está em dia com o catálogo (rode npm run marketplace)", () => {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const atual = JSON.parse(readFileSync(join(raiz, ".claude-plugin/marketplace.json"), "utf8"));
  assert.deepEqual(atual, montarManifesto(raiz));
  assert.deepEqual(gruposDesatualizados(raiz), [], "cópia de grupo em plugins/ diverge do catálogo");
});

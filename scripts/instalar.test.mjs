// Testes do instalador com um HOME de mentira. Roda com: node --test scripts/*.test.mjs
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, readlinkSync, realpathSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = fileURLToPath(new URL("..", import.meta.url));
const SCRIPT = join(RAIZ, "scripts/instalar.sh");
const SKILLS = join(RAIZ, "skills");
const INSTALAVEIS = readdirSync(SKILLS).filter((n) => !existsSync(join(SKILLS, n, ".nao-instalar"))).sort();
const [A, B] = INSTALAVEIS;

function home(pastas = [".claude/skills", ".zcode/skills"]) {
  const h = mkdtempSync(join(tmpdir(), "terras-home-"));
  for (const p of pastas) mkdirSync(join(h, p), { recursive: true });
  return h;
}
const roda = (h, ...args) => execFileSync("bash", [SCRIPT, ...args], { env: { ...process.env, HOME: h }, encoding: "utf8" });

test("sem --aplicar não muda nada", () => {
  const h = home();
  const saida = roda(h);
  assert.match(saida, /simulação/i);
  assert.equal(readdirSync(join(h, ".claude/skills")).length, 0);
});

test("--aplicar cria um link por skill em cada pasta de agente que existe", () => {
  const h = home();
  roda(h, "--aplicar");
  const esperado = readdirSync(SKILLS).filter((n) => !existsSync(join(SKILLS, n, ".nao-instalar"))).length;
  for (const p of [".claude/skills", ".zcode/skills"]) {
    const itens = readdirSync(join(h, p));
    assert.equal(itens.length, esperado, p);
    const link = join(h, p, A);
    assert.ok(lstatSync(link).isSymbolicLink());
    assert.equal(realpathSync(link), realpathSync(join(SKILLS, A)));
  }
  assert.ok(!existsSync(join(h, ".codex/skills")), "não cria pasta de agente que não existe");
});

test("pasta real no caminho vai para o backup antes do link", () => {
  const h = home();
  mkdirSync(join(h, ".zcode/skills", B));
  writeFileSync(join(h, ".zcode/skills", B, "SKILL.md"), "versão antiga");
  roda(h, "--aplicar");
  assert.ok(lstatSync(join(h, ".zcode/skills", B)).isSymbolicLink());
  const backups = readdirSync(join(h, ".terras-skills-backup"));
  assert.equal(backups.length, 1);
  const salvo = join(h, ".terras-skills-backup", backups[0], "zcode", B, "SKILL.md");
  assert.equal(readFileSync(salvo, "utf8"), "versão antiga");
});

test("link que já aponta para o repositório fica como está e rodar de novo não faz backup", () => {
  const h = home();
  roda(h, "--aplicar");
  const saida = roda(h, "--aplicar");
  assert.match(saida, /0 alterado/);
  assert.ok(!existsSync(join(h, ".terras-skills-backup")));
});

test("link apontando para outro lugar é trocado e o destino antigo registrado", () => {
  const h = home();
  mkdirSync(join(h, "antigo", A), { recursive: true });
  symlinkSync(join(h, "antigo", A), join(h, ".claude/skills", A));
  roda(h, "--aplicar");
  assert.equal(realpathSync(join(h, ".claude/skills", A)), realpathSync(join(SKILLS, A)));
  const backups = readdirSync(join(h, ".terras-skills-backup"));
  const registro = readFileSync(join(h, ".terras-skills-backup", backups[0], "claude", `${A}.link`), "utf8");
  assert.equal(registro.trim(), join(h, "antigo", A));
  assert.ok(existsSync(join(h, "antigo", A)), "o destino do link antigo não é tocado");
  assert.ok(readlinkSync(join(h, ".claude/skills", A)).startsWith("/"));
});

test("~/.agents/skills não recebe link (nome duplicado com ~/.zcode fica ambíguo)", () => {
  const h = home([".zcode/skills", ".agents/skills"]);
  roda(h, "--aplicar");
  assert.equal(readdirSync(join(h, ".agents/skills")).length, 0);
});

test("skill com .nao-instalar não recebe link, e o link que já existia para ela sai", () => {
  const h = home();
  roda(h, "--aplicar");
  const alvo = readdirSync(SKILLS).find((n) => existsSync(join(SKILLS, n, ".nao-instalar")));
  assert.ok(alvo, "nenhuma skill marcada com .nao-instalar no repositório");
  assert.ok(!existsSync(join(h, ".claude/skills", alvo)), `${alvo} foi instalada`);
  symlinkSync(join(SKILLS, alvo), join(h, ".claude/skills", alvo));
  const saida = roda(h, "--aplicar");
  assert.match(saida, new RegExp(`remove link\\s+.*${alvo}`));
  assert.ok(!existsSync(join(h, ".claude/skills", alvo)));
});

test("pasta real com o nome de uma skill .nao-instalar não é tocada", () => {
  const h = home();
  const alvo = readdirSync(SKILLS).find((n) => existsSync(join(SKILLS, n, ".nao-instalar")));
  mkdirSync(join(h, ".claude/skills", alvo));
  roda(h, "--aplicar");
  assert.ok(lstatSync(join(h, ".claude/skills", alvo)).isDirectory());
  assert.ok(!existsSync(join(h, ".terras-skills-backup")));
});

test("link para skill que saiu do repositório é removido; link alheio fica", () => {
  const h = home();
  symlinkSync(join(SKILLS, "terras-que-nao-existe-mais"), join(h, ".claude/skills/terras-que-nao-existe-mais"));
  mkdirSync(join(h, "outro/terras-de-outro"), { recursive: true });
  symlinkSync(join(h, "outro/terras-de-outro"), join(h, ".claude/skills/terras-de-outro"));
  const saida = roda(h, "--aplicar");
  assert.match(saida, /remove órfão/);
  assert.ok(!existsSync(join(h, ".claude/skills/terras-que-nao-existe-mais")) && !lstatExiste(join(h, ".claude/skills/terras-que-nao-existe-mais")));
  assert.ok(lstatSync(join(h, ".claude/skills/terras-de-outro")).isSymbolicLink());
});

function lstatExiste(p) {
  try { lstatSync(p); return true; } catch { return false; }
}

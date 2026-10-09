// Testes do gerador de pacotes (zip para upload no claude.ai e no ChatGPT)
// sobre repositórios de mentira, mais a guarda do repositório real: toda skill
// instalável daqui passa nos limites do upload.
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { inflateRawSync } from "node:zlib";
import { conferir, empacotar, gerarPacotes, skillsEmpacotaveis } from "./pacotes.mjs";

const skill = (nome, extra = "", descricao = `Faz ${nome}.`) => `---\nname: ${nome}\ndescription: "${descricao}"\n---\n\n# ${nome}\n${extra}`;

function repo(arquivos, { fora = {}, ignorados = {} } = {}) {
  const raiz = mkdtempSync(join(tmpdir(), "terras-pac-"));
  const escrever = (lista) => {
    for (const [caminho, conteudo] of Object.entries(lista)) {
      const alvo = join(raiz, caminho);
      mkdirSync(dirname(alvo), { recursive: true });
      writeFileSync(alvo, conteudo);
    }
  };
  escrever({ ...arquivos, "marketplace-fora.json": JSON.stringify(fora) });
  execFileSync("git", ["init", "-q", raiz]);
  execFileSync("git", ["-C", raiz, "add", "."]);
  escrever(ignorados); // existe no disco e não está no git
  return raiz;
}

/** Leitor do diretório central: [{ caminho, dados }]. Só o que o gerador escreve. */
function lerZip(buf) {
  const fim = buf.lastIndexOf(Buffer.from([0x50, 0x4b, 0x05, 0x06]));
  let o = buf.readUInt32LE(fim + 16);
  const entradas = [];
  for (let i = 0; i < buf.readUInt16LE(fim + 10); i++) {
    const metodo = buf.readUInt16LE(o + 10);
    const tamanho = buf.readUInt32LE(o + 20);
    const nlen = buf.readUInt16LE(o + 28);
    const caminho = buf.toString("utf8", o + 46, o + 46 + nlen);
    const local = buf.readUInt32LE(o + 42);
    const inicio = local + 30 + buf.readUInt16LE(local + 26) + buf.readUInt16LE(local + 28);
    const corpo = buf.subarray(inicio, inicio + tamanho);
    entradas.push({ caminho, dados: metodo === 8 ? inflateRawSync(corpo) : corpo });
    o += 46 + nlen + buf.readUInt16LE(o + 30) + buf.readUInt16LE(o + 32);
  }
  return entradas;
}

test("o zip tem a pasta da skill no topo, com o conteúdo íntegro, e só o que o git rastreia", () => {
  const corpo = "x".repeat(5000);
  const raiz = repo(
    { "skills/terras-a/SKILL.md": skill("terras-a"), "skills/terras-a/scripts/run.sh": "echo oi\n", "skills/terras-a/references/longo.md": corpo },
    { ignorados: { "skills/terras-a/references/perfil.md": "dado pessoal", "skills/terras-a/config.json": "{}" } },
  );
  const entradas = lerZip(empacotar(raiz, "terras-a"));
  assert.deepEqual(entradas.map((e) => e.caminho), ["terras-a/SKILL.md", "terras-a/references/longo.md", "terras-a/scripts/run.sh"]);
  assert.equal(entradas[1].dados.toString(), corpo, "deflate ida e volta");
  assert.equal(entradas[2].dados.toString(), "echo oi\n", "arquivo pequeno vai sem compressão e íntegro");
});

test("o zip é reprodutível: mesmo conteúdo, mesmos bytes", () => {
  const raiz = repo({ "skills/terras-a/SKILL.md": skill("terras-a") });
  assert.ok(empacotar(raiz, "terras-a").equals(empacotar(raiz, "terras-a")));
});

test("se o unzip existe na máquina, ele aceita o zip", (t) => {
  try { execFileSync("unzip", ["-v"], { stdio: "ignore" }); } catch { return t.skip("sem unzip na máquina"); }
  const raiz = repo({ "skills/terras-a/SKILL.md": skill("terras-a"), "skills/terras-a/b.md": "y".repeat(3000) });
  const destino = join(raiz, "dist");
  gerarPacotes(raiz, destino);
  execFileSync("unzip", ["-tq", join(destino, "terras-a.zip")]);
});

test("skill de processo e skill de cliente não viram pacote", () => {
  const raiz = repo(
    { "skills/terras-a/SKILL.md": skill("terras-a"), "skills/terras-proc/SKILL.md": skill("terras-proc"), "skills/terras-proc/.nao-instalar": "x", "skills/terras-cli/SKILL.md": skill("terras-cli") },
    { fora: { "terras-cli": "cliente" } },
  );
  assert.deepEqual(skillsEmpacotaveis(raiz), ["terras-a"]);
  assert.throws(() => gerarPacotes(raiz, join(raiz, "dist"), ["terras-cli"]), /fora do marketplace/);
});

test("o que o upload recusaria é erro, e nenhum pacote é gravado", () => {
  const raiz = repo({
    "skills/terras-a/SKILL.md": skill("terras-outro"),
    "skills/terras-b/SKILL.md": skill("terras-b", "", "d".repeat(1025)),
    "skills/terras-c/SKILL.md": skill("terras-c"),
  });
  assert.match(conferir(raiz, "terras-a").erros.join(), /diferente da pasta/);
  assert.match(conferir(raiz, "terras-b").erros.join(), /1025 caracteres/);
  const destino = join(raiz, "dist");
  assert.throws(() => gerarPacotes(raiz, destino), /terras-a: .*\n.*terras-b/);
  assert.throws(() => readFileSync(join(destino, "terras-c.zip")), /ENOENT/);
});

test("citar a pasta vizinha é aviso, não erro", () => {
  const raiz = repo({ "skills/terras-a/SKILL.md": skill("terras-a", "Use ../terras-b/scripts/x.sh e ../terras-a/y.\n") });
  assert.deepEqual(conferir(raiz, "terras-a"), { erros: [], avisos: ["cita a pasta vizinha terras-b: suba o pacote dela também"] });
});

test("repositório real: toda skill instalável passa nos limites do upload", () => {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const ruins = skillsEmpacotaveis(raiz).map((n) => [n, conferir(raiz, n).erros]).filter(([, e]) => e.length);
  assert.deepEqual(ruins, []);
});

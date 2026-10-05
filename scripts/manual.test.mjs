// Guarda de sincronia do MANUAL.md com as skills do repositório.
// Roda com: node --test scripts/
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { gerarManual } from "./manual.mjs";

test("o MANUAL.md está em dia com as skills (rode node scripts/manual.mjs)", () => {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const caminho = join(raiz, "MANUAL.md");
  const atual = existsSync(caminho) ? readFileSync(caminho, "utf8") : "";
  assert.equal(atual, gerarManual(raiz), "MANUAL.md desatualizado: rode `node scripts/manual.mjs`");
});

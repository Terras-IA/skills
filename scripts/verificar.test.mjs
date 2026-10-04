// Testes do verificador sobre repositórios de mentira montados em diretório
// temporário. Roda com: node --test scripts/
import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { verificar } from "./verificar.mjs";

const SKILL_OK = "---\nname: terras-exemplo\ndescription: Faz uma coisa util.\nkeywords: [exemplo, coisa util]\n---\n\n# Exemplo\n";

function repo(arquivos, catalogo = []) {
  const raiz = mkdtempSync(join(tmpdir(), "terras-skills-"));
  for (const [caminho, conteudo] of Object.entries(arquivos)) {
    const alvo = join(raiz, caminho);
    mkdirSync(dirname(alvo), { recursive: true });
    writeFileSync(alvo, conteudo);
  }
  writeFileSync(join(raiz, "catalogo.json"), JSON.stringify({ skills: catalogo.map((nome) => ({ nome })) }));
  return raiz;
}
const regras = (raiz) => verificar(raiz).map((p) => p.regra);

test("repositório correto não tem problema", () => {
  assert.deepEqual(verificar(repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK }, ["terras-exemplo"])), []);
});

test("pasta sem prefixo da casa é recusada", () => {
  const raiz = repo({ "skills/exemplo/SKILL.md": SKILL_OK.replace("terras-exemplo", "exemplo") });
  assert.ok(regras(raiz).includes("prefixo"));
});

test("prefixo terrasia- é aceito", () => {
  const raiz = repo({ "skills/terrasia-exemplo/SKILL.md": SKILL_OK.replace("terras-exemplo", "terrasia-exemplo") }, ["terrasia-exemplo"]);
  assert.deepEqual(verificar(raiz), []);
});

test("name do SKILL.md diferente da pasta é recusado", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK.replace("name: terras-exemplo", "name: terras-outro") });
  assert.ok(regras(raiz).includes("nome"));
});

test("CRLF no cabeçalho é recusado", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK.replace(/\n/g, "\r\n") });
  assert.ok(regras(raiz).includes("crlf"));
});

test("skill do catálogo sem keywords é recusada", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK.replace(/^keywords:.*\n/m, "") }, ["terras-exemplo"]);
  assert.ok(regras(raiz).includes("catalogo"));
});

test("skill do catálogo com descrição acima de 280 é recusada", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK.replace("Faz uma coisa util.", "x".repeat(281)) }, ["terras-exemplo"]);
  assert.ok(regras(raiz).includes("catalogo"));
});

test("o catálogo lê catalogo.md quando ele existe", () => {
  const raiz = repo(
    {
      "skills/terras-exemplo/SKILL.md": SKILL_OK.replace(/^keywords:.*\n/m, ""),
      "skills/terras-exemplo/catalogo.md": SKILL_OK,
    },
    ["terras-exemplo"],
  );
  assert.deepEqual(verificar(raiz), []);
});

test("skill listada no catálogo sem pasta é recusada", () => {
  assert.ok(regras(repo({}, ["terras-fantasma"])).includes("catalogo"));
});

for (const trecho of [
  "rode python3 ~/.claude/skills/terras-exemplo/x.py",
  "a canonica e ~/.zcode/skills/terras-exemplo",
  'BASE="$HOME/.zcode/skills"',
  "link em ~/.config/opencode/skills",
  "no Claude Code, use a ferramenta",
  "pergunte com AskUserQuestion",
  "publique o plano com TodoWrite",
  "dispare subagentes em paralelo",
  "leia CLAUDE_SESSION_ID",
]) {
  test(`dependência de harness é recusada: ${trecho}`, () => {
    const raiz = repo({ "skills/terras-exemplo/SKILL.md": `${SKILL_OK}\n${trecho}\n` });
    assert.ok(regras(raiz).includes("harness"), trecho);
  });
}

test("citar Claude como IA-alvo e CLAUDE.md como arquivo não é dependência", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": `${SKILL_OK}\nIA-alvo: ChatGPT, Claude ou Gemini. Leia o CLAUDE.md do repo.\n` });
  assert.deepEqual(verificar(raiz), []);
});

test("dependência de harness também é recusada em script", () => {
  const raiz = repo({
    "skills/terras-exemplo/SKILL.md": SKILL_OK,
    "skills/terras-exemplo/scripts/x.py": 'CFG = "~/.zcode/v2/provider_config.json"\n',
  });
  assert.ok(regras(raiz).includes("harness"));
});

test("caminho listado em .vendor fica fora da regra de harness", () => {
  const raiz = repo({
    "skills/terras-exemplo/SKILL.md": SKILL_OK,
    "skills/terras-exemplo/.vendor": "scripts/lib/  # upstream exemplo, MIT\n",
    "skills/terras-exemplo/scripts/lib/motor.py": "# funciona no Claude Code e no Codex\n",
  });
  assert.deepEqual(verificar(raiz), []);
});

test("marca de origem no texto da skill é recusada", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": `${SKILL_OK}\nUse o design system do iFood Benefícios.\n` });
  assert.ok(regras(raiz).includes("origem"));
});

test("segredo no conteúdo é recusado", () => {
  const raiz = repo({
    "skills/terras-exemplo/SKILL.md": SKILL_OK,
    "skills/terras-exemplo/scripts/x.py": `KEY = "sk-${"a".repeat(32)}"\n`,
  });
  assert.ok(regras(raiz).includes("segredo"));
});

test("arquivo de credencial ou cache é recusado", () => {
  for (const arq of ["config.json", ".env", "scripts/__pycache__/x.pyc"]) {
    const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK, [`skills/terras-exemplo/${arq}`]: "x" });
    assert.ok(regras(raiz).includes("lixo"), arq);
  }
});

test("config.example.json é permitido", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK, "skills/terras-exemplo/config.example.json": "{}" });
  assert.deepEqual(verificar(raiz), []);
});

test("marca de origem em script também é recusada", () => {
  const raiz = repo({
    "skills/terras-exemplo/SKILL.md": SKILL_OK,
    "skills/terras-exemplo/scripts/x.py": "# tokens do design system do iFood\n",
  });
  assert.ok(regras(raiz).includes("origem"));
});

test("CNPJ ou CPF no conteúdo é recusado, inclusive em CSV de exemplo", () => {
  for (const [arq, txt] of [
    ["depara.example.csv", "cnpj,nome\n12.345.678/0001-90,Empresa\n"],
    ["references/x.md", "CPF do titular: 123.456.789-09\n"],
  ]) {
    const raiz = repo({ "skills/terras-exemplo/SKILL.md": SKILL_OK, [`skills/terras-exemplo/${arq}`]: txt });
    assert.ok(regras(raiz).includes("dado-pessoal"), arq);
  }
});

test("e-mail real no conteúdo é recusado", () => {
  const raiz = repo({ "skills/terras-exemplo/SKILL.md": `${SKILL_OK}\nEnvie para fulano@empresa.com.br.\n` });
  assert.ok(regras(raiz).includes("dado-pessoal"));
});

test("e-mail de exemplo, licença de fonte e código vendorizado passam", () => {
  const raiz = repo({
    "skills/terras-exemplo/SKILL.md": `${SKILL_OK}\nEx.: user@example.com, you@example.org, your_email@gmail.com.\n`,
    "skills/terras-exemplo/fonts/Fonte-OFL.txt": "Copyright 2011 autor@fundidora.com\n",
    "skills/terras-exemplo/.vendor": "scripts/\n",
    "skills/terras-exemplo/scripts/x.py": "contato = 'hello@upstream.ai'\n",
  });
  assert.deepEqual(verificar(raiz), []);
});

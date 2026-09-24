#!/usr/bin/env node
// Verificador do repositório de skills. Sem dependência: só node:*.
//
// Barra o que já custou retrabalho: skill sem o prefixo terras-, cabeçalho que
// o parser do motor recusa, skill do catálogo sem keywords (liberada e muda),
// dependência de um harness específico, marca de terceiro que sobrou de
// importação, segredo e arquivo de credencial ou cache.
//
//   node scripts/verificar.mjs            # verifica o repositório
//   node scripts/verificar.mjs <raiz>     # verifica outra raiz (testes)
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const NOME_RE = /^terras-[a-z0-9]+(-[a-z0-9]+)*$/;
const MAX_CABECALHO = 1024; // teto de frontmatter de skill de agente
const MAX_DESCRICAO_CATALOGO = 280; // teto do parser do motor
const TEXTO = /\.(md|py|sh|mjs|js|cjs|ts|json|txt|html|css|toml|ya?ml)$/i;

// Dependência de harness: caminho de instalação de um agente específico, nome
// de ferramenta de um agente específico, variável de ambiente de um agente.
// "Claude" como IA-alvo e CLAUDE.md como arquivo de repo são conteúdo e passam.
const HARNESS = [
  [/(~|\$HOME|\$\{HOME\})\/\.(claude|zcode|codex|agents)\b/, "caminho de instalação de agente"],
  [/\.config\/opencode\b/, "caminho de instalação de agente"],
  [/\bClaude Code\b/, "nome de harness"],
  [/\b(AskUserQuestion|TodoWrite|WebFetch|WebSearch)\b/, "ferramenta de harness"],
  [/\bsub-?agent/i, "ferramenta de harness"],
  [/\bCLAUDE_[A-Z][A-Z_]*\b/, "variável de ambiente de harness"],
];
const ORIGEM = [
  [/\bifood\b/i, "iFood"],
  [/fala a[íi]/i, "Fala Aí"],
  [/\balli\b/i, "Alli"],
  [/all faces/i, "All Faces"],
];
const SEGREDO = [
  /\bsk-[A-Za-z0-9_-]{24,}/,
  /\bghp_[A-Za-z0-9]{24,}/,
  /\bAKIA[0-9A-Z]{16}\b/,
  /-----BEGIN [A-Z ]*PRIVATE KEY-----/,
  /"(api_?key|apiKey|access_token|refresh_token|client_secret)"\s*:\s*"[^"<.]{16,}"/,
];
const LIXO = [/(^|\/)__pycache__\//, /\.pyc$/, /(^|\/)\.env$/, /(^|\/)config\.json$/, /(^|\/)\.venv\//, /(^|\/)node_modules\//];

function arquivos(dir) {
  const saida = [];
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) saida.push(p + "/", ...arquivos(p));
    else saida.push(p);
  }
  return saida;
}

function cabecalho(txt) {
  const m = /^---\n([\s\S]*?)\n---(\n|$)/.exec(txt);
  if (!m) return null;
  const campos = {};
  for (const linha of m[1].split("\n")) {
    const c = /^([a-zA-Z_-]+):\s?(.*)$/.exec(linha);
    if (c) campos[c[1]] = c[2].trim();
  }
  return { bruto: m[1], campos, linhas: m[1].split("\n") };
}

const semAspas = (v) => (v ?? "").replace(/^["']|["']$/g, "");

function vendorizados(dirSkill) {
  const arq = join(dirSkill, ".vendor");
  if (!existsSync(arq)) return [];
  return readFileSync(arq, "utf8")
    .split("\n")
    .map((l) => l.replace(/#.*/, "").trim())
    .filter(Boolean);
}

export function verificar(raiz) {
  const problemas = [];
  const acusa = (regra, caminho, detalhe) => problemas.push({ regra, caminho: relative(raiz, caminho), detalhe });
  const dirSkills = join(raiz, "skills");
  const pastas = existsSync(dirSkills)
    ? readdirSync(dirSkills, { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name)
    : [];

  for (const nome of pastas) {
    const dir = join(dirSkills, nome);
    if (!NOME_RE.test(nome)) acusa("prefixo", dir, "pasta precisa ser terras-<nome-em-kebab-case>");

    const skill = join(dir, "SKILL.md");
    if (!existsSync(skill)) {
      acusa("nome", dir, "sem SKILL.md");
    } else {
      const txt = readFileSync(skill, "utf8");
      if (txt.includes("\r")) acusa("crlf", skill, "CRLF: o parser do motor é flat e recusa");
      const cab = cabecalho(txt.replace(/\r\n/g, "\n"));
      if (!cab) acusa("nome", skill, "sem cabeçalho entre ---");
      else {
        if (semAspas(cab.campos.name) !== nome) acusa("nome", skill, `name "${cab.campos.name}" diferente da pasta`);
        if (!semAspas(cab.campos.description)) acusa("nome", skill, "description vazia");
        if (cab.bruto.length > MAX_CABECALHO) acusa("nome", skill, `cabeçalho com ${cab.bruto.length} caracteres (teto ${MAX_CABECALHO})`);
      }
    }

    const vendor = vendorizados(dir);
    for (const caminho of arquivos(dir)) {
      const rel = relative(dir, caminho);
      if (LIXO.some((re) => re.test(rel)) && !/\.example\./.test(rel)) {
        acusa("lixo", caminho, "credencial, ambiente ou cache não entram no repositório");
        continue;
      }
      if (caminho.endsWith("/") || !TEXTO.test(caminho) || statSync(caminho).size > 2_000_000) continue;
      const txt = readFileSync(caminho, "utf8");
      for (const re of SEGREDO) if (re.test(txt)) acusa("segredo", caminho, `casa ${re}`);
      if (!vendor.some((v) => rel.startsWith(v))) {
        txt.split("\n").forEach((linha, i) => {
          for (const [re, tipo] of HARNESS) if (re.test(linha)) acusa("harness", `${caminho}:${i + 1}`, `${tipo}: ${linha.trim().slice(0, 120)}`);
        });
      }
      if (!vendor.some((v) => rel.startsWith(v))) for (const [re, marca] of ORIGEM) if (re.test(txt)) acusa("origem", caminho, `cita "${marca}"`);
    }
  }

  // Catálogo do motor: cada nome listado precisa de um arquivo que o parser aceite.
  const arqCatalogo = join(raiz, "catalogo.json");
  const catalogo = existsSync(arqCatalogo) ? JSON.parse(readFileSync(arqCatalogo, "utf8")).skills ?? [] : [];
  for (const { nome } of catalogo) {
    const dir = join(dirSkills, nome);
    const arq = existsSync(join(dir, "catalogo.md")) ? join(dir, "catalogo.md") : join(dir, "SKILL.md");
    if (!existsSync(arq)) {
      acusa("catalogo", dir, "listada em catalogo.json sem pasta ou sem SKILL.md");
      continue;
    }
    const txt = readFileSync(arq, "utf8");
    if (txt.includes("\r")) acusa("crlf", arq, "CRLF: o parser do motor é flat e recusa");
    const cab = cabecalho(txt.replace(/\r\n/g, "\n"));
    if (!cab) {
      acusa("catalogo", arq, "sem cabeçalho");
      continue;
    }
    if (semAspas(cab.campos.name) !== nome) acusa("catalogo", arq, `name "${cab.campos.name}" diferente de ${nome}`);
    const desc = semAspas(cab.campos.description);
    if (!desc) acusa("catalogo", arq, "description vazia");
    if (desc.length > MAX_DESCRICAO_CATALOGO) acusa("catalogo", arq, `description com ${desc.length} caracteres (teto ${MAX_DESCRICAO_CATALOGO})`);
    if (/^description:\s*[|>]/m.test(cab.bruto)) acusa("catalogo", arq, "description em bloco YAML: o parser é flat");
    const kw = /^\[(.*)\]$/.exec(cab.campos.keywords ?? "")?.[1]?.split(",").map((k) => k.trim()).filter(Boolean) ?? [];
    if (!kw.length) acusa("catalogo", arq, "sem keywords: a skill fica liberada e não dispara");
  }
  return problemas;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raiz = process.argv[2] ?? fileURLToPath(new URL("..", import.meta.url));
  const problemas = verificar(raiz);
  for (const p of problemas) console.log(`${p.regra.padEnd(8)} ${p.caminho}  ${p.detalhe}`);
  const pastas = readdirSync(join(raiz, "skills")).length;
  console.log(problemas.length ? `\n${problemas.length} problema(s) em ${pastas} skill(s)` : `ok: ${pastas} skill(s), nenhum problema`);
  process.exit(problemas.length ? 1 : 0);
}

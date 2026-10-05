#!/usr/bin/env node
// Gera o .claude-plugin/marketplace.json a partir do catálogo: cada skill
// instalável de skills/ vira um plugin do marketplace `terras`, que aponta para
// a PRÓPRIA pasta da skill (strict: false + skills: ["./"]). Nada é copiado: a
// fonte continua única, e o motor terrasia segue lendo skills/<nome>/.
//
// Skills que dependem da pasta vizinha (../terras-x) saem JUNTAS num plugin de
// grupo (marketplace-grupos.json): o gerador copia as pastas lado a lado para
// plugins/<grupo>/skills/, a única cópia do repositório, conferida pelo gate.
//
// Ficam de fora: skill de processo do motor (marcada com .nao-instalar) e o que
// estiver em marketplace-fora.json (com o motivo). Plugin escrito à mão (source
// em ./plugins/) é preservado como está.
//
//   npm run marketplace            # regrava o manifesto
//   npm run marketplace -- --check # só confere (sai 1 se estiver desatualizado)
//
// A sincronia também é teste do gate (scripts/marketplace.test.mjs).
import { createHash } from "node:crypto";
import { cpSync, existsSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_DESCRICAO = 300;

export function cabecalho(txt) {
  const m = /^---\n([\s\S]*?)\n---(\n|$)/.exec(txt);
  if (!m) return null;
  const campos = {};
  const linhas = m[1].split("\n");
  for (let i = 0; i < linhas.length; i++) {
    const c = /^([a-zA-Z_-]+):\s?(.*)$/.exec(linhas[i]);
    if (!c) continue;
    let valor = c[2].trim();
    // Bloco YAML (`>`/`|` com modificadores): o valor são as linhas indentadas
    // seguintes. O motor exige cabeçalho plano, mas o manifesto é do marketplace,
    // que lê YAML de verdade — sem isto a descrição sairia como ">-".
    if (/^[|>][1-9+-]*$/.test(valor)) {
      const partes = [];
      for (i++; i < linhas.length; i++) {
        const l = linhas[i];
        if (l.trim() === "") continue;
        if (!/^\s/.test(l)) { i--; break; }
        partes.push(l.trim());
      }
      valor = partes.join(" ");
    }
    campos[c[1]] = valor;
  }
  return campos;
}

export const semAspas = (v) => (v ?? "").replace(/^["']|["']$/g, "");

/** Descrição para o manifesto: inteira se cabe, senão cortada no fim de uma frase. */
function descricaoCurta(texto) {
  if (texto.length <= MAX_DESCRICAO) return texto;
  const corte = texto.slice(0, MAX_DESCRICAO);
  const fim = corte.lastIndexOf(". ");
  return fim > 0 ? corte.slice(0, fim + 1) : corte.trimEnd();
}

function lista(v) {
  const m = /^\[(.*)\]$/.exec((v ?? "").trim());
  return m ? m[1].split(",").map((s) => semAspas(s.trim())).filter(Boolean) : [];
}

const lerJson = (caminho, padrao) => (existsSync(caminho) ? JSON.parse(readFileSync(caminho, "utf8")) : padrao);

/** Grupos declarados, já validados: toda skill citada existe e é publicável. */
function lerGrupos(raiz, fora) {
  const grupos = lerJson(join(raiz, "marketplace-grupos.json"), {});
  for (const [grupo, g] of Object.entries(grupos)) {
    for (const nome of g.skills) {
      const dir = join(raiz, "skills", nome);
      if (!existsSync(join(dir, "SKILL.md"))) throw new Error(`grupo ${grupo}: skill ${nome} não existe no catálogo`);
      if (existsSync(join(dir, ".nao-instalar")) || nome in fora) throw new Error(`grupo ${grupo}: skill ${nome} está fora do marketplace`);
    }
  }
  return grupos;
}

/** Resumo do conteúdo de uma pasta (caminhos relativos + bytes), para comparar cópia e fonte. */
function resumoDaPasta(dir) {
  const h = createHash("sha256");
  const andar = (d, rel) => {
    for (const nome of readdirSync(d).sort()) {
      const p = join(d, nome);
      const r = rel ? `${rel}/${nome}` : nome;
      if (statSync(p).isDirectory()) andar(p, r);
      else h.update(r).update("\0").update(readFileSync(p)).update("\0");
    }
  };
  if (!existsSync(dir)) return null;
  andar(dir, "");
  return h.digest("hex");
}

const manifestoDoGrupo = (grupo, g, dono) => ({
  name: grupo,
  version: g.version ?? "1.0.0",
  description: g.description,
  ...(dono ? { author: { name: dono } } : {}),
  license: "MIT",
});

/** Grupos cuja cópia em plugins/ falta ou diverge do catálogo. */
export function gruposDesatualizados(raiz) {
  const atual = lerJson(join(raiz, ".claude-plugin/marketplace.json"), {});
  const grupos = lerGrupos(raiz, lerJson(join(raiz, "marketplace-fora.json"), {}));
  const ruins = [];
  for (const [grupo, g] of Object.entries(grupos)) {
    const base = join(raiz, "plugins", grupo);
    const pj = join(base, ".claude-plugin/plugin.json");
    const esperado = JSON.stringify(manifestoDoGrupo(grupo, g, atual.owner?.name), null, 2) + "\n";
    const copiadas = existsSync(join(base, "skills")) ? readdirSync(join(base, "skills")).sort() : [];
    const iguais =
      existsSync(pj) &&
      readFileSync(pj, "utf8") === esperado &&
      JSON.stringify(copiadas) === JSON.stringify([...g.skills].sort()) &&
      g.skills.every((n) => resumoDaPasta(join(base, "skills", n)) === resumoDaPasta(join(raiz, "skills", n)));
    if (!iguais) ruins.push(grupo);
  }
  return ruins;
}

/** Recria plugins/<grupo>/ a partir do catálogo (apaga e copia: sem resto de versão anterior). */
export function sincronizarGrupos(raiz) {
  const atual = lerJson(join(raiz, ".claude-plugin/marketplace.json"), {});
  const grupos = lerGrupos(raiz, lerJson(join(raiz, "marketplace-fora.json"), {}));
  for (const [grupo, g] of Object.entries(grupos)) {
    const base = join(raiz, "plugins", grupo);
    rmSync(base, { recursive: true, force: true });
    mkdirSync(join(base, ".claude-plugin"), { recursive: true });
    writeFileSync(join(base, ".claude-plugin/plugin.json"), JSON.stringify(manifestoDoGrupo(grupo, g, atual.owner?.name), null, 2) + "\n");
    for (const nome of g.skills) cpSync(join(raiz, "skills", nome), join(base, "skills", nome), { recursive: true });
  }
  return Object.keys(grupos);
}

export function montarManifesto(raiz) {
  const atual = lerJson(join(raiz, ".claude-plugin/marketplace.json"), { name: "terras", plugins: [] });
  const fora = lerJson(join(raiz, "marketplace-fora.json"), {});
  const grupos = lerGrupos(raiz, fora);
  const agrupadas = new Set(Object.values(grupos).flatMap((g) => g.skills));
  const manuais = (atual.plugins ?? []).filter((p) => !(p.name in grupos) && (typeof p.source !== "string" || !p.source.startsWith("./skills/")));
  const deGrupo = Object.entries(grupos)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([grupo, g]) => ({
      name: grupo,
      description: g.description,
      version: g.version ?? "1.0.0",
      source: `./plugins/${grupo}`,
      category: g.category ?? "productivity",
      license: "MIT",
      ...(atual.owner?.name ? { author: { name: atual.owner.name } } : {}),
    }));
  const dirSkills = join(raiz, "skills");
  const gerados = [];
  for (const nome of readdirSync(dirSkills).sort()) {
    const dir = join(dirSkills, nome);
    const arquivo = join(dir, "SKILL.md");
    if (!existsSync(arquivo) || existsSync(join(dir, ".nao-instalar")) || nome in fora || agrupadas.has(nome)) continue;
    if (manuais.some((p) => p.name === nome)) throw new Error(`${nome}: já existe plugin escrito à mão com este nome; renomeie um dos dois`);
    const campos = cabecalho(readFileSync(arquivo, "utf8")) ?? {};
    const plugin = {
      name: nome,
      description: descricaoCurta(semAspas(campos.description)),
      version: semAspas(campos.version) || "1.0.0",
      source: `./skills/${nome}`,
      strict: false,
      skills: ["./"],
      category: semAspas(campos.category) || "productivity",
      license: "MIT",
    };
    if (atual.owner?.name) plugin.author = { name: atual.owner.name };
    const chaves = lista(campos.keywords);
    if (chaves.length) plugin.keywords = chaves;
    gerados.push(plugin);
  }
  return { ...atual, plugins: [...manuais, ...deGrupo, ...gerados] };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const caminho = join(raiz, ".claude-plugin/marketplace.json");
  const novo = `${JSON.stringify(montarManifesto(raiz), null, 2)}\n`;
  const gruposRuins = gruposDesatualizados(raiz);
  const emDia = existsSync(caminho) && readFileSync(caminho, "utf8") === novo && gruposRuins.length === 0;
  if (process.argv.includes("--check")) {
    console.log(emDia ? "marketplace.json em dia com o catálogo" : "marketplace.json DESATUALIZADO: rode npm run marketplace");
    process.exit(emDia ? 0 : 1);
  }
  if (!emDia) writeFileSync(caminho, novo);
  if (gruposRuins.length) sincronizarGrupos(raiz);
  const n = JSON.parse(novo).plugins.length;
  console.log(emDia ? `nada a mudar (${n} plugins)` : `marketplace.json regravado: ${n} plugins`);
}

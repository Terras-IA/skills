#!/usr/bin/env node
// Abre um .bpmn no bpmn-js (o motor do Camunda Modeler e do bpmn.io) e salva o PNG.
// É a prova de que o arquivo abre com diagrama: erro de importação ou elemento
// sem coordenada sai no terminal e o script termina com código 1.
//
//   node render_bpmn.mjs <arquivo.bpmn> [--out <base>] [--escala 2]
//
// O Playwright é resolvido de TERRAS_MERMAID_DEPS (ou TERRAS_EXCALIDRAW_DEPS).
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";

const VERSAO_BPMN_JS = "17.11.1";
const CDN = `https://unpkg.com/bpmn-js@${VERSAO_BPMN_JS}/dist`;
const DEPS = process.env.TERRAS_MERMAID_DEPS || process.env.TERRAS_EXCALIDRAW_DEPS ||
  join(process.env.XDG_CACHE_HOME || join(homedir(), ".cache"), "terras-excalidraw");

function opcoes(argv) {
  const o = { entrada: null, out: null, escala: 2 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") o.out = argv[++i];
    else if (a === "--escala") o.escala = Number(argv[++i]) || 2;
    else if (!o.entrada) o.entrada = a;
    else throw new Error(`argumento inesperado: ${a}`);
  }
  if (!o.entrada) throw new Error("uso: node render_bpmn.mjs <arquivo.bpmn> [--out <base>] [--escala N]");
  return o;
}

const o = opcoes(process.argv.slice(2));
const base = o.out || join(dirname(o.entrada), basename(o.entrada).replace(/\.bpmn$/, ""));
const xml = readFileSync(o.entrada, "utf8");

async function carregarPlaywright() {
  try { return createRequire(join(DEPS, "package.json"))("playwright"); }
  catch { return await import("playwright"); }
}

const { chromium } = await carregarPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: o.escala, viewport: { width: 1600, height: 1000 } });
await page.setContent(`<!doctype html><html><head>
<link rel="stylesheet" href="${CDN}/assets/diagram-js.css">
<link rel="stylesheet" href="${CDN}/assets/bpmn-js.css">
<link rel="stylesheet" href="${CDN}/assets/bpmn-font/css/bpmn.css">
</head><body style="margin:0;background:#fff"><div id="c" style="width:100vw;height:100vh"></div></body></html>`);
await page.addScriptTag({ url: `${CDN}/bpmn-viewer.production.min.js` });

const r = await page.evaluate(async (xml) => {
  const viewer = new window.BpmnJS({ container: "#c" });
  try {
    const { warnings } = await viewer.importXML(xml);
    const registry = viewer.get("elementRegistry");
    const semDi = [];
    const defs = viewer.getDefinitions();
    const ids = new Set(registry.getAll().map((e) => e.id));
    for (const proc of defs.rootElements.filter((e) => e.$type === "bpmn:Process")) {
      for (const el of proc.flowElements || []) if (!ids.has(el.id)) semDi.push(el.id);
    }
    const vb = viewer.get("canvas").viewbox();
    return { ok: true, warnings: warnings.map((w) => w.message), semDi, inner: vb.inner, n: registry.getAll().length };
  } catch (e) {
    return { ok: false, erro: String(e && e.message || e), warnings: (e.warnings || []).map((w) => w.message) };
  }
}, xml);

if (!r.ok) {
  console.error(`ERRO ao importar ${o.entrada}: ${r.erro}`);
  for (const w of r.warnings) console.error(`  aviso: ${w}`);
  await browser.close();
  process.exit(1);
}
// redimensiona para o desenho inteiro caber e tira o PNG
const w = Math.ceil(r.inner.width + 80), h = Math.ceil(r.inner.height + 80);
await page.setViewportSize({ width: Math.min(w, 8000), height: Math.min(h, 8000) });
await page.evaluate(async (xml) => {
  document.querySelector("#c").innerHTML = "";
  const v = new window.BpmnJS({ container: "#c" });
  await v.importXML(xml);
  v.get("canvas").zoom("fit-viewport", "auto");
}, xml);
await page.screenshot({ path: `${base}.bpmn.png` });
await browser.close();

for (const aviso of r.warnings) console.error(`aviso: ${aviso}`);
if (r.semDi.length) console.error(`sem coordenada (não aparece no Camunda/Bizagi): ${r.semDi.join(", ")}`);
console.log(`${base}.bpmn.png (${w}x${h} @${o.escala}x) · ${r.n} elementos desenhados · ${r.warnings.length} avisos`);
process.exit(r.warnings.length || r.semDi.length ? 1 : 0);

#!/usr/bin/env node
// Renderiza um .mmd direto com o Mermaid (SVG vetorial + PNG em alta resolução).
// Complementa o render do Excalidraw: aqui a saída é o diagrama "cru" do Mermaid,
// com texto vetorial e tamanho nativo — bom para documento, slide e impressão.
//
//   node render-mermaid.mjs <arquivo.mmd> [--out <base>] [--escala 3]
//
// O Playwright é resolvido de TERRAS_MERMAID_DEPS (ou TERRAS_EXCALIDRAW_DEPS).
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { basename, dirname, join } from "node:path";

const VERSAO_MERMAID = "11.4.1";
const DEPS = process.env.TERRAS_MERMAID_DEPS || process.env.TERRAS_EXCALIDRAW_DEPS ||
  join(process.env.XDG_CACHE_HOME || join(homedir(), ".cache"), "terras-excalidraw");

function opcoes(argv) {
  const o = { entrada: null, out: null, escala: 3 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") o.out = argv[++i];
    else if (a === "--escala") o.escala = Number(argv[++i]) || 3;
    else if (!o.entrada) o.entrada = a;
    else throw new Error(`argumento inesperado: ${a}`);
  }
  if (!o.entrada) throw new Error("uso: node render-mermaid.mjs <arquivo.mmd> [--out <base>] [--escala N]");
  return o;
}

const o = opcoes(process.argv.slice(2));
const base = o.out || join(dirname(o.entrada), basename(o.entrada).replace(/\.mmd$/, ""));
const fonte = readFileSync(o.entrada, "utf8");

async function carregarPlaywright() {
  try { return createRequire(join(DEPS, "package.json"))("playwright"); }
  catch { return await import("playwright"); }
}

const { chromium } = await carregarPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ deviceScaleFactor: o.escala });
await page.setContent('<!doctype html><html><body style="margin:0;background:#fff"><div id="c"></div></body></html>');
await page.evaluate(async ({ fonte, versao }) => {
  const mermaid = (await import(`https://esm.sh/mermaid@${versao}`)).default;
  mermaid.initialize({
    startOnLoad: false,
    theme: "neutral",
    securityLevel: "loose",
    fontFamily: '"trebuchet ms", verdana, arial, sans-serif',
    flowchart: { htmlLabels: false, useMaxWidth: false, curve: "basis" },
  });
  const { svg } = await mermaid.render("grafico", fonte);
  document.getElementById("c").innerHTML = svg;
  const el = document.querySelector("#c svg");
  el.setAttribute("width", el.viewBox.baseVal.width);
  el.setAttribute("height", el.viewBox.baseVal.height);
}, { fonte, versao: VERSAO_MERMAID });

const el = page.locator("#c svg");
await page.evaluate(() => document.fonts.ready);
const svg = await el.evaluate((n) => n.outerHTML);
writeFileSync(`${base}.mermaid.svg`, svg);
await el.screenshot({ path: `${base}.mermaid.png` });
const dim = await el.evaluate((n) => [n.viewBox.baseVal.width, n.viewBox.baseVal.height]);
await browser.close();
console.log(`${base}.mermaid.svg · ${base}.mermaid.png (${dim[0]}x${dim[1]} @${o.escala}x = ${Math.round(dim[0] * o.escala)}x${Math.round(dim[1] * o.escala)} px)`);

#!/usr/bin/env node
// Gera um desenho Excalidraw editável (.excalidraw) e as imagens (SVG, PNG) a
// partir de um esqueleto JSON, de um Mermaid ou de um .excalidraw já existente.
//
//   node render.mjs <entrada> [--out <base>] [--png|--svg|--sem-imagem] [--escuro] [--escala 2]
//
// Entrada:
//   *.json        esqueleto: lista de elementos mínimos (ou { "elements": [...] })
//   *.mmd         Mermaid (flowchart, sequence e class viram elementos editáveis)
//   *.excalidraw  cena pronta: só reexporta as imagens (depois que alguém editou)
//
// A conversão roda num Chromium sem tela (Playwright), porque a biblioteca do
// Excalidraw mede texto no canvas do navegador. O código da biblioteca vem do
// esm.sh com versão fixa; o conteúdo do desenho nunca sai da máquina.
//
// Saída: <base>.excalidraw, <base>.svg e <base>.png, e um relatório em JSON no
// stdout com a contagem de elementos e os defeitos encontrados (seta solta,
// texto fora de caixa, sobreposição). Sai com código 2 quando há defeito.
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { basename, dirname, extname, join, resolve } from "node:path";

const VERSAO_EXCALIDRAW = "0.18.1";
const VERSAO_MERMAID = "2.2.2";

function argumentos(argv) {
  const opc = { entrada: null, out: null, png: true, svg: true, escuro: false, escala: 2 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") opc.out = argv[++i];
    else if (a === "--png") opc.svg = false;
    else if (a === "--svg") opc.png = false;
    else if (a === "--sem-imagem") opc.png = opc.svg = false;
    else if (a === "--escuro") opc.escuro = true;
    else if (a === "--escala") opc.escala = Number(argv[++i]) || 2;
    else if (a === "-h" || a === "--help") opc.ajuda = true;
    else if (!opc.entrada) opc.entrada = a;
    else throw new Error(`argumento inesperado: ${a}`);
  }
  return opc;
}

const AJUDA = `uso: node render.mjs <entrada.json|.mmd|.excalidraw> [--out <base>] [--png|--svg|--sem-imagem] [--escuro] [--escala N]`;

// O Playwright fica num cache fora da skill: a pasta da skill pode ser só
// leitura (plugin instalado) e o verificador do repositório barra node_modules.
const DEPS = process.env.TERRAS_EXCALIDRAW_DEPS || join(process.env.XDG_CACHE_HOME || join(homedir(), ".cache"), "terras-excalidraw");

async function carregarPlaywright() {
  try {
    return createRequire(join(DEPS, "package.json"))("playwright");
  } catch {
    try {
      return await import("playwright");
    } catch {
      throw new Error(`playwright não instalado. Rode uma vez: npm install --no-package-lock --prefix "${DEPS}" playwright`);
    }
  }
}

// Roda dentro do navegador. Recebe a entrada já lida e devolve cena + imagens.
async function noNavegador({ tipo, conteudo, escuro, escala, png, svg, vEx, vMm }) {
  const ex = await import(`https://esm.sh/@excalidraw/excalidraw@${vEx}`);
  // Sem o editor montado, ninguém registra as fontes no documento, e o texto é
  // medido com a fonte reserva: a caixa sai estreita e o texto vaza na imagem.
  // O SVG exportado traz as fontes embutidas (só com os glifos usados), então
  // exportamos todo o texto da entrada nas três famílias e registramos o
  // @font-face que veio nele antes de medir qualquer coisa.
  const amostra = [...new Set(conteudo)].join("").replace(/\s+/g, "") + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  const aquecimento = await ex.exportToSvg({
    elements: ex.convertToExcalidrawElements(
      [5, 6, 8].map((fontFamily, i) => ({ type: "text", x: 0, y: i * 40, text: amostra, fontFamily })),
    ),
    files: {},
  });
  const estilo = document.createElement("style");
  estilo.textContent = [...aquecimento.querySelectorAll("style")].map((s) => s.textContent).join("\n");
  document.head.append(estilo);
  await Promise.all(["Excalifont", "Nunito", "Comic Shanns"].map((f) => document.fonts.load(`20px "${f}"`, amostra)));
  let elements;
  let files = {};
  let appState = { viewBackgroundColor: "#ffffff" };

  if (tipo === "excalidraw") {
    const cena = JSON.parse(conteudo);
    const r = ex.restore(cena, null, null);
    elements = r.elements;
    files = r.files ?? {};
    appState = { viewBackgroundColor: cena.appState?.viewBackgroundColor ?? "#ffffff" };
  } else {
    let esqueleto;
    if (tipo === "mermaid") {
      const mm = await import(`https://esm.sh/@excalidraw/mermaid-to-excalidraw@${vMm}`);
      const r = await mm.parseMermaidToExcalidraw(conteudo, { themeVariables: { fontSize: "20px" } });
      esqueleto = r.elements;
      files = r.files ?? {};
    } else {
      const j = JSON.parse(conteudo);
      esqueleto = Array.isArray(j) ? j : j.elements;
      if (!Array.isArray(esqueleto)) throw new Error("esqueleto: esperado uma lista de elementos ou { elements: [...] }");
    }
    if (tipo === "esqueleto") tracarSetas(esqueleto);
    elements = ex.convertToExcalidrawElements(esqueleto, { regenerateIds: false });
  }

  // Seta com start.id e end.id e sem "points": traça a reta entre as bordas das
  // duas formas. O conversor liga a seta, mas não a move até as formas.
  function tracarSetas(lista) {
    const formasPorId = new Map(lista.filter((e) => e.id && e.type !== "arrow").map((e) => [e.id, e]));
    const borda = (f, dx, dy) => {
      const hw = (f.width ?? 100) / 2;
      const hh = (f.height ?? 100) / 2;
      if (!dx && !dy) return 0;
      if (f.type === "ellipse") return 1 / Math.hypot(dx / hw, dy / hh);
      if (f.type === "diamond") return 1 / (Math.abs(dx) / hw + Math.abs(dy) / hh);
      return Math.min(dx ? hw / Math.abs(dx) : Infinity, dy ? hh / Math.abs(dy) : Infinity);
    };
    for (const s of lista) {
      if (s.type !== "arrow" || s.points) continue;
      const a = formasPorId.get(s.start?.id);
      const b = formasPorId.get(s.end?.id);
      if (!a || !b) continue;
      const ca = [a.x + (a.width ?? 100) / 2, a.y + (a.height ?? 100) / 2];
      const cb = [b.x + (b.width ?? 100) / 2, b.y + (b.height ?? 100) / 2];
      const dx = cb[0] - ca[0];
      const dy = cb[1] - ca[1];
      const dist = Math.hypot(dx, dy) || 1;
      const folga = 8 / dist;
      const t0 = borda(a, dx, dy) + folga;
      const t1 = 1 - borda(b, -dx, -dy) - folga;
      const p0 = [ca[0] + dx * t0, ca[1] + dy * t0];
      const p1 = [ca[0] + dx * t1, ca[1] + dy * t1];
      s.x = p0[0];
      s.y = p0[1];
      s.width = Math.abs(p1[0] - p0[0]);
      s.height = Math.abs(p1[1] - p0[1]);
      s.points = [[0, 0], [p1[0] - p0[0], p1[1] - p0[1]]];
    }
  }

  // Defeitos que o olho humano veria no desenho e o agente não vê no JSON.
  const vivos = elements.filter((e) => !e.isDeleted);
  const porId = new Map(vivos.map((e) => [e.id, e]));
  const defeitos = [];
  for (const e of vivos) {
    if (e.type === "arrow") {
      const rot = e.boundElements?.find((b) => b.type === "text") ? porId.get(e.boundElements.find((b) => b.type === "text").id)?.text : "";
      const nome = `seta ${e.id}${rot ? ` ("${rot}")` : ""}`;
      if (!e.startBinding) defeitos.push(`${nome}: início solto (não está ligado a nenhuma forma)`);
      if (!e.endBinding) defeitos.push(`${nome}: fim solto (não está ligado a nenhuma forma)`);
      const longe = (ponta, ligacao) => {
        const f = porId.get(ligacao?.elementId);
        if (!f) return false;
        const [px, py] = [e.x + ponta[0], e.y + ponta[1]];
        const fx = Math.max(f.x - px, 0, px - (f.x + f.width));
        const fy = Math.max(f.y - py, 0, py - (f.y + f.height));
        return Math.hypot(fx, fy) > 30;
      };
      if (longe(e.points[0], e.startBinding)) defeitos.push(`${nome}: ligada, mas o início está desenhado longe da forma`);
      if (longe(e.points.at(-1), e.endBinding)) defeitos.push(`${nome}: ligada, mas o fim está desenhado longe da forma`);
    }
    if (e.type === "text" && e.containerId && !porId.has(e.containerId)) defeitos.push(`texto ${e.id}: aponta para uma caixa que não existe`);
  }
  const formas = vivos.filter((e) => ["rectangle", "ellipse", "diamond"].includes(e.type));
  for (let i = 0; i < formas.length; i++) {
    for (let k = i + 1; k < formas.length; k++) {
      const a = formas[i];
      const b = formas[k];
      const cruza = a.x < b.x + b.width && b.x < a.x + a.width && a.y < b.y + b.height && b.y < a.y + a.height;
      const contem = (p, q) => p.x <= q.x && p.y <= q.y && p.x + p.width >= q.x + q.width && p.y + p.height >= q.y + q.height;
      if (cruza && !contem(a, b) && !contem(b, a)) defeitos.push(`formas ${a.id} e ${b.id} se sobrepõem`);
    }
  }
  for (const t of vivos.filter((e) => e.type === "text" && e.containerId)) {
    const c = porId.get(t.containerId);
    if (c && c.type === "arrow") {
      const [dx, dy] = c.points.at(-1);
      if (t.width > Math.hypot(dx, dy) - 24) defeitos.push(`rótulo "${t.text.slice(0, 40)}" é maior que a seta ${c.id}: afaste as formas`);
    }
    if (c && c.type !== "arrow" && (t.width > c.width + 1 || t.height > c.height + 1)) defeitos.push(`texto de ${c.id} não cabe na caixa ("${t.text.slice(0, 40)}")`);
  }

  const cena = {
    type: "excalidraw",
    version: 2,
    source: "https://excalidraw.com",
    elements,
    appState: { gridSize: 20, viewBackgroundColor: appState.viewBackgroundColor },
    files,
  };
  const opcoesExport = {
    elements: vivos,
    appState: { exportBackground: true, viewBackgroundColor: appState.viewBackgroundColor, exportWithDarkMode: escuro, exportScale: escala },
    files,
    exportPadding: 24,
  };
  const saida = { cena, defeitos, contagem: {} };
  for (const e of vivos) saida.contagem[e.type] = (saida.contagem[e.type] ?? 0) + 1;
  if (svg) {
    const el = await ex.exportToSvg({ ...opcoesExport, appState: { ...opcoesExport.appState, exportEmbedScene: false } });
    saida.svg = el.outerHTML;
  }
  if (png) {
    const blob = await ex.exportToBlob({ ...opcoesExport, mimeType: "image/png" });
    const buf = new Uint8Array(await blob.arrayBuffer());
    let bin = "";
    for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode(...buf.subarray(i, i + 0x8000));
    saida.png = btoa(bin);
  }
  return saida;
}

async function main() {
  const opc = argumentos(process.argv.slice(2));
  if (opc.ajuda || !opc.entrada) {
    console.log(AJUDA);
    process.exit(opc.entrada ? 0 : 1);
  }
  const entrada = resolve(opc.entrada);
  const ext = extname(entrada).toLowerCase();
  const tipo = ext === ".mmd" || ext === ".mermaid" ? "mermaid" : ext === ".excalidraw" ? "excalidraw" : "esqueleto";
  const base = opc.out ? resolve(opc.out) : join(dirname(entrada), basename(entrada, extname(entrada)));
  const conteudo = readFileSync(entrada, "utf8");

  const { chromium } = await carregarPlaywright();
  const navegador = await chromium.launch();
  try {
    const pagina = await navegador.newPage();
    const erros = [];
    pagina.on("pageerror", (e) => erros.push(e.message));
    // Página em origem https para o import de módulo do esm.sh funcionar.
    await pagina.route("https://terras-excalidraw.local/", (r) =>
      r.fulfill({ contentType: "text/html", body: "<!doctype html><meta charset=utf-8><body></body>" }),
    );
    await pagina.goto("https://terras-excalidraw.local/");
    const r = await pagina.evaluate(noNavegador, {
      tipo,
      conteudo,
      escuro: opc.escuro,
      escala: opc.escala,
      png: opc.png,
      svg: opc.svg,
      vEx: VERSAO_EXCALIDRAW,
      vMm: VERSAO_MERMAID,
    });
    const gravados = [];
    if (tipo !== "excalidraw") {
      writeFileSync(`${base}.excalidraw`, JSON.stringify(r.cena, null, 2) + "\n");
      gravados.push(`${base}.excalidraw`);
    }
    if (r.svg) {
      writeFileSync(`${base}.svg`, r.svg);
      gravados.push(`${base}.svg`);
    }
    if (r.png) {
      writeFileSync(`${base}.png`, Buffer.from(r.png, "base64"));
      gravados.push(`${base}.png`);
    }
    const relatorio = { gravados, elementos: r.contagem, defeitos: r.defeitos, errosDaPagina: erros };
    console.log(JSON.stringify(relatorio, null, 2));
    process.exitCode = r.defeitos.length ? 2 : 0;
  } finally {
    await navegador.close();
  }
}

main().catch((e) => {
  const msg = String(e?.message ?? e);
  console.error(/esm\.sh|Failed to fetch|ERR_NAME|net::/i.test(msg) ? `sem acesso ao esm.sh para baixar a biblioteca do Excalidraw: ${msg}` : msg);
  process.exit(1);
});

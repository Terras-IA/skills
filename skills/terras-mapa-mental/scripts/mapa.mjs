#!/usr/bin/env node
// Gera um mapa mental a partir de um roteiro em Markdown (títulos e listas).
//
//   node mapa.mjs <roteiro.md> [--out <base>] [--formatos svg,png,html,excalidraw]
//                 [--max-nivel 4] [--max-filhos 7] [--max-rotulo 40] [--escala 2]
//
// Entrada: o primeiro título "#" é o centro; "##" e abaixo, e itens de lista
// ("-", "*", "1.") indentados de 2 em 2 espaços, são os ramos.
//
// Saída (cada uma opcional por --formatos):
//   <base>.svg         desenho estático, layout de dois lados, uma cor por ramo
//   <base>.png         o mesmo SVG fotografado num Chromium sem tela (Playwright)
//   <base>.html        mapa interativo (markmap, versão fixa no CDN), abre e fecha ramos
//   <base>.excalidraw  cena editável, pelo render.mjs da skill terras-excalidraw
//
// No stdout, um relatório JSON com a contagem de nós e os defeitos (nível fundo
// demais, ramo com filhos demais, rótulo longo, mapa vazio). Sai com código 2
// quando há defeito: corrija o roteiro e rode de novo.
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { basename, dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const VERSAO_MARKMAP = "0.18.12";
const FORMATOS = ["svg", "png", "html", "excalidraw"];
// Uma cor por ramo de primeiro nível: fundo claro e traço do mesmo tom.
const PALETA = [
  ["#e7f5ff", "#1c7ed6"],
  ["#ebfbee", "#2f9e44"],
  ["#fff4e6", "#e8590c"],
  ["#f3f0ff", "#7048e8"],
  ["#fff0f6", "#d6336c"],
  ["#e6fcf5", "#0c8599"],
  ["#f8f0e8", "#8d5524"],
  ["#f1f3f5", "#495057"],
];

function argumentos(argv) {
  const opc = { entrada: null, out: null, formatos: FORMATOS, maxNivel: 4, maxFilhos: 7, maxRotulo: 40, escala: 2 };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--out") opc.out = argv[++i];
    else if (a === "--formatos") opc.formatos = argv[++i].split(",").map((f) => f.trim()).filter(Boolean);
    else if (a === "--max-nivel") opc.maxNivel = Number(argv[++i]);
    else if (a === "--max-filhos") opc.maxFilhos = Number(argv[++i]);
    else if (a === "--max-rotulo") opc.maxRotulo = Number(argv[++i]);
    else if (a === "--escala") opc.escala = Number(argv[++i]) || 2;
    else if (a === "-h" || a === "--help") opc.ajuda = true;
    else if (!opc.entrada) opc.entrada = a;
    else throw new Error(`argumento inesperado: ${a}`);
  }
  for (const f of opc.formatos) if (!FORMATOS.includes(f)) throw new Error(`formato desconhecido: ${f} (use ${FORMATOS.join(", ")})`);
  return opc;
}

// ---------- roteiro → árvore ----------

export function lerRoteiro(texto) {
  let raiz = null;
  const pilha = []; // [{ nivel, no }]
  let nivelTitulo = 0;
  const limpa = (s) => s.replace(/\*\*|__|`/g, "").replace(/\[([^\]]+)\]\([^)]*\)/g, "$1").trim();
  for (const linha of texto.replace(/\r\n/g, "\n").split("\n")) {
    let nivel;
    let rotulo;
    const t = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(linha);
    const l = /^(\s*)(?:[-*+]|\d+[.)])\s+(.+)$/.exec(linha);
    if (t) {
      nivel = t[1].length - 1;
      nivelTitulo = nivel;
      rotulo = t[2];
    } else if (l) {
      nivel = nivelTitulo + 1 + Math.floor(l[1].replace(/\t/g, "  ").length / 2);
      rotulo = l[2];
    } else continue;
    const no = { rotulo: limpa(rotulo), filhos: [] };
    if (!raiz) {
      raiz = no;
      pilha.push({ nivel, no });
      continue;
    }
    while (pilha.length > 1 && pilha.at(-1).nivel >= nivel) pilha.pop();
    pilha.at(-1).no.filhos.push(no);
    pilha.push({ nivel: Math.max(nivel, pilha.at(-1).nivel + 1), no });
  }
  return raiz;
}

export function conferir(raiz, { maxNivel, maxFilhos, maxRotulo }) {
  const defeitos = [];
  let nos = 0;
  let fundo = 0;
  if (!raiz) return { nos, niveis: 0, defeitos: ["roteiro vazio: comece com um título '# Centro'"] };
  if (!raiz.filhos.length) defeitos.push(`centro "${raiz.rotulo}" sem ramos`);
  const anda = (no, nivel, caminho) => {
    nos++;
    fundo = Math.max(fundo, nivel);
    if (nivel > maxNivel) defeitos.push(`nível ${nivel} > ${maxNivel}: "${caminho}" (suba o detalhe ou corte)`);
    if (no.rotulo.length > maxRotulo) defeitos.push(`rótulo com ${no.rotulo.length} caracteres (teto ${maxRotulo}): "${no.rotulo}"`);
    if (no.filhos.length > maxFilhos) defeitos.push(`"${no.rotulo}" tem ${no.filhos.length} filhos (teto ${maxFilhos}): agrupe`);
    for (const f of no.filhos) anda(f, nivel + 1, `${caminho} > ${f.rotulo}`);
  };
  anda(raiz, 0, raiz.rotulo);
  return { nos, niveis: fundo, defeitos };
}

// ---------- layout de dois lados ----------

// Medidas por destino: o SVG usa fonte sem serifa e curvas; o Excalidraw usa
// Excalifont (mais larga) e setas retas, que pedem vão horizontal maior para
// não cortar a caixa vizinha.
const MEDIDAS = {
  svg: { fonte: [22, 17, 14], fator: 0.58, folga: [48, 28, 28], altura: [64, 44, 34], minimo: [160, 70, 70], vaoX: 56, vaoY: 12 },
  excalidraw: { fonte: [24, 20, 16], fator: 0.62, folga: [60, 40, 36], altura: [80, 56, 46], minimo: [180, 90, 80], vaoX: 150, vaoY: 22 },
};
const em = (lista, nivel) => lista[Math.min(nivel, lista.length - 1)];
const fonte = (nivel, m = MEDIDAS.svg) => em(m.fonte, nivel);

function medir(no, nivel, m) {
  no.nivel = nivel;
  no.w = Math.max(em(m.minimo, nivel), Math.ceil(no.rotulo.length * fonte(nivel, m) * m.fator) + em(m.folga, nivel));
  no.h = em(m.altura, nivel);
  for (const f of no.filhos) medir(f, nivel + 1, m);
  const soma = no.filhos.reduce((s, f) => s + f.alt, 0) + m.vaoY * Math.max(0, no.filhos.length - 1);
  no.alt = Math.max(no.h, soma);
}

function posicionar(no, lado, xBorda, yTopo, m) {
  // xBorda: borda do pai do lado em que este nó cresce.
  no.lado = lado;
  no.cx = xBorda + lado * (m.vaoX + no.w / 2);
  no.cy = yTopo + no.alt / 2;
  let y = yTopo + (no.alt - (no.filhos.reduce((s, f) => s + f.alt, 0) + m.vaoY * Math.max(0, no.filhos.length - 1))) / 2;
  for (const f of no.filhos) {
    posicionar(f, lado, no.cx + (lado * no.w) / 2, y, m);
    y += f.alt + m.vaoY;
  }
}

export function layout(raiz, m = MEDIDAS.svg) {
  medir(raiz, 0, m);
  raiz.cx = 0;
  raiz.cy = 0;
  // Ramos maiores primeiro, cada um para o lado mais leve; depois devolve a
  // ordem original dentro de cada lado, para a leitura seguir o roteiro.
  const ordem = raiz.filhos.map((f, i) => ({ f, i, cor: i % PALETA.length }));
  const lados = { 1: [], [-1]: [] };
  const peso = { 1: 0, [-1]: 0 };
  for (const r of [...ordem].sort((a, b) => b.f.alt - a.f.alt)) {
    const l = peso[1] <= peso[-1] ? 1 : -1;
    lados[l].push(r);
    peso[l] += r.f.alt + m.vaoY;
  }
  for (const l of [1, -1]) {
    const lista = lados[l].sort((a, b) => a.i - b.i);
    const total = lista.reduce((s, r) => s + r.f.alt, 0) + m.vaoY * Math.max(0, lista.length - 1);
    let y = -total / 2;
    for (const r of lista) {
      pintar(r.f, r.cor);
      posicionar(r.f, l, (l * raiz.w) / 2, y, m);
      y += r.f.alt + m.vaoY;
    }
  }
  const nos = [];
  const anda = (n, pai) => {
    nos.push({ n, pai });
    for (const f of n.filhos) anda(f, n);
  };
  anda(raiz, null);
  return nos;
}

function pintar(no, cor) {
  no.cor = cor;
  for (const f of no.filhos) pintar(f, cor);
}

// ---------- saídas ----------

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function svg(nos) {
  const M = 32;
  const xs = nos.flatMap(({ n }) => [n.cx - n.w / 2, n.cx + n.w / 2]);
  const ys = nos.flatMap(({ n }) => [n.cy - n.h / 2, n.cy + n.h / 2]);
  const [x0, x1, y0, y1] = [Math.min(...xs) - M, Math.max(...xs) + M, Math.min(...ys) - M, Math.max(...ys) + M];
  const partes = [];
  for (const { n, pai } of nos) {
    if (!pai) continue;
    const [, traco] = PALETA[n.cor];
    const sx = pai.cx + (n.lado * pai.w) / 2;
    const ex = n.cx - (n.lado * n.w) / 2;
    const mx = (sx + ex) / 2;
    const w = n.nivel === 1 ? 3 : 2;
    partes.push(`<path d="M${sx},${pai.cy} C${mx},${pai.cy} ${mx},${n.cy} ${ex},${n.cy}" fill="none" stroke="${traco}" stroke-width="${w}" stroke-opacity="0.7"/>`);
  }
  for (const { n } of nos) {
    const [fundo, traco] = n.nivel === 0 ? ["#212529", "#212529"] : PALETA[n.cor];
    const r = n.nivel === 0 ? n.h / 2 : 10;
    const corTexto = n.nivel === 0 ? "#ffffff" : n.nivel === 1 ? traco : "#343a40";
    const peso = n.nivel <= 1 ? 600 : 400;
    partes.push(
      `<rect x="${n.cx - n.w / 2}" y="${n.cy - n.h / 2}" width="${n.w}" height="${n.h}" rx="${r}" fill="${n.nivel >= 2 ? "#ffffff" : fundo}" stroke="${traco}" stroke-width="${n.nivel === 0 ? 0 : 1.5}"/>`,
      `<text x="${n.cx}" y="${n.cy}" text-anchor="middle" dominant-baseline="central" font-size="${fonte(n.nivel)}" font-weight="${peso}" fill="${corTexto}">${esc(n.rotulo)}</text>`,
    );
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x0} ${y0} ${x1 - x0} ${y1 - y0}" width="${x1 - x0}" height="${y1 - y0}" font-family="Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">
<rect x="${x0}" y="${y0}" width="${x1 - x0}" height="${y1 - y0}" fill="#ffffff"/>
${partes.join("\n")}
</svg>
`;
}

function html(titulo, roteiro) {
  // O roteiro vai dentro de <script type="text/template">: só "</script" quebraria.
  const corpo = roteiro.replace(/<\/script/gi, "<\\/script");
  return `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(titulo)}</title>
<style>
  :root { color-scheme: light; }
  html, body { margin: 0; height: 100%; background: #ffffff; font-family: Inter, "Segoe UI", Roboto, sans-serif; }
  .markmap { width: 100vw; height: 100dvh; }
  .dica { position: fixed; left: 16px; bottom: 12px; font-size: 13px; color: #868e96; }
</style>
<script>window.markmap = { autoLoader: { toolbar: true } };</script>
<script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@${VERSAO_MARKMAP}"></script>
</head>
<body>
<div class="markmap"><script type="text/template">
---
markmap:
  initialExpandLevel: 3
  colorFreezeLevel: 2
  maxWidth: 280
---
${corpo}
</script></div>
<p class="dica">Clique num nó para abrir ou fechar o ramo. Role para dar zoom.</p>
</body>
</html>
`;
}

function esqueletoExcalidraw(nos) {
  const els = [];
  const id = new Map();
  nos.forEach(({ n }, i) => id.set(n, `n${i}`));
  for (const { n } of nos) {
    const [fundo, traco] = n.nivel === 0 ? ["#212529", "#212529"] : PALETA[n.cor];
    els.push({
      type: n.nivel === 0 ? "ellipse" : "rectangle",
      id: id.get(n),
      x: Math.round(n.cx - n.w / 2),
      y: Math.round(n.cy - n.h / 2),
      width: n.w,
      height: n.h,
      strokeColor: traco,
      backgroundColor: n.nivel >= 2 ? "#ffffff" : fundo,
      fillStyle: "solid",
      ...(n.nivel === 0 ? {} : { roundness: { type: 3 } }),
      label: { text: n.rotulo, fontSize: fonte(n.nivel, MEDIDAS.excalidraw), strokeColor: n.nivel === 0 ? "#ffffff" : "#1e1e1e" },
    });
  }
  for (const { n, pai } of nos) {
    if (!pai) continue;
    // Da borda lateral do pai à borda interna do filho: as bordas internas dos
    // irmãos ficam alinhadas, então a linha não atravessa caixa vizinha. Do
    // centro ao centro, ela cortaria os irmãos de cima ou de baixo.
    const sx = Math.round(pai.cx + (n.lado * pai.w) / 2);
    const ex = Math.round(n.cx - (n.lado * n.w) / 2);
    els.push({
      type: "arrow",
      x: sx,
      y: Math.round(pai.cy),
      points: [
        [0, 0],
        [ex - sx, Math.round(n.cy - pai.cy)],
      ],
      start: { id: id.get(pai) },
      end: { id: id.get(n) },
      strokeColor: PALETA[n.cor][1],
      endArrowhead: null,
    });
  }
  return els;
}

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

async function png(arqSvg, arqPng, escala) {
  const { chromium } = await carregarPlaywright();
  const nav = await chromium.launch();
  try {
    const pag = await nav.newPage({ deviceScaleFactor: escala });
    const txt = readFileSync(arqSvg, "utf8");
    const [, w, h] = /width="([\d.]+)" height="([\d.]+)"/.exec(txt);
    await pag.setViewportSize({ width: Math.ceil(Number(w)), height: Math.ceil(Number(h)) });
    await pag.setContent(`<html><body style="margin:0">${txt}</body></html>`);
    await pag.locator("svg").screenshot({ path: arqPng });
  } finally {
    await nav.close();
  }
}

function renderExcalidraw() {
  if (process.env.TERRAS_EXCALIDRAW_RENDER) return process.env.TERRAS_EXCALIDRAW_RENDER;
  // A pasta da skill costuma ser um link; o Node resolve o caminho real, e a
  // terras-excalidraw fica ao lado no mesmo repositório.
  const aqui = dirname(fileURLToPath(import.meta.url));
  return resolve(aqui, "../../terras-excalidraw/scripts/render.mjs");
}

async function main() {
  const opc = argumentos(process.argv.slice(2));
  if (opc.ajuda || !opc.entrada) {
    console.log("uso: node mapa.mjs <roteiro.md> [--out <base>] [--formatos svg,png,html,excalidraw] [--max-nivel 4] [--max-filhos 7] [--max-rotulo 40] [--escala 2]");
    process.exit(opc.ajuda ? 0 : 1);
  }
  const roteiro = readFileSync(opc.entrada, "utf8");
  const base = opc.out ?? join(dirname(opc.entrada), basename(opc.entrada, extname(opc.entrada)));
  const raiz = lerRoteiro(roteiro);
  const rel = { entrada: opc.entrada, ...conferir(raiz, opc), arquivos: [], avisos: [] };
  if (rel.defeitos.length) {
    console.log(JSON.stringify(rel, null, 2));
    process.exit(2);
  }
  const nos = layout(raiz);
  const quer = new Set(opc.formatos);
  if (quer.has("svg") || quer.has("png")) {
    writeFileSync(`${base}.svg`, svg(nos));
    if (quer.has("svg")) rel.arquivos.push(`${base}.svg`);
  }
  if (quer.has("png")) {
    await png(`${base}.svg`, `${base}.png`, opc.escala);
    rel.arquivos.push(`${base}.png`);
  }
  if (quer.has("html")) {
    writeFileSync(`${base}.html`, html(raiz.rotulo, roteiro));
    rel.arquivos.push(`${base}.html`);
  }
  if (quer.has("excalidraw")) {
    const render = renderExcalidraw();
    if (!existsSync(render)) {
      rel.avisos.push(`render.mjs da terras-excalidraw não encontrado em ${render}; defina TERRAS_EXCALIDRAW_RENDER`);
    } else {
      const esq = `${base}.excalidraw-esqueleto.json`;
      writeFileSync(esq, JSON.stringify(esqueletoExcalidraw(layout(raiz, MEDIDAS.excalidraw)), null, 2));
      let saida;
      try {
        saida = execFileSync(process.execPath, [render, esq, "--out", base, "--sem-imagem"], { encoding: "utf8" });
      } catch (e) {
        saida = e.stdout ?? "";
        if (e.status !== 2) rel.avisos.push(`render.mjs falhou: ${(e.stderr ?? e.message).trim().split("\n").at(-1)}`);
      }
      if (existsSync(`${base}.excalidraw`)) rel.arquivos.push(`${base}.excalidraw`);
      try {
        const r = JSON.parse(saida);
        if (r.defeitos?.length) rel.avisos.push(...r.defeitos.map((d) => `excalidraw: ${typeof d === "string" ? d : JSON.stringify(d)}`));
      } catch {}
    }
  }
  console.log(JSON.stringify(rel, null, 2));
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((e) => {
    console.error(e.message);
    process.exit(1);
  });
}

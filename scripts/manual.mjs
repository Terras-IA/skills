#!/usr/bin/env node
// Gera o MANUAL.md: todas as skills do repositório, agrupadas por área curada
// (scripts/manual-areas.json), com descrição completa, palavras-chave e a
// forma de instalar. Inclui o que o marketplace deixa de fora: as skills de
// processo do motor (.nao-instalar) e as de projeto de cliente
// (marketplace-fora.json).
//
//   node scripts/manual.mjs            # regrava o MANUAL.md
//   node scripts/manual.mjs --check    # só confere (sai 1 se desatualizado)
//
// O parsing do cabeçalho é próprio de propósito: é pequeno e mantém este
// gerador autossuficiente, sem depender de export de outro script.
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const AQUI = dirname(fileURLToPath(import.meta.url));
const RAIZ = join(AQUI, "..");

const semAspas = (v) => (v ?? "").replace(/^["']|["']$/g, "").trim();

/** Cabeçalho frontmatter: valor plano ou bloco YAML (`>`/`|`, motor recusa, mas existe). */
function cabecalho(txt) {
  const m = /^---\n([\s\S]*?)\n---(\n|$)/.exec(txt.replace(/\r\n/g, "\n"));
  if (!m) return {};
  const campos = {};
  const linhas = m[1].split("\n");
  for (let i = 0; i < linhas.length; i++) {
    const c = /^([a-zA-Z_-]+):\s?(.*)$/.exec(linhas[i]);
    if (!c) continue;
    let valor = c[2].trim();
    if (/^[|>][1-9+-]*$/.test(valor)) {
      const partes = [];
      for (i++; i < linhas.length; i++) {
        const l = linhas[i];
        if (l.trim() === "") continue;
        if (!/^\s/.test(l)) {
          i--;
          break;
        }
        partes.push(l.trim());
      }
      valor = partes.join(" ");
    }
    campos[c[1]] = semAspas(valor);
  }
  return campos;
}

const listaChaves = (v) => {
  const m = /^\[(.*)\]$/.exec((v ?? "").trim());
  if (!m) return [];
  return m[1]
    .split(",")
    .map((k) => semAspas(k.trim()))
    .filter(Boolean);
};

function ler(caminho, padrao) {
  return existsSync(caminho) ? JSON.parse(readFileSync(caminho, "utf8")) : padrao;
}

/** Âncora do GitHub para o título de uma seção: minúsculas, sem pontuação, espaços viram hífen. */
const ancora = (titulo) => titulo.toLowerCase().replace(/[^\w\sÀ-ÿ-]/g, "").replace(/\s+/g, "-");

export function gerarManual(raiz) {
  const dirSkills = join(raiz, "skills");
  const areas = ler(join(raiz, "scripts", "manual-areas.json"), { areas: [] }).areas;
  const fora = ler(join(raiz, "marketplace-fora.json"), {});
  const grupos = ler(join(raiz, "marketplace-grupos.json"), {});
  const grupoDe = {};
  for (const [nome, def] of Object.entries(grupos)) for (const s of def.skills ?? []) grupoDe[s] = nome;

  const nomes = readdirSync(dirSkills, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();

  const info = {};
  for (const nome of nomes) {
    const dir = join(dirSkills, nome);
    const cab = cabecalho(readFileSync(join(dir, "SKILL.md"), "utf8"));
    info[nome] = {
      descricao: cab.description ?? "",
      palavras: listaChaves(cab.keywords),
      versao: cab.version ?? "",
      processo: existsSync(join(dir, ".nao-instalar")),
      cliente: Object.hasOwn(fora, nome),
    };
  }

  const instalaveis = nomes.filter((n) => !info[n].processo && !info[n].cliente);
  const doProcesso = nomes.filter((n) => info[n].processo);
  const doCliente = nomes.filter((n) => info[n].cliente);

  const mapeadas = new Set(areas.flatMap((a) => a.skills));
  const semArea = instalaveis.filter((n) => !mapeadas.has(n));

  const entrada = (nome) => {
    const i = info[nome];
    const linhas = [`### ${nome}`, ""];
    if (i.descricao) linhas.push(i.descricao, "");
    const meta = [];
    if (i.processo) meta.push("Processo do motor: não vai ao marketplace; vive no repositório do motor (terrasia)");
    else if (i.cliente) meta.push(`Fora do marketplace: ${fora[nome]}`);
    else if (grupoDe[nome]) meta.push(`Sai no plugin do grupo: \`/plugin install ${grupoDe[nome]}@terras\``);
    else meta.push(`\`/plugin install ${nome}@terras\``);
    if (i.versao) meta.push(`v${i.versao}`);
    linhas.push(meta.join(" · "));
    if (i.palavras.length) {
      linhas.push("", `Palavras-chave: ${i.palavras.map((k) => `\`${k}\``).join(", ")}`);
    }
    return linhas.join("\n");
  };

  const entradas = (lista) => lista.flatMap((n) => [entrada(n), ""]);

  const blocos = [];
  for (const area of areas) {
    const skills = area.skills.filter((n) => instalaveis.includes(n)).sort();
    if (!skills.length) continue;
    blocos.push(`## ${area.nome}`, "", `*${area.descricao}*`, "", ...entradas(skills));
  }
  if (semArea.length) {
    blocos.push(
      "## Outras",
      "",
      "*Ainda sem área no manual: classifique cada uma em `scripts/manual-areas.json`.*",
      "",
      ...entradas(semArea)
    );
  }
  if (doCliente.length) {
    blocos.push(
      "## Fora do marketplace: projeto de cliente",
      "",
      "*Skills ligadas a trabalho de cliente, fora do marketplace por decisão (motivo em `marketplace-fora.json`).*",
      "",
      ...entradas(doCliente)
    );
  }
  if (doProcesso.length) {
    blocos.push(
      "## Processo do motor (terrasia)",
      "",
      "*Skills de processo que vivem no repositório do motor; aqui existe só a versão de catálogo (marcada `.nao-instalar`).*",
      "",
      ...entradas(doProcesso)
    );
  }

  const indice = areas
    .map((a) => ({ nome: a.nome, n: a.skills.filter((s) => instalaveis.includes(s)).length }))
    .filter((a) => a.n > 0)
    .map((a) => `- [${a.nome}](#${ancora(a.nome)}) — ${a.n} skills`);

  const comeco = [
    "# Manual das skills do terras",
    "",
    "> **Arquivo gerado.** Rode `node scripts/manual.mjs` para regravar; não edite à mão.",
    "",
    `**${nomes.length} skills** neste repositório: **${instalaveis.length} instaláveis** pelo marketplace, **${doProcesso.length} de processo do motor** e **${doCliente.length} ligadas a projeto de cliente**.`,
    "",
    "## Instalar e usar",
    "",
    "**No Claude Code**, pelo marketplace de plugins:",
    "",
    "```bash",
    "/plugin marketplace add Terras-IA/skills",
    "/plugin install terras-linkedin@terras",
    "```",
    "",
    "Dentro do Claude Code, `/plugin` mostra o catálogo inteiro e instala o que você marcar; depois, `/plugin marketplace update terras` atualiza.",
    "",
    "**No ZCode, no Codex (GPT) e no opencode**, por link simbólico, com o repositório como fonte:",
    "",
    "```bash",
    "git clone https://github.com/Terras-IA/skills.git ~/terras-skills",
    "bash ~/terras-skills/scripts/instalar.sh            # simulação: mostra o que faria",
    "bash ~/terras-skills/scripts/instalar.sh --aplicar  # executa",
    "```",
    "",
    "O script cria um link por skill em cada pasta de agente que já existir na máquina: `~/.zcode/skills` (ZCode), `~/.codex/skills` (Codex/GPT), `~/.config/opencode/skills` (opencode) e `~/.claude/skills` (Claude Code). Pasta de agente que não existe não é criada, e o que já estiver no lugar vai para backup antes de ser substituído. Como o link aponta para o repositório, atualizar tudo depois é `git -C ~/terras-skills pull`.",
    "",
    "**Sem link simbólico** (Windows, ou agente que não segue link): copie a pasta `skills/<nome>/` para a pasta de skills do agente. É também o caminho para instalar apenas algumas skills, em vez do conjunto inteiro.",
    "",
    "**Como pedir.** A skill certa casa pelas palavras do seu pedido, então citar o termo forte ajuda mais do que pedir genérico: \"revisa esse post do LinkedIn\", \"erro de fila no Laravel\", \"monta a matriz GUT disso\". Cada skill abaixo lista as palavras-chave que a acionam.",
    "",
    "## Índice",
    "",
    ...indice,
    "",
  ];

  return [...comeco, ...blocos].join("\n").replace(/\n{3,}/g, "\n\n").trimEnd() + "\n";
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const destino = join(RAIZ, "MANUAL.md");
  const novo = gerarManual(RAIZ);
  if (process.argv.includes("--check")) {
    const atual = existsSync(destino) ? readFileSync(destino, "utf8") : "";
    if (atual !== novo) {
      console.error("MANUAL.md desatualizado: rode `node scripts/manual.mjs`.");
      process.exit(1);
    }
    console.log("ok: MANUAL.md em dia");
  } else {
    writeFileSync(destino, novo);
    console.log("MANUAL.md regravado");
  }
}

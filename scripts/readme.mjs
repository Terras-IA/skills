#!/usr/bin/env node
// A seção do catálogo no README é GERADA do catálogo real: a contagem e a
// lista de todas as skills instaláveis, cada uma com a descrição curta do
// cabeçalho. Mesma regra de exclusão do marketplace (scripts/marketplace.mjs):
// fora skill de processo do motor (.nao-instalar) e skill de projeto de
// cliente (marketplace-fora.json); skill que sai em plugin de grupo aparece
// apontando esse plugin.
//
//   npm run readme            # regrava a seção entre os marcadores
//   npm run readme -- --check # só confere (sai 1 se estiver desatualizado)
//
// A sincronia também é teste do gate (scripts/readme.test.mjs).
import { existsSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { cabecalho, semAspas } from "./marketplace.mjs";

export const INICIO = "<!-- catalogo:inicio -->";
export const FIM = "<!-- catalogo:fim -->";
const MAX_RESUMO = 170;

const lerJson = (caminho, padrao) => (existsSync(caminho) ? JSON.parse(readFileSync(caminho, "utf8")) : padrao);

// Conectivo que não pode ficar pendurado antes das reticências ("… e leitor de").
const CONECTIVO = new Set(["a", "à", "às", "ao", "aos", "as", "com", "da", "das", "de", "do", "dos", "e", "em", "entre", "na", "nas", "no", "nos", "o", "os", "ou", "para", "por", "que", "sem", "sobre", "um", "uma"]);

/** Descrição de uma linha para a tabela: corta em frase inteira (ou palavra inteira) e escapa o que quebra a célula. */
function resumo(texto) {
  let t = texto.replace(/\s+/g, " ").trim();
  if (t.length > MAX_RESUMO) {
    const corte = t.slice(0, MAX_RESUMO);
    const fim = corte.lastIndexOf(". ");
    if (fim > 0) {
      t = corte.slice(0, fim + 1);
    } else {
      const palavra = corte.slice(0, corte.lastIndexOf(" ")).replace(/[\s,;:]+$/, "").split(" ");
      while (palavra.length > 1 && CONECTIVO.has(palavra.at(-1).toLowerCase())) palavra.pop();
      t = `${palavra.join(" ")}…`;
    }
  }
  return t.replace(/\|/g, "\\|");
}

const singular = (n, um, varios) => `${n} ${n === 1 ? um : varios}`;

/** Catálogo instalável: nome, resumo e plugin de grupo (quando a skill sai em grupo), mais as contas. */
export function listarCatalogo(raiz) {
  const fora = lerJson(join(raiz, "marketplace-fora.json"), {});
  const grupos = lerJson(join(raiz, "marketplace-grupos.json"), {});
  const pluginDe = {};
  for (const [grupo, g] of Object.entries(grupos)) for (const nome of g.skills) pluginDe[nome] = grupo;
  const dirSkills = join(raiz, "skills");
  const skills = [];
  let total = 0;
  let naoInstalar = 0;
  for (const nome of readdirSync(dirSkills).sort()) {
    const dir = join(dirSkills, nome);
    if (!existsSync(join(dir, "SKILL.md"))) continue;
    total++;
    if (existsSync(join(dir, ".nao-instalar"))) {
      naoInstalar++;
      continue;
    }
    if (nome in fora) continue;
    const campos = cabecalho(readFileSync(join(dir, "SKILL.md"), "utf8")) ?? {};
    skills.push({ nome, resumo: resumo(semAspas(campos.description)), plugin: pluginDe[nome] });
  }
  return { skills, total, naoInstalar, fora: total - naoInstalar - skills.length };
}

/** Seção inteira, marcadores inclusive, pronta para entrar no README. */
export function montarSecao(raiz) {
  const { skills, total, naoInstalar, fora } = listarCatalogo(raiz);
  const razoes = [
    naoInstalar ? `${singular(naoInstalar, "skill", "skills")} de processo do motor (\`.nao-instalar\`)` : "",
    fora ? `${singular(fora, "skill ligada", "skills ligadas")} a projeto de cliente (\`marketplace-fora.json\`)` : "",
  ].filter(Boolean);
  const conta =
    skills.length === total
      ? `**${singular(skills.length, "skill instalável", "skills instaláveis")}** neste repositório.`
      : `**${singular(skills.length, "skill instalável", "skills instaláveis")}** entre as ${total} deste ` +
        `repositório; as demais ficam fora do marketplace — ${razoes.join(" e ")}.`;
  return [
    INICIO,
    "<!-- gerado por `npm run readme` a partir do catálogo — não edite à mão -->",
    "",
    conta,
    "",
    "<details>",
    `<summary><b>Ver a lista completa (${skills.length} skills)</b></summary>`,
    "",
    "| Skill | O que faz |",
    "|---|---|",
    ...skills.map((s) => `| [\`${s.nome}\`](skills/${s.nome}) | ${s.resumo}${s.plugin ? ` · Instale com o plugin \`${s.plugin}\`. |` : " |"}`),
    "",
    "</details>",
    FIM,
  ].join("\n");
}

/** Troca a seção entre os marcadores pelo texto novo, preservando o resto do arquivo. */
export function aplicarSecao(readme, secao) {
  const i = readme.indexOf(INICIO);
  const f = readme.indexOf(FIM);
  if (i === -1 || f === -1 || f < i) throw new Error(`README sem os marcadores ${INICIO} … ${FIM}`);
  return readme.slice(0, i) + secao + readme.slice(f + FIM.length);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const caminho = join(raiz, "README.md");
  const atual = readFileSync(caminho, "utf8");
  const novo = aplicarSecao(atual, montarSecao(raiz));
  const emDia = atual === novo;
  if (process.argv.includes("--check")) {
    console.log(emDia ? "README em dia com o catálogo" : "README DESATUALIZADO: rode npm run readme");
    process.exit(emDia ? 0 : 1);
  }
  if (!emDia) writeFileSync(caminho, novo);
  const { skills } = listarCatalogo(raiz);
  console.log(emDia ? "nada a mudar" : `README regravado: ${skills.length} skills na lista`);
}

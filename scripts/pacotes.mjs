#!/usr/bin/env node
// Gera um .zip por skill instalável para o upload de skill no claude.ai e no
// ChatGPT, que leem o mesmo formato: o zip contém a PASTA da skill no topo
// (<nome>/SKILL.md), não o SKILL.md solto.
//
// O filtro é o do marketplace: fica fora skill de processo do motor
// (.nao-instalar) e o que estiver em marketplace-fora.json. Entra no zip só
// arquivo RASTREADO pelo git: o que está no .gitignore (perfil.md com dado
// pessoal, config.json, token) não pode sair por carona num pacote.
//
// O upload recusa nome fora de [a-z0-9-] ou acima de 64 caracteres, nome
// diferente da pasta e descrição vazia ou acima de 1024: aqui isso é erro, antes
// de alguém descobrir na tela de upload. Skill que cita a pasta vizinha
// (../terras-x) sai com aviso: no upload cada zip é uma skill, então quem
// instala precisa subir a vizinha também.
//
//   npm run pacotes                  # gera dist/pacotes/ (apaga o anterior)
//   npm run pacotes -- terras-a ...  # só essas
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { crc32, deflateRawSync } from "node:zlib";
import { cabecalho, semAspas } from "./marketplace.mjs";

const NOME_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const MAX_NOME = 64;
const MAX_DESCRICAO = 1024;

const lerJson = (caminho, padrao) => (existsSync(caminho) ? JSON.parse(readFileSync(caminho, "utf8")) : padrao);

/** Arquivos rastreados pelo git dentro de skills/<nome>, relativos à pasta da skill. */
export function arquivosRastreados(raiz, nome) {
  const saida = execFileSync("git", ["-C", raiz, "ls-files", "-z", "--", `skills/${nome}`], { encoding: "utf8" });
  return saida
    .split("\0")
    .filter(Boolean)
    .map((p) => p.slice(`skills/${nome}/`.length))
    .filter((p) => p !== ".nao-instalar")
    .sort();
}

/** Skills que viram pacote: as instaláveis do catálogo, na ordem alfabética. */
export function skillsEmpacotaveis(raiz) {
  const fora = lerJson(join(raiz, "marketplace-fora.json"), {});
  return readdirSync(join(raiz, "skills"))
    .sort()
    .filter((nome) => {
      const dir = join(raiz, "skills", nome);
      return existsSync(join(dir, "SKILL.md")) && !existsSync(join(dir, ".nao-instalar")) && !(nome in fora);
    });
}

/** Erros que o upload recusaria e avisos de pasta vizinha, de uma skill. */
export function conferir(raiz, nome) {
  const txt = readFileSync(join(raiz, "skills", nome, "SKILL.md"), "utf8");
  const campos = cabecalho(txt);
  const erros = [];
  if (!campos) return { erros: ["SKILL.md sem cabeçalho ---"], avisos: [] };
  const nomeCab = semAspas(campos.name);
  const descricao = semAspas(campos.description);
  if (nomeCab !== nome) erros.push(`name "${nomeCab}" diferente da pasta`);
  if (!NOME_RE.test(nome) || nome.length > MAX_NOME) erros.push(`nome fora de [a-z0-9-] ou acima de ${MAX_NOME} caracteres`);
  if (!descricao) erros.push("description vazia");
  else if (descricao.length > MAX_DESCRICAO) erros.push(`description com ${descricao.length} caracteres (máximo ${MAX_DESCRICAO})`);
  const vizinhas = [...new Set([...txt.matchAll(/\.\.\/((?:terras|terrasia)-[a-z0-9-]+)/g)].map((m) => m[1]))].filter((v) => v !== nome).sort();
  return { erros, avisos: vizinhas.map((v) => `cita a pasta vizinha ${v}: suba o pacote dela também`) };
}

/**
 * Zip mínimo (deflate, sem dependência) e reprodutível: data fixa, ordem
 * alfabética, nada de metadado da máquina. Mesmo conteúdo, mesmos bytes.
 */
export function montarZip(entradas) {
  const DATA = (1 << 5) | 1; // 1980-01-01, a menor data DOS: sem relógio no zip
  const locais = [];
  const centrais = [];
  let deslocamento = 0;
  for (const { caminho, dados } of entradas) {
    const nome = Buffer.from(caminho, "utf8");
    const comprimido = deflateRawSync(dados);
    const usaDeflate = comprimido.length < dados.length;
    const corpo = usaDeflate ? comprimido : dados;
    const crc = crc32(dados);
    const comum = (b, o) => {
      b.writeUInt16LE(20, o); // versão necessária
      b.writeUInt16LE(0x0800, o + 2); // nome em UTF-8
      b.writeUInt16LE(usaDeflate ? 8 : 0, o + 4);
      b.writeUInt16LE(0, o + 6); // hora
      b.writeUInt16LE(DATA, o + 8);
      b.writeUInt32LE(crc, o + 10);
      b.writeUInt32LE(corpo.length, o + 14);
      b.writeUInt32LE(dados.length, o + 18);
      b.writeUInt16LE(nome.length, o + 22);
      b.writeUInt16LE(0, o + 24); // extra
    };
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    comum(local, 4);
    locais.push(local, nome, corpo);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(0x0314, 4); // feito por: unix, 2.0
    comum(central, 6);
    central.writeUInt32LE((0o100644 << 16) >>> 0, 38); // permissão de arquivo comum (sem sinal: << 16 estoura 31 bits)
    central.writeUInt32LE(deslocamento, 42);
    centrais.push(central, nome);
    deslocamento += local.length + nome.length + corpo.length;
  }
  const diretorio = Buffer.concat(centrais);
  const fim = Buffer.alloc(22);
  fim.writeUInt32LE(0x06054b50, 0);
  fim.writeUInt16LE(entradas.length, 8);
  fim.writeUInt16LE(entradas.length, 10);
  fim.writeUInt32LE(diretorio.length, 12);
  fim.writeUInt32LE(deslocamento, 16);
  return Buffer.concat([...locais, diretorio, fim]);
}

/** Zip de uma skill: <nome>/<arquivo> para cada arquivo rastreado. */
export function empacotar(raiz, nome) {
  const arquivos = arquivosRastreados(raiz, nome);
  return montarZip(arquivos.map((rel) => ({ caminho: `${nome}/${rel}`, dados: readFileSync(join(raiz, "skills", nome, rel)) })));
}

/** Gera os pacotes em <destino>; erro de qualquer skill aborta antes de gravar. */
export function gerarPacotes(raiz, destino, nomes = skillsEmpacotaveis(raiz)) {
  const empacotaveis = new Set(skillsEmpacotaveis(raiz));
  const relatorio = [];
  for (const nome of nomes) {
    if (!empacotaveis.has(nome)) throw new Error(`${nome}: não existe ou está fora do marketplace`);
    relatorio.push({ nome, ...conferir(raiz, nome) });
  }
  const comErro = relatorio.filter((r) => r.erros.length);
  if (comErro.length) throw new Error(comErro.map((r) => `${r.nome}: ${r.erros.join("; ")}`).join("\n"));
  rmSync(destino, { recursive: true, force: true });
  mkdirSync(destino, { recursive: true });
  for (const r of relatorio) {
    const zip = empacotar(raiz, r.nome);
    writeFileSync(join(destino, `${r.nome}.zip`), zip);
    r.bytes = zip.length;
  }
  return relatorio;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
  const destino = join(raiz, "dist/pacotes");
  const pedidos = process.argv.slice(2).filter((a) => !a.startsWith("-"));
  try {
    const relatorio = gerarPacotes(raiz, destino, pedidos.length ? pedidos : undefined);
    for (const r of relatorio) for (const a of r.avisos) console.log(`aviso: ${r.nome} ${a}`);
    const total = relatorio.reduce((s, r) => s + r.bytes, 0);
    console.log(`${relatorio.length} pacotes em dist/pacotes/ (${(total / 1e6).toFixed(1)} MB)`);
  } catch (e) {
    console.error(e.message);
    process.exit(1);
  }
}

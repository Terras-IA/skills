#!/usr/bin/env node
// Confere o arquivo de CV-base do Pitch por Vaga (https://pitch.coderstudio.club).
// Uso: node validar.mjs <arquivo.json> [--embrulhar]
//   --embrulhar  grava de volta no formato de importação {tipo, versao, cv} quando o arquivo veio só com o objeto do CV.
// Saída: JSON com erros e avisos. Código 0 = pode importar, 1 = erro de formato, 2 = só avisos.
import { readFileSync, writeFileSync } from "node:fs";

const TOPICOS = ["intro", "pitch", "skills", "exp", "proj", "why", "edu", "soft", "close"];
const PERGUNTAS = ["q-about", "q-why-leave", "q-strength", "q-weak", "q-challenge", "q-conflict", "q-hire", "q-english", "q-salary", "q-start", "q-ask"];
const VARIAVEIS = ["nome", "empresa", "vaga", "foco", "skills", "projetos", "motivo", "salario", "inicio", "tagline"];
const OBRIGATORIAS = { skills: ["skills"], proj: ["projetos"], why: ["empresa", "motivo"], "q-salary": ["salario"], "q-start": ["inicio"] };
const RECOMENDADAS = { pitch: ["foco"], "q-about": ["foco"], intro: ["nome"] };
const semVar = t => String(t || "").replace(/\{\{\w+\}\}/g, "");
const PT = /\b(você|voce|não|nao|para|também|empresa|trabalho|experiência|projeto|eu sou|minha|meu|com a|que eu)\b/i;

const [arq, ...flags] = process.argv.slice(2);
if (!arq) { console.error("uso: node validar.mjs <arquivo.json> [--embrulhar]"); process.exit(1); }
const erros = [], avisos = [];
let bruto;
try { bruto = JSON.parse(readFileSync(arq, "utf8")); }
catch (e) { console.log(JSON.stringify({ ok: false, erros: ["não é JSON válido: " + e.message], avisos }, null, 2)); process.exit(1); }

let cv = bruto, embrulhado = false;
if (bruto && typeof bruto.cv === "object") { cv = bruto.cv; embrulhado = true;
  if (bruto.tipo !== "pitch-cv") avisos.push('raiz: "tipo" deveria ser "pitch-cv"');
  if (bruto.versao !== 2) avisos.push("raiz: \"versao\" deveria ser 2");
} else avisos.push('o arquivo não está embrulhado em {"tipo":"pitch-cv","versao":2,"cv":{...}}; rode com --embrulhar');

const str = (v, onde, obrig = true) => { if (typeof v !== "string" || (obrig && !v.trim())) erros.push(`${onde}: texto obrigatório`); return typeof v === "string" ? v : ""; };
const lista = (v, onde) => { if (!Array.isArray(v)) { erros.push(`${onde}: deveria ser lista`); return []; } return v; };
const slug = (id, onde) => { if (typeof id !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(id)) erros.push(`${onde}: id "${id}" precisa ser slug (minúsculas, dígitos, hífen)`); };

str(cv.nome, "nome"); str(cv.titulo, "titulo"); str(cv.contato, "contato"); str(cv.tagline, "tagline");
if (/@|\+?\d[\d\s().-]{8,}\d/.test(cv.contato || "")) avisos.push("contato: parece ter e-mail ou telefone; o slide é público na tela, prefira cidade e links");

const projetos = lista(cv.projetos, "projetos");
if (projetos.length > 6) avisos.push(`projetos: ${projetos.length}, o ideal é até 6`);
const pids = new Set();
projetos.forEach((p, i) => { const o = `projetos[${i}]`; slug(p.id, o); if (pids.has(p.id)) erros.push(`${o}: id repetido "${p.id}"`); pids.add(p.id);
  ["nome", "curto", "stack", "fala"].forEach(k => str(p[k], `${o}.${k}`)); if (PT.test(semVar(p.fala))) avisos.push(`${o}.fala: parece português; o texto falado é em inglês`); });

const perfis = lista(cv.perfis, "perfis");
if (perfis.length < 2 || perfis.length > 5) avisos.push(`perfis: ${perfis.length}, o esperado é de 2 a 5 tipos de vaga`);
const perfIds = new Set();
perfis.forEach((p, i) => { const o = `perfis[${i}]`; slug(p.id, o); if (perfIds.has(p.id)) erros.push(`${o}: id repetido "${p.id}"`); perfIds.add(p.id);
  str(p.nome, `${o}.nome`); str(p.foco, `${o}.foco`);
  if (PT.test(semVar(p.foco))) avisos.push(`${o}.foco: parece português; o foco é falado em inglês`);
  const sk = lista(p.skills, `${o}.skills`); if (sk.length < 6 || sk.length > 10) avisos.push(`${o}.skills: ${sk.length}, o esperado é de 6 a 10`);
  lista(p.projetos, `${o}.projetos`).forEach(id => { if (!pids.has(id)) erros.push(`${o}.projetos: "${id}" não existe em projetos`); });
  if (!(p.projetos || []).length) avisos.push(`${o}.projetos: vazio, o slide de projetos fica em branco nesse perfil`); });

lista(cv.extras, "extras");
const exp = lista(cv.exp, "exp");
if (!exp.length) erros.push("exp: precisa de ao menos uma experiência");
if (exp.length > 6) avisos.push(`exp: ${exp.length}, o ideal é até 6`);
exp.forEach((e, i) => ["periodo", "cargo", "detalhe"].forEach(k => str(e[k], `exp[${i}].${k}`)));

const b = cv.bullets || {};
["pitch", "edu", "soft"].forEach(k => { const l = lista(b[k], `bullets.${k}`); if (!l.length) avisos.push(`bullets.${k}: vazio`); });

const textos = cv.textos || {};
for (const id of [...TOPICOS, ...PERGUNTAS]) {
  const t = textos[id];
  if (typeof t !== "string" || !t.trim()) { erros.push(`textos.${id}: faltando`); continue; }
  const usadas = [...t.matchAll(/\{\{(\w+)\}\}/g)].map(m => m[1]);
  usadas.filter(v => !VARIAVEIS.includes(v)).forEach(v => erros.push(`textos.${id}: variável {{${v}}} não existe no site`));
  (OBRIGATORIAS[id] || []).filter(v => !usadas.includes(v)).forEach(v => erros.push(`textos.${id}: precisa conter {{${v}}}`));
  (RECOMENDADAS[id] || []).filter(v => !usadas.includes(v)).forEach(v => avisos.push(`textos.${id}: costuma conter {{${v}}}`));
  if (/\{(?!\{)[a-z]+\}(?!\})/.test(t)) erros.push(`textos.${id}: variável com chave simples; use {{nome}}`);
  if (PT.test(semVar(t))) avisos.push(`textos.${id}: parece português; o texto falado é em inglês`);
}
Object.keys(textos).filter(k => ![...TOPICOS, ...PERGUNTAS].includes(k)).forEach(k => avisos.push(`textos.${k}: chave desconhecida, o site ignora`));

const lacunas = JSON.stringify(cv).match(/\[[^\]"]{2,80}\]/g) || [];
if (flags.includes("--embrulhar") && !embrulhado && !erros.length) writeFileSync(arq, JSON.stringify({ tipo: "pitch-cv", versao: 2, cv }, null, 2) + "\n");
const ok = !erros.length;
console.log(JSON.stringify({ ok, arquivo: arq, perfis: perfis.length, projetos: projetos.length, experiencias: exp.length, lacunas: lacunas.length, erros, avisos }, null, 2));
process.exit(!ok ? 1 : avisos.length ? 2 : 0);

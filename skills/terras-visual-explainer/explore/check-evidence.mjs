#!/usr/bin/env node
// Confere a evidência de código de cada diagrama com data-explore contra o repositório git.
// Uso: node check-evidence.mjs pagina.html --repo-dir /caminho/do/repo [--json]
// Sai com código 1 quando alguma referência falha. Não lê a working tree: só bytes do commit.
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';

const args = process.argv.slice(2);
const htmlPath = args.find((a) => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--repo-dir');
const repoDir = args.includes('--repo-dir') ? args[args.indexOf('--repo-dir') + 1] : process.cwd();
const asJson = args.includes('--json');
if (!htmlPath) {
  console.error('uso: node check-evidence.mjs pagina.html --repo-dir /caminho/do/repo [--json]');
  process.exit(2);
}

const git = (...a) => execFileSync('git', ['-C', repoDir, ...a], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
const tryGit = (...a) => { try { return git(...a); } catch { return null; } };

const html = readFileSync(htmlPath, 'utf8');
const shells = [...html.matchAll(/<section\b(?=[^>]*diagram-shell)(?=[^>]*data-explore)[^>]*>([\s\S]*?)<\/section>/g)];
const problems = [];
const checked = [];

shells.forEach((m, i) => {
  const body = m[1];
  const where = `diagrama ${i + 1}`;
  const src = body.match(/<script type="text\/plain" class="diagram-source">([\s\S]*?)<\/script>/)?.[1] || '';
  const evRaw = body.match(/<script type="application\/json" class="diagram-evidence">([\s\S]*?)<\/script>/)?.[1];
  if (!evRaw) return;
  let ev;
  try { ev = JSON.parse(evRaw); } catch (err) { problems.push({ where, rule: 'json', msg: err.message }); return; }

  if (!/^[0-9a-f]{40}$/.test(ev.commit || '')) {
    problems.push({ where, rule: 'commit-formato', msg: `commit precisa ter 40 caracteres hex: "${ev.commit}"` });
    return;
  }
  if (tryGit('cat-file', '-e', `${ev.commit}^{commit}`) === null) {
    problems.push({ where, rule: 'commit-ausente', msg: `commit ${ev.commit} não existe em ${repoDir}` });
    return;
  }
  if (ev.repo && /\/\/[^/]*@/.test(ev.repo)) {
    problems.push({ where, rule: 'credencial-na-url', msg: 'repo tem usuário ou token na URL; remover antes de publicar' });
  }

  for (const [id, list] of Object.entries(ev.nodes || {})) {
    if (!new RegExp(`(^|[^\\w-])${id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}([^\\w-]|$)`, 'm').test(src)) {
      problems.push({ where, rule: 'bloco-inexistente', msg: `evidência para "${id}", que não aparece na fonte Mermaid` });
    }
    if (list.length > 3) problems.push({ where, rule: 'muitas-faixas', msg: `"${id}" tem ${list.length} faixas; máximo 3` });
    for (const s of list) {
      const ref = `${s.path}${s.lines ? ':' + s.lines : ''}`;
      const blob = tryGit('show', `${ev.commit}:${s.path}`);
      if (blob === null) { problems.push({ where, rule: 'arquivo-ausente', msg: `${id}: ${s.path} não existe no commit` }); continue; }
      const total = blob.endsWith('\n') ? blob.split('\n').length - 1 : blob.split('\n').length;
      if (s.lines) {
        const [a, b = a] = String(s.lines).split('-').map(Number);
        if (!(a >= 1 && b >= a)) { problems.push({ where, rule: 'faixa-invalida', msg: `${id}: ${ref}` }); continue; }
        if (b > total) { problems.push({ where, rule: 'faixa-fora', msg: `${id}: ${ref} passa do fim (${total} linhas)` }); continue; }
      }
      checked.push(`${id} ${ref}`);
    }
  }
});

const result = { ok: problems.length === 0, diagramas: shells.length, conferidas: checked.length, problems };
if (asJson) console.log(JSON.stringify(result, null, 2));
else {
  console.log(`${shells.length} diagrama(s) com data-explore, ${checked.length} referência(s) conferida(s).`);
  problems.forEach((p) => console.log(`FALHA [${p.rule}] ${p.where}: ${p.msg}`));
  if (result.ok) console.log('OK: toda evidência existe no commit fixado.');
}
process.exit(result.ok ? 0 : 1);

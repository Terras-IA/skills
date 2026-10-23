// terras-coders-mural: helper injetado na aba https://app.coders.com.br (logada).
// Uso: cole o arquivo inteiro num javascript_exec; depois chame window.__mural.<fn>(...)
// em execuções curtas (a ferramenta de JS corta em ~45s). O token nunca sai da página.
(() => {
  const ORIGIN = 'https://app.coders.com.br';
  const CHANNEL = 'mural-posts';
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function guard() {
    if (location.origin !== ORIGIN) {
      throw new Error('aba errada: ' + location.origin + ' (navegue para ' + ORIGIN + '/comunidade)');
    }
    if (location.pathname.startsWith('/login')) {
      throw new Error('sessão expirada: a aba voltou para /login. Peça ao usuário para fazer login na COD3RS e reabra ' + ORIGIN + '/comunidade');
    }
    const t = localStorage.getItem('_cj_token');
    if (!t) throw new Error('sem sessão: faça login na COD3RS nesta aba');
    return t;
  }

  async function api(path, opts = {}) {
    const token = guard();
    const res = await fetch(path, {
      ...opts,
      headers: { Authorization: 'Bearer ' + token, 'Content-Type': 'application/json', ...(opts.headers || {}) },
    });
    const text = await res.text();
    let body;
    try { body = JSON.parse(text); } catch { throw new Error('resposta não-JSON (' + res.status + ') em ' + path); }
    if (!res.ok) throw new Error((body && body.error) || 'HTTP ' + res.status + ' em ' + path);
    return body;
  }

  // channelReads pode vir como array ou como objeto { '<slug>:<kind>': ... }.
  function channelKeys(cr) {
    if (!cr) return [];
    if (Array.isArray(cr)) {
      return cr.map((c) => (typeof c === 'string' ? c : c && (c.channel || c.key || c.id || c.slug))).filter(Boolean);
    }
    return Object.keys(cr);
  }

  let meCache = null;
  async function me() {
    if (!meCache) {
      const b = await api('/api/community/bootstrap');
      meCache = { username: b.me.username, displayName: b.me.displayName, channels: channelKeys(b.channelReads) };
    }
    return meCache;
  }

  // Espaços que não valem ponto (ou já são cobertos por list()).
  const NAO_PONTUAVEIS = ['mural-posts', 'geral', 'avisos', 'career-in-public', 'showcase', 'apresentacoes', 'mural-vagas'];

  // Slugs dos espaços de posts conhecidos (Domains e Stacks), para passar a listSpace().
  async function spaces() {
    const { channels } = await me();
    const slugs = channels.filter((k) => k.endsWith(':post')).map((k) => k.slice(0, -':post'.length));
    return [...new Set(slugs)].filter((s) => !NAO_PONTUAVEIS.includes(s)).sort();
  }

  const LINK_RE = /https?:\/\/(?:lnkd\.in|(?:www\.)?linkedin\.com)[^\s"'<>)\]\\]+/;
  // Um post do mural pode listar vários links (ex.: 3 posts do LinkedIn). Todos contam.
  // Lê o conteúdo inteiro (sem corte) e separa links colados sem espaço
  // ("https://lnkd.in/p/Xhttps://lnkd.in/p/X" vira um link só, depois do Set).
  function linksOf(p) {
    const all = (p.content || '') + ' ' + JSON.stringify(p.attachments || '');
    const re = new RegExp(LINK_RE.source, 'g');
    const out = [];
    for (const m of all.match(re) || []) {
      for (const part of m.split(/(?=https?:\/\/)/)) {
        const u = part.split('](')[0].split('?utm_')[0].replace(/[.,;:!?*_]+$/, '');
        if (new RegExp('^' + LINK_RE.source + '$').test(u)) out.push(u);
      }
    }
    return [...new Set(out)];
  }

  function slim(p, espaco = CHANNEL) {
    const links = linksOf(p);
    return {
      id: p.id,
      espaco,
      autor: p.authorDisplayName,
      quando: p.createdAt,
      titulo: p.title || '',
      texto: (p.content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim(),
      link: links[0] || null,
      links,
      curtido: !!p.likedByMe,
      comentarios: p.commentCount || 0,
    };
  }

  // Posts de outras pessoas. Sem argumentos: última página (mais recentes).
  // {hours: N} = desde N horas atrás; {before: ISO} = página anterior (o "rolar a tela").
  async function list({ hours, before } = {}) {
    const { username } = await me();
    let q = '?kind=post';
    if (hours) q += '&since=' + encodeURIComponent(new Date(Date.now() - hours * 3600e3).toISOString());
    else if (before) q += '&before=' + encodeURIComponent(before);
    const r = await api('/api/community/spaces/' + CHANNEL + '/messages' + q);
    const items = (r.items || []).filter((p) => p.author !== username).map((p) => slim(p));
    const oldest = (r.items || []).reduce((a, p) => (!a || p.createdAt < a ? p.createdAt : a), null);
    return { items, oldest, hasMore: !!r.hasMore };
  }

  // Posts de outras pessoas em qualquer espaço (Domains e Stacks; slugs em spaces()),
  // dos últimos `days` dias. Pagina com hasMore + before=<createdAt mais antigo>.
  // hasMore=true na volta = parou no limite de páginas antes de cobrir a janela.
  async function listSpace(slug, days = 30) {
    const { username } = await me();
    const since = new Date(Date.now() - days * 86400e3).toISOString();
    const base = '/api/community/spaces/' + encodeURIComponent(slug) + '/messages?kind=post';
    let pool = [];
    let r = await api(base);
    let oldest = null;
    for (let g = 0; ; g++) {
      const page = r.items || [];
      pool = pool.concat(page);
      oldest = pool.reduce((a, p) => (!a || p.createdAt < a ? p.createdAt : a), null);
      if (!r.hasMore || !page.length || (oldest && oldest < since)) { r = { hasMore: false }; break; }
      if (g >= 15) break;
      await sleep(200);
      r = await api(base + '&before=' + encodeURIComponent(oldest));
    }
    const seen = new Set();
    const items = pool
      .filter((p) => p.createdAt >= since && p.author !== username && !seen.has(p.id) && seen.add(p.id))
      .map((p) => slim(p, slug));
    return { espaco: slug, items, oldest, hasMore: !!r.hasMore };
  }

  // Ids em que o usuário já comentou no mural (use para pular o que já foi engajado).
  async function commented(ids) {
    const { username } = await me();
    const out = [];
    for (const id of ids) {
      const j = await api('/api/community/messages/' + id + '/comments');
      const arr = Array.isArray(j) ? j : j.items || j.comments || [];
      if (arr.some((c) => c.author === username)) out.push(id);
    }
    return out;
  }

  // Curtir é TOGGLE no servidor: só chama para posts com likedByMe === false,
  // relendo o estado na hora no espaço do post. Máx. 20 por chamada.
  async function likeIn(slug, ids) {
    if (ids.length > 20) throw new Error('máx. 20 por chamada');
    const { displayName } = await me();
    const state = {};
    const base = '/api/community/spaces/' + encodeURIComponent(slug) + '/messages?kind=post';
    let page = await api(base);
    let pool = page.items || [];
    for (let g = 0; g < 10 && page.hasMore && !ids.every((i) => pool.some((p) => p.id === i)); g++) {
      const oldest = pool.reduce((a, p) => (!a || p.createdAt < a ? p.createdAt : a), null);
      page = await api(base + '&before=' + encodeURIComponent(oldest));
      if (!page.items || !page.items.length) break;
      pool = pool.concat(page.items);
    }
    pool.forEach((p) => (state[p.id] = p.likedByMe));
    const res = [];
    for (const id of ids) {
      if (!(id in state)) { res.push([id, 'não encontrado']); continue; }
      if (state[id]) { res.push([id, 'já curtido']); continue; }
      const r = await api('/api/community/messages/' + id + '/like', {
        method: 'POST', body: JSON.stringify({ author: displayName }),
      });
      res.push([id, r.liked ? 'curtido' : 'ATENÇÃO: descurtiu']);
      await sleep(400);
    }
    return res;
  }

  // Mural de Posts.
  const like = (ids) => likeIn(CHANNEL, ids);

  // pairs = [[id, texto], ...]. Pula posts onde já existe comentário do usuário.
  // Máx. 10 por chamada (fica abaixo do timeout de 45s).
  async function comment(pairs) {
    if (pairs.length > 10) throw new Error('máx. 10 por chamada');
    const { displayName } = await me();
    const done = await commented(pairs.map((p) => p[0]));
    const res = [];
    for (const [id, content] of pairs) {
      if (done.includes(id)) { res.push([id, 'já comentado']); continue; }
      await api('/api/community/messages/' + id + '/comments', {
        method: 'POST', body: JSON.stringify({ author: displayName, content }),
      });
      res.push([id, 'comentado']);
      await sleep(500);
    }
    return res;
  }

  // Publica um post novo no mural. Só com aprovação explícita do texto final.
  async function publish({ title, content }) {
    const { displayName } = await me();
    return api('/api/community/spaces/' + CHANNEL + '/messages', {
      method: 'POST',
      body: JSON.stringify({ author: displayName, title, content, attachments: [], coverUrl: '', kind: 'post' }),
    });
  }

  window.__mural = { me, spaces, list, listSpace, commented, like, likeIn, comment, publish };
  return 'window.__mural pronto: ' + Object.keys(window.__mural).join(', ');
})();

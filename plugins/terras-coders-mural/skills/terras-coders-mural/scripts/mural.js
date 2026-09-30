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

  let meCache = null;
  async function me() {
    if (!meCache) {
      const b = await api('/api/community/bootstrap');
      meCache = { username: b.me.username, displayName: b.me.displayName };
    }
    return meCache;
  }

  const LINK_RE = /https?:\/\/(?:lnkd\.in|(?:www\.)?linkedin\.com)[^\s"'<>)\]\\]+/;
  function linkOf(p) {
    const all = (p.content || '') + ' ' + JSON.stringify(p.attachments || '');
    const m = all.match(LINK_RE);
    return m ? m[0].split('](')[0].split('?utm_')[0] : null;
  }

  function slim(p) {
    return {
      id: p.id,
      autor: p.authorDisplayName,
      quando: p.createdAt,
      titulo: p.title || '',
      texto: (p.content || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').slice(0, 280),
      link: linkOf(p),
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
    const items = (r.items || []).filter((p) => p.author !== username).map(slim);
    const oldest = (r.items || []).reduce((a, p) => (!a || p.createdAt < a ? p.createdAt : a), null);
    return { items, oldest, hasMore: !!r.hasMore };
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
  // relendo o estado na hora. Máx. 20 por chamada.
  async function like(ids) {
    if (ids.length > 20) throw new Error('máx. 20 por chamada');
    const { displayName } = await me();
    const state = {};
    let page = await api('/api/community/spaces/' + CHANNEL + '/messages?kind=post');
    let pool = page.items || [];
    for (let g = 0; g < 6 && !ids.every((i) => pool.some((p) => p.id === i)); g++) {
      const oldest = pool.reduce((a, p) => (!a || p.createdAt < a ? p.createdAt : a), null);
      page = await api('/api/community/spaces/' + CHANNEL + '/messages?kind=post&before=' + encodeURIComponent(oldest));
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

  window.__mural = { me, list, commented, like, comment, publish };
  return 'window.__mural pronto: ' + Object.keys(window.__mural).join(', ');
})();

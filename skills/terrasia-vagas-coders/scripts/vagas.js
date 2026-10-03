// terrasia-vagas-coders: helper injetado na aba https://app.coders.com.br (logada).
// Uso: cole o arquivo inteiro num javascript_exec; depois chame window.__vagas.<fn>(...)
// em execuções curtas (a ferramenta de JS corta em ~45s). O token nunca sai da página.
// SOMENTE LEITURA: nenhuma função aqui envia POST/PUT/DELETE.
(() => {
  const ORIGIN = 'https://app.coders.com.br';

  function guard() {
    if (location.origin !== ORIGIN) {
      throw new Error('aba errada: ' + location.origin + ' (navegue para ' + ORIGIN + '/comunidade#vagas)');
    }
    const t = localStorage.getItem('_cj_token');
    if (!t) throw new Error('sem sessão: faça login na COD3RS nesta aba');
    return t;
  }

  async function api(path) {
    const token = guard();
    const res = await fetch(path, { headers: { Authorization: 'Bearer ' + token } });
    const text = await res.text();
    let body;
    try { body = JSON.parse(text); } catch { throw new Error('resposta não-JSON (' + res.status + ') em ' + path); }
    if (!res.ok) throw new Error((body && (body.error || body.message)) || 'HTTP ' + res.status + ' em ' + path);
    return body;
  }

  // Identidade: board (assinante) com fallback para a comunidade.
  async function me() {
    try {
      const b = await api('/api/board/me');
      return { fonte: 'board', assinante: true, perfil: b };
    } catch (e) {
      const b = await api('/api/community/bootstrap');
      return { fonte: 'comunidade (sem acesso ao board?)', assinante: false, usuario: b.me && b.me.displayName, erroBoard: String(e.message || e) };
    }
  }

  async function facets() {
    const f = await api('/api/board/jobs/facets');
    return {
      fontes: (f.sources || []).map((s) => s.value || s),
      periodos: (f.schedules || []).map((s) => s.value || s),
      modalidades: (f.modalities || []).map((s) => s.value || s),
      escopos: (f.locationScopes || []).map((s) => s.value || s),
    };
  }

  const DATA = (j) => j.sentAt || j.firstSeenAt || j.createdAt || '';

  function slim(j) {
    return {
      quando: DATA(j),
      titulo: j.title || '',
      empresa: j.company || '',
      fonte: j.source || '',
      onde: j.location || '',
      escopo: j.locationScope || '',
      modalidade: j.modality || '',
      periodo: j.schedule || '',
      salario: j.salary || '',
      url: j.jobUrl || '',
    };
  }

  function params(o) {
    const n = new URLSearchParams();
    if (o.q) n.set('q', o.q);
    n.set('page', String(o.page));
    n.set('limit', String(o.limit));
    if (o.desde) n.set('dateFrom', o.desde);
    for (const s of o.fontes || []) n.append('source', s);
    for (const s of o.periodos || []) n.append('schedule', s);
    for (const s of o.modalidades || []) n.append('modality', s);
    for (const s of o.escopos || []) n.append('locationScope', s);
    n.set('avoidBrazil', o.semBrasil ? '1' : '0');
    return n.toString();
  }

  // Lista vagas. Opções (todas opcionais): { dias: 7 } OU { desde: 'YYYY-MM-DD' },
  // { q, fontes[], periodos[], modalidades[], escopos[], semBrasil, maxVagas: 300 }.
  // Pagina até esgotar, parar em 'desde' ou bater maxVagas.
  async function list(opts = {}) {
    const o = { dias: opts.desde ? undefined : (opts.dias || 7), page: 1, limit: 50, maxVagas: 300, ...opts };
    if (o.desde === undefined && o.dias !== undefined) {
      o.desde = new Date(Date.now() - o.dias * 864e5).toISOString().slice(0, 10);
    }
    const vistas = new Set();
    const itens = [];
    let total = null;
    for (let page = 1; page <= 8; page++) {
      o.page = page;
      const r = await api('/api/board/jobs?' + params(o));
      total = typeof r.total === 'number' ? r.total : total;
      const jobs = r.jobs || [];
      if (!jobs.length) break;
      for (const j of jobs) {
        const s = slim(j);
        if (vistas.has(s.url)) continue;
        vistas.add(s.url);
        itens.push(s);
      }
      const coletados = page * o.limit;
      if (itens.length >= o.maxVagas || coletados >= (total || 0) || jobs.length < o.limit) break;
      await new Promise((res) => setTimeout(res, 300));
    }
    itens.sort((a, b) => (a.quando < b.quando ? 1 : -1));
    return { total: total ?? itens.length, desde: o.desde || null, recebidas: Math.min(itens.length, o.maxVagas), vagas: itens.slice(0, o.maxVagas) };
  }

  window.__vagas = { me, facets, list, _api: api };
})();

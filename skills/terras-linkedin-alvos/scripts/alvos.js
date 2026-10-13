// terras-linkedin-alvos: helper para a página de atividade de um perfil
// (https://www.linkedin.com/in/<slug>/recent-activity/all/). A navegação zera o window:
// injete este arquivo de novo a cada perfil, junto com a chamada.
//   await window.__alvos.scan(48)      -> posts do perfil com menos de 48h
//   await window.__alvos.like(urn)     -> curte um post do scan (nunca descurte)
// Interface em português ou inglês.
//
// Layout de out/2026: o card é [role=listitem][componentkey^="update-card-focus"], sem data-urn
// no HTML. O URN só existe nas props do React (chave "reactionState-urn:li:activity:N"), e o botão
// de reação não tem aria-pressed: o estado vem no aria-label ("nenhuma reação" = não curtido).
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const CARD = 'main [role=listitem][componentkey^="update-card-focus"]';
  const REPOST = /compartilhou|republicou|reposted|shared this/i;
  const NO_REACTION = /nenhuma reação|no reaction/i;
  // Data absoluta ("9 de out.") ou relativa ("há 4 h", "4 h" sozinha na linha, "4h •").
  const DATE = /\d{1,2} de [a-zç]{3,5}\.(?: de \d{4})?|há \d+\s?(?:min|h|d|sem|m|a)\b|^\d+\s?(?:min|h|d|sem|w|mo)\b(?=\s*(?:•|$))/im;

  // O id de atividade do LinkedIn é um snowflake: os bits altos são o epoch em ms.
  const tsOf = (urn) => Number(BigInt(urn.split(':').pop()) >> 22n);

  // Dois ids por card: o da atividade (data real de publicação, inclusive post agendado) e o que o
  // botão de reação usa (em post agendado é um ugcPost com a data de criação do rascunho).
  function urnsOf(card) {
    const fk = Object.keys(card).find((k) => k.startsWith('__reactFiber'));
    if (!fk) return {};
    const SKIP = new Set(['_owner', 'return', 'stateNode', 'sibling', 'alternate', 'child']);
    const out = {};
    const walk = (o, d, seen) => {
      if ((out.atividade && out.reacao) || d > 7 || !o || typeof o !== 'object' || seen.has(o)) return;
      seen.add(o);
      for (const k of Object.keys(o)) {
        if (SKIP.has(k)) continue;
        let v;
        try { v = o[k]; } catch (e) { continue; }
        if (typeof v === 'string') {
          const r = v.match(/^reactionState-(urn:li:(?:activity|share|ugcPost):\d+)$/);
          if (r && !out.reacao) out.reacao = r[1];
          const a = v.match(/urn:li:activity:\d{15,}/);
          if (a && !out.atividade) out.atividade = a[0];
        } else if (v && typeof v === 'object') walk(v, d + 1, seen);
      }
    };
    // Desce só na subárvore do card (subir pega o id de outro card).
    const root = card[fk];
    const stack = [root];
    for (let n = 0; stack.length && n < 8000 && !(out.atividade && out.reacao); n++) {
      const f = stack.pop();
      walk(f.memoizedProps, 0, new WeakSet());
      if (f.child) stack.push(f.child);
      if (f.sibling && f !== root) stack.push(f.sibling);
    }
    return out;
  }
  const urnOf = (card) => { const u = urnsOf(card); return u.atividade || u.reacao || null; };

  const likeBtn = (card) =>
    [...card.querySelectorAll('button[aria-label]')].find((b) =>
      /^(Situação do botão de reação|Reaction button state)/i.test(b.getAttribute('aria-label')));
  const isLiked = (btn) => !NO_REACTION.test(btn.getAttribute('aria-label'));

  async function scan(maxAgeHours = 48) {
    if (!/linkedin\.com$/.test(location.hostname)) throw new Error('aba errada: ' + location.hostname);
    if (!/\/recent-activity\//.test(location.pathname)) throw new Error('abra /in/<slug>/recent-activity/all/');
    for (let i = 0; i < 25 && !document.querySelector(CARD); i++) await sleep(400);
    // O card chega pronto do servidor; o id só aparece quando o React hidrata, card a card.
    for (let i = 0; i < 30 && [...document.querySelectorAll(CARD)].some((c) => !urnOf(c)); i++) await sleep(400);
    const cards = [...document.querySelectorAll(CARD)];
    if (!cards.length) return { perfil: document.title, posts: [], aviso: 'nenhum post carregado (perfil sem atividade pública?)' };
    const now = Date.now();
    const posts = cards.map((c) => {
      const { atividade, reacao } = urnsOf(c);
      const urn = atividade || reacao || null;
      const lines = c.innerText.split('\n').map((s) => s.trim()).filter(Boolean);
      const head = lines.slice(0, 3).join(' ');
      const repost = REPOST.test(head);
      const ts = urn ? tsOf(urn) : null; // o id carrega o instante em que foi criado
      const dataVisivel = (lines.slice(0, 14).join('\n').match(DATE) || [null])[0];
      const btn = likeBtn(c);
      return {
        urn,
        urnReacao: reacao || null, // o que o "Gostei" do card curte; em repost é o post original
        url: urn ? 'https://www.linkedin.com/feed/update/' + urn + '/' : null,
        publicado: ts ? new Date(ts).toISOString() : null,
        idadeHoras: ts ? Math.round((now - ts) / 36e5) : null,
        dataVisivel,
        repost,
        curtido: btn ? isLiked(btn) : null,
        texto: c.innerText.replace(/\s+/g, ' ').slice(0, 700),
      };
    });
    const comIdade = posts.filter((p) => p.idadeHoras !== null);
    return {
      perfil: document.title.replace(/^[^|]*Atividades?\s*\|\s*|^Activity\s*\|\s*/i, '').replace(/\s*\|\s*LinkedIn.*$/, ''),
      posts: posts.filter((p) => p.idadeHoras !== null && p.idadeHoras <= maxAgeHours),
      maisRecenteHoras: comIdade.length ? Math.min(...comIdade.map((p) => p.idadeHoras)) : null,
      // Post sem URN não entra em `posts`: confira à mão pela dataVisivel.
      semUrn: posts.filter((p) => !p.urn).map((p) => ({ dataVisivel: p.dataVisivel, texto: p.texto.slice(0, 120) })),
      // Último post próprio e último repost pela data visível, para revisar alvo parado.
      ultimoProprio: (posts.find((p) => !p.repost) || {}).dataVisivel || null,
      ultimoRepost: (posts.find((p) => p.repost) || {}).dataVisivel || null,
    };
  }

  async function like(urn) {
    const card = [...document.querySelectorAll(CARD)].find((c) => { const u = urnsOf(c); return u.atividade === urn || u.reacao === urn; });
    if (!card) throw new Error('post não está na página: ' + urn);
    const btn = likeBtn(card);
    if (!btn) throw new Error('botão de reação não encontrado');
    if (isLiked(btn)) return 'já curtido';
    btn.click();
    for (let i = 0; i < 10; i++) {
      await sleep(400);
      const b = likeBtn(card);
      if (b && isLiked(b)) return 'curtido';
    }
    throw new Error('não confirmado: confira o post antes de clicar de novo (o botão é toggle)');
  }

  window.__alvos = { scan, like, urnsOf };
})();

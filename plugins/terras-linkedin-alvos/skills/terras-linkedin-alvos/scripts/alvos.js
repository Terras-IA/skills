// terras-linkedin-alvos: helper para a página de atividade de um perfil
// (https://www.linkedin.com/in/<slug>/recent-activity/all/). A navegação zera o window:
// injete este arquivo de novo a cada perfil, junto com a chamada.
//   await window.__alvos.scan(48)      -> posts do perfil com menos de 48h
//   await window.__alvos.like(urn)     -> curte um post do scan (nunca descurte)
// Interface em português ou inglês.
(() => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const REPOST = /compartilhou isso|republicou|reposted this|shared this/i;

  // O id de atividade do LinkedIn é um snowflake: os bits altos são o epoch em ms.
  const tsOf = (urn) => Number(BigInt(urn.split(':').pop()) >> 22n);

  function likeBtn(card) {
    return [...card.querySelectorAll('button[aria-pressed]')].find((b) =>
      /gostei|like|reagir|react/i.test((b.getAttribute('aria-label') || '') + ' ' + b.innerText));
  }

  async function scan(maxAgeHours = 48) {
    if (!/linkedin\.com$/.test(location.hostname)) throw new Error('aba errada: ' + location.hostname);
    if (!/\/recent-activity\//.test(location.pathname)) throw new Error('abra /in/<slug>/recent-activity/all/');
    for (let i = 0; i < 20 && !document.querySelector('main [data-urn^="urn:li:activity:"]'); i++) await sleep(400);
    const cards = [...document.querySelectorAll('main [data-urn^="urn:li:activity:"]')];
    if (!cards.length) return { perfil: document.title, posts: [], aviso: 'nenhum post carregado (perfil sem atividade pública?)' };
    const now = Date.now();
    const posts = cards.map((c) => {
      const urn = c.getAttribute('data-urn');
      const ts = tsOf(urn);
      const head = c.innerText.slice(0, 200);
      const btn = likeBtn(c);
      return {
        urn,
        url: 'https://www.linkedin.com/feed/update/' + urn + '/',
        publicado: new Date(ts).toISOString(),
        idadeHoras: Math.round((now - ts) / 36e5),
        repost: REPOST.test(head),
        curtido: btn ? btn.getAttribute('aria-pressed') === 'true' : null,
        texto: c.innerText.replace(/\s+/g, ' ').slice(0, 700),
      };
    });
    return {
      perfil: document.title.replace(/^[^|]*Atividades?\s*\|\s*|^Activity\s*\|\s*/i, '').replace(/\s*\|\s*LinkedIn.*$/, ''),
      posts: posts.filter((p) => p.idadeHoras <= maxAgeHours),
      maisRecenteHoras: posts.length ? Math.min(...posts.map((p) => p.idadeHoras)) : null,
    };
  }

  async function like(urn) {
    const card = document.querySelector('main [data-urn="' + urn + '"]');
    if (!card) throw new Error('post não está na página: ' + urn);
    const btn = likeBtn(card);
    if (!btn) throw new Error('botão de reação não encontrado');
    if (btn.getAttribute('aria-pressed') === 'true') return 'já curtido';
    btn.click();
    for (let i = 0; i < 10; i++) {
      await sleep(400);
      if (btn.getAttribute('aria-pressed') === 'true') return 'curtido';
    }
    throw new Error('não confirmado: confira o post antes de clicar de novo (o botão é toggle)');
  }

  window.__alvos = { scan, like };
})();

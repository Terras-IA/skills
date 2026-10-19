// Coletor de posts da busca/timeline do X (x.com). Só lê: não curte, não reposta,
// não segue, não responde. Os únicos cliques são em "Mostrar mais" (expande o
// texto no lugar) e "Mostrar original" (desfaz a tradução automática), nenhum
// com efeito na conta. Devolve uma string JSON compacta: grave-a como veio.
// Uso no javascript_tool, colando este arquivo inteiro e na mesma chamada:
//   await xColetar({rolagens: 6})
async function xColetar({rolagens = 6, original = true, pausa = 1800} = {}) {
  const dorme = ms => new Promise(r => setTimeout(r, ms));
  const num = s => {
    if (!s) return 0;
    const m = String(s).replace(/\./g, '').replace(',', '.').match(/([\d.]+)\s*(mil|mi|k|m)?/i);
    if (!m) return 0;
    let v = parseFloat(m[1]);
    const u = (m[2] || '').toLowerCase();
    if (u === 'mil' || u === 'k') v *= 1e3;
    if (u === 'mi' || u === 'm') v *= 1e6;
    return Math.round(v);
  };
  const metrica = (rotulo, ...nomes) => {
    for (const n of nomes) {
      const m = rotulo.match(new RegExp('([\\d.,]+)\\s+' + n, 'i'));
      if (m) return num(m[1]);
    }
    return 0;
  };
  if (document.querySelector('a[href="/login"], a[data-testid="loginButton"]') &&
      !document.querySelector('[data-testid="SideNav_AccountSwitcher_Button"]')) {
    return JSON.stringify({erro: 'deslogado'});
  }
  const vistos = new Map();
  const ler = async () => {
    for (const a of document.querySelectorAll('article[data-testid="tweet"]')) {
      const link = a.querySelector('time')?.closest('a')?.href;
      if (!link || vistos.has(link)) continue;
      const mais = a.querySelector('[data-testid="tweet-text-show-more-link"]');
      if (mais && mais.tagName === 'BUTTON') { mais.click(); await dorme(600); }
      if (original && /Traduzido d|Translated from/i.test(a.innerText)) {
        const b = [...a.querySelectorAll('button, [role="button"], span')]
          .find(e => /^(Mostrar original|Show original)$/i.test(e.innerText?.trim()));
        if (b) { b.click(); await dorme(700); }
      }
      const nomeBloco = a.querySelector('[data-testid="User-Name"]')?.innerText.split('\n') || [];
      const rotulo = a.querySelector('[role="group"]')?.getAttribute('aria-label') || '';
      const textos = [...a.querySelectorAll('[data-testid="tweetText"]')];
      const statusLinks = [...a.querySelectorAll('a[href*="/status/"]')].map(x => x.href.split('?')[0])
        .filter(h => !h.includes('/analytics') && !h.includes('/photo/') && !h.includes('/video/'));
      vistos.set(link, {
        url: link.split('?')[0],
        nome: nomeBloco[0] || '',
        handle: (nomeBloco.find(s => s.startsWith('@')) || '').slice(1),
        data: a.querySelector('time')?.getAttribute('datetime') || null,
        texto: textos[0]?.innerText || '',
        truncado: !!a.querySelector('[data-testid="tweet-text-show-more-link"]'),
        citado: textos[1] ? {texto: textos[1].innerText, url: statusLinks.find(h => h !== link.split('?')[0]) || null} : null,
        traduzido: /Traduzido d|Translated from/i.test(a.innerText) && !/Mostrar tradução|Show translation/i.test(a.innerText),
        repost: a.querySelector('[data-testid="socialContext"]')?.innerText || null,
        promovido: /\bPromovido\b|\bPromoted\b|\bAnúncio\b|\bAd\b$/m.test(a.innerText),
        verificado: !!a.querySelector('[data-testid="icon-verified"]'),
        midia: [a.querySelector('[data-testid="videoPlayer"]') && 'video', a.querySelector('[data-testid="tweetPhoto"]') && 'foto', a.querySelector('[data-testid="card.wrapper"]') && 'card'].filter(Boolean),
        links: [...a.querySelectorAll('[data-testid="tweetText"] a, [data-testid="card.wrapper"] a')]
          .map(x => x.href).filter(h => !/x\.com\/(hashtag|search)|\/status\/|^https:\/\/x\.com\/[A-Za-z0-9_]+$/.test(h)),
        respostas: metrica(rotulo, 'respostas?', 'repl(y|ies)'),
        reposts: metrica(rotulo, 'reposts?'),
        curtidas: metrica(rotulo, 'curtidas?', 'likes?'),
        salvos: metrica(rotulo, 'items? salvos?', 'bookmarks?'),
        views: metrica(rotulo, 'visualizações', 'views?'),
      });
    }
  };
  for (let i = 0; i <= rolagens; i++) {
    await ler();
    if (i < rolagens) { window.scrollBy(0, window.innerHeight * 1.6); await dorme(pausa); }
  }
  return JSON.stringify({consulta: new URLSearchParams(location.search).get('q'), coletadoEm: new Date().toISOString(), total: vistos.size, posts: [...vistos.values()]});
}

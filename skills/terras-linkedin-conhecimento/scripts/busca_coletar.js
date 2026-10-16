// Coleta posts com imagem da busca de conteúdo do LinkedIn (navegador logado).
// Abra antes: https://www.linkedin.com/search/results/content/?keywords=TEMA&contentType=%22photos%22&datePosted=%22past-month%22
// Cole o arquivo inteiro no javascript_tool; na mesma execução: await buscaColetar(2, 6)
//   -> { q, total, out: [{autor, img, reac, urn, texto}] }, ordenado por reações.
// Para reusar em várias buscas sem colar de novo: sessionStorage.coleta = '(' + buscaColetar + ')'
// e, depois de cada navegação, await eval(sessionStorage.coleta)(2, 6).
//
// Só lê. A URN sai das props do React do card; nenhum clique. O menu "..." da busca não tem
// "Incorporar" e "Copiar link" escreve na área de transferência do usuário: não usar.

async function buscaColetar(ROLAGENS = 2, TOP = 6) {
  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
  function cards() {
    const v = new Set(), l = [];
    for (const h of document.querySelectorAll('h2,h3,span')) {
      if (h.innerText !== 'Publicação no feed') continue;
      let c = h.parentElement;
      while (c && c.innerText.length < 150) c = c.parentElement;
      if (!c) continue;
      const k = c.innerText.slice(0, 160);
      if (v.has(k)) continue; // o mesmo card aparece duas vezes na árvore
      v.add(k); l.push(c);
    }
    return l;
  }
  const PREFIXO = 'Abrir menu de controle da publicação de ';
  const menuDoCard = (c) => [...c.querySelectorAll('button')].find((x) => (x.getAttribute('aria-label') || '').startsWith(PREFIXO));
  function urn(btn) {
    const re = /urn:li:(?:activity|ugcPost|share):\d+/;
    const k = Object.keys(btn).find((k) => k.startsWith('__reactFiber'));
    let f = btn[k], n = 0;
    while (f && n < 80) {
      try {
        const s = JSON.stringify(f.memoizedProps, (kk, v) => (typeof v === 'object' && v && v.$$typeof) ? undefined : v);
        const m = s && s.match(re);
        if (m) return m[0];
      } catch (e) { /* props circulares */ }
      f = f.return; n++;
    }
    return null;
  }
  function reacoes(t) {
    const ls = t.split('\n').map((s) => s.trim()).filter(Boolean).slice(-12);
    const n = ls.find((s) => /^[\d.,]+( mil)?$/.test(s));
    if (!n) return 0;
    let v = parseFloat(n.replace(/\./g, '').replace(',', '.'));
    if (/mil/.test(n)) v *= 1000;
    return v;
  }
  // a busca rola dentro de <main id="workspace">, não na janela
  for (let i = 0; i < 20 && !document.getElementById('workspace'); i++) await esperar(500);
  await esperar(3000);
  for (let i = 0; i < ROLAGENS; i++) {
    const ws = document.getElementById('workspace') || document.scrollingElement;
    ws.scrollTop = ws.scrollHeight;
    await esperar(2500);
  }
  const todos = cards();
  const lista = todos.map((c) => {
    const b = menuDoCard(c);
    return { b, autor: b && b.getAttribute('aria-label').replace(PREFIXO, ''), t: c.innerText,
      video: c.querySelectorAll('video').length > 0,
      img: [...c.querySelectorAll('img')].filter((x) => /feedshare|image-shrink|article-cover/.test(x.src)).length };
  })
    .filter((p) => p.autor && !/Promovida|Promoted/.test(p.t.slice(0, 400)) && !p.video && p.img > 0 && p.t.length > 450
      && !/hiring|vaga |vagas|looking for a|estamos buscando|we are currently looking|recruit|estágio|open to work/i.test(p.t.slice(0, 700)))
    .map((p) => ({ autor: p.autor, img: p.img, reac: reacoes(p.t), urn: urn(p.b),
      texto: p.t.replace(/\s+/g, ' ').replace(/^Publicação no feed /, '').replace(/^.*?Seguir /, '').slice(0, 200) }))
    .sort((a, b) => b.reac - a.reac);
  return { q: new URLSearchParams(location.search).get('keywords'), total: todos.length, out: lista.slice(0, TOP) };
}

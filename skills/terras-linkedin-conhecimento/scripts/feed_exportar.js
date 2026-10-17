// Exporta os posts do feed do LinkedIn já aberto e logado, para análise em lote.
// Abra antes https://www.linkedin.com/feed/ com a ordenação "Mais recentes".
//
// Dois jeitos de rodar:
//   - navegador embutido: cole o arquivo inteiro no javascript_tool e, na mesma execução,
//     await feedExportar({alvo: 120})                 -> {total, posts: [...]}
//   - console do navegador do usuário (F12 › Console): cole o arquivo e rode
//     await feedExportar({alvo: 120, baixar: true})   -> baixa feed-linkedin.json
//
// Cada post: {url, urn, autor, quando, texto, promovido, temVideo, links}. O formato é o que
// scripts/feed_indice.py lê. Alvo acima do mínimo pedido: duplicata e repost saem na contagem.
//
// Só lê. A URN sai das props do React do botão "..." do card, sem abrir menu; o único clique é
// no "…mais" do próprio texto, que só expande. Nunca clica em "Copiar link".

async function feedExportar({ alvo = 120, maxRolagens = 120, baixar = false } = {}) {
  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
  const PREFIXO = 'Abrir menu de controle da publicação de ';

  // O feed novo não tem data-urn: cada post é um card com o título oculto "Publicação no feed".
  function cards() {
    const vistos = new Set(), lista = [];
    for (const h of document.querySelectorAll('h2,h3,span')) {
      if (h.innerText !== 'Publicação no feed') continue;
      let c = h.parentElement;
      while (c && c.innerText.length < 150) c = c.parentElement;
      if (!c) continue;
      const chave = c.innerText.slice(0, 160);
      if (vistos.has(chave)) continue; // o mesmo card aparece duas vezes na árvore
      vistos.add(chave); lista.push(c);
    }
    return lista;
  }
  const menuDoCard = (c) => [...c.querySelectorAll('button')]
    .find((b) => (b.getAttribute('aria-label') || '').startsWith(PREFIXO));
  function urnDoBotao(btn) {
    const re = /urn:li:(?:activity|ugcPost|share):\d+/;
    const k = Object.keys(btn).find((x) => x.startsWith('__reactFiber'));
    let f = k && btn[k], n = 0;
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
  function quando(texto) {
    const m = texto.match(/\n\s*(\d+\s*(?:min|h|d|sem|m|a|w|mo|yr)s?)\s*[•·]/);
    return m ? m[1] : '';
  }

  const posts = new Map();
  for (let i = 0; i < maxRolagens && posts.size < alvo; i++) {
    for (const c of cards()) {
      const btn = menuDoCard(c);
      if (!btn) continue;
      const urn = urnDoBotao(btn);
      const autor = btn.getAttribute('aria-label').replace(PREFIXO, '');
      const chave = urn || `${autor}|${c.innerText.slice(0, 200)}`;
      if (posts.has(chave)) continue;
      const mais = [...c.querySelectorAll('button')].find((b) => /^…?\s*(mais|more|ver mais|see more)$/i.test(b.innerText.trim()));
      if (mais) { mais.click(); await esperar(150); }
      const texto = c.innerText.replace(/^Publicação no feed\s*/, '');
      posts.set(chave, {
        url: urn ? `https://www.linkedin.com/feed/update/${urn}/` : '',
        urn,
        autor,
        quando: quando(c.innerText),
        texto,
        promovido: /Promovida|Promoted/.test(c.innerText.slice(0, 400)),
        temVideo: c.querySelectorAll('video').length > 0,
        links: [...new Set([...c.querySelectorAll('a[href]')].map((a) => a.href))],
      });
    }
    window.scrollBy(0, 2500);
    await esperar(1500);
    const carregar = [...document.querySelectorAll('button')].find((b) => /Carregar mais|Show more/.test(b.innerText));
    if (carregar) { carregar.click(); await esperar(2000); }
  }

  const lista = [...posts.values()];
  if (baixar) {
    const blob = new Blob([JSON.stringify(lista, null, 2)], { type: 'application/json' });
    Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'feed-linkedin.json' }).click();
  }
  return { total: lista.length, semUrn: lista.filter((p) => !p.urn).length, posts: baixar ? undefined : lista };
}

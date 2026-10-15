// Coleta posts do feed do LinkedIn já aberto e logado no navegador.
// Cole o arquivo inteiro no javascript_tool e chame, na mesma execução ou depois:
//   await feedColetar({rolagens: 8})          -> lista de posts {autor, texto, video, cardIdx}
//   await feedUrn('Nome do autor')            -> 'urn:li:ugcPost:...' do post desse autor
//
// Só lê: abre o menu "..." do card e o diálogo "Incorporar esta publicação" (que traz a URN)
// e fecha o diálogo pelo botão "Fechar". Nunca clica em "Copiar link" nem "Copiar código":
// um clique sintético nesses itens escreve na área de transferência do usuário.

(() => {
  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

  // O feed novo não tem data-urn: cada post é um card com o título oculto "Publicação no feed".
  function cards() {
    const vistos = new Set();
    const lista = [];
    for (const h of document.querySelectorAll('h2,h3,span')) {
      if (h.innerText !== 'Publicação no feed') continue;
      let c = h.parentElement;
      while (c && c.innerText.length < 150) c = c.parentElement;
      if (!c) continue;
      const chave = c.innerText.slice(0, 160);
      if (vistos.has(chave)) continue; // o mesmo card aparece duas vezes na árvore
      vistos.add(chave);
      lista.push(c);
    }
    return lista;
  }

  function autorDoCard(c) {
    const b = [...c.querySelectorAll('button')]
      .map((x) => x.getAttribute('aria-label') || '')
      .find((l) => l.startsWith('Abrir menu de controle da publicação de '));
    return b ? b.replace('Abrir menu de controle da publicação de ', '') : null;
  }

  // Varre também shadow DOM: o diálogo de incorporar vive dentro de um shadowRoot.
  function varrer(raiz, fn) {
    raiz.querySelectorAll('*').forEach((e) => {
      if (e.shadowRoot) varrer(e.shadowRoot, fn);
      fn(e);
    });
  }

  function dialogoIncorporar() {
    let campo = null;
    varrer(document, (e) => {
      if (!campo && typeof e.value === 'string' && e.value.includes('embed/feed/update')) campo = e;
    });
    if (!campo) return null;
    let d = campo;
    while (d && !(d.getAttribute && d.getAttribute('role') === 'dialog')) d = d.parentNode;
    return { campo, dialogo: d };
  }

  async function fecharDialogo() {
    for (let i = 0; i < 5; i++) {
      const x = dialogoIncorporar();
      if (!x) return true;
      const fechar = x.dialogo && [...x.dialogo.querySelectorAll('button')]
        .find((b) => b.getAttribute('aria-label') === 'Fechar');
      if (fechar) fechar.click();
      await esperar(700);
    }
    return !dialogoIncorporar();
  }

  window.feedColetar = async ({ rolagens = 8 } = {}) => {
    for (let i = 0; i < rolagens; i++) {
      window.scrollBy(0, 2500);
      await esperar(1500);
      const mais = [...document.querySelectorAll('button')].find((b) => /Carregar mais|Show more/.test(b.innerText));
      if (mais) { mais.click(); await esperar(2000); }
    }
    return cards().map((c, i) => ({
      cardIdx: i,
      autor: autorDoCard(c),
      promovido: /Promovida|Promoted/.test(c.innerText.slice(0, 400)),
      video: c.querySelectorAll('video').length > 0,
      texto: c.innerText.replace(/\s+/g, ' ').slice(0, 600),
    }));
  };

  window.feedUrn = async (autor) => {
    if (!(await fecharDialogo())) return { erro: 'diálogo anterior não fechou' };
    const menu = [...document.querySelectorAll('button')]
      .find((b) => b.getAttribute('aria-label') === 'Abrir menu de controle da publicação de ' + autor);
    if (!menu) return { erro: 'card não encontrado: ' + autor };
    menu.scrollIntoView({ block: 'center' });
    await esperar(600);
    menu.click();
    await esperar(1000);
    const item = [...document.querySelectorAll('[role=menuitem]')]
      .find((e) => e.innerText.trim() === 'Incorporar esta publicação');
    if (!item) { document.body.click(); return { erro: 'item Incorporar ausente (post sem embed)' }; }
    item.click();
    let x = null;
    for (let i = 0; i < 10 && !x; i++) { await esperar(500); x = dialogoIncorporar(); }
    const m = x && x.campo.value.match(/embed\/feed\/update\/(urn:li:[a-zA-Z]+:\d+)/);
    await fecharDialogo();
    return m ? { autor, urn: m[1], url: `https://www.linkedin.com/feed/update/${m[1]}/` } : { erro: 'URN não lida' };
  };

  return 'feedColetar e feedUrn prontos';
})();

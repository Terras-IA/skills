// Varre o feed do LinkedIn já aberto e logado, acumulando os posts de uma carga de página.
// Cole o arquivo inteiro no javascript_tool, em toda carga de página. Depois, em chamadas separadas (cada uma < 45 s):
//   feedVarrerInicio(desdeMs)          -> zera o acumulado e fixa o início da janela (epoch em ms)
//   await feedVarrer({segundos: 35})   -> rola e colhe; repita até `parar: true`
//   feedVarrerResultado(excluir)       -> string JSON compacta com os posts da janela; `excluir` =
//                                         ids (fim da URN) ou autores já gravados em carga anterior
//
// Uma carga de página dá de 40 a 80 posts: depois disso o scroll infinito para de carregar
// (`motivo: 'carga esgotada'`) e não há botão de "carregar mais". Mais posts = recarregar o feed e
// fazer nova carga; o varredura.py junta as cargas sem duplicar.
//
// Estado em window.__varredura: sobrevive entre chamadas, some se a página recarregar.
// Só lê: nenhum clique em post, menu ou botão. A URN sai das props do React do botão "..." do card,
// e a data exata sai do próprio ID da URN (os 41 bits altos são o epoch em ms).

function feedVarrerInstalar() {
  const PREFIXO = 'Abrir menu de controle da publicação de ';
  const tsDoId = (urn) => Number(BigInt(urn.split(':').pop()) >> 22n);

  function urnDoBotao(btn) {
    const re = /urn:li:(?:activity|ugcPost|share):\d+/g;
    const k = Object.keys(btn).find((x) => x.startsWith('__reactFiber'));
    let f = btn[k], n = 0;
    const achadas = [];
    while (f && n < 80) {
      try {
        const s = JSON.stringify(f.memoizedProps, (kk, v) => (typeof v === 'object' && v && v.$$typeof) ? undefined : v);
        for (const m of (s && s.match(re)) || []) if (!achadas.includes(m)) achadas.push(m);
      } catch (e) { /* props circulares */ }
      f = f.return; n++;
    }
    // anúncio traz activity e share do mesmo post; a mais nova (maior ID) é a publicação
    return achadas.sort((a, b) => tsDoId(b) - tsDoId(a))[0] || null;
  }

  // Sem URN (post de grupo, "parabenizou"): data aproximada pelo rótulo do card.
  const MESES = { jan: 0, fev: 1, mar: 2, abr: 3, mai: 4, jun: 5, jul: 6, ago: 7, set: 8, out: 9, nov: 10, dez: 11 };
  function tsDoRotulo(linhas) {
    const agora = Date.now();
    for (const l of linhas.slice(0, 14)) {
      if (/^(Agora mesmo|Agora|Just now)$/i.test(l)) return agora;
      let m = l.match(/^(?:há\s+)?(\d+)\s*(min|h|d|sem|m[eê]s|a)\b/);
      if (m) {
        const mult = { min: 6e4, h: 36e5, d: 864e5, sem: 6048e5, a: 31536e6 }[m[2]] || 2592e6;
        return agora - Number(m[1]) * mult;
      }
      m = l.match(/^(\d{1,2}) de (\w{3})\.?(?: de (\d{4}))?$/);
      if (m && m[2] in MESES) {
        const d = new Date(m[3] ? Number(m[3]) : new Date().getFullYear(), MESES[m[2]], Number(m[1]), 12);
        if (d.getTime() > agora) d.setFullYear(d.getFullYear() - 1);
        return d.getTime();
      }
    }
    return null;
  }

  function cardDoBotao(btn) {
    let c = btn;
    while (c && !/^Publicação no feed/.test(c.innerText || '')) c = c.parentElement;
    return c;
  }

  function tipo(c) {
    if (c.querySelector('video')) return 'video';
    if (/Documento|páginas\b/.test(c.innerText) && c.querySelector('iframe, [class*="document"]')) return 'documento';
    if ([...c.querySelectorAll('img')].some((x) => /feedshare|image-shrink|article-cover/.test(x.src))) return 'imagem';
    return 'texto';
  }

  function colher() {
    const v = window.__varredura;
    let novos = 0, novosNaJanela = 0;
    for (const b of document.querySelectorAll('button')) {
      const rotulo = b.getAttribute('aria-label') || '';
      if (!rotulo.startsWith(PREFIXO)) continue;
      const c = cardDoBotao(b);
      if (!c) continue;
      const autor = rotulo.slice(PREFIXO.length);
      const linhas = c.innerText.split('\n').map((s) => s.trim()).filter(Boolean);
      const urn = urnDoBotao(b);
      const chave = urn || autor + '|' + linhas.slice(2, 8).join(' ').slice(0, 120);
      if (v.posts.has(chave)) {
        // a mídia carrega depois do card: card lido como texto pode ganhar vídeo ou imagem depois
        const antes = v.posts.get(chave), agora = tipo(c);
        if (antes.tipo === 'texto' && agora !== 'texto') antes.tipo = agora;
        continue;
      }
      const ts = urn ? tsDoId(urn) : tsDoRotulo(linhas);
      const p = {
        urn, autor, ts, quando: ts ? new Date(ts).toISOString().slice(0, 16) + 'Z' : null,
        ts_aprox: !urn, tipo: tipo(c),
        promovido: /Promovida|Promoted/.test(c.innerText.slice(0, 400)),
        contexto: linhas[1] === autor ? '' : (linhas[1] || '').slice(0, 60),
        url: urn ? `https://www.linkedin.com/feed/update/${urn}/` : null,
        texto: c.innerText.replace(/\s+/g, ' ').replace(/^Publicação no feed /, '').slice(0, 700),
      };
      v.posts.set(chave, p);
      novos++;
      if (ts && ts >= v.desde) novosNaJanela++;
    }
    return { novos, novosNaJanela };
  }

  window.feedVarrerInicio = (desdeMs) => {
    window.__varredura = { desde: desdeMs, posts: new Map(), rodadas: 0, foraSeguidas: 0, paradas: 0, inicio: Date.now() };
    colher();
    return { desde: new Date(desdeMs).toISOString(), coletados: window.__varredura.posts.size };
  };

  // Para quando 3 rodadas seguidas trazem posts novos mas nenhum na janela (o feed já passou dela),
  // 3 rodadas sem nada novo (carga esgotada) ou no limite de posts.
  window.feedVarrer = async ({ segundos = 35, limite = 300, espera = 2500 } = {}) => {
    const v = window.__varredura;
    if (!v) return { erro: 'chame feedVarrerInicio(desdeMs) antes' };
    if (!/Feed \| LinkedIn/.test(document.title)) return { erro: 'fora do feed ou deslogado: ' + document.title };
    if (!innerHeight) return { erro: 'viewport 0: painel do navegador escondido; use resize_window e recarregue' };
    const fim = Date.now() + segundos * 1000;
    let motivo = null;
    v.paradas = 0; // cada chamada recomeça a contar: depois de destravar, a carga continua
    while (Date.now() + espera < fim) {
      const el = document.getElementById('workspace') || document.scrollingElement;
      el.scrollTop = el.scrollHeight;
      await new Promise((r) => setTimeout(r, espera));
      const r = colher();
      v.rodadas++;
      v.paradas = r.novos ? 0 : v.paradas + 1;
      if (r.novos) v.foraSeguidas = r.novosNaJanela ? 0 : v.foraSeguidas + 1;
      if (v.foraSeguidas >= 3) { motivo = 'passou da janela'; break; }
      if (v.paradas >= 3) { motivo = 'carga esgotada'; break; }
      if (v.posts.size >= limite) { motivo = 'limite de posts'; break; }
    }
    const lista = [...v.posts.values()];
    return {
      parar: !!motivo, motivo, rodadas: v.rodadas, coletados: lista.length,
      na_janela: lista.filter((p) => p.ts && p.ts >= v.desde).length,
      sem_urn: lista.filter((p) => !p.urn).length,
    };
  };

  // Só os posts da janela não promovidos (e os sem data, para o triador decidir); o resto entra só
  // na contagem. Texto cortado em 450: o integral vem depois do baixar_post.py.
  window.feedVarrerResultado = (excluir = []) => {
    const v = window.__varredura;
    const todos = [...v.posts.values()];
    const naJanela = todos.filter((p) => !p.ts || p.ts >= v.desde);
    const posts = naJanela.filter((p) => !p.promovido)
      .filter((p) => !excluir.includes(p.urn ? p.urn.split(':').pop() : p.autor))
      .map((p) => ({ ...p, texto: p.texto.slice(0, 450) }));
    return JSON.stringify({
      coletado_em: new Date(v.inicio).toISOString(), desde: new Date(v.desde).toISOString(),
      rodadas: v.rodadas, coletados: todos.length, fora_da_janela: todos.length - naJanela.length,
      promovidos: naJanela.length - posts.length, posts,
    });
  };

  return 'feedVarrerInicio, feedVarrer e feedVarrerResultado prontos';
}

// O CSP do LinkedIn barra eval e new Function: não dá para guardar o código na aba e reinstalar.
feedVarrerInstalar();

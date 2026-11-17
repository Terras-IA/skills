/* terras-licao-interativa — motor de cena isométrica passo a passo.
   Lê window.__CURSO__ (formato em references/formato.md) e desenha tudo em SVG.
   Sem dependências e sem build. */
(function () {
  'use strict';
  var CURSO = window.__CURSO__;
  var TW = 96, TH = 48;
  var NS = 'http://www.w3.org/2000/svg';

  // [topo, face esquerda, face direita, contorno]
  var TONS = {
    azul: ['#cfe0f7', '#a9c6ec', '#86a9d9', '#3d5f8f'],
    verde: ['#d6efc8', '#b3dd9f', '#90c47b', '#4a7a3a'],
    laranja: ['#fbd7b5', '#f4b483', '#e3925a', '#94532a'],
    roxo: ['#e2d8f5', '#c8b8ec', '#a993d9', '#5e4b8f'],
    rosa: ['#f5d3dc', '#eab0c0', '#d78ea3', '#8c4a5c'],
    amarelo: ['#f7ebb5', '#eed98a', '#dcc061', '#86712a'],
    cinza: ['#e7e3db', '#cbc7bd', '#aeaa9f', '#66625a'],
    vermelho: ['#f6c9c3', '#ec9f95', '#d9786c', '#8e3a30'],
    teal: ['#c9ece6', '#9fd8cf', '#78c0b5', '#2f6f66']
  };
  var CORES_MOD = ['#e3925a', '#90c47b', '#86a9d9', '#a993d9', '#d78ea3', '#dcc061', '#78c0b5', '#aeaa9f', '#d9786c'];
  var PESSOAS = ['#86a9d9', '#90c47b', '#e3925a', '#a993d9', '#d78ea3', '#dcc061', '#78c0b5'];

  var TXT = {
    pt: { curso: 'Curso', progresso: 'Progresso', replay: 'Recomeçar', pausa: 'Pausar', seguir: 'Seguir', nesta: 'Nesta lição',
      voltar: 'Voltar', passo: 'passo', aprende: 'Você vai aprender', proximo: 'Próximo', proxLicao: 'Próxima lição', fim: 'Fim do curso',
      licoes: 'lições', min: 'min', passos: 'passos', ideia: 'Ideia-chave', mudou: 'O que mudou', filtro: 'Buscar lição…',
      req: 'requisição', resp: 'resposta', falha: 'falhou', pesado: 'pesado', certo: 'Certo.', errado: 'Não é essa.', de: 'de',
      tipos: { contexto: 'contexto', problema: 'problema', solucao: 'solução', tecnica: 'técnica', troca: 'trade-off', resumo: 'resumo' } },
    en: { curso: 'Course', progresso: 'Progress', replay: 'Replay', pausa: 'Pause', seguir: 'Play', nesta: 'In this lesson',
      voltar: 'Back', passo: 'step', aprende: "You'll learn", proximo: 'Next', proxLicao: 'Next lesson', fim: 'End of course',
      licoes: 'lessons', min: 'min', passos: 'steps', ideia: 'Key idea', mudou: 'What changed', filtro: 'Search lessons…',
      req: 'request', resp: 'response', falha: 'failed', pesado: 'heavy', certo: 'Right.', errado: 'Not that one.', de: 'of',
      tipos: { contexto: 'setup', problema: 'problem', solucao: 'solution', tecnica: 'technique', troca: 'trade-off', resumo: 'recap' } }
  };
  var T = TXT[(CURSO.idioma || 'pt').slice(0, 2)] || TXT.pt;

  // ---------- utilidades ----------
  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function md(s) {
    return esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`(.+?)`/g, '<code>$1</code>');
  }
  function paras(s) { return String(s || '').split(/\n\s*\n/).map(function (p) { return '<p>' + md(p).replace(/\n/g, '<br>') + '</p>'; }).join(''); }
  function P(x, y, z) { return [(x - y) * TW / 2, (x + y) * TH / 2 - (z || 0)]; }
  function tom(n) { return TONS[n] || TONS.azul; }
  function guardar(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function ler(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function largura(txt, px) { return String(txt).length * (px || 10.5) * 0.62 + 16; }

  // ---------- dados ----------
  var LICOES = [];
  (CURSO.modulos || []).forEach(function (m, mi) {
    (m.licoes || []).forEach(function (l, li) { l._mod = mi; l._idx = li; LICOES.push(l); });
  });
  var CHAVE = 'licao:' + (CURSO.id || CURSO.titulo);
  var visto = ler(CHAVE, {});

  // Dobra os passos: cada passo herda o estado anterior e aplica seus remendos.
  function estados(l) {
    var nos = {};
    ((l.cena && l.cena.nos) || []).forEach(function (n) { nos[n.id] = Object.assign({}, n); });
    var lig = (l.cena && l.cena.ligacoes) || [];
    var met = {};
    (l.metricas || []).forEach(function (m) { met[m.id] = m.valor == null ? '—' : m.valor; });
    return (l.passos || []).map(function (p) {
      var novo = {};
      Object.keys(nos).forEach(function (k) { novo[k] = Object.assign({}, nos[k]); });
      Object.keys(p.nos || {}).forEach(function (id) {
        var patch = p.nos[id];
        if (patch === null) delete novo[id];
        else novo[id] = Object.assign({}, novo[id] || {}, patch, { id: id });
      });
      nos = novo;
      if (p.ligacoes) lig = p.ligacoes;
      met = Object.assign({}, met, p.metricas || {});
      return { nos: nos, lig: lig, met: met };
    });
  }

  // ---------- geometria dos nós ----------
  function dims(n) {
    var s = n.tamanho || 1;
    if (n.tipo === 'pessoas') s = n.tamanho || 1.6;
    return { s: s, a: TW / 2 * 0.9 * s, b: TH / 2 * 0.9 * s, h: n.tipo === 'pessoas' ? 8 : (n.altura || 40) * s };
  }
  function caixaEnvolvente(n) {
    var d = dims(n), p = P(n.x, n.y, n.z), X = p[0], Y = p[1];
    if (n.tipo === 'zona') {
      var w = (n.largura || 3) / 2, q = (n.fundo || 2) / 2;
      var c = [P(n.x - w, n.y - q), P(n.x + w, n.y - q), P(n.x + w, n.y + q), P(n.x - w, n.y + q)];
      var xs = c.map(function (k) { return k[0]; }), ys = c.map(function (k) { return k[1]; });
      return [Math.min.apply(0, xs), Math.min.apply(0, ys), Math.max.apply(0, xs), Math.max.apply(0, ys) + 16];
    }
    if (n.tipo === 'placa') { var pw = larguraPlaca(n); return [X - pw / 2, Y - 14, X + pw / 2, Y + alturaPlaca(n)]; }
    if (n.tipo === 'banco' && n.rotulo) { var rx = d.a * 0.78; return [X - d.a - 10, Y - d.h - d.b - 64, X + rx + largura(n.rotulo) + 10, Y + d.b + 40]; }
    if (n.tipo === 'fila') {
      var k = n.quantidade || 5, e = n.espaco || 0.6, dir = n.direcao === 'y' ? [0, e] : [e, 0];
      var f = P(n.x + dir[0] * (k - 1), n.y + dir[1] * (k - 1), n.z);
      return [Math.min(X, f[0]) - 30, Math.min(Y, f[1]) - 60, Math.max(X, f[0]) + 30, Math.max(Y, f[1]) + 40];
    }
    if (n.tipo === 'rotulo') { var lw = largura(n.rotulo); return [X - lw / 2, Y - 14, X + lw / 2, Y + 14]; }
    return [X - d.a - 10, Y - d.h - d.b - 64, X + d.a + 10, Y + d.b + 40];
  }

  function pill(x, y, txt, cls, px) {
    var w = largura(txt, px);
    return '<g class="pill ' + (cls || '') + '"><rect x="' + (x - w / 2) + '" y="' + (y - 10) + '" width="' + w + '" height="20" rx="10"/>' +
      '<text x="' + x + '" y="' + (y + 3.6) + '" text-anchor="middle">' + esc(txt) + '</text></g>';
  }
  function linhasRotulo(txt) {
    txt = String(txt || '');
    if (txt.length <= 11 || txt.indexOf(' ') < 0) return [txt];
    var meio = Math.floor(txt.length / 2), esq = txt.lastIndexOf(' ', meio), dir = txt.indexOf(' ', meio);
    var corte = esq < 0 ? dir : (dir < 0 ? esq : (meio - esq <= dir - meio ? esq : dir));
    return [txt.slice(0, corte), txt.slice(corte + 1)];
  }
  function rotuloSobre(X, Y, n) {
    var out = '';
    var linhas = linhasRotulo(n.rotulo);
    var temIc = !!n.icone;
    var y0 = Y - (linhas.length - 1) * 6 + (temIc ? 8 : 4);
    if (temIc) out += '<text class="ic-no" x="' + X + '" y="' + (y0 - 13) + '">' + esc(n.icone) + '</text>';
    linhas.forEach(function (ln, i) { out += '<text class="rot-no" x="' + X + '" y="' + (y0 + i * 12) + '">' + esc(ln) + '</text>'; });
    return out;
  }

  function desenhaCaixa(n, c) {
    var d = dims(n), p = P(n.x, n.y, n.z), X = p[0], Y = p[1], a = d.a, b = d.b, h = d.h;
    var top = [X, Y - h - b, X + a, Y - h, X, Y - h + b, X - a, Y - h].join(' ');
    var esq = [X - a, Y - h, X, Y - h + b, X, Y + b, X - a, Y].join(' ');
    var dir = [X + a, Y - h, X, Y - h + b, X, Y + b, X + a, Y].join(' ');
    var sombra = [X, Y - b + 6, X + a + 6, Y + 4, X, Y + b + 8, X - a + 2, Y + 4].join(' ');
    var s = '<polygon points="' + sombra + '" fill="var(--sombra)"/>' +
      '<g class="corpo" stroke="' + c[3] + '" stroke-width="1.5" stroke-linejoin="round">' +
      '<polygon points="' + esq + '" fill="' + c[1] + '"/><polygon points="' + dir + '" fill="' + c[2] + '"/>' +
      '<polygon points="' + top + '" fill="' + c[0] + '"/></g>';
    s += rotuloSobre(X, Y - h, n);
    return { svg: s, X: X, topo: Y - h - b, base: Y + b };
  }
  function desenhaBanco(n, c) {
    var d = dims(n), p = P(n.x, n.y, n.z), X = p[0], Y = p[1], rx = d.a * 0.78, ry = d.b * 0.78, h = d.h;
    var corpo = 'M' + (X - rx) + ',' + (Y - h) + ' L' + (X - rx) + ',' + Y + ' A' + rx + ',' + ry + ' 0 0 0 ' + (X + rx) + ',' + Y + ' L' + (X + rx) + ',' + (Y - h) + ' Z';
    var faixa = 'M' + (X - rx) + ',' + (Y - h * 0.45) + ' A' + rx + ',' + ry + ' 0 0 0 ' + (X + rx) + ',' + (Y - h * 0.45);
    var s = '<ellipse cx="' + (X + 4) + '" cy="' + (Y + 5) + '" rx="' + (rx + 4) + '" ry="' + (ry + 2) + '" fill="var(--sombra)"/>' +
      '<g class="corpo" stroke="' + c[3] + '" stroke-width="1.5"><path d="' + corpo + '" fill="' + c[1] + '"/>' +
      '<path d="' + faixa + '" fill="none" opacity=".6"/>' +
      '<ellipse cx="' + X + '" cy="' + (Y - h) + '" rx="' + rx + '" ry="' + ry + '" fill="' + c[0] + '"/></g>';
    if (n.icone) s += '<text class="ic-no" x="' + X + '" y="' + (Y - h + 5) + '">' + esc(n.icone) + '</text>';
    if (n.rotulo) s += pill(X + rx + largura(n.rotulo) / 2 + 4, Y - h * 0.5, n.rotulo);
    return { svg: s, X: X, topo: Y - h - ry, base: Y + ry };
  }
  function desenhaPessoas(n, c) {
    var d = dims(n), p = P(n.x, n.y, n.z), X = p[0], Y = p[1], a = d.a, b = d.b, h = 8;
    var top = [X, Y - h - b, X + a, Y - h, X, Y - h + b, X - a, Y - h].join(' ');
    var esq = [X - a, Y - h, X, Y - h + b, X, Y + b, X - a, Y].join(' ');
    var dir = [X + a, Y - h, X, Y - h + b, X, Y + b, X + a, Y].join(' ');
    var s = '<g class="corpo" stroke="#66625a" stroke-width="1.2" stroke-linejoin="round"><polygon points="' + esq + '" fill="#d9d4c8"/>' +
      '<polygon points="' + dir + '" fill="#c4bfb2"/><polygon points="' + top + '" fill="#f6f3ec"/></g>';
    var qtd = Math.max(1, Math.min(n.quantidade || 8, 36));
    var k = Math.ceil(Math.sqrt(qtd)), passo = (d.s * 0.8) / k, figs = [];
    for (var i = 0; i < qtd; i++) {
      var col = i % k, lin = Math.floor(i / k);
      var gx = n.x + (col - (k - 1) / 2) * passo, gy = n.y + (lin - (k - 1) / 2) * passo;
      figs.push([gx, gy, i]);
    }
    figs.sort(function (u, v) { return (u[0] + u[1]) - (v[0] + v[1]); });
    figs.forEach(function (f) {
      var q = P(f[0], f[1], (n.z || 0) + h), cor = n.tom ? c[2] : PESSOAS[f[2] % PESSOAS.length];
      s += '<rect x="' + (q[0] - 4) + '" y="' + (q[1] - 15) + '" width="8" height="13" rx="3.5" fill="' + cor + '" stroke="#4b473f" stroke-width=".9"/>' +
        '<circle cx="' + q[0] + '" cy="' + (q[1] - 19) + '" r="3.6" fill="#f2dcc0" stroke="#4b473f" stroke-width=".9"/>';
    });
    if (n.rotulo) s += pill(X, Y + b + 22, (n.icone ? n.icone + ' ' : '') + n.rotulo);
    return { svg: s, X: X, topo: Y - h - b - 26, base: Y + b + 30 };
  }
  function desenhaFila(n, c) {
    var k = Math.max(1, Math.min(n.quantidade || 5, 14)), e = n.espaco || 0.6, dir = n.direcao === 'y' ? [0, e] : [e, 0];
    var s = '', a = TW / 2 * 0.42, b = TH / 2 * 0.42, h = 9, X0, Y0, topo = Infinity;
    for (var i = 0; i < k; i++) {
      var p = P(n.x + dir[0] * i, n.y + dir[1] * i, n.z), X = p[0], Y = p[1];
      if (i === 0) { X0 = X; Y0 = Y; }
      var top = [X, Y - h - b, X + a, Y - h, X, Y - h + b, X - a, Y - h].join(' ');
      var esq = [X - a, Y - h, X, Y - h + b, X, Y + b, X - a, Y].join(' ');
      var dr = [X + a, Y - h, X, Y - h + b, X, Y + b, X + a, Y].join(' ');
      s += '<g class="corpo" stroke="' + c[3] + '" stroke-width="1.2" stroke-linejoin="round"><polygon points="' + esq + '" fill="' + c[1] + '"/>' +
        '<polygon points="' + dr + '" fill="' + c[2] + '"/><polygon points="' + top + '" fill="' + c[0] + '"/></g>';
      topo = Math.min(topo, Y - h - b);
    }
    if (n.rotulo) s += pill(X0, topo - 16, (n.icone ? n.icone + ' ' : '') + n.rotulo);
    return { svg: s, X: X0, topo: topo - 28, base: Y0 + b };
  }
  function desenhaZona(n, c) {
    var w = (n.largura || 3) / 2, q = (n.fundo || 2) / 2, z = n.z || 0;
    var pts = [P(n.x - w, n.y - q, z), P(n.x + w, n.y - q, z), P(n.x + w, n.y + q, z), P(n.x - w, n.y + q, z)];
    var s = '<polygon class="corpo" points="' + pts.map(function (k) { return k.join(','); }).join(' ') + '" fill="' + c[0] + '" fill-opacity=".45" stroke="' + c[3] +
      '" stroke-width="1.3" stroke-dasharray="6 4"/>';
    if (n.rotulo) {
      var a = pts[3], b2 = pts[2], ang = Math.atan2(b2[1] - a[1], b2[0] - a[0]) * 180 / Math.PI;
      s += '<text class="zona-rot" transform="translate(' + (a[0] + 10) + ',' + (a[1] + 4) + ') rotate(' + ang + ')" dy="10">' + esc(n.rotulo) + '</text>';
    }
    return { svg: s, X: P(n.x, n.y)[0], topo: P(n.x, n.y)[1], base: P(n.x, n.y)[1] };
  }
  // placa: cartão plano com título e até 6 linhas (tabela de alçada, checklist, regra)
  function linhasPlaca(n) { return (n.linhas || []).slice(0, 6); }
  function larguraPlaca(n) {
    var m = Math.max(String(n.rotulo || '').length, 8);
    linhasPlaca(n).forEach(function (l) { m = Math.max(m, String(l).length); });
    return Math.min(320, m * 6.4 + 28);
  }
  function alturaPlaca(n) { return 30 + linhasPlaca(n).length * 15; }
  function desenhaPlaca(n, c) {
    var p = P(n.x, n.y, n.z), X = p[0], Y = p[1], w = larguraPlaca(n), h = alturaPlaca(n), x0 = X - w / 2;
    var s = '<g class="corpo"><rect x="' + (x0 + 3) + '" y="' + (Y - 10 + 4) + '" width="' + w + '" height="' + h + '" rx="8" fill="var(--sombra)"/>' +
      '<rect x="' + x0 + '" y="' + (Y - 10) + '" width="' + w + '" height="' + h + '" rx="8" fill="var(--cartao)" stroke="' + c[3] + '" stroke-width="1.3"/>' +
      '<rect x="' + x0 + '" y="' + (Y - 10) + '" width="5" height="' + h + '" rx="2" fill="' + c[2] + '"/></g>';
    s += '<text class="placa-tit" x="' + (x0 + 14) + '" y="' + (Y + 6) + '">' + esc((n.icone ? n.icone + ' ' : '') + (n.rotulo || '')) + '</text>';
    linhasPlaca(n).forEach(function (l, i) { s += '<text class="placa-lin" x="' + (x0 + 14) + '" y="' + (Y + 24 + i * 15) + '">' + esc(l) + '</text>'; });
    return { svg: s, X: X, topo: Y - 10, base: Y - 10 + h };
  }
  function desenhaRotulo(n) {
    var p = P(n.x, n.y, n.z);
    return { svg: pill(p[0], p[1], (n.icone ? n.icone + ' ' : '') + n.rotulo, n.estilo), X: p[0], topo: p[1] - 12, base: p[1] + 12 };
  }

  function desenhaNo(n, cls) {
    var c = tom(n.tom);
    if (n.estado === 'caido') c = TONS.cinza;
    if (n.estado === 'quente') c = TONS.vermelho;
    var r;
    switch (n.tipo) {
      case 'banco': r = desenhaBanco(n, c); break;
      case 'pessoas': r = desenhaPessoas(n, c); break;
      case 'fila': r = desenhaFila(n, c); break;
      case 'zona': r = desenhaZona(n, c); break;
      case 'rotulo': r = desenhaRotulo(n); break;
      case 'placa': r = desenhaPlaca(n, c); break;
      default: r = desenhaCaixa(n, c);
    }
    var extra = '', y = r.topo - 14;
    if (n.estado === 'caido') {
      var dd = dims(n), pp = P(n.x, n.y, n.z);
      var cx = n.tipo === 'caixa' || !n.tipo ? pp[0] + dd.a / 2 : r.X, cy = n.tipo === 'caixa' || !n.tipo ? pp[1] - dd.h / 2 + dd.b / 2 : r.topo + 22;
      extra += '<path d="M' + (cx - 9) + ',' + (cy - 9) + ' L' + (cx + 9) + ',' + (cy + 9) + ' M' + (cx + 9) + ',' + (cy - 9) + ' L' + (cx - 9) + ',' + (cy + 9) +
        '" stroke="#d0533f" stroke-width="3.2" stroke-linecap="round"/>';
      extra += pill(r.X, y, '⨯ ' + (n.selo || (T === TXT.en ? 'DOWN' : 'FORA')), 'alerta'); y -= 24;
    } else if (n.selo) { extra += pill(r.X, y, n.selo, n.estado === 'quente' ? 'alerta' : (n.estilo || '')); y -= 24; }
    if (typeof n.carga === 'number') {
      var v = Math.max(0, Math.min(100, n.carga)), w = 70, bx = r.X - w / 2;
      var cor = v < 60 ? '#5aa36b' : v < 85 ? '#e0a33a' : '#d0533f';
      extra += '<g class="pill"><rect x="' + bx + '" y="' + (y - 10) + '" width="' + w + '" height="20" rx="10"/>' +
        '<rect x="' + (bx + 8) + '" y="' + (y - 3) + '" width="28" height="6" rx="3" fill="var(--grade)" stroke="none"/>' +
        '<rect x="' + (bx + 8) + '" y="' + (y - 3) + '" width="' + (28 * v / 100) + '" height="6" rx="3" fill="' + cor + '" stroke="none"/>' +
        '<text x="' + (bx + w - 9) + '" y="' + (y + 3.6) + '" text-anchor="end">' + Math.round(v) + '%</text></g>';
    }
    var est = n.estado === 'fantasma' ? ' fantasma' : n.estado === 'quente' ? ' quente' : '';
    return '<g class="no' + est + (cls ? ' ' + cls : '') + '" data-id="' + esc(n.id) + '">' + r.svg + extra + '</g>';
  }

  // ---------- ligações e pacotes ----------
  function ancora(n) { return [n.x, n.y]; }
  function caminho(lig, nos) {
    var A = nos[lig.de], B = nos[lig.para];
    if (!A || !B) return null;
    var a = ancora(A), b = ancora(B), pts;
    if (lig.rota === 'reta' || a[0] === b[0] || a[1] === b[1]) pts = [a, b];
    else if (lig.rota === 'y') pts = [a, [a[0], b[1]], b];
    else pts = [a, [b[0], a[1]], b];
    return pts.map(function (k) { return P(k[0], k[1], Math.min(A.z || 0, B.z || 0) + 2); });
  }
  function comprimento(pts) { var L = 0; for (var i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; }
  function pontoEm(pts, f) {
    var L = comprimento(pts) * f;
    for (var i = 1; i < pts.length; i++) {
      var s = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
      if (L <= s || i === pts.length - 1) { var t = s ? Math.min(1, L / s) : 0; return [pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * t, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * t]; }
      L -= s;
    }
    return pts[0];
  }

  var pacotes = [], rodando = true, ultimo = 0, relogio = 0;
  function montaPacotes(lig, nos, g) {
    pacotes = [];
    lig.forEach(function (l) {
      var pts = caminho(l, nos);
      if (!pts || l.fluxo === 0) return;
      var fl = l.fluxo == null ? 1 : l.fluxo;
      var qtd = Math.max(1, Math.min(14, Math.round(3 * fl)));
      var vel = 70 * (l.velocidade || 1) / Math.max(40, comprimento(pts));
      var sentidos = l.sentido === 'ambos' ? [1, -1] : l.sentido === 'volta' ? [-1] : [1];
      sentidos.forEach(function (sen) {
        var rev = sen < 0 ? pts.slice().reverse() : pts;
        for (var i = 0; i < qtd; i++) {
          var h = (i * 0.6180339887) % 1;
          var falha = sen > 0 && h < (l.falha || 0);
          var pesado = !falha && sen > 0 && ((i * 0.381966) % 1) < (l.pesados || 0);
          var el = document.createElementNS(NS, pesado ? 'rect' : 'circle');
          var cor = falha ? 'var(--falha)' : pesado ? 'var(--pesado)' : sen < 0 ? 'var(--resp)' : (l.cor ? tom(l.cor)[3] : 'var(--req)');
          if (pesado) { el.setAttribute('width', 10); el.setAttribute('height', 10); el.setAttribute('rx', 2); }
          else el.setAttribute('r', 4);
          el.setAttribute('fill', cor); el.setAttribute('stroke', '#fff'); el.setAttribute('stroke-width', 1.2);
          el.setAttribute('class', 'pac');
          g.appendChild(el);
          pacotes.push({ el: el, pts: rev, fase: i / qtd + (sen < 0 ? 0.5 / qtd : 0), vel: vel, falha: falha, pesado: pesado, falhaEm: l.falhaEm == null ? 0.6 : l.falhaEm });
        }
      });
    });
    posicionaPacotes();
  }
  function posicionaPacotes() {
    pacotes.forEach(function (p) {
      var f = (p.fase + relogio * p.vel) % 1;
      var op = 1;
      var corte = p.falhaEm >= 1 ? 1 : p.falhaEm;
      if (p.falha && corte < 1 && f > corte - 0.05) { op = Math.max(0, 1 - (f - corte + 0.05) / 0.15); }
      if (p.falha && corte < 1 && capturando && f > corte - 0.05) op = 0.9;
      if (f < 0.04) op = Math.min(op, f / 0.04);
      if (f > 0.96) op = Math.min(op, (1 - f) / 0.04);
      var q = pontoEm(p.pts, p.falha && corte < 1 ? Math.min(f, corte + 0.1) : f);
      if (p.pesado) { p.el.setAttribute('x', q[0] - 5); p.el.setAttribute('y', q[1] - 5); }
      else { p.el.setAttribute('cx', q[0]); p.el.setAttribute('cy', q[1]); }
      p.el.setAttribute('opacity', op);
    });
  }
  var capturando = false;
  var reduz = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function laco(t) {
    if (ultimo && rodando && !reduz) relogio += Math.min(0.05, (t - ultimo) / 1000);
    ultimo = t;
    if (rodando && !reduz) posicionaPacotes();
    requestAnimationFrame(laco);
  }

  // ---------- render ----------
  var atual = { licao: null, passo: 0, est: null, camera: null };

  function camera(l, est) {
    var x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, gx0 = Infinity, gy0 = Infinity, gx1 = -Infinity, gy1 = -Infinity;
    est.forEach(function (e) {
      Object.keys(e.nos).forEach(function (k) {
        var n = e.nos[k], bb = caixaEnvolvente(n);
        x0 = Math.min(x0, bb[0]); y0 = Math.min(y0, bb[1]); x1 = Math.max(x1, bb[2]); y1 = Math.max(y1, bb[3]);
        gx0 = Math.min(gx0, n.x); gy0 = Math.min(gy0, n.y); gx1 = Math.max(gx1, n.x); gy1 = Math.max(gy1, n.y);
      });
    });
    if (!isFinite(x0)) { x0 = -200; y0 = -150; x1 = 200; y1 = 150; gx0 = gy0 = 0; gx1 = gy1 = 0; }
    var pad = 24, w = x1 - x0 + pad * 2, h = y1 - y0 + pad * 2;
    if (w / h > 2.2) { var nh = w / 2.2; y0 -= (nh - h) / 2; h = nh; }
    if (w / h < 1.25) { var nw = h * 1.25; x0 -= (nw - w) / 2; w = nw; }
    return { vb: [x0 - pad, y0 - pad, w, h], grade: [Math.floor(gx0) - 4, Math.floor(gy0) - 4, Math.ceil(gx1) + 4, Math.ceil(gy1) + 4] };
  }

  function desenhaGrade(cam) {
    var g = cam.grade, s = '<g class="g-grade">';
    for (var x = g[0]; x <= g[2]; x++) { var a = P(x - 0.5, g[1] - 0.5), b = P(x - 0.5, g[3] + 0.5); s += '<line x1="' + a[0] + '" y1="' + a[1] + '" x2="' + b[0] + '" y2="' + b[1] + '"/>'; }
    for (var y = g[1]; y <= g[3]; y++) { var c = P(g[0] - 0.5, y - 0.5), d = P(g[2] + 0.5, y - 0.5); s += '<line x1="' + c[0] + '" y1="' + c[1] + '" x2="' + d[0] + '" y2="' + d[1] + '"/>'; }
    return s + '</g>';
  }

  function visiveis(nos) { return Object.keys(nos).map(function (k) { return nos[k]; }).filter(function (n) { return !n.oculto; }); }

  function renderCena(i, anterior) {
    var l = atual.licao, e = atual.est[i], svg = $('svg');
    var cam = atual.camera;
    svg.setAttribute('viewBox', cam.vb.join(' '));
    var nos = visiveis(e.nos);
    var antes = anterior ? anterior.nos : null;
    var zonas = nos.filter(function (n) { return n.tipo === 'zona'; });
    var resto = nos.filter(function (n) { return n.tipo !== 'zona'; }).sort(function (a, b) { var pa = a.tipo === 'placa' ? 1e4 : 0, pb = b.tipo === 'placa' ? 1e4 : 0; return (pa - pb) || (a.x + a.y) - (b.x + b.y) || (a.z || 0) - (b.z || 0); });
    var mapa = {}; nos.forEach(function (n) { mapa[n.id] = n; });
    var s = desenhaGrade(cam);
    s += '<g>' + zonas.map(function (n) { return desenhaNo(n, classeMuda(n, antes)); }).join('') + '</g>';
    s += '<g>';
    e.lig.forEach(function (lg) {
      var pts = caminho(lg, mapa); if (!pts) return;
      s += '<polyline class="lig' + (lg.tracejada ? ' tracejada' : '') + '" points="' + pts.map(function (k) { return k.join(','); }).join(' ') + '"/>';
    });
    s += '</g><g id="g-pac"></g><g>';
    resto.forEach(function (n) { s += desenhaNo(n, classeMuda(n, antes)); });
    s += '</g><g>';
    e.lig.forEach(function (lg) {
      if (!lg.rotulo) return;
      var pts = caminho(lg, mapa); if (!pts) return;
      var m = pontoEm(pts, lg.posRotulo == null ? 0.5 : lg.posRotulo);
      s += pill(m[0], m[1], lg.rotulo, lg.estilo);
    });
    s += '</g>';
    svg.innerHTML = s;
    montaPacotes(e.lig, mapa, $('g-pac'));
  }
  function classeMuda(n, antes) {
    if (!antes) return 'entra';
    var v = antes[n.id];
    if (!v || v.oculto) return 'entra';
    return JSON.stringify(v) !== JSON.stringify(n) ? 'muda' : '';
  }

  function renderMetricas(i, anterior) {
    var l = atual.licao, e = atual.est[i];
    $('metricas').innerHTML = (l.metricas || []).map(function (m) {
      var v = e.met[m.id], valor = v, cls = '';
      if (v && typeof v === 'object') { valor = v.valor; cls = v.tom || ''; }
      var antes = anterior ? anterior.met[m.id] : undefined;
      var mudou = anterior && JSON.stringify(antes) !== JSON.stringify(v);
      return '<div class="metrica ' + cls + (mudou ? ' mudou' : '') + '"><small>' + esc(m.rotulo) + '</small><b>' + esc(valor) + '</b></div>';
    }).join('');
  }

  function renderPainel(i) {
    var l = atual.licao, p = l.passos[i], n = l.passos.length;
    $('passo-num').textContent = T.passo + ' ' + (i + 1) + ' / ' + n;
    var tp = p.tipo || 'contexto';
    $('passo-tipo').className = 'selo ' + tp;
    $('passo-tipo').textContent = (T.tipos[tp] || tp).toUpperCase();
    $('passo-titulo').textContent = p.titulo || '';
    $('passo-texto').innerHTML = paras(p.texto);
    $('passo-ideia').innerHTML = p.ideia ? '<div class="caixa"><small>' + esc(T.ideia) + '</small>' + md(p.ideia) + '</div>' : '';
    $('passo-mudou').innerHTML = (p.mudou && p.mudou.length) ? '<div class="mudou"><small>' + esc(T.mudou) + '</small><ul>' + p.mudou.map(function (m) {
      var c = m.charAt(0) === '+' ? 'mais' : m.charAt(0) === '-' ? 'menos' : '';
      var t = (c || m.charAt(0) === '·') ? m.slice(1).trim() : m;
      return '<li class="' + c + '"><span class="s">' + (c === 'mais' ? '+' : c === 'menos' ? '−' : '·') + '</span><span>' + md(t) + '</span></li>';
    }).join('') + '</ul></div>' : '';
    var q = p.quiz;
    if (q) {
      $('passo-quiz').innerHTML = '<div class="quiz"><p>' + md(q.pergunta) + '</p>' + q.opcoes.map(function (o, k) {
        return '<button data-k="' + k + '">' + md(o) + '</button>';
      }).join('') + '<div class="porque" hidden></div></div>';
      Array.prototype.forEach.call($('passo-quiz').querySelectorAll('button'), function (b) {
        b.onclick = function () {
          var k = +b.dataset.k, ok = k === q.certa;
          b.classList.add(ok ? 'certa' : 'errada');
          if (!ok) $('passo-quiz').querySelectorAll('button')[q.certa].classList.add('certa');
          var pq = $('passo-quiz').querySelector('.porque'); pq.hidden = false;
          pq.innerHTML = '<b>' + (ok ? T.certo : T.errado) + '</b> ' + md(q.porque || '');
        };
      });
    } else $('passo-quiz').innerHTML = '';
    $('bt-voltar').disabled = i === 0;
    var prox = $('bt-proximo');
    if (i < n - 1) prox.innerHTML = esc(T.proximo) + ': ' + esc(l.passos[i + 1].rotulo || l.passos[i + 1].titulo) + ' →';
    else {
      var nx = LICOES[LICOES.indexOf(l) + 1];
      prox.innerHTML = nx ? esc(T.proxLicao) + ': ' + esc(nx.titulo) + ' →' : esc(T.fim) + ' ✓';
      prox.disabled = !nx;
    }
    if (i < n - 1) prox.disabled = false;
    $('objetivos').innerHTML = (l.objetivos || []).map(function (o) {
      var ok = (i + 1) >= (o.passo || n);
      return '<li class="' + (ok ? 'ok' : '') + '"><span class="cx">' + (ok ? '✓' : '') + '</span><span>' + md(o.texto) + '</span></li>';
    }).join('');
    $('objetivos-box').hidden = !(l.objetivos && l.objetivos.length);
  }

  function renderLinha(i) {
    var l = atual.licao;
    $('linha').innerHTML = l.passos.map(function (p, k) {
      return '<button class="' + (k < i ? 'feito' : k === i ? 'atual' : '') + '" data-k="' + k + '" aria-label="' + esc(p.titulo) + '"' + (k === i ? ' aria-current="step"' : '') +
        '><span class="n">' + (k + 1) + '</span>' + esc(p.rotulo || '') + '</button>';
    }).join('');
    Array.prototype.forEach.call($('linha').querySelectorAll('button'), function (b) { b.onclick = function () { ir(atual.licao.id, +b.dataset.k); }; });
    $('passo-de').textContent = T.passo + ' ' + (i + 1) + ' ' + T.de + ' ' + l.passos.length;
    var at = $('linha').querySelector('.atual'), ln = $('linha');
    if (at) ln.scrollLeft = at.offsetLeft - ln.clientWidth / 2 + at.offsetWidth / 2;
  }

  function renderLegenda(l) {
    var itens = l.legenda || [{ cor: 'var(--req)', texto: T.req }, { cor: 'var(--resp)', texto: T.resp }, { cor: 'var(--falha)', texto: T.falha }];
    $('legenda').innerHTML = itens.map(function (it) {
      var cor = TONS[it.cor] ? TONS[it.cor][2] : it.cor;
      return '<span><i class="' + (it.forma === 'quadrado' ? 'q' : '') + '" style="background:' + esc(cor) + '"></i>' + esc(it.texto) + '</span>';
    }).join('');
  }

  function renderCabecalho(l) {
    var m = CURSO.modulos[l._mod];
    $('trilha').textContent = (m.titulo || '') + '  ·  ' + (l._idx + 1) + '/' + m.licoes.length;
    $('licao-titulo').textContent = l.titulo;
    $('licao-resumo').textContent = l.resumo || '';
    var chips = [];
    if (l.minutos) chips.push('⏱ ' + l.minutos + ' ' + T.min);
    if (l.nivel) chips.push('▲ ' + l.nivel);
    chips.push('☰ ' + l.passos.length + ' ' + T.passos);
    $('chips').innerHTML = chips.map(function (c) { return '<span class="chip">' + esc(c) + '</span>'; }).join('');
    document.title = l.titulo + ' · ' + CURSO.titulo;
  }

  function renderArvore() {
    var f = ($('filtro').value || '').toLowerCase();
    var feitas = 0;
    $('arvore').innerHTML = CURSO.modulos.map(function (m, mi) {
      var aberto = atual.licao && atual.licao._mod === mi || !!f;
      var itens = m.licoes.filter(function (l) { return !f || (l.titulo + ' ' + (l.resumo || '')).toLowerCase().indexOf(f) >= 0; });
      if (f && !itens.length) return '';
      var nFeitas = m.licoes.filter(function (l) { return visto[l.id] >= l.passos.length - 1; }).length;
      feitas += nFeitas;
      return '<div class="modulo' + (aberto ? '' : ' fechado') + '"><button aria-expanded="' + aberto + '" data-m="' + mi + '"><span class="cor" style="background:' + (m.cor && TONS[m.cor] ? TONS[m.cor][2] : CORES_MOD[mi % CORES_MOD.length]) + '"></span>' +
        String(mi + 1).padStart(2, '0') + '. ' + esc(m.titulo) + '<span class="cont">' + nFeitas + '/' + m.licoes.length + '</span></button><ul>' +
        itens.map(function (l) {
          var ok = visto[l.id] >= l.passos.length - 1;
          return '<li><a href="#' + l.id + '-p1" class="' + (atual.licao === l ? 'atual' : '') + '">' + (ok ? '<span class="ok">✓</span>' : '') + esc(l.titulo) + '</a></li>';
        }).join('') + '</ul></div>';
    }).join('');
    Array.prototype.forEach.call($('arvore').querySelectorAll('.modulo>button'), function (b) {
      b.onclick = function () { b.parentNode.classList.toggle('fechado'); b.setAttribute('aria-expanded', !b.parentNode.classList.contains('fechado')); };
    });
    Array.prototype.forEach.call($('arvore').querySelectorAll('a'), function (a) { a.onclick = function () { $('curso').classList.remove('aberto'); }; });
    var total = 0, tf = 0;
    LICOES.forEach(function (l) { total++; if (visto[l.id] >= l.passos.length - 1) tf++; });
    $('progresso').textContent = tf + ' / ' + total;
  }

  // Âncora #<lição>-p<passo>: só letras, dígitos e hífen, para funcionar também dentro de Artifact.
  function ir(id, k) { location.hash = '#' + id + '-p' + (k + 1); }

  function aplicarHash() {
    var m = location.hash.match(/^#\/?(.+?)(?:-p|\/)(\d+)$/);
    var l = m ? LICOES.filter(function (x) { return x.id === decodeURIComponent(m[1]); })[0] : null;
    if (!l) l = LICOES[0];
    var k = m && l.id === decodeURIComponent(m[1]) ? Math.max(0, Math.min(l.passos.length - 1, +m[2] - 1)) : 0;
    var trocou = atual.licao !== l;
    var anterior = null;
    if (trocou) {
      atual.licao = l; atual.est = estados(l); atual.camera = camera(l, atual.est);
      renderCabecalho(l); renderLegenda(l);
    } else anterior = atual.est[atual.passo];
    if (!trocou && Math.abs(k - atual.passo) !== 1) anterior = k > 0 ? atual.est[k - 1] : null;
    atual.passo = k;
    if ((visto[l.id] || -1) < k) { visto[l.id] = k; guardar(CHAVE, visto); }
    renderCena(k, anterior); renderMetricas(k, anterior); renderPainel(k); renderLinha(k);
    renderArvore();
  }

  // ---------- interface ----------
  function init() {
    if (/captura/.test(location.search)) { document.documentElement.classList.add('captura'); reduz = true; capturando = true; }
    if (!LICOES.length) { document.body.innerHTML = '<p style="padding:20px">Curso sem lições.</p>'; return; }
    $('curso-titulo').textContent = CURSO.titulo || '';
    $('total-licoes').textContent = LICOES.length + ' ' + T.licoes;
    Array.prototype.forEach.call(document.querySelectorAll('[data-t]'), function (el) { el.textContent = T[el.dataset.t] || ''; });
    $('filtro').placeholder = T.filtro;
    $('filtro').oninput = renderArvore;
    var tema = ler('licao:tema', null);
    if (tema) document.documentElement.dataset.theme = tema;
    $('bt-tema').onclick = function () {
      var escuro = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.dataset.theme = escuro ? 'light' : 'dark';
      guardar('licao:tema', document.documentElement.dataset.theme);
    };
    $('bt-menu').onclick = function () { var c = $('curso').classList.toggle('aberto'); $('bt-menu').setAttribute('aria-expanded', c); };
    $('bt-voltar').onclick = function () { if (atual.passo > 0) ir(atual.licao.id, atual.passo - 1); };
    $('bt-proximo').onclick = proximo;
    $('bt-replay').onclick = function () { ir(atual.licao.id, 0); };
    $('bt-pausa').onclick = pausa;
    document.addEventListener('keydown', function (ev) {
      if (/INPUT|TEXTAREA/.test(ev.target.tagName)) return;
      if (ev.key === 'ArrowRight') { ev.preventDefault(); proximo(); }
      else if (ev.key === 'ArrowLeft') { ev.preventDefault(); if (atual.passo > 0) ir(atual.licao.id, atual.passo - 1); }
      else if (ev.key === ' ' && ev.target.tagName !== 'BUTTON') { ev.preventDefault(); pausa(); }
      else if (ev.key === 'r' || ev.key === 'R') ir(atual.licao.id, 0);
    });
    window.addEventListener('hashchange', aplicarHash);
    aplicarHash();
    requestAnimationFrame(laco);
  }
  function proximo() {
    var l = atual.licao;
    if (atual.passo < l.passos.length - 1) ir(l.id, atual.passo + 1);
    else { var nx = LICOES[LICOES.indexOf(l) + 1]; if (nx) ir(nx.id, 0); }
  }
  function pausa() {
    rodando = !rodando;
    $('bt-pausa').innerHTML = rodando ? '<span aria-hidden="true">❚❚</span> ' + esc(T.pausa) : '<span aria-hidden="true">▶</span> ' + esc(T.seguir);
  }
  init();
})();

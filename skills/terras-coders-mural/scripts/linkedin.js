// terras-coders-mural: helper para comentar num post do LinkedIn já aberto na aba.
// A navegação zera o window, então injete de novo a cada post:
//   1) navigate para o link do post
//   2) javascript_exec: <este arquivo> + `await window.__li.prep(SNIP)`
//   3) computer type: o texto do comentário (digitação real; setar innerText não habilita o botão)
//   4) javascript_exec: <este arquivo> + `await window.__li.submit(SNIP)`
// SNIP = trecho de ~20-30 caracteres do FIM do comentário, usado para achar duplicata e confirmar.
// Antes de escrever o comentário (passo 3), leia a conversa: `await window.__li.comments()` devolve
// o texto dos comentários já publicados (abre "Carregar mais" e respostas). O LinkedIn esconde parte
// deles em "Mais relevantes": se `oculto` vier true, troque para "Mais recentes" com clique real
// (find "Mais relevantes" → clicar → find "Mais recentes" → clicar) e chame de novo. Respostas
// recolhidas ("Ver respostas anteriores") também só abrem com clique real: se `recolhidas` > 0,
// clique em cada uma pelo find e chame de novo.
// Funciona com a interface em português ou inglês.
(() => {
  const SUBMIT = ['Comentar', 'Comment', 'Publicar', 'Post'];
  const ME = ['Você', 'You'];
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const editor = () => document.querySelector('main [contenteditable=true][role=textbox]');
  const mainText = () => (document.querySelector('main') || document.body).innerText;
  const actionBtn = () =>
    [...document.querySelectorAll('main button')].find((b) =>
      /^(Comentar|Comment)$/.test((b.getAttribute('aria-label') || '').trim()));

  async function prep(snip) {
    if (!/linkedin\.com$/.test(location.hostname)) throw new Error('aba errada: ' + location.hostname);
    for (let i = 0; i < 15 && !actionBtn() && !editor(); i++) await sleep(400);
    if (/Somente suas conexões podem comentar|Only connections can comment/.test(mainText())) throw new Error('só conexões');
    if (mainText().includes(snip)) throw new Error('já comentado');
    // Comentário anterior do usuário, com qualquer texto: o LinkedIn marca o autor com "• Você" / "• You".
    if (/•\s*(Você|You)\s*\n/.test(mainText())) throw new Error('já existe comentário seu neste post');
    if (!editor()) {
      const b = actionBtn();
      if (b) b.click();
      for (let i = 0; i < 10 && !editor(); i++) await sleep(400);
    }
    const e = editor();
    if (!e) throw new Error('editor de comentário não encontrado (post removido ou comentários fechados?)');
    e.scrollIntoView({ block: 'center' });
    e.focus();
    return 'pronto para digitar';
  }

  async function submit(snip) {
    let btn = null;
    for (let i = 0; i < 12 && !btn; i++) {
      btn = [...document.querySelectorAll('main button')].find(
        (b) => SUBMIT.includes(b.innerText.trim()) && !b.disabled);
      if (!btn) await sleep(400);
    }
    if (!btn) throw new Error('botão de enviar não habilitou');
    btn.click();
    for (let k = 0; k < 12; k++) {
      await sleep(500);
      const t = mainText();
      const i = t.indexOf(snip);
      const stillInEditor = ((editor() && editor().innerText) || '').includes(snip);
      if (i >= 0 && !stillInEditor && ME.some((w) => t.slice(Math.max(0, i - 500), i).includes(w))) {
        return 'publicado';
      }
    }
    throw new Error('não confirmado: confira o post manualmente antes de repetir');
  }

  // Texto da conversa do post, para não repetir a pergunta ou o ponto de outra pessoa.
  async function comments() {
    if (!/linkedin\.com$/.test(location.hostname)) throw new Error('aba errada: ' + location.hostname);
    for (let i = 0; i < 15 && !actionBtn() && !editor(); i++) await sleep(400);
    for (let k = 0; k < 8; k++) {
      const b = [...document.querySelectorAll('main button')].find((x) =>
        /^(Carregar mais|Load more|Ver respostas anteriores|See previous replies|Ver mais respostas|See more replies)/i.test(x.innerText.trim()));
      if (!b) break;
      b.click();
      await sleep(1500);
    }
    const t = mainText();
    // Com poucos comentários o LinkedIn não mostra o seletor de ordem; aí a conversa começa depois
    // dos contadores de reação, que terminam em caracteres de largura zero.
    let i = t.search(/\n(Mais relevantes|Mais recentes|Most relevant|Most recent)\n/);
    if (i < 0) i = t.lastIndexOf('\u200b');
    if (i < 0) return { ordem: null, oculto: false, recolhidas: 0, texto: '' };
    const fim = t.search(/\n(Sobre|About)\n\n(Acessibilidade|Accessibility)/);
    const ordem = /^\n(Mais|Most)/.test(t.slice(i, i + 6)) ? t.slice(i + 1).split('\n')[0] : null;
    return {
      ordem,
      oculto: /Alguns comentários podem não ser exibidos|Some comments may not be shown/.test(t),
      recolhidas: (t.match(/\n(Ver respostas anteriores|See previous replies)\n/g) || []).length,
      texto: t.slice(i, fim > i ? fim : undefined).replace(/\n(Exibir tradução|See translation)\n/g, '\n').slice(0, 8000),
    };
  }

  window.__li = { prep, submit, comments };
})();

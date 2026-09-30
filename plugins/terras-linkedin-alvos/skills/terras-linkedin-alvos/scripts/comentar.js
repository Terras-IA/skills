// terras-linkedin-alvos: helper para comentar num post do LinkedIn já aberto na aba.
// A navegação zera o window, então injete de novo a cada post:
//   1) navigate para o link do post
//   2) javascript_exec: <este arquivo> + `await window.__li.prep(SNIP)`
//   3) computer type: o texto do comentário (digitação real; setar innerText não habilita o botão)
//   4) javascript_exec: <este arquivo> + `await window.__li.submit(SNIP)`
// SNIP = trecho de ~20-30 caracteres do FIM do comentário, usado para achar duplicata e confirmar.
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

  window.__li = { prep, submit };
})();

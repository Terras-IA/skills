// terras-linkedin-conexoes: convite com nota a partir do perfil já aberto na aba.
// A navegação zera o window, então injete de novo a cada perfil:
//   1) navigate para linkedin.com/in/<slug>/
//   2) javascript_exec: <este arquivo> + `await window.__conv.abrir(NOME)`
//   3) computer type: a nota (digitação real; setar value não habilita o Enviar)
//   4) javascript_exec: <este arquivo> + `window.__conv.conferir(INICIO, FIM)`
//   5) javascript_exec: <este arquivo> + `await window.__conv.enviar()`
//   6) recarregar o perfil, injetar e rodar `window.__conv.status(NOME)` até "Pendente"
// NOME = nome como aparece no card (basta o primeiro nome se for único no card).
// Funciona com a interface em português ou inglês.
(() => {
  const CONECTAR = /^(Conectar|Connect)$/;
  const MAIS = /^(Mais|More)$/;
  const NOTA = /^(Adicionar nota|Add a note)$/;
  const ENVIAR = /^(Enviar|Send)$/;
  const PENDENTE = /^(Pendente|Pending)$/;
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const txt = (e) => (e.innerText || '').trim();

  // O card do perfil é o primeiro section do main. Tudo fora dele (barra lateral,
  // "Pessoas que você talvez conheça") tem botões Conectar de OUTRAS pessoas.
  const card = () => {
    const c = document.querySelector('main')?.querySelector('section');
    if (!c) throw new Error('card do perfil não encontrado');
    return c;
  };

  // O diálogo do convite é renderizado dentro de um shadow root.
  const raizes = () => [document, ...[...document.querySelectorAll('*')].filter((e) => e.shadowRoot).map((e) => e.shadowRoot)];
  const noDialogo = (sel, re) => {
    for (const r of raizes()) {
      const el = [...r.querySelectorAll(sel)].find((e) => !re || re.test(txt(e) || e.getAttribute('aria-label') || ''));
      if (el) return el;
    }
    return null;
  };

  function botaoDireto(nome) {
    return [...card().querySelectorAll('button, a')].find((x) =>
      CONECTAR.test(txt(x)) && (x.getAttribute('aria-label') || '').includes(nome));
  }

  async function abrir(nome) {
    if (!nome) throw new Error('passe o nome da pessoa');
    if (!document.querySelector('main')?.innerText.includes(nome)) throw new Error(`"${nome}" não aparece na página: perfil errado?`);
    let el = botaoDireto(nome), via = 'direto';
    if (!el) {
      const mais = [...card().querySelectorAll('button')].find((b) => MAIS.test(txt(b)));
      if (!mais) throw new Error('sem botão Conectar no card (e sem menu Mais)');
      mais.click();
      for (let i = 0; i < 10 && !el; i++) {
        await sleep(300);
        // O menu "Mais" abre como [role=menuitem]; o aria-label do item traz o nome da pessoa.
        // Item sem aria-label é aceito (o menu acabou de abrir a partir do card); com aria-label,
        // ele precisa trazer o nome da pessoa.
        el = [...document.querySelectorAll('[role=menuitem]')].find((x) => {
          const al = x.getAttribute('aria-label');
          return CONECTAR.test(txt(x).split('\n')[0]) && (!al || al.includes(nome));
        });
      }
      if (!el) throw new Error('sem botão Conectar no card (nem no menu Mais) com esse nome');
      via = 'menu Mais';
    }
    el.click();
    let nota;
    for (let i = 0; i < 15 && !nota; i++) { await sleep(400); nota = noDialogo('button', NOTA); }
    if (!nota) throw new Error('diálogo sem "Adicionar nota" (pedido de e-mail ou layout novo): pare neste perfil');
    nota.click();
    let campo;
    for (let i = 0; i < 10 && !campo; i++) { await sleep(300); campo = noDialogo('textarea'); }
    if (!campo) throw new Error('campo da nota não abriu');
    campo.focus();
    return `diálogo aberto (${via}); digite a nota agora`;
  }

  function conferir(inicio, fim) {
    const v = noDialogo('textarea')?.value || '';
    if (!v.startsWith(inicio)) throw new Error(`nota não começa com "${inicio}": ${v.slice(0, 40)}`);
    if (!v.trimEnd().endsWith(fim)) throw new Error(`nota não termina com "${fim}"`);
    if (v.length > 300) throw new Error(`nota com ${v.length} caracteres (máx. 300)`);
    if (v.includes('—')) throw new Error('nota com travessão');
    return `ok, ${v.length} caracteres`;
  }

  async function enviar() {
    const b = noDialogo('button', ENVIAR);
    if (!b) throw new Error('botão Enviar não encontrado');
    if (b.disabled) throw new Error('Enviar desabilitado: a nota foi digitada de verdade?');
    b.click();
    await sleep(2000);
    return 'enviado; recarregue e rode status()';
  }

  function status(nome) {
    const c = card();
    if (!c.innerText.includes(nome)) return 'card não é dessa pessoa';
    if ([...c.querySelectorAll('button, a')].some((x) => PENDENTE.test(txt(x)))) return 'Pendente';
    if (botaoDireto(nome)) return 'Conectar (convite não foi)';
    return 'indefinido: confira o menu Mais';
  }

  window.__conv = { abrir, conferir, enviar, status };
})();

# Terras skills

Marketplace de plugins do Claude Code. Cada skill é um plugin: instale só as que quiser.

```bash
/plugin marketplace add Terras-IA/skills
```

Para atualizar: `/plugin marketplace update terras`.

## terras-coders-mural

Faz a rodada de engajamento do **Mural de Posts**:

1. lista os posts novos (ou mais antigos, como quando você rola a tela);
2. lê cada post linkado no LinkedIn;
3. escreve um comentário curto e específico, em inglês para o LinkedIn e em português para o mural;
4. **mostra tudo numa tabela e espera o seu "aprovado"**;
5. curte e comenta no mural, e comenta no LinkedIn, conferindo cada publicação.

Nada é publicado sem a sua aprovação no chat.

### Requisitos

- Claude Code com um navegador que o agente controla: o navegador integrado do app desktop ou a
  extensão Claude in Chrome.
- Estar logado na COD3RS e no LinkedIn nesse navegador.

### Instalação

```bash
/plugin install terras-coders-mural@terras
```

Depois, é só pedir: "curte e comenta os posts de hoje do mural da COD3RS".

## terras-linkedin-alvos

Para networking com poucas pessoas-chave (executivos, gestores e recrutadores das empresas onde
você quer trabalhar):

1. você passa a lista de perfis uma vez;
2. o plugin acha os posts recentes de cada um (pela data exata do post);
3. prepara comentários de 250 a 450 caracteres que acrescentam algo (experiência, dado ou pergunta);
4. **mostra tudo e espera o seu "aprovado"**;
5. curte, comenta e registra o que foi feito para nunca comentar duas vezes no mesmo post;
6. depois de 2-3 comentários num mesmo alvo, sugere o convite de conexão com nota.

Roda na hora ("vê se meus alvos postaram") ou agendado. Na rodada agendada, as curtidas podem ser
automáticas se você ativar; os comentários sempre esperam a sua aprovação.

```bash
/plugin install terras-linkedin-alvos@terras
```

### Aviso

O LinkedIn proíbe automação nos termos de uso. O plugin trabalha devagar, em volume baixo e com
aprovação humana, o que reduz o risco, mas não o elimina. Use por sua conta.

A API do mural é interna à COD3RS e pode mudar sem aviso.

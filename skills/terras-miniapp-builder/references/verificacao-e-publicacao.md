# Verificar e publicar

## Verificar não é "buildou"

Build limpo prova que compila, não que funciona. A verificação de verdade é **abrir o
app e olhar** — e é onde quase toda regressão aparece.

### O que olhar

- **Fluxo central do início ao fim**, com dado real, não só a primeira tela.
- **Estado vazio** (app recém-instalado, sem nenhum registro) — é o que a maioria vê
  primeiro, e o que costuma quebrar.
- **Os dois temas.** Um tema secundário mal testado é o mesmo que não existir.
- **Recarregar a página** no meio do fluxo: o estado persiste? A rota volta certa?
- **Dado de versão anterior.** Simule um registro incompleto (campo faltando) e confirme
  que o app não cai — leitura defensiva de banco local é obrigatória, porque você não
  controla o que já está gravado no aparelho das pessoas.
- **Acessibilidade básica:** foco visível, alvos de toque, rótulos de ícone.
- **Movimento:** nada de piscar na abertura; a preferência de tema resolvida antes do
  primeiro paint.

Use o navegador embutido para isso e guarde as capturas — elas servem de evidência na
entrega e de antes/depois quando alguém disser "não vi diferença".

## Publicar: preview primeiro, produção depois

```bash
vercel deploy            # PREVIEW — não toca no domínio
vercel deploy --prod     # produção — só depois de aval explícito
```

Sequência correta:

1. **Antes do primeiro deploy**, `vercel init`/link do projeto e `.vercel` no `.gitignore`.
2. **`git init` desde o começo** e commit antes de publicar. Publicar sem histórico é
   publicar sem volta.
3. **Preview**, e mantenha **Deployment Protection** ligada enquanto o conteúdo não tiver
   o aval de quem responde por ele. Preview fica atrás de login — diga isso a quem for
   olhar, senão a pessoa acha que o link está quebrado.
4. **Confirme o que o servidor entrega:** busque o HTML publicado e cheque o hash do
   asset; compare com o build local. "Fiz deploy" e "está no ar" são coisas diferentes.
5. **Produção** só com autorização explícita de quem pediu. Depois de publicar, verifique
   de novo o endereço público, e não só a URL do deploy.
6. **Vercel protege as URLs de deploy individuais** (preview e os endereços por hash) por
   padrão; só o alias de produção é público. Não conclua que o app está fora do ar por
   causa de um 302 — siga o redirect e veja onde caiu.

Cabeçalhos que valem configurar em `vercel.json`: cache longo e imutável para assets com
hash, cache curto para ícones e fontes, `sw.js` sempre revalidado, e os de segurança
(`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`).

## O service worker é a armadilha

O PWA instala um service worker que serve o app do cache. Consequência prática, já
observada: **depois de publicar, um navegador que já visitou o app pode continuar
rodando o bundle anterior.** O servidor entregava o arquivo novo; a página carregava o
antigo, do precache. Uma navegação não bastou — só resolveu ao desregistrar o SW e
apagar o cache.

Ordem de suspeita quando alguém disser "não vi diferença" ou "não entrou":

1. **Qual bundle a página está rodando?** Compare com o que o servidor entrega. Isto é
   a primeira coisa a checar, não a última.
2. O service worker está servindo versão antiga? (desregistrar + limpar cache confirma)
3. Só depois: cache de CDN, ou a mudança realmente não está no código.

E antes de publicar de novo, decida a **estratégia de atualização**. `autoUpdate` sozinho
não resolve para quem já está com o app aberto. As opções:

- **Banner discreto de "nova versão disponível"** com recarga no toque — melhor para app
  onde a pessoa pode estar no meio de um registro (recarregar sozinho perde o que ela
  digitou).
- Checar `registration.update()` ao voltar o foco/visibilidade da página.

No app nativo o WebView tem o mesmo comportamento, então decida isso **antes** de ir para
as lojas.

## Checklist antes de dizer "está pronto"

- [ ] Repositório versionado desde o começo, com commit antes do primeiro deploy
- [ ] Build limpo e sem pendência de tipo
- [ ] Fluxo central exercitado no navegador, com dado real e com dado vazio
- [ ] Os dois temas conferidos, e a abertura sem flash de tema
- [ ] Leitura defensiva de registro antigo/incompleto
- [ ] Preview publicado e **visto** por quem autoriza
- [ ] Hash do asset publicado confere com o build local
- [ ] Estratégia de atualização do service worker definida
- [ ] Produção publicada só após aval, e verificada depois
- [ ] Documentos de entrega escritos (README, BACKLOG, privacidade, roadmap)

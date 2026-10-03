# Configuração inicial — Instagram API com login do Instagram

Fazer uma vez. No fim, o `config.json` da pasta da skill estará completo e `ig.py verificar` responde com os dados da conta. Sem página no Facebook, sem revisão de app da Meta: como o app é usado só pela sua própria conta, ele fica em modo de desenvolvimento.

> **Parado por decisão do usuário em 03/10/2026.** O bucket do Supabase e o `config.json` já estão criados (faltam os três valores da Meta). Não retomar este guia por conta própria: só seguir se o usuário pedir para voltar com a publicação automática.

## 1. Conta profissional no Instagram

1. No app do Instagram: Configurações → Tipo e ferramentas de conta → Mudar para conta profissional.
2. Escolher **Empresa** (ou Criador; Empresa cobre tudo desta skill).
3. Anotar o **@ do perfil** (vai no `perfil` do config).

## 2. App na Meta e token

1. Acessar https://developers.facebook.com/apps e entrar com a conta do Instagram/Facebook da igreja.
2. **Criar app** → tipo **Empresa** (Business) → nome (ex.: `iecsjc-instagram`) → sem ligar a app a nenhum Business Manager existente.
3. No painel do app, **Adicionar produto** → **Instagram**.
4. Em Instagram → **API setup with Instagram login** (Configuração de API com login do Instagram), aceitar os termos.
5. Na mesma tela, gerar token: **Generate access token** → entrar com a conta do Instagram profissional → autorizar as permissões `instagram_business_basic` e `instagram_business_content_publish`.
6. Copiar o token (válido ~1 hora) e o **Instagram app secret** (Configurações → Básico → App secret; clicar em mostrar).
7. Ainda na tela de API setup, anotar o **Instagram account ID** (número comprido, começa com 1784...) — é o `ig_user_id`.

## 3. Token de longa duração

O token curto dura 1 hora; o script troca por um de ~60 dias (e depois renova):

```bash
# preencha antes no config.json: access_token (o curto) e app_secret
python3 $SKILL_DIR/scripts/ig.py token --trocar
```

Renovação depois de ~50 dias: `ig.py token --renovar`. Se o token expirar sem renovação, repetir o passo 2.5.

## 4. Hospedagem das imagens (Supabase)

A API do Instagram não recebe upload de arquivo: busca a imagem de uma URL pública. A casa usa um bucket público no Supabase (o mesmo fornecedor do site).

1. No painel do Supabase do projeto (o do site serve), **Storage** → **New bucket** → nome `instagram` → marcar **Public bucket**.
2. **Project Settings → API**: copiar `Project URL` e a `service_role` key.
3. Colocar no `config.json` (chaves `url` e `chave` da seção `hospedagem`).

A service_role chaveia tudo do bucket: fica só no `config.json` desta máquina, nunca em commit, chat ou print. Alternativa aceita pelo script: qualquer URL pública por post (`ig.py publicar --url https://...`).

## 5. Preencher o config.json

```bash
cp $SKILL_DIR/config.exemplo.json $SKILL_DIR/config.json
```

| Chave | O quê |
|---|---|
| `ig_user_id` | Instagram account ID do passo 2.7 (só dígitos) |
| `access_token` | token do passo 3 (o script o substitui ao trocar/renovar) |
| `app_secret` | App secret do passo 2.6 |
| `fuso` | `America/Sao_Paulo` (padrão) |
| `pasta_raiz` | `/home/support/Documents/IECSJC/instagram` |
| `perfil` | `@` do perfil, para referência |
| `hashtags_base` | hashtags fixas no fim de todo post de feed |
| `hospedagem` | do passo 4 |

## 6. Testar

```bash
ig.py verificar        # conta, token e limite de publicação
ig.py validar --arquivo "/home/support/Documents/IECSJC/instagram/stories/Festival Jovem Congregacional Neon.png"
ig.py fila
```

Primeiro teste real: publicar de verdade um post que seria publicado mesmo (ou um story, que some em 24h). Todo `publicar` cria conteúdo visível; não existe "modo teste" na API.

## 7. Manutenção

- **Token**: `ig.py verificar` avisa aos 50 dias; `ig.py token --renovar` renova por mais 60.
- **Trocou a senha do Instagram**: token antigo cai; repetir o passo 2.5.
- **Post falhou**: `ig.py verificar` primeiro; mensagem da API vem com o motivo (permissão, token, imagem inacessível). Depois de resolver, republicar.

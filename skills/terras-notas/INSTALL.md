# Instalação — terras-notas

## 1. Dependências locais (uma vez)

```bash
bash $SKILL_DIR/scripts/setup.sh
```

Cria `~/.config/terras-notas/` com venv (herda `pdfplumber`/`requests` do
sistema) e instala `msal`. Copia `config.json` e `depara.csv` iniciais se
ainda não existirem. Sem sudo; o `apt` não é necessário.

## 2. Registro do app no Entra (uma vez, ~10 min, gratuito)

A skill precisa de um "client_id" para falar com o Outlook em seu nome.

1. Acesse **https://entra.microsoft.com** com a conta Microsoft que usa o
   Outlook (a mesma caixa que recebe os e-mails da Fênix).
2. **Entra ID → Aplicativos → Registros de aplicativo → + Novo registro**.
3. Preencha:
   - Nome: `terras-notas`
   - Tipos de conta com suporte: **"Somente contas neste diretório
     organizacional"** basta (single-tenant). Para servir também conta
     pessoal, escolha "qualquer diretório organizacional e contas pessoais".
   - URI de redirecionamento: **não é necessário** para o login por código de
     dispositivo — pode deixar em branco.
4. **Registrar**. Na página do app, copie o **ID do aplicativo (cliente)**
   (um GUID) e também o **ID do diretório (tenant)** (visível em
   *Visão geral*).
5. No app: **Autenticação → aba Settings → "Allow public client flows" =
   Enabled → Salvar**. Sem isso o login por código falha com
   `AADSTS7000218`.
6. Cole os dois valores na config `~/.config/terras-notas/config.json`:

```json
{ "client_id": "<ID do aplicativo>", "tenant": "<ID do diretório>" }
```

> `tenant` pode ficar `"common"` para conta pessoal; para app single-tenant é
> obrigatório usar o id do diretório (ou o domínio), senão vem `AADSTS50194`.

> Permissões delegadas (`Mail.ReadWrite`, `Mail.Send`) não precisam ser
> marcadas no portal: o consentimento acontece no `auth`, na tela da
> Microsoft. Em tenant que exige consentimento de admin, aprove o app antes.

## 3. Login e descoberta (uma vez)

```bash
python3 $SKILL_DIR/scripts/terras_notas.py auth
```

Aparecerá `Acesse https://microsoft.com/devicelogin e insira o código XXXX`.
Faça isso no navegador, autorize, e o token fica em cache (renova sozinho).

```bash
python3 $SKILL_DIR/scripts/terras_notas.py descobrir-remetente
```

Lista quem mandou e-mail com "fenix/assessoria". Confirme o endereço da
Fênix Assessoria e coloque um trecho dele em `remetentes_fenix` na config
(ex.: `["@fenixassessoria.com.br"]`).

## 4. De-para e testes

```bash
python3 $SKILL_DIR/scripts/terras_notas.py depara list
python3 $SKILL_DIR/scripts/terras_notas.py run          # fetch + parse + match
python3 $SKILL_DIR/scripts/terras_notas.py despachar --rascunho
```

Confira os rascunhos no Outlook; quando estiver confiante:
`despachar --enviar --yes`.

# Microsoft Graph — endpoints usados pela skill

Autenticação **delegada** (device code) com MSAL PublicClientApplication.
A authority vem do campo `tenant` da config (`common` para conta pessoal;
id do diretório para app de tenant único). Escopos: `Mail.ReadWrite`,
`Mail.Send` — `offline_access`/`openid`/`profile` são reservados e o MSAL os
adiciona sozinho (passá-los na lista levanta `ValueError`).

Cache de token serializável em `~/.config/terras-notas/token.json` (mode 600);
`acquire_token_silent` renova com o refresh token — o `auth` interativo só é
preciso quando o refresh expira ou é revogado.

## Erros já encontrados

| Erro | Causa | Correção |
|---|---|---|
| `AADSTS7000218` (client_assertion/client_secret) | app tratado como cliente confidencial | Entra → app → **Authentication → Settings → Allow public client flows = Yes**, Salvar |
| `AADSTS50194` (/common em app single-tenant) | app é `AzureADMyOrg` e a authority era `common` | usar o id do diretório no campo `tenant` |
| 403 `Authorization_RequestDenied` em `/me` | `/me` exige `User.Read`, que não pedimos | sondar `/me/messages?$top=1` (o `auth` já faz isso) |
| `ValueError: reserved scope` | `offline_access` na lista de escopos | remover; o MSAL adiciona |

## Endpoints

| Chamada | Rota | Uso |
|---|---|---|
| Quem sou / correio | `GET /me/messages?$top=1&$select=subject` | sondagem de acesso no `auth` |
| Busca (descobrir-remetente) | `GET /me/messages?$search="fenix OR assessoria"&$count=true&$top=50` | achou a Fênix sem saber o endereço |
| Listar janela | `GET /me/messages?$filter=receivedDateTime ge …&$orderby=receivedDateTime DESC&$top=200` | `fetch` filtra remetente no cliente |
| Anexos | `GET /me/messages/{id}/attachments` | `contentBytes` em base64 |
| Rascunho | `POST /me/messages` | `despachar --rascunho` (cai na pasta Rascunhos) |
| Apagar rascunho | `DELETE /me/messages/{id}` | desfazer um rascunho errado (id fica no state) |
| Enviar | `POST /me/sendMail` | `despachar --enviar --yes`, com `saveToSentItems: true` |
| Conferir enviados | `GET /me/mailFolders/sentitems/messages` | prova de que saiu, com destinatários e anexo |

## Assinatura (imagem embutida)

Envio por API **não** recebe a assinatura do Outlook. O padrão que o Outlook
usa (e que a skill reproduz em HTML):

```json
{
  "body": { "contentType": "HTML", "content": "...<p>At.te,</p><p><img src=\"cid:assinatura\"></p>" },
  "attachments": [
    { "@odata.type": "#microsoft.graph.fileAttachment", "name": "assinatura.png",
      "contentType": "image/png", "isInline": true, "contentId": "assinatura",
      "contentBytes": "<base64>" }
  ]
}
```

Extrair a assinatura de um e-mail já enviado pelo Outlook:

```python
msgs = GET /me/mailFolders/sentitems/messages?$top=25&$select=id,subject
anexos = GET /me/messages/{id}/attachments        # sem $select: contentId só existe em fileAttachment
inline = [a for a in anexos if a["isInline"] and a["contentType"].startswith("image/")]
open("assinatura.png","wb").write(base64.b64decode(inline[0]["contentBytes"]))
```

## Pegadinhas

- `$search` **exige** cabeçalho `ConsistencyLevel: eventual` e `$count=true`;
  sem eles o Graph responde 400.
- `$search` não aceita `$orderby` na mesma chamada: a descoberta ordena no
  cliente por `receivedDateTime`.
- `POST /me/sendMail` responde **202 sem corpo** — não é erro.
- Anexo inline (`isInline: true`) e imagens de assinatura vêm junto na lista
  de anexos: filtre por `contentType == application/pdf` ou nome `.pdf`
  (o CLI já faz isso).
- Limite prático de anexo por upload simples: ~3 MB. NFS-e de SJC tem ~30 KB.
- Erros 401 com token válido em cache geralmente são conta errada: apague
  `token.json` e refaça `auth`.
- Conta pessoal (outlook.com): se `Mail.ReadWrite` devolver
  `AADSTS65001`/consentimento, o registro do app precisa estar como
  "contas em qualquer diretório organizacional e contas Microsoft pessoais"
  (multitenant + personal). Ver INSTALL.md.

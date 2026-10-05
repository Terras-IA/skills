# Pareamento e problemas do canal WhatsApp

## Onde a sessão mora

`<sidecar>/.auth/` — a credencial da conta, mesma classe do arquivo `.env`. Nunca copiar, versionar nem mandar para outra máquina. Parear de novo escreve ali; publicar apenas lê.

## Parear por código (funciona remoto)

1. O celular precisa estar com a tela de digitação aberta: WhatsApp → Aparelhos conectados → Conectar um aparelho → "Conectar com número de telefone em vez disso". Atenção: o campo já vem com o DDI selecionado; digite só DDD + número, senão acusa "número incorreto".
2. Apagar a sessão velha SÓ se ela estiver morta (status 401); estado meio registrado atrapalha. Com a sessão viva, não toque.
3. Pedir o código UMA vez e imprimir. O código vale poucos minutos: combine com o dono para ele estar na tela antes.
4. Se o celular aceitar e a conexão cair com status 515 (restart required), **não é falha**: reconecte com o MESMO estado (mesma pasta `.auth`, sem apagar) e o registro conclui. Apagar nesse momento foi o que travava pareamentos por meses.
5. `connection: open` = sessão salva. Valide com um envio de teste para o próprio número antes de publicar no canal.

## Parear por QR (bom quando é local)

A página de pareamento do sidecar serve um QR que se renova sozinho, em loopback. Para acessar de outra máquina, túnel SSH (`ssh -L 4411:127.0.0.1:4411 <host>`) e abra `http://127.0.0.1:4411`. Se abrir a porta para a rede local, feche assim que parear: o QR é credencial de pareamento.

## Descobrir o JID do canal pelo link de convite

O link `https://whatsapp.com/channel/<código>` traz o código de convite. Consulta de metadata por convite (`newsletterMetadata("invite", <código>)`) devolve o id; o mesmo id terminado em `@newsletter` é o que vai na config. O papel da conta sai na consulta por "jid" (`viewer_metadata.role`), não na por convite.

## Problemas comuns

| Sintoma | O que é | O que fazer |
|---|---|---|
| status 401, "aparelho deslogado" | o celular removeu o aparelho (logout ou troca de número) | apagar `.auth` e reparear |
| status 515 no pareamento | reinício pedido pelo servidor, parte normal do registro | reconectar com o MESMO estado, sem apagar |
| código "expirado" repetido | a janela do código é curta, e a corrida com o celular come a validade | deixar a tela de digitação aberta e pedir o código com o celular à mão |
| "número incorreto" ao digitar | o campo do celular já tem o DDI preenchido | digitar só DDD + número |
| "Bad MAC / Failed to decrypt" no início | fila antiga de notificações da sessão recém-pareada | ignorar; para em poucos minutos |
| leitura de mensagens do canal estoura timeout | limitação do fetch de newsletter nesta versão do Baileys | confirmação visual é do dono, no aplicativo |
| evento de QR com sessão existente | o pareamento não está mais valendo | reparear |

## Limpeza de sessão

Para começar do zero: parar o sidecar, apagar `.auth` e reparear. Guardar a pasta antiga (`mv .auth .auth-removida-<data>`) é precaução aceitável por pouco tempo; ela continua sendo credencial, nunca em pasta versionada ou sincronizada.

# Checklist por camada

Confira no painel e na documentação oficial (developers.cloudflare.com) antes de citar limite de plano: os números mudam. O que está aqui é o mapa, não a tabela de preços.

## 1. DNS e proxy

- Nameservers da Cloudflare no registrador e zona "Active".
- Todo registro que serve HTTP(S) com proxy ligado (nuvem laranja).
- Registro que não pode ter proxy (MX, mail, ftp, ssh) **não** pode apontar para o IP do servidor web.
- Subdomínios esquecidos: `dev`, `staging`, `homolog`, `cpanel`, `origin`, `direct`. O `checar.py` testa os comuns; peça a lista completa da zona ao usuário (exportar DNS no painel).

## 2. Estancar (site caindo agora)

| Ação | Onde | Efeito | Custo para o usuário |
|------|------|--------|----------------------|
| Under Attack | Visão geral da zona, ou Segurança > Configurações | Desafio JS para todo visitante | Atrito para cliente real; API e app mobile podem quebrar. Desligar quando passar |
| Rate limit | Segurança > WAF > Regras de limitação de taxa | Bloqueia IP que passa de N requisições em X s num caminho | Free tem poucas regras: use no caminho que o log mostra |
| Bot Fight Mode | Segurança > Bots | Desafia robô conhecido | Pode atrapalhar integração legítima (webhook, monitor) |
| Regra de WAF personalizada | Segurança > WAF > Regras personalizadas | Desafio ou bloqueio por caminho, ASN, país, user-agent | Free tem quantidade limitada |

Exceção para API e webhook: regra que pula o desafio para o caminho `/api/` ou IP do parceiro, senão Under Attack derruba integração.

## 3. Fechar a origem

### Opção A: firewall só com faixas da Cloudflare

Faixas oficiais: `https://www.cloudflare.com/ips-v4` e `ips-v6`. Busque na hora, não cole de memória.

ufw:
```bash
for ip in $(curl -s https://www.cloudflare.com/ips-v4) $(curl -s https://www.cloudflare.com/ips-v6); do
  sudo ufw allow proto tcp from "$ip" to any port 80,443
done
sudo ufw deny 80/tcp && sudo ufw deny 443/tcp
```
Confira a ordem das regras (`ufw status numbered`): o allow tem que vir antes do deny. Agende a atualização das faixas (cron semanal).

Firewall da hospedagem (security group, painel da VPS) é melhor que o do sistema: o tráfego nem chega à máquina.

### Opção B: Cloudflare Tunnel

`cloudflared` no servidor abre conexão de saída para a Cloudflare. O servidor fecha todas as portas de entrada web. Bom para VPS pequena e para painel administrativo. Exige instalar e manter o agente.

### Opção C, complemento: Authenticated Origin Pulls

O servidor exige certificado de cliente da Cloudflare (mTLS). Impede que alguém use a própria conta Cloudflare apontando para o seu IP.

### Conferência

`checar.py DOMINIO --origem IP --host app.DOMINIO` tem que dar fechado em HTTP e HTTPS.

## 4. IP vazado

Fontes de vazamento além do DNS atual:
- SPF com `ip4:` do servidor.
- Cabeçalho `Received:` de e-mail enviado pelo próprio servidor (formulário de contato via PHP `mail()`).
- Histórico de DNS de antes da Cloudflare (serviços de histórico de DNS guardam por anos).
- Certificado emitido para o IP, banner de FTP/SSH, página padrão do servidor indexada.

Se vazou e o ataque é dirigido: novo IP, nada além da web nele, e só a Cloudflare sabe o novo. Envio de e-mail por serviço externo (SMTP transacional), não pelo servidor.

## 5. Robôs que imitam navegador

- Turnstile no formulário atacado. Validar o token no servidor (`siteverify`); só o widget no front não protege.
- Regras por comportamento (caminho + taxa) valem mais que bloqueio por país.

## 6. Servidor enxergar o visitante real

nginx:
```nginx
# um set_real_ip_from por faixa da Cloudflare
set_real_ip_from 173.245.48.0/20;
real_ip_header CF-Connecting-IP;
```
Apache: `mod_remoteip` com `RemoteIPHeader CF-Connecting-IP` e `RemoteIPTrustedProxy` por faixa.

## 7. Fora do HTTP

Proxy da nuvem laranja cobre HTTP(S). SSH, FTP, SMTP e banco não passam por ele. Opções: restringir por IP no firewall, VPN, Cloudflare Access/Tunnel para SSH, Spectrum (planos pagos) para TCP genérico.

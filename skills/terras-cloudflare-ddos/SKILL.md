---
name: terras-cloudflare-ddos
description: "Proteção contra DDoS e robôs com Cloudflare: mede de fora se o domínio está atrás do proxy, acha IP de origem vazado e fecha a porta dos fundos. Use quando site cai com 503, 'estamos protegidos?' ou para revisar Cloudflare. DAST é terras-zap. DDoS, origin IP, WAF."
keywords: [cloudflare, ddos, 503, robos, bots, proxy, nuvem laranja, ip de origem, firewall, turnstile, rate limit, under attack, waf, origin ip]
---

# Cloudflare contra DDoS: medir, estancar, fechar a origem

## Objetivo

Deixar um site atrás da Cloudflare de forma que o ataque não chegue ao servidor por nenhum caminho. A nuvem laranja ligada no registro principal não basta. Se o IP da origem é conhecido, o atacante vai direto nele e a Cloudflare nem vê o tráfego. Esta skill mede isso de fora, põe em ordem o que fazer e separa o que estanca hoje do que fecha de vez.

## Regra dura

1. **Meça antes de afirmar.** Rode `scripts/checar.py` antes de dizer "está protegido" ou "não está". Sem a medição, a resposta é palpite.
2. **Site caído agora: estanque primeiro.** Ligue o modo Under Attack e uma regra de rate limit antes de qualquer arquitetura. Depois feche a origem.
3. **IP vazado continua vazado.** Fechar o firewall protege as portas web, mas um IP que já esteve em DNS público pode receber flood de rede. Se houve vazamento e o ataque foi dirigido, troque o IP da origem e não publique o novo em lugar nenhum: mail, FTP e painel saem desse IP.
4. **Não afirme o que a Cloudflare não faz no plano.** A mitigação de DDoS é automática e ilimitada em todos os planos, inclusive o Free. O que muda por plano é a quantidade de regras de WAF e de rate limit e os recursos de robô. Proxy em HTTP(S) não protege portas que não são web (SSH, FTP, SMTP, banco).
5. **Teste de acesso direto só com autorização.** `--origem` faz requisição ao IP do servidor. Use só em servidor do usuário ou de cliente que autorizou. Não varra IPs de terceiros.
6. **Mudança na conta é do usuário.** Ligar Under Attack, criar regra, mudar DNS ou firewall: proponha o passo exato e espere o sim. O MCP de Workers ligado nesta máquina não mexe em DNS nem em zona; não finja que leu a configuração da zona.

## Como trabalhar

1. **Medir de fora.**
   ```bash
   python3 "$SKILL_DIR/scripts/checar.py" DOMINIO --sub app --sub OUTRO
   ```
   Lista apex, subdomínios comuns, os passados em `--sub` e os alvos do MX, cada IP marcado `ok` (faixa Cloudflare) ou `!!` (exposto). Saída 1 = achou exposição. `--json` para relatório.
   - IP `!!` igual ao do servidor web = origem vazada. Anote por onde (mail, ftp, cpanel, subdomínio esquecido em "DNS only").
   - Peça ao usuário outras fontes de vazamento que o DNS atual não mostra: SPF com `ip4:`, cabeçalho `Received` de e-mail enviado pelo servidor, histórico de DNS anterior à Cloudflare, certificado emitido para o IP.
2. **Testar a porta dos fundos** (com autorização, regra 5):
   ```bash
   python3 "$SKILL_DIR/scripts/checar.py" DOMINIO --origem IP --host app.DOMINIO
   ```
   `ABERTA` = a origem aceita tráfego que não passou pela Cloudflare. Fechada só conta depois do passo 4.
3. **Estancar, se o site está caindo agora.** Proponha, nesta ordem: modo Under Attack na zona; regra de rate limit no caminho que o log mostra (login, busca, API); Bot Fight Mode. Detalhe e limites por plano: `references/checklist.md`.
4. **Fechar a origem.** Duas saídas, escolha com o usuário:
   - Firewall do servidor aceita 80/443 só das faixas em cloudflare.com/ips (ufw, nftables, security group). Liste as faixas pelo script, não de memória: elas mudam.
   - Cloudflare Tunnel (`cloudflared`): o servidor não abre porta de entrada nenhuma. Melhor quando dá para instalar o agente.
   Refaça o passo 2: tem que dar fechado nas duas portas.
5. **Tirar o resto do IP.** Mail, FTP e painel que estavam no mesmo IP vão para outro host ou passam a ser só por VPN/IP fixo. Se houve vazamento e ataque dirigido, troque o IP (regra 3). Refaça o passo 1: nenhum `!!` apontando para a origem.
6. **Robôs que imitam navegador.** Turnstile no formulário que o ataque usa (login, cadastro, contato), validado no servidor. Regras de WAF por caminho, ASN ou país só com base no log, não por chute.
7. **Servidor enxergar o visitante real.** `mod_remoteip` (Apache) ou `real_ip_header CF-Connecting-IP` (nginx), confiando só nas faixas da Cloudflare. Sem isso, fail2ban e limite por IP bloqueiam a própria Cloudflare.
8. **Entregar.** Tabela com: item, medido (sim/não), estado, próximo passo, dono. Separe o que foi medido do que o usuário afirmou. Feche dizendo o que ainda não está protegido.

## O que esta skill não cobre

- Varredura de vulnerabilidade da aplicação: `terras-zap`. Revisão de código: `terras-security-review`.
- Causa interna do 503 (pool do PHP-FPM, banco lento, memória): olhe o servidor depois de estancar; a Cloudflare não conserta aplicação que cai com tráfego legítimo.

## Referências

- `references/checklist.md` — itens por camada, o que cada plano libera, comandos de firewall com as faixas da Cloudflare, Tunnel e onde fica cada botão no painel.
- `references/vermelho.md` — o que um agente sem a skill errou no cenário de teste e a regra que fecha cada falha.

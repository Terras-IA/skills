# Vermelho: o que deu errado sem a skill (2026-11-15)

Cenário: software house, site PHP numa VPS caiu hoje com 503 por robôs. Domínio já na Cloudflare Free, nuvem laranja no `app`. `mail` e `ftp` apontam para a mesma VPS. "Estamos protegidos?"

Agente sem a skill acertou o centro (a origem segue exposta pelo mail e ftp, fechar 80/443 só para a Cloudflare, restaurar IP real). Falhas:

| # | Falha observada | Regra que fecha |
|---|---|---|
| 1 | Afirmou sem medir; "provavelmente em DNS-only" ficou como suposição | Regra 1 e passo 1 (`checar.py`) |
| 2 | "O plano Free não bloqueia robôs por conta própria": mistura robô com DDoS e sugere que o Free não mitiga ataque. A mitigação de DDoS é automática em todos os planos | Regra 4 |
| 3 | O site caiu hoje e o primeiro passo foi conferir nameserver; Under Attack não aparece na lista | Regra 2 e passo 3 |
| 4 | Troca de IP só "se o ataque continuar"; com IP já público e firewall só em 80/443, o flood de rede ainda chega | Regra 3 e passo 5 |
| 5 | Turnstile não aparece; robô que imita navegador passa pelo Bot Fight Mode | Passo 6 |
| 6 | Cloudflare Tunnel não aparece como alternativa à lista de IPs no firewall | Passo 4 |
| 7 | Sugeriu `curl` direto no IP sem lembrar de autorização | Regra 5 |

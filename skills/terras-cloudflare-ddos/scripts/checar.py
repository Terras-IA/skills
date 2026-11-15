#!/usr/bin/env python3
"""Confere, de fora e só lendo, se um domínio está atrás da Cloudflare e onde vaza a origem.

Uso:
  checar.py DOMINIO [--sub app --sub www ...] [--origem IP] [--host app.dominio] [--json]

O que faz:
  1. Baixa as faixas oficiais da Cloudflare (cloudflare.com/ips-v4 e ips-v6).
  2. Resolve A, AAAA e CNAME do apex, dos subdomínios comuns e dos passados em --sub,
     e os alvos do MX. Marca cada IP como "cloudflare" ou "exposto".
  3. Se --origem for passado, tenta HTTP e HTTPS direto no IP com o Host do site.
     Responder = a origem aceita tráfego que não veio da Cloudflare (porta dos fundos aberta).
     Só use --origem em servidor do próprio usuário ou do cliente que autorizou.

Saída: 0 tudo atrás da Cloudflare e origem fechada; 1 achou exposição; 2 erro de uso ou rede.
Não altera nada: só DNS e requisições GET/HEAD.
"""
import argparse
import ipaddress
import json
import ssl
import subprocess
import sys
import urllib.request

COMUNS = ["www", "app", "api", "admin", "painel", "mail", "webmail", "smtp", "ftp",
          "cpanel", "dev", "staging", "homolog", "origin", "direct", "vpn"]
URLS_IPS = ["https://www.cloudflare.com/ips-v4", "https://www.cloudflare.com/ips-v6"]


def faixas_cloudflare():
    redes = []
    for url in URLS_IPS:
        req = urllib.request.Request(url, headers={"User-Agent": "checar-cloudflare/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            for linha in r.read().decode().split():
                redes.append(ipaddress.ip_network(linha.strip()))
    return redes


def dig(nome, tipo):
    out = subprocess.run(["dig", "+short", "+time=3", "+tries=2", nome, tipo],
                         capture_output=True, text=True).stdout
    return [l.strip().rstrip(".") for l in out.splitlines() if l.strip()]


def e_ip(s):
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        return False


def classificar(ip, redes):
    end = ipaddress.ip_address(ip)
    return "cloudflare" if any(end in r for r in redes if r.version == end.version) else "exposto"


def resolver(nome, redes):
    """Devolve [{nome, tipo, valor, status}] para A/AAAA, seguindo CNAME."""
    linhas = []
    for tipo in ("A", "AAAA"):
        for v in dig(nome, tipo):
            if e_ip(v):
                linhas.append({"nome": nome, "tipo": tipo, "valor": v, "status": classificar(v, redes)})
            else:
                linhas.append({"nome": nome, "tipo": "CNAME", "valor": v, "status": "cname"})
    # dedup de CNAME repetido entre A e AAAA
    vistos, unicos = set(), []
    for l in linhas:
        k = (l["tipo"], l["valor"])
        if k not in vistos:
            vistos.add(k)
            unicos.append(l)
    return unicos


def testar_origem(ip, host):
    """Tenta falar direto com a origem. Devolve lista de {url, status|erro}."""
    resultados = []
    alvo = f"[{ip}]" if ":" in ip else ip
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    for esquema in ("http", "https"):
        url = f"{esquema}://{alvo}/"
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"Host": host, "User-Agent": "checar-cloudflare/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=8, context=ctx if esquema == "https" else None) as r:
                resultados.append({"url": url, "status": r.status, "aberta": True})
        except urllib.error.HTTPError as e:
            # qualquer resposta HTTP prova que a porta aceita conexão vinda de fora da Cloudflare
            resultados.append({"url": url, "status": e.code, "aberta": True})
        except Exception as e:  # timeout, recusa, reset: fechada para nós
            resultados.append({"url": url, "erro": type(e).__name__, "aberta": False})
    return resultados


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dominio")
    ap.add_argument("--sub", action="append", default=[], help="subdomínio extra (repetível)")
    ap.add_argument("--origem", help="IP da origem para testar acesso direto (só com autorização)")
    ap.add_argument("--host", help="Host usado no teste direto (padrão: o domínio)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    try:
        redes = faixas_cloudflare()
    except Exception as e:
        print(f"[erro] não baixei as faixas da Cloudflare: {e}", file=sys.stderr)
        return 2

    dom = a.dominio.lower().strip(".")
    nomes = [dom] + [f"{s}.{dom}" for s in dict.fromkeys(COMUNS + a.sub)]
    registros = []
    for n in nomes:
        registros += resolver(n, redes)

    mx = []
    for linha in dig(dom, "MX"):
        partes = linha.split()
        if partes:
            alvo = partes[-1].rstrip(".")
            mx.append(alvo)
            for r in resolver(alvo, redes):
                r["via_mx"] = True
                registros.append(r)

    expostos = [r for r in registros if r["status"] == "exposto"]
    origem = testar_origem(a.origem, a.host or dom) if a.origem else []
    porta_aberta = any(o["aberta"] for o in origem)

    rel = {
        "dominio": dom,
        "registros": registros,
        "mx": mx,
        "expostos": expostos,
        "ips_expostos": sorted({r["valor"] for r in expostos}),
        "origem_testada": a.origem,
        "origem": origem,
        "porta_dos_fundos_aberta": porta_aberta,
    }
    if a.json:
        print(json.dumps(rel, ensure_ascii=False, indent=2))
    else:
        for r in registros:
            marca = {"cloudflare": "ok ", "exposto": "!! ", "cname": "-> "}[r["status"]]
            extra = " (MX)" if r.get("via_mx") else ""
            print(f"{marca}{r['nome']:<32} {r['tipo']:<5} {r['valor']}{extra}")
        if expostos:
            print(f"\n[!] IPs fora da Cloudflare: {', '.join(rel['ips_expostos'])}")
        for o in origem:
            print(f"[origem] {o['url']} -> {o.get('status', o.get('erro'))}"
                  f"{'  ABERTA' if o['aberta'] else ''}")
    return 1 if expostos or porta_aberta else 0


if __name__ == "__main__":
    sys.exit(main())

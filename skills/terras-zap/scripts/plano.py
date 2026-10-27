#!/usr/bin/env python3
"""Gera o plano YAML do Automation Framework do ZAP.

Modos:
  baseline  spider + varredura passiva (não ataca; padrão)
  api       importa OpenAPI + passiva
  full      baseline + varredura ATIVA (exige --autorizacao)
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


def lista(valores):
    return "[" + ", ".join(json.dumps(v) for v in valores) + "]"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url", help="URL de entrada do alvo")
    p.add_argument("--modo", choices=["baseline", "api", "full"], default="baseline")
    p.add_argument("--saida", required=True, help="pasta onde ficam plano e relatórios")
    p.add_argument("--openapi", help="URL ou arquivo da spec OpenAPI (modo api)")
    p.add_argument("--excluir", action="append", default=[], help="regex de caminho a não tocar (ex.: .*logout.*)")
    p.add_argument("--ajax", action="store_true", help="usa também o spider AJAX (SPA; mais lento, abre Firefox headless)")
    p.add_argument("--spider-min", type=int, default=5)
    p.add_argument("--ativo-min", type=int, default=30)
    p.add_argument("--autorizacao", help="quem autorizou a varredura ativa e onde (obrigatório no modo full)")
    a = p.parse_args()

    u = urlparse(a.url)
    if u.scheme not in ("http", "https") or not u.netloc:
        sys.exit("URL precisa ser http(s)://host/...")
    if a.modo == "full" and not (a.autorizacao or "").strip():
        sys.exit("Modo full ataca o alvo: passe --autorizacao 'quem autorizou, quando, escopo'.")
    if a.modo == "api" and not a.openapi:
        sys.exit("Modo api precisa de --openapi.")

    saida = Path(a.saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    base = f"{u.scheme}://{u.netloc}"
    excluir = a.excluir + [r".*logout.*", r".*sair.*", r".*signout.*"]

    y = [
        "# Gerado por terras-zap/scripts/plano.py",
        f"# modo: {a.modo}",
    ]
    if a.autorizacao:
        y.append(f"# autorizacao: {a.autorizacao}")
    y += [
        "env:",
        "  contexts:",
        "    - name: alvo",
        f"      urls: {lista([a.url])}",
        f"      includePaths: {lista([re.escape(base) + '.*'])}",
        f"      excludePaths: {lista(excluir)}",
        "  parameters:",
        "    failOnError: true",
        "    failOnWarning: false",
        "    progressToStdout: true",
        "jobs:",
        "  - type: passiveScan-config",
        "    parameters:",
        "      maxAlertsPerRule: 10",
    ]
    if a.modo == "api":
        alvo_api = a.openapi
        chave = "apiUrl" if re.match(r"https?://", alvo_api) else "apiFile"
        if chave == "apiFile":
            alvo_api = str(Path(alvo_api).resolve())
        y += [
            "  - type: openapi",
            "    parameters:",
            f"      {chave}: {json.dumps(alvo_api)}",
            f"      targetUrl: {json.dumps(base)}",
            "      context: alvo",
        ]
    y += [
        "  - type: spider",
        "    parameters:",
        "      context: alvo",
        f"      maxDuration: {a.spider_min}",
    ]
    if a.ajax:
        y += [
            "  - type: spiderAjax",
            "    parameters:",
            "      context: alvo",
            f"      maxDuration: {a.spider_min}",
            "      browserId: firefox-headless",
        ]
    y += [
        "  - type: passiveScan-wait",
        "    parameters:",
        "      maxDuration: 10",
    ]
    if a.modo == "full":
        y += [
            "  - type: activeScan",
            "    parameters:",
            "      context: alvo",
            f"      maxScanDurationInMins: {a.ativo_min}",
            "      threadPerHost: 2",
        ]
    for tpl, arq in (("traditional-json", "zap.json"), ("traditional-html", "zap.html")):
        y += [
            "  - type: report",
            "    parameters:",
            f"      template: {tpl}",
            f"      reportDir: {json.dumps(str(saida))}",
            f"      reportFile: {arq}",
        ]

    plano = saida / "plano.yaml"
    plano.write_text("\n".join(y) + "\n")
    print(plano)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Gera a arte de fundo do banner via qwen-image (Model Studio, provedor Alibaba).

Uso:
    python3 gen_art.py --prompt "..." --out /caminho/arte.png [--size 1200x628]
    python3 gen_art.py --prompt-file prompt.txt --out arte.png --model qwen-image-3.0

A chave sai do provider_config.json do ZCode (provedor com baseUrl maas.aliyuncs.com)
ou da variável TERRAS_IMAGE_KEY. A URL devolvida é um OSS com expiração, então o
download acontece na mesma execução.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

PROVIDER_CONFIG = os.path.expanduser("~/.zcode/v2/provider_config.json")
DEFAULT_ENDPOINT = (
    "https://ws-crocxnyahqxwobq2.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/images/generations"
)
DEFAULT_MODEL = "qwen-image-3.0-pro"
SIZE_RE = re.compile(r"^\d{3,4}x\d{3,4}$")


def find_key():
    """Procura a apiKey do provedor Alibaba/Model Studio no config do ZCode."""
    env = os.environ.get("TERRAS_IMAGE_KEY")
    if env:
        return env, DEFAULT_ENDPOINT
    try:
        with open(PROVIDER_CONFIG) as fh:
            cfg = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.exit(f"não consegui ler {PROVIDER_CONFIG}: {exc}")
    rules = (
        cfg.get("config", {}).get("providerConfigRules", {}).get("providerRules", [])
    )
    for rule in rules:
        conf = rule.get("config", {})
        base = (conf.get("api", {}) or {}).get("baseUrl", "") or ""
        key = (conf.get("access", {}) or {}).get("apiKey", "") or ""
        if "maas.aliyuncs.com" in base and key:
            endpoint = base.rstrip("/") + "/images/generations"
            return key, endpoint
    sys.exit(
        "nenhum provedor maas.aliyuncs.com com apiKey em "
        f"{PROVIDER_CONFIG}; use TERRAS_IMAGE_KEY para passar a chave na mão"
    )


def generate(prompt, out_path, size, model, key, endpoint, timeout=180):
    payload = json.dumps(
        {"model": model, "prompt": prompt, "n": 1, "size": size}
    ).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        sys.exit(f"HTTP {exc.code} na geração: {detail}")
    except urllib.error.URLError as exc:
        sys.exit(f"falha de rede na geração: {exc}")

    data = body.get("data") or []
    if not data or not data[0].get("url"):
        sys.exit(f"resposta sem url de imagem: {json.dumps(body)[:400]}")
    url = data[0]["url"]

    # A URL do OSS expira; baixar já.
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        img = resp.read()

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(img)

    usage = body.get("usage") or {}
    got = f"{usage.get('output_width')}x{usage.get('output_height')}"
    print(f"{out_path} {len(img)} bytes modelo={model} pedido={size} devolvido={got}")
    if usage.get("output_width") and got != size:
        print(
            f"AVISO: o modelo devolveu {got} e não {size}; conferir antes de renderizar",
            file=sys.stderr,
        )
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--prompt")
    src.add_argument("--prompt-file")
    ap.add_argument("--out", required=True, help="caminho do PNG de saída")
    ap.add_argument("--size", default="1200x628", help="<largura>x<altura>, com x")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    if not SIZE_RE.match(args.size):
        sys.exit(f"size inválido: {args.size!r}; usar <largura>x<altura>, ex. 1200x628")

    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as fh:
            prompt = fh.read().strip()
    if not prompt:
        sys.exit("prompt vazio")

    key, endpoint = find_key()
    generate(prompt, args.out, args.size, args.model, key, endpoint)


if __name__ == "__main__":
    main()

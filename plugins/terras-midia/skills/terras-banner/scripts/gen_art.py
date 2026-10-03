#!/usr/bin/env python3
"""Gera a arte de fundo do banner via qwen-image (Model Studio, provedor Alibaba).

Uso:
    python3 gen_art.py --prompt "..." --out /caminho/arte.png [--size 1200x628]
    python3 gen_art.py --prompt-file prompt.txt --out arte.png --model qwen-image-3.0

A chave sai de TERRAS_IMAGE_KEY (Model Studio/Alibaba). Quando o Model Studio
falha (cota gratuita esgotada é o caso comum), cai para o provedor x.ai
(grok-imagine-image-2.0, chave em TERRAS_IMAGE_KEY_XAI) e depois para a OpenAI
(gpt-image-2, chave em TERRAS_IMAGE_KEY_OPENAI; o tamanho pedido vira o mais
próximo entre 1024x1024, 1536x1024 e 1024x1536). A URL devolvida é um OSS com
expiração, então o download acontece na mesma execução.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request

DEFAULT_ENDPOINT = os.environ.get("TERRAS_IMAGE_ENDPOINT") or (
    "https://ws-crocxnyahqxwobq2.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1/images/generations"
)
DEFAULT_MODEL = "qwen-image-3.0-pro"
XAI_ENDPOINT = "https://api.x.ai/v1/images/generations"
XAI_MODEL = "grok-imagine-image-2.0"
OPENAI_ENDPOINT = "https://api.openai.com/v1/images/generations"
OPENAI_MODEL = "gpt-image-2"
SIZE_RE = re.compile(r"^\d{3,4}x\d{3,4}$")


def find_key():
    """Chave do Model Studio (Alibaba) pela variável de ambiente."""
    key = os.environ.get("TERRAS_IMAGE_KEY")
    if not key:
        sys.exit(
            "TERRAS_IMAGE_KEY não definida: exporte a apiKey do Model Studio "
            "(maas.aliyuncs.com) antes de gerar a arte"
        )
    return key, DEFAULT_ENDPOINT


def find_xai_key():
    """Chave do provedor x.ai (TERRAS_IMAGE_KEY_XAI), fallback do Model Studio.

    Devolve (key, endpoint) ou (None, None).
    """
    env = os.environ.get("TERRAS_IMAGE_KEY_XAI")
    if env:
        return env, XAI_ENDPOINT
    return None, None


def find_openai_key():
    """Chave do provedor OpenAI (TERRAS_IMAGE_KEY_OPENAI), fallback final.

    Devolve (key, endpoint) ou (None, None).
    """
    env = os.environ.get("TERRAS_IMAGE_KEY_OPENAI")
    if env:
        return env, OPENAI_ENDPOINT
    return None, None


def tamanho_openai(size):
    """A API da OpenAI só aceita 3 tamanhos; escolhe o mais próximo pelo aspecto."""
    largura, altura = (int(x) for x in size.split("x"))
    aspecto = largura / altura
    if aspecto > 1.2:
        return "1536x1024"
    if aspecto < 0.83:
        return "1024x1536"
    return "1024x1024"


def generate(prompt, out_path, size, model, key, endpoint, timeout=180, send_size=True):
    payload = {"model": model, "prompt": prompt, "n": 1}
    if send_size:
        payload["size"] = size
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode(),
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
        raise RuntimeError(f"HTTP {exc.code} na geração: {detail}")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"falha de rede na geração: {exc}")

    data = body.get("data") or []
    primeiro = data[0] if data else {}
    if not primeiro.get("url") and not primeiro.get("b64_json"):
        raise RuntimeError(f"resposta sem imagem: {json.dumps(body)[:400]}")

    if primeiro.get("b64_json"):
        img = base64.b64decode(primeiro["b64_json"])
    else:
        # A URL do OSS (ou do x.ai) expira; baixar já.
        with urllib.request.urlopen(primeiro["url"], timeout=timeout) as resp:
            img = resp.read()

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(img)

    usage = body.get("usage") or {}
    got = f"{usage.get('output_width')}x{usage.get('output_height')}"
    print(f"{out_path} {len(img)} bytes modelo={model} pedido={size} devolvido={got}")
    if send_size and usage.get("output_width") and got != size:
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
    try:
        generate(prompt, args.out, args.size, args.model, key, endpoint)
        return
    except RuntimeError as exc:
        print(f"AVISO: Model Studio falhou ({exc}); tentando x.ai", file=sys.stderr)

    xkey, xendpoint = find_xai_key()
    if xkey:
        try:
            generate(prompt, args.out, args.size, XAI_MODEL, xkey, xendpoint,
                     send_size=False)
            return
        except RuntimeError as exc:
            print(f"AVISO: x.ai falhou ({exc}); tentando OpenAI", file=sys.stderr)
    else:
        print("AVISO: sem chave x.ai; tentando OpenAI", file=sys.stderr)

    okey, oendpoint = find_openai_key()
    if not okey:
        sys.exit("erro: geração falhou em todos os provedores disponíveis")
    generate(prompt, args.out, tamanho_openai(args.size), OPENAI_MODEL, okey,
             oendpoint)


if __name__ == "__main__":
    main()

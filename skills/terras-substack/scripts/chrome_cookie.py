#!/usr/bin/env python3
"""Importa cookies de um dominio do perfil local do Chrome/Chromium/Brave (Linux).

Le apenas as linhas do dominio pedido na base de cookies do navegador e usa a
chave "Chrome Safe Storage" do chaveiro do sistema para descriptografar os
valores (AES-128-CBC, formato v10/v11). Nada e enviado para a rede.

Uso:
    python3 chrome_cookie.py --cookie-header substack.com
    python3 chrome_cookie.py --json substack.com
    python3 chrome_cookie.py --value substack.com substack.sid
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

PROFILE_CANDIDATES = (
    "~/.config/google-chrome",
    "~/.config/google-chrome-beta",
    "~/.config/chromium",
    "~/.config/BraveSoftware/Brave-Browser",
)

SALT = b"saltysalt"
IV = b" " * 16


def find_profile(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_dir():
            raise SystemExit(f"perfil nao encontrado: {path}")
        return path
    for candidate in PROFILE_CANDIDATES:
        path = Path(candidate).expanduser()
        if path.is_dir():
            return path
    raise SystemExit("nenhum perfil de Chrome/Chromium encontrado")


def keyring_password() -> bytes | None:
    """Senha "Chrome Safe Storage" via libsecret (chaveiro do sistema)."""
    try:
        import gi

        gi.require_version("Secret", "1")
        from gi.repository import Secret
    except Exception:
        return None

    try:
        schema = Secret.Schema.new(
            "com.google.Chrome.SafeStorage",
            Secret.SchemaFlags.NONE,
            {"application": Secret.SchemaAttributeType.STRING},
        )
        secret = Secret.password_lookup_sync(schema, {"application": "chrome"}, None)
    except Exception:
        return None
    return secret.encode("utf-8") if secret else None


def secret_tool_password() -> bytes | None:
    if not shutil.which("secret-tool"):
        return None
    try:
        out = subprocess.run(
            ["secret-tool", "lookup", "application", "chrome"],
            capture_output=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return None
    return out or None


def derive_key(password: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha1", password, SALT, iterations, 16)


def _aes_cbc_decrypt(blob: bytes, key: bytes) -> bytes | None:
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        decryptor = Cipher(algorithms.AES(key), modes.CBC(IV)).decryptor()
        return decryptor.update(blob) + decryptor.finalize()
    except ImportError:
        pass

    if not shutil.which("openssl"):
        return None
    proc = subprocess.run(
        ["openssl", "enc", "-d", "-aes-128-cbc", "-K", key.hex(), "-iv", IV.hex(), "-nopad"],
        input=blob,
        capture_output=True,
    )
    return proc.stdout if proc.returncode == 0 else None


def _strip_pkcs7(data: bytes) -> bytes:
    if not data:
        return data
    pad = data[-1]
    if 1 <= pad <= 16 and data[-pad:] == bytes([pad]) * pad:
        return data[:-pad]
    return data


def _looks_like_text(data: bytes) -> bool:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return not any(ch in text for ch in "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f")


def decrypt_value(encrypted: bytes, keys: list[bytes]) -> str | None:
    if not encrypted:
        return None
    if encrypted[:3] not in (b"v10", b"v11"):
        # Valor em texto puro (cookies nao criptografados).
        return encrypted.decode("utf-8", "replace")

    body = encrypted[3:]
    for key in keys:
        for candidate in (body, body[:-16] if len(body) > 32 else body):
            plain = _aes_cbc_decrypt(candidate, key)
            if not plain:
                continue
            plain = _strip_pkcs7(plain)
            if plain and _looks_like_text(plain):
                return plain.decode("utf-8")
    return None


def candidate_keys() -> list[bytes]:
    password = keyring_password() or secret_tool_password()
    keys: list[bytes] = []
    if password:
        keys.extend(derive_key(password, 1003))
        keys.append(derive_key(password, 1))
    keys.extend([derive_key(b"peanuts", 1), derive_key(b"peanuts", 1003)])
    return keys


def find_cookie_databases(profile: Path, profile_name: str | None) -> list[Path]:
    """Bases de cookies do perfil.

    Sem `profile_name`, varre o perfil inteiro — navegadores embutidos
    (Electron) guardam a sessao em `Partitions/<nome>/Cookies`, e nessas bases o
    valor costuma estar em texto claro, sem criptografia.
    """
    if profile_name:
        candidate = profile / profile_name / "Cookies"
        if not candidate.is_file():
            raise SystemExit(f"base de cookies nao encontrada: {candidate}")
        return [candidate]

    found = [path for path in profile.rglob("Cookies") if path.is_file() and path.stat().st_size < 100 * 1024 * 1024]
    if not found:
        raise SystemExit(f"nenhuma base de cookies em {profile}")
    # Bases com dados primeiro (Default e Partitions tendem a ser maiores que stubs).
    return sorted(found, key=lambda path: path.stat().st_size, reverse=True)


def read_cookies(profile: Path, domain: str, profile_name: str | None = None) -> list[dict]:
    keys = candidate_keys()
    cookies: dict[tuple[str, str], dict] = {}

    for db_path in find_cookie_databases(profile, profile_name):
        with tempfile.TemporaryDirectory() as tmp:
            # O navegador mantem a base aberta; uma copia evita lock.
            copy = Path(tmp) / "Cookies"
            try:
                shutil.copy2(db_path, copy)
            except OSError:
                continue
            for suffix in ("-wal", "-shm"):
                extra = Path(str(db_path) + suffix)
                if extra.is_file():
                    shutil.copy2(extra, Path(str(copy) + suffix))

            try:
                con = sqlite3.connect(f"file:{copy}?mode=ro", uri=True)
                con.row_factory = sqlite3.Row
                rows = con.execute(
                    """
                    SELECT host_key, name, value, encrypted_value, path,
                           is_secure, is_httponly, expires_utc
                    FROM cookies
                    WHERE host_key LIKE ?
                    ORDER BY host_key, name
                    """,
                    (f"%{domain}%",),
                ).fetchall()
                con.close()
            except sqlite3.Error:
                continue

        for row in rows:
            value = row["value"] or decrypt_value(row["encrypted_value"], keys)
            if value is None:
                continue
            key = (row["host_key"], row["name"])
            existing = cookies.get(key)
            if existing and len(existing["value"]) >= len(value):
                continue
            cookies[key] = {
                "host": row["host_key"],
                "name": row["name"],
                "value": value,
                "path": row["path"],
                "secure": bool(row["is_secure"]),
                "http_only": bool(row["is_httponly"]),
                "fonte": str(db_path),
            }

    return [cookies[key] for key in sorted(cookies)]


RELEVANT_COOKIES = ("substack.sid", "substack.lli", "connect.sid")


def save_config(cookies: list[dict], publication: str | None, user_id: str | None) -> int:
    """Grava os cookies de sessao na config da ferramenta (arquivo 600)."""
    selected = {c["name"]: c["value"] for c in cookies if c["name"] in RELEVANT_COOKIES}
    if "substack.sid" not in selected:
        print("cookie substack.sid nao encontrado: a sessao pode nao estar logada", file=sys.stderr)
        return 1

    config_path = Path(os.environ.get("SUBSTACK_CONFIG", "~/.config/terras-substack/config.json")).expanduser()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    os.chmod(config_path.parent, 0o700)
    config: dict = {}
    if config_path.is_file():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except ValueError:
            config = {}
    if publication:
        config["publication"] = publication
    if user_id:
        config["user_id"] = int(user_id)
    stored = dict(config.get("cookies") or {})
    stored.update(selected)
    config["cookies"] = stored
    config.setdefault("posts_dir", "~/Documents/Diversos/substack")

    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    os.chmod(config_path, 0o600)
    print(f"config salva em {config_path} (mode 600)")
    print("cookies gravados:", ", ".join(sorted(selected)))
    if not config.get("publication"):
        print("falta o campo 'publication': rode `terras_substack.py publications` para descobrir a URL")
    if not config.get("user_id"):
        print("falta o campo 'user_id': rode `terras_substack.py whoami`")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("domain", help="dominio a filtrar, ex.: substack.com")
    parser.add_argument("--profile", help="caminho do perfil do navegador")
    parser.add_argument(
        "--profile-name",
        help="subpasta do perfil (Default, session/Partitions/x). Sem isso, varre o perfil inteiro.",
    )
    parser.add_argument("--json", action="store_true", help="saida JSON")
    parser.add_argument("--cookie-header", action="store_true", help="saida pronta para o header Cookie")
    parser.add_argument("--value", metavar="NOME", help="imprime apenas o valor do cookie com esse nome")
    parser.add_argument("--save-config", action="store_true", help="salva os cookies na config da ferramenta (mode 600)")
    parser.add_argument("--publication", help="publicacao a gravar na config junto com --save-config")
    parser.add_argument("--user-id", help="user_id a gravar na config junto com --save-config")
    args = parser.parse_args()

    profile = find_profile(args.profile)
    cookies = read_cookies(profile, args.domain, args.profile_name)
    if not cookies:
        print(f"nenhum cookie encontrado para {args.domain} em {profile}", file=sys.stderr)
        return 1

    if args.save_config:
        return save_config(cookies, args.publication, args.user_id)

    if args.value:
        for cookie in cookies:
            if cookie["name"] == args.value:
                print(cookie["value"])
                return 0
        print(f"cookie {args.value} nao encontrado", file=sys.stderr)
        return 1

    if args.cookie_header:
        print("; ".join(f"{c['name']}={c['value']}" for c in cookies))
        return 0

    if args.json:
        json.dump(cookies, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    for cookie in cookies:
        size = len(cookie["value"])
        preview = cookie["value"][:12].replace("\n", "")
        flags = "".join(["S" if cookie["secure"] else "-", "H" if cookie["http_only"] else "-"])
        print(f"{cookie['host']:<20} {cookie['name']:<28} {size:>6}B [{flags}] {preview}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

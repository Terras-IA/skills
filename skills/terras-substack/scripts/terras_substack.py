#!/usr/bin/env python3
"""Publica e gerencia posts na Substack pela API interna do editor.

Sem dependencias externas alem de `requests` (ja presente no Python do sistema).
Nao existe API publica de escrita na Substack: tudo aqui usa os mesmos endpoints
que o editor web usa, autenticados pelo cookie de sessao `substack.sid`.

Configuracao em ~/.config/terras-substack/config.json (mode 600):
    {
      "publication": "https://minhapublicacao.substack.com",
      "user_id": 123456,
      "cookies": {"substack.sid": "...", "substack.lli": "..."},
      "posts_dir": "~/Documents/Diversos/substack"
    }

Variaveis de ambiente sobrepoem o arquivo: SUBSTACK_PUBLICATION, SUBSTACK_SID,
SUBSTACK_USER_ID, SUBSTACK_COOKIES (string "a=1; b=2").

Comandos de escrita nunca publicam por acidente: `publish` exige --yes e envia
apenas para a web por padrao (o e-mail so sai com --send-email).
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("requests ausente: instale python3-requests ou rode dentro de um venv com requests")

API_BASE = "https://substack.com/api/v1"
CONFIG_PATH = Path(os.environ.get("SUBSTACK_CONFIG", "~/.config/terras-substack/config.json")).expanduser()
DEFAULT_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36"
)

EXIT_USAGE = 2
EXIT_AUTH = 3
EXIT_NOT_FOUND = 4
EXIT_API = 5


class SubstackError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, exit_code: int = EXIT_API):
        super().__init__(message)
        self.status = status
        self.exit_code = exit_code


# --------------------------------------------------------------------------
# Markdown -> ProseMirror (schema do editor da Substack)
# --------------------------------------------------------------------------

INLINE_RE = re.compile(
    r"""
      (?P<code>`(?P<code_body>[^`]+)`)
    | (?P<image>!\[(?P<img_alt>[^\]]*)\]\((?P<img_src>[^)\s]+)(?:\s+"(?P<img_title>[^"]*)")?\))
    | (?P<link>\[(?P<link_text>[^\]]+)\]\((?P<link_href>[^)\s]+)\))
    | (?P<bolditalic>\*\*\*(?P<bi_body>[^*]+)\*\*\*)
    | (?P<bold>\*\*(?P<bold_body>[^*]+)\*\*)
    | (?P<strike>~~(?P<strike_body>[^~]+)~~)
    | (?P<italic>\*(?P<it_body>[^*\n]+)\*)
    | (?P<italic_us>(?<![A-Za-z0-9_])_(?P<itus_body>[^_\n]+)_(?![A-Za-z0-9_]))
    """,
    re.VERBOSE,
)

DIRECTIVE_RE = re.compile(r"^:::\s*(?P<name>[a-zA-Z-]+)\s*(?P<rest>.*)$")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.*)$")
ULIST_RE = re.compile(r"^(?P<indent>\s*)[-*+]\s+(?P<text>.*)$")
OLIST_RE = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)[.)]\s+(?P<text>.*)$")
IMAGE_ONLY_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+\"(?P<title>[^\"]*)\")?\)\s*$")
HR_RE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")


def _text(value: str, marks: list[dict] | None = None) -> dict:
    node: dict[str, Any] = {"type": "text", "text": value}
    if marks:
        node["marks"] = marks
    return node


def parse_inline(text: str, marks: list[dict] | None = None) -> list[dict]:
    """Converte formatacao inline do markdown em nos `text` com marks."""
    marks = list(marks or [])
    nodes: list[dict] = []
    pos = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > pos:
            plain = text[pos : match.start()]
            if plain:
                nodes.append(_text(plain, marks))
        kind = match.lastgroup
        if kind == "code":
            nodes.append(_text(match.group("code_body"), marks + [{"type": "code"}]))
        elif kind == "image":
            nodes.append(
                _text(
                    match.group("img_alt") or match.group("img_src"),
                    marks + [{"type": "link", "attrs": {"href": match.group("img_src")}}],
                )
            )
        elif kind == "link":
            link_mark = {"type": "link", "attrs": {"href": match.group("link_href")}}
            nodes.extend(parse_inline(match.group("link_text"), marks + [link_mark]))
        elif kind == "bolditalic":
            nodes.extend(parse_inline(match.group("bi_body"), marks + [{"type": "strong"}, {"type": "em"}]))
        elif kind == "bold":
            nodes.extend(parse_inline(match.group("bold_body"), marks + [{"type": "strong"}]))
        elif kind == "strike":
            nodes.extend(parse_inline(match.group("strike_body"), marks + [{"type": "strikethrough"}]))
        elif kind == "italic":
            nodes.extend(parse_inline(match.group("it_body"), marks + [{"type": "em"}]))
        elif kind == "italic_us":
            nodes.extend(parse_inline(match.group("itus_body"), marks + [{"type": "em"}]))
        pos = match.end()
    if pos < len(text):
        tail = text[pos:]
        if tail:
            nodes.append(_text(tail, marks))
    return nodes


def _paragraph(lines: list[str]) -> dict:
    return {"type": "paragraph", "content": parse_inline(" ".join(line.strip() for line in lines))}


def _image_node(src: str, alt: str | None = None, caption: str | None = None, title: str | None = None) -> dict:
    content: list[dict] = [
        {
            "type": "image2",
            "attrs": {
                "src": src,
                "srcNoWatermark": None,
                "fullscreen": False,
                "imageSize": "normal",
                "height": 819,
                "width": 1456,
                "resizeWidth": 728,
                "bytes": None,
                "alt": alt,
                "title": title,
                "type": None,
                "href": None,
                "belowTheFold": False,
                "topImage": False,
                "internalRedirect": None,
                "isProcessing": False,
                "align": None,
                "offset": False,
            },
        }
    ]
    if caption:
        content.append({"type": "caption", "content": parse_inline(caption)})
    return {"type": "captionedImage", "content": content}


def _list_tree(lines: list[tuple[int, str, bool]]) -> list[dict]:
    """Monta listas (possivelmente aninhadas) a partir de (indent, texto, ordenada)."""
    root: list[dict] = []
    stack: list[tuple[int, dict]] = []  # (indent, lista)

    for indent, text, ordered in lines:
        node_type = "ordered_list" if ordered else "bullet_list"
        item = {"type": "list_item", "content": [{"type": "paragraph", "content": parse_inline(text)}]}
        while stack and indent < stack[-1][0]:
            stack.pop()
        if stack and indent == stack[-1][0] and stack[-1][1]["type"] == node_type:
            stack[-1][1]["content"].append(item)
            continue
        new_list = {"type": node_type, "content": [item]}
        if stack and indent > stack[-1][0]:
            parent_items = stack[-1][1]["content"]
            parent_items[-1]["content"].append(new_list)
        else:
            root.append(new_list)
        stack.append((indent, new_list))
    return root


def markdown_to_doc(markdown_text: str) -> dict:
    """Converte um subconjunto de markdown no doc ProseMirror do editor."""
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    blocks: list[dict] = []
    i = 0
    pending_caption: str | None = None

    def flush_caption() -> None:
        nonlocal pending_caption
        if pending_caption and blocks and blocks[-1].get("type") == "captionedImage":
            content = blocks[-1]["content"]
            caption_node = {"type": "caption", "content": parse_inline(pending_caption)}
            if len(content) > 1 and content[-1].get("type") == "caption":
                content[-1] = caption_node
            else:
                content.append(caption_node)
        pending_caption = None

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            flush_caption()
            i += 1
            continue

        # Bloco de codigo
        fence = re.match(r"^\s*(```|~~~)\s*(?P<lang>[A-Za-z0-9+#._-]*)\s*$", line)
        if fence:
            marker = fence.group(1)
            lang = fence.group("lang") or None
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(marker):
                body.append(lines[i])
                i += 1
            i += 1  # consome o fechamento
            node: dict[str, Any] = {"type": "codeBlock", "content": [_text("\n".join(body))]}
            if lang:
                node["attrs"] = {"language": lang}
            blocks.append(node)
            flush_caption()
            continue

        # Diretivas ::: nome args
        directive = DIRECTIVE_RE.match(line)
        if directive:
            name = directive.group("name").lower()
            rest = directive.group("rest").strip()
            i += 1
            if name == "paywall":
                blocks.append({"type": "paywall"})
            elif name in ("subscribe", "subscribe-widget"):
                message = rest or "Assine para receber os proximos posts e apoiar este trabalho."
                blocks.append(
                    {
                        "type": "subscribeWidget",
                        "attrs": {"url": "%%checkout_url%%", "text": "Assine", "language": "pt"},
                        "content": [{"type": "ctaCaption", "content": parse_inline(message)}],
                    }
                )
            elif name == "button":
                text_part, _, href = rest.partition("|")
                blocks.append({"type": "button", "attrs": {"href": href.strip() or "#", "text": text_part.strip() or "Saiba mais"}})
            elif name == "caption":
                pending_caption = rest
            elif name in ("pullquote", "callout", "calloutBlock"):
                inner: list[str] = []
                while i < len(lines) and not lines[i].strip().startswith(":::"):
                    inner.append(lines[i])
                    i += 1
                i += 1
                paragraphs = [p for p in _parse_blocks("\n".join(inner)) if p.get("type") == "paragraph"] or [
                    {"type": "paragraph", "content": []}
                ]
                node_type = "pullquote" if name == "pullquote" else "calloutBlock"
                node = {"type": node_type, "content": paragraphs}
                if node_type == "pullquote":
                    node["attrs"] = {"align": None, "color": None}
                blocks.append(node)
            elif name in ("divider", "hr"):
                blocks.append({"type": "horizontal_rule"})
            else:
                raise SubstackError(f"diretiva ::: desconhecida: {name}")
            flush_caption()
            continue

        # Titulos
        heading = HEADING_RE.match(line)
        if heading:
            flush_caption()
            level = len(heading.group("hashes"))
            blocks.append({"type": "heading", "attrs": {"level": level}, "content": parse_inline(heading.group("text"))})
            i += 1
            continue

        # Regua horizontal
        if HR_RE.match(line):
            flush_caption()
            blocks.append({"type": "horizontal_rule"})
            i += 1
            continue

        # Citacao
        if line.lstrip().startswith(">"):
            flush_caption()
            quoted: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner_blocks = _parse_blocks("\n".join(quoted)) or [{"type": "paragraph", "content": []}]
            blocks.append({"type": "blockquote", "content": inner_blocks})
            continue

        # Listas (com aninhamento por indentacao)
        if ULIST_RE.match(line) or OLIST_RE.match(line):
            flush_caption()
            items: list[tuple[int, str, bool]] = []
            while i < len(lines):
                current = lines[i]
                ul = ULIST_RE.match(current)
                ol = OLIST_RE.match(current)
                if not (ul or ol):
                    if not current.strip():
                        break
                    # continuacao do item anterior
                    if items:
                        indent, text, ordered = items[-1]
                        items[-1] = (indent, f"{text} {current.strip()}", ordered)
                        i += 1
                        continue
                    break
                match = ul or ol
                items.append((len(match.group("indent")), match.group("text"), bool(ol)))
                i += 1
            blocks.extend(_list_tree(items))
            continue

        # Imagem isolada na linha (com legenda opcional na linha seguinte iniciando por "^ ")
        image_only = IMAGE_ONLY_RE.match(line)
        if image_only:
            flush_caption()
            caption = None
            if i + 1 < len(lines) and lines[i + 1].lstrip().startswith("^ "):
                caption = lines[i + 1].lstrip()[2:].strip()
                i += 1
            blocks.append(
                _image_node(
                    image_only.group("src"),
                    alt=image_only.group("alt") or None,
                    caption=caption,
                    title=image_only.group("title") or None,
                )
            )
            i += 1
            continue

        # Paragrafo
        para: list[str] = []
        while i < len(lines):
            current = lines[i]
            if not current.strip():
                break
            if (
                HEADING_RE.match(current)
                or HR_RE.match(current)
                or DIRECTIVE_RE.match(current)
                or ULIST_RE.match(current)
                or OLIST_RE.match(current)
                or IMAGE_ONLY_RE.match(current)
                or re.match(r"^\s*(```|~~~)", current)
                or current.lstrip().startswith(">")
            ):
                break
            para.append(current)
            i += 1
        if para:
            flush_caption()
            blocks.append(_paragraph(para))

    flush_caption()
    return {"type": "doc", "content": blocks}


def _parse_blocks(markdown_text: str) -> list[dict]:
    return markdown_to_doc(markdown_text)["content"]


# --------------------------------------------------------------------------
# ProseMirror -> Markdown (para conferir rascunhos existentes)
# --------------------------------------------------------------------------

def _inline_to_markdown(nodes: Iterable[dict]) -> str:
    out: list[str] = []
    for node in nodes or []:
        if node.get("type") == "hard_break":
            out.append("\n")
            continue
        text = node.get("text", "")
        for mark in node.get("marks", []) or []:
            kind = mark.get("type")
            if kind == "strong":
                text = f"**{text}**"
            elif kind == "em":
                text = f"*{text}*"
            elif kind == "code":
                text = f"`{text}`"
            elif kind == "strikethrough":
                text = f"~~{text}~~"
            elif kind == "link":
                href = (mark.get("attrs") or {}).get("href", "")
                text = f"[{text}]({href})"
        out.append(text)
    return "".join(out)


def doc_to_markdown(node: dict, depth: int = 0) -> str:
    """Converte o doc ProseMirror de volta em markdown (nos desconhecidos viram comentario)."""
    node_type = node.get("type")
    content = node.get("content") or []
    attrs = node.get("attrs") or {}

    if node_type == "doc":
        return "\n\n".join(filter(None, (doc_to_markdown(child, depth) for child in content)))
    if node_type == "paragraph":
        return _inline_to_markdown(content)
    if node_type == "heading":
        level = attrs.get("level", 2)
        return f"{'#' * level} {_inline_to_markdown(content)}"
    if node_type == "text":
        return _inline_to_markdown([node])
    if node_type == "bullet_list":
        return "\n".join(
            f"{'  ' * depth}- " + doc_to_markdown(item, depth + 1).replace("\n", f"\n{'  ' * (depth + 1)}")
            for item in content
        )
    if node_type == "ordered_list":
        return "\n".join(
            f"{'  ' * depth}{index + 1}. "
            + doc_to_markdown(item, depth + 1).replace("\n", f"\n{'  ' * (depth + 1)}")
            for index, item in enumerate(content)
        )
    if node_type == "list_item":
        return "\n".join(filter(None, (doc_to_markdown(child, depth) for child in content)))
    if node_type == "blockquote":
        inner = "\n\n".join(filter(None, (doc_to_markdown(child, depth) for child in content)))
        return "\n".join(f"> {line}" for line in inner.split("\n"))
    if node_type == "codeBlock":
        language = attrs.get("language") or ""
        return f"```{language}\n{_inline_to_markdown(content)}\n```"
    if node_type == "horizontal_rule":
        return "---"
    if node_type == "captionedImage":
        image = next((child for child in content if child.get("type") == "image2"), None)
        caption = next((child for child in content if child.get("type") == "caption"), None)
        image_attrs = (image or {}).get("attrs") or {}
        alt = image_attrs.get("alt") or ""
        src = image_attrs.get("src") or ""
        out = f"![{alt}]({src})"
        if caption:
            out += f"\n^ {doc_to_markdown(caption, depth)}"
        return out
    if node_type in ("caption", "ctaCaption"):
        return _inline_to_markdown(content)
    if node_type == "paywall":
        return "::: paywall"
    if node_type == "subscribeWidget":
        caption = next((child for child in content if child.get("type") == "ctaCaption"), None)
        text = doc_to_markdown(caption, depth) if caption else ""
        return f"::: subscribe {text}".rstrip()
    if node_type == "button":
        return f"::: button {attrs.get('text', '')} | {attrs.get('href', '')}"
    if node_type in ("pullquote", "calloutBlock"):
        name = "pullquote" if node_type == "pullquote" else "callout"
        inner = "\n\n".join(filter(None, (doc_to_markdown(child, depth) for child in content)))
        return f"::: {name}\n{inner}\n:::"
    if node_type in ("footnote", "footnoteAnchor"):
        return f"<!-- footnote nao suportada no markdown: {node_type} -->"
    return f"<!-- no nao convertido: {node_type} -->"


# --------------------------------------------------------------------------
# Frontmatter + configuracao
# --------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    if lines[0].strip() != "---":
        return {}, text
    meta: dict[str, Any] = {}
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[index + 1 :])
        match = re.match(r"^(?P<key>[A-Za-z_][\w-]*):\s*(?P<value>.*)$", line)
        if not match:
            continue
        key = match.group("key").lower()
        value: Any = match.group("value").strip()
        if value.startswith("[") and value.endswith("]"):
            value = [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
        elif "," in value and key in {"tags", "palavras-chave", "keywords"}:
            value = [item.strip().strip("'\"") for item in value.split(",") if item.strip()]
        else:
            value = value.strip("'\"")
        meta[key] = value
    return {}, text


def load_config() -> dict[str, Any]:
    config: dict[str, Any] = {}
    if CONFIG_PATH.is_file():
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    elif CONFIG_PATH.exists():
        raise SubstackError(f"config invalida: {CONFIG_PATH} nao e um arquivo")

    env_map = {
        "publication": "SUBSTACK_PUBLICATION",
        "user_id": "SUBSTACK_USER_ID",
        "posts_dir": "SUBSTACK_POSTS_DIR",
    }
    for key, env_name in env_map.items():
        if os.environ.get(env_name):
            config[key] = os.environ[env_name]

    cookies = dict(config.get("cookies") or {})
    if os.environ.get("SUBSTACK_SID"):
        cookies["substack.sid"] = os.environ["SUBSTACK_SID"]
    if os.environ.get("SUBSTACK_COOKIES"):
        for pair in os.environ["SUBSTACK_COOKIES"].split(";"):
            name, _, value = pair.strip().partition("=")
            if name:
                cookies[name] = value
    config["cookies"] = cookies
    if config.get("user_id"):
        config["user_id"] = int(config["user_id"])
    return config


class Client:
    """Cliente HTTP fino sobre os endpoints internos do editor."""

    def __init__(self, config: dict[str, Any], dry_run: bool = False, timeout: int = 30, allow_missing: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.timeout = timeout
        configured_publication = (config.get("publication") or "").rstrip("/")
        self.configured = bool(configured_publication)
        # Sem publicacao configurada, comandos offline/dry-run ainda mostram a URL
        # de destino; comandos reais falham em `pub_api`.
        self.publication = configured_publication or ("https://SEU-SUBDOMINIO.substack.com" if allow_missing else "")

        self.session = requests.Session()
        headers = {"User-Agent": DEFAULT_UA, "Accept": "application/json", "Content-Type": "application/json"}
        if configured_publication:
            headers["Origin"] = configured_publication
            headers["Referer"] = f"{configured_publication}/publish/post"
        self.session.headers.update(headers)
        for name, value in (config.get("cookies") or {}).items():
            self.session.cookies.set(name, value)

    @property
    def pub_api(self) -> str:
        if not self.publication:
            raise SubstackError(
                "publication nao configurada: defina em "
                f"{CONFIG_PATH} ou na variavel SUBSTACK_PUBLICATION "
                "(rode `publications` para descobrir a URL)",
                exit_code=EXIT_USAGE,
            )
        return f"{self.publication}/api/v1"

    def has_session(self) -> bool:
        return bool(self.session and self.session.cookies.get("substack.sid"))

    def _check(self, response: requests.Response) -> Any:
        if response.status_code in (401, 403):
            raise SubstackError(
                "sessao invalida ou expirada (HTTP "
                f"{response.status_code}). Renove o cookie substack.sid: "
                "Chrome > substack.com > DevTools (F12) > Application > Cookies > copie o valor de "
                "'substack.sid' e salve em "
                f"{CONFIG_PATH} (chave cookies).",
                status=response.status_code,
                exit_code=EXIT_AUTH,
            )
        if response.status_code == 404:
            raise SubstackError(f"nao encontrado (HTTP 404): {response.url}", status=404, exit_code=EXIT_NOT_FOUND)
        if not response.ok:
            body = response.text[:400].replace("\n", " ")
            raise SubstackError(f"HTTP {response.status_code}: {body}", status=response.status_code)
        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text[:2000]}

    def request(self, method: str, url: str, skip_dry_run: bool = False, **kwargs) -> Any:
        if self.dry_run and not skip_dry_run:
            return {
                "dry_run": True,
                "method": method,
                "url": url,
                "json": kwargs.get("json"),
                "data": "<binario>" if kwargs.get("data") else None,
            }
        if not self.publication:
            raise SubstackError(
                "publication nao configurada: defina em "
                f"{CONFIG_PATH} ou na variavel SUBSTACK_PUBLICATION",
                exit_code=EXIT_USAGE,
            )
        response = self.session.request(method, url, timeout=self.timeout, **kwargs)
        return self._check(response)

    # -- leitura -----------------------------------------------------------
    def profile(self) -> dict:
        return self.request("GET", f"{API_BASE}/user/profile/self")

    def publications(self) -> list[dict]:
        profile = self.profile()
        publications = []
        for entry in profile.get("publicationUsers") or []:
            publication = entry.get("publication")
            if not publication:
                continue
            subdomain = publication.get("subdomain")
            domain = publication.get("custom_domain")
            url = f"https://{domain}" if domain else f"https://{subdomain}.substack.com"
            publications.append(
                {
                    "id": publication.get("id"),
                    "name": publication.get("name"),
                    "subdomain": subdomain,
                    "custom_domain": domain,
                    "url": url,
                    "is_primary": entry.get("is_primary", False),
                    "role": entry.get("role"),
                }
            )
        return publications

    def drafts(self, limit: int = 20) -> dict:
        data = self.request("GET", f"{self.pub_api}/drafts", params={"limit": limit})
        return data if isinstance(data, dict) else {"posts": data or []}

    def published(self, limit: int = 20) -> dict:
        # A API exige ordenacao explicita aqui; sem order_by ela responde
        # 400 Invalid value, como se os parametros estivessem errados.
        return self.request(
            "GET",
            f"{self.pub_api}/post_management/published",
            params={
                "limit": limit,
                "offset": 0,
                "order_by": "post_date",
                "order_direction": "desc",
            },
        )

    def draft(self, draft_id: int) -> dict:
        return self.request("GET", f"{self.pub_api}/drafts/{draft_id}")

    # -- escrita -----------------------------------------------------------
    def create_draft(self, payload: dict) -> dict:
        return self.request("POST", f"{self.pub_api}/drafts", json=payload)

    def update_draft(self, draft_id: int, payload: dict) -> dict:
        return self.request("PUT", f"{self.pub_api}/drafts/{draft_id}", json=payload)

    def prepublish(self, draft_id: int) -> dict:
        return self.request("GET", f"{self.pub_api}/drafts/{draft_id}/prepublish")

    def publish(self, draft_id: int, send_email: bool = False, share: bool = False) -> dict:
        # O rascunho e criado com should_send_email=false. Ao pedir envio,
        # liga o campo antes de publicar para o e-mail nao sair em silencio.
        if send_email and not self.dry_run:
            self.update_draft(draft_id, {"should_send_email": True})
        return self.request(
            "POST",
            f"{self.pub_api}/drafts/{draft_id}/publish",
            json={"send": send_email, "share_automatically": share},
        )

    def schedule(self, draft_id: int, when: datetime) -> dict:
        return self.request(
            "POST",
            f"{self.pub_api}/drafts/{draft_id}/scheduled_release",
            json={"trigger_at": when.astimezone(timezone.utc).isoformat()},
        )

    def unschedule(self, draft_id: int) -> dict:
        return self.request("DELETE", f"{self.pub_api}/drafts/{draft_id}/scheduled_release")

    def delete_draft(self, draft_id: int) -> dict:
        return self.request("DELETE", f"{self.pub_api}/drafts/{draft_id}")

    def upload_image(self, path: Path) -> dict:
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return self.request(
            "POST",
            f"{self.pub_api}/image",
            data={"image": f"data:{mime};base64,{encoded}"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    def tags(self) -> list[dict]:
        return self.request("GET", f"{self.pub_api}/publication/post-tag") or []

    def ensure_tag(self, name: str) -> int | str:
        # Em dry-run nao ha lista real de tags nem id de tag criada: devolver um
        # id simbolico deixa a simulacao mostrar a chamada que prende a tag.
        if self.dry_run:
            return f"<id-da-tag:{name}>"
        for tag in self.tags():
            if (tag.get("name") or "").strip().lower() == name.strip().lower():
                return tag["id"]
        created = self.request("POST", f"{self.pub_api}/publication/post-tag", json={"name": name})
        return created["id"]

    def set_tags(self, post_id: int, names: list[str]) -> list[dict]:
        results = []
        for name in names:
            tag_id = self.ensure_tag(name)
            results.append(self.request("POST", f"{self.pub_api}/post/{post_id}/tag/{tag_id}"))
        return results


# --------------------------------------------------------------------------
# Payload de rascunho
# --------------------------------------------------------------------------

def build_payload(config: dict, meta: dict, doc: dict, defaults: dict, strict_user: bool = True) -> dict:
    user_id = config.get("user_id") or defaults.get("user_id")
    if not user_id and strict_user:
        raise SubstackError(
            "user_id desconhecido: rode `terras_substack.py whoami` e salve o id na config",
            exit_code=EXIT_USAGE,
        )
    audience = meta.get("audience") or defaults.get("audience") or "everyone"
    payload = {
        "draft_title": meta.get("title") or defaults.get("title") or "",
        "draft_subtitle": meta.get("subtitle") or meta.get("description") or defaults.get("subtitle") or "",
        "draft_body": json.dumps(doc, ensure_ascii=False),
        "draft_bylines": [{"id": int(user_id or 0), "is_guest": False}],
        "audience": audience,
        "write_comment_permissions": meta.get("comments") or audience,
        "draft_section_id": None,
        "section_chosen": True,
        # Cinto e suspensorio: o rascunho nasce configurado para NAO enviar e-mail,
        # mesmo se a publicacao for disparada pela interface depois.
        "should_send_email": False,
    }
    if meta.get("section_id"):
        payload["draft_section_id"] = int(meta["section_id"])
    return payload


def load_post_file(path: Path) -> tuple[dict, dict]:
    raw = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(raw)
    doc = markdown_to_doc(body)
    if not meta.get("title"):
        first_heading = next((node for node in doc["content"] if node.get("type") == "heading" and node["attrs"]["level"] == 1), None)
        if first_heading:
            meta["title"] = "".join(child.get("text", "") for child in first_heading.get("content", []))
            doc["content"] = [node for node in doc["content"] if node is not first_heading]
    return meta, doc


def browser_snippet(publication: str, payload: dict, draft_id: int | None = None, action: str = "draft") -> str:
    if action == "draft":
        url = f"{publication}/api/v1/drafts"
        method = "POST"
    elif action == "publish":
        url = f"{publication}/api/v1/drafts/{draft_id}/publish"
        method = "POST"
        payload = {"send": False, "share_automatically": False}
    elif action == "prepublish":
        url = f"{publication}/api/v1/drafts/{draft_id}/prepublish"
        method = "GET"
        payload = None
    else:
        raise SubstackError(f"acao desconhecida para o snippet: {action}", exit_code=EXIT_USAGE)

    body = f",\n    body: JSON.stringify({json.dumps(payload, ensure_ascii=False, indent=2)})" if payload else ""
    return f"""// Rode com a aba logada em {publication} (browser-use: tab.playwright.evaluate)
(async () => {{
  const res = await fetch("{url}", {{
    method: "{method}",
    credentials: "include",
    headers: {{ "Content-Type": "application/json" }}{body}
  }});
  return {{ status: res.status, body: await res.json().catch(() => null) }};
}})()"""


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print(data: Any, as_text: bool = False) -> None:
    if as_text and isinstance(data, str):
        print(data)
        return
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="terras_substack.py",
        description="Publica e gerencia posts na Substack pela API interna do editor.",
    )
    parser.add_argument("--dry-run", action="store_true", help="mostra a requisicao sem executar")
    parser.add_argument("--json", action="store_true", help="saida JSON (padrao)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="valida configuracao e sessao")
    sub.add_parser("whoami", help="perfil do usuario e publicacoes vinculadas")
    sub.add_parser("publications", help="lista publicacoes")

    drafts = sub.add_parser("drafts", help="lista rascunhos")
    drafts.add_argument("--limit", type=int, default=20)

    published = sub.add_parser("published", help="lista posts publicados")
    published.add_argument("--limit", type=int, default=20)

    get_draft = sub.add_parser("get-draft", help="detalhe de um rascunho")
    get_draft.add_argument("draft_id", type=int)
    get_draft.add_argument("--markdown", action="store_true", help="converte o corpo para markdown")

    md2json = sub.add_parser("md2json", help="converte markdown em doc ProseMirror")
    md2json.add_argument("arquivo", type=Path)
    md2json.add_argument("--doc-only", action="store_true", help="imprime apenas o doc (sem frontmatter)")

    payload_cmd = sub.add_parser("payload", help="gera o payload do rascunho para inspecao")
    payload_cmd.add_argument("arquivo", type=Path)

    create = sub.add_parser("create-draft", help="cria rascunho a partir de um markdown")
    create.add_argument("arquivo", type=Path)
    create.add_argument("--title")
    create.add_argument("--subtitle")
    create.add_argument("--audience", choices=["everyone", "only_paid", "founding", "only_free"])
    create.add_argument("--tags", help="lista separada por virgulas")
    create.add_argument("--prepublish", action="store_true", help="roda o prepublish em seguida")

    update = sub.add_parser("update-draft", help="substitui o corpo de um rascunho")
    update.add_argument("draft_id", type=int)
    update.add_argument("arquivo", type=Path)

    prepublish = sub.add_parser("prepublish", help="valida o rascunho no servidor")
    prepublish.add_argument("draft_id", type=int)

    publish = sub.add_parser("publish", help="publica de verdade (exige --yes)")
    publish.add_argument("draft_id", type=int)
    publish.add_argument("--yes", action="store_true", help="confirma a publicacao")
    publish.add_argument("--send-email", action="store_true", help="dispara o e-mail para os assinantes")
    publish.add_argument("--share", action="store_true", help="compartilha automaticamente")

    schedule = sub.add_parser("schedule", help="agenda a publicacao")
    schedule.add_argument("draft_id", type=int)
    schedule.add_argument("--at", required=True, help="ISO 8601, ex.: 2026-09-20T09:00:00-03:00")
    schedule.add_argument("--yes", action="store_true")

    unschedule = sub.add_parser("unschedule", help="cancela o agendamento")
    unschedule.add_argument("draft_id", type=int)

    unpublish = sub.add_parser("unpublish", help="despublica (remove do ar)")
    unpublish.add_argument("draft_id", type=int)
    unpublish.add_argument("--yes", action="store_true")

    delete = sub.add_parser("delete-draft", help="apaga um rascunho")
    delete.add_argument("draft_id", type=int)
    delete.add_argument("--yes", action="store_true")

    image = sub.add_parser("upload-image", help="envia imagem e devolve a URL")
    image.add_argument("arquivo", type=Path)

    tags = sub.add_parser("tags", help="lista tags da publicacao")

    set_tags = sub.add_parser("set-tags", help="aplica tags a um post")
    set_tags.add_argument("post_id", type=int)
    set_tags.add_argument("nomes", nargs="+")

    snippet = sub.add_parser("browser-payload", help="imprime JS para publicar pela aba logada")
    snippet.add_argument("arquivo", type=Path)
    snippet.add_argument("--action", choices=["draft", "prepublish", "publish"], default="draft")
    snippet.add_argument("--draft-id", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config = load_config()

    try:
        client = Client(
            config,
            dry_run=args.dry_run,
            allow_missing=args.dry_run
            or args.command in {"check", "whoami", "publications", "md2json", "payload", "browser-payload"},
        )
    except SubstackError as error:
        print(f"erro: {error}", file=sys.stderr)
        return error.exit_code

    def need_session() -> None:
        if args.dry_run:
            return
        if not client.has_session():
            raise SubstackError(
                "cookie substack.sid ausente. Pegue em Chrome > substack.com > DevTools (F12) > "
                f"Application > Cookies > substack.sid e salve em {CONFIG_PATH}.",
                exit_code=EXIT_AUTH,
            )

    try:
        command = args.command

        if command == "check":
            state: dict[str, Any] = {
                "config": str(CONFIG_PATH),
                "config_exists": CONFIG_PATH.is_file(),
                "publication": config.get("publication") or None,
                "publication_configurada": client.configured,
                "session_cookie": client.has_session(),
                "user_id": config.get("user_id"),
            }
            if state["session_cookie"]:
                profile = client.profile()
                state["autenticado"] = True
                state["usuario"] = {"id": profile.get("id"), "nome": profile.get("name")}
                state["publicacoes"] = client.publications()
            else:
                state["autenticado"] = False
            faltando = []
            if not state["session_cookie"]:
                faltando.append("cookie substack.sid (ver references/credenciais.md)")
            if not state["publication_configurada"]:
                faltando.append("publication (rode `publications` ou crie a publicacao no editor)")
            if not state["user_id"]:
                faltando.append("user_id (rode `whoami`)")
            if faltando:
                state["proximo_passo"] = faltando
            _print(state)
            return 0 if state["session_cookie"] and state["publication_configurada"] else EXIT_AUTH

        if command == "whoami":
            need_session()
            profile = client.profile()
            _print(
                {
                    "id": profile.get("id"),
                    "nome": profile.get("name"),
                    "publicacoes": client.publications(),
                    "dica": "salve o id em user_id e a URL da publicacao em publication",
                }
            )
            return 0

        if command == "publications":
            need_session()
            _print(client.publications())
            return 0

        if command == "drafts":
            need_session()
            drafts = client.drafts(limit=args.limit)
            _print(
                [
                    {
                        "id": draft.get("id"),
                        "titulo": draft.get("draft_title") or draft.get("title"),
                        "slug": draft.get("slug"),
                        "atualizado": draft.get("draft_updated_at") or draft.get("updated_at"),
                        "post_date": draft.get("post_date"),
                        "publicado": draft.get("is_published"),
                    }
                    for draft in drafts.get("posts", [])
                ]
            )
            return 0

        if command == "published":
            need_session()
            data = client.published(limit=args.limit)
            posts = data.get("posts") if isinstance(data, dict) else data
            _print(
                [
                    {
                        "id": post.get("id"),
                        "titulo": post.get("title") or post.get("draft_title"),
                        "url": post.get("canonical_url"),
                        "data": post.get("post_date"),
                        "audiencia": post.get("audience"),
                    }
                    for post in (posts or [])
                ]
            )
            return 0

        if command == "get-draft":
            need_session()
            draft = client.draft(args.draft_id)
            body = draft.get("draft_body")
            if isinstance(body, str):
                try:
                    body = json.loads(body)
                except ValueError:
                    body = None
            out = {
                "id": draft.get("id"),
                "titulo": draft.get("draft_title") or draft.get("title"),
                "subtitulo": draft.get("draft_subtitle") or draft.get("subtitle"),
                "audiencia": draft.get("audience"),
                "post_date": draft.get("post_date"),
                "url": draft.get("canonical_url"),
                "nos": [node.get("type") for node in (body or {}).get("content", [])],
            }
            if args.markdown and body:
                out["markdown"] = doc_to_markdown(body)
            _print(out)
            return 0

        if command == "md2json":
            meta, doc = load_post_file(args.arquivo)
            _print(doc if args.doc_only else {"frontmatter": meta, "doc": doc})
            return 0

        if command == "payload":
            meta, doc = load_post_file(args.arquivo)
            payload = build_payload(config, meta, doc, {}, strict_user=False)
            preview = dict(payload)
            preview["draft_body"] = f"<doc ProseMirror com {len(doc['content'])} nos>"
            _print({"payload": preview, "doc": doc})
            return 0

        if command == "browser-payload":
            meta, doc = load_post_file(args.arquivo)
            payload = build_payload(config, meta, doc, {}, strict_user=False)
            publication = client.publication or "https://SEU-SUBDOMINIO.substack.com"
            print(browser_snippet(publication, payload, args.draft_id, args.action))
            return 0

        if command == "create-draft":
            need_session()
            meta, doc = load_post_file(args.arquivo)
            defaults = {"title": args.title, "subtitle": args.subtitle, "audience": args.audience}
            payload = build_payload(config, meta, doc, defaults, strict_user=not args.dry_run)
            draft = client.create_draft(payload)
            if args.dry_run:
                _print(draft)
                return 0
            draft_id = draft.get("id") if isinstance(draft, dict) else None
            result: dict[str, Any] = {
                "draft_id": draft_id,
                "titulo": payload["draft_title"],
                "nos": len(doc["content"]),
                "url_rascunho": f"{client.publication}/publish/post/{draft_id}" if draft_id else None,
                "publicado": False,
            }
            tags = args.tags or meta.get("tags")
            if isinstance(tags, list):
                tags = ",".join(tags)
            if tags and draft_id:
                result["tags"] = client.set_tags(draft_id, [name.strip() for name in tags.split(",") if name.strip()])
            if args.prepublish and draft_id:
                result["prepublish"] = client.prepublish(draft_id)
            _print(result)
            return 0

        if command == "update-draft":
            need_session()
            meta, doc = load_post_file(args.arquivo)
            payload = {"draft_body": json.dumps(doc, ensure_ascii=False)}
            if meta.get("title"):
                payload["draft_title"] = meta["title"]
            if meta.get("subtitle") or meta.get("description"):
                payload["draft_subtitle"] = meta.get("subtitle") or meta.get("description")
            _print(client.update_draft(args.draft_id, payload))
            return 0

        if command == "prepublish":
            need_session()
            _print(client.prepublish(args.draft_id))
            return 0

        if command == "publish":
            need_session()
            if not args.yes and not args.dry_run:
                raise SubstackError(
                    "publicacao bloqueada: confirme com --yes. "
                    "Por padrao o post vai para a web sem disparar e-mail; use --send-email para enviar.",
                    exit_code=EXIT_USAGE,
                )
            result = client.publish(args.draft_id, send_email=args.send_email, share=args.share)
            _print(
                {
                    "draft_id": args.draft_id,
                    "publicado": not args.dry_run,
                    "email_disparado": args.send_email if not args.dry_run else False,
                    "url": (result or {}).get("canonical_url") if isinstance(result, dict) else None,
                    "resposta": result,
                }
            )
            return 0

        if command == "schedule":
            need_session()
            if not args.yes and not args.dry_run:
                raise SubstackError("agendamento bloqueado: confirme com --yes", exit_code=EXIT_USAGE)
            when = datetime.fromisoformat(args.at)
            _print(client.schedule(args.draft_id, when))
            return 0

        if command == "unschedule":
            need_session()
            _print(client.unschedule(args.draft_id))
            return 0

        if command in ("unpublish", "delete-draft"):
            need_session()
            if not args.yes and not args.dry_run:
                raise SubstackError(f"{command} bloqueado: confirme com --yes", exit_code=EXIT_USAGE)
            _print(client.delete_draft(args.draft_id))
            return 0

        if command == "upload-image":
            need_session()
            _print(client.upload_image(args.arquivo))
            return 0

        if command == "tags":
            need_session()
            _print([{"id": tag.get("id"), "nome": tag.get("name")} for tag in client.tags()])
            return 0

        if command == "set-tags":
            need_session()
            _print(client.set_tags(args.post_id, args.nomes))
            return 0

    except SubstackError as error:
        print(f"erro: {error}", file=sys.stderr)
        return error.exit_code
    except requests.RequestException as error:
        print(f"erro de rede: {error}", file=sys.stderr)
        return EXIT_API

    raise SubstackError(f"comando nao implementado: {args.command}", exit_code=EXIT_USAGE)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Shared helpers for building the Spinoza Markdown archive."""

from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


ARCHIVE_ROOT = Path(__file__).resolve().parents[1]
METADATA_ROOT = ARCHIVE_ROOT / "metadata"
CACHE_ROOT = ARCHIVE_ROOT / "cache"
OUTPUT_ROOT = ARCHIVE_ROOT / "spinoza_md"
USER_AGENT = "Codex local Spinoza markdown converter (+https://openai.com/)"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def status(message: str, quiet: bool = False) -> None:
    if not quiet:
        print(message, file=sys.stderr)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def markdown_hash(markdown: str) -> str:
    normalized = re.sub(r"\s+", " ", markdown).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def cache_path_for(url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return CACHE_ROOT / f"{digest}.txt"


def fetch_text(url: str, *, retries: int = 3, timeout: int = 45, delay: float = 0.25, use_cache: bool = True) -> str:
    cache_path = cache_path_for(url)
    if use_cache and cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                raw = response.read()
                charset = response.headers.get_content_charset() or "utf-8"
            text = raw.decode(charset, errors="replace")
            if use_cache:
                atomic_write(cache_path, text)
            time.sleep(delay)
            return text
        except Exception as exc:  # noqa: BLE001 - conversion should record transient fetch failures.
            last_error = exc
            if attempt < retries:
                time.sleep(delay * attempt)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def api_url(base: str, params: dict[str, str | int]) -> str:
    merged = {"format": "json", "formatversion": "2", **params}
    return f"{base}?{urlencode(merged)}"


def fetch_json(url: str, *, use_cache: bool = True):
    return json.loads(fetch_text(url, use_cache=use_cache))


def wikisource_page_url(title: str) -> str:
    return f"https://la.wikisource.org/wiki/{quote(title.replace(' ', '_'), safe=':_(),')}"


def slugify(text: str, fallback: str = "item") -> str:
    text = html.unescape(text).replace("\xa0", " ").lower()
    text = unicodedata.normalize("NFKD", text)
    out = []
    for char in text:
        if char.isascii() and char.isalnum():
            out.append(char)
        else:
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug[:100] or fallback


def compact_spaces(text: str) -> str:
    text = html.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def yaml_quote(value) -> str:
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(yaml_quote(item) for item in value) + "]"
    if value is None:
        return '""'
    value = str(value)
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_front_matter(metadata: dict) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {yaml_quote(value)}")
    lines.append("---")
    return "\n".join(lines)


class MarkdownHTMLParser(HTMLParser):
    """Small HTML-to-Markdown converter tuned for Wikisource rendered pages."""

    SKIP_TAGS = {"script", "style", "sup"}
    BLOCK_TAGS = {"p", "div", "section", "article", "blockquote", "li", "tr"}
    SKIP_CLASS_PARTS = {
        "ws-noexport",
        "noprint",
        "toc",
        "metadata",
        "mw-editsection",
        "mw-jump",
        "catlinks",
        "printfooter",
        "ambox",
        "navbox",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.href_stack: list[str | None] = []
        self.heading_stack: list[int] = []
        self.list_depth = 0

    def should_skip(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        if tag in self.SKIP_TAGS:
            return True
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        class_value = attrs_dict.get("class", "")
        elem_id = attrs_dict.get("id", "")
        if tag == "table" and ("toc" in class_value or "nav" in class_value or elem_id == "toc"):
            return True
        haystack = f"{class_value} {elem_id}".lower()
        return any(part in haystack for part in self.SKIP_CLASS_PARTS)

    def append(self, text: str) -> None:
        if self.skip_depth == 0:
            self.parts.append(text)

    def ensure_break(self, count: int = 2) -> None:
        if self.skip_depth:
            return
        current = "".join(self.parts)
        if not current:
            return
        trailing = len(current) - len(current.rstrip("\n"))
        if trailing < count:
            self.parts.append("\n" * (count - trailing))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.skip_depth or self.should_skip(tag, attrs):
            self.skip_depth += 1
            return
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.ensure_break(2)
            self.append("#" * level + " ")
            self.heading_stack.append(level)
        elif tag in self.BLOCK_TAGS:
            self.ensure_break(2)
            if tag == "li":
                self.append("- ")
        elif tag == "br":
            self.append("\n")
        elif tag in {"i", "em"}:
            self.append("*")
        elif tag in {"b", "strong"}:
            self.append("**")
        elif tag == "a":
            href = attrs_dict.get("href")
            if href and href.startswith("#"):
                href = None
            self.href_stack.append(href)
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            self.ensure_break(2)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self.heading_stack:
                self.heading_stack.pop()
            self.ensure_break(2)
        elif tag in self.BLOCK_TAGS:
            self.ensure_break(2)
        elif tag in {"i", "em"}:
            self.append("*")
        elif tag in {"b", "strong"}:
            self.append("**")
        elif tag == "a":
            if self.href_stack:
                self.href_stack.pop()
        elif tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
            self.ensure_break(2)

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if not data:
            return
        data = data.replace("\xa0", " ")
        if data.strip():
            self.append(re.sub(r"\s+", " ", data))
        elif self.parts and not self.parts[-1].endswith((" ", "\n")):
            self.append(" ")

    def markdown(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\[modifier\]\s*", "", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"(?m)^#{1,6}\s*$\n?", "", text)
        noise_lines = {
            "EPUB MOBI PDF RTF TXT",
            "Jump to content",
            "Jump to navigation Jump to search",
        }
        lines = [line.rstrip() for line in text.splitlines()]
        lines = [line for line in lines if line.strip() not in noise_lines]
        return "\n".join(lines).strip()


def html_to_markdown(source: str) -> str:
    parser = MarkdownHTMLParser()
    parser.feed(source)
    return parser.markdown()


def markdown_document(metadata: dict, title: str, source_url: str, body: str) -> str:
    metadata = dict(metadata)
    metadata.setdefault("created", str(metadata.get("conversion_date", now_iso()))[:10])
    role_map = {
        "authorial_language_text": "author_original",
        "historical_translation_collection": "historical_translation",
        "surviving_textual_witness": "text_witness",
        "individual_correspondence_language_status_unverified": "text_witness",
        "mixed_correspondence_language_status_unverified": "text_witness",
    }
    role = role_map.get(metadata.get("text_role"), metadata.get("text_role", "author_original"))
    metadata["text_role"] = role
    metadata["core_corpus_eligible"] = "true" if role == "author_original" else "false"
    metadata.setdefault("llm_wiki_eligible", "true")
    metadata.setdefault("source_format", "web_api")
    metadata.setdefault("source_license", "not_stated")
    metadata.setdefault("redistribution_approved", "false")
    metadata.setdefault("rights_review_status", "unreviewed")
    metadata.setdefault("text_status", "web_transcription_unverified")
    metadata.setdefault("source_url", source_url or "not_stated")
    lines = [
        render_front_matter(metadata),
        "",
        f"# {title}",
        "",
        f"Source: <{source_url}>",
        "",
        body.strip(),
    ]
    return "\n".join(part for part in lines if part is not None).strip() + "\n"


def front_matter_block(markdown: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", markdown, flags=re.S)
    if not match:
        return {}
    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def relative_to_archive(path: Path) -> str:
    return str(path.relative_to(ARCHIVE_ROOT))

#!/usr/bin/env python3
"""Convert Spinoza et Nous Latin web transcriptions to Markdown."""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote

import spinoza_common as common


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import split_longform_markdown as longform  # noqa: E402

API_BASE = "https://spinozaetnous.org/w/api.php"
SITE_ROOT = "https://spinozaetnous.org/wiki"
STATE_PATH = common.METADATA_ROOT / "spinoza_spinozaetnous_state.json"
MANIFEST_PATH = common.METADATA_ROOT / "spinoza_web_manifest.json"
PREFERRED_PATH = common.METADATA_ROOT / "preferred_sources.json"
OUTPUT_ROOT = common.OUTPUT_ROOT / "latin_web" / "spinozaetnous"
LETTER_ROOT = OUTPUT_ROOT / "epistolae"
AUTHOR = "Benedictus de Spinoza"
LETTER_AUTHOR = "Benedictus de Spinoza and correspondents"
SOURCE_LICENSE = "Spinoza et Nous: attribution required; non-commercial use only"
MISSING_LETTERS = [38, 42, 43, 49, 69, 84]


WORKS = [
    {
        "id": "web-spinozaetnous-tractatus-theologico-politicus",
        "slug": "tractatus-theologico-politicus",
        "title": "Tractatus theologico-politicus",
        "work_year": "1670",
        "index_page": "Tractatus theologico-politicus",
        "mode": "children",
        "expected_children": ["Tractatus theologico-politicus/Praefatio"]
        + [f"Tractatus theologico-politicus/Caput {roman}" for roman in [
            "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
            "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
        ]],
        "output_file": "tractatus-theologico-politicus.md",
    },
    {
        "id": "web-spinozaetnous-renati-descartes-principia-philosophiae",
        "slug": "renati-descartes-principia-philosophiae",
        "title": "Renati Descartes principia philosophiae more geometrico demonstrata",
        "work_year": "1663",
        "index_page": "Renati Descartes Principia philosophiae",
        "mode": "children",
        "expected_children": [
            "Renati Descartes Principia philosophiae/Praefatio",
            "Renati Descartes Principia philosophiae/Pars I",
            "Renati Descartes Principia philosophiae/Pars II",
            "Renati Descartes Principia philosophiae/Pars III",
        ],
        "output_file": "renati-descartes-principia-philosophiae.md",
    },
    {
        "id": "web-spinozaetnous-cogitata-metaphysica",
        "slug": "cogitata-metaphysica",
        "title": "Cogitata metaphysica",
        "work_year": "1663",
        "index_page": "Cogitata metaphysica",
        "mode": "children",
        "expected_children": ["Cogitata metaphysica - Pars I", "Cogitata metaphysica - Pars II"],
        "output_file": "cogitata-metaphysica.md",
    },
    {
        "id": "web-spinozaetnous-tractatus-de-intellectus-emendatione",
        "slug": "tractatus-de-intellectus-emendatione",
        "title": "Tractatus de intellectus emendatione",
        "work_year": "1677",
        "index_page": "Tractatus de intellectus emendatione",
        "mode": "single",
        "output_file": "tractatus-de-intellectus-emendatione.md",
    },
    {
        "id": "web-spinozaetnous-ethica",
        "slug": "ethica",
        "title": "Ethica ordine geometrico demonstrata",
        "work_year": "1677",
        "index_page": "Ethica ordine geometrico demonstrata",
        "mode": "children",
        "expected_children": [f"Ethica - Pars {roman}" for roman in ["I", "II", "III", "IV", "V"]],
        "output_file": "ethica.md",
    },
    {
        "id": "web-spinozaetnous-tractatus-politicus",
        "slug": "tractatus-politicus",
        "title": "Tractatus politicus",
        "work_year": "1677",
        "index_page": "Tractatus politicus",
        "mode": "single",
        "output_file": "tractatus-politicus.md",
    },
    {
        "id": "web-spinozaetnous-epistolae",
        "slug": "epistolae",
        "title": "Epistolae",
        "work_year": "1677",
        "index_page": "Epistolae",
        "mode": "letters",
        "output_file": "epistolae.md",
    },
]


def page_url(page_title: str) -> str:
    return f"{SITE_ROOT}/{quote(page_title.replace(' ', '_'), safe='/:_(),-')}"


def parse_api_text(value) -> str:
    if isinstance(value, dict):
        return value.get("*", "")
    return value or ""


def fetch_page(page_title: str, *, force_fetch: bool, include_text: bool = True) -> dict:
    props = "links|revid|displaytitle"
    if include_text:
        props = "text|" + props
    url = common.api_url(API_BASE, {"action": "parse", "page": page_title, "prop": props})
    data = common.fetch_json(url, use_cache=not force_fetch)
    if "parse" not in data:
        error_text = " ".join(str(value) for value in data.get("error", {}).values())
        if "DBConnectionError" in error_text or "max_user_connections" in error_text:
            for attempt in range(1, 5):
                time.sleep(attempt)
                data = common.fetch_json(url, use_cache=False)
                if "parse" in data:
                    break
    if "parse" not in data:
        error = data.get("error", {})
        raise RuntimeError(f"Spinoza et Nous parse failed for {page_title}: {error.get('code')} {error.get('info')}")
    parsed = data["parse"]
    links = []
    for item in parsed.get("links", []):
        if isinstance(item, dict):
            title = item.get("*") or item.get("title")
            if title:
                links.append(title)
    return {
        "page_title": page_title,
        "source_url": page_url(page_title),
        "revision_id": parsed.get("revid", ""),
        "display_title": parse_api_text(parsed.get("displaytitle", "")),
        "html": parse_api_text(parsed.get("text", "")),
        "links": links,
    }


class SpinozaWebHTMLParser(HTMLParser):
    """HTML-to-Markdown converter for the old Spinoza et Nous MediaWiki."""

    VOID_TAGS = {"br", "hr", "img", "meta", "link", "input"}
    SKIP_TAGS = {"script", "style", "table"}
    SKIP_CLASS_PARTS = {"editsection", "hiddenstructure", "noprint", "printfooter", "navbox"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.reference_depth = 0
        self.in_references = 0
        self.reference_li = False
        self.anchor_stack: list[str] = []
        self.heading_stack: list[int] = []
        self.list_stack: list[str] = []

    def append(self, value: str) -> None:
        if not self.skip_depth and not self.reference_depth:
            self.parts.append(value)

    def ensure_break(self, count: int = 2) -> None:
        if self.skip_depth or self.reference_depth:
            return
        current = "".join(self.parts)
        if not current:
            return
        trailing = len(current) - len(current.rstrip("\n"))
        if trailing < count:
            self.parts.append("\n" * (count - trailing))

    @staticmethod
    def attrs_dict(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
        return {key.lower(): value or "" for key, value in attrs}

    def should_skip(self, tag: str, attrs: list[tuple[str, str | None]]) -> bool:
        if tag in self.SKIP_TAGS:
            return True
        values = self.attrs_dict(attrs)
        haystack = f"{values.get('class', '')} {values.get('id', '')}".lower()
        return any(part in haystack for part in self.SKIP_CLASS_PARTS)

    @staticmethod
    def footnote_number(identifier: str) -> str:
        match = re.search(r"(?:cite_ref|cite_note)-([0-9]+)", identifier)
        return str(int(match.group(1)) + 1) if match else "note"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = self.attrs_dict(attrs)
        if self.reference_depth:
            if tag not in self.VOID_TAGS:
                self.reference_depth += 1
            return
        if self.skip_depth:
            if tag not in self.VOID_TAGS:
                self.skip_depth += 1
            return
        if tag == "sup" and "reference" in values.get("class", "").lower():
            self.append(f"[^{self.footnote_number(values.get('id', ''))}]")
            self.reference_depth = 1
            return
        if self.should_skip(tag, attrs):
            if tag not in self.VOID_TAGS:
                self.skip_depth = 1
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = min(6, max(2, int(tag[1])))
            self.ensure_break(2)
            self.append("#" * level + " ")
            self.heading_stack.append(level)
        elif tag in {"p", "div", "section", "article"}:
            self.ensure_break(2)
        elif tag == "blockquote":
            self.ensure_break(2)
            self.append("> ")
        elif tag == "br":
            self.append("\n")
        elif tag in {"i", "em"}:
            self.append("*")
        elif tag in {"b", "strong"}:
            self.append("**")
        elif tag == "sup":
            self.append("<sup>")
        elif tag == "sub":
            self.append("<sub>")
        elif tag in {"ul", "ol"}:
            if tag == "ol" and "references" in values.get("class", "").lower():
                self.in_references += 1
            self.list_stack.append(tag)
            self.ensure_break(2)
        elif tag == "li":
            self.ensure_break(1)
            if self.in_references and values.get("id", "").startswith("cite_note"):
                self.reference_li = True
                self.append(f"[^{self.footnote_number(values['id'])}]: ")
            else:
                self.append("- ")
        elif tag == "a":
            href = values.get("href", "")
            self.anchor_stack.append("backlink" if self.reference_li and href.startswith("#cite_ref") else "normal")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self.reference_depth:
            self.reference_depth -= 1
            return
        if self.skip_depth:
            self.skip_depth -= 1
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            if self.heading_stack:
                self.heading_stack.pop()
            self.ensure_break(2)
        elif tag in {"p", "div", "section", "article", "blockquote"}:
            self.ensure_break(2)
        elif tag in {"i", "em"}:
            self.append("*")
        elif tag in {"b", "strong"}:
            self.append("**")
        elif tag == "sup":
            self.append("</sup>")
        elif tag == "sub":
            self.append("</sub>")
        elif tag == "a":
            if self.anchor_stack:
                self.anchor_stack.pop()
        elif tag == "li":
            self.reference_li = False
            self.ensure_break(1)
        elif tag in {"ul", "ol"}:
            if tag == "ol" and self.in_references:
                self.in_references -= 1
            if self.list_stack:
                self.list_stack.pop()
            self.ensure_break(2)

    def handle_data(self, data: str) -> None:
        if self.skip_depth or self.reference_depth:
            return
        if self.anchor_stack and self.anchor_stack[-1] == "backlink":
            return
        data = html.unescape(data).replace("\xa0", " ")
        if not data:
            return
        if data.strip():
            self.append(re.sub(r"\s+", " ", data))
        elif self.parts and not self.parts[-1].endswith((" ", "\n")):
            self.append(" ")

    def markdown(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\[\s*modifier\s*\]\s*", "", text, flags=re.I)
        text = re.sub(r"(?mi)^\s*Sommaire\s*$", "", text)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"(?m)^#{1,6}\s*$\n?", "", text)
        return text.strip()


def html_to_markdown(source: str) -> str:
    parser = SpinozaWebHTMLParser()
    parser.feed(source)
    return parser.markdown()


def namespace_footnotes(markdown: str, page_title: str) -> str:
    prefix = common.slugify(page_title, fallback="page")
    return re.sub(r"\[\^([^\]]+)\]", lambda match: f"[^{prefix}-{match.group(1)}]", markdown)


def letter_group_links(index_page: dict) -> list[str]:
    links = []
    for title in index_page["links"]:
        if title == "Aliae Epistolae" or title.startswith("Ab et ad ") or title.startswith("Ad "):
            links.append(title)
    if not links:
        raise RuntimeError("No letter collection pages discovered from Epistolae")
    return links


def discover_work(work: dict, *, force_fetch: bool) -> dict:
    index = fetch_page(work["index_page"], force_fetch=force_fetch)
    page_titles: list[str]
    if work["mode"] == "single":
        page_titles = [work["index_page"]]
    elif work["mode"] == "children":
        missing = [title for title in work["expected_children"] if title not in index["links"]]
        if missing:
            raise RuntimeError(f"{work['slug']} missing expected child pages: {', '.join(missing)}")
        page_titles = work["expected_children"]
    else:
        page_titles = letter_group_links(index)

    pages = []
    for title in page_titles:
        page = index if title == work["index_page"] else fetch_page(title, force_fetch=force_fetch)
        pages.append({
            "page_title": page["page_title"],
            "source_url": page["source_url"],
            "revision_id": page["revision_id"],
        })
        time.sleep(0.15)
    edition_identified = "gebhardt" in index["html"].lower()
    status = "web_transcription_edition_identified_unverified" if edition_identified else "web_transcription_unverified"
    if work["mode"] == "letters":
        status = "partial_web_transcription"
    return {
        **{key: value for key, value in work.items() if key not in {"expected_children"}},
        "source_url": index["source_url"],
        "index_revision_id": index["revision_id"],
        "edition_claim": "Gebhardt edition" if edition_identified else "not explicitly identified on index page",
        "text_status": status,
        "pages": pages,
        "output_path": common.relative_to_archive(OUTPUT_ROOT / work["output_file"]),
    }


def build_manifest(*, force_fetch: bool) -> dict:
    items = [discover_work(work, force_fetch=force_fetch) for work in WORKS]
    items.append({
        "id": "web-spinozaetnous-compendium-grammatices-linguae-hebraeae",
        "slug": "compendium-grammatices-linguae-hebraeae",
        "title": "Compendium Grammatices Linguae Hebraeae",
        "status": "source_pdf_available_web_transcription_missing",
        "source_pdf": "source_pdfs/bruder-vol-iii-1846.pdf",
        "output_path": "",
    })
    return {
        "generated_at": common.now_iso(),
        "source_site": "spinozaetnous.org",
        "source_license": SOURCE_LICENSE,
        "intended_use": "public non-commercial research archive",
        "items": items,
    }


def manifest_item(work: dict, manifest: dict) -> dict:
    for item in manifest.get("items", []):
        if item.get("id") == work["id"]:
            return item
    raise RuntimeError(f"Missing manifest item for {work['id']}")


def fetch_manifest_pages(item: dict, *, force_fetch: bool, quiet: bool) -> list[dict]:
    pages = []
    for page_info in item["pages"]:
        common.status(f"  fetch {page_info['page_title']}", quiet)
        page = fetch_page(page_info["page_title"], force_fetch=force_fetch)
        pages.append(page)
        time.sleep(0.15)
    return pages


def revision_string(pages: list[dict]) -> str:
    return "; ".join(f"{page['page_title']}:{page['revision_id']}" for page in pages)


def work_metadata(work: dict, item: dict, pages: list[dict], *, author: str = AUTHOR) -> dict:
    metadata = {
        "id": work["id"],
        "type": "source",
        "tags": ["spinoza", "latin", "authorial-language"],
        "collection": "spinoza-original-language",
        "author": author,
        "title": work["title"],
        "language": "la",
        "source_url": item["source_url"],
        "source_site": "spinozaetnous.org",
        "source_revision_id": revision_string(pages),
        "source_license": SOURCE_LICENSE,
        "work_year": work["work_year"],
        "conversion_date": common.now_iso(),
        "text_status": item["text_status"],
        "source_edition_claim": item["edition_claim"],
    }
    if work["mode"] == "letters":
        metadata.update({
            "text_role": "text_witness",
            "core_corpus_eligible": "false",
            "llm_wiki_eligible": "true",
            "original_language_status": "verify the composition language and transmission history of each letter before core-corpus use",
        })
    else:
        metadata.update({
            "text_role": "author_original",
            "core_corpus_eligible": "true",
            "llm_wiki_eligible": "true",
            "original_language_status": "Latin authorial-language work",
        })
    return metadata


def convert_standard_work(work: dict, item: dict, pages: list[dict]) -> tuple[str, dict]:
    parts = []
    for page in pages:
        body = namespace_footnotes(html_to_markdown(page["html"]), page["page_title"])
        parts.append(f"## {page['page_title']}\n\nSource page: <{page['source_url']}>\n\n{body}")
    metadata = work_metadata(work, item, pages)
    markdown = common.markdown_document(metadata, work["title"], item["source_url"], "\n\n---\n\n".join(parts))
    return markdown, {}


LETTER_HEADING_RE = re.compile(r"(?mi)^#{2,6}\s+Epistola\s+(\d+)(?:\s+(bis))?(?=\s|\(|$)")


def split_letter_page(page: dict) -> list[dict]:
    markdown = namespace_footnotes(html_to_markdown(page["html"]), page["page_title"])
    matches = list(LETTER_HEADING_RE.finditer(markdown))
    letters = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        number = int(match.group(1))
        is_bis = bool(match.group(2))
        key = f"{number}-bis" if is_bis else str(number)
        body = markdown[match.start():end].strip()
        letters.append({
            "key": key,
            "number": number,
            "is_bis": is_bis,
            "title": f"Epistola {number}{' bis' if is_bis else ''}",
            "body": body,
            "source_url": page["source_url"],
            "page_title": page["page_title"],
            "revision_id": page["revision_id"],
        })
    return letters


def letter_sort_key(letter: dict) -> tuple[int, int]:
    return letter["number"], 1 if letter["is_bis"] else 0


def convert_letters(work: dict, item: dict, pages: list[dict]) -> tuple[str, dict]:
    by_key: dict[str, dict] = {}
    for page in pages:
        for letter in split_letter_page(page):
            if letter["key"] in by_key:
                raise RuntimeError(f"Duplicate letter discovered: {letter['key']}")
            by_key[letter["key"]] = letter
    letters = sorted(by_key.values(), key=letter_sort_key)
    regular_numbers = sorted(letter["number"] for letter in letters if not letter["is_bis"])
    missing = sorted(set(range(1, 85)) - set(regular_numbers))
    if missing != MISSING_LETTERS:
        raise RuntimeError(f"Unexpected letter coverage; missing={missing}")
    bis_keys = [letter["key"] for letter in letters if letter["is_bis"]]
    if bis_keys != ["12-bis", "67-bis"]:
        raise RuntimeError(f"Unexpected bis letters: {bis_keys}")

    LETTER_ROOT.mkdir(parents=True, exist_ok=True)
    expected_paths: set[Path] = set()
    letter_hashes: dict[str, str] = {}
    combined_parts = []
    for letter in letters:
        suffix = "-bis" if letter["is_bis"] else ""
        path = LETTER_ROOT / f"epistola-{letter['number']:03d}{suffix}.md"
        expected_paths.add(path)
        metadata = {
            "id": f"web-spinozaetnous-epistola-{letter['number']:03d}{suffix}",
            "type": "source",
            "tags": ["spinoza", "latin", "correspondence"],
            "collection": "spinoza-correspondence",
            "author": LETTER_AUTHOR,
            "title": letter["title"],
            "language": "la",
            "source_url": letter["source_url"],
            "source_site": "spinozaetnous.org",
            "source_revision_id": f"{letter['page_title']}:{letter['revision_id']}",
            "source_license": SOURCE_LICENSE,
            "work_year": "",
            "conversion_date": common.now_iso(),
            "text_status": "web_transcription_edition_identified_unverified",
            "source_edition_claim": item["edition_claim"],
            "text_role": "text_witness",
            "core_corpus_eligible": "false",
            "llm_wiki_eligible": "true",
            "original_language_status": "the Latin source text may be authorial or an early translation; verify per letter before core-corpus use",
        }
        body = f"Source collection page: <{letter['source_url']}>\n\n{letter['body']}"
        document = common.markdown_document(metadata, letter["title"], letter["source_url"], body)
        common.atomic_write(path, document)
        letter_hashes[common.relative_to_archive(path)] = common.markdown_hash(document)
        combined_parts.append(f"## {letter['title']}\n\nSource collection page: <{letter['source_url']}>\n\n{letter['body']}")
    for stale_path in LETTER_ROOT.glob("epistola-*.md"):
        if stale_path not in expected_paths:
            stale_path.unlink()

    metadata = work_metadata(work, item, pages, author=LETTER_AUTHOR)
    metadata["letter_coverage"] = "78 regular letters plus Epistola 12 bis and 67 bis"
    metadata["missing_letter_numbers"] = ", ".join(map(str, MISSING_LETTERS))
    intro = "\n\n".join([
        "Coverage note: the source index lists Epistolae 1-84, but the available collection pages contain 78 regular numbers plus Epistola 12 bis and 67 bis.",
        f"Missing source pages: {', '.join(map(str, MISSING_LETTERS))}.",
        "\n\n---\n\n".join(combined_parts),
    ])
    markdown = common.markdown_document(metadata, work["title"], item["source_url"], intro)
    return markdown, {"letter_hashes": letter_hashes, "letter_count": len(letters), "missing_letters": missing}


def state_item_complete(state_item: dict, output_path: Path, work: dict) -> bool:
    if state_item.get("status") != "done" or not longform.materialized_output_exists(output_path, root=PROJECT_ROOT):
        return False
    if common.markdown_hash(longform.read_materialized_text(output_path, root=PROJECT_ROOT)) != state_item.get("hash"):
        return False
    if work["mode"] == "letters":
        hashes = state_item.get("letter_hashes", {})
        if len(hashes) != 80:
            return False
        for relative_path, expected_hash in hashes.items():
            path = common.ARCHIVE_ROOT / relative_path
            if not path.exists() or common.markdown_hash(path.read_text(encoding="utf-8")) != expected_hash:
                return False
    return True


def write_preferred_sources(manifest: dict) -> None:
    web_items = {item.get("slug"): item for item in manifest["items"]}
    current = common.read_json(PREFERRED_PATH, {"works": {}})
    works = current.get("works", {})
    for slug in [
        "tractatus-theologico-politicus",
        "renati-descartes-principia-philosophiae",
        "cogitata-metaphysica",
        "tractatus-de-intellectus-emendatione",
        "ethica",
        "tractatus-politicus",
        "epistolae",
    ]:
        item = web_items[slug]
        output_path = common.ARCHIVE_ROOT / item["output_path"]
        split_spec = longform.registered_spec(output_path, PROJECT_ROOT)
        source_record = {"preferred_markdown": item["output_path"]}
        if split_spec:
            manifest_path = longform.manifest_path_for(output_path)
            work_manifest = common.read_json(manifest_path, {"chapters": []})
            source_record = {
                "preferred_markdown": "",
                "preferred_work_manifest": common.relative_to_archive(manifest_path),
                "chapter_files": [
                    common.relative_to_archive(manifest_path.parent / chapter["file"])
                    for chapter in work_manifest["chapters"]
                ],
            }
        works[slug] = {
            **source_record,
            "source_site": "spinozaetnous.org",
            "license": SOURCE_LICENSE,
            "text_status": item["text_status"],
            "text_role": "text_witness" if slug == "epistolae" else "author_original",
            "core_corpus_eligible": slug != "epistolae",
            "llm_wiki_eligible": True,
        }
    works["compendium-grammatices-linguae-hebraeae"] = {
        "preferred_markdown": "",
        "source_pdf": "source_pdfs/bruder-vol-iii-1846.pdf",
        "text_status": "source_scans_and_chapter_structure_available_web_transcription_missing",
        "text_role": "scan_reference",
        "core_corpus_eligible": False,
        "llm_wiki_eligible": False,
    }
    common.write_json(PREFERRED_PATH, {"generated_at": common.now_iso(), "works": works})


def print_dry_run(manifest: dict) -> None:
    print(f"Source: {manifest['source_site']}")
    for item in manifest["items"]:
        if item.get("status") == "source_pdf_available_web_transcription_missing":
            print(f"- {item['slug']}: no web transcription; PDF retained")
            continue
        print(f"- {item['slug']}: pages={len(item['pages'])} status={item['text_status']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Spinoza et Nous Latin web texts to Markdown.")
    parser.add_argument("--dry-run", action="store_true", help="Discover pages and print coverage without writing files")
    parser.add_argument("--rebuild-manifest", action="store_true", help="Rebuild the web source manifest")
    parser.add_argument("--resume", action="store_true", help="Skip completed outputs whose hashes still match state")
    parser.add_argument("--force", action="store_true", help="Re-convert completed outputs")
    parser.add_argument("--force-fetch", action="store_true", help="Ignore cached source responses")
    parser.add_argument("--only", help="Convert one work slug or id")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress messages")
    args = parser.parse_args()

    if args.dry_run or args.rebuild_manifest or not MANIFEST_PATH.exists():
        manifest = build_manifest(force_fetch=args.force_fetch)
        if args.dry_run:
            print_dry_run(manifest)
            return 0
        common.write_json(MANIFEST_PATH, manifest)
    else:
        manifest = common.read_json(MANIFEST_PATH, {})

    works = WORKS
    if args.only:
        works = [work for work in WORKS if args.only in {work["slug"], work["id"]}]
        if not works:
            raise SystemExit(f"No Spinoza et Nous work with id or slug {args.only}")

    old_state = common.read_json(STATE_PATH, {"items": {}})
    state = {"generated_at": common.now_iso(), "items": {}}
    converted = skipped = failed = 0
    for work in works:
        item = manifest_item(work, manifest)
        output_path = OUTPUT_ROOT / work["output_file"]
        previous = old_state.get("items", {}).get(work["id"], {})
        if args.resume and not args.force and state_item_complete(previous, output_path, work):
            state["items"][work["id"]] = previous
            skipped += 1
            common.status(f"skip done {work['id']}", args.quiet)
            continue
        common.status(f"convert {work['id']}", args.quiet)
        try:
            pages = fetch_manifest_pages(item, force_fetch=args.force_fetch, quiet=args.quiet)
            if work["mode"] == "letters":
                markdown, extras = convert_letters(work, item, pages)
            else:
                markdown, extras = convert_standard_work(work, item, pages)
            longform.write_or_split(output_path, markdown, root=PROJECT_ROOT)
            state_record = {
                "status": "done",
                "hash": common.markdown_hash(markdown),
                "output_path": common.relative_to_archive(output_path),
                "updated_at": common.now_iso(),
                "bytes": longform.materialized_output_bytes(output_path, root=PROJECT_ROOT),
                "source_url": item["source_url"],
                **extras,
            }
            if longform.registered_spec(output_path, PROJECT_ROOT):
                work_manifest_path = longform.manifest_path_for(output_path)
                work_manifest = common.read_json(work_manifest_path, {"chapters": []})
                state_record.update({
                    "work_manifest": common.relative_to_archive(work_manifest_path),
                    "chapter_count": len(work_manifest["chapters"]),
                })
            state["items"][work["id"]] = state_record
            converted += 1
        except Exception as exc:  # noqa: BLE001 - keep the batch resumable.
            state["items"][work["id"]] = {"status": "failed", "error": str(exc), "updated_at": common.now_iso()}
            failed += 1
        common.write_json(STATE_PATH, state)

    if not args.only:
        for work in WORKS:
            if work["id"] not in state["items"] and work["id"] in old_state.get("items", {}):
                state["items"][work["id"]] = old_state["items"][work["id"]]
        common.write_json(STATE_PATH, state)
        write_preferred_sources(manifest)
    common.status(f"converted={converted} skipped={skipped} failed={failed}", args.quiet)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

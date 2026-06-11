#!/usr/bin/env python3
"""Convert Spinoza's Dutch Short Treatise from Dutch Wikisource."""

from __future__ import annotations

import argparse
import re
from urllib.parse import quote

import spinoza_common as common


API_BASE = "https://nl.wikisource.org/w/api.php"
PAGE_TITLE = "Korte Verhandeling van God, de mensch en deszelvs welstand"
SOURCE_URL = f"https://nl.wikisource.org/wiki/{quote(PAGE_TITLE.replace(' ', '_'), safe=':_(),')}"
OUTPUT_PATH = common.OUTPUT_ROOT / "dutch_web" / "nlwikisource" / "korte-verhandeling.md"
STATE_PATH = common.METADATA_ROOT / "spinoza_nl_wikisource_state.json"
PREFERRED_PATH = common.METADATA_ROOT / "preferred_sources.json"
SOURCE_LICENSE = "Wikisource page license: CC BY-SA 4.0; source transcription and manuscript are public domain"
TEXT_STATUS = "complete_surviving_dutch_text_unverified"


def fetch_page(*, use_cache: bool) -> dict:
    url = common.api_url(
        API_BASE,
        {
            "action": "parse",
            "page": PAGE_TITLE,
            "prop": "text|revid|displaytitle",
            "redirects": "1",
        },
    )
    data = common.fetch_json(url, use_cache=use_cache)
    if "parse" not in data:
        error = data.get("error", {})
        raise RuntimeError(f"Dutch Wikisource parse failed: {error.get('code')} {error.get('info')}")
    return data["parse"]


def clean_body(html: str) -> str:
    body = common.html_to_markdown(html)
    start = body.find("**INHOUD**")
    if start >= 0:
        body = body[start:]
    body = re.sub(r"(?m)^Figure \d+\..*$\n?", "", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def validate_body(body: str) -> list[str]:
    issues: list[str] = []
    if "## Het eerste DEEL, van GOD" not in body:
        issues.append("missing first part")
    if "## Het twede DEEL van DE MENSCH" not in body:
        issues.append("missing second part")
    first_part = set(re.findall(r"(?m)^### Cap\. ([IVX]+) ", body))
    if not {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}.issubset(first_part):
        issues.append("first part does not contain chapters I-X")
    for marker in ["2/1,1", "2/10,1", "2/20,1"]:
        if marker not in body:
            issues.append(f"missing structural marker {marker}")
    if "### Cap. XXVI Van de waare vrijheid" not in body:
        issues.append("missing second-part chapter XXVI")
    if len(body) < 150_000:
        issues.append(f"body unexpectedly short: {len(body)} characters")
    return issues


def update_preferred_source() -> None:
    data = common.read_json(PREFERRED_PATH, {"works": {}})
    works = data.setdefault("works", {})
    works["korte-verhandeling"] = {
        "preferred_markdown": common.relative_to_archive(OUTPUT_PATH),
        "source_site": "nl.wikisource.org",
        "license": SOURCE_LICENSE,
        "text_status": TEXT_STATUS,
        "text_role": "text_witness",
        "core_corpus_eligible": False,
        "llm_wiki_eligible": True,
        "original_language_status": "surviving Dutch text, generally considered a translation of a lost Latin original",
    }
    works["compendium-grammatices-linguae-hebraeae"] = {
        "preferred_markdown": "",
        "source_pdf": "source_pdfs/bruder-vol-iii-1846.pdf",
        "structured_scan_url": "https://diglib.hab.de/drucke/ac-343/start.htm",
        "text_status": "source_scans_and_chapter_structure_available_web_transcription_missing",
        "text_role": "scan_reference",
        "core_corpus_eligible": False,
        "llm_wiki_eligible": False,
    }
    works["ultimi-barbarorum"] = {
        "preferred_markdown": "",
        "text_status": "reported_lost_fragment_no_surviving_document",
        "text_role": "lost_reported_fragment",
        "core_corpus_eligible": False,
        "llm_wiki_eligible": False,
    }
    if "epistolae" in works:
        works["epistolae"]["missing_gebhardt_numbers"] = "38, 42, 43, 49, 69, 84"
    data["generated_at"] = common.now_iso()
    common.write_json(PREFERRED_PATH, data)


def state_complete(state: dict) -> bool:
    if state.get("status") != "done" or not OUTPUT_PATH.exists():
        return False
    return common.markdown_hash(OUTPUT_PATH.read_text(encoding="utf-8")) == state.get("hash")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert the Dutch Short Treatise from Dutch Wikisource.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and validate without writing Markdown")
    parser.add_argument("--resume", action="store_true", help="Skip an output whose hash matches state")
    parser.add_argument("--force", action="store_true", help="Rewrite an existing output")
    parser.add_argument("--force-fetch", action="store_true", help="Ignore cached API responses")
    args = parser.parse_args()

    state = common.read_json(STATE_PATH, {})
    if args.resume and not args.force and state_complete(state):
        update_preferred_source()
        print("skip done korte-verhandeling")
        return 0

    page = fetch_page(use_cache=not args.force_fetch)
    html = page["text"] if isinstance(page["text"], str) else page["text"].get("*", "")
    body = clean_body(html)
    issues = validate_body(body)
    if issues:
        raise RuntimeError("; ".join(issues))
    print(f"revision={page.get('revid')} characters={len(body)}")
    if args.dry_run:
        return 0

    metadata = {
        "id": "nlwikisource-korte-verhandeling",
        "type": "source",
        "tags": ["spinoza", "dutch", "textual-witness"],
        "collection": "spinoza-historical-witnesses",
        "author": "Benedictus de Spinoza",
        "title": PAGE_TITLE,
        "language": "nl",
        "source_url": SOURCE_URL,
        "source_site": "nl.wikisource.org",
        "source_revision_id": page.get("revid", ""),
        "source_license": SOURCE_LICENSE,
        "work_year": "ca. 1660",
        "conversion_date": common.now_iso(),
        "text_status": TEXT_STATUS,
        "text_role": "text_witness",
        "core_corpus_eligible": "false",
        "llm_wiki_eligible": "true",
        "source_format": "web_api",
        "redistribution_approved": "false",
        "rights_review_status": "unreviewed",
        "source_document": "Koninklijke Bibliotheek, The Hague, manuscript KB 75 G 15",
        "original_language_status": "surviving Dutch text, generally considered a translation of a lost Latin original",
    }
    markdown = common.markdown_document(metadata, PAGE_TITLE, SOURCE_URL, body)
    common.atomic_write(OUTPUT_PATH, markdown)
    state = {
        "status": "done",
        "hash": common.markdown_hash(markdown),
        "bytes": OUTPUT_PATH.stat().st_size,
        "output_path": common.relative_to_archive(OUTPUT_PATH),
        "source_revision_id": page.get("revid", ""),
        "updated_at": common.now_iso(),
    }
    common.write_json(STATE_PATH, state)
    update_preferred_source()
    print(f"wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

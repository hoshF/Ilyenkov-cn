#!/usr/bin/env python3
"""Fetch DBNL Nagelate schriften TEI XML and convert it to Markdown."""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import spinoza_common as common


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import split_longform_markdown as longform  # noqa: E402

DBNL_ID = "spin003nage01"
XML_URL = f"https://www.dbnl.org/nieuws/xml.php?id={DBNL_ID}"
TXT_URL = f"https://www.dbnl.org/nieuws/text.php?id={DBNL_ID}"
DOWNLOADS_URL = "https://www.dbnl.org/tekst/spin003nage01_01/downloads.php"
STATE_PATH = common.METADATA_ROOT / "spinoza_dbnl_state.json"
OUTPUT_PATH = common.OUTPUT_ROOT / "dutch" / "nagelate-schriften.md"
PREFERRED_PATH = common.METADATA_ROOT / "preferred_sources.json"
SOURCE_LICENSE = "DBNL page states Auteursrechtvrij; diplomatic source text from 1677"


def strip_doctype(xml_text: str) -> str:
    return re.sub(r"<!DOCTYPE[^>]+>\s*", "", xml_text, count=1)


def flatten_text(element: ET.Element) -> str:
    parts: list[str] = []
    if element.text:
        parts.append(element.text)
    for child in element:
        if child.tag == "pb":
            n = child.attrib.get("n", "")
            if n:
                parts.append(f" {{=={n}==}} ")
        else:
            parts.append(flatten_text(child))
        if child.tail:
            parts.append(child.tail)
    return common.compact_spaces("".join(parts))


def convert_body(element: ET.Element, level: int = 2) -> list[str]:
    lines: list[str] = []
    for child in element:
        if child.tag == "pb":
            n = child.attrib.get("n")
            if n:
                lines.append(f"{{=={n}==}}")
        elif child.tag == "head":
            text = flatten_text(child)
            if text:
                heading_level = min(level, 6)
                lines.append(f"{'#' * heading_level} {text}")
        elif child.tag == "p":
            text = flatten_text(child)
            if text:
                lines.append(text)
        elif child.tag in {"div", "body", "text"}:
            lines.extend(convert_body(child, min(level + 1, 6) if child.tag == "div" else level))
        elif child.tag in {"list", "lg"}:
            lines.extend(convert_body(child, level))
        elif child.tag == "item":
            text = flatten_text(child)
            if text:
                lines.append(f"- {text}")
        else:
            text = flatten_text(child)
            if text:
                lines.append(text)
    return lines


def header_metadata(root: ET.Element) -> dict[str, str]:
    def first_text(path: str) -> str:
        found = root.find(path)
        return flatten_text(found) if found is not None else ""

    return {
        "title": first_text("./teiHeader/fileDesc/titleStmt/title") or "Nagelate schriften",
        "author": first_text("./teiHeader/fileDesc/titleStmt/author") or "Benedictus de Spinoza",
        "idno": first_text("./teiHeader/fileDesc/publicationStmt/idno") or "spin003nage01_01",
        "source_desc": first_text("./teiHeader/fileDesc/sourceDesc/p"),
        "encoding": first_text("./teiHeader/encodingDesc/p"),
    }


def convert_xml(xml_text: str) -> str:
    root = ET.fromstring(strip_doctype(xml_text))
    source = header_metadata(root)
    body = root.find("./text/body")
    if body is None:
        raise RuntimeError("DBNL XML has no text/body")
    body_markdown = "\n\n".join(convert_body(body)).strip()
    metadata = {
        "id": "dbnl-nagelate-schriften",
        "type": "source",
        "tags": ["spinoza", "dutch", "historical-translation"],
        "collection": "spinoza-historical-witnesses",
        "author": source["author"],
        "title": source["title"],
        "language": "nl",
        "source_url": XML_URL,
        "source_site": "dbnl.org",
        "source_file_id": source["idno"],
        "source_license": SOURCE_LICENSE,
        "work_year": "1677",
        "conversion_date": common.now_iso(),
        "text_status": "complete_historical_dutch_translation_unverified",
        "text_role": "historical_translation",
        "core_corpus_eligible": "false",
        "llm_wiki_eligible": "true",
        "source_format": "tei_xml",
        "redistribution_approved": "false",
        "rights_review_status": "unreviewed",
        "original_language_status": "Dutch translation of works composed primarily in Latin; not an authorial-language source",
    }
    preface = "\n".join(
        [
            f"Source downloads: <{DOWNLOADS_URL}>",
            f"Plain text fallback: <{TXT_URL}>",
            f"DBNL source description: {source['source_desc']}",
            f"Encoding: {source['encoding']}",
            "",
            body_markdown,
        ]
    )
    return common.markdown_document(metadata, source["title"], XML_URL, preface)


def state_complete(state: dict) -> bool:
    if state.get("status") != "done" or not longform.materialized_output_exists(OUTPUT_PATH, root=PROJECT_ROOT):
        return False
    return common.markdown_hash(longform.read_materialized_text(OUTPUT_PATH, root=PROJECT_ROOT)) == state.get("hash")


def update_preferred_source() -> None:
    data = common.read_json(PREFERRED_PATH, {"works": {}})
    manifest_path = longform.manifest_path_for(OUTPUT_PATH)
    manifest = common.read_json(manifest_path, {"chapters": []})
    data.setdefault("works", {})["nagelate-schriften"] = {
        "preferred_markdown": "",
        "preferred_work_manifest": common.relative_to_archive(manifest_path),
        "chapter_files": [
            common.relative_to_archive(manifest_path.parent / chapter["file"])
            for chapter in manifest["chapters"]
        ],
        "source_site": "dbnl.org",
        "text_status": "complete_historical_dutch_translation_unverified",
        "text_role": "historical_translation",
        "core_corpus_eligible": False,
        "llm_wiki_eligible": True,
        "original_language_status": "Dutch translation of works composed primarily in Latin; not an authorial-language source",
    }
    data["generated_at"] = common.now_iso()
    common.write_json(PREFERRED_PATH, data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert DBNL Nagelate schriften XML to Markdown.")
    parser.add_argument("--resume", action="store_true", help="Skip completed output whose hash still matches state")
    parser.add_argument("--force-fetch", action="store_true", help="Ignore cached source response")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress messages")
    args = parser.parse_args()

    state = common.read_json(STATE_PATH, {})
    if args.resume and state_complete(state):
        update_preferred_source()
        common.status("skip done dbnl-nagelate-schriften", args.quiet)
        return 0

    common.status("convert dbnl-nagelate-schriften", args.quiet)
    xml_text = common.fetch_text(XML_URL, use_cache=not args.force_fetch)
    markdown = convert_xml(xml_text)
    longform.write_or_split(OUTPUT_PATH, markdown, root=PROJECT_ROOT)
    manifest_path = longform.manifest_path_for(OUTPUT_PATH)
    manifest = common.read_json(manifest_path, {"chapters": []})
    common.write_json(
        STATE_PATH,
        {
            "status": "done",
            "hash": common.markdown_hash(markdown),
            "output_path": common.relative_to_archive(OUTPUT_PATH),
            "work_manifest": common.relative_to_archive(manifest_path),
            "chapter_count": len(manifest["chapters"]),
            "updated_at": common.now_iso(),
            "bytes": longform.materialized_output_bytes(OUTPUT_PATH, root=PROJECT_ROOT),
            "source_url": XML_URL,
            "fallback_text_url": TXT_URL,
        },
    )
    update_preferred_source()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

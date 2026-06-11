#!/usr/bin/env python3
"""Fetch Latin Wikisource Spinoza texts and convert them to Markdown."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import spinoza_common as common


API_BASE = "https://la.wikisource.org/w/api.php"
AUTHOR_TITLE = "Scriptor:Benedictus de Spinoza"
MANIFEST_PATH = common.METADATA_ROOT / "spinoza_catalog_manifest.json"
STATE_PATH = common.METADATA_ROOT / "spinoza_wikisource_state.json"
OUTPUT_ROOT = common.OUTPUT_ROOT / "latin"
AUTHOR = "Benedictus de Spinoza"
SOURCE_LICENSE = "Wikisource page license: CC BY-SA 4.0; source text is public-domain historical text"


def query_page_wikitext(title: str, *, use_cache: bool) -> dict:
    url = common.api_url(
        API_BASE,
        {
            "action": "query",
            "titles": title,
            "prop": "revisions",
            "rvprop": "ids|timestamp|content",
        },
    )
    data = common.fetch_json(url, use_cache=use_cache)
    pages = data.get("query", {}).get("pages", [])
    if not pages or "missing" in pages[0]:
        raise RuntimeError(f"Wikisource page not found: {title}")
    return pages[0]


def parse_author_catalog(wikitext: str) -> list[dict]:
    items: list[dict] = []
    for line in wikitext.splitlines():
        line = line.strip()
        if not line.startswith("*[["):
            continue
        match = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\](.*)$", line)
        if not match:
            continue
        page_title, label, tail = match.groups()
        title = label or page_title
        year_match = re.search(r"\((\d{4})\)", tail)
        completion_match = re.search(r"Image:(\d+)%\.png", tail)
        completion = int(completion_match.group(1)) if completion_match else None
        text_status = "partial_or_unverified" if completion is not None and completion < 100 else "complete_or_unverified"
        items.append(
            {
                "id": common.slugify(page_title),
                "author": AUTHOR,
                "title": title,
                "page_title": page_title,
                "language": "la",
                "work_year": year_match.group(1) if year_match else "",
                "source_url": common.wikisource_page_url(page_title),
                "source_site": "la.wikisource.org",
                "source_license": SOURCE_LICENSE,
                "wikisource_completion_percent": completion,
                "text_status": text_status,
                "output_path": common.relative_to_archive(OUTPUT_ROOT / f"{common.slugify(page_title)}.md"),
            }
        )
    return items


def build_manifest(*, rebuild: bool, quiet: bool) -> dict:
    if MANIFEST_PATH.exists() and not rebuild:
        manifest = common.read_json(MANIFEST_PATH, {})
        if manifest:
            return manifest

    common.status("Fetching Latin Wikisource author catalog", quiet)
    page = query_page_wikitext(AUTHOR_TITLE, use_cache=not rebuild)
    revision = page["revisions"][0]
    items = parse_author_catalog(revision["content"])
    manifest = {
        "source": common.wikisource_page_url(AUTHOR_TITLE),
        "source_site": "la.wikisource.org",
        "generated_at": common.now_iso(),
        "author_page_revision_id": revision.get("revid"),
        "author_page_timestamp": revision.get("timestamp"),
        "items": items,
    }
    common.write_json(MANIFEST_PATH, manifest)
    return manifest


def fetch_rendered_page(item: dict, *, use_cache: bool) -> dict:
    parse_url = common.api_url(
        API_BASE,
        {
            "action": "parse",
            "page": item["page_title"],
            "prop": "text|revid|displaytitle|links",
            "redirects": "1",
        },
    )
    data = common.fetch_json(parse_url, use_cache=use_cache)
    if "parse" not in data:
        error = data.get("error", {})
        code = error.get("code", "unknown")
        info = error.get("info", "unknown API error")
        raise RuntimeError(f"Wikisource parse failed ({code}): {info}")
    parsed = data["parse"]
    query = query_page_wikitext(item["page_title"], use_cache=use_cache)
    revision = query["revisions"][0]
    return {
        "html": parsed["text"],
        "revision_id": parsed.get("revid") or revision.get("revid"),
        "timestamp": revision.get("timestamp"),
        "pageid": parsed.get("pageid"),
        "links": parsed.get("links", []),
    }


def child_pages_for(item: dict, page: dict) -> list[str]:
    if item["page_title"] != "Ethica":
        return []
    prefix = "Ethica/Pars "
    children = [link["title"] for link in page.get("links", []) if link.get("ns") == 0 and link.get("title", "").startswith(prefix)]
    order = {
        "prima": 1,
        "secunda": 2,
        "tertia": 3,
        "quarta": 4,
        "quinta": 5,
    }

    def sort_key(title: str) -> int:
        match = re.search(r"Pars\s+([a-z]+)", title, flags=re.I)
        return order.get(match.group(1).lower(), 99) if match else 99

    return sorted(set(children), key=sort_key)


def convert_item(item: dict, *, force_fetch: bool = False) -> str:
    page = fetch_rendered_page(item, use_cache=not force_fetch)
    body_parts = [common.html_to_markdown(page["html"])]
    revision_ids = [str(page["revision_id"])]
    for child_title in child_pages_for(item, page):
        child_item = {**item, "page_title": child_title}
        child_page = fetch_rendered_page(child_item, use_cache=not force_fetch)
        child_source = common.wikisource_page_url(child_title)
        child_body = common.html_to_markdown(child_page["html"])
        body_parts.append(f"Source part page: <{child_source}>\n\n{child_body}")
        revision_ids.append(f"{child_title}:{child_page['revision_id']}")
    body = "\n\n---\n\n".join(part for part in body_parts if part.strip())
    metadata = {
        "id": item["id"],
        "type": "source",
        "tags": ["spinoza", "latin", "wikisource-backup"],
        "collection": "spinoza-original-language-backup",
        "llm_wiki_eligible": "true",
        "author": item["author"],
        "title": item["title"],
        "language": item["language"],
        "source_url": item["source_url"],
        "source_site": item["source_site"],
        "source_revision_id": "; ".join(revision_ids),
        "source_license": item["source_license"],
        "work_year": item.get("work_year", ""),
        "conversion_date": common.now_iso(),
        "text_status": item["text_status"],
    }
    return common.markdown_document(metadata, item["title"], item["source_url"], body)


def state_item_complete(state_item: dict, item: dict) -> bool:
    if state_item.get("status") != "done":
        return False
    output_path = common.ARCHIVE_ROOT / item["output_path"]
    if not output_path.exists():
        return False
    return common.markdown_hash(output_path.read_text(encoding="utf-8")) == state_item.get("hash")


def item_by_id(manifest: dict, item_id: str) -> dict:
    for item in manifest["items"]:
        if item["id"] == item_id:
            return item
    raise KeyError(f"No manifest item with id {item_id}")


def convert_items(args: argparse.Namespace, manifest: dict) -> int:
    state = common.read_json(STATE_PATH, {"items": {}})
    state.setdefault("items", {})
    items = manifest["items"]
    if args.only:
        items = [item_by_id(manifest, args.only)]
    if args.limit is not None:
        items = items[: args.limit]

    converted = skipped = failed = missing = 0
    for item in items:
        item_state = state["items"].get(item["id"], {})
        if args.resume and not args.force and state_item_complete(item_state, item):
            skipped += 1
            common.status(f"skip done {item['id']}", args.quiet)
            continue

        common.status(f"convert {item['id']}", args.quiet)
        try:
            markdown = convert_item(item, force_fetch=args.force_fetch)
            output_path = common.ARCHIVE_ROOT / item["output_path"]
            common.atomic_write(output_path, markdown)
            digest = common.markdown_hash(markdown)
            state["items"][item["id"]] = {
                "status": "done",
                "hash": digest,
                "output_path": item["output_path"],
                "updated_at": common.now_iso(),
                "bytes": output_path.stat().st_size,
            }
            converted += 1
        except Exception as exc:  # noqa: BLE001 - keep batch conversion resumable.
            message = str(exc)
            if "missingtitle" in message:
                missing += 1
                status = "missing_source_page"
            else:
                failed += 1
                status = "failed"
            state["items"][item["id"]] = {
                "status": status,
                "error": message,
                "updated_at": common.now_iso(),
            }
        common.write_json(STATE_PATH, state)

    common.status(f"converted={converted} skipped={skipped} missing={missing} failed={failed}", args.quiet)
    return 1 if failed else 0


def print_manifest_summary(manifest: dict) -> None:
    by_status = Counter(item["text_status"] for item in manifest["items"])
    print(f"Manifest: {MANIFEST_PATH}")
    print(f"Total items: {len(manifest['items'])}")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    for item in manifest["items"]:
        year = f" ({item['work_year']})" if item.get("work_year") else ""
        completion = item.get("wikisource_completion_percent")
        percent = f" [{completion}%]" if completion is not None else ""
        print(f"- {item['id']}: {item['title']}{year}{percent}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Latin Wikisource Spinoza texts to Markdown.")
    parser.add_argument("--resume", action="store_true", help="Skip completed items whose output hash still matches state")
    parser.add_argument("--force", action="store_true", help="Re-convert even completed items")
    parser.add_argument("--force-fetch", action="store_true", help="Ignore cached source responses")
    parser.add_argument("--only", help="Convert only one manifest item id")
    parser.add_argument("--limit", type=int, help="Convert only the first N manifest items")
    parser.add_argument("--dry-run", action="store_true", help="Build/print manifest but do not convert")
    parser.add_argument("--rebuild-manifest", action="store_true", help="Re-fetch author page and rebuild manifest")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress messages")
    args = parser.parse_args()

    manifest = build_manifest(rebuild=args.rebuild_manifest, quiet=args.quiet)
    if args.dry_run:
        print_manifest_summary(manifest)
        return 0
    return convert_items(args, manifest)


if __name__ == "__main__":
    raise SystemExit(main())

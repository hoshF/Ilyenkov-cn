#!/usr/bin/env python3
"""Audit generated Spinoza Markdown outputs and metadata."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys

import spinoza_common as common


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
import split_longform_markdown as longform  # noqa: E402

MANIFEST_PATH = common.METADATA_ROOT / "spinoza_catalog_manifest.json"
WIKISOURCE_STATE_PATH = common.METADATA_ROOT / "spinoza_wikisource_state.json"
DBNL_STATE_PATH = common.METADATA_ROOT / "spinoza_dbnl_state.json"
WEB_MANIFEST_PATH = common.METADATA_ROOT / "spinoza_web_manifest.json"
WEB_STATE_PATH = common.METADATA_ROOT / "spinoza_spinozaetnous_state.json"
PREFERRED_SOURCES_PATH = common.METADATA_ROOT / "preferred_sources.json"
NL_WIKISOURCE_STATE_PATH = common.METADATA_ROOT / "spinoza_nl_wikisource_state.json"
GAP_MANIFEST_PATH = common.METADATA_ROOT / "spinoza_gap_manifest.json"
CORPUS_POLICY_PATH = common.METADATA_ROOT / "corpus_policy.json"
ELEMENTS_PATH = common.METADATA_ROOT / "ethica_elements.json"
AUDIT_PATH = common.METADATA_ROOT / "source_audit.md"
WEB_ROOT = common.OUTPUT_ROOT / "latin_web" / "spinozaetnous"
PDF_ROOT = common.ARCHIVE_ROOT / "source_pdfs"
EXPECTED_WEB_WORKS = {
    "web-spinozaetnous-tractatus-theologico-politicus",
    "web-spinozaetnous-renati-descartes-principia-philosophiae",
    "web-spinozaetnous-cogitata-metaphysica",
    "web-spinozaetnous-tractatus-de-intellectus-emendatione",
    "web-spinozaetnous-ethica",
    "web-spinozaetnous-tractatus-politicus",
    "web-spinozaetnous-epistolae",
}
MISSING_LETTERS = [38, 42, 43, 49, 69, 84]
EXPECTED_PDFS = [
    "bruder-vol-i-1843.pdf",
    "bruder-vol-ii-1844.pdf",
    "bruder-vol-iii-1846.pdf",
]
REQUIRED_FRONT_MATTER = {
    "id",
    "type",
    "created",
    "author",
    "title",
    "language",
    "source_url",
    "source_site",
    "source_license",
    "work_year",
    "conversion_date",
    "text_status",
}


def audit_markdown(path: Path) -> list[str]:
    issues: list[str] = []
    if not longform.materialized_output_exists(path, root=PROJECT_ROOT):
        return [f"missing file: {path}"]
    text = longform.read_materialized_text(path, root=PROJECT_ROOT)
    front = common.front_matter_block(text)
    missing = REQUIRED_FRONT_MATTER - set(front)
    if not front:
        issues.append("missing front matter")
    if missing:
        issues.append(f"missing front matter keys: {', '.join(sorted(missing))}")
    if "source_revision_id" not in front and "source_file_id" not in front:
        issues.append("missing source_revision_id or source_file_id")
    if "Source: <" not in text:
        issues.append("missing Source link")
    for noise in ["Jump to content", "EPUB MOBI PDF RTF TXT", "Navigation menu"]:
        if noise in text:
            issues.append(f"possible navigation noise: {noise}")
    return issues


def audit_wikisource() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    manifest = common.read_json(MANIFEST_PATH, {})
    state = common.read_json(WIKISOURCE_STATE_PATH, {"items": {}})
    items = manifest.get("items", [])
    lines.append(f"- Wikisource manifest items: {len(items)}")
    done = 0
    for item in items:
        output = common.ARCHIVE_ROOT / item["output_path"]
        item_issues: list[str] = []
        state_item = state.get("items", {}).get(item["id"], {})
        if state_item.get("status") == "missing_source_page":
            lines.append(f"- Wikisource unavailable on source site: {item['id']}")
            continue
        item_issues.extend(audit_markdown(output))
        if state_item.get("status") != "done":
            item_issues.append(f"state not done: {state_item.get('status', 'missing')}")
        elif common.markdown_hash(longform.read_materialized_text(output, root=PROJECT_ROOT)) != state_item.get("hash"):
            item_issues.append("state hash mismatch")
        else:
            done += 1
        if item_issues:
            issues.extend([f"{item['id']}: {issue}" for issue in item_issues])
    lines.append(f"- Wikisource converted and hash-verified: {done}/{len(items)}")
    return lines, issues


def audit_dbnl() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    state = common.read_json(DBNL_STATE_PATH, {})
    output = common.OUTPUT_ROOT / "dutch" / "nagelate-schriften.md"
    item_issues = audit_markdown(output)
    if state.get("status") != "done":
        item_issues.append(f"state not done: {state.get('status', 'missing')}")
    elif longform.materialized_output_exists(output, root=PROJECT_ROOT) and common.markdown_hash(
        longform.read_materialized_text(output, root=PROJECT_ROOT)
    ) != state.get("hash"):
        item_issues.append("state hash mismatch")
    if item_issues:
        issues.extend([f"dbnl-nagelate-schriften: {issue}" for issue in item_issues])
    lines.append(f"- DBNL Nagelate schriften: {'ok' if not item_issues else 'issues found'}")
    return lines, issues


def audit_dutch_short_treatise() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    state = common.read_json(NL_WIKISOURCE_STATE_PATH, {})
    output = common.OUTPUT_ROOT / "dutch_web" / "nlwikisource" / "korte-verhandeling.md"
    item_issues = audit_markdown(output)
    if state.get("status") != "done":
        item_issues.append(f"state not done: {state.get('status', 'missing')}")
    elif output.exists() and common.markdown_hash(output.read_text(encoding="utf-8")) != state.get("hash"):
        item_issues.append("state hash mismatch")
    if output.exists():
        text = output.read_text(encoding="utf-8")
        for marker in [
            "## Het eerste DEEL, van GOD",
            "## Het twede DEEL van DE MENSCH",
            "### Cap. XXVI Van de waare vrijheid",
        ]:
            if marker not in text:
                item_issues.append(f"missing structure: {marker}")
    if item_issues:
        issues.extend([f"nlwikisource-korte-verhandeling: {issue}" for issue in item_issues])
    lines.append(f"- Dutch Wikisource Korte Verhandeling: {'ok' if not item_issues else 'issues found'}")
    return lines, issues


def audit_gap_manifest() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    data = common.read_json(GAP_MANIFEST_PATH, {"items": []})
    items = {item.get("id"): item for item in data.get("items", [])}
    expected = {
        "compendium-grammatices-linguae-hebraeae": "source_scans_and_chapter_structure_available_web_transcription_missing",
        "epistolae-source-gaps": "original_language_web_transcriptions_missing",
        "ultimi-barbarorum": "reported_lost_fragment_no_surviving_document",
    }
    for item_id, status in expected.items():
        if items.get(item_id, {}).get("status") != status:
            issues.append(f"gap manifest status missing or incorrect: {item_id}")
    if items.get("epistolae-source-gaps", {}).get("missing_gebhardt_numbers") != MISSING_LETTERS:
        issues.append("gap manifest letter-number list mismatch")
    lines.append(f"- Explicit unresolved text/fragment gaps recorded: {len(items)}")
    return lines, issues


def audit_corpus_policy() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    policy = common.read_json(CORPUS_POLICY_PATH, {})
    preferred = common.read_json(PREFERRED_SOURCES_PATH, {"works": {}}).get("works", {})
    if policy.get("default_llm_source_role") != "historically_attested_source_text":
        issues.append("corpus policy does not default to historically attested source text")

    core_latin = [
        "tractatus-theologico-politicus",
        "renati-descartes-principia-philosophiae",
        "cogitata-metaphysica",
        "tractatus-de-intellectus-emendatione",
        "ethica",
        "tractatus-politicus",
    ]
    for work_id in core_latin:
        item = preferred.get(work_id, {})
        if item.get("text_role") != "author_original" or item.get("core_corpus_eligible") is not True:
            issues.append(f"authorial-language work not core-corpus eligible: {work_id}")
        if item.get("llm_wiki_eligible") is not True:
            issues.append(f"authorial-language work not LLM-wiki eligible: {work_id}")

    non_core = {
        "nagelate-schriften": "historical_translation",
        "korte-verhandeling": "text_witness",
        "epistolae": "text_witness",
    }
    for work_id, role in non_core.items():
        item = preferred.get(work_id, {})
        if item.get("text_role") != role or item.get("core_corpus_eligible") is not False:
            issues.append(f"non-core textual layer classified incorrectly: {work_id}")
        if item.get("llm_wiki_eligible") is not True:
            issues.append(f"historical textual layer not LLM-wiki eligible: {work_id}")

    front_matter_expectations = {
        common.OUTPUT_ROOT / "dutch" / "nagelate-schriften.md": "historical_translation",
        common.OUTPUT_ROOT / "dutch_web" / "nlwikisource" / "korte-verhandeling.md": "text_witness",
        WEB_ROOT / "epistolae.md": "text_witness",
        WEB_ROOT / "ethica.md": "author_original",
    }
    for path, role in front_matter_expectations.items():
        if not longform.materialized_output_exists(path, root=PROJECT_ROOT):
            issues.append(f"missing policy-audited Markdown: {path}")
            continue
        front = common.front_matter_block(longform.read_materialized_text(path, root=PROJECT_ROOT))
        if front.get("text_role") != role:
            issues.append(f"incorrect text_role in {path.name}: {front.get('text_role')}")

    lines.append("- Corpus policy: authorial-language texts are strict core; attested early translations and witnesses are also LLM-wiki eligible")
    return lines, issues


def audit_web_spinozaetnous() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    manifest = common.read_json(WEB_MANIFEST_PATH, {"items": []})
    state = common.read_json(WEB_STATE_PATH, {"items": {}})
    preferred = common.read_json(PREFERRED_SOURCES_PATH, {"works": {}})
    manifest_items = {item.get("id"): item for item in manifest.get("items", [])}
    state_items = state.get("items", {})
    done = 0
    for item_id in sorted(EXPECTED_WEB_WORKS):
        item = manifest_items.get(item_id)
        state_item = state_items.get(item_id, {})
        if not item:
            issues.append(f"{item_id}: missing from web manifest")
            continue
        if state_item.get("status") != "done":
            issues.append(f"{item_id}: state not done: {state_item.get('status', 'missing')}")
            continue
        output_path = common.ARCHIVE_ROOT / item.get("output_path", "")
        item_issues = audit_markdown(output_path)
        if longform.materialized_output_exists(output_path, root=PROJECT_ROOT) and common.markdown_hash(
            longform.read_materialized_text(output_path, root=PROJECT_ROOT)
        ) != state_item.get("hash"):
            item_issues.append("state hash mismatch")
        if item_issues:
            issues.extend([f"{item_id}: {issue}" for issue in item_issues])
        else:
            done += 1

    ttp = longform.read_materialized_text(WEB_ROOT / "tractatus-theologico-politicus.md", root=PROJECT_ROOT)
    ttp_headers = re.findall(r"^## Tractatus theologico-politicus/(.+)$", ttp, re.MULTILINE)
    expected_ttp = ["Praefatio"] + [f"Caput {roman}" for roman in (
        "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
        "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    )]
    if ttp_headers != expected_ttp:
        issues.append(f"TTP page coverage mismatch: {ttp_headers}")

    ppc = (WEB_ROOT / "renati-descartes-principia-philosophiae.md").read_text(encoding="utf-8")
    ppc_headers = re.findall(r"^## Renati Descartes Principia philosophiae/(.+)$", ppc, re.MULTILINE)
    if ppc_headers != ["Praefatio", "Pars I", "Pars II", "Pars III"]:
        issues.append(f"PPC page coverage mismatch: {ppc_headers}")

    ethica = (WEB_ROOT / "ethica.md").read_text(encoding="utf-8")
    ethica_headers = re.findall(r"^## Ethica - (Pars [IVX]+)$", ethica, re.MULTILINE)
    if ethica_headers != ["Pars I", "Pars II", "Pars III", "Pars IV", "Pars V"]:
        issues.append(f"Ethica web page coverage mismatch: {ethica_headers}")

    tp = (WEB_ROOT / "tractatus-politicus.md").read_text(encoding="utf-8")
    tp_chapters = [int(number) for number in re.findall(r"^#{1,6}\s+Caput\s+(\d+)\s*$", tp, re.MULTILINE | re.IGNORECASE)]
    if tp_chapters != list(range(1, 12)):
        issues.append(f"TP chapter coverage mismatch: {tp_chapters}")
    if "Reliqua desiderantur" not in tp:
        issues.append("TP missing Reliqua desiderantur")

    letter_state = state_items.get("web-spinozaetnous-epistolae", {})
    letter_hashes = letter_state.get("letter_hashes", {})
    if letter_state.get("letter_count") != 80 or len(letter_hashes) != 80:
        issues.append("Epistolae does not contain 80 split letter files")
    if letter_state.get("missing_letters") != MISSING_LETTERS:
        issues.append(f"Epistolae missing-number list mismatch: {letter_state.get('missing_letters')}")
    for relative_path, expected_hash in letter_hashes.items():
        path = common.ARCHIVE_ROOT / relative_path
        letter_issues = audit_markdown(path)
        if path.exists() and common.markdown_hash(path.read_text(encoding="utf-8")) != expected_hash:
            letter_issues.append("state hash mismatch")
        issues.extend([f"{path.name}: {issue}" for issue in letter_issues])
    for required in ["epistola-012-bis.md", "epistola-067-bis.md"]:
        if not (WEB_ROOT / "epistolae" / required).exists():
            issues.append(f"Epistolae missing split file: {required}")
    for number in MISSING_LETTERS:
        if (WEB_ROOT / "epistolae" / f"epistola-{number:03d}.md").exists():
            issues.append(f"Epistolae unexpectedly contains declared-missing letter {number}")

    for path in WEB_ROOT.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        definitions = re.findall(r"^\[\^([^]]+)\]:", text, re.MULTILINE)
        duplicates = sorted(name for name, count in Counter(definitions).items() if count > 1)
        if duplicates:
            issues.append(f"{path.name}: duplicate footnote definitions: {', '.join(duplicates[:5])}")
        for noise in ["Traité théologico-politique", "Autres œuvres", "Plan de l’Éthique"]:
            if noise in text:
                issues.append(f"{path.name}: possible Spinoza et Nous navigation noise: {noise}")

    compendium = manifest_items.get("web-spinozaetnous-compendium-grammatices-linguae-hebraeae", {})
    if compendium.get("status") != "source_pdf_available_web_transcription_missing":
        issues.append("Compendium manifest gap status missing or incorrect")
    preferred_compendium = preferred.get("works", {}).get("compendium-grammatices-linguae-hebraeae", {})
    if preferred_compendium.get("preferred_markdown"):
        issues.append("Compendium preferred source must not point to Markdown")

    lines.append(f"- Spinoza et Nous web works converted and hash-verified: {done}/{len(EXPECTED_WEB_WORKS)}")
    lines.append(f"- Epistolae split files: {len(letter_hashes)} (missing source numbers: {', '.join(map(str, MISSING_LETTERS))})")
    lines.append("- Compendium: source PDF retained; web transcription and Markdown unavailable")
    return lines, issues


def audit_reference_pdfs() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    present = 0
    for filename in EXPECTED_PDFS:
        path = PDF_ROOT / filename
        if not path.exists():
            issues.append(f"missing reference PDF: {filename}")
        elif path.stat().st_size == 0:
            issues.append(f"empty reference PDF: {filename}")
        else:
            present += 1
    lines.append(f"- Bruder reference PDFs retained: {present}/{len(EXPECTED_PDFS)}")
    return lines, issues


def audit_ethica() -> tuple[list[str], list[str]]:
    lines: list[str] = []
    issues: list[str] = []
    data = common.read_json(ELEMENTS_PATH, {})
    elements = data.get("elements", [])
    counter = Counter(element.get("type") for element in elements)
    parts = sorted({element.get("part") for element in elements if element.get("part")})
    lines.append(f"- Ethica structured elements: {len(elements)}")
    lines.append(f"- Ethica parts detected: {', '.join(map(str, parts)) or 'none'}")
    lines.append("- Ethica element types: " + ", ".join(f"{k}={v}" for k, v in sorted(counter.items())))
    if parts != [1, 2, 3, 4, 5]:
        issues.append("Ethica does not contain detected parts 1-5")
    for required in ["definition", "axiom", "proposition", "demonstration", "scholium"]:
        if counter.get(required, 0) == 0:
            issues.append(f"Ethica missing detected element type: {required}")
    if not (common.OUTPUT_ROOT / "latin" / "ethica-structured.md").exists():
        issues.append("missing ethica-structured.md")
    return lines, issues


def main() -> int:
    report: list[str] = [
        "---",
        'title: "Spinoza Source Audit"',
        'created: "' + common.now_iso()[:10] + '"',
        'type: "analysis"',
        'tags: ["spinoza", "source-metadata", "audit"]',
        'language: "en"',
        'collection: "corpus-metadata"',
        'llm_wiki_eligible: "true"',
        "---",
        "",
        "# Spinoza Source Audit",
        "",
        f"Generated at: {common.now_iso()}",
        "",
        "## Automated Checks",
        "",
    ]
    issues: list[str] = []
    for lines, found_issues in [
        audit_wikisource(),
        audit_dbnl(),
        audit_dutch_short_treatise(),
        audit_web_spinozaetnous(),
        audit_gap_manifest(),
        audit_corpus_policy(),
        audit_reference_pdfs(),
        audit_ethica(),
    ]:
        report.extend(lines)
        issues.extend(found_issues)
    report.extend(
        [
            "",
            "## Critical-Edition Sampling",
            "",
            "- Gebhardt 1925 `Spinoza Opera` PDF: reference source for future manual/automated sampling.",
            "- 1677 `Opera posthuma` and `Nagelate Schriften` scans: reference sources for future page-level checks.",
            "- This v1 audit verifies generated files, metadata, hashes, and Ethics structure; it does not claim full critical collation.",
            "",
            "## Issues",
            "",
        ]
    )
    if issues:
        report.extend(f"- {issue}" for issue in issues)
    else:
        report.append("- None found by automated audit.")
    common.atomic_write(AUDIT_PATH, "\n".join(report).rstrip() + "\n")
    print(f"wrote {AUDIT_PATH}")
    print(f"issues={len(issues)}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build stable element IDs for the generated Latin Ethics Markdown."""

from __future__ import annotations

import json
import re
from pathlib import Path

import spinoza_common as common


INPUT_PATH = common.OUTPUT_ROOT / "latin" / "ethica.md"
OUTPUT_PATH = common.OUTPUT_ROOT / "latin" / "ethica-structured.md"
ELEMENTS_PATH = common.METADATA_ROOT / "ethica_elements.json"

ROMAN = {
    "i": 1,
    "ii": 2,
    "iii": 3,
    "iv": 4,
    "v": 5,
    "vi": 6,
    "vii": 7,
    "viii": 8,
    "ix": 9,
    "x": 10,
    "xi": 11,
    "xii": 12,
    "xiii": 13,
    "xiv": 14,
    "xv": 15,
    "xvi": 16,
    "xvii": 17,
    "xviii": 18,
    "xix": 19,
    "xx": 20,
}
PART_WORDS = {"prima": 1, "secunda": 2, "tertia": 3, "quarta": 4, "quinta": 5}
PART_URL_WORDS = {"prima": 1, "secunda": 2, "tertia": 3, "quarta": 4, "quinta": 5}


def number_from_token(token: str) -> int | None:
    token = token.strip().strip(".").lower()
    if token.isdigit():
        return int(token)
    return ROMAN.get(token)


def detect_part(text: str) -> int | None:
    lower = text.lower()
    match = re.search(r"\bpars\s+(prima|secunda|tertia|quarta|quinta|i{1,3}|iv|v)\b", lower)
    if not match:
        return None
    token = match.group(1)
    return PART_WORDS.get(token) or number_from_token(token)


def detect_part_source_marker(text: str) -> int | None:
    lower = text.lower()
    if not lower.startswith("source part page:"):
        return None
    match = re.search(r"ethica(?:%2f|/)pars[_\s-]+(prima|secunda|tertia|quarta|quinta)", lower)
    if not match:
        return None
    return PART_URL_WORDS[match.group(1)]


def mark_part(current: dict, part: int) -> tuple[str, str] | None:
    current["part"] = part
    current["proposition"] = None
    current["section"] = None
    current["corollarium_count"] = 0
    seen = current.setdefault("parts_seen", set())
    if part in seen:
        return None
    seen.add(part)
    return f"E{part}", "part"


def classify_text_marker(text: str, current: dict) -> tuple[str, str] | None:
    clean = re.sub(r"\s+", " ", text).strip()
    lower = clean.lower().strip("* ")
    part = current.get("part")

    source_part = detect_part_source_marker(clean)
    if source_part:
        return mark_part(current, source_part)

    maybe_part = detect_part(clean)
    if maybe_part:
        return mark_part(current, maybe_part)

    part = current.get("part")
    if not part:
        return None

    if re.fullmatch(r"\**\s*definitiones\s*\**", lower):
        current["section"] = "definition"
        return f"E{part}DefSection", "definition_section"

    if re.fullmatch(r"\**\s*axiomata\s*\**", lower):
        current["section"] = "axiom"
        return f"E{part}AxiomSection", "axiom_section"

    if re.fullmatch(r"\**\s*postulata\s*\**", lower):
        current["section"] = "postulate"
        return f"E{part}PostSection", "postulate_section"

    if current.get("section") in {"definition", "axiom", "postulate"}:
        numbered = re.match(r"^([ivxlcdm\d]+)\.\s+", lower)
        if numbered:
            n = number_from_token(numbered.group(1))
            if n:
                prefix = {"definition": "D", "axiom": "A", "postulate": "Post"}[current["section"]]
                return f"E{part}{prefix}{n}", current["section"]

    match = re.search(r"\bdefinitio(?:nes)?\s*([ivxlcdm\d]+)?", lower)
    if match and match.group(1):
        n = number_from_token(match.group(1))
        if n:
            return f"E{part}D{n}", "definition"

    match = re.search(r"\baxioma(?:ta)?\s*([ivxlcdm\d]+)?", lower)
    if match and match.group(1):
        n = number_from_token(match.group(1))
        if n:
            return f"E{part}A{n}", "axiom"

    match = re.search(r"\bpropositio\s+([ivxlcdm\d]+)", lower)
    if match:
        n = number_from_token(match.group(1))
        if n:
            current["proposition"] = n
            current["section"] = None
            current["corollarium_count"] = 0
            return f"E{part}P{n}", "proposition"

    proposition = current.get("proposition")
    if proposition:
        if re.fullmatch(r"\**\s*demonstratio\.?\s*\**", lower):
            return f"E{part}P{proposition}Dem", "demonstration"
        if re.fullmatch(r"\**\s*scholium\.?\s*\**", lower):
            return f"E{part}P{proposition}Schol", "scholium"
        if re.fullmatch(r"\**\s*corollarium\.?\s*\**", lower):
            current["corollarium_count"] = current.get("corollarium_count", 0) + 1
            suffix = "Cor" if current["corollarium_count"] == 1 else f"Cor{current['corollarium_count']}"
            return f"E{part}P{proposition}{suffix}", "corollary"

    if "appendix" in lower or "appendice" in lower:
        return f"E{part}App", "appendix"

    match = re.search(r"\blemma\s+([ivxlcdm\d]+)", lower)
    if match:
        n = number_from_token(match.group(1))
        if n:
            return f"E{part}L{n}", "lemma"

    match = re.search(r"\bpostulatum\s+([ivxlcdm\d]+)", lower)
    if match:
        n = number_from_token(match.group(1))
        if n:
            return f"E{part}Post{n}", "postulate"

    return None


def build_structure(markdown: str) -> tuple[str, list[dict]]:
    lines = markdown.splitlines()
    current = {"part": None, "proposition": None, "section": None, "corollarium_count": 0, "parts_seen": set()}
    seen_ids: dict[str, int] = {}
    elements: list[dict] = []
    out: list[str] = []
    current_element_index: int | None = None
    in_front_matter = False

    for line_number, line in enumerate(lines, start=1):
        if line_number == 1 and line.strip() == "---":
            in_front_matter = True
            out.append(line)
            continue
        if in_front_matter:
            out.append(line)
            if line.strip() == "---":
                in_front_matter = False
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        marker_text = heading_match.group(2) if heading_match else line
        classified = classify_text_marker(marker_text, current)
        if classified:
            element_id, element_type = classified
            seen_ids[element_id] = seen_ids.get(element_id, 0) + 1
            if seen_ids[element_id] > 1:
                element_id = f"{element_id}_{seen_ids[element_id]}"
            out.append(f"<!-- element_id: {element_id} -->")
            elements.append(
                {
                    "id": element_id,
                    "type": element_type,
                    "part": current.get("part"),
                    "title": re.sub(r"^#{1,6}\s+", "", marker_text).strip(),
                    "start_line": line_number,
                }
            )
            if current_element_index is not None:
                elements[current_element_index]["end_line"] = line_number - 1
            current_element_index = len(elements) - 1
        out.append(line)

    if current_element_index is not None:
        elements[current_element_index]["end_line"] = len(lines)
    return "\n".join(out).rstrip() + "\n", elements


def main() -> int:
    if not INPUT_PATH.exists():
        raise SystemExit(f"Missing input file: {INPUT_PATH}")
    markdown = INPUT_PATH.read_text(encoding="utf-8")
    structured, elements = build_structure(markdown)
    structured = structured.replace(
        'id: "ethica"\n',
        'id: "ethica-structured"\nbase_text_id: "ethica"\ntext_variant: "structured-elements"\n',
        1,
    )
    common.atomic_write(OUTPUT_PATH, structured)
    common.write_json(
        ELEMENTS_PATH,
        {
            "source_markdown": common.relative_to_archive(INPUT_PATH),
            "structured_markdown": common.relative_to_archive(OUTPUT_PATH),
            "generated_at": common.now_iso(),
            "element_count": len(elements),
            "elements": elements,
        },
    )
    print(f"wrote {OUTPUT_PATH}")
    print(f"elements={len(elements)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

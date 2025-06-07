"""Fetch reliability tables from various WikiProject pages."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from typing import List, Optional

import requests
import mwparserfromhell

from scripts.common import HEADERS
from scripts.fetch_perennial_sources import (
    SourceEntry,
    STATUS_MAP,
    clean_source_name,
)

MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"
PAGES = [
    "Wikipedia:WikiProject_Video_games/Sources",
    "Wikipedia:WikiProject_Film/Resources",
    "Wikipedia:WikiProject_Albums/Sources",
    "Wikipedia:WikiProject_Christian_music/Sources",
    "Wikipedia:WikiProject_Professional_wrestling/Sources",
    "Wikipedia:WikiProject_Korea/Reliable_sources",
]


def fetch_page(title: str) -> str:
    """Fetch raw wikitext for a WikiProject page."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
    }
    response = requests.get(MEDIAWIKI_API, params=params, timeout=30, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    return page.get("revisions", [])[0]["*"] if "revisions" in page else ""


def _status_from_heading(text: str) -> Optional[str]:
    """Return the reliability code if the heading text matches a status."""
    text = text.lower()
    # Check longer phrases first to avoid matching "reliable" inside
    # "unreliable" headings.
    order = [
        "generally unreliable",
        "unreliable",
        "generally reliable",
        "reliable",
        "no consensus",
        "deprecated",
        "blacklisted",
        "marginally reliable",
    ]
    for key in order:
        if key in text:
            return STATUS_MAP.get(key)
    return None


def _parse_bullet_line(line: str) -> tuple[str, str]:
    """Return ``(name, notes)`` from a bullet line."""

    text = line.lstrip("*#").strip()
    dash_variants = [" – ", " -- ", " — ", " - ", "—", "–", "-"]
    name_part = text
    notes_part = ""
    for dash in dash_variants:
        if dash in text:
            name_part, notes_part = text.split(dash, 1)
            break
    name = clean_source_name(mwparserfromhell.parse(name_part).strip_code().strip())
    notes = mwparserfromhell.parse(notes_part).strip_code().strip()
    return name, notes


def _parse_table(table_text: str, status: Optional[str]) -> List[SourceEntry]:
    """Return entries extracted from a wikitext table."""

    code = mwparserfromhell.parse(table_text)
    result: List[SourceEntry] = []
    for row in code.filter_tags(matches=lambda t: t.tag == "tr"):
        cells = row.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"))
        if not cells:
            continue
        text = cells[0].contents.strip_code().strip()
        if text.lower() in {"name", "publication", "source"}:
            continue
        name = clean_source_name(text)
        notes = mwparserfromhell.parse(cells[-1].contents).strip_code().strip()
        row_status = status
        if row_status is None:
            class_attr = row.get("class") if row.has("class") else None
            if class_attr:
                class_value = str(class_attr.value)
                if "ko-rel" in class_value:
                    row_status = "gr"
                elif "ko-unrel" in class_value:
                    row_status = "gu"
                elif "ko-nocon" in class_value:
                    row_status = "nc"
                elif "ko-b" in class_value:
                    row_status = "d"
        result.append(
            SourceEntry(
                source_name=name,
                reliability_status=row_status,
                notes=notes,
            )
        )
    return result


def parse_page(wikitext: str) -> List[SourceEntry]:
    """Parse reliability tables and bullet/numbered lists from wikitext."""

    entries: List[SourceEntry] = []
    current_status: Optional[str] = None

    lines = iter(wikitext.splitlines())
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("="):
            heading = mwparserfromhell.parse(stripped).strip_code().strip()
            status = _status_from_heading(heading)
            if status:
                current_status = status
            continue

        if stripped.startswith("{|"):
            table_lines = [line]
            for next_line in lines:
                table_lines.append(next_line)
                if next_line.strip().startswith("|}"):
                    break
            entries.extend(_parse_table("\n".join(table_lines), current_status))
            continue

        marker = stripped.lstrip("#:*")
        prefix = stripped[: len(stripped) - len(marker)]
        if prefix and prefix[0] in "*#":
            name, notes = _parse_bullet_line(stripped)
            if name:
                entries.append(
                    SourceEntry(
                        source_name=name,
                        reliability_status=current_status,
                        notes=notes,
                    )
                )

    return entries


def fetch_all() -> List[SourceEntry]:
    """Download and parse all configured WikiProject pages."""
    entries: List[SourceEntry] = []
    for title in PAGES:
        text = fetch_page(title)
        entries.extend(parse_page(text))
    return entries


def save_to_json(entries: List[SourceEntry], path: str) -> None:
    """Write entries to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(e) for e in entries], fh, ensure_ascii=False, indent=2)


def save_to_csv(entries: List[SourceEntry], path: str) -> None:
    """Write entries to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["source_name", "reliability_status", "notes"]
        )
        writer.writeheader()
        for e in entries:
            writer.writerow(asdict(e))


def main() -> None:
    """Fetch WikiProject tables and output JSON and CSV files."""
    entries = fetch_all()
    print(f"Fetched {len(entries)} sources")
    save_to_json(entries, "wikiproject_sources.json")
    save_to_csv(entries, "wikiproject_sources.csv")


if __name__ == "__main__":
    main()


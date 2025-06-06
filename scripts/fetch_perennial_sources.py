"""Utilities for working with Wikipedia's Perennial sources page.

This implements phases 1–3 of ``docs/roadmap.md``:

* Fetch raw wikitext for each Perennial sources subpage via the MediaWiki API.
* Parse the wikitables into structured :class:`SourceEntry` records.
* Provide a small CLI to output the resulting list as JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
import mwparserfromhell

MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"
BASE_TITLE = "Wikipedia:Reliable_sources/Perennial_sources"

@dataclass
class SourceEntry:
    source_name: str
    reliability_status: Optional[str] = None
    notes: Optional[str] = None
    applies_to: Optional[str] = None


def fetch_subpage(title: str) -> str:
    """Fetch raw wikitext for a given subpage."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "content",
        "titles": title,
    }
    response = requests.get(MEDIAWIKI_API, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    return page.get("revisions", [])[0]["*"] if "revisions" in page else ""


def extract_rows(wikitext: str) -> List[str]:
    """Return raw wikitext rows from a perennial sources subpage."""
    if "<onlyinclude>" in wikitext:
        wikitext = wikitext.split("<onlyinclude>", 1)[1].split("</onlyinclude>", 1)[0]
    rows = wikitext.split("\n|- ")
    return rows[1:]


def _split_cells(row: str) -> List[str]:
    """Split a row string into individual cell strings."""
    lines = row.split("\n")
    cells: List[str] = []
    current = ""
    for line in lines[1:]:  # skip the row attributes
        if line.startswith("|"):
            if current:
                cells.append(current)
            current = line[1:].strip()
        else:
            current += " " + line.strip()
    if current:
        cells.append(current)
    return cells


def parse_row(row: str) -> SourceEntry:
    """Parse a single wikitext table row into :class:`SourceEntry`."""
    cells = _split_cells(row)
    if len(cells) < 6:
        raise ValueError("unexpected row structure")

    source_name = mwparserfromhell.parse(cells[0]).strip_code().strip()
    status_templates = mwparserfromhell.parse(cells[1]).filter_templates()
    reliability_status = None
    if status_templates:
        param = status_templates[0].params[0].value
        reliability_status = param.strip_code().strip()

    notes = mwparserfromhell.parse(cells[4]).strip_code().strip()
    applies_to = mwparserfromhell.parse(cells[5]).strip_code().strip()

    return SourceEntry(
        source_name=source_name,
        reliability_status=reliability_status,
        notes=notes,
        applies_to=applies_to,
    )


def fetch_all() -> List[SourceEntry]:
    """Fetch and parse all perennial source subpages."""
    entries: List[SourceEntry] = []
    for i in range(1, 9):
        subpage_title = f"{BASE_TITLE}/{i}"
        wikitext = fetch_subpage(subpage_title)
        for raw in extract_rows(wikitext):
            try:
                entries.append(parse_row(raw))
            except Exception:
                continue
    return entries


def save_to_json(entries: List[SourceEntry], path: str) -> None:
    """Save extracted entries to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(e) for e in entries], fh, ensure_ascii=False, indent=2)


def main() -> None:
    """Fetch the perennial sources tables and write them to JSON."""
    entries = fetch_all()
    print(f"Fetched {len(entries)} sources")
    save_to_json(entries, "perennial_sources.json")


if __name__ == "__main__":
    main()

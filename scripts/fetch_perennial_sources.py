"""Utilities for working with Wikipedia's Perennial sources page."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import List, Optional

import requests
import mwparserfromhell

MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"
TITLE = "Wikipedia:Reliable_sources/Perennial_sources"

@dataclass
class SourceEntry:
    source_name: str
    reliability_status: Optional[str] = None
    notes: Optional[str] = None
    applies_to: Optional[str] = None


def fetch_wikitext() -> str:
    """Fetch raw wikitext for the perennial sources page."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "content",
        "titles": TITLE,
    }
    response = requests.get(MEDIAWIKI_API, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    return page.get("revisions", [])[0]["*"] if "revisions" in page else ""


def parse_tables(wikitext: str) -> List[List[str]]:
    """Extract wikitable rows as lists of cell strings."""
    wikicode = mwparserfromhell.parse(wikitext)
    tables = wikicode.filter_tags(matches=lambda node: node.tag == "table" and "wikitable" in node.get("class", []))
    extracted = []
    for table in tables:
        table_code = mwparserfromhell.parse(str(table))
        for row in table_code.filter_tags(matches=lambda n: n.tag == "tr"):
            cells = [c.strip_code().strip() for c in mwparserfromhell.parse(str(row)).filter_tags(matches=lambda n: n.tag in ("td", "th"))]
            extracted.append(cells)
    return extracted


def save_to_json(entries: List[SourceEntry], path: str) -> None:
    """Save extracted entries to a JSON file."""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump([asdict(e) for e in entries], fh, ensure_ascii=False, indent=2)


def main() -> None:
    """Fetch the page and print the number of tables found."""
    wikitext = fetch_wikitext()
    tables = parse_tables(wikitext)
    print(f"Found {len(tables)} table rows")


if __name__ == "__main__":
    main()

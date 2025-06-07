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
    text = text.lower()
    for key, value in STATUS_MAP.items():
        if key in text:
            return value
    return None


def parse_page(wikitext: str) -> List[SourceEntry]:
    """Parse wikitables on a WikiProject page into ``SourceEntry`` records."""
    code = mwparserfromhell.parse(wikitext)
    entries: List[SourceEntry] = []
    current_status: Optional[str] = None
    for node in code.nodes:
        if isinstance(node, mwparserfromhell.nodes.heading.Heading):
            status = _status_from_heading(node.title.strip_code().strip())
            if status:
                current_status = status
        elif isinstance(node, mwparserfromhell.nodes.tag.Tag) and node.tag == "table":
            for row in node.contents.filter_tags(matches=lambda t: t.tag == "tr"):
                cells = row.contents.filter_tags(matches=lambda t: t.tag in ("td", "th"))
                if not cells or cells[0].tag == "th":
                    continue
                text = cells[0].contents.strip_code().strip()
                if text.lower() in {"name", "publication", "source"}:
                    continue
                name = clean_source_name(text)
                notes = mwparserfromhell.parse(cells[-1].contents).strip_code().strip()
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


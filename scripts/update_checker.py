"""Check Wikipedia for updates to the perennial sources tables.

This implements phase 6 of ``docs/roadmap.md``:
* Check each perennial sources subpage via the MediaWiki API.
* If the revision ID has changed since the last run, re-fetch and
  regenerate ``perennial_sources.json`` and ``perennial_sources.csv``.
"""

from __future__ import annotations

import json
import os
from typing import Dict

import requests
from scripts.common import HEADERS

from fetch_perennial_sources import (
    BASE_TITLE,
    MEDIAWIKI_API,
    clean_entries,
    fetch_all,
    save_to_csv,
    save_to_json,
    validate_entries,
)

REV_FILE = "revision_ids.json"


def fetch_revision_id(title: str) -> int:
    """Return the latest revision ID for a given page title."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "rvprop": "ids",
        "titles": title,
    }
    r = requests.get(MEDIAWIKI_API, params=params, timeout=30, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))
    return page.get("revisions", [])[0]["revid"]


def load_revision_ids() -> Dict[str, int]:
    if os.path.exists(REV_FILE):
        with open(REV_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_revision_ids(ids: Dict[str, int]) -> None:
    with open(REV_FILE, "w", encoding="utf-8") as fh:
        json.dump(ids, fh, indent=2)


def main() -> None:
    prev_ids = load_revision_ids()
    new_ids: Dict[str, int] = {}
    changed = False

    for i in range(1, 9):
        title = f"{BASE_TITLE}/{i}"
        revid = fetch_revision_id(title)
        new_ids[title] = revid
        if prev_ids.get(title) != revid:
            changed = True

    if not changed:
        print("No updates detected.")
        return

    entries = fetch_all()
    entries = clean_entries(entries)
    validate_entries(entries)
    print(f"Fetched {len(entries)} sources")
    save_to_json(entries, "perennial_sources.json")
    save_to_csv(entries, "perennial_sources.csv")
    save_revision_ids(new_ids)


if __name__ == "__main__":
    main()

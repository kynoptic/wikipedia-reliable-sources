"""Fetch lists of good and featured articles from Wikipedia categories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import requests
from scripts.common import HEADERS


API_URL = "https://en.wikipedia.org/w/api.php"


def _fetch_category_members(category: str) -> List[str]:
    """Return all article titles in a Wikipedia category."""
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": "max",
        "format": "json",
    }
    titles: List[str] = []
    while True:
        resp = requests.get(
            API_URL, params=params, timeout=10, headers=HEADERS
        )
        resp.raise_for_status()
        data = resp.json()
        members = data.get("query", {}).get("categorymembers", [])
        titles.extend(m["title"] for m in members if m.get("ns") == 0)
        cont = data.get("continue")
        if not cont:
            break
        # Continue fetching additional pages using the API-provided parameters
        params.update(cont)
    return titles


def fetch_good_and_featured(output_dir: Path) -> None:
    """Fetch article lists and write them under ``output_dir`` as JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)
    good = _fetch_category_members("Good articles")
    featured = _fetch_category_members("Featured articles")

    (output_dir / "good_articles.json").write_text(json.dumps(good, indent=2))
    (output_dir / "featured_articles.json").write_text(
        json.dumps(featured, indent=2)
    )


if __name__ == "__main__":
    fetch_good_and_featured(Path("data/raw"))

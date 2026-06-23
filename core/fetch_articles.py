"""Fetch lists of good and featured articles from Wikipedia categories."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

import requests
from scripts.common import HEADERS


API_URL = "https://en.wikipedia.org/w/api.php"

_CSV_FIELDS = ["number", "title", "pageid", "namespace", "length", "touched"]


def _fetch_category_members(category: str) -> List[dict]:
    """Return ``{"pageid", "title"}`` records for articles in a category.

    Page ids are returned as strings so they join directly against the
    ``page_id`` column of the citation dumps.
    """
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmprop": "ids|title",
        "cmlimit": "max",
        "format": "json",
    }
    members: List[dict] = []
    while True:
        resp = requests.get(
            API_URL, params=params, timeout=10, headers=HEADERS
        )
        resp.raise_for_status()
        data = resp.json()
        page = data.get("query", {}).get("categorymembers", [])
        members.extend(
            {"pageid": str(m["pageid"]), "title": m["title"]}
            for m in page
            if m.get("ns") == 0
        )
        cont = data.get("continue")
        if not cont:
            break
        # Continue fetching additional pages using the API-provided parameters
        params.update(cont)
    return members


def _write_csv(members: List[dict], path: Path) -> None:
    """Write members as a join-ready CSV matching the citation-dump schema."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
        writer.writeheader()
        for number, member in enumerate(members, start=1):
            writer.writerow(
                {
                    "number": number,
                    "title": member["title"],
                    "pageid": member["pageid"],
                    "namespace": "",
                    "length": "",
                    "touched": "",
                }
            )


def fetch_good_and_featured(output_dir: Path) -> None:
    """Fetch article lists and write title-only JSON plus page-id CSVs.

    The JSON files keep the title-only shape consumed by
    :mod:`core.fetch_wikitext`; the CSVs add page ids so the lists can be joined
    against citation dumps by :func:`core.process_citations.load_article_ids`.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    good = _fetch_category_members("Good articles")
    featured = _fetch_category_members("Featured articles")

    (output_dir / "good_articles.json").write_text(
        json.dumps([m["title"] for m in good], indent=2)
    )
    (output_dir / "featured_articles.json").write_text(
        json.dumps([m["title"] for m in featured], indent=2)
    )
    _write_csv(good, output_dir / "good-articles.csv")
    _write_csv(featured, output_dir / "featured-articles.csv")


if __name__ == "__main__":
    fetch_good_and_featured(Path("data/raw"))

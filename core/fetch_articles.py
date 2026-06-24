"""Fetch lists of good and featured articles from Wikipedia categories."""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import List

import requests
from scripts.common import HEADERS


API_URL = "https://en.wikipedia.org/w/api.php"

_CSV_FIELDS = ["number", "title", "pageid", "namespace", "length", "touched"]

_MAX_RETRIES = 6
_BASE_DELAY = 1.0
_PAGE_DELAY = 0.2  # politeness pause between paginated requests


def _api_get(params: dict) -> dict:
    """GET the MediaWiki API, backing off on rate-limit responses (429/503).

    Large categories require many paginated requests; the API rate-limits rapid
    bursts, so retry with exponential backoff (honoring ``Retry-After``).
    """
    delay = _BASE_DELAY
    resp = None
    for _ in range(_MAX_RETRIES):
        resp = requests.get(API_URL, params=params, timeout=30, headers=HEADERS)
        if resp.status_code in (429, 503):
            try:
                wait = float(resp.headers.get("Retry-After", ""))
            except ValueError:
                wait = delay
            time.sleep(wait)
            delay = min(delay * 2, 30.0)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()  # retries exhausted; 429/503 always raises here
    return resp.json()  # unreachable, kept for return-type completeness


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
        data = _api_get(params)
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
        time.sleep(_PAGE_DELAY)
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


PETSCAN_URL = "https://petscan.wmcloud.org/"


def fetch_petscan_csv(category: str, depth: int = 0) -> str:
    """Return a category's full member list as PetScan CSV in one request.

    PetScan runs the category query server-side and returns every member as a
    single ``number,title,pageid,namespace,length,touched`` CSV — avoiding the
    ~500-per-request pagination (and rate limits) of the categorymembers API.
    """
    params = {
        "language": "en",
        "project": "wikipedia",
        "categories": category,
        "depth": str(depth),
        "ns[0]": "1",
        "format": "csv",
        "doit": "1",
    }
    resp = requests.get(PETSCAN_URL, params=params, timeout=180, headers=HEADERS)
    resp.raise_for_status()
    return resp.text


def fetch_fa_ga_petscan(output_dir: Path) -> None:
    """Write current Featured/Good article CSVs via PetScan (one request each)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "featured-articles.csv").write_text(
        fetch_petscan_csv("Featured articles")
    )
    (output_dir / "good-articles.csv").write_text(
        fetch_petscan_csv("Good articles")
    )


if __name__ == "__main__":
    fetch_fa_ga_petscan(Path("data/raw/citations/current"))

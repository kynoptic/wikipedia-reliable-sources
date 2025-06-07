"""Download article wikitext using the MediaWiki API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import requests
from scripts.common import HEADERS

API_URL = "https://en.wikipedia.org/w/api.php"


def _fetch_single(title: str) -> str:
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": 2,
        "format": "json",
    }
    resp = requests.get(API_URL, params=params, timeout=10, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", [])
    if pages and "revisions" in pages[0]:
        return pages[0]["revisions"][0]["slots"]["main"].get("content", "")
    return ""


def fetch_wikitext(article_list: Iterable[str], output_dir: Path) -> None:
    """Fetch wikitext for each article in ``article_list``."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for title in article_list:
        content = _fetch_single(title)
        fname = title.replace("/", "_") + ".txt"
        (output_dir / fname).write_text(content)


if __name__ == "__main__":
    articles_path = Path("data/raw/good_articles.json")
    if articles_path.exists():
        articles = json.loads(articles_path.read_text())
    else:
        articles = []
    fetch_wikitext(articles, Path("data/raw/wikitext"))

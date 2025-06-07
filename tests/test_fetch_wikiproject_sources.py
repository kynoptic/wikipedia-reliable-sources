import sys
from pathlib import Path
from typing import Any

import requests
from scripts.common import HEADERS

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_wikiproject_sources import fetch_page, parse_page


def test_fetch_page(monkeypatch: Any) -> None:
    """Ensure page is requested with the correct headers."""

    def fake_get(url: str, params: Any | None = None, timeout: int = 30, headers: dict | None = None) -> Any:
        assert headers == HEADERS

        class Response:
            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict:
                return {"query": {"pages": {"1": {"revisions": [{"*": "text"}]}}}}

        return Response()

    monkeypatch.setattr(requests, "get", fake_get)

    result = fetch_page("Dummy")
    assert result == "text"


def test_parse_page_extracts_entries() -> None:
    wikitext = (
        "==Reliable sources==\n"
        "===Generally reliable===\n"
        "{| class=\"wikitable\"\n"
        "|-\n! Name !! Notes\n"
        "|-\n| [[Foo News]] || Some ''notes''\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo News"
    assert entry.reliability_status == "gr"
    assert entry.notes == "Some notes"


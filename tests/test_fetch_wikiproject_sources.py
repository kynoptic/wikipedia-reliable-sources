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


def test_parse_page_handles_row_headers() -> None:
    """Rows starting with ``th`` cells should not be skipped."""

    wikitext = (
        "==Unreliable sources==\n"
        "{| class=\"wikitable\"\n"
        "|-\n! Name !! Notes\n"
        "|-\n! [[Bad Source]] || Some ''notes''\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Bad Source"
    assert entry.reliability_status == "gu"


def test_parse_page_extracts_bullet_entries() -> None:
    wikitext = (
        "==Reliable sources==\n"
        "===Generally reliable===\n"
        "* [[Foo Site]] \u2013 Example notes\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo Site"
    assert entry.reliability_status == "gr"
    assert entry.notes == "Example notes"


def test_parse_page_handles_numbered_lists() -> None:
    wikitext = (
        "==Unreliable sources==\n"
        "# [[Bad Site]] - info\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Bad Site"
    assert entry.reliability_status == "gu"


def test_parse_page_class_based_status() -> None:
    """Rows with reliability class attributes should set the status."""

    wikitext = (
        "{| class=\"wikitable\"\n"
        "|- class=\"ko-unrel\"\n"
        "| [[Foo Source]] || Some notes\n"
        "|}\n"
    )

    entries = parse_page(wikitext)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.source_name == "Foo Source"
    assert entry.reliability_status == "gu"
    assert entry.notes == "Some notes"


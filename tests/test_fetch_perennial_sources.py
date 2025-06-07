import sys
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_perennial_sources import fetch_subpage, extract_rows, parse_row


def test_parse_row(monkeypatch: Any) -> None:
    """Parse a minimal table row and verify fields are extracted."""

    wikitext = (
        "\n|- class=\"s-gr\" id=\"Example\"\n"
        "| [[Example News]]\n"
        "| {{WP:RSPSTATUS|gr}}\n"
        "| Discussion\n"
        "| {{WP:RSPLAST|2023}}\n"
        "| Some ''notes'' here.\n"
    )

    def fake_get(url: str, params: Any | None = None, timeout: int = 30) -> Any:
        class Response:
            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict:
                return {"query": {"pages": {"1": {"revisions": [{"*": wikitext}]}}}}

        return Response()

    monkeypatch.setattr(requests, "get", fake_get)

    fetched = fetch_subpage("Dummy")
    row = extract_rows(fetched)[0]
    entry = parse_row(row)

    assert entry.source_name == "Example News"
    assert entry.reliability_status == "gr"
    assert entry.notes == "Some notes here."

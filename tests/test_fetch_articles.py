import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.fetch_articles as fa


class DummyResponse:
    def __init__(self, data: dict) -> None:
        self._data = data

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        pass


def test_fetch_category_members_paginates(monkeypatch: Any) -> None:
    """_fetch_category_members handles MediaWiki pagination."""

    page1 = {
        "query": {
            "categorymembers": [
                {"title": "A", "ns": 0},
                {"title": "Talk:B", "ns": 1},
            ]
        },
        "continue": {"cmcontinue": "token"},
    }
    page2 = {
        "query": {
            "categorymembers": [
                {"title": "C", "ns": 0},
            ]
        }
    }

    calls: list[dict] = []

    def fake_get(url: str, params: dict, timeout: int = 10, headers: dict | None = None) -> DummyResponse:
        calls.append(params.copy())
        return DummyResponse(page2 if params.get("cmcontinue") else page1)

    monkeypatch.setattr(fa.requests, "get", fake_get)

    result = fa._fetch_category_members("Good articles")

    assert result == ["A", "C"]
    assert calls[0].get("cmcontinue") is None
    assert calls[1].get("cmcontinue") == "token"

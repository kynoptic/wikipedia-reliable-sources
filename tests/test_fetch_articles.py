import csv
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.fetch_articles as fa


class DummyResponse:
    def __init__(self, data: dict | None = None, status_code: int = 200, text: str = "") -> None:
        self._data = data
        self.status_code = status_code
        self.headers: dict = {}
        self.text = text

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        pass


def test_fetch_category_members_paginates(monkeypatch: Any) -> None:
    """_fetch_category_members paginates and captures page ids."""

    page1 = {
        "query": {
            "categorymembers": [
                {"pageid": 11, "title": "A", "ns": 0},
                {"pageid": 22, "title": "Talk:B", "ns": 1},
            ]
        },
        "continue": {"cmcontinue": "token"},
    }
    page2 = {
        "query": {
            "categorymembers": [
                {"pageid": 33, "title": "C", "ns": 0},
            ]
        }
    }

    calls: list[dict] = []

    def fake_get(url: str, params: dict, timeout: int = 10, headers: dict | None = None) -> DummyResponse:
        calls.append(params.copy())
        return DummyResponse(page2 if params.get("cmcontinue") else page1)

    monkeypatch.setattr(fa.requests, "get", fake_get)
    monkeypatch.setattr(fa.time, "sleep", lambda _s: None)

    result = fa._fetch_category_members("Good articles")

    assert result == [
        {"pageid": "11", "title": "A"},
        {"pageid": "33", "title": "C"},
    ]
    assert calls[0]["cmprop"] == "ids|title"
    assert calls[0].get("cmcontinue") is None
    assert calls[1].get("cmcontinue") == "token"


def test_fetch_fa_ga_petscan_writes_csvs(monkeypatch: Any, tmp_path: Path) -> None:
    """fetch_fa_ga_petscan writes one PetScan CSV per list."""

    csv_body = '"number","title","pageid"\n"1","Anarchism","12"\n'
    calls: list[str] = []

    def fake_get(url: str, params: dict, timeout: int = 60, headers: dict | None = None) -> DummyResponse:
        calls.append(params["categories"])
        return DummyResponse(text=csv_body)

    monkeypatch.setattr(fa.requests, "get", fake_get)
    fa.fetch_fa_ga_petscan(tmp_path)

    assert sorted(calls) == ["Featured articles", "Good articles"]
    assert (tmp_path / "featured-articles.csv").read_text() == csv_body
    assert (tmp_path / "good-articles.csv").read_text() == csv_body


def test_fetch_good_and_featured_writes_json_and_csv(monkeypatch: Any, tmp_path: Path) -> None:
    """fetch_good_and_featured writes title-only JSON plus page-id CSVs."""

    members = {
        "Good articles": [{"pageid": "1", "title": "Anarchism"}],
        "Featured articles": [{"pageid": "25", "title": "Autism"}],
    }
    monkeypatch.setattr(fa, "_fetch_category_members", lambda cat: members[cat])

    fa.fetch_good_and_featured(tmp_path)

    assert json.loads((tmp_path / "good_articles.json").read_text()) == ["Anarchism"]

    with (tmp_path / "featured-articles.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["pageid"] == "25"
    assert rows[0]["title"] == "Autism"

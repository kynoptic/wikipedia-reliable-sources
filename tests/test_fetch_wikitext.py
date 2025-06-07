import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import src.fetch_wikitext as fw


class DummyResponse:
    def __init__(self, data: dict) -> None:
        self._data = data

    def json(self) -> dict:
        return self._data

    def raise_for_status(self) -> None:
        pass


def test_fetch_single(monkeypatch: Any) -> None:
    data = {
        "query": {
            "pages": [
                {"revisions": [{"slots": {"main": {"content": "hello"}}}]}
            ]
        }
    }

    def fake_get(url: str, params: dict, timeout: int = 10) -> DummyResponse:
        return DummyResponse(data)

    monkeypatch.setattr(fw.requests, "get", fake_get)

    result = fw._fetch_single("Title")
    assert result == "hello"


def test_fetch_wikitext_writes_files(tmp_path: Path, monkeypatch: Any) -> None:
    titles = ["Page One", "Foo/Bar"]

    def fake_fetch(title: str) -> str:
        return f"content-{title}"

    monkeypatch.setattr(fw, "_fetch_single", fake_fetch)

    fw.fetch_wikitext(titles, tmp_path)

    assert (tmp_path / "Page One.txt").read_text() == "content-Page One"
    assert (tmp_path / "Foo_Bar.txt").read_text() == "content-Foo/Bar"

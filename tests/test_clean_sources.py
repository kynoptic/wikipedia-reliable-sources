import sys
import json
from pathlib import Path
from typing import Any
import runpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.clean_sources import (
    clean_refs,
    load_refs,
    save_sources,
    load_alias_map,
    rank_sources,
)
from core.utils.normalize_url import NormalizationConfig


def test_clean_refs_counts():
    refs = [
        {"article": "A", "url": "https://www.nyti.ms/foo?ref=bar"},
        {"article": "A", "url": "https://nytimes.com/foo"},
        {"article": "B", "url": "https://nytimes.com/bar"},
        {"article": "B", "url": "https://example.com?x=1"},
    ]
    config = NormalizationConfig(aliases={"nyti.ms": "nytimes.com"})
    result = clean_refs(refs, config)
    data = {r["source"]: r for r in result}
    assert data["https://nytimes.com"]["total_count"] == 3
    assert data["https://nytimes.com"]["unique_count"] == 2
    assert data["https://example.com"]["total_count"] == 1
    assert data["https://example.com"]["unique_count"] == 1


def test_load_refs_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"
    result = load_refs(path)
    assert result == []


def test_load_refs_reads_json(tmp_path: Path) -> None:
    data = [{"url": "https://example.com"}]
    path = tmp_path / "refs.json"
    path.write_text(json.dumps(data))
    assert load_refs(path) == data


def test_save_sources_writes_csv(tmp_path: Path) -> None:
    records = [{"source": "a", "unique_count": 1, "total_count": 2}]
    path = tmp_path / "out.csv"
    save_sources(records, path)
    assert path.read_text().splitlines()[0] == "source,unique_count,total_count"


def test_load_alias_map_calls_loader(tmp_path: Path, monkeypatch: Any) -> None:
    called = {}

    def fake_load_aliases(p: Path) -> dict:
        called["path"] = p
        return {"a.com": "b.com"}

    monkeypatch.setattr("core.clean_sources.load_aliases", fake_load_aliases)
    custom = tmp_path / "aliases.json"
    result = load_alias_map(custom)
    assert called["path"] == custom
    assert result == {"a.com": "b.com"}


def test_rank_sources_orders_and_limits() -> None:
    data = [
        {"source": "b", "unique_count": 1, "total_count": 3},
        {"source": "a", "unique_count": 1, "total_count": 5},
        {"source": "c", "unique_count": 1, "total_count": 1},
    ]
    ranked = rank_sources(data, limit=2)
    assert [r["source"] for r in ranked] == ["a", "b"]


def test_main_invocation(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.chdir(tmp_path)
    sys.modules.pop("core.clean_sources", None)
    runpy.run_module("core.clean_sources", run_name="__main__")

    assert (tmp_path / "data/processed/sources_canonical.csv").exists()
    assert (tmp_path / "outputs/top_sources.csv").exists()


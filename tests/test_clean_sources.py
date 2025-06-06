import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.clean_sources import clean_refs
from src.utils.normalize_url import NormalizationConfig


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

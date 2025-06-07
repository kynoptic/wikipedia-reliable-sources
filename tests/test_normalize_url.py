import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.utils.normalize_url import canonicalize_url, NormalizationConfig


def test_alias_and_query_strip():
    config = NormalizationConfig(aliases={"nyti.ms": "nytimes.com"})
    url = "https://www.nyti.ms/path?utm_source=twitter"
    assert canonicalize_url(url, config) == "https://nytimes.com"


def test_keep_query_params():
    config = NormalizationConfig(strip_query_params=False)
    url = "https://example.com/?b=1&a=2"
    assert canonicalize_url(url, config) == "https://example.com?a=2&b=1"

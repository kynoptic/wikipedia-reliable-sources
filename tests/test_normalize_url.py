import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.utils.normalize_url import (
    canonicalize_url,
    decompose_host,
    NormalizationConfig,
)


def test_alias_and_query_strip():
    config = NormalizationConfig(aliases={"nyti.ms": "nytimes.com"})
    url = "https://www.nyti.ms/path?utm_source=twitter"
    assert canonicalize_url(url, config) == "https://nytimes.com"


def test_keep_query_params():
    config = NormalizationConfig(strip_query_params=False)
    url = "https://example.com/?b=1&a=2"
    assert canonicalize_url(url, config) == "https://example.com?a=2&b=1"


def test_decompose_host_multi_label_suffix():
    parts = decompose_host("news.bbc.co.uk")
    assert (parts.host, parts.subdomain, parts.domain, parts.suffix) == (
        "news.bbc.co.uk",
        "news",
        "bbc",
        "co.uk",
    )


def test_decompose_host_plain_domain():
    parts = decompose_host("nytimes.com")
    assert (parts.subdomain, parts.domain, parts.suffix) == ("", "nytimes", "com")


def test_decompose_host_keeps_www_subdomain():
    parts = decompose_host("www.nytimes.com")
    assert (parts.subdomain, parts.domain, parts.suffix) == ("www", "nytimes", "com")


def test_decompose_host_ip_address():
    parts = decompose_host("192.168.0.1")
    assert (parts.subdomain, parts.domain, parts.suffix) == ("", "192.168.0.1", "")


def test_decompose_host_empty():
    parts = decompose_host("")
    assert (parts.host, parts.subdomain, parts.domain, parts.suffix) == (
        "",
        "",
        "",
        "",
    )

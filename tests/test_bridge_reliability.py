import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.bridge_reliability as br
from core.bridge_reliability import (
    bridge,
    coverage_gaps,
    load_domain_citations,
    load_reliability,
    resolve_domains,
)


class Resp:
    def __init__(self, data: dict, status_code: int = 200) -> None:
        self._data = data
        self.status_code = status_code
        self.headers: dict = {}

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self._data


def test_load_reliability(tmp_path: Path) -> None:
    csv_path = tmp_path / "p.csv"
    csv_path.write_text(
        "source_name,reliability_status,notes\n"
        "The New York Times,gr,n\n"
        "Daily Mail,d,n\n"
    )
    assert load_reliability(csv_path) == {
        "The New York Times": "gr",
        "Daily Mail": "d",
    }


def test_load_domain_citations_keys_by_full_domain(tmp_path: Path) -> None:
    csv_path = tmp_path / "c.csv"
    csv_path.write_text(
        "domain_url,suffix_url,total_citations,fa_citations,ga_citations,distinct_articles\n"
        "nytimes,com,495111,6520,40695,227818\n"
        "bbc,co.uk,466990,4784,24238,150983\n"
    )
    cites = load_domain_citations(csv_path)
    assert cites["nytimes.com"]["total"] == 495111
    assert cites["bbc.co.uk"]["fa"] == 4784


def test_bridge_attaches_citations_and_skips_unresolved() -> None:
    reliability = {"NYT": "gr", "BBC": "gr", "Unmapped": "gu"}
    name_domains = {"NYT": {"nytimes.com"}, "BBC": {"bbc.com", "bbc.co.uk"}}  # Unmapped absent
    citations = {
        "nytimes.com": {"total": 100, "fa": 10, "ga": 20, "articles": 50},
        "bbc.com": {"total": 106, "fa": 7, "ga": 35, "articles": 56},
        "bbc.co.uk": {"total": 467, "fa": 48, "ga": 242, "articles": 151},
    }
    rows = bridge(reliability, name_domains, citations)
    assert {r["source_name"] for r in rows} == {"NYT", "BBC"}  # Unmapped skipped
    bbc = next(r for r in rows if r["source_name"] == "BBC")
    assert bbc["total_citations"] == 573  # summed across both TLD variants
    assert bbc["fa_citations"] == 55
    assert bbc["domain"] == "bbc.co.uk"  # most-cited variant reported


def test_coverage_gaps_excludes_rated_domains() -> None:
    citations = {
        "google.com": {"total": 500, "fa": 5, "ga": 9, "articles": 200},
        "nytimes.com": {"total": 100, "fa": 10, "ga": 20, "articles": 50},
        "randomblog.com": {"total": 80, "fa": 0, "ga": 1, "articles": 40},
    }
    gaps = coverage_gaps(citations, rated_domains={"nytimes.com"}, limit=10)
    domains = [g["domain"] for g in gaps]
    assert domains == ["google.com", "randomblog.com"]  # sorted by total, nytimes excluded
    assert gaps[0]["total_citations"] == 500


def test_qids_to_domains_keeps_dominant_root_drops_noise(monkeypatch: Any) -> None:
    # NYT: nytimes.com (dominant root) plus a stray loc.gov mirror that must drop.
    claims = [
        {"mainsnak": {"datavalue": {"value": "https://nytimes.com"}}},
        {"mainsnak": {"datavalue": {"value": "https://www.nytimes.com/"}}},
        {"mainsnak": {"datavalue": {"value": "https://hdl.loc.gov/x"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q9684": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q9684"]) == {"Q9684": {"nytimes.com"}}


def test_qids_to_domains_keeps_tld_variants(monkeypatch: Any) -> None:
    # BBC lists both .com and .co.uk (same root) — keep both.
    claims = [
        {"mainsnak": {"datavalue": {"value": "https://bbc.com"}}},
        {"mainsnak": {"datavalue": {"value": "https://bbc.co.uk"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q9531": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q9531"]) == {"Q9531": {"bbc.com", "bbc.co.uk"}}


def test_strip_qualifier() -> None:
    assert br._strip_qualifier("The New York Times (NYT)") == "The New York Times"
    assert br._strip_qualifier("BBC (British Broadcasting Corporation)") == "BBC"
    assert br._strip_qualifier("Reuters") == "Reuters"


def test_resolve_domains_retries_with_stripped_qualifier(monkeypatch: Any) -> None:
    # The qualified name does not resolve; the stripped base does.
    def fake_titles_to_qids(names: list[str]) -> dict[str, str]:
        return {n: "Q9684" for n in names if n == "The New York Times"}

    monkeypatch.setattr(br, "_titles_to_qids", fake_titles_to_qids)
    monkeypatch.setattr(br, "_qids_to_domains", lambda qids: {"Q9684": {"nytimes.com"}})
    result = br.resolve_domains(["The New York Times (NYT)"])
    assert result == {"The New York Times (NYT)": {"nytimes.com"}}


def test_resolve_domains_end_to_end(monkeypatch: Any) -> None:
    def fake_get(url, params=None, headers=None, timeout=None):
        if url == br.WP_API:
            return Resp(
                {
                    "query": {
                        "pages": [
                            {"title": "The New York Times", "pageprops": {"wikibase_item": "Q9684"}}
                        ],
                        "normalized": [],
                        "redirects": [],
                    }
                }
            )
        return Resp(
            {
                "entities": {
                    "Q9684": {"claims": {"P856": [{"mainsnak": {"datavalue": {"value": "https://nytimes.com"}}}]}}
                }
            }
        )

    monkeypatch.setattr(br.requests, "get", fake_get)
    assert resolve_domains(["The New York Times"]) == {"The New York Times": {"nytimes.com"}}

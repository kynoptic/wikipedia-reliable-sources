import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import core.bridge_reliability as br
from core.bridge_reliability import (
    bridge,
    collapse_by_domain,
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
    gaps = coverage_gaps(
        citations, rated_domains={"nytimes.com"}, limit=10, drop_non_editorial=False
    )
    domains = [g["domain"] for g in gaps]
    assert domains == ["google.com", "randomblog.com"]  # sorted by total, nytimes excluded
    assert gaps[0]["total_citations"] == 500


def test_coverage_gaps_drops_non_editorial_infrastructure() -> None:
    # Archives, databases, and government/edu sites are not rateable editorial
    # sources; they crowd out the genuinely unrated outlets worth surfacing.
    citations = {
        "nih.gov": {"total": 9000, "fa": 1, "ga": 1, "articles": 5000},
        "archive.org": {"total": 8000, "fa": 1, "ga": 1, "articles": 4000},
        "worldcat.org": {"total": 7000, "fa": 1, "ga": 1, "articles": 3000},
        "nla.gov.au": {"total": 6000, "fa": 1, "ga": 1, "articles": 2000},
        "harvard.edu": {"total": 5000, "fa": 1, "ga": 1, "articles": 1000},
        "indiatimes.com": {"total": 4000, "fa": 1, "ga": 1, "articles": 900},
    }
    gaps = coverage_gaps(citations, rated_domains=set(), limit=10)
    assert [g["domain"] for g in gaps] == ["indiatimes.com"]  # only editorial outlet survives


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


def test_qids_to_domains_ignores_google_books_archive_links(monkeypatch: Any) -> None:
    # The Atlantic: its real site appears once, but two Google Books scan links
    # share the google root and would win a naive most-frequent vote.
    claims = [
        {"mainsnak": {"datavalue": {"value": "https://www.theatlantic.com/"}}},
        {"mainsnak": {"datavalue": {"value": "http://books.google.com/books?id=cN"}}},
        {"mainsnak": {"datavalue": {"value": "http://books.google.com/books?id=lY"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q1542536": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q1542536"]) == {"Q1542536": {"theatlantic.com"}}


def test_qids_to_domains_skips_deprecated_rank_claims(monkeypatch: Any) -> None:
    # National Geographic: the archive scan links are flagged deprecated on
    # Wikidata, leaving only the live site at normal rank.
    claims = [
        {"rank": "normal", "mainsnak": {"datavalue": {"value": "https://www.nationalgeographic.com/"}}},
        {"rank": "deprecated", "mainsnak": {"datavalue": {"value": "http://natgeo.galegroup.com/x"}}},
        {"rank": "deprecated", "mainsnak": {"datavalue": {"value": "http://example-mirror.com/y"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q5973845": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q5973845"]) == {"Q5973845": {"nationalgeographic.com"}}


def test_qids_to_domains_prefers_preferred_rank(monkeypatch: Any) -> None:
    # A single preferred-rank claim outweighs more numerous normal-rank links.
    claims = [
        {"rank": "preferred", "mainsnak": {"datavalue": {"value": "https://example.org/"}}},
        {"rank": "normal", "mainsnak": {"datavalue": {"value": "https://other.com/"}}},
        {"rank": "normal", "mainsnak": {"datavalue": {"value": "https://other.com/x"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q1": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q1"]) == {"Q1": {"example.org"}}


def test_qids_to_domains_preferred_rank_keeps_variant_tlds(monkeypatch: Any) -> None:
    # BBC marks bbc.com preferred and bbc.co.uk normal; a preferred root must
    # not prune the normal-rank TLD variant that shares it.
    claims = [
        {"rank": "preferred", "mainsnak": {"datavalue": {"value": "https://www.bbc.com/"}}},
        {"rank": "normal", "mainsnak": {"datavalue": {"value": "https://www.bbc.co.uk/"}}},
    ]
    monkeypatch.setattr(
        br.requests,
        "get",
        lambda *a, **k: Resp({"entities": {"Q9531": {"claims": {"P856": claims}}}}),
    )
    assert br._qids_to_domains(["Q9531"]) == {"Q9531": {"bbc.com", "bbc.co.uk"}}


def test_collapse_by_domain_dedupes_shared_domain() -> None:
    # Two RSP rows for the same outlet share a domain and the full domain count;
    # collapsing must yield one row, not double the citations.
    rows = [
        {"source_name": "Fox News (politics)", "status": "gu", "domain": "foxnews.com",
         "total_citations": 19853, "fa_citations": 181, "ga_citations": 912, "distinct_articles": 14267},
        {"source_name": "Fox News (talk shows)", "status": "gu", "domain": "foxnews.com",
         "total_citations": 19853, "fa_citations": 181, "ga_citations": 912, "distinct_articles": 14267},
    ]
    collapsed = collapse_by_domain(rows)
    assert len(collapsed) == 1
    assert collapsed[0]["total_citations"] == 19853  # not summed to 39706
    assert collapsed[0]["domain"] == "foxnews.com"
    assert "Fox News (politics)" in collapsed[0]["source_name"]
    assert "Fox News (talk shows)" in collapsed[0]["source_name"]


def test_collapse_by_domain_resolves_to_most_cautious_status() -> None:
    # When splits of one domain carry different ratings, the most cautious wins
    # so a Goggle never boosts a domain that is unreliable for some topics.
    rows = [
        {"source_name": "Outlet (good topic)", "status": "gr", "domain": "x.com",
         "total_citations": 100, "fa_citations": 1, "ga_citations": 2, "distinct_articles": 50},
        {"source_name": "Outlet (bad topic)", "status": "d", "domain": "x.com",
         "total_citations": 100, "fa_citations": 1, "ga_citations": 2, "distinct_articles": 50},
    ]
    collapsed = collapse_by_domain(rows)
    assert len(collapsed) == 1
    assert collapsed[0]["status"] == "d"  # deprecated outranks generally-reliable


def test_get_json_honors_fractional_retry_after(monkeypatch: Any) -> None:
    calls = {"n": 0}
    slept: list = []

    def fake_get(url, params=None, headers=None, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            r = Resp({}, status_code=429)
            r.headers = {"Retry-After": "1.5"}  # fractional — int parse would miss it
            return r
        return Resp({"ok": True})

    monkeypatch.setattr(br.requests, "get", fake_get)
    monkeypatch.setattr(br.time, "sleep", lambda s: slept.append(s))
    assert br._get_json("http://x", {}) == {"ok": True}
    assert slept == [1.5]


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

"""Join perennial-source reliability ratings to citation-frequency data.

Perennial sources are identified by name; the citation tables by domain. This
resolves each source's registrable domain via Wikidata's official-website
property (P856), then joins against a per-domain citation table to surface:

* the reliability-rated sources most cited by Featured/Good articles,
* heavily-cited domains with no reliability rating (coverage gaps),
* deprecated/unreliable domains still heavily cited (red flags).
"""

from __future__ import annotations

import csv
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import requests
import tldextract

from scripts.common import HEADERS

WP_API = "https://en.wikipedia.org/w/api.php"
WD_API = "https://www.wikidata.org/w/api.php"
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())
_BATCH = 50
_MAX_RETRIES = 6
_PAGE_DELAY = 0.3  # politeness pause between batched API requests


def _get_json(url: str, params: dict) -> dict:
    """GET a JSON API response, backing off on rate-limit replies (429/503)."""
    delay = 1.0
    resp = None
    for _ in range(_MAX_RETRIES):
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if resp.status_code in (429, 503):
            retry_after = resp.headers.get("Retry-After", "")
            time.sleep(float(retry_after) if retry_after.isdigit() else delay)
            delay = min(delay * 2, 30.0)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()
    return resp.json()

STATUS_LABELS = {
    "gr": "generally reliable",
    "gu": "generally unreliable",
    "nc": "no consensus",
    "d": "deprecated/blacklisted",
    "m": "marginally reliable",
}
UNRELIABLE = {"gu", "d"}


def load_reliability(path: Path) -> dict[str, str]:
    """Return ``{source_name: status}`` from a perennial-sources CSV."""
    out: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("source_name") or "").strip()
            status = (row.get("reliability_status") or "").strip()
            if name and status:
                out[name] = status
    return out


def load_domain_citations(path: Path) -> dict[str, dict]:
    """Return ``{domain: {total, fa, ga, articles}}`` from a per-domain CSV."""
    out: dict[str, dict] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            suffix = row["suffix_url"]
            domain = f"{row['domain_url']}.{suffix}" if suffix else row["domain_url"]
            out[domain] = {
                "total": int(row["total_citations"]),
                "fa": int(row["fa_citations"]),
                "ga": int(row["ga_citations"]),
                "articles": int(row["distinct_articles"]),
            }
    return out


def _chunks(seq: list, n: int):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def _titles_to_qids(names: list[str]) -> dict[str, str]:
    """Map source names (article titles) to Wikidata QIDs, resolving redirects."""
    mapping: dict[str, str] = {}
    for batch in _chunks(names, _BATCH):
        data = _get_json(
            WP_API,
            {
                "action": "query",
                "prop": "pageprops",
                "ppprop": "wikibase_item",
                "titles": "|".join(batch),
                "redirects": "1",
                "formatversion": "2",
                "format": "json",
            },
        )
        time.sleep(_PAGE_DELAY)
        query = data.get("query", {})
        norm = {n["from"]: n["to"] for n in query.get("normalized", [])}
        redir = {r["from"]: r["to"] for r in query.get("redirects", [])}
        final_to_request: dict[str, str] = {}
        for name in batch:
            title = norm.get(name, name)
            title = redir.get(title, title)
            final_to_request[title] = name
        for page in query.get("pages", []):
            qid = page.get("pageprops", {}).get("wikibase_item")
            request = final_to_request.get(page["title"])
            if qid and request:
                mapping[request] = qid
    return mapping


def _qids_to_domains(qids: list[str]) -> dict[str, set[str]]:
    """Map QIDs to their official-website domains via the P856 claims.

    A source may list multiple domains: legitimate variants share a registrable
    root (``bbc.com`` + ``bbc.co.uk``), while mirrors/unrelated links (a NYT
    ``loc.gov`` archive link) do not. Keep every full domain that shares the
    dominant root, which captures TLD variants but drops the noise.
    """
    out: dict[str, set[str]] = {}
    for batch in _chunks(qids, _BATCH):
        data = _get_json(
            WD_API,
            {
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "claims",
                "format": "json",
            },
        )
        time.sleep(_PAGE_DELAY)
        for qid, entity in data.get("entities", {}).items():
            root_counts: Counter = Counter()
            by_root: dict[str, set[str]] = defaultdict(set)
            for claim in entity.get("claims", {}).get("P856", []):
                try:
                    url = claim["mainsnak"]["datavalue"]["value"]
                except (KeyError, TypeError):
                    continue
                extracted = _EXTRACT(url)
                if extracted.domain and extracted.suffix:
                    root_counts[extracted.domain] += 1
                    by_root[extracted.domain].add(f"{extracted.domain}.{extracted.suffix}")
            if root_counts:
                dominant_root = root_counts.most_common(1)[0][0]
                out[qid] = by_root[dominant_root]
    return out


_QUALIFIER_RE = re.compile(r"\s*\([^()]*\)\s*$")


def _strip_qualifier(name: str) -> str:
    """Drop a trailing disambiguating parenthetical, e.g. ``"BBC (…)" -> "BBC"``."""
    return _QUALIFIER_RE.sub("", name)


def resolve_domains(names: list[str]) -> dict[str, str]:
    """Map source names to their official-website registrable domain via Wikidata.

    Perennial-source names often carry a parenthetical qualifier (``The New York
    Times (NYT)``) that is not an article title, so unresolved names are retried
    with the trailing ``(…)`` stripped.
    """
    name_qid = _titles_to_qids(names)
    bases = {
        name: _strip_qualifier(name)
        for name in names
        if name not in name_qid and _strip_qualifier(name) != name
    }
    if bases:
        retried = _titles_to_qids(sorted(set(bases.values())))
        for name, base in bases.items():
            if base in retried:
                name_qid[name] = retried[base]
    qid_domain = _qids_to_domains(sorted(set(name_qid.values())))
    return {
        name: qid_domain[qid]
        for name, qid in name_qid.items()
        if qid in qid_domain
    }


_EMPTY = {"total": 0, "fa": 0, "ga": 0, "articles": 0}


def bridge(
    reliability: dict[str, str],
    name_domains: dict[str, set[str]],
    citations: dict[str, dict],
) -> list[dict]:
    """Attach citation counts to each rated source with resolved domain(s).

    A source's counts are summed across its domain variants (e.g. ``bbc.com`` +
    ``bbc.co.uk``); the reported domain is the most-cited variant.
    """
    rows = []
    for name, status in reliability.items():
        domains = name_domains.get(name)
        if not domains:
            continue
        per = {d: citations.get(d, _EMPTY) for d in domains}
        primary = max(domains, key=lambda d: per[d]["total"])
        rows.append(
            {
                "source_name": name,
                "status": status,
                "domain": primary,
                "total_citations": sum(c["total"] for c in per.values()),
                "fa_citations": sum(c["fa"] for c in per.values()),
                "ga_citations": sum(c["ga"] for c in per.values()),
                "distinct_articles": sum(c["articles"] for c in per.values()),
            }
        )
    return rows


def coverage_gaps(
    citations: dict[str, dict], rated_domains: set[str], limit: int = 50
) -> list[dict]:
    """Return the most-cited domains that have no reliability rating."""
    ranked = sorted(
        citations.items(), key=lambda kv: kv[1]["total"], reverse=True
    )
    gaps = []
    for domain, cites in ranked:
        if domain in rated_domains:
            continue
        gaps.append(
            {
                "domain": domain,
                "total_citations": cites["total"],
                "fa_citations": cites["fa"],
                "ga_citations": cites["ga"],
                "distinct_articles": cites["articles"],
            }
        )
        if len(gaps) >= limit:
            break
    return gaps


def _write_csv(rows: list[dict], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--perennial", type=Path, default=Path("perennial_sources.csv"))
    parser.add_argument(
        "--citations",
        type=Path,
        default=Path("data/processed/citations_2023_by_domain.csv"),
    )
    parser.add_argument("--outdir", type=Path, default=Path("outputs"))
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args(argv)

    reliability = load_reliability(args.perennial)
    name_domains = resolve_domains(list(reliability))
    citations = load_domain_citations(args.citations)
    matched = bridge(reliability, name_domains, citations)

    ranked = sorted(matched, key=lambda r: r["total_citations"], reverse=True)
    red_flags = sorted(
        (r for r in matched if r["status"] in UNRELIABLE and r["total_citations"]),
        key=lambda r: r["total_citations"],
        reverse=True,
    )
    rated_domains: set[str] = set().union(*name_domains.values()) if name_domains else set()
    gaps = coverage_gaps(citations, rated_domains, args.top)

    rated_fields = [
        "source_name",
        "status",
        "domain",
        "total_citations",
        "fa_citations",
        "ga_citations",
        "distinct_articles",
    ]
    gap_fields = ["domain", "total_citations", "fa_citations", "ga_citations", "distinct_articles"]
    _write_csv(ranked, args.outdir / "reliability_ranking.csv", rated_fields)
    _write_csv(red_flags, args.outdir / "red_flags.csv", rated_fields)
    _write_csv(gaps, args.outdir / "coverage_gaps.csv", gap_fields)

    print(
        f"Resolved {len(name_domains)}/{len(reliability)} sources to domains; "
        f"{len(matched)} rated+matched, {len(red_flags)} red flags, {len(gaps)} gaps"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

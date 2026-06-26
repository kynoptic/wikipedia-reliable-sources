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
from urllib.parse import urlsplit

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
            try:
                wait = float(resp.headers.get("Retry-After", ""))
            except ValueError:
                wait = delay
            time.sleep(wait)
            delay = min(delay * 2, 30.0)
            continue
        resp.raise_for_status()
        return resp.json()
    resp.raise_for_status()  # retries exhausted; 429/503 always raises here
    return resp.json()  # unreachable, kept for return-type completeness

STATUS_LABELS = {
    "gr": "generally reliable",
    "gu": "generally unreliable",
    "nc": "no consensus",
    "d": "deprecated/blacklisted",
    "m": "marginally reliable",
}
UNRELIABLE = {"gu", "d"}

# Most cautious first. When several rated source-splits resolve to one domain
# (RSP lists outlets per era/section), the domain inherits the most cautious
# rating so a Goggle never boosts a domain that is unreliable for some topics.
# Unknown statuses sort after all known ratings and are superseded by any known
# rating (an unknown paired only with ``gr`` resolves to ``gr``).
_STATUS_PRECEDENCE = ["d", "gu", "nc", "m", "gr"]


def _most_cautious(statuses: list[str]) -> str:
    """Return the most cautious status; requires a non-empty list."""
    return min(
        statuses,
        key=lambda s: _STATUS_PRECEDENCE.index(s) if s in _STATUS_PRECEDENCE else len(_STATUS_PRECEDENCE),
    )


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


# Archive, catalogue, and digitisation hosts that Wikidata lists under P856
# (official website) for older publications. They are not the source's own site,
# yet a publication may carry several such links — enough to win a naive
# most-frequent-root vote and hijack the resolved domain (e.g. two
# ``books.google.com`` scans outvoting ``theatlantic.com``). Matched by host
# suffix, so subdomains like ``catalog.hathitrust.org`` are covered.
_AGGREGATOR_HOSTS = frozenset(
    {
        "hathitrust.org",
        "galegroup.com",
        "gale.com",
        "archive.org",
        "worldcat.org",
        "jstor.org",
        "proquest.com",
        "loc.gov",  # Library of Congress catalogue links (lccn.loc.gov, etc.)
    }
)


def _is_aggregator_link(url: str) -> bool:
    """True for archive/catalogue links that are not a source's own website."""
    host = (urlsplit(url).hostname or "").lower()
    if host.startswith("books.google."):
        return True
    return any(host == h or host.endswith("." + h) for h in _AGGREGATOR_HOSTS)


# Known-wrong P856 resolutions, mapped to the domain a search engine actually
# indexes. Wikidata's official-website claim can lead with a freshly-rebranded
# domain while demoting the established one to ``deprecated`` rank: MSNBC's
# entity now lists ``ms.now`` at normal rank and ``msnbc.com`` as deprecated, so
# the rank filter in ``_qids_to_domains`` keeps only ``ms.now`` — a live hostname
# absent from Brave Search's index. Corrected here so the Goggle targets the
# domain that still carries the source's content. Keyed by registrable domain.
_DOMAIN_CORRECTIONS = {
    "ms.now": "msnbc.com",
}


def _qids_to_domains(qids: list[str]) -> dict[str, set[str]]:
    """Map QIDs to their official-website domains via the P856 claims.

    A source may list multiple domains: legitimate variants share a registrable
    root (``bbc.com`` + ``bbc.co.uk``), while mirrors/unrelated links (a NYT
    ``loc.gov`` archive link) do not. Selection, in order:

    1. Drop ``deprecated``-rank claims and archive/catalogue aggregator links.
    2. If any ``preferred``-rank claims remain, vote for the dominant root using
       only those; otherwise vote across all surviving claims.
    3. Keep every full domain sharing the dominant root, so a preferred
       ``bbc.com`` does not prune a normal-rank ``bbc.co.uk``.
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
            candidates: list[tuple[str, str, str]] = []  # (rank, root, full_domain)
            for claim in entity.get("claims", {}).get("P856", []):
                try:
                    url = claim["mainsnak"]["datavalue"]["value"]
                except (KeyError, TypeError):
                    continue
                rank = claim.get("rank", "normal")
                if rank == "deprecated" or _is_aggregator_link(url):
                    continue
                extracted = _EXTRACT(url)
                if extracted.domain and extracted.suffix:
                    candidates.append(
                        (rank, extracted.domain, f"{extracted.domain}.{extracted.suffix}")
                    )
            if not candidates:
                continue
            # Preferred-rank claims decide which root wins, but the chosen root
            # keeps all its TLD variants regardless of their individual rank, so
            # a preferred ``bbc.com`` does not prune a normal-rank ``bbc.co.uk``.
            preferred_roots = [root for rank, root, _ in candidates if rank == "preferred"]
            vote_pool = preferred_roots or [root for _, root, _ in candidates]
            dominant_root = Counter(vote_pool).most_common(1)[0][0]
            out[qid] = {
                _DOMAIN_CORRECTIONS.get(full.lower(), full)
                for _, root, full in candidates
                if root == dominant_root
            }
    return out


_QUALIFIER_RE = re.compile(r"\s*\([^()]*\)\s*$")


def _strip_qualifier(name: str) -> str:
    """Drop a trailing disambiguating parenthetical, e.g. ``"BBC (…)" -> "BBC"``."""
    return _QUALIFIER_RE.sub("", name)


def resolve_domains(names: list[str]) -> dict[str, set[str]]:
    """Map source names to their official-website registrable domain(s) via Wikidata.

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
    ``distinct_articles`` is summed too, so an article citing more than one
    variant is counted once per variant (a slight over-count for such sources).
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


def collapse_by_domain(rows: list[dict]) -> list[dict]:
    """Merge rated rows that resolve to the same primary domain into one row.

    RSP lists many outlets as several time- or section-scoped entries that share
    a single domain (``Fox News (politics)`` and ``Fox News (talk shows)`` both
    map to ``foxnews.com``). Each entry inherited the full per-domain citation
    count, so summing would double-count; instead the merged row takes the
    representative (max) counts, joins the source names, and adopts the most
    cautious status across the splits.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["domain"]].append(row)
    merged = []
    for domain, members in groups.items():
        names = sorted({m["source_name"] for m in members})
        merged.append(
            {
                "source_name": "; ".join(names),
                "status": _most_cautious([m["status"] for m in members]),
                "domain": domain,
                "total_citations": max(m["total_citations"] for m in members),
                "fa_citations": max(m["fa_citations"] for m in members),
                "ga_citations": max(m["ga_citations"] for m in members),
                "distinct_articles": max(m["distinct_articles"] for m in members),
            }
        )
    return merged


# Suffixes for non-editorial sources (government, education, military). These
# are reliable by nature and never appear on the Perennial Sources list, so they
# are noise in a coverage-gap report meant to surface unrated editorial outlets.
_NON_EDITORIAL_SUFFIXES = ("gov", "edu", "mil")
# Archives, library catalogues, and identifier resolvers — cited heavily but not
# rateable editorial sources. Keyed by registrable domain to match the citation
# table (which collapses ``books.google.com`` into ``google.com``), so only
# registrable domains belong here.
_NON_EDITORIAL_DOMAINS = frozenset(
    {
        "archive.org",
        "worldcat.org",
        "hathitrust.org",
        "jstor.org",
        "doi.org",
    }
)


def _is_editorial_candidate(domain: str) -> bool:
    """True unless the domain is government/education/military or an archive."""
    labels = set(_EXTRACT(domain).suffix.split("."))  # "gov.au" -> {"gov", "au"}
    if labels & set(_NON_EDITORIAL_SUFFIXES):
        return False
    return domain not in _NON_EDITORIAL_DOMAINS


def coverage_gaps(
    citations: dict[str, dict],
    rated_domains: set[str],
    limit: int = 50,
    drop_non_editorial: bool = True,
) -> list[dict]:
    """Return the most-cited domains that have no reliability rating.

    With ``drop_non_editorial`` (the default), government/education/military and
    archive/identifier domains are excluded so the report surfaces genuinely
    unrated editorial outlets rather than infrastructure that will never be rated.
    Returns fewer than ``limit`` rows when too few editorial candidates remain.
    """
    ranked = sorted(
        citations.items(), key=lambda kv: kv[1]["total"], reverse=True
    )
    gaps = []
    for domain, cites in ranked:
        if domain in rated_domains:
            continue
        if drop_non_editorial and not _is_editorial_candidate(domain):
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
    matched = collapse_by_domain(bridge(reliability, name_domains, citations))

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

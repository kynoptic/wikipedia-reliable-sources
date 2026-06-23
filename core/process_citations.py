"""Aggregate Wikipedia citation dumps into per-host and per-domain frequency tables.

This reimplements a Google Cloud Dataprep (Trifacta) flow that ranked web sources
by how often Wikipedia's Featured and Good articles cite them. It streams a CS1
citations TSV, extracts each citation's URL, tags the citing article as
Featured/Good, and pivots by host and by domain. See
``data/raw/citations/README.md`` for the original flow.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import urlparse

from .utils.normalize_url import (
    NormalizationConfig,
    decompose_host,
    load_aliases,
)

DEFAULT_CONFIG = NormalizationConfig()
DEFAULT_ALIAS_PATH = Path("data/alias_map.json")

_CITATION_COLUMNS = 6

# A record begins with "<revision_id>\t<page_id>\t"; everything after that may
# contain embedded newlines (the cite_type / JSON column), so lines that do not
# match are continuations of the current record.
_RECORD_START = re.compile(r"^\d+\t\d+\t")


@dataclass
class CitationRow:
    """One parsed citation from the CS1 citations TSV."""

    revision_id: str
    page_id: str
    timestamp: str
    page_title: str
    cite_type: str
    url: str


@dataclass
class ArticleClassifier:
    """Looks up whether a citing article's page id is Featured or Good."""

    featured_ids: set[str] = field(default_factory=set)
    good_ids: set[str] = field(default_factory=set)

    def is_featured(self, page_id: str) -> bool:
        return page_id in self.featured_ids

    def is_good(self, page_id: str) -> bool:
        return page_id in self.good_ids


def normalize_cite_type(raw: str) -> str:
    """Canonicalize a citation template name, e.g. ``"Cite book " -> "cite book"``."""
    return " ".join(raw.replace("_", " ").lower().split())


def load_article_ids(path: Path) -> set[str]:
    """Return the set of ``pageid`` strings from a Featured/Good article CSV.

    Page ids are kept as strings to match the TSV's ``page_id`` column. Missing
    files yield an empty set to simplify pipeline usage.
    """
    if not path.exists():
        return set()
    ids: set[str] = set()
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            page_id = (row.get("pageid") or "").strip()
            if page_id:
                ids.add(page_id)
    return ids


def load_classifier(featured_path: Path, good_path: Path) -> ArticleClassifier:
    """Build an :class:`ArticleClassifier` from the FA and GA article CSVs."""
    return ArticleClassifier(
        featured_ids=load_article_ids(featured_path),
        good_ids=load_article_ids(good_path),
    )


def _parse_record(record: str) -> CitationRow | None:
    """Parse one reassembled record into a :class:`CitationRow`, or ``None``."""
    parts = record.split("\t", _CITATION_COLUMNS - 1)
    if len(parts) < _CITATION_COLUMNS:
        return None
    revision_id, page_id, timestamp, page_title, cite_type, blob = parts
    try:
        # strict=False tolerates raw control chars (e.g. tabs/newlines) that the
        # maxsplit above preserves inside the JSON column.
        meta = json.loads(blob, strict=False)
    except (json.JSONDecodeError, ValueError):
        return None
    return CitationRow(
        revision_id=revision_id,
        page_id=page_id,
        timestamp=timestamp,
        page_title=page_title,
        cite_type=normalize_cite_type(cite_type),
        url=meta.get("URL") or "",
    )


def iter_citation_rows(path: Path) -> Iterator[CitationRow]:
    """Stream :class:`CitationRow` records from a CS1 citations TSV.

    The file is read line by line (constant memory) regardless of size. Records
    may span multiple physical lines because the cite_type / JSON column can
    contain embedded newlines, so lines are accumulated until the next
    record-start marker (see :data:`_RECORD_START`). The sixth column is a JSON
    object; ``split("\\t", 5)`` keeps it intact even when it contains tabs.
    Records with too few columns or malformed JSON are skipped and counted; the
    skip total is reported to stderr when iteration completes.
    """
    skipped = 0
    buffer = ""

    def consume(record: str) -> Iterator[CitationRow]:
        nonlocal skipped
        row = _parse_record(record.rstrip("\n"))
        if row is None:
            skipped += 1
        else:
            yield row

    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if buffer and _RECORD_START.match(line):
                yield from consume(buffer)
                buffer = line
            else:
                buffer += line
    if buffer:
        yield from consume(buffer)
    if skipped:
        print(f"Skipped {skipped} malformed citation rows", file=sys.stderr)


def _host_of(url: str, config: NormalizationConfig) -> str:
    """Extract the lowercased hostname from ``url``, applying domain aliases.

    Returns ``""`` for URLs that :func:`urlparse` rejects (e.g. malformed IPv6
    netlocs), which appear in real dumps.
    """
    try:
        host = (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""
    if config.aliases and host in config.aliases:
        host = config.aliases[host]
    return host


def aggregate_citations(
    rows: Iterable[CitationRow],
    classifier: ArticleClassifier,
    config: NormalizationConfig = DEFAULT_CONFIG,
) -> tuple[list[dict], list[dict]]:
    """Pivot citations into per-host and per-domain frequency tables.

    Returns ``(by_host_rows, by_domain_rows)``. Each row carries total citation
    count, Featured- and Good-article citation counts, and the number of distinct
    citing articles. Rows without a URL are ignored. ``by_host`` keeps subdomains
    separate; ``by_domain`` collapses them onto ``(domain, suffix)``.
    """
    host_stats: dict[tuple, dict] = defaultdict(_new_accumulator)
    domain_stats: dict[tuple, dict] = defaultdict(_new_accumulator)

    for row in rows:
        if not row.url:
            continue
        parts = decompose_host(_host_of(row.url, config))
        if not parts.domain:
            continue
        is_featured = classifier.is_featured(row.page_id)
        is_good = classifier.is_good(row.page_id)
        host_key = (parts.host, parts.subdomain, parts.domain, parts.suffix)
        domain_key = (parts.domain, parts.suffix)
        for stats, key in ((host_stats, host_key), (domain_stats, domain_key)):
            acc = stats[key]
            acc["total"] += 1
            acc["fa"] += is_featured
            acc["ga"] += is_good
            acc["articles"].add(row.page_id)

    by_host = [
        {
            "host_url": host,
            "subdomain_url": subdomain,
            "domain_url": domain,
            "suffix_url": suffix,
            "total_citations": acc["total"],
            "fa_citations": acc["fa"],
            "ga_citations": acc["ga"],
            "distinct_articles": len(acc["articles"]),
        }
        for (host, subdomain, domain, suffix), acc in host_stats.items()
    ]
    by_domain = [
        {
            "domain_url": domain,
            "suffix_url": suffix,
            "total_citations": acc["total"],
            "fa_citations": acc["fa"],
            "ga_citations": acc["ga"],
            "distinct_articles": len(acc["articles"]),
        }
        for (domain, suffix), acc in domain_stats.items()
    ]
    return by_host, by_domain


def _new_accumulator() -> dict:
    return {"total": 0, "fa": 0, "ga": 0, "articles": set()}


_HOST_FIELDS = [
    "host_url",
    "subdomain_url",
    "domain_url",
    "suffix_url",
    "total_citations",
    "fa_citations",
    "ga_citations",
    "distinct_articles",
]

_DOMAIN_FIELDS = [
    "domain_url",
    "suffix_url",
    "total_citations",
    "fa_citations",
    "ga_citations",
    "distinct_articles",
]


def _save_table(data: list[dict], path: Path, fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def save_host_table(data: list[dict], path: Path) -> None:
    """Write the per-host frequency table to ``path`` as CSV."""
    _save_table(data, path, _HOST_FIELDS)


def save_domain_table(data: list[dict], path: Path) -> None:
    """Write the per-domain frequency table to ``path`` as CSV."""
    _save_table(data, path, _DOMAIN_FIELDS)


def rank_by_count(data: list[dict], limit: int = 50) -> list[dict]:
    """Return rows sorted by ``total_citations`` descending, capped at ``limit``."""
    ranked = sorted(data, key=lambda r: r["total_citations"], reverse=True)
    return ranked[:limit]


if __name__ == "__main__":
    citations_dir = Path("data/raw/citations")
    tsv_path = citations_dir / "zenodo-55004" / "enwiki_2016-06-01_CS1_citations.tsv"
    featured_path = citations_dir / "featured-articles.csv"
    good_path = citations_dir / "good-articles.csv"

    host_path = Path("data/processed/citations_by_host.csv")
    domain_path = Path("data/processed/citations_by_domain.csv")
    top_path = Path("outputs/top_sources_by_domain.csv")

    config = NormalizationConfig(aliases=load_aliases(DEFAULT_ALIAS_PATH))
    classifier = load_classifier(featured_path, good_path)

    by_host, by_domain = aggregate_citations(
        iter_citation_rows(tsv_path), classifier, config
    )

    for path in (host_path, domain_path, top_path):
        path.parent.mkdir(parents=True, exist_ok=True)

    save_host_table(by_host, host_path)
    save_domain_table(by_domain, domain_path)
    save_domain_table(rank_by_count(by_domain), top_path)

    print(
        f"Wrote {len(by_host)} hosts and {len(by_domain)} domains "
        f"from {tsv_path}"
    )

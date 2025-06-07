"""Process extracted citation references and output canonical source counts."""

from pathlib import Path
import json
from collections import Counter, defaultdict
from .utils.normalize_url import (
    canonicalize_url,
    NormalizationConfig,
    load_aliases,
)


DEFAULT_CONFIG = NormalizationConfig()
DEFAULT_ALIAS_PATH = Path("data/alias_map.json")


def load_refs(path: Path) -> list:
    """Return a list of raw reference dicts from ``path``.

    The file is expected to contain JSON produced by
    :func:`src.extract_refs.extract_references`. When the file does not exist
    an empty list is returned to simplify pipeline usage.
    """
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def clean_refs(refs: list, config: NormalizationConfig = DEFAULT_CONFIG) -> list:
    """Normalize reference URLs and count usage statistics."""

    total_counter = Counter()
    unique_per_article = defaultdict(set)
    for ref in refs:
        url = ref.get("url") or ""
        article = ref.get("article")
        canonical = canonicalize_url(url, config)
        if article:
            # Track sources that appear in each article so we can compute unique counts
            unique_per_article[article].add(canonical)
        total_counter[canonical] += 1

    result = []
    for source, total_count in total_counter.items():
        unique_count = sum(1 for articles in unique_per_article.values() if source in articles)
        result.append({"source": source, "unique_count": unique_count, "total_count": total_count})
    return result


def save_sources(data: list, path: Path) -> None:
    """Write cleaned source counts to ``path`` as a CSV file."""

    import csv

    fieldnames = ["source", "unique_count", "total_count"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_alias_map(path: Path = DEFAULT_ALIAS_PATH) -> dict:
    """Load alias mapping from JSON."""
    return load_aliases(path)


def rank_sources(data: list, limit: int = 50) -> list:
    """Return sources sorted by total count descending."""
    ranked = sorted(data, key=lambda r: r["total_count"], reverse=True)
    return ranked[:limit]


if __name__ == "__main__":
    refs_path = Path("data/processed/refs_extracted.json")
    canonical_path = Path("data/processed/sources_canonical.csv")
    top_path = Path("outputs/top_sources.csv")

    alias_map = load_alias_map()
    config = NormalizationConfig(aliases=alias_map)

    refs = load_refs(refs_path)
    cleaned = clean_refs(refs, config)

    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    top_path.parent.mkdir(parents=True, exist_ok=True)

    save_sources(cleaned, canonical_path)
    top = rank_sources(cleaned)
    save_sources(top, top_path)

"""Process extracted citation references and output canonical source counts."""

from pathlib import Path
import json
from collections import Counter, defaultdict
from .utils.normalize_url import canonicalize_url, NormalizationConfig


ndefault_config = NormalizationConfig()


def load_refs(path: Path) -> list:
    if not path.exists():
        return []
    with path.open() as f:
        return json.load(f)


def clean_refs(refs: list, config: NormalizationConfig = ndefault_config):
    total_counter = Counter()
    unique_per_article = defaultdict(set)
    for ref in refs:
        url = ref.get("url") or ""
        article = ref.get("article")
        canonical = canonicalize_url(url, config)
        if article:
            unique_per_article[article].add(canonical)
        total_counter[canonical] += 1
    result = []
    for source, total_count in total_counter.items():
        unique_count = sum(1 for articles in unique_per_article.values() if source in articles)
        result.append({"source": source, "unique_count": unique_count, "total_count": total_count})
    return result


def save_sources(data: list, path: Path) -> None:
    import csv
    fieldnames = ["source", "unique_count", "total_count"]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    refs_path = Path("data/processed/refs_extracted.json")
    output_path = Path("data/processed/sources_canonical.csv")
    refs = load_refs(refs_path)
    cleaned = clean_refs(refs)
    save_sources(cleaned, output_path)

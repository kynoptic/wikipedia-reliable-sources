# API Usage Examples

This guide shows how to call the Python modules directly from your own code instead of running the command line wrappers.

## Fetch article lists

```python
from pathlib import Path
from core.fetch_articles import fetch_good_and_featured

fetch_good_and_featured(Path("data/raw"))
```

This downloads `good_articles.json` and `featured_articles.json` under `data/raw/`.

## Download article wikitext

```python
from pathlib import Path
from core.fetch_wikitext import fetch_wikitext

articles = ["Example", "Another article"]
fetch_wikitext(articles, Path("data/raw/wikitext"))
```

## Extract citation references

```python
from pathlib import Path
from core.extract_refs import extract_references

extract_references(
    Path("data/raw/wikitext"),
    Path("data/processed/refs_extracted.json"),
)
```

## Clean and rank sources

```python
from pathlib import Path
from core.clean_sources import (
    load_refs,
    clean_refs,
    load_alias_map,
    save_sources,
    rank_sources,
)
from core.utils.normalize_url import NormalizationConfig

refs = load_refs(Path("data/processed/refs_extracted.json"))
aliases = load_alias_map()
config = NormalizationConfig(aliases=aliases)
cleaned = clean_refs(refs, config)

save_sources(cleaned, Path("data/processed/sources_canonical.csv"))

# Top sources by total citations
ranked = rank_sources(cleaned)
save_sources(ranked, Path("outputs/top_sources.csv"))
```

These snippets mirror the steps performed by the command line scripts, allowing you to integrate the pipeline into other projects.

# Roadmap

## 📌 Objective

Automatically fetch the Perennial Sources table, other reliable-source lists from WikiProjects, and sources used in Featured and Good Articles, and use them to keep the Goggle definition current.

## Status

The loop is closed: `core.build_goggle` regenerates both `.goggle` files from the reliability data. A data-derived base layer is merged with a [curated overlay file](../goggle_overlay.txt) that holds rules the data cannot yet produce.

## Next: generate path-qualified rules

The overlay's largest fixed cost is the per-topic path-qualified rules (`/*science^$downrank=2,site=foxnews.com`) — nuance the current parser discards because it collapses each source to a single status. Generating these from data, so the overlay shrinks over time, takes three steps:

1. **Retain qualifiers in the parser.** `scripts/fetch_perennial_sources.py` dedupes by name and drops the trailing `(…)`. Keep one row per RSP entry with its qualifier and per-row status.
2. **Curate a qualifier→path lookup** (`data/topic_paths.json`) mapping recurring topic qualifiers (`science`, `politics`, `blogs`) to Goggle path patterns. Topic→URL-path is fuzzy, so this stays a small hand-maintained table.
3. **Emit path-qualified base rules** when a domain carries multiple per-qualifier statuses. As lookup coverage grows, rules migrate out of the overlay's path-qualified section into the generated base.

## Automation

Tie generation into `scripts/update_checker.py`: when an upstream source list changes, refresh the resolved-domain cache, rerun the bridge and the build, and commit the updated goggles.

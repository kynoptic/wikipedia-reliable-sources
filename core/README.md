# Core Modules

This package contains the main logic for fetching and processing Wikipedia reliability data.

- `fetch_articles.py` – Download lists of featured and good articles.
- `fetch_wikitext.py` – Retrieve article wikitext for offline parsing.
- `extract_refs.py` – Parse citation URLs from wikitext files.
- `clean_sources.py` – Normalize reference URLs and rank canonical sources.
- `utils/normalize_url.py` – Helper functions for URL canonicalization.

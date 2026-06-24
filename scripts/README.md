# Utility Scripts

Standalone command-line utilities for interacting with Wikipedia data.

- `fetch_citation_data.py` – Re-download the raw citation dumps in `data/raw/citations/` from their published archives (Zenodo, figshare, GitHub release). `--fetch-2023` also pulls the ~7.3 GB 2023 Parquet dataset.
- `fetch_perennial_sources.py` – Parse the "Perennial sources" tables and generate JSON and CSV outputs.
- `update_checker.py` – Detect changes to the tables and regenerate outputs when needed.
- `common.py` – Shared HTTP headers and constants.

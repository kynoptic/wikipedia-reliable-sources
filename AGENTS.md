# `AGENTS.md` – Project guide for AI agents

## Project overview

Wikipedia Goggles builds two [Brave Search Goggle](https://github.com/brave/goggles-quickstart) definitions that rerank search results toward sources the Wikipedia community considers reliable. A Python pipeline fetches reliability data, normalizes citation domains, and regenerates the `.goggle` files. Stack: Python 3, `requests`, `beautifulsoup4`, `mwparserfromhell`, `pytest`.

## Commands

```bash
pip install -r requirements.txt   # install dependencies
pytest                            # run the test suite
python -m core.build_goggle       # regenerate both .goggle files from reliability data
```

The full data pipeline (fetch → normalize → build) is documented in the [build pipeline guide](docs/pipeline.md).

## Architecture

- `core/` – pipeline modules
  - `fetch_articles.py`, `fetch_wikitext.py`, `extract_refs.py` – gather Featured/Good-article citations
  - `clean_sources.py`, `process_citations.py` – normalize and rank citation domains
  - `bridge_reliability.py` – merge the rated source lists into `outputs/reliability_ranking.csv`
  - `build_goggle.py` – emit the two `.goggle` files from the ranking plus `goggle_overlay.txt`
  - `utils/` – shared helpers such as `normalize_url.py`
- `scripts/` – standalone CLIs: `fetch_perennial_sources.py`, `fetch_wikiproject_sources.py`, `update_checker.py`
- `data/` – raw and processed datasets; `outputs/` – generated rankings and reports
- `tests/` – pytest suite; `.github/workflows/ci.yml` – runs `pytest` on push and PR
- `wikipedia-reliable-sources.goggle`, `wikipedia-reliable-sources-only.goggle` – build artifacts, never hand-edited

## Conventions

- Type hints and docstrings on all new Python; unit tests for new functionality.
- The `.goggle` files are generated. Edit reliability data or `goggle_overlay.txt`, then rebuild — never edit a `.goggle` by hand.

## Constraints

- **ALWAYS** run `pytest` and ensure it passes before committing.
- `goggle_overlay.txt` holds rules the generator cannot yet derive; the curated overlay wins on conflict with the base layer.

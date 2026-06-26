# Wikipedia Goggles

This repository hosts two [Brave Search Goggles](https://github.com/brave/goggles-quickstart) that reranks search results to promote sources considered reliable by the Wikipedia community:

1. **`wikipedia-reliable-sources-only.goggle`** – Boosts reliable sources and downranks contentious ones, showing no other results. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%253A%252F%252Fraw.githubusercontent.com%252Fkynoptic%252Fwikipedia-reliable-sources%252Fmain%252Fwikipedia-reliable-sources-only.goggle).
2. **`wikipedia-reliable-sources.goggle`** – Similar to the first, but it allows additional sources while discarding those deemed unreliable. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fkynoptic%2Fwikipedia-reliable-sources%2Fmain%2Fwikipedia-reliable-sources.goggle).

## Reliability sources

This project leverages reliability ratings from various Wikipedia sources to assess the trustworthiness of content. The ratings are based on the following Wikipedia pages:

- [Reliable sources/Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources)
- [WikiProject Video games/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Video_games/Sources)
- [WikiProject Film/Resources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Film/Resources)
- [WikiProject Albums/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Albums/Sources)
- [WikiProject Christian music/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Christian_music/Sources)
- [WikiProject Professional wrestling/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Professional_wrestling/Sources)
- [WikiProject Korea/Reliable sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Korea/Reliable_sources)

Additionally, sources frequently used in featured articles (FA) and good articles (GA) are included.

## Project structure

- `core/` – Python modules with data processing logic
- `scripts/` – Standalone command-line utilities
- `tests/` – Pytest suite
- `docs/` – Documentation and roadmap
- `data/` – Raw and processed datasets
- `outputs/` – Generated analysis results

## How reliability affects rankings

The reliability ratings are adjusted using the following parameters:

- `$boost=2` – Applied to sources considered "Generally reliable" or "Reliable"
- `$downrank=2` – Used for sources labeled with "No consensus"
- `$discard` – Assigned to sources determined as "Unreliable," "Blacklisted," or "Deprecated"

## Extracting perennial sources

Run `scripts/fetch_perennial_sources.py` to download and parse the perennial
sources list from Wikipedia. The script cleans and validates the data then
writes `perennial_sources.json` and `perennial_sources.csv` containing
structured records.

```bash
python scripts/fetch_perennial_sources.py
```

### JSON output

Running the script prints the number of parsed entries (for example,
`Fetched 485 sources`) and writes `perennial_sources.json`.  The file is a JSON
array where each object has the following fields:

| Field | Description |
|-------|-------------|
| `source_name` | Name of the publication or website. |
| `reliability_status` | Two letter code from the `WP:RSPSTATUS` legend (e.g. `gr` = generally reliable, `gu` = generally unreliable, `nc` = no consensus, `d` = deprecated, `m` = marginal). |
| `notes` | Summary of discussions about the source. |

Example entry:

```json
[
  {
    "source_name": "ABC News (US)",
    "reliability_status": "gr",
    "notes": "There is consensus that ABC News, the news division of the American Broadcasting Company, is generally reliable. It is not to be confused with other publications of the same name."
  }
]
```

### CSV output

The script also writes a `perennial_sources.csv` file with the same fields for
easy spreadsheet analysis.

## Checking for updates

Run `scripts/update_checker.py` periodically. It compares the current revision
IDs of the perennial sources subpages against `revision_ids.json`. If any page
has changed since the last run, the script re-fetches the tables and updates
`perennial_sources.json` and `perennial_sources.csv`.

```bash
python scripts/update_checker.py
```

## Extracting WikiProject sources

Run `scripts/fetch_wikiproject_sources.py` to download the reliability tables
maintained by several WikiProjects. The command outputs
`wikiproject_sources.json` and `wikiproject_sources.csv` at the repository
root.

```bash
python scripts/fetch_wikiproject_sources.py
```

## Citation normalization pipeline

The project now includes a modular workflow for gathering citation data and normalizing source URLs.

1. **Fetch article lists**

   ```bash
   python -m core.fetch_articles
   ```

   This writes `good_articles.json` and `featured_articles.json` under `data/raw/`.

2. **Download wikitext for each article**

   ```bash
   python -m core.fetch_wikitext
   ```

   Wikitext files are stored in `data/raw/wikitext/`.

3. **Extract citation URLs**

   ```bash
   python -m core.extract_refs
   ```

   The extracted references are written to `data/processed/refs_extracted.json`.

4. **Normalize and rank sources**

   ```bash
   python -m core.clean_sources
   ```

  The script applies domain aliases from `data/alias_map.json`, writes canonical counts to `data/processed/sources_canonical.csv`, and outputs the top sources to `outputs/top_sources.csv`.

### Updating domain aliases

Add new mappings in `data/alias_map.json` to normalize additional domains.
Each entry maps a short hostname to its canonical form. These aliases are loaded
by `core/clean_sources`, so updates affect how sources are deduplicated.

## Generating the goggles

The two `.goggle` files are build artifacts of the reliability data, not hand-edited files. `core.build_goggle` merges two layers:

- a **base** layer derived from the data — one `site=` rule per rated domain, with the reliability status mapped to a Goggle action (`gr`→`$boost=2`, `nc`→`$downrank=2`, `gu`/`d`→`$discard`, `m`→no rule); and
- a curated **overlay** ([`goggle_overlay.txt`](goggle_overlay.txt)) holding rules the data cannot yet derive: per-topic path-qualified rules (`/*science^…`) and domains added by hand or mined from Featured/Good-article citations.

```bash
python -m core.build_goggle
```

This reads `outputs/reliability_ranking.csv` (produced by `core.bridge_reliability`) and `goggle_overlay.txt`, then writes both goggle variants and `outputs/goggle_gap_candidates.csv` (heavily-cited but unrated domains, for manual review — never auto-added).

On a conflict, the curated overlay value wins. Edit `goggle_overlay.txt` by hand to maintain rules the generator can't produce.

### Domain exclusions

Some ranking entries describe a narrow product or portal (e.g. "Google Maps (Google Street View)" rated `nc`) that resolves to a generic registrable domain shared by the whole platform. Emitting a `site=google.com` rule from such an entry would downrank every Google property, not just Street View. These domains are listed in `PRODUCT_PORTAL_DOMAINS` in `core/build_goggle.py` and are excluded from base rule generation. Human curation via `goggle_overlay.txt` remains fully expressible for those domains.

### Bootstrapping the overlay

The overlay is seeded once from the existing hand-maintained goggle, capturing every rule the base does not reproduce:

```bash
python -m core.build_goggle --seed-overlay
```

Run this against the pristine hand file, before the first generated build overwrites it; the command refuses to seed from an already-generated goggle. Seeding also writes `outputs/goggle_diff.md` — what the base generates versus the hand-maintained goggle: additions, conflicts (where the data disagrees with a curated rule), and the overlay-preserved remainder. The diff reflects that one-time comparison, so the normal build does not regenerate it.

## Running tests

Install the dependencies listed in `requirements.txt` and execute the test suite with `pytest`:

```bash
pip install -r requirements.txt
pytest
```

Contributors should run the tests before committing changes to ensure nothing breaks.

## Programmatic API usage

Import functions from the `core` package to integrate the pipeline into your own
scripts. See `docs/api_usage.md` for complete examples.

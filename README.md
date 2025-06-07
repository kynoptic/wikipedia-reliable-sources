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

## Citation normalization pipeline

The project now includes a modular workflow for gathering citation data and normalizing source URLs.

1. **Fetch article lists**

   ```bash
   python -m src.fetch_articles
   ```
   This writes `good_articles.json` and `featured_articles.json` under `data/raw/`.

2. **Download wikitext for each article**

   ```bash
   python -m src.fetch_wikitext
   ```
   Wikitext files are stored in `data/raw/wikitext/`.

3. **Extract citation URLs**

   ```bash
   python -m src.extract_refs
   ```
   The extracted references are written to `data/processed/refs_extracted.json`.

4. **Normalize and rank sources**

   ```bash
   python -m src.clean_sources
   ```
  The script applies domain aliases from `data/alias_map.json`, writes canonical counts to `data/processed/sources_canonical.csv`, and outputs the top sources to `outputs/top_sources.csv`.

### Updating domain aliases

Add new mappings in `data/alias_map.json` to normalize additional domains.
Each entry maps a short hostname to its canonical form. These aliases are loaded
by `src/clean_sources`, so updates affect how sources are deduplicated.

## Running tests

Install the dependencies listed in `requirements.txt` and execute the test suite with `pytest`:

```bash
pip install -r requirements.txt
pytest
```

Contributors should run the tests before committing changes to ensure nothing breaks.

# Build pipeline

How to regenerate the `.goggle` files from upstream Wikipedia reliability data. The flow has three stages: fetch the rated source lists, normalize citation domains from Featured/Good articles, then build the goggles.

Install dependencies first, from the repository root:

```bash
pip install -r requirements.txt
```

## Fetch the reliability source lists

Download and parse the [Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources) table. The script cleans and validates the data, then writes `perennial_sources.json` and `perennial_sources.csv`:

```bash
python scripts/fetch_perennial_sources.py
```

It prints the number of parsed entries (for example, `Fetched 485 sources`). Each record has these fields:

| Field | Description |
|-------|-------------|
| `source_name` | Name of the publication or website. |
| `reliability_status` | Two-letter code from the `WP:RSPSTATUS` legend (`gr` = generally reliable, `gu` = generally unreliable, `nc` = no consensus, `d` = deprecated, `m` = marginal). |
| `notes` | Summary of discussions about the source. |

Download the per-WikiProject reliability tables (video games, film, albums, and others), writing `wikiproject_sources.json` and `wikiproject_sources.csv` at the repository root:

```bash
python scripts/fetch_wikiproject_sources.py
```

To refresh only when upstream changed, run the update checker. It compares the current revision IDs of the perennial-sources subpages against `revision_ids.json` and re-fetches the tables only if a page has changed since the last run:

```bash
python scripts/update_checker.py
```

## Normalize citation domains

This stage mines the domains cited by Featured and Good articles so heavily-cited but unrated sources surface for review.

1. **Fetch article lists** — writes `good_articles.json` and `featured_articles.json` under `data/raw/`:

   ```bash
   python -m core.fetch_articles
   ```

2. **Download wikitext** for each article into `data/raw/wikitext/`:

   ```bash
   python -m core.fetch_wikitext
   ```

3. **Extract citation URLs** to `data/processed/refs_extracted.json`:

   ```bash
   python -m core.extract_refs
   ```

4. **Normalize and rank** — applies domain aliases from `data/alias_map.json`, writes canonical counts to `data/processed/sources_canonical.csv`, and outputs the top sources to `outputs/top_sources.csv`:

   ```bash
   python -m core.clean_sources
   ```

To normalize additional domains, add mappings to `data/alias_map.json`; see the [configuration guide](configuration.md) for the file format.

## Build the goggles

The two `.goggle` files are build artifacts of the reliability data, not hand-edited files. `core.build_goggle` merges two layers:

- a **base** layer derived from the data — one `site=` rule per rated domain, with the reliability status mapped to a Goggle action (`gr`→`$boost=2`, `nc`→`$downrank=2`, `gu`/`d`→`$discard`, `m`→no rule); and
- a curated **overlay** ([`goggle_overlay.txt`](../goggle_overlay.txt)) holding rules the data cannot yet derive: per-topic path-qualified rules (`/*science^…`) and domains added by hand or mined from Featured/Good-article citations.

```bash
python -m core.build_goggle
```

This reads `outputs/reliability_ranking.csv` (produced by `core.bridge_reliability`) and `goggle_overlay.txt`, then writes both goggle variants and `outputs/goggle_gap_candidates.csv` (heavily-cited but unrated domains, for manual review — never auto-added). On a conflict, the curated overlay value wins. Edit `goggle_overlay.txt` by hand to maintain rules the generator can't produce.

### Domain exclusions

Some ranking entries describe a narrow product or portal (for example, "Google Maps (Google Street View)" rated `nc`) that resolves to a generic registrable domain shared by the whole platform. Emitting a `site=google.com` rule from such an entry would downrank every Google property, not just Street View. These domains are listed in `PRODUCT_PORTAL_DOMAINS` in `core/build_goggle.py` and excluded from base rule generation. Human curation via `goggle_overlay.txt` remains fully expressible for those domains.

### Bootstrapping the overlay

The overlay is seeded once from the existing hand-maintained goggle, capturing every rule the base does not reproduce:

```bash
python -m core.build_goggle --seed-overlay
```

Run this against the pristine hand file, before the first generated build overwrites it; the command refuses to seed from an already-generated goggle. Seeding also writes `outputs/goggle_diff.md` — what the base generates versus the hand-maintained goggle: additions, conflicts (where the data disagrees with a curated rule), and the overlay-preserved remainder. The diff reflects that one-time comparison, so a normal build does not regenerate it.

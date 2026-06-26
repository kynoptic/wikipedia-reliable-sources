# [`/data/processed`]

## Purpose

Normalized citation and source data produced by the cleaning pipeline.

## Contents

### Files

* **[`refs_extracted.json`](./refs_extracted.json)** – Citation URLs extracted
  from wikitext
* **[`sources_canonical.csv`](./sources_canonical.csv)** – Ranked list of
  canonicalized sources

### Generated files (git-ignored)

Produced by `core.process_citations` from the citation dumps; large and
regenerable, so kept out of git history.

* **`citations_by_host.csv`** – One row per host (e.g. `news.bbc.co.uk`) with
  columns `host_url`, `subdomain_url`, `domain_url`, `suffix_url`, `total_citations`,
  `fa_citations`, `ga_citations`, and `distinct_articles`. The `fa_`/`ga_` counts are
  citations from Featured/Good articles.
* **`citations_by_domain.csv`** – The same aggregation collapsed onto
  `(domain_url, suffix_url)`, dropping the host/subdomain columns.

## Usage

`core.clean_sources` produces the canonical source files; `core.process_citations`
produces the per-host and per-domain citation tables. These files can be analyzed
or used in further processing.

## Related modules

* [`../../core/`](../../core/) – Modules that produce and consume these outputs
* [`../raw/`](../raw/) – Source data used to generate the processed files
* [`../README.md`](../README.md) – Data directory overview

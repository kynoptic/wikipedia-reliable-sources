# [`/outputs`]

## Purpose

Post-processed reports and summaries generated from the dataset.

## Contents

### Files

* **[`top_sources.csv`](./top_sources.csv)** – Ranking of the most cited domains
* **[`top_sources_by_domain.csv`](./top_sources_by_domain.csv)** – Top domains
  from the citation dumps, with Featured/Good-article citation counts

## Usage

`core.clean_sources` produces the cited-domain ranking; `core.process_citations`
produces the citation-dump ranking. Both can be viewed in spreadsheet software or
used for analysis.

## Related modules

* [`../core/`](../core/) – Cleaning and ranking logic
* [`../data/processed/`](../data/processed/) – Source data for these outputs
* [`../README.md`](../README.md) – Project overview

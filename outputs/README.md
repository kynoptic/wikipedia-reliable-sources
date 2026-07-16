# [`/outputs`]

## Purpose

Post-processed reports and summaries generated from the dataset.

## Contents

### Files

* **[`top_sources.csv`](./top_sources.csv)** – Ranking of the most cited domains
* **[`top_sources_by_domain.csv`](./top_sources_by_domain.csv)** – Top domains
  from the citation dumps, with Featured/Good-article citation counts
* **[`reliability_ranking.csv`](./reliability_ranking.csv)** – Reliability-rated
  sources ranked by citation volume, one row per resolved domain, sourced from
  the Perennial Sources list and, optionally, WikiProject-specific reliability
  tables
* **[`red_flags.csv`](./red_flags.csv)** – Heavily-cited domains rated unreliable
  or deprecated
* **[`coverage_gaps.csv`](./coverage_gaps.csv)** – Heavily-cited editorial domains
  with no reliability rating yet
* **[`goggle_diff.md`](./goggle_diff.md)** – What the data-driven goggle base
  generates versus the committed goggle: additions, conflicts, and the rules
  preserved in the curated overlay
* **[`goggle_gap_candidates.csv`](./goggle_gap_candidates.csv)** – Unrated domains
  surfaced for manual review when building the goggles; never auto-added

## Usage

`core.clean_sources` produces the cited-domain ranking; `core.process_citations`
produces the citation-dump ranking; `core.bridge_reliability` joins the Perennial
Sources ratings — merged with the optional WikiProject-specific ratings from
`--wikiproject` (`wikiproject_sources.csv`) — to citation volume to produce the
reliability ranking, red flags, and coverage gaps. A source rated by both the
Perennial Sources list and a WikiProject list, or by more than one WikiProject
list, is merged to the most cautious of its ratings before the domain join.
Rows in the bridge outputs are keyed by domain: sources that share a domain
(Perennial Sources lists some outlets per era or section, and a domain can also
be rated by more than one input list) collapse into one row carrying the most
cautious of their ratings; the merged row does not record which list(s)
contributed it. `core.build_goggle` consumes the reliability ranking to
regenerate the goggle files and the gap-candidate report; the goggle diff is
written when the overlay is seeded. All files can be viewed in spreadsheet
software or used for analysis.

## Related modules

* [`../core/`](../core/) – Cleaning and ranking logic
* [`../data/processed/`](../data/processed/) – Source data for these outputs
* [`../README.md`](../README.md) – Project overview

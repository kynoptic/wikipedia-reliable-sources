# Changelog

All notable user-facing changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Engineering-facing changes live in [DEVLOG.md](DEVLOG.md).

## [Unreleased]

### Added

- The reliability bridge can now ingest WikiProject source ratings: a bridge
  run with `--wikiproject` joins `wikiproject_sources.csv` alongside the
  Perennial Sources list, so domains from the six WikiProject source guides
  surface as generated `.goggle` rules on the next data regeneration (the
  committed ranking and goggle files are not yet regenerated)
- `fetch_wikiproject_sources.py` now covers three more WikiProject pages —
  Anime and manga/Online reliable sources, Board and table games/Sources,
  and National Basketball Association/References — so their ratings will
  surface once the ranking is regenerated (tracked in #55, since a full
  regeneration currently drops hand-edited rows)
- The goggle header's documented page list now matches what the fetch layer
  actually consumes; `WikiProject_Video_games/Search_engine` was removed
  since its bare-URL inclusion/exclusion format does not fit the
  reliability-status model the rest of the pipeline expects

## [0.1.0] - 2026-06-26

First tagged release.

### Added

- Two Brave Search goggle files that rerank results by Wikipedia community
  reliability:
  - `wikipedia-reliable-sources-only.goggle` — boosts reliable sources and shows
    nothing else
  - `wikipedia-reliable-sources.goggle` — boosts reliable sources and discards
    unreliable ones while keeping other results
- Tiered ranking rules: generally reliable sources are boosted, "no consensus"
  sources downranked, and unreliable, deprecated, or blacklisted sources discarded
- Reliability data compiled from Wikipedia's Perennial Sources list, six
  WikiProject source guides (Video games, Film, Albums, Christian music,
  Professional wrestling, Korea), and sources frequently cited in Featured and
  Good Articles
- Fetchers that download and parse each upstream source list:
  - `fetch_perennial_sources.py` — writes structured `perennial_sources.json` and
    `.csv` with reliability-status codes and discussion notes
  - `fetch_wikiproject_sources.py` — WikiProject source recommendations
  - `fetch_citation_data.py` — citation data extracted from articles
- Source-reliability bridge that maps each rated source to its domains, validates
  the generated rules, and deduplicates output into `reliability_ranking.csv`
- Update checker that detects when Wikipedia's upstream ratings change and
  regenerates the affected outputs

[0.1.0]: https://github.com/kynoptic/wikipedia-reliable-sources/releases/tag/v0.1.0

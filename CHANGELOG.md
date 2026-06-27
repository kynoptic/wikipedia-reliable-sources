# Changelog

All notable user-facing changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Engineering-facing changes live in [DEVLOG.md](DEVLOG.md).

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

# Development log

Engineering-facing changes — internal tooling, tests, refactors, and developer
docs — that do not affect end users. User-facing changes live in
[CHANGELOG.md](CHANGELOG.md).

## [0.1.0] - 2026-06-26

### Added

- Python package under `core/` for the data pipeline: citation processing,
  reliability bridge, goggle builder, source cleaning, URL normalization, and
  article/wikitext fetching
- Standalone command-line utilities under `scripts/` wrapping the fetch and
  update-check workflows
- Project organized into semantic directories (`core/`, `scripts/`, `data/`,
  `outputs/`, `tests/`, `docs/`)
- CI workflow running the pytest suite and markdown lint on every push
- Pytest coverage across the citation pipeline, reliability bridge, goggle build,
  URL normalization, source cleaning, and update checker
- markdownlint-styleguide linting wired up via a git-tag dependency
- Documentation: README with goggle usage and reliability parameters, per-script
  guides, and programmatic API usage notes

[0.1.0]: https://github.com/kynoptic/wikipedia-reliable-sources/releases/tag/v0.1.0

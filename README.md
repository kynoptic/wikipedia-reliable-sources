# Wikipedia Goggles

Three [Brave Search Goggles](https://github.com/brave/goggles-quickstart) that rerank search results according to what the Wikipedia community considers reliable:

1. **`wikipedia-reliable-sources-only.goggle`** – Boosts reliable sources and downranks contentious ones, showing no other results. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%253A%252F%252Fraw.githubusercontent.com%252Fkynoptic%252Fwikipedia-reliable-sources%252Fmain%252Fwikipedia-reliable-sources-only.goggle).
2. **`wikipedia-reliable-sources.goggle`** – Similar to the first, but allows additional sources while discarding those deemed unreliable. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fkynoptic%2Fwikipedia-reliable-sources%2Fmain%2Fwikipedia-reliable-sources.goggle).
3. **`wikipedia-reliable-sources-demote.goggle`** – Downranks contentious sources and discards unreliable ones, boosting nothing, so normal ranking decides everything else. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fkynoptic%2Fwikipedia-reliable-sources%2Fmain%2Fwikipedia-reliable-sources-demote.goggle).

## Reliability sources

Reliability ratings are drawn from these Wikipedia pages:

- [Reliable sources/Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources)
- [WikiProject Video games/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Video_games/Sources)
- [WikiProject Film/Resources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Film/Resources)
- [WikiProject Albums/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Albums/Sources)
- [WikiProject Christian music/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Christian_music/Sources)
- [WikiProject Professional wrestling/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Professional_wrestling/Sources)
- [WikiProject Korea/Reliable sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Korea/Reliable_sources)
- [WikiProject Anime and manga/Online reliable sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Anime_and_manga/Online_reliable_sources)
- [WikiProject Board and table games/Sources](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Board_and_table_games/Sources)
- [WikiProject National Basketball Association/References](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/References)

Sources frequently cited in Featured Articles (FA) and Good Articles (GA) are also included.

## How reliability affects rankings

Each rated domain maps to a Goggle action:

- `$boost=2` – sources considered "Generally reliable" or "Reliable"
- `$downrank=2` – sources labeled "No consensus"
- `$discard` – sources determined "Unreliable," "Blacklisted," or "Deprecated"

## Quickstart

Requires Python 3. From the repository root:

```bash
pip install -r requirements.txt   # install dependencies
pytest                            # run the test suite
python -m core.build_goggle       # regenerate both .goggle files
```

The `.goggle` files are build artifacts of the reliability data, not hand-edited. To regenerate them from upstream — fetching the source lists, normalizing citation domains, and merging the curated overlay — see the [build pipeline guide](docs/pipeline.md).

## Project structure

- `core/` – pipeline modules (fetch, normalize, rank, build)
- `scripts/` – standalone command-line utilities
- `tests/` – pytest suite
- `data/` – raw and processed datasets
- `outputs/` – generated rankings and reports
- `docs/` – pipeline, configuration, API, and roadmap documentation

## Documentation

- [Build pipeline](docs/pipeline.md) – regenerate the goggles end to end
- [Programmatic API usage](docs/api_usage.md) – call the `core` modules from your own scripts
- [Configuration](docs/configuration.md) – editable settings and defaults
- [Roadmap](docs/roadmap.md) – development goals

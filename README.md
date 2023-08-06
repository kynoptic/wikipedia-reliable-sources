# Wikipedia reliable sources Goggles for Brave search

This repository hosts two Goggle files that enhance the search experience on Brave Search by utilizing Wikipedia's reliability ratings:

1. **`wikipedia-reliable-sources-only.goggle`** – This file boosts reliable sources and downranks contentious ones, showing no other results. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%253A%252F%252Fraw.githubusercontent.com%252Fkynoptic%252Fwikipedia-reliable-sources%252Fmain%252Fwikipedia-reliable-sources-only.goggle).
2. **`wikipedia-reliable-sources.goggle`** – Similar to the first, but it allows additional sources while discarding those deemed unreliable. [Search using this Goggle](https://search.brave.com/goggles?goggles_id=https%3A%2F%2Fraw.githubusercontent.com%2Fkynoptic%2Fwikipedia-reliable-sources%2Fmain%2Fwikipedia-reliable-sources.goggle).

## About Goggles

Goggles are an innovative feature of Brave Search, enabling users to choose, modify, or enhance the ranking of search results. They provide a transparent and customizable means to refine your search experience.

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

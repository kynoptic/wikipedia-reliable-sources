# Roadmap

## 📌 Objective

Programmatically extract and structure data from [Wikipedia:Reliable sources/Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources), converting it into a machine-readable format (e.g. JSON, CSV, or a database table) for downstream use.

## 🧪 Fetching raw content

**Option A – Wikitext (recommended for flexibility):**

* [x] Use MediaWiki API:

  ```http
  GET https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&rvprop=content&titles=Wikipedia:Reliable_sources/Perennial_sources
  ```

* Tooling:

  * [x] Use `requests` (or similar HTTP client).
  * [x] Use `mwparserfromhell` to parse the returned wikitext into a usable format.

**Option B – Rendered HTML:**

* [ ] Use Wikipedia REST API:

  ```http
  GET https://en.wikipedia.org/api/rest_v1/page/html/Wikipedia:Reliable_sources/Perennial_sources
  ```

* Tooling:

  * [ ] Use `requests` + `BeautifulSoup` to parse `<table class="wikitable">`.

* Detect and flag disputed sources.
* Build a web API to serve structured data.
* Map source domains to categories or political leanings.
* Integrate with a citation checker.

## Maintenance

* [x] Document contributor guidelines in `AGENTS.md`.
* [ ] Expand test coverage for new modules.
* [ ] Set up continuous integration to run tests automatically.
* [x] Standardize default config constant naming.

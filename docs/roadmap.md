
### 📌 Objective

Programmatically extract and structure data from [Wikipedia:Reliable sources/Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources), converting it into a machine-readable format (e.g. JSON, CSV, or a database table) for downstream use.

---

### ✅ Discovery and scoping

**Goal**: Understand the structure and format of the Wikipedia page.

* [ ] Review the page manually in both rendered and wikitext form.
* [ ] Note:

  * Number and format of tables.
  * Columns used (e.g., Source, Reliability, Notes, Applies to).
  * Any irregularities (merged cells, nested templates, etc.).

---

### 🧪 Fetching raw content

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

---

### 🏗️ Parse tables into structured records

**Goal**: Convert each wikitable row into a Python dict (or class object).

* [x] Extract rows from each table.
* [x] Parse individual cells into structured fields:

  * `source_name`
  * `reliability_status` (e.g. "generally unreliable")
  * `notes` (remove formatting)
  * `applies_to` (e.g. "politics", "science")

**Tips**:

* Normalize field names.
* Handle empty or merged cells.
* Remove wikitext artifacts (`[[`, `{{`, `<ref>`, etc.)

---

### 🧹 Clean and validate data

* [x] Ensure consistency in field values (e.g., normalize "generally reliable", "deprecated").
* [x] Deduplicate if needed.
* [x] Validate against a few test entries manually.

---

### 💾 Export and reuse

* [x] Output to:

  * `JSON` for API or frontend use.
  * `CSV` for analysis.
* [ ] Optional: Save to SQLite or Postgres table if needed.

---

### 🧪 Update checker (optional)

If you want to keep the data fresh:

* [x] Check for page edits via MediaWiki API `action=query&prop=revisions`.
* [x] If last revision ID differs, re-fetch and update.

---

### 📘 Deliverables

* [x] Python script or module:

  * `fetch_perennial_sources.py` or similar.
* [x] Output:

  * `perennial_sources.json` or `perennial_sources.csv`
* [x] README:

  * Instructions to run, dependencies, data fields description.

---

### 📦 Modular citation normalization pipeline

Build a configurable pipeline that turns raw citation data into canonical source counts.

**Tasks**:
* [x] Organize the project with a clear directory structure under `src/`, `data/`, and `outputs/`.
* [x] Implement URL normalization logic in `src/utils/normalize_url.py` with support for alias mapping and query stripping.
* [x] Process extracted references in `clean_sources.py` to count total and unique citations per source.
* [x] Output `sources_canonical.csv` and `top_sources.csv` summarizing the results.

---

### 🧠 Stretch goals (optional)

* Detect and flag disputed sources.
* Build a web API to serve structured data.
* Map source domains to categories or political leanings.
* Integrate with a citation checker.



### 📌 Objective

Programmatically extract and structure data from [Wikipedia:Reliable sources/Perennial sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources), converting it into a machine-readable format (e.g. JSON, CSV, or a database table) for downstream use.

---

### ✅ Phase 1: Discovery and scoping

**Goal**: Understand the structure and format of the Wikipedia page.

* [ ] Review the page manually in both rendered and wikitext form.
* [ ] Note:

  * Number and format of tables.
  * Columns used (e.g., Source, Reliability, Notes, Applies to).
  * Any irregularities (merged cells, nested templates, etc.).

---

### 🧪 Phase 2: Fetching raw content

**Option A – Wikitext (recommended for flexibility):**

* Use MediaWiki API:

  ```http
  GET https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&rvprop=content&titles=Wikipedia:Reliable_sources/Perennial_sources
  ```

* Tooling:

  * Use `requests` (or similar HTTP client).
  * Use `mwparserfromhell` to parse the returned wikitext into a usable format.

**Option B – Rendered HTML:**

* Use Wikipedia REST API:

  ```http
  GET https://en.wikipedia.org/api/rest_v1/page/html/Wikipedia:Reliable_sources/Perennial_sources
  ```

* Tooling:

  * Use `requests` + `BeautifulSoup` to parse `<table class="wikitable">`.

---

### 🏗️ Phase 3: Parse tables into structured records

**Goal**: Convert each wikitable row into a Python dict (or class object).

* [ ] Extract rows from each table.
* [ ] Parse individual cells into structured fields:

  * `source_name`
  * `reliability_status` (e.g. "generally unreliable")
  * `notes` (remove formatting)
  * `applies_to` (e.g. "politics", "science")

**Tips**:

* Normalize field names.
* Handle empty or merged cells.
* Remove wikitext artifacts (`[[`, `{{`, `<ref>`, etc.)

---

### 🧹 Phase 4: Clean and validate data

* [ ] Ensure consistency in field values (e.g., normalize "generally reliable", "deprecated").
* [ ] Deduplicate if needed.
* [ ] Validate against a few test entries manually.

---

### 💾 Phase 5: Export and reuse

* [ ] Output to:

  * `JSON` for API or frontend use.
  * `CSV` for analysis.
* [ ] Optional: Save to SQLite or Postgres table if needed.

---

### 🧪 Phase 6 (Optional): Update checker

If you want to keep the data fresh:

* [ ] Check for page edits via MediaWiki API `action=query&prop=revisions`.
* [ ] If last revision ID differs, re-fetch and update.

---

### 📘 Deliverables

* Python script or module:

  * `fetch_perennial_sources.py` or similar.
* Output:

  * `perennial_sources.json` or `perennial_sources.csv`
* README:

  * Instructions to run, dependencies, data fields description.

---

### 🧠 Stretch goals (optional)

* Detect and flag disputed sources.
* Build a web API to serve structured data.
* Map source domains to categories or political leanings.
* Integrate with a citation checker.


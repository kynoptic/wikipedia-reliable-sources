# `AGENTS.md` – Project guide for AI agents

## Project overview and goals

Wikipedia Goggles provides Brave Search Goggle definitions and tools for processing Wikipedia's reliability data. Scripts fetch article lists, download wikitext, extract citation URLs, and rank domains so search results favor reputable sources.

The long-term goal is to automatically fetch the Perennial Sources table, other reliable source lists from WikiProjects, and sources used in Featured Articles and Good Articles to automatically update the Goggle definition.

## Repository structure

- `/core/` – Python modules for fetching and processing data
  - `fetch_articles.py` – Download lists of featured and good articles
  - `fetch_wikitext.py` – Retrieve article wikitext
  - `extract_refs.py` – Parse citation URLs
  - `clean_sources.py` – Normalize and rank references
  - `/utils/` – Shared helpers such as `normalize_url.py`
- `/scripts/` – Standalone command line utilities
  - `fetch_perennial_sources.py` – Parse perennial source tables
  - `update_checker.py` – Detect page updates and regenerate outputs
- `/data/` – Raw and processed datasets
- `/outputs/` – Generated reports
- `/tests/` – Pytest suite covering modules and scripts
- `/docs/` – Roadmap and configuration notes
- `.github/` – Continuous integration workflow
- `requirements.txt` – Python dependencies
- `wikipedia-reliable-sources.goggle` – Brave Search Goggle definition

### Key files

- `.github/workflows/ci.yml` – Runs tests on push and pull request

## Environment setup and commands

- **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

- **Run scripts** (examples):

    ```bash
    python scripts/fetch_perennial_sources.py
    python scripts/update_checker.py
    ```

- **Run tests**:

    ```bash
    pytest
    ```

## Markdown formatting conventions

- Use backticks to wrap all:
  - Filenames (e.g., `main.py`)
  - Directories (e.g., `src/`)
  - Code snippets, flags, and inline commands (e.g., `--help`)
- Prefer fenced code blocks (` ``` `) for multi-line commands or examples
- Markdown files must be named in kebab case (e.g., `my-file.md`) with no spaces.
  Spaces are acceptable in image filenames, external links, and other asset references.

## Code clarity and documentation standards

- Follow PEP 8 style conventions
- Include type hints and docstrings on all new Python code
- Provide unit tests for new functionality and keep existing tests passing
- Commit messages must follow Conventional Commits without a scope
- Run `pytest` before each commit

## Tools and capabilities

- `requests` and `beautifulsoup4` for HTTP and HTML parsing
- `mwparserfromhell` for wikitext parsing
- GitHub Actions runs `pytest` via `ci.yml`

## Agent roles and interaction

- Single autonomous agent responsible for planning, coding, and testing

## Constraints and safety rules

- **ALWAYS** run `pytest` and ensure it passes before committing
- **NEVER** bypass the Conventional Commits format
- **KEEP** commit scopes empty (`<type>: <subject>`)

## Known issues and context

- Integration tests for the update workflow are still missing
- Documentation needs examples of API usage

## Example tasks

- **Add integration tests for update workflow**
  - Edit: `tests/test_update_checker.py`
  - Validate with: `pytest`
- **Build API to serve structured data**
  - Add a new module under `core/`
  - Provide tests and update documentation

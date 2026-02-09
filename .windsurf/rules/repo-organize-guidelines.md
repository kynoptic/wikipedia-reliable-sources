---
trigger: model_decision
description: "Enforce high-level repository layout for discoverability and AI compatibility."
---

# Semantic organization of the repository

- Group related content into clearly named directories (e.g. `core/`, `ui/`, `tests/`, `docs/`, `extension/`).
- Avoid cryptic or abbreviated names; prefer descriptive names like `cli_interface/` or `prompt_templates/`.
- Place a concise `README.md` in major directories to explain purpose and structure (e.g. `docs/architecture/README.md`).
- Split up excessively large source files; avoid "God files" exceeding typical AI or human readability thresholds.
- Keep modules focused; follow separation of concerns to support modular loading and indexing.
- Order and format code consistently—group related functions, maintain style conventions, and apply standard docstring/documentation patterns.
- Centralize configuration files in-repo and document all config options with comments and/or in `docs/configuration.md`.
- Treat file paths and names as discoverability aids—for both human contributors and AI tools relying on semantic cues.


---
trigger: glob
description: "A consolidated set of rules for maintaining a structured, human-readable changelog following the Keep a Changelog standard."
globs: "**/CHANGELOG.md"
name: "changelog-rules"
---
# Changelog standards (Keep a Changelog)

- Adhere strictly to the [Keep a Changelog](https://keepachangelog.com) format and [Semantic Versioning 2.0.0](https://semver.org).
- Maintain an `## [Unreleased]` section at the top for all new changes.
- Use H2 headings for versions in reverse chronological order, with dates formatted as `YYYY-MM-DD` (e.g., `## [1.2.0] - 2025-07-15`).
- Group all changes under one of the following H3 headings: `### Added`, `### Changed`, `### Deprecated`, `### Removed`, `### Fixed`, or `### Security`.
- Write entries for humans, not machines. Focus on the *impact* of the change.
  - Start each entry with an imperative verb (e.g., "Add support for...", "Fix crash when...").
  - **Good:** `Fix a bug where the parser would crash on malformed input.`
  - **Bad:** Pasting a raw git commit message like `a3f4b1: refactor(parser)`.
- Remove any empty change-type sections from a release to avoid clutter.
- Tag each release in version control to match the changelog version (e.g., `git tag -a v1.2.0`).
- For retracted releases, add a `[YANKED]` tag to the version heading.


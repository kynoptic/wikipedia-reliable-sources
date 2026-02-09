---
trigger: glob
description: "Ensure consistent naming, documentation, and AI-readable metadata across source files."
globs: "**/*.py,**/*.js,**/*.ts,**/*.md,**/*.java,**/*.go,**/*.rs"
---
# Code clarity standards for naming, documentation, and AI usability

## Naming and file metadata

- Use precise, domain-relevant names for all variables, functions, classes, and files.
- Avoid vague or generic names (e.g. `temp`, `foo`, `data`, `list`) and unclear abbreviations.
- Add type annotations for all function parameters and return values in supported languages.
- Start each source file with a short header comment summarizing its purpose and contents.
- Document non-obvious metadata (e.g. side effects, environment dependencies, external references) in the file header.

## Docstrings and inline comments

- Write a concise docstring for every public function, class, and method.
- Start each docstring with a summary of the entity’s purpose and problem it solves.
- Use a structured format (e.g. `Args:` / `Returns:`) to describe inputs and outputs.
- Include usage examples for complex or reusable functions to aid AI and human readers.
- Standardize on a single docstring style (e.g. triple-quoted Python, JSDoc, or Javadoc) across the codebase.
- Use inline comments to explain non-obvious logic, edge cases, or design decisions—not just what the code does.
- Avoid redundant comments (e.g. `i += 1  // increment i`) that restate the code.
- Treat missing, vague, or misleading documentation as a code review blocker when warranted.

## AI-aligned clarity

- Favor explicitness over brevity in naming, docstrings, and metadata.
- Structure documentation to be easily parsed by both humans and LLMs.
- Clarify behavior, intent, and edge cases to support accurate AI generation and future maintenance.


# `/.vscode/custom-rules`

## Purpose

Store the project's custom markdownlint rules for local development and testing.

## Contents

### Files

* **[`backtick-code-elements.js`](./backtick-code-elements.js)** – Enforces backticks around code snippets.
* **[`sentence-case-heading.js`](./sentence-case-heading.js)** – Requires headings to use sentence case.

## Usage

Point markdownlint at this directory using the `customRules` option or `import` the files into your own configuration.

## Related modules

* [`../../src/`](../../src/) – Exports these rules as a single array.
* [`../../docs/reference/rules.md`](../../docs/reference/rules.md) – Rule descriptions and examples.
* [`../../README.md`](../../README.md) – Project overview.

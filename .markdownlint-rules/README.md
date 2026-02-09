# `/src`
<!-- markdownlint-disable backtick-code-elements -->

## Purpose

This folder exposes the package entry point and shared utilities.

## Contents

### Files

* **[`index.js`](./index.js)** – Aggregates and exports all custom markdownlint rules.
* **[`logger.js`](./logger.js)** – Debug logger configured via the `debug` module.

## Usage

Import the rule array and use it with markdownlint or custom tooling:

```javascript
import rules from 'markdownlint-trap';
```

## Related modules

* [`../.vscode/custom-rules/`](../.vscode/custom-rules/) – Rule implementations.
* [`../README.md`](../README.md) – Project overview.
<!-- markdownlint-enable backtick-code-elements -->

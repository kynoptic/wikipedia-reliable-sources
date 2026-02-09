---
trigger: glob
description: "Apply file and module structure conventions across the codebase."
globs: "**/*"
---
# Code structure and clarity guidelines

- Group code by feature domain (e.g. `/auth`, `/orders`), not by file type.
- Avoid deep directory nesting; favor flatter, clearer structures.
- Start each service or app with a single, clear entry point (e.g. `main.ts`, `index.js`).
- Delete unused or legacy code proactively.
- Use descriptive, intention-revealing names over comments or cleverness.
- Encapsulate side effects (e.g. DB, HTTP, filesystem) within boundary modules.
- Fail loudly in development; log or assert on unexpected states.
- Tag incomplete logic clearly with `// TODO:` or `// FIXME:` annotations.


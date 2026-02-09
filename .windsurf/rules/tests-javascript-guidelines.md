---
trigger: glob
description: "Enforce test-first and behavior-driven test practices in JavaScript and TypeScript."
globs: "**/test_*.js,**/test_*.ts,**/*_test.js,**/*_test.ts,**/tests/**/*.js,**/tests/**/*.ts"
---
# JavaScript and TypeScript behavior-focused test conventions

- Begin with a failing test that captures the intended behavior before writing implementation code.
- Follow the red–green–refactor pattern for all changes.
- **FORBIDDEN: Bypassing test failures or disabling tests to achieve feature goals.** Tests exist to prevent regressions and improve code quality—they are not obstacles to remove when inconvenient.
- Use framework-standard naming for test files (e.g. `*.test.js`, `*.spec.ts`) and behavioral test names (e.g. `should_X_when_Y`).
- Keep tests short, focused, and isolated; refactor repeated logic into shared utilities or fixtures.
- Use parameterized testing features (e.g. `test.each` in Jest) for input variation.
- Mock external dependencies only (APIs, timers, file system) using `jest.mock` or `sinon`; test real object interactions when possible.
- Include failure-path tests to validate resilience and error handling.
- Focus on behavior quality over coverage percentages; use coverage tools for information but prioritize meaningful test validation.
- Use property-based libraries (e.g. `fast-check`) where input space is large or unpredictable.
- NEVER rewrite a test to pass broken logic; treat tests as behavioral contracts.
- Use tags or naming patterns (`describe.unit`, `describe.feature`) to support filtered CI runs.


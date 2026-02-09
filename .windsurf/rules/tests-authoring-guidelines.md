---
trigger: model_decision
description: "Global test-first strategy for all languages and frameworks."
---
# Test quality and behavior-focused strategy

- Write a failing test *before* implementing a new feature, bug fix, or refactor.
- Use the red–green–refactor cycle to iteratively define, implement, and refine behavior.
- Structure test files and function names to match framework discovery patterns (e.g., `test_*.ext`, `*.spec.ext`).
- Test one behavior per function with descriptive names (`test_should_X_when_Y`); group assertions only if verifying a single concern.
- Keep test logic minimal; extract setup to fixtures or reusable helpers.
- Use data-driven or parameterized tests to cover edge cases and behavioral variance.
- Mock external dependencies only (I/O, time, network); avoid mocking internal objects to test real interactions.
- Include failure-path and edge-case tests to clarify expected boundaries and errors.
- Focus on behavior coverage over code coverage metrics; write tests that verify meaningful user-facing functionality.
- Prefer property-based testing for scenarios involving input invariants or unpredictable input spaces.
- NEVER alter tests to suit incorrect behavior—only update when intended behavior changes.
- **FORBIDDEN: Bypassing tests to achieve user goals, even temporarily.** Tests exist to improve code quality and catch regressions—they are not barriers to remove when inconvenient.
- **FORBIDDEN: Taking shortcuts around test failures without explicit user permission.** Always fix the underlying issue causing test failures.
- Commit tests and implementation together to preserve them as co-evolving specifications.

## Recommended folder structure

```text
tests/
├── unit/         # Stateless logic and core utilities
├── features/     # Behavioral or workflow-oriented specs
├── fixtures/     # Shared setup data and mocks
└── config/       # Test runner and environment config
```


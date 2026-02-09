---
trigger: glob
description: "Conventions for authoring test files."
globs: "**/*.{test,spec}.{js,ts,jsx,tsx}"
---
# Behavior-focused test file conventions

- Write one test suite per logical module or behavior group.
- Use behavioral test names that describe outcomes (`test_should_X_when_Y`, `test_rejects_X_when_Y`).
- Test observable behavior and outcomes, not implementation details or internal method calls.
- Mock external dependencies only; test real object interactions to verify actual behavior.
- Refactor test code for readability just like production code.
- Keep fixtures and test data minimal and purpose-driven.
- Include edge cases and failure paths alongside happy-path tests.
- Avoid overlapping tests that duplicate coverage without adding confidence.

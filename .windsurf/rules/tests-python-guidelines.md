---
trigger: glob
description: "Author Python tests using PyTest with a test-first, behavior-driven workflow."
globs: "**/test_*.py,**/tests/**/*.py"
---
# Python behavior-focused testing with PyTest

- Start every feature or fix by writing a failing test that defines expected behavior.
- Follow the red–green–refactor loop: write → fail → pass → refactor.
- **FORBIDDEN: Bypassing test failures or disabling tests to achieve feature goals.** Tests exist to prevent regressions and improve code quality—they are not obstacles to remove when inconvenient.
- Name test files as `test_*.py` and use behavioral test function names like `test_should_X_when_Y` for clarity.
- Keep tests ≤10 lines; extract shared logic to fixtures or `conftest.py`.
- Use `@pytest.mark.parametrize` to express variation and edge cases.
- Group multiple `assert` statements only when they verify a single behavior.
- Mock external dependencies only (I/O, time, APIs) with `pytest-mock`; avoid mocking internal business logic.
- Use `pytest.raises` to test expected exceptions or error conditions.
- Focus on behavior quality over coverage percentages; use `pytest-cov` for information but prioritize tests that catch real bugs.
- Use `hypothesis` for property-based tests to validate invariants across diverse inputs.
- NEVER adapt a test to broken code; revise tests only when expected behavior changes.
- Tag tests with `@pytest.mark.unit` or `@pytest.mark.feature` for CI grouping and selective runs.


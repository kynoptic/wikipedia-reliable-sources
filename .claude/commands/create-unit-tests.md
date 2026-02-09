Automate the generation of language-agnostic unit tests for pure functions or logic-heavy components, ensuring correctness, edge case coverage, and maintainable test structure.

1. **Identify target function or module** – Select a deterministic, side-effect-free function or logic unit. Prefer computational helpers, data validators, or transformation routines where output depends solely on input.

2. **Analyze dependencies and imports** – Examine the target function's imports and dependencies. Identify:
   - External libraries or frameworks used (e.g. database clients, HTTP clients, file systems)
   - Internal modules or utilities required
   - Configuration or environment dependencies
   - Any third-party services or APIs accessed

3. **Define test scenarios** – Construct representative input/output pairs covering:
   - Typical use cases
   - Edge conditions (e.g. empty, null, max/min)
   - Invalid or malformed inputs  
   Store these scenarios as structured data for iteration (e.g. in JSON, YAML, or a test table).

4. **Create test file in appropriate directory** – Generate or open a test file in the language's standard test location (e.g. `tests/unit/`, `src/__tests__/`, `spec/`). Name it based on the module under test (e.g. `test_math_helpers`, `invoice_spec`).

5. **Scaffold test imports and setup** – Add necessary imports and setup code:
   - Import the target function or module being tested
   - Import required testing framework components (e.g. `jest`, `pytest`, `unittest`)
   - Import any utilities needed for test assertions or data generation
   - Set up test configuration or environment variables if required

6. **Create strategic mocks for external dependencies only** – Mock only true external dependencies:
   - **Mock:** Database clients, HTTP APIs, file system operations, external services
   - **Don't mock:** Internal objects, validators, business logic components
   - Generate mock objects using the language's mocking framework
   - Ensure mocks return predictable, controlled responses for test scenarios
   - Focus on testing the contract with external systems, not internal interactions

7. **Generate behavioral test functions** – For each scenario:
   - Use behavioral names (e.g. `test_should_sum_positive_numbers_when_valid_input`, `test_should_reject_null_input_with_clear_error`)
   - Test outcomes and behavior, not implementation details
   - Assert expected outputs using the language's test framework (e.g. `assert`, `expect`, `should`)
   - Verify the test would fail if the underlying behavior was broken

   Python (PyTest) example:

   ```python
   import pytest

   @pytest.mark.unit
   @pytest.mark.parametrize("a,b,expected", [
       (1, 2, 3),
       (0, 0, 0),
       (-1, 1, 0),
   ])
   def test_add(a, b, expected):
       assert add(a, b) == expected
   ```

8. **Support parameterized and edge tests** – Use the testing framework's parameterization feature (if available) to efficiently cover multiple inputs. For invalid or error scenarios, assert expected exceptions or error codes.

9. **Annotate tests and add documentation** – For each test, include:
   - A concise docstring or comment explaining the behavior
   - Optional metadata (e.g. component name, test category, tags):

     ```
     # Component: billing
     # Category: unit
     # Purpose: ensures invoice rounding logic handles fractions
     ```

10. **Run test suite** – Execute the full unit test suite using the project's test runner (e.g. `npm test`, `pytest`, `go test`, `cargo test`, `dotnet test`). If failures occur, rerun with verbose or debug mode to inspect causes.

    Python (PyTest) commands:

    - `pytest -q tests/unit/`
    - Verbose retry: `pytest -v tests/unit/`

11. **Refactor and ensure maintainability** – If test logic is duplicated, extract shared setup into reusable fixtures or helpers. Ensure all tests are consistently named and scoped, and that all defined scenarios are covered.

12. **Summarize and propose next steps** – Confirm that all generated tests pass. Recommend follow-up such as:
   - Adding integration or boundary-layer tests
   - Enforcing test coverage thresholds
   - Reviewing tests for business rule alignment

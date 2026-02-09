Bootstrap any software project by detecting the environment type, creating a local development runtime, installing dependencies, running a linter if configured, performing a smoke test, and logging the outcome to a setup report file.

**CRITICAL QUALITY INTEGRITY**: This workflow respects all configured quality gates (linters, tests, etc.). NEVER bypass quality checks to achieve setup goals. If quality tools fail, investigate and fix the underlying issues rather than disabling or skipping them.

1. **Detect environment type** – Inspect the root directory for standard dependency manifests such as `package.json`, `requirements.txt`, `pyproject.toml`, `Gemfile`, `go.mod`, or `Cargo.toml`. Based on presence, classify the project as Node.js, Python, Ruby, Go, Rust, or Other.

2. **Create isolated environment** – Based on the detected type:
   - **Node.js**: Use `npm install` or `yarn install` to initialize `node_modules`.
   - **Python**: Create and activate a `.venv` using `python -m venv .venv`.
   - **Ruby**: Run `bundle install`.
   - **Go**: Ensure `go.mod` exists; use `go mod download`.
   - **Rust**: Confirm presence of `Cargo.toml`; run `cargo fetch`.
   - If type is unrecognized, skip this step with a warning.

3. **Install project dependencies** – Execute the appropriate install command based on the language ecosystem. Capture output and exit code for logging.

4. **Run linter if available** – Check for the presence of common linters (e.g., `.eslintrc`, `.flake8`, `tox.ini`, `.rubocop.yml`, `clippy.toml`). If found:
   - Execute the corresponding linter command (`eslint`, `flake8`, `rubocop`, `cargo clippy`, etc.).
   - Log pass/fail status and output.
   - If no linter is found, record "no linter configured" in log.

5. **Run smoke test** – Attempt to execute a basic command to verify project operability:
   - **Node.js**: Run `npm test` if defined.
   - **Python**: Try `pytest` or import main module.
   - **Go/Rust**: Run `go test` or `cargo test`.
   - If no smoke test is defined, log a placeholder or minimal execution (e.g., check for syntax).

6. **Log results to file** – Create a `setup-log.txt` in the project root. Include:
   - Detected environment type
   - Dependency installation result (success/fail, key messages)
   - Linter output or skip reason
   - Smoke test output or skip reason
   - Timestamp and tool versions

7. **Summarize setup** – Output a summary message indicating project bootstrap status. Highlight any failures, skipped steps, or suggestions for next setup actions (e.g., "Consider adding a linter config" or "Add a test script to automate smoke check").

## Related

## Setup validation standards

**Environment detection**: Automatically identify project type (Node.js, Python, Rust, etc.) and configure appropriate development environment.

**Quality gates**: Install and configure linters, formatters, and pre-commit hooks. Ensure all tools pass before considering setup complete.

**Test integrity**: Run test suite as smoke test. Tests must pass to validate environment setup - never skip or bypass test failures.

**Documentation updates**: Generate or update README files with current setup status and next steps for contributors.

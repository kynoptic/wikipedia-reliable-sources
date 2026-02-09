---
trigger: glob
description: "Enforce consistent, structured logging in Python services and data pipelines."
globs: "**/*.py"
---
# Python logging conventions

- Use a shared `get_logger()` helper to create context-aware loggers.
- Enrich every log with structured fields (e.g., `task`, `date`, `source`, `run_id`, `stage`, `region`).
- Format log output to include timestamp, level, module name, and structured context.
- Follow log level usage:
  - `DEBUG`: diagnostics (e.g., raw payloads, parsing steps)
  - `INFO`: normal operations (e.g., task start/complete)
  - `WARNING`: recoverable issues (e.g., optional data missing)
  - `ERROR`: failed operations (e.g., HTTP errors)
  - `CRITICAL`: unrecoverable/system failures (e.g., config errors)
- Include a `correlation_id` in logs for all multi-step or multi-service operations.
- Use `@timed` decorators or `time.time()` to measure function durations.
- NEVER log sensitive data (e.g., API keys, tokens, PII); explicitly mask or omit.
- Add `extra.context` to `ERROR` and `CRITICAL` logs (e.g., exception type, inputs, remediation).
- Log all system boundaries: APIs, file I/O, database, cloud integrations.
- Configure output:
  - Console logs: `INFO+`, concise
  - File logs: `DEBUG+`, full context
- Respect a global `LOG_LEVEL` setting for environment-specific verbosity.

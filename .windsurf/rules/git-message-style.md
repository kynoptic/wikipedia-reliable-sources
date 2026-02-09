---
trigger: model_decision
description: "Standardize git commit message structure for consistency and readability."
---
# Git commit message formatting rules

## Writing style philosophy

Commits should be **imperative, action-oriented, and granular**:
- **Purpose**: Capture *what changed* in the codebase at a specific point
- **Audience**: Developers reading `git log` or debugging history
- **Style**: Short, imperative commands ("fix: handle null input in parser")

## Formatting requirements

- Use [Conventional Commits](https://www.conventionalcommits.org/) format for all commit messages
- Don't use a scope. Instead, start each commit message with `<type>: <subject>` on the first line.
- You MUST limit the subject line to 50 characters maximum.
- Use sentence case for commit subject: capitalize only the first word and proper nouns (e.g., `feat: add user authentication` not `feat: Add User Authentication`).
- Use a blank line after the subject before starting the body.
- Write body lines as bullet points with unlimited line length.
- Include only one change per bullet point in the body.
- Emphasize the *what* and *why* of changes, not the implementation details.
- Capitalize proper nouns and preserve original casing for identifiers.


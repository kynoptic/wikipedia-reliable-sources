# Contributor Guidelines

## Required workflow
- Keep these instructions open as you work.
- After **every commit** you make, open `docs/roadmap.md` and bring it up to date:
  1. Mark any finished tasks with `[x]` checkboxes.
  2. Add new unchecked boxes for follow-up work or ideas.
  3. If the roadmap looks complete, suggest fresh directions or improvements.
- The roadmap must always reflect the current repository status.

## Development practices
- Ensure all new Python code includes type hints and docstrings.
- Follow basic [PEP 8](https://peps.python.org/pep-0008/) style conventions.
- Provide unit tests for any new functionality and keep existing tests passing.
- Run `pytest` before each commit to verify the test suite.

## Commits
- Keep commits logically scoped.
- Use clear messages following [Conventional Commits](https://www.conventionalcommits.org/) with no scope.
- Start with `<type>: <subject>` on the first line.
- Limit the subject line to 50 characters.
- Leave a blank line after the subject.
- Write body lines as bullet points under 72 characters.
- Include only one change per bullet.
- Focus on what and why, not implementation details.
- Capitalize proper nouns and preserve original casing for identifiers.

Stick to these rules so that the project remains consistent and easy to maintain.

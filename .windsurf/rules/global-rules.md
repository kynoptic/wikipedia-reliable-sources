---
name: global-rules
descriptive-title: Global coding and development guidelines
description: Comprehensive rules covering tool usage, commits, versioning, documentation, formatting, and quality standards for all projects.
summary: Universal development standards including Conventional Commits, semantic versioning, MECE documentation principles, test quality over coverage metrics, and strict quality gate enforcement.
---

# Global instructions

## Essentials

**Non-negotiable guardrails that apply to ALL development work:**

- **Test integrity**: Never bypass tests, lints, or quality gates without explicit permission. Fix the root cause, not the symptom. If root cause is out of scope (e.g., dependency bugs), escalate with an ADR or issue documenting why a bypass is necessary.
- **Tiered testing workflow**: Follow the `fast → test-tiered → test → full` progression. Start with fast tests, escalate only as needed.
- **Type checking ratchet**: No regression in type coverage. Every change must maintain or improve type safety.
- **Behavioral tests only**: Tests must validate observable behavior (not implementation). Use naming pattern `test_should_<behavior>_when_<condition>` for readability. Maximum 5 mocks per test, 3:1 mock-to-assertion ratio.
- **Conventional commits**: All commits follow `<type>[scope]: <description>` format. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
- **Metadata hygiene**: All issues and PRs must have Value/Effort labels and project assignments.
- **Issue-driven delivery**: Roadmap/backlog entries are promoted to issues, developed on dedicated branches using `issue-<id>-<slug>` naming, and finished as metadata-aligned PRs. All PRs must link to issues using "Closes #123" format and inherit ALL metadata from linked issues.
- **Documentation-as-code**: All significant changes, features, and architectural decisions are documented in the repository using issues, stories, and ADRs before or during implementation. Follow complete backlog-to-delivery workflow with proper metadata hygiene.

## Tool usage

- **GitHub:** Use `gh`.
- **Secrets and credentials:** Use `op` (1Password CLI) for SSH keys and API credentials.
- **Search:** Use `rg` (ripgrep) instead of `grep`.

## Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org) standard:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- Allowed types include: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
- Use `scope` for module, directory, or component names.
- Include a body for breaking changes or multi-file refactors.
- Subject line must be ≤ 50 characters. Body lines have unlimited length.

## Release versioning

**Critical**: Follow strict semantic versioning when cutting releases. **Always use the lowest/most minor increment unless there is strong evidence at BOTH commit message level AND actual code diff level.**

- **PATCH** (x.y.z): Bug fixes, type annotations, test improvements, documentation, internal refactoring
- **MINOR** (x.y.0): New features, new CLI commands, new user-facing functionality
- **MAJOR** (x.0.0): Breaking changes, API changes, removed functionality

**Evidence required**: Analyze both `git log` messages AND `git diff` changes from previous version to justify any increment above PATCH.

## Documentation

- Apply **MECE** principles as the primary rule. Each document belongs to exactly one MECE area from the information architecture. Example IA (adapt as needed):
  - *Getting started*
  - *Tasks and operations*
  - *Configuration*
  - *APIs and schema*
  - *Concepts and architecture*
  - *Troubleshooting and known issues*
  - *Release notes and changes*

- Apply **Diátaxis** secondarily to ensure docs address one of the four areas: `tutorial`, `how-to`, `reference`, or `explanation`.

- **Single-purpose rule:** If a file spans multiple MECE areas or Diátaxis types, split it. Cross-link, don’t mix.

- Update documentation with every user-visible change.

- Record significant decisions as one-page ADRs in `docs/adr/`.
  - File naming: `adr-<number>-<short-title>.md` (e.g., `adr-001-init-architecture.md`).
  - Structure: Context, Decision, Alternatives considered, Consequences.

## Formatting

- **Backticks:** Wrap code, commands, file paths, directories, inputs, outputs, error messages, IP addresses, and data elements.
- **Bold:** Use for UI elements (**Save** button, **File** menu) and key phrases.
- **Italic:** Use for emphasis, variables in commands, and defined terms.
- **GitHub Markdown Alerts:** Use sparingly for enhanced documentation clarity. Follow hierarchy: WARNING > IMPORTANT > CAUTION > NOTE > TIP. Limit to 1-2 alerts per document section. Syntax: `> [!TYPE]` with exact capitalization.
- **Illustrative emojis:** Use purposefully and sparingly as visual signposts to aid navigation and comprehension. Choose emojis that directly relate to content meaning, not for decoration. Limit to key headings and important callouts.

## Test and quality integrity

**CRITICAL: NEVER bypass tests, lints, or other quality gates without explicit user permission.** These tools exist to improve code quality and prevent regressions—they are not obstacles to be removed when inconvenient.

- Tests and lints must pass before code is considered complete
- When quality gates fail, fix the underlying issue rather than bypassing the check
- Only bypass quality checks when the user explicitly authorizes it
- You may recommend bypassing as an option, but cannot do it without permission
- Quality tools serve the goal of better code, not as barriers to productivity

## Test quality over coverage

**Focus on behavior validation over coverage metrics** to prevent shallow "vanity tests" that execute code without verifying meaningful functionality.

- **Write behavioral tests**: Use names like `test_should_X_when_Y` that describe expected outcomes
- **Test behavior, not implementation**: Verify observable results, not internal method calls or state changes
- **Strategic mocking only**: Mock external dependencies (APIs, databases, file systems), not internal business logic
- **Include error paths**: Test boundary conditions, invalid inputs, and failure modes
- **Eliminate vanity tests**: Remove tests that pass regardless of whether the feature actually works
- **Quality over quantity**: Better to have fewer tests that catch real bugs than many shallow tests for coverage

## Style guide fallback

If uncertain, follow in this order:

1. [Google Developer Documentation Style Guide](https://developers.google.com/style)
2. [Rackspace Style Guide for Technical Content](https://style.rackspace.com/)
3. [Microsoft Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/)
4. [Apple Style Guide](https://help.apple.com/applestyleguide/)

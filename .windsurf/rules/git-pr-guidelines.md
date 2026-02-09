---
trigger: model_decision
description: "Enforce standardized conventions for Git-based repositories for pull requests."
name: "@repo-conventions"
---
# Pull request (PR) conventions

## Writing style philosophy

PR titles should be **solution-oriented and descriptive**:
- **Purpose**: Explain *what this set of commits accomplishes*
- **Audience**: Reviewers, maintainers, and release notes readers
- **Style**: Clear, solution-focused summary ("Add input validation for empty usernames")

## Requirements

- Use Git CLI to create and manage pull requests, ensuring a clean UI in GitHub.
- PR titles must clearly and concisely describe the purpose of the change using sentence case (capitalize only the first word and proper nouns).
- When squash merging, always use both `--subject` and `--body` flags to ensure proper conventional commit format: `gh pr merge --squash --subject "feat: add feature" --body "Details..."`
- Finish approved PRs with `gh pr merge` (or the GitHub UI) so the PR ends in the **Merged** state—never close a PR that already landed on `main`.
- **Critical**: GitHub's default squash merge behavior uses PR title as commit subject, which may not follow conventional commit format. Repository settings and PR title take precedence over `--body` flag for the subject line.
- Follow the branch naming convention:
  - `feat/<feature-name>`
  - `fix/<bug-name>`
  - `docs/<topic>`
- Apply labels like `type:feature` or `priority:high` to classify PRs.

## GitHub squash merge behavior (2025)

Understanding GitHub's squash merge behavior is critical for maintaining clean commit history:

### Default behavior patterns
- **Single commit PR**: Uses original commit message, ignores PR title
- **Multiple commit PR**: Uses PR title as commit subject, lists commits in body
- **Repository settings override**: Can be configured to use PR title only, PR title + commit details, or PR title + description

### Why `--body` alone is insufficient
The `gh pr merge --body` flag only controls the body text of the merge commit, not the subject line. GitHub still uses the PR title as the subject unless explicitly overridden with `--subject`.

### Recommended merge command pattern
```bash
gh pr merge <pr-number> --squash --delete-branch \
  --subject "feat(scope): conventional commit format subject" \
  --body "- Detailed change descriptions
- Context and rationale
- Impact statement

Closes #<issue-number>"
```

### Repository configuration impact
GitHub repositories can be configured with different default merge commit message formats:
- Default message (current behavior)
- Pull request title only
- Pull request title + commit details
- Pull request title + description

These settings can override CLI behavior, making explicit `--subject` usage essential for consistent conventional commit formatting.

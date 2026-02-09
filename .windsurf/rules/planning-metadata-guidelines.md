---
area: planning
subarea: metadata
goal: guidelines
platforms:
  - windsurf
  - claude
status: active
requires: []
---

# Planning metadata guidelines

## Purpose

Enforce consistent metadata across issues, pull requests, and project boards to enable effective planning, tracking, and decision-making.

## Writing style philosophy

Issues should be **problem-oriented and descriptive**:
- **Purpose**: Explain *what's wrong* (bugs) or *what's desired* (features)
- **Audience**: Team members triaging, prioritizing, or discussing work
- **Style**: Plain English, clear problem/goal statements ("Crash when saving profile with empty username")

## Required metadata fields

### Issues

Every issue MUST include:

**GitHub Project Custom Fields:**
- **Value**: Business or technical value (Essential/Useful/Nice-to-have)
  - *Tip: You can think of this similar to "Must fix/Should fix/Nice to have" used in code reviews*
- **Effort**: Engineering effort estimate (Heavy/Moderate/Light)
- **Status**: Always set to "Backlog" for new issues
- **Project**: Associated GitHub project board

**GitHub Issue Labels:**
- **Type**: bug, feature, chore, docs, etc.
- **Area**: frontend, backend, api, infra, etc.

**Dependencies**: Blocked by/Blocking relationships (when applicable)

### Pull requests

Every PR MUST:
- **Link to issue(s)**: Use "Closes #123" or "Fixes #456"
- **Inherit project metadata**: Copy Value/Effort custom fields from linked issues
- **Add to project**: Same project board as the linked issue
- **Apply labels**: Include type and area labels from issue

## Metadata alignment rules

1. **PR-Issue parity**: PRs inherit custom fields (Value/Effort) and labels from linked issues
2. **No orphan work**: Every PR must link to at least one issue
3. **Project tracking**: Both issue and PR appear on the same project board
4. **Status synchronization**: Issue status updates when PR is merged

## Labels vs Custom Fields

### GitHub Issue Labels (Repository-scoped)
- **Purpose**: Categorization and filtering within repositories
- **Scope**: Defined per repository, used for issues/PRs in that repo
- **Examples**: `bug`, `feature`, `priority:high`, `area:frontend`
- **Use for**: Type classification, area identification, quick filtering

### GitHub Project Custom Fields (Project-scoped)
- **Purpose**: Structured data tracking across repositories
- **Scope**: Defined per project, can span multiple repositories
- **Examples**: Value (Essential/Useful/Nice-to-have), Effort (Heavy/Moderate/Light)
- **Use for**: Planning data, effort estimation, value assessment


## Issue dependencies

### Blocking relationships

- **Blocked by**: Issues that must be completed before this one can start
- **Blocking**: Issues that cannot start until this one is completed
- **Maximum**: Up to 50 dependencies per relationship type
- **Visibility**: Mark dependencies in the Relationships sidebar

### Dependency search filters

Use GitHub CLI to find dependency-related issues:

```bash
# Find all blocked issues
gh issue list --search "is:blocked is:open" --json number,title,assignees

# Find issues blocking others
gh issue list --search "is:blocking is:open" --json number,title

# Find issues blocked by a specific issue
gh issue list --search "blocked-by:#123" --json number,title

# Find issues that a specific issue is blocking
gh issue list --search "blocking:#123" --json number,title

# Get detailed blocking information
gh api repos/{owner}/{repo}/issues/123/blocked_by
gh api repos/{owner}/{repo}/issues/123/blocking
```

### Dependency management commands

**Set up blocking relationship:**
```bash
# Issue A is blocked by Issue B
gh api graphql -f query='
mutation($issueId: ID!, $blockedById: ID!) {
  addBlockedBy(input: {
    issueOrPullRequestId: $issueId,
    blockedByIssueOrPullRequestId: $blockedById
  }) { issueOrPullRequest { ... on Issue { number } } }
}' -F issueId="$(gh issue view A --json id -q .id)" \
   -F blockedById="$(gh issue view B --json id -q .id)"
```

**Remove blocking relationship:**
```bash
# Remove blocking relationship
gh api graphql -f query='
mutation($issueId: ID!, $blockedById: ID!) {
  removeBlockedBy(input: {
    issueOrPullRequestId: $issueId,
    blockedByIssueOrPullRequestId: $blockedById
  }) { issueOrPullRequest { ... on Issue { number } } }
}' -F issueId="$(gh issue view A --json id -q .id)" \
   -F blockedById="$(gh issue view B --json id -q .id)"
```

### Dependency best practices

1. **Keep chains short**: Avoid dependency chains longer than 3-4 issues
2. **Document rationale**: Explain why the dependency exists
3. **Check before starting**: Verify all blockers are resolved using `gh api repos/{owner}/{repo}/issues/{issue}/blocked_by`
4. **Update status**: Mark issues as blocked when dependencies exist
5. **Notify stakeholders**: Alert assignees when their work blocks others

## Value/Effort matrix

| | Light Effort | Moderate Effort | Heavy Effort |
|---|---|---|---|
| **Essential** | Do First | Do First | Plan Carefully |
| **Useful** | Do Next | Evaluate ROI | Consider Breaking Down |
| **Nice-to-have** | Quick Wins Only | Usually Defer | Usually Skip |


## Automation expectations

- Use issue templates with metadata fields pre-configured
- Implement GitHub Actions/GitLab CI to validate metadata completeness
- Auto-link PRs to issues using branch naming conventions
- Synchronize project board columns with issue status
- Generate planning reports from metadata queries

## Anti-patterns to avoid

- Creating PRs without linked issues ("drive-by fixes")
- Mismatched effort estimates between issue and implementation
- Using generic values like "Medium" for everything
- Letting metadata drift out of sync during development
- Starting work on blocked issues without resolving dependencies
- Creating circular dependency chains
- Not updating blocked issues when blockers are resolved

## Validation checklist

Before marking issue as "Ready":
- [ ] Value assessment completed
- [ ] Effort estimated by implementer
- [ ] Status set to "Backlog"
- [ ] Project assigned
- [ ] Dependencies identified and linked
- [ ] No circular dependencies exist
- [ ] Acceptance criteria clearly defined and testable

**Acceptance criteria requirements:**
- Must be specific, measurable, and testable
- Should use GIVEN/WHEN/THEN format when appropriate
- Must include both positive and negative test cases
- Should cover edge cases and error conditions
- Must be verifiable through automated or manual testing

Before starting work on an issue:
- [ ] All blocking dependencies resolved
- [ ] Acceptance criteria understood and achievable
- [ ] Test strategy planned for each criterion

Before opening PR:
- [ ] All acceptance criteria from linked issue fulfilled
- [ ] Tests written and passing for each criterion
- [ ] Linked to issue(s) with "Closes/Fixes"
- [ ] Copied Value/Effort labels
- [ ] Added to same project as issue
- [ ] Status remains "Doing"
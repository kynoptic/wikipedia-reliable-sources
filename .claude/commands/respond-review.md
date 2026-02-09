Address reviewer feedback and resolve quality gate failures on pull requests.

Parse review comments, implement requested changes, fix failing checks, and maintain professional dialogue with reviewers.

## Prerequisites

- PR has review comments or failed checks
- Write access to PR branch
- Understanding of project quality standards

## Process

### 1. Assess feedback scope

```bash
# View PR conversation comments
gh pr view 123 --comments

# View review summaries (not inline comments)
gh pr view 123 --json reviews --jq '.reviews[] | {author:.author.login, state:.state, body:.body}'

# Get all review comments via API (includes inline)
gh api repos/:owner/:repo/pulls/123/comments --paginate

# Check CI status
gh pr checks 123
```

**Note**: `gh pr view --comments` doesn't show inline review comments. Use the API or web interface for complete view.

Categorize feedback:
- **Blocking**: Must fix before merge
- **Suggestions**: Improvements to consider
- **Questions**: Clarification needed
- **Nitpicks**: Optional polish

### 2. Parse CI failures

```bash
# Get detailed CI logs
gh run list --branch=issue-123-feature
gh run view RUN_ID --log-failed

# Common failure patterns:
# - Test failures: Extract test names
# - Lint errors: Note file:line locations
# - Type errors: Identify signatures needing fixes
```

### 3. Address blocking feedback

Start with hard requirements:

**Test failures**:
```bash
# Reproduce locally
pytest tests/path/to/failing_test.py -xvs

# Fix and verify
$EDITOR relevant_module.py
make test-last-failed
```

**Type errors**:
```bash
# See specific errors
mypy path/to/module.py

# Fix incrementally
$EDITOR module.py
mypy path/to/module.py  # Verify fix
```

**Lint violations**:
```bash
# Auto-fix where possible
ruff check --fix path/to/file.py
ruff format path/to/file.py

# Manual fixes for logic issues
$EDITOR file.py
```

### 4. Implement reviewer suggestions

For each substantive comment:

```bash
# Create focused commit addressing feedback
git add -p
git commit -m "refactor: extract validation logic per review feedback"
```

Link commits to review comments:
```bash
git commit -m "test: add edge case for empty input

Addresses reviewer concern about boundary conditions.
See: https://github.com/org/repo/pull/123#discussion_r1234567"
```

### 5. Respond to review comments

> [!IMPORTANT]
> **Always include `@codex` in every PR comment** to ensure proper notification and tracking. This is required for all PR responses.

**Add general PR comment**:

```bash
# Simple response
gh pr comment 123 --body "Thanks for the review! Addressed all feedback in commits abc123 and def456. @codex"

# From file (ensure response.md includes @codex)
gh pr comment 123 --body-file response.md
```

**Reply to inline comments** (requires web or API):

```bash
# No direct CLI support for threaded replies
# Options:
# 1. Use web interface (gh pr view 123 --web)
# 2. Quote in new comment (include @codex):
gh pr comment 123 --body "> Original comment text

✅ Done in commit abc123. Extracted the validation logic as suggested. @codex"

# 3. Use API for review responses (include @codex)
gh pr review 123 --comment --body "Addressed all inline feedback. See commits abc123 and def456. @codex"
```

**Response templates**:

For implemented changes:

```markdown
✅ Done in commit abc123. Extracted the validation logic into a separate method as suggested. @codex
```

For clarifications:

```markdown
Good point about the performance impact. I benchmarked this change:
- Before: 1.2s for 10k items
- After: 1.1s for 10k items
The caching actually improves performance slightly. @codex
```

For respectful disagreement:

```markdown
I considered this approach but went with the current implementation because:
1. It maintains consistency with existing patterns in `core/validation/`
2. The simpler approach would require migrating 15 other modules

Happy to revisit if you feel strongly about this. @codex
```

### 6. Update PR after changes

```bash
# Push all fixes
git push

# Update PR description if scope changed
gh pr edit 123 --body "$(cat <<'EOF'
## Summary
[Original summary]

## Updates from review
- Added validation for empty inputs
- Improved error messages
- Added performance benchmarks
EOF
)"

# Request re-review from specific reviewers
gh pr edit 123 --add-reviewer username1,username2

# Post completion comment with @codex (REQUIRED)
gh pr comment 123 --body "All requested changes have been implemented and CI checks are passing. Ready for re-review. @codex"
```

### 7. Verify all checks pass

```bash
# Run full validation locally
make full

# Monitor CI
gh pr checks 123 --watch

# Ensure all threads resolved
gh pr view 123 --json reviewDecision
```

## Response patterns

### For performance concerns

```bash
# Add benchmark
make performance FOCUS=specific_test

# Document in PR (include @codex)
"Benchmarked the change: no regression detected. See `performance_report.md` @codex"
```

### For architectural questions

```bash
# Create ADR if needed
$EDITOR docs/adr/ADR-XXX-design-decision.md

# Link in response (include @codex)
"Created ADR-058 documenting this design choice: [link] @codex"
```

### For test coverage gaps

```bash
# Add specific test
$EDITOR tests/test_behavioral.py

# Commit with context
git commit -m "test: add behavioral test for error path

Covers the uncaught exception case raised in review"
```

## Professional communication

### Do

- Thank reviewers for thorough feedback
- Acknowledge valid concerns
- Provide data/benchmarks for claims
- Link to relevant code/docs
- Mark resolved conversations

### Don't

- Dismiss feedback defensively
- Implement without understanding why
- Leave questions unanswered
- Force push unless requested
- Merge with unresolved threads

## Quality gates

- [ ] All CI checks passing
- [ ] Review comments addressed or responded to
- [ ] No unresolved conversation threads
- [ ] Re-review requested from blockers
- [ ] PR description updated if needed
- [ ] Commits remain atomic and well-formed

## Expected outcomes

- All feedback addressed professionally
- CI status green
- Reviewers satisfied or concerns documented
- PR ready for final approval
- Clear audit trail of changes
- Final comment posted @mentioning codex to notify of completion
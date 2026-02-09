Create properly formatted GitHub issues from user requests with complete metadata.

**Optional skill integration**: This command can leverage the following skills when available:
- `gh-project-manage`: Set Value/Effort custom fields on created issues
- `gh-issue-dependencies`: Establish blocking/blocked-by relationships
- `gh-issue-hierarchy`: Create parent-child issue structures and sub-issues

Check for skill availability and use them to enhance metadata management. Gracefully degrade if skills are not available.

---

## Purpose

Create GitHub issues from user conversation requests, using project templates and ensuring metadata hygiene.

## Prerequisites

- `gh` CLI authenticated
- 1Password CLI `op` for secrets access (if needed)
- Repository write access

## Process

### 1. Parse user request

Analyze the user's conversational request to extract:
- Core problem or need
- User impact or motivation
- Success criteria (if provided)
- Technical constraints
- Any relevant context from the conversation

### 2. Determine issue type

**Feature request** if user describes:
- New capability needed
- User-facing enhancement
- System improvement

**Bug report** if user describes:
- Broken functionality
- Unexpected behavior
- Data quality issue

### 3. Create GitHub issue

Use appropriate template:

```bash
# Feature request
gh issue create \
  --template feature.md \
  --title "Problem statement from user request" \
  --assignee @me

# Bug report
gh issue create \
  --template bug.md \
  --title "Broken behavior description" \
  --assignee @me
```

**Title guidelines** (plain English, problem-oriented):

✅ Good issue titles:
- "Can't export user data to CSV"
- "Japanese game titles cause validation errors"
- "Pipeline performance degrades with 10k+ entries"
- "Crash when saving profile with empty username"

❌ Avoid:
- "fix: handle null input" (conventional commit format)
- "Add Unicode normalization" (solution-oriented)
- "Update QID system" (too vague)
- "Issue #123" (not descriptive)

### 4. Set labels

```bash
# Get issue number from creation output
ISSUE_NUM="123"

# Apply labels based on user request context
# First, query available repository labels
AVAILABLE_LABELS=$(gh label list --repo $(gh repo view --json nameWithOwner -q .nameWithOwner) --json name --jq '.[].name')

# Determine appropriate labels from issue type and context
# Map user request to available labels:
# - bug/security/performance: Critical issues requiring attention
# - testing/refactor/ci: Code quality and infrastructure
# - config/docs: Routine maintenance
# - dependencies: Dependency updates
# Use multiple labels if appropriate (e.g., "bug,security")

# Example: For feature request
gh issue edit $ISSUE_NUM --add-label "enhancement"

# Example: For bug with security implications
# gh issue edit $ISSUE_NUM --add-label "bug,security"
```

**Label selection guidance:**
1. Query available labels first to see what exists in this repository
2. Choose labels that describe the issue's **nature** (bug/enhancement) and **area** (security/performance/docs)
3. Apply multiple labels if the issue spans categories
4. If needed labels don't exist, note this for repository maintainers
5. Follow semantic color standards (see `core/rules/label-color-standards.md` for color guidance)

**Required metadata**:
- **Value**: Essential/Useful/Nice-to-have (business impact)
  - *Similar to "Must fix/Should fix/Nice to have" prioritization used in reviews*
- **Effort**: Heavy/Moderate/Light (implementation scope)
- **Status**: Set to `Backlog`

**Project assignment**: Issues are automatically added to the appropriate GitHub project board via repository workflows.

### 5. Set metadata and dependencies (if skills available)

**Use agent skills when available** for enhanced metadata and dependency management:

**Setting custom fields (Value/Effort)**:
- If `gh-project-manage` skill is available, use it to set Value and Effort custom fields:
  ```bash
  # Invoke skill to set metadata
  # The skill will handle project association and field updates
  ```
- Value options: Essential, Useful, Nice-to-have
- Effort options: Light, Moderate, Heavy

**Setting issue dependencies**:
- If `gh-issue-dependencies` skill is available, use it to establish blocking relationships:
  ```bash
  # Invoke skill to set dependencies
  # Example: This issue blocks another, or is blocked by prerequisites
  ```
- Identify dependencies from user context (e.g., "we need X before we can do Y")
- Prevent circular dependencies

**Setting issue hierarchy**:
- If `gh-issue-hierarchy` skill is available, use it for parent-child relationships:
  ```bash
  # Invoke skill to create sub-issues or link to parent epics
  ```

**Fallback**: If skills are not available, note metadata requirements for manual assignment.

### 6. Template completion

**Feature template sections**:

```markdown
## Summary
One-line overview of the capability needed.

## The problem
Why this matters to users or contributors. Focus on pain points.

## Proposed solution
How we'll solve it (keep distinct from the problem).

## Acceptance criteria (testable)
- [ ] GIVEN <context> WHEN <action> THEN <outcome>
- [ ] GIVEN valid data WHEN pipeline runs THEN exports CSV
- [ ] Documentation updated

## Testing strategy (test-first)
- **Unit tests**: Component validation logic
- **E2E tests**: Full export workflow
- **Edge cases**: Empty data, special characters, large files
```

**Bug template sections**:

```markdown
## The problem
What's broken and why it matters.

## Expected behavior
What should happen instead.

## Actual behavior
What actually happens (include error messages, logs).

## Acceptance criteria (testable)
- [ ] GIVEN <broken state> WHEN <trigger> THEN <fixed behavior>
- [ ] No regression in existing functionality
- [ ] Error handling improved

## Testing strategy (test-first)
- **Regression tests**: Ensure fix doesn't break other cases
- **Unit tests**: Isolate and verify the fix
- **Edge cases**: Boundary conditions around the bug
```

Ensure all criteria are:
- Specific and measurable
- Focused on observable behavior
- Testable by someone other than implementer
- Written in GIVEN-WHEN-THEN format

### 7. Confirm with user

After creating the issue:
- Provide the issue URL to the user
- Summarize the issue title and key metadata
- Confirm all required fields were populated
- Ask if any adjustments are needed

## Quality gates

- [ ] Issue follows template structure completely
- [ ] Title describes problem, not solution
- [ ] All applicable labels added
- [ ] Value/Effort custom fields set (if `gh-project-manage` skill available)
- [ ] Dependencies established (if `gh-issue-dependencies` skill available and dependencies identified)
- [ ] Hierarchy relationships set (if `gh-issue-hierarchy` skill available and parent/child structure needed)
- [ ] Acceptance criteria are testable
- [ ] Testing strategy specified
- [ ] User confirmed issue is accurate

## Expected outcomes

- GitHub issue ready for implementation
- Clear acceptance criteria for validation
- Appropriate labels applied
- Value/Effort metadata set (when skills available)
- Dependencies and hierarchy established (when applicable and skills available)
- User has issue URL and can track progress
- Issue will be automatically added to project board via repository workflows

## Request examples

**User says**: "We need to handle games with Japanese titles better"

**Issue created**:
- Title: "Japanese game titles cause validation errors"
- Problem: QID resolution fails for kanji/hiragana/katakana
- Acceptance criteria: Japanese titles resolve correctly
- Testing: Add test cases with actual Japanese games

**User says**: "The pipeline is too slow for large datasets"

**Issue created**:
- Title: "Pipeline performance degrades with 10k+ entries"
- Problem: Processing time grows exponentially
- Acceptance criteria: Linear scaling up to 50k entries
- Testing: Performance benchmarks at various scales
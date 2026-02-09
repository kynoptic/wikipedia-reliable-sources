---
area: docs
subarea: as
goal: code
platforms:
  - windsurf
  - claude
status: active
requires: []
---

# Documentation as code guidelines

## Purpose

Establish a systematic approach to documentation that treats it as an integral part of the development workflow, not an afterthought.

## Core philosophy

**Documentation follows the same lifecycle as code**: planned, written, reviewed, tested, versioned, and maintained.

## Writing style by artifact type

Different development artifacts serve different purposes and audiences, requiring distinct writing styles:

### Issues

- **Style**: Descriptive, problem-oriented, plain English
- **Purpose**: Explain *what's wrong* (bugs) or *what's desired* (features)
- **Audience**: Team members triaging, prioritizing, or discussing work
- **Example**: "Crash when saving profile with empty username"

### Pull requests

- **Style**: Solution-oriented, concise summary of change
- **Purpose**: Explain *what this set of commits accomplishes*
- **Audience**: Reviewers, maintainers, release notes readers
- **Example**: "Add input validation for empty usernames"

### Commits

- **Style**: Imperative, action-oriented, granular
- **Purpose**: Capture *what changed* in the codebase at a specific point
- **Audience**: Developers reading `git log` or debugging history
- **Example**: "fix: reject empty usernames when saving profile"

> [!TIP]
> When linked together (issue ↔ PR ↔ commits), these create a clean story: *Issue* describes the problem, *PR* describes the solution, *commits* describe the implementation steps.

## Documentation lifecycle

### 1. Backlog → (Optional Story) → Issue → Implementation → (ADR when needed) → Milestone

Default flow:

```
Backlog Item
    ↓
Issue (technical task)
    ↓
Implementation (code + docs)
    ↓
Milestone (released)
```

Optional branches:
- **Story (user need)**: Use when delivering a user-facing feature that benefits from a durable narrative. Skip for internal maintenance or bug fixes.
- **ADR (decision record)**: Add only when the change involves meaningful tradeoffs or architectural impact that must be documented for future reference.

### 2. Documentation types by lifecycle stage

**Backlog stage:**
- User stories with acceptance criteria
- Problem statements
- High-level requirements

**Story stage (optional):**
- Detailed user scenarios
- Success criteria
- Out-of-scope items

**Issue stage:**
- Technical specifications
- Implementation plan
- Dependencies and blockers

**Implementation stage:**
- Code comments and docstrings
- API documentation
- User-facing documentation updates

**ADR stage (when warranted):**
- Architecture Decision Records
- Design rationale
- Alternative considerations

**Milestone stage:**
- Release notes
- Change logs
- Migration guides

## Structured metadata requirements

### All documentation MUST include

```yaml
---
title: "Document Title"
type: [tutorial|how-to|reference|explanation]  # Diátaxis classification
area: [getting-started|tasks|configuration|api|concepts|troubleshooting|releases]  # MECE classification
audience: [developer|user|admin|architect]
status: [draft|review|active|deprecated]
last_updated: YYYY-MM-DD
related_issues: [123, 456]
related_adrs: [adr-001, adr-002]
---
```

### GitHub Markdown Alerts integration

- Use NOTE, TIP, IMPORTANT, WARNING, CAUTION with exact syntax: `> [!TYPE]` with proper capitalization
- Align alert types with Diátaxis types and MECE areas appropriately
- Limit to 1-2 alerts per document section for maximum impact
- Follow alert hierarchy: WARNING > IMPORTANT > CAUTION > NOTE > TIP
- Position alerts before the content they reference for logical flow

### Issue metadata alignment

```yaml
# Issues must include:

# Repository Labels (repository-scoped):
labels:
  - type: [bug|feature|chore|docs]
  - area: [frontend|backend|api|docs|infra]

# Project Custom Fields (project-scoped):
project_fields:
  - value: [essential|useful|nice-to-have]
  - effort: [heavy|moderate|light]
  - status: "Backlog"  # Always set to Backlog for new issues

project: "Product Development"
assignees: ["developer", "reviewer"]

# Dependencies (when applicable):
blocked_by: [123, 456]  # Issues that must complete first
blocking: [789]         # Issues that depend on this one
```

### PR metadata inheritance

PRs automatically inherit from linked issues:
- Repository labels (type, area) from the issue
- Project board placement
- Project custom field values (Value/Effort)

### CLI Usage for Labels vs Custom Fields

**Repository Labels (simple CLI commands):**
```bash
# Add/remove labels to issues or PRs
gh issue edit 123 --add-label "type:bug,area:frontend"
gh pr edit 456 --remove-label "type:feature"

# Copy labels from issue to PR
LABELS=$(gh issue view 123 --json labels -q '.labels[].name' | tr '\n' ',' | sed 's/,$//')
gh pr edit 456 --add-label "$LABELS"

# List all repository labels
gh label list --repo owner/repo
```

**Project Custom Fields (GraphQL required):**
```bash
# Update custom field value (requires project/item/field IDs)
gh api graphql -f query='mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_kwDOABCDEF"
    itemId: "PVTI_lADOABCDEFABCD"
    fieldId: "PVTF_lADOABCDEFABCD"
    value: {singleSelectOptionId: "abc123"}
  }) { projectV2Item { id } }
}'

# Get project structure to find IDs
gh api graphql -f query='query($project: ID!) {
  node(id: $project) {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField {
            id name options { id name }
          }
        }
      }
    }
  }
}' -F project="PVT_kwDOABCDEF"
```

## Repository structure

### Documentation organization

```
docs/
├── adr/                    # Architecture Decision Records
│   ├── adr-001-database-choice.md
│   └── adr-002-auth-strategy.md
├── api/                    # API reference documentation
├── concepts/               # Conceptual explanations
├── getting-started/        # Onboarding tutorials
├── how-to/                # Task-oriented guides
├── releases/              # Release notes and changelogs
├── troubleshooting/       # Problem-solving guides
└── README.md              # Navigation hub
```

### Issue templates

```markdown
<!-- .github/ISSUE_TEMPLATE/feature.md -->
---
name: Feature Request
about: Propose a new feature
title: "[FEATURE] "
labels: ["type:feature", "status:triage"]
---

## User Story
As a [type of user], I want [goal] so that [benefit].

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Documentation updated
- [ ] Tests added

## Value/Effort
- **Value**: [Essential|Useful|Nice-to-have] - [justification]
- **Effort**: [Heavy|Moderate|Light] - [estimation reasoning]

## Definition of Done
- [ ] Feature implemented
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] ADR created (if architectural)
```

## GitHub Project hygiene

### Project boards configuration

```yaml
# .github/project.yml
name: "Product Development"
fields:
  - name: "Status"
    type: "select"
    options: ["Backlog", "Todo", "Doing", "Done"]

  - name: "Value"
    type: "select"
    options: ["Essential", "Useful", "Nice-to-have"]

  - name: "Effort"
    type: "select"
    options: ["Heavy", "Moderate", "Light"]

views:
  - name: "Sprint Board"
    layout: "board"
    field: "Status"
    filter: "status:Todo,Doing"

  - name: "Backlog"
    layout: "table"
    sort: ["value:desc", "effort:asc"]
```

### Milestone management

```bash
# Create milestone with clear scope
gh api repos/:owner/:repo/milestones \
  --field title="v1.2.0" \
  --field description="User authentication and profile management" \
  --field due_on="2024-03-15T00:00:00Z"

# Link issues to milestone
gh issue edit 123 --milestone "v1.2.0"
```

## ADR (Architecture Decision Record) standards

### ADR template

```markdown
# ADR-001: Database Choice for User Management

## Status
Accepted

## Context
We need to choose a database for the user management system. We have 10,000+ expected users, need ACID transactions, and require complex queries for reporting.

> [!IMPORTANT]
> This decision affects the entire user management architecture and data persistence strategy.

## Decision
We will use PostgreSQL as our primary database.

## Alternatives Considered
1. **MongoDB**: Good for document storage but weak consistency guarantees
2. **MySQL**: Familiar but limited JSON support for user preferences
3. **SQLite**: Too limited for production scale

## Consequences

### Positive
- Strong consistency and ACID compliance
- Excellent JSON support for user preferences
- Rich ecosystem and tooling
- Team familiarity

### Negative
- Higher operational complexity than SQLite
- Requires PostgreSQL expertise for optimization
- Additional infrastructure dependency

> [!CAUTION]
> Migration from PostgreSQL to another database system would be complex and time-consuming due to PostgreSQL-specific features we plan to use.

## Implementation Plan
- [ ] Set up PostgreSQL instance
- [ ] Create migration scripts
- [ ] Update connection configuration
- [ ] Document backup procedures

> [!TIP]
> Consider using connection pooling from the start to optimize performance under load.

## Related Issues
- Issue #123: User registration system
- Issue #124: User profile management

## Date
2024-01-15
```

### ADR naming convention

```
adr-{number}-{short-title}.md

Examples:
- adr-001-database-choice.md
- adr-002-authentication-strategy.md
- adr-003-frontend-framework.md
```

## Automation and tooling

### Documentation validation

```yaml
# .github/workflows/docs.yml
name: Documentation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate documentation metadata
        run: python scripts/validate_docs.py
      - name: Check ADR numbering
        run: python scripts/check_adr_sequence.py
      - name: Lint markdown
        uses: DavidAnson/markdownlint-cli2-action@v9
```

### Automatic linking

```python
# scripts/link_docs_to_issues.py
def update_issue_links():
    """Automatically update documentation with issue references"""
    for doc in glob.glob("docs/**/*.md"):
        if "related_issues" in frontmatter:
            for issue_num in frontmatter["related_issues"]:
                add_backlink_to_issue(issue_num, doc)
```

### Milestone documentation generation

```bash
# Generate release notes from milestone
gh api repos/:owner/:repo/milestones/1/issues | \
  jq -r '.[] | "- \(.title) (#\(.number))"' > release_notes.md
```

## Quality gates

### Documentation checklist for PRs

- [ ] All new features documented
- [ ] API changes reflected in docs
- [ ] ADR created for architectural decisions
- [ ] Related issues linked
- [ ] Milestone assigned
- [ ] Metadata complete and accurate

### Issue hygiene checklist

- [ ] Clear user story or problem statement
- [ ] Acceptance criteria defined
- [ ] Value/Effort assessed
- [ ] Dependencies identified (blocked by/blocking)
- [ ] No circular dependencies exist
- [ ] Appropriate labels applied
- [ ] Project board placement
- [ ] Status set to "Backlog" or "Blocked" if dependencies exist

### Milestone closure checklist

- [ ] All issues closed or moved to next milestone
- [ ] Release notes generated
- [ ] ADRs updated with implementation outcomes
- [ ] Documentation reflects released state
- [ ] Changelog updated

## Metrics and reporting

### Documentation health metrics

```bash
# Check documentation coverage
python scripts/doc_coverage.py
# Output:
# - % of features with documentation
# - % of APIs with examples
# - % of ADRs with implementation status

# Check metadata compliance
python scripts/metadata_audit.py
# Output:
# - % of docs with complete metadata
# - % of issues with proper labels
# - % of PRs with linked issues
```

### Planning effectiveness metrics

```bash
# Measure planning accuracy
python scripts/planning_metrics.py
# Output:
# - Effort estimation accuracy
# - Milestone scope creep
# - Issue completion rate by complexity
```

## Anti-patterns to avoid

### Documentation anti-patterns

- Writing docs after the feature is complete
- Documenting implementation details instead of user behavior
- Creating docs without linking to related issues
- Letting docs drift out of sync with code

### Planning anti-patterns

- Creating issues without user stories
- Missing Value/Effort assessments
- Working on issues not in current milestone
- Closing milestones with unfinished work

### Project hygiene anti-patterns

- PRs without linked issues
- Issues without proper labels
- Milestones without clear scope
- Decisions made without ADRs

## Benefits

1. **Traceability**: Every change links back to user need
2. **Quality**: Documentation reviewed like code
3. **Consistency**: Standardized metadata across all artifacts
4. **Automation**: Tools enforce standards and generate reports
5. **Knowledge retention**: Decisions and rationale preserved
6. **Planning accuracy**: Historical data improves estimation
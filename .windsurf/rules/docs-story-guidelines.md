---
trigger: glob
description: "User stories are the single source of truth for new features and significant changes, capturing why we're doing something, what the outcome should be, and how we'll prove it works."
globs: "docs/stories/US-*.md"
---
# User story structure and requirements

## Purpose

User stories are the **single source of truth** for new features and significant changes in the project. They capture **why we're doing something, what the outcome should be, and how we'll prove it works**.

**When a user story is required**: Any work that adds functionality, changes behavior, or affects user experience must map to a story. If there's no story, there's no feature code.

**When a user story is NOT required**: Documentation updates, typo fixes, minor refactoring, and other non-functional changes can be committed directly without a story.

## Core principles

### 1. One story, one outcome

Keep each story atomic. It should describe a single capability from the user's perspective.

### 2. Follow the template exactly

Use the standard template structure. Fill in each section. No free-form notes.

### 3. Budgets must be explicit

Always restate the current performance, accessibility, and SEO budgets. If you need to raise a budget (e.g., allow a small amount of JS), note the change and justify it.

### 4. Accessibility and SEO are non-negotiable

Every story must include accessibility and SEO requirements. Even if nothing changes, copy them in to reaffirm compliance.

### 5. Acceptance criteria = checklist

Write them as concrete, testable boxes. We should be able to go down the list and tick ✅ / ❌.

### 6. Micro-spec stays minimal

Describe only what you're changing: structure, data, copy, rollback. Do not over-specify or include future ideas.

### 7. Decision log links to ADRs

For significant architectural decisions, create a standalone ADR in `docs/adr/` and link to it. For minor decisions, document directly in this section. If no decisions required, leave "(none)".

### 8. Outcomes must be updated after merge

Add PR link, commit hash, budget measurements, and any notes. This closes the loop.

## Required sections

### Story statement

Use the format: **As a `<user>`, I want `<capability>` so that `<outcome>`.**

- `<user>`: Who benefits (end user, developer, maintainer)
- `<capability>`: What they can do
- `<outcome>`: Why it matters

### Acceptance criteria

Concrete, testable checkboxes that define when the story is complete.

```markdown
- [ ] Criterion 1 with specific, measurable result
- [ ] Criterion 2 with observable behavior
- [ ] Criterion 3 with validation method
```

### Budgets

Performance constraints that must be maintained or explicitly raised:

- Transfer: Total bytes over network
- Client JS: JavaScript bundle size (prefer 0 KB)
- HTML: Markup size
- CSS: Stylesheet size
- Data: JSON/API payload size
- LCP: Largest Contentful Paint (mobile)
- CLS: Cumulative Layout Shift

### Accessibility (AA)

WCAG 2.1 Level AA compliance requirements:

- Landmarks present (`header`, `main`, `footer`)
- One `h1`, logical heading hierarchy
- Visible focus indicators, no keyboard traps
- Color contrast ≥ 4.5:1
- Screen reader text where needed (aria-label, sr-only)

### SEO

Search engine optimization requirements:

- Unique `<title>` and `<meta name="description">` per page
- Canonical URL correct
- Structured data valid (JSON-LD: `ItemList`, `VideoGame`, etc.)

### Micro-spec (scope)

Minimal specification of changes:

- **UI**: Structure, components, or markup changes
- **Data**: Source, shape, or transformation logic
- **Copy**: Titles, labels, alt text, or microcopy
- **Rollback**: Steps to revert in one commit if needed

### Tasks

Ordered checklist of implementation steps. Keep granular and actionable.

### Decision log

Significant technical decisions with links to ADRs or inline documentation:

```markdown
### `YYYY-MM-DD` — Decision Topic

- **Decision**: One-sentence summary
- **Justification**: See **[ADR-XXX: Title](../adr/adr-XXX-title.md)** for full details

### `YYYY-MM-DD` — Minor Decision (direct documentation)

- **Choice**: Short rationale
- **Impact**: +positive / –negative
- **Rollback**: How to undo

(Use "(none)" if no decisions required)
```

### Outcomes

Post-merge section documenting results:

- PR: Link to merged pull request
- Commit: SHA of merge commit
- Budgets: Actual measurements from build + screenshots
- Lighthouse: Scores for performance, accessibility, SEO
- Notes: Lessons learned or issues encountered

## File naming

Stories use the pattern: `US-<id>-<slug>.md`

- `<id>`: Sequential number (001, 002, etc.)
- `<slug>`: Short kebab-case description

**Examples**:
- `US-001-ranked-list.md`
- `US-002-game-detail-page.md`
- `US-003-search-filter.md`

## Workflow integration

1. **Create story first**: Document the feature in `docs/stories/`
2. **Branch from story**: Use `issue-<id>-<slug>` or similar naming
3. **Open PR**: Reference the story in PR description
4. **Validate completion**: Ensure all acceptance criteria met
5. **Update outcomes**: Add PR link, metrics, and notes
6. **Merge**: Only when all boxes are checked

For non-story work (docs, typos, refactoring), commit directly to main using conventional commit format.

## Quality gates

Stories cannot be closed until:

- ✅ All acceptance criteria checked
- ✅ Budgets measured and documented
- ✅ Accessibility tested and validated
- ✅ SEO requirements verified
- ✅ Outcomes section updated with results

## Examples

See `docs/stories/US-001-ranked-list.md` for a concrete example of a properly filled-in story for the MVP ranked list feature.

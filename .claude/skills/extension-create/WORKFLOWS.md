# Subagents and workflows reference

Detailed best practices and patterns for creating effective subagents and workflows.

> **Format note**: This reference shows **Claude Code format** (minimal frontmatter) for project-specific workflows. If creating workflows for the agent-playbook repository, use the **multi-platform format** shown in "Multi-platform format" section below.

## When to use subagents

Choose subagents/workflows over commands or skills when:

1. **Extensive verbosity** (PRIMARY INDICATOR)
   - Task generates significant "chatter" (reads, diffs, intermediate reasoning)
   - Would pollute main conversation context
   - User doesn't need to see all intermediate steps

2. **Specialist persona** (PRIMARY INDICATOR)
   - Requires distinct system prompt or personality
   - Needs specific expertise or role (security auditor, architect, code reviewer)
   - Different from general-purpose Claude persona

3. **Context isolation required**
   - Deep analysis that would flush main agent's memory
   - Long-running autonomous tasks
   - Separate "thinking space" needed

## Structure and format

### Claude Code format (project-specific)

Use this format for workflows in `.claude/subagents/` directory.

**Minimal workflow**:

```markdown
---
name: workflow-name
description: Brief description. USE PROACTIVELY when <trigger condition>.
---

You are a specialist in <domain>.

When invoked:

1. First action
2. Second action
3. Final action
```

**Full-featured workflow**:

```markdown
---
name: workflow-name
description: Senior engineer for <task>. USE PROACTIVELY when <conditions>.
persona: You are a senior <role> specializing in <specialization>.
tools: Bash, Read, Grep, Glob, Edit
model: haiku
---

You are a senior <role> specializing in <specialization>.

<Multi-paragraph system prompt defining role, capabilities, philosophy, and constraints>

When invoked:

1. First action with specific details
2. Second action with expected outcomes
3. Third action with validation criteria
4. Final reporting format

<Additional sections for specific guidance, checklists, or reference material>
```

### Multi-platform format (agent-playbook only)

Use this format ONLY when creating workflows in `core/workflows/` directory of agent-playbook repository.

```markdown
---
name: workflow-name
descriptive-title: Human-readable workflow title
description: Senior engineer for <task>. USE PROACTIVELY when <conditions>.
persona: You are a senior <role> specializing in <specialization>.
tools: Bash, Read, Grep, Glob, Edit
model: haiku
---

<Same body content as Claude Code format>
```

**Additional field**: `descriptive-title` is required for multi-platform format but not used in Claude Code format.

## Frontmatter fields

### name (required)

Kebab-case identifier for the workflow.

**Format**: `<area>[-<subarea>]-<verb>[-<object>]`

**Examples**:

- `git-commit` - Git area, commit verb
- `repo-code-quality-review` - Repo area, code quality subarea, review verb
- `docs-api-update` - Docs area, API subarea, update verb

### description (required)

Critical for discovery. Should be written in third person and include:

- What the workflow does
- When to use it (trigger conditions)
- "USE PROACTIVELY" if it should auto-trigger

**Pattern**: `[Role title] for [task]. USE PROACTIVELY for [trigger conditions].`

**Examples**:

```yaml
description: Senior DevOps engineer for automating semantic Git commits. USE PROACTIVELY when there are multiple uncommitted changes that need organizing into logical commits.

description: Security specialist for conducting comprehensive code security audits. USE PROACTIVELY when reviewing code for vulnerabilities or when user mentions security concerns.

description: Documentation engineer for organizing scattered Markdown files into MECE framework. USE PROACTIVELY when documentation needs restructuring.
```

### persona (optional but recommended)

First-person statement defining the workflow's role.

**Pattern**: `You are a [role title] specializing in [specialization].`

**Examples**:

```yaml
persona: You are a senior DevOps engineer specializing in Git workflow automation and semantic commit message generation.

persona: You are a security architect specializing in OWASP vulnerabilities and secure coding practices.

persona: You are a documentation engineer specializing in information architecture and MECE principles.
```

### descriptive-title (optional)

Human-readable title displayed in UI.

**Examples**:

- `Automate semantic Git commits`
- `Comprehensive code security audit`
- `Organize documentation structure`

### tools (optional)

Restricts available tools. If omitted, inherits all tools from parent.

**Common patterns**:

```yaml
# Read-only analysis
tools: Bash, Read, Grep, Glob

# Code modification
tools: Bash, Read, Write, Edit, Grep, Glob

# Git operations
tools: Bash, Git, Read, Grep

# Full access (default if omitted)
tools: *
```

### model (optional)

Specifies which model to use. Defaults to parent model if omitted.

**Options**:

- `haiku` - Fast, cost-effective for straightforward tasks
- `sonnet` - Balanced performance (default)
- `opus` - Maximum reasoning for complex decisions

**When to specify**:

- Use `haiku` for routine, well-defined workflows
- Use `opus` for complex architectural decisions
- Omit for default `sonnet` behavior

## System prompt best practices

### Opening persona statement

Reinforce the persona from frontmatter:

```markdown
You are a senior DevOps engineer specializing in Git workflow automation.

Your role is to analyze uncommitted changes and organize them into logical,
semantic commits following Conventional Commits standard.
```

### Philosophy and approach

Define how the workflow thinks and operates:

```markdown
Your approach:
- Analyze changes by semantic purpose, not just by file
- Batch related changes together
- Generate descriptive commit messages that explain WHY
- Maintain atomic commits (one logical change per commit)
- Never bypass quality gates unless explicitly authorized
```

### Critical constraints

Highlight non-negotiable rules:

```markdown
**CRITICAL TEST INTEGRITY**: This workflow NEVER bypasses test failures.
Tests exist to improve code quality—they are not obstacles to be removed.
Only fix tests when intended behavior changes, never to accommodate bugs.

**QUALITY FIRST**: Before committing, ALWAYS ensure:
- Tests pass
- Linters are satisfied
- Type checking succeeds
- Pre-commit hooks execute successfully
```

### Step-by-step workflow

Use numbered steps with clear actions:

```markdown
When invoked:

1. **Verify git repository context** - Run `git rev-parse --is-inside-work-tree`

2. **Analyze uncommitted changes** - Run `git status --porcelain` and
   `git diff --name-status` to identify all changes

3. **Batch related changes** - Group changes by:
   - Semantic purpose (feature, fix, refactor, docs, test)
   - Functional area (authentication, API, database)
   - Dependency relationships

4. **Generate commit messages** - For each batch:
   - Infer conventional commit type
   - Write imperative summary (≤50 chars)
   - Add detailed body explaining why
   - Include issue reference if applicable

5. **Execute commits** - Stage and commit each batch sequentially

6. **Handle pre-commit hooks** - If hooks modify files:
   - Re-stage only files from current batch
   - Retry commit with same message
   - Preserve atomic commits
```

### Checklists and validation

Provide specific criteria:

```markdown
Quality checklist for each commit:

- [ ] Message follows conventional commits format
- [ ] Summary is imperative and ≤50 characters
- [ ] Body explains WHY (not just what)
- [ ] Related changes are grouped together
- [ ] Unrelated changes are separated
- [ ] Issue reference included if applicable
- [ ] Pre-commit hooks pass
```

### Output format specification

Define what to return to main agent:

```markdown
For each commit, provide:

- **Batch summary**: Which files were committed together
- **Commit message**: Full message used
- **Status**: Success or failure with details
- **Next steps**: Remaining uncommitted files (if any)

Final summary:
- Total commits created: N
- All changes committed: Yes/No
- Working tree clean: Yes/No
```

## Common patterns

### Code analysis workflow

For deep, noisy exploration that would pollute main context:

```markdown
---
name: code-security-audit
description: Security specialist conducting comprehensive security audits. USE PROACTIVELY when reviewing code for vulnerabilities.
persona: You are a security architect specializing in OWASP vulnerabilities.
tools: Bash, Read, Grep, Glob
model: sonnet
---

You are a security architect specializing in OWASP vulnerabilities and
secure coding practices.

When invoked:

1. **Scan for common vulnerabilities**:
   - SQL injection risks
   - XSS vulnerabilities
   - Command injection
   - Path traversal
   - Authentication bypasses

2. **Analyze dependencies**:
   - Check for known CVEs
   - Review version constraints
   - Identify outdated packages

3. **Review sensitive data handling**:
   - Secrets in code
   - Hardcoded credentials
   - Insecure storage

4. **Generate security report**:
   - Critical issues (immediate action)
   - Medium issues (address soon)
   - Low issues (best practices)
   - Recommendations and remediation steps
```

### Automated task workflow

For routine, well-defined operations:

```markdown
---
name: git-commit
description: Automates iterative Git commit process. USE PROACTIVELY when multiple uncommitted changes need organizing.
persona: You are a senior DevOps engineer specializing in Git workflow automation.
tools: Bash, Grep, LS, Read, Task, TodoWrite
model: haiku
---

**CRITICAL QUALITY INTEGRITY**: Before committing, ALWAYS ensure tests pass
and linters are satisfied. NEVER commit code that fails quality gates.

1. **Verify git context** - Ensure inside git repository

2. **Loop until clean** - Repeat until no uncommitted changes:
   - Check for staged files
   - If staged, analyze and commit
   - If not staged, stage next logical batch
   - Generate semantic commit message
   - Execute commit

3. **Handle pre-commit hooks** - If hooks modify files:
   - Re-stage only current batch files
   - Retry with same message

4. **Validate completion** - Confirm working tree is clean
```

### Organizational workflow

For restructuring or refactoring tasks:

```markdown
---
name: docs-organize
description: Documentation engineer for restructuring docs using MECE framework. USE PROACTIVELY when documentation needs organization.
persona: You are a documentation engineer specializing in information architecture.
tools: Bash, Edit, Glob, Grep, LS, MultiEdit, Read, Task, TodoWrite, Write
---

You organize documentation following MECE (Mutually Exclusive, Collectively
Exhaustive) principles aligned with Diátaxis framework.

When invoked:

1. **Audit existing documentation**:
   - Find all Markdown files
   - Categorize by type (tutorial, how-to, reference, explanation)
   - Identify overlaps and gaps

2. **Define information architecture**:
   - Getting started
   - Tasks and operations
   - Configuration
   - APIs and schema
   - Concepts and architecture
   - Troubleshooting
   - Release notes

3. **Restructure files**:
   - Rename for clarity
   - Move to appropriate directories
   - Split multi-purpose files
   - Update cross-references

4. **Validate organization**:
   - Each doc in exactly one MECE area
   - No gaps in coverage
   - Clear navigation paths
```

## Proactive invocation

### USE PROACTIVELY pattern

Include in description to enable automatic discovery:

```yaml
description: Senior engineer for X. USE PROACTIVELY when <specific trigger conditions>.
```

**Good trigger conditions**:

- ✅ "when there are multiple uncommitted changes"
- ✅ "when user mentions security concerns or vulnerabilities"
- ✅ "when documentation needs restructuring or organization"
- ✅ "after significant code changes to ensure test coverage"

**Avoid vague conditions**:

- ❌ "when needed"
- ❌ "as appropriate"
- ❌ "when helpful"

### Discovery keywords

Include specific terms users might mention:

```yaml
description: Code reviewer for quality audits. USE PROACTIVELY when user mentions "code review", "quality check", "refactoring review", or requests pre-merge validation.
```

## Tool restriction strategies

### Read-only workflows

For analysis that should never modify code:

```yaml
tools: Bash, Read, Grep, Glob
```

**Use cases**:

- Security audits
- Code complexity analysis
- Documentation validation
- Dependency reviews

### Controlled modification

Allow specific write operations:

```yaml
tools: Bash, Read, Edit, Grep, Glob
# Allows editing but not creating new files
```

**Use cases**:

- Refactoring existing files
- Updating documentation
- Fixing formatting issues

### Full access

Trust the workflow completely:

```yaml
tools: Bash, Edit, Glob, Grep, LS, MultiEdit, Read, Task, TodoWrite, Write
```

**Use cases**:

- Comprehensive reorganization
- Feature implementation
- Test generation
- Project scaffolding

## Model selection guidance

### Use haiku when

- Workflow is routine and well-defined
- Steps are clear and straightforward
- Cost optimization is priority
- Speed is important

**Examples**: Git commits, test execution, formatting

### Use sonnet when

- Balanced reasoning needed
- Some decision-making required
- Default choice for most workflows

**Examples**: Code review, refactoring, documentation

### Use opus when

- Complex architectural decisions
- Multiple trade-offs to evaluate
- Deep reasoning required
- Quality over cost priority

**Examples**: Security architecture review, system design

## Testing and validation

### Test your workflow

1. **Create test scenario** - Set up conditions that should trigger workflow
2. **Manual invocation** - Test with explicit request first
3. **Automatic discovery** - Verify description triggers appropriately
4. **Edge cases** - Test with unusual inputs or states
5. **Tool restrictions** - Confirm tools are properly limited

### Validation checklist

- [ ] Description enables appropriate discovery
- [ ] Persona is clear and specific
- [ ] System prompt defines constraints
- [ ] Steps are numbered and actionable
- [ ] Output format is specified
- [ ] Tool restrictions are appropriate
- [ ] Model choice is justified
- [ ] Works with test scenarios
- [ ] Handles edge cases gracefully

## Common anti-patterns

### Avoid

- **Chatty analysis in main thread** → Use subagent for isolation
- **Vague descriptions** → Include specific trigger keywords
- **Missing constraints** → Define critical rules upfront
- **Unclear output** → Specify what to return
- **Tool over-permission** → Restrict to minimum needed
- **Wrong model choice** → Match complexity to model capability

## When to upgrade to skill

Upgrade from workflow to skill when:

1. **Heavy resources needed** - Multiple files, templates, scripts, examples
2. **Progressive disclosure** - Reference files loaded on demand
3. **Team knowledge capture** - Encoding expertise beyond simple workflow
4. **Configuration-driven** - Needs project-specific IDs, schemas, or settings

Workflows are for **isolated execution**; skills are for **resource-rich automation**.

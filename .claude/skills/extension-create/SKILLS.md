# Agent skills reference

Detailed best practices and patterns for creating effective agent skills.

> **Format note**: This reference shows **Claude Code format** (minimal frontmatter) for project-specific skills. If creating skills for the agent-playbook repository, use the **multi-platform format** shown in "Multi-platform format" section below.

## When to use skills

Choose skills over commands or workflows when:

1. **Heavy resource use** (PRIMARY INDICATOR)
   - Requires multiple files (templates, scripts, examples, reference docs)
   - Needs progressive disclosure (load details on demand)
   - Captures complex domain knowledge
   - Configuration-driven with project-specific data

2. **Team standardization**
   - Workflow should be consistent across team
   - Knowledge should be centralized and version-controlled
   - Shared expertise and best practices

3. **Automatic discovery**
   - Should trigger based on user intent without explicit command
   - Model should find skill contextually
   - Natural language requests should activate it

## Structure and format

### Directory layout

```
skill-name/
├── SKILL.md              # Main skill file (required)
├── REFERENCE.md          # Detailed reference (optional)
├── EXAMPLES.md           # Usage examples (optional)
├── scripts/              # Helper scripts (optional)
│   └── helper.sh
└── templates/            # Template files (optional)
    └── template.txt
```

### Claude Code format (project-specific)

Use this format for skills in `.claude/skills/` directory.

**Minimal SKILL.md**:

```markdown
---
name: skill-name
description: What it does and when to use it. Write in third person. Include trigger keywords.
---

# Skill title

Brief overview.

## What you should do

[Step-by-step instructions for Claude]
```

**Full-featured SKILL.md**:

```markdown
---
name: skill-name
description: Third-person description with specific trigger keywords. Use when <conditions>.
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob"]
---

# Skill title

Brief overview of what this skill does and why it's valuable.

## What you should do

When invoked, help the user by:

1. **Understanding the request** - Determine what's needed
2. **Gathering context** - Read relevant files
3. **Executing workflow** - Follow specific steps
4. **Validating results** - Confirm success

## Supporting files

Reference additional files Claude can access when needed:

- `REFERENCE.md` - Detailed reference documentation
- `EXAMPLES.md` - Usage examples and patterns
- `scripts/helper.sh` - Helper script for automation
- `templates/template.txt` - Template file for scaffolding

## [Additional sections as needed]

[Domain-specific content, patterns, examples, troubleshooting]
```

### Multi-platform format (agent-playbook only)

Use this format ONLY when creating skills in `core/skills/` directory of agent-playbook repository.

```markdown
---
name: skill-name
descriptive-title: Human-readable skill title
description: Third-person description with specific trigger keywords. Use when <conditions>.
status: stable
platforms: ["claude-code"]
allowed-tools: ["Read", "Write", "Bash", "Grep", "Glob"]
requires: ["gh CLI authenticated", "repository write access"]
tags: ["github", "automation", "setup"]
category: development
---

<Same body content as Claude Code format>
```

**Additional fields** for multi-platform format:
- `descriptive-title` - Human-readable title
- `status` - `stable`, `beta`, `experimental`, or `deprecated`
- `platforms` - Array of platforms: `["claude-code"]`, `["windsurf"]`, etc.
- `tags` - Array of keywords for categorization
- `category` - High-level category: `development`, `testing`, `documentation`, etc.

## Frontmatter fields

### name (required)

Kebab-case identifier using gerund form.

**Pattern**: `<area>[-<subarea>]-<verb-ing>[-<object>]`

**Good examples** (gerund form):

- `managing-github-projects` - "Managing X"
- `processing-excel-files` - "Processing Y"
- `creating-agent-skills` - "Creating Z"
- `running-tests` - "Running W"

**Avoid**:

- ❌ `github-projects` - Missing verb
- ❌ `excel-helper` - Vague, not gerund
- ❌ `test-runner` - Noun, not gerund
- ❌ `git-tools` - Too generic

### description (required)

Critical for automatic discovery. Must be third-person with specific triggers.

**Pattern**: `[Action verb] [object] [details]. Use when [trigger conditions].`

**Elements to include**:

1. **What it does** - Primary functionality
2. **When to use** - Trigger conditions
3. **Key capabilities** - Specific features
4. **Trigger keywords** - Terms users might mention

**Good examples**:

```yaml
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

description: Manages GitHub Projects V2 items and custom fields using GitHub CLI. Use when adding issues to projects, updating Status/Value/Effort fields, or performing bulk operations.

description: Executes language-agnostic test suites to validate behavioral correctness. Use to validate code changes proactively, or when the user mentions running tests, test failures, or test debugging.
```

**Avoid**:

```yaml
# Too vague
description: Helps with Excel files.

# First person
description: I can help you process PDF files.

# Missing triggers
description: Manages GitHub Projects.

# Too technical for discovery
description: Implements PDF processing via pypdf2 library bindings.
```

### status (recommended)

Indicates maturity and stability.

**Options**:

- `stable` - Production-ready, well-tested
- `beta` - Functional but may change
- `experimental` - Early development, expect changes
- `deprecated` - No longer maintained, use alternative

### platforms (recommended)

Which platforms support this skill.

**Options**: `["claude-code"]`, `["windsurf"]`, `["claude-code", "windsurf"]`

### allowed-tools (recommended)

Restricts which tools Claude can use within this skill.

**Common patterns**:

```yaml
# Read-only analysis
allowed-tools: ["Read", "Grep", "Glob"]

# Code modification
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob"]

# Full automation
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob", "AskUserQuestion"]

# GitHub integration
allowed-tools: ["Bash", "gh", "Read", "Write"]
```

### requires (optional)

Lists prerequisites and dependencies.

**Examples**:

```yaml
requires: ["gh CLI authenticated", "repository write access"]
requires: ["python >= 3.11", "pypdf2 >= 3.0.0"]
requires: ["node >= 18", "npm >= 9"]
```

### tags (optional)

Keywords for categorization and discovery.

```yaml
tags: ["github", "automation", "projects", "kanban"]
tags: ["testing", "quality", "ci-cd"]
tags: ["documentation", "markdown", "organization"]
```

### category (optional)

High-level categorization.

**Common categories**: `development`, `testing`, `documentation`, `git`, `github`, `data`, `security`

## Writing effective descriptions

### Third-person voice

Always write in third person, present tense:

**Good**:

- ✅ "Processes Excel files and generates reports"
- ✅ "Analyzes code for security vulnerabilities"
- ✅ "Creates GitHub Projects with standardized fields"

**Avoid**:

- ❌ "I can help you process Excel files"
- ❌ "You can use this to analyze code"
- ❌ "This skill creates GitHub Projects"

### Include trigger keywords

Add specific terms users would naturally mention:

```yaml
description: Reviews content against style guide compliance. Use when reviewing emails, knowledge base articles, or when user mentions "content review", "style guide", "editorial standards", or "content quality".
```

**Trigger keywords**:

- User actions: "review", "check", "validate", "create", "setup"
- Domain terms: "pull request", "test failures", "documentation"
- Tools/tech: "GitHub Projects", "PDF files", "Excel spreadsheets"
- Quality concerns: "style guide", "security", "performance"

### What + when pattern

Combine capabilities with usage context:

```yaml
# What: Manages GitHub Projects V2 items
# When: adding issues, updating fields, bulk operations
description: Manages GitHub Projects V2 items and custom fields. Use when adding issues to projects, updating Status/Value/Effort fields, or performing bulk operations.
```

## Progressive disclosure

Keep `SKILL.md` under 500 lines by moving detailed content to separate files.

### Reference files

**REFERENCE.md** - Detailed technical documentation:

```markdown
# Detailed reference

## API documentation

Complete method signatures, parameters, return values.

## Configuration options

All available settings with descriptions and defaults.

## Advanced usage

Complex scenarios and edge cases.
```

**EXAMPLES.md** - Usage patterns and samples:

```markdown
# Examples

## Basic usage

[Simple, common scenarios]

## Advanced patterns

[Complex workflows and integrations]

## Troubleshooting examples

[Common issues and solutions]
```

### When to use progressive disclosure

**Keep in SKILL.md**:

- Overview and navigation
- Step-by-step workflow
- Common patterns
- Quick reference

**Move to reference files**:

- Complete API documentation
- All configuration options
- Extensive examples
- Deep troubleshooting guides
- Historical context

### Referencing files

Use clear, descriptive references:

```markdown
## API reference

For complete API documentation, see [REFERENCE.md](REFERENCE.md).

## Examples

See [EXAMPLES.md](EXAMPLES.md) for:
- Basic form filling workflows
- Advanced template usage
- Integration patterns
```

Claude loads these files only when needed, preserving context window.

## Skill structure patterns

### Configuration-driven skill

For project-specific settings and IDs:

```markdown
---
name: managing-github-projects
description: Manages GitHub Projects V2 with project-specific field IDs and options.
allowed-tools: ["Bash", "gh", "Read", "Write"]
---

# Managing GitHub projects

## Project configuration

Your project details:
- **Project ID**: `PVT_abcd1234`
- **Status field ID**: `PVTSSF_xyz789`
- **Status options**: Backlog, Todo, In Progress, Done

## What you should do

1. Use `gh project` commands with IDs above
2. Update fields using exact option values
3. [Additional workflow steps]

## Field reference

See [FIELDS.md](FIELDS.md) for complete field IDs and options.
```

### Template-based skill

For scaffolding and code generation:

```markdown
---
name: scaffolding-microservices
description: Creates standardized microservice structure with templates.
allowed-tools: ["Read", "Write", "Bash"]
---

# Scaffolding microservices

## What you should do

1. Ask for service name
2. Create directory structure using templates
3. Generate boilerplate files
4. Configure dependencies

## Templates

- `templates/service-template/` - Base service structure
- `templates/api-template/` - API endpoint template
- `templates/test-template/` - Test file template

See [TEMPLATES.md](TEMPLATES.md) for template customization.
```

### Analysis and reporting skill

For code quality, security, or metrics:

```markdown
---
name: auditing-test-quality
description: Analyzes test suite quality and identifies vanity tests.
allowed-tools: ["Bash", "Read", "Grep", "Glob"]
---

# Auditing test quality

## What you should do

1. Scan test files for patterns
2. Identify vanity tests (execute but don't validate)
3. Check behavioral naming patterns
4. Analyze mock usage (max 5 per test, 3:1 mock:assertion ratio)
5. Generate quality report

## Quality criteria

See [CRITERIA.md](CRITERIA.md) for complete quality standards.
```

### Automation workflow skill

For repetitive tasks with validation:

```markdown
---
name: running-tests
description: Executes test suites with automatic failure debugging.
allowed-tools: ["Bash", "Read", "Write", "Edit", "Grep"]
---

# Running tests

## What you should do

**CRITICAL**: Never bypass test failures. Fix root cause, not symptoms.

1. Detect test command (pytest, npm test, go test)
2. Execute test suite
3. If failures:
   - Parse failure output
   - Identify root cause
   - Fix broken tests or code
   - Re-run validation
4. Confirm all tests pass

## Test patterns

See [PATTERNS.md](PATTERNS.md) for test execution patterns by language.
```

## Discovery optimization

### Test your description

Good descriptions enable contextual discovery:

**Test scenarios**:

1. **Direct request**: "Create a GitHub Project"
   - Should trigger `managing-github-projects` skill

2. **Implicit request**: "I need to organize my issues"
   - Should suggest `managing-github-projects` skill

3. **Problem-based**: "My tests are failing"
   - Should trigger `running-tests` skill

### Keyword density

Include variations users might say:

```yaml
description: Manages GitHub Projects V2 items and custom fields using GitHub CLI. Use when adding issues to projects, updating Status (Backlog/Todo/Doing/Done), Value (Essential/Useful/Nice-to-have), or Effort (Light/Moderate/Heavy) fields, querying project data, or performing bulk operations.
```

Keywords: GitHub, Projects, issues, Status, Value, Effort, fields, project data, bulk operations

## Best practices

### Do

- **Use gerund form naming** - "Managing X", not "Manager" or "Manage"
- **Write third-person descriptions** - "Processes files", not "I process"
- **Include specific triggers** - "when user mentions X, Y, Z"
- **Keep SKILL.md focused** - Move details to reference files
- **Restrict tools appropriately** - Least privilege principle
- **Test discovery** - Verify natural language triggers it

### Don't

- **Don't use vague names** - Avoid "helper", "utils", "tools"
- **Don't write first-person** - Never "I can help you"
- **Don't skip triggers** - Always include "Use when..." context
- **Don't overload SKILL.md** - Split when approaching 500 lines
- **Don't allow all tools** - Be explicit about permissions
- **Don't assume discovery** - Test with real user phrases

## Validation checklist

Before finalizing a skill:

### Content quality

- [ ] Description uses third-person voice
- [ ] Description includes both what and when
- [ ] Description has specific trigger keywords
- [ ] Name uses gerund form ("Managing X")
- [ ] `SKILL.md` body under 500 lines
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Concrete examples (not abstract)
- [ ] Forward slashes in all paths

### Technical correctness

- [ ] Frontmatter YAML is valid
- [ ] `allowed-tools` lists real tools
- [ ] `requires` dependencies are accurate
- [ ] File references use correct paths
- [ ] Scripts are executable and tested

### Discovery testing

- [ ] Direct requests trigger skill appropriately
- [ ] Implicit requests suggest skill
- [ ] Trigger keywords work as expected
- [ ] Doesn't trigger for unrelated requests

## Common skill types

### GitHub automation

**Pattern**: Project IDs + field options + CLI commands

```markdown
---
name: managing-github-projects
description: Manages GitHub Projects V2 with standardized fields.
allowed-tools: ["Bash", "gh", "Read"]
---

## Project configuration

- Project ID: PVT_xyz
- Field IDs: Status, Value, Effort
- Options: [specific values]

## Commands

`gh project item-add`
`gh project field-update`
```

### Document processing

**Pattern**: Workflows + validation + scripts

```markdown
---
name: processing-pdf-files
description: Extracts text, fills forms, merges PDF documents.
allowed-tools: ["Bash", "Read", "Write"]
---

## Workflow

1. Analyze PDF structure
2. Map form fields
3. Validate data
4. Fill and save

Scripts: `scripts/pdf-merge.py`
```

### Code generation

**Pattern**: Templates + examples + style guide

```markdown
---
name: generating-components
description: Scaffolds React components with TypeScript and tests.
allowed-tools: ["Read", "Write", "Bash"]
---

## Templates

- Component: `templates/component.tsx`
- Test: `templates/component.test.tsx`
- Styles: `templates/component.module.css`

Follow project style guide.
```

### Quality analysis

**Pattern**: Criteria + scanning + reporting

```markdown
---
name: auditing-code-quality
description: Analyzes code for complexity and maintainability.
allowed-tools: ["Bash", "Read", "Grep", "Glob"]
---

## Quality criteria

- Cyclomatic complexity < 10
- Function length < 50 lines
- Max nesting depth: 4

Scan, analyze, report issues.
```

## When to create a skill

Create a skill (not command or workflow) when:

1. **Multiple supporting files needed** - Templates, scripts, examples
2. **Team knowledge to capture** - Standardized workflows
3. **Automatic discovery required** - Should trigger contextually
4. **Configuration-driven** - Project-specific IDs or settings
5. **Progressive disclosure beneficial** - Reference docs loaded on demand

## Further reading

For comprehensive best practices including:

- Degrees of freedom in skill design
- Content guidelines and anti-patterns
- Evaluation strategies
- Detailed skill type patterns

See the `creating-agent-skills` skill or [BEST-PRACTICES.md](../creating-agent-skills/BEST-PRACTICES.md) in this repository.

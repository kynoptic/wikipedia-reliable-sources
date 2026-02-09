# Agent Skills Best Practices Reference

Complete reference for best practices when creating Agent Skills.

## Core principles

### Concise is key

The context window is a public good. Only add context Claude doesn't already have.

**Default assumption**: Claude is already very smart.

**Good example (concise)**:

```markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

**Bad example (too verbose)**:

```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available for PDF processing, but we
recommend pdfplumber because it's easy to use and handles most cases well.
First, you'll need to install it using pip. Then you can use the code below...
```

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility:

- **High freedom** (text-based instructions): Multiple approaches valid, decisions depend on context
- **Medium freedom** (pseudocode/scripts with parameters): Preferred pattern exists, some variation acceptable
- **Low freedom** (specific scripts): Operations fragile, consistency critical, specific sequence required

**Analogy**: Think of Claude as a robot exploring a path:
- Narrow bridge with cliffs = low freedom (exact instructions)
- Open field with no hazards = high freedom (general direction)

## Content guidelines

### Avoid time-sensitive information

Use "old patterns" section for deprecated content:

```markdown
## Current method

Use the v2 API endpoint: `api.example.com/v2/messages`

## Old patterns

<details>
<summary>Legacy v1 API (deprecated 2025-08)</summary>

The v1 API used: `api.example.com/v1/messages`

This endpoint is no longer supported.
</details>
```

### Use consistent terminology

Choose one term and use it throughout:

**Good (consistent)**:
- Always "API endpoint"
- Always "field"
- Always "extract"

**Bad (inconsistent)**:
- Mix "API endpoint", "URL", "API route", "path"
- Mix "field", "box", "element", "control"

## Common patterns

### Template pattern

Provide templates for output format:

**For strict requirements**:

```markdown
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data
```
```

**For flexible guidance**:

```markdown
## Report structure

Here is a sensible default format, adapt as needed:

```markdown
# [Analysis Title]

## Executive summary
[Overview]

## Key findings
[Adapt based on what you discover]
```

Adjust sections as needed for the specific analysis type.
```

### Examples pattern

Provide input/output pairs:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

Follow this style: type(scope): brief description, then detailed explanation.
```

## Anti-patterns to avoid

### Avoid Windows-style paths

Always use forward slashes:

- ✅ Good: `scripts/helper.py`, `reference/guide.md`
- ❌ Avoid: `scripts\helper.py`, `reference\guide.md`

### Avoid offering too many options

Don't present multiple approaches unless necessary:

**Bad (confusing)**:
"You can use pypdf, or pdfplumber, or PyMuPDF, or pdf2image, or..."

**Good (provides default)**:
"Use pdfplumber for text extraction. For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."

### Avoid deeply nested references

Keep all references one level deep from SKILL.md.

### Avoid vague names

Use specific, descriptive names that indicate what the skill does.

## Evaluation and iteration

### Build evaluations first

Create evaluations BEFORE writing extensive documentation:

1. **Identify gaps**: Run Claude on tasks without the skill, document failures
2. **Create evaluations**: Build 3 scenarios that test these gaps
3. **Establish baseline**: Measure performance without the skill
4. **Write minimal instructions**: Create just enough to address gaps
5. **Iterate**: Execute evaluations, compare against baseline, refine

### Develop skills iteratively with Claude

**Creating a new skill**:

1. Complete a task without a skill - notice what context you repeatedly provide
2. Identify the reusable pattern - what information would help similar tasks?
3. Ask Claude to create a skill - Claude understands skill format natively
4. Review for conciseness - remove unnecessary explanations
5. Improve information architecture - organize content effectively
6. Test on similar tasks - use with fresh Claude instance
7. Iterate based on observation - refine based on actual usage

**Iterating on existing skills**:

1. Use skill in real workflows - give Claude actual tasks
2. Observe behavior - note where it struggles or succeeds
3. Return to Claude for improvements - describe what you observed
4. Review suggestions - Claude can suggest reorganization or stronger language
5. Apply and test changes - update skill and test again
6. Repeat based on usage - continue observe-refine-test cycle

### Observe how Claude navigates skills

Pay attention to:
- Unexpected exploration paths
- Missed connections to important files
- Overreliance on certain sections
- Ignored content

The name and description are critical for skill discovery.

## Common skill types and patterns

### Data analysis skills

**Pattern**: Domain-specific schemas + common queries + filters

**Example**: BigQuery analysis with table schemas, naming conventions, filtering rules

**Key elements**:
- Table schemas in reference files
- Common query patterns
- Business rules (e.g., "always exclude test accounts")
- Domain-specific calculations

### Document processing skills

**Pattern**: Workflows + validation + utility scripts

**Example**: PDF form filling with analyze → map → validate → fill workflow

**Key elements**:
- Clear step-by-step workflows
- Validation at each step
- Error recovery guidance
- Utility scripts for fragile operations

### Code generation skills

**Pattern**: Templates + examples + style guide

**Example**: Commit message generation with format + examples

**Key elements**:
- Output templates
- Input/output example pairs
- Style guidelines
- Edge case handling

### Configuration skills

**Pattern**: Project-specific settings + references

**Example**: GitHub Projects with pre-configured IDs and field options

**Key elements**:
- Project-specific constants
- Field/option mappings
- Quick reference tables
- Workflow patterns

## When creating a skill, ask:

1. **Is this reusable?** - Does this knowledge apply to multiple tasks?
2. **Is this domain-specific?** - Does it contain information Claude doesn't already have?
3. **Is this actionable?** - Can Claude use this to complete tasks?
4. **Is this discoverable?** - Will the description trigger when relevant?
5. **Is this concise?** - Have you removed unnecessary explanations?
6. **Is this testable?** - Can you verify the skill works with evaluations?

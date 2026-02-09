---
area: docs
subarea: github
goal: alerts
platforms:
  - windsurf
  - claude
status: active
requires: []
---

# GitHub Markdown Alerts usage guidelines

## Purpose
Standardize the use of GitHub's five native markdown alert types to improve documentation clarity, user experience, and information hierarchy.

## Alert types and usage

### NOTE - General information
> [!NOTE]
> Use NOTE for helpful context, clarification, or supplementary details that enhance understanding without being critical to success.

**When to use:**
- Providing background context or clarification
- Adding supplementary details that enhance understanding
- Highlighting useful information for quick scanning

**Avoid using for:**
- Critical information that users must know
- Warnings about risks or consequences

### TIP - Helpful advice
> [!TIP]
> Use TIP for optional information that helps users be more successful, efficient, or follow best practices.

**When to use:**
- Sharing best practices or recommended approaches
- Offering shortcuts or time-saving techniques
- Providing optimization suggestions or pro techniques

**Avoid using for:**
- Required steps or essential information
- Risk warnings or destructive actions

### IMPORTANT - Critical information
> [!IMPORTANT]
> Use IMPORTANT for crucial information that users absolutely need to know to achieve their goal successfully.

**When to use:**
- Highlighting required steps that cannot be skipped
- Emphasizing critical configuration requirements
- Drawing attention to essential prerequisites

**Avoid using for:**
- Nice-to-know details or optional information
- General tips or suggestions

### WARNING - Urgent attention required
> [!WARNING]
> Use WARNING for critical content that demands immediate attention due to security concerns, data loss risks, or destructive actions.

**When to use:**
- Alerting to security vulnerabilities or risks
- Highlighting destructive or irreversible actions
- Indicating potential data loss or system damage

**Avoid using for:**
- General cautions or minor issues
- Performance implications without data risk

### CAUTION - Risk awareness
> [!CAUTION]
> Use CAUTION for advising users about risks or negative consequences that are important but less urgent than WARNING level.

**When to use:**
- Highlighting actions that might cause unexpected behavior
- Warning about performance implications
- Noting compatibility or limitation issues

**Avoid using for:**
- Critical security risks (use WARNING)
- General information (use NOTE)

## Alert hierarchy and priority

When multiple alerts are needed, follow this priority order:

1. **WARNING** - Most critical, immediate risks
2. **IMPORTANT** - Essential information for success
3. **CAUTION** - Important risks to be aware of
4. **NOTE** - Helpful contextual information
5. **TIP** - Nice-to-have optimizations

## Usage best practices

### Placement guidelines
- Position alerts at logical points in content flow
- Place before the content they relate to, not after
- Use sparingly - limit to 1-2 alerts per document section
- Avoid consecutive alerts (merge or restructure content instead)

### Content guidelines
- Keep alert text concise and actionable
- Include specific examples or code when relevant
- Use active voice and clear language
- All standard markdown formatting works within alerts

### Frequency guidelines
> [!NOTE]
> GitHub recommends using alerts sparingly - limit to 1-2 per article for maximum impact.

**Recommended limits:**
- Maximum 3-4 alerts per document
- No more than 2 alerts per section
- Never stack alerts consecutively
- Prefer restructuring content over multiple alerts

## Syntax reference

```markdown
> [!NOTE]
> Note content here

> [!TIP]
> Tip content here

> [!IMPORTANT]
> Important content here

> [!WARNING]
> Warning content here

> [!CAUTION]
> Caution content here
```

## Multi-line alert formatting

> [!IMPORTANT]
> Multi-line alerts support full markdown formatting:
>
> - Bullet points for clarity
> - Code examples: `npm install`
> - **Bold text** for emphasis
> - Links and other formatting
>
> Always maintain proper spacing and indentation.

## Integration with documentation standards

### Diátaxis alignment
- **Tutorials**: Use NOTE for context, TIP for best practices
- **How-to guides**: Use IMPORTANT for required steps, CAUTION for risks
- **Reference**: Use NOTE for clarification, WARNING for destructive operations
- **Explanations**: Use NOTE for additional context, TIP for deeper insights

### MECE framework alignment
- **Getting started**: IMPORTANT for prerequisites, TIP for efficiency
- **Tasks and operations**: WARNING for destructive actions, CAUTION for side effects
- **Configuration**: IMPORTANT for required settings, NOTE for optional parameters
- **Troubleshooting**: CAUTION for potential causes, TIP for solutions

## Examples by documentation type

### Installation guides
> [!IMPORTANT]
> Python 3.11 or higher is required before proceeding with installation.

> [!WARNING]
> Never run `pip install` with `sudo` on macOS or Linux as this can break your system Python installation.

> [!TIP]
> Use a virtual environment to avoid dependency conflicts: `python -m venv venv && source venv/bin/activate`

### API documentation
> [!IMPORTANT]
> All API requests must include a valid authentication token in the `Authorization` header.

> [!WARNING]
> API tokens expire after 24 hours. Expired tokens result in 401 Unauthorized responses.

> [!TIP]
> Use the `/auth/refresh` endpoint to obtain a new token before the current one expires.

### Configuration guides
> [!NOTE]
> Configuration files use YAML format and support environment variable substitution using `${VAR_NAME}` syntax.

> [!CAUTION]
> Changing the database port requires restarting all connected services and may cause temporary downtime.

### Troubleshooting documentation
> [!NOTE]
> Permission errors often indicate insufficient access rights for your user account.

> [!CAUTION]
> Changing file permissions with `chmod 777` creates security vulnerabilities. Use minimum required permissions instead.

## Visual appearance reference

When rendered on GitHub, alerts display with distinctive colors and icons:

- **NOTE**: Blue with info icon
- **TIP**: Green with lightbulb icon
- **IMPORTANT**: Purple with report icon
- **WARNING**: Yellow with warning triangle icon
- **CAUTION**: Red with stop sign icon

## Anti-patterns to avoid

### Don't overuse alerts
```markdown
<!-- ❌ Bad: Alert overload -->
> [!WARNING]
> This is dangerous

> [!IMPORTANT]
> This is critical

> [!CAUTION]
> This might break

> [!NOTE]
> Just so you know
```

### Don't nest or stack alerts
```markdown
<!-- ❌ Bad: Consecutive alerts -->
> [!WARNING]
> Security risk here

> [!CAUTION]
> Performance impact too
```

### Don't use wrong alert types
```markdown
<!-- ❌ Bad: Wrong severity -->
> [!WARNING]
> Here's a helpful tip for better performance
```

### Do restructure instead
```markdown
<!-- ✅ Good: Single comprehensive alert -->
> [!WARNING]
> This operation involves security risks and performance impacts:
>
> - May expose sensitive data if permissions are incorrect
> - Can cause temporary slowdown during processing
> - Requires administrative privileges to execute
```

## Quality checklist

Before publishing documentation with alerts:

- [ ] Each alert uses the most appropriate type for its content
- [ ] Alert content is concise and actionable
- [ ] No more than 2 alerts per section
- [ ] No consecutive alerts without intervening content
- [ ] All alerts add meaningful value to user experience
- [ ] Alert hierarchy follows logical priority order
- [ ] Standard markdown formatting is used correctly within alerts
# Label Color Standards

Reference guide for semantic color assignment when creating repository labels.

## Quick Reference Table

| Category | Purpose | Hex Code | Example Labels |
|----------|---------|----------|----------------|
| **Critical (Red)** | Urgent, blocking issues | `FF3B30` | bug, breaking-change |
| **High Priority (Orange)** | Important, needs attention | `FF9500` | security, performance |
| **Medium Priority (Light Orange)** | Notable issues | `FF6B35` | accessibility, ux |
| **Success (Green)** | Quality improvements | `34C759` | testing, quality |
| **Enhancement (Light Green)** | Nice to have | `30D158` | enhancement, feature-request |
| **Refinement (Purple)** | Code improvement | `AF52DE` | refactor, cleanup |
| **Feature (Light Purple)** | New capability | `5856D6` | api, new-feature |
| **Infrastructure (Cyan)** | Build/deploy systems | `00C7BE` | ci, deployment |
| **Technical (Blue)** | Technical components | `007AFF` | dependencies, architecture |
| **Routine (Medium Gray)** | Documentation, config | `8E8E93` | docs, config |
| **Minor (Light Gray)** | Cosmetic, trivial | `C7C7CC` | formatting, typo |
| **Blocked (Dark Gray)** | Cannot proceed | `48484A` | blocked, on-hold |

## Color Assignment Decision Tree

### Step 1: Determine urgency/impact
- **Critical/blocking** → Red-Orange spectrum (`FF3B30` - `FF6B35`)
- **Important/valuable** → Purple-Blue spectrum (`5856D6` - `007AFF`)
- **Positive/quality** → Green spectrum (`30D158` - `34C759`)
- **Routine/neutral** → Gray spectrum (`48484A` - `C7C7CC`)

### Step 2: Select specific shade
- **Darker = higher urgency** within same color family
- **Brighter = more positive** for quality/enhancement labels

## Color Families Explained

### Red-Orange Spectrum (Critical/Urgent)
Use for issues that **block progress** or require **immediate attention**:
- `FF3B30` (Red) - Critical bugs, breaking changes
- `FF9500` (Orange) - Security vulnerabilities, high priority
- `FF6B35` (Light Orange) - Performance issues, accessibility

### Green Spectrum (Quality/Positive)
Use for issues that **improve quality** or **add value**:
- `34C759` (Green) - Testing, quality assurance
- `30D158` (Light Green) - Enhancements, improvements

### Purple Spectrum (Refinement/Features)
Use for **code improvements** or **new capabilities**:
- `AF52DE` (Purple) - Refactoring, code cleanup
- `5856D6` (Light Purple) - New features, API changes

### Blue-Cyan Spectrum (Infrastructure/Technical)
Use for **build systems** or **technical infrastructure**:
- `00C7BE` (Cyan) - CI/CD, deployment, automation
- `007AFF` (Blue) - Dependencies, architecture, technical debt

### Gray Spectrum (Routine/Neutral)
Use for **routine maintenance** or **blocked items**:
- `48484A` (Dark Gray) - Blocked, on-hold, wontfix
- `8E8E93` (Medium Gray) - Documentation, maintenance
- `C7C7CC` (Light Gray) - Configuration, minor changes

## Color Selection Rules

1. **Darker shades = higher urgency** within same color family
2. **Never use pure red (`FF0000`)** - too alarming, reserve for true emergencies
3. **Limit to 2-3 shades per color family** - too many creates confusion
4. **Test accessibility** - ensure sufficient contrast (WCAG AA minimum)
5. **Match GitHub defaults when possible** - `bug` uses GitHub's default red (`FF3B30`)

## Implementation

```bash
# Create label with semantic color
gh label create "bug" --description "Something isn't working" --color "FF3B30"

# Update existing label to standard color
gh label edit "security" --color "FF9500" --description "Security vulnerabilities"
```

## Common Patterns

**Single label:**
```bash
gh label create "docs" --color "8E8E93" --description "Documentation"
```

**Multiple related labels (use consistent color family):**
```bash
gh label create "frontend" --color "007AFF" --description "Frontend code"
gh label create "backend" --color "007AFF" --description "Backend code"
gh label create "api" --color "007AFF" --description "API related"
```

## Anti-patterns to Avoid

❌ **Don't use:**
- Random colors without semantic meaning
- Pure primary colors (pure red `FF0000`, pure blue `0000FF`)
- Too many shades (more than 3 per color family)
- Low contrast colors (fails WCAG AA)
- Neon or garish colors that clash with GitHub UI
- **Status labels** (`todo`, `in-progress`, `done`) - use Status custom field in Projects V2
- **Priority labels** (`high-priority`, `low-priority`) - use Value/Effort custom fields
- **Value labels** (`essential`, `nice-to-have`) - use Value custom field
- **Effort labels** (`heavy`, `light`) - use Effort custom field

✅ **Do use:**
- Colors from the standard palette above
- Consistent colors for similar label types
- Darker shades for higher priority
- Test colors against both light and dark GitHub themes

> **Important**: When using GitHub Projects V2, status, priority, value, and effort should be managed as custom fields, not labels. Labels should describe the **nature** (bug, enhancement) and **area** (frontend, api, security) of work.

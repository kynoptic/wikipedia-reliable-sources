# Style mapping reference

Complete reference for Word-to-Markdown style conversions defined in `config/style_map.yml`.

## Style priority hierarchy

1. **Character styles** (highest) - Applied to inline text spans
2. **Paragraph styles** - Applied to entire paragraphs
3. **Direct formatting** - Bold, italic, etc.
4. **Plain text** (lowest) - Default handling

## Character styles

| Word Style | Markdown | Description | Example |
|------------|----------|-------------|---------|
| `Code` | backticks | Inline code elements | `` `<div>` `` |
| `Input` | kbd_tag | Keyboard input references | `<kbd>Space bar</kbd>` |

## Paragraph styles

| Word Style | Markdown | Level | Description |
|------------|----------|-------|-------------|
| `Title` | h1 | 1 | Document title - main H1 heading |
| `Subtitle` | italic | - | Document subtitle with italic |
| `Heading 1` | h2 | 2 | First level heading (offset from Title) |
| `Heading 2` | h3 | 3 | Second level heading |
| `Heading 3` | h4 | 4 | Third level heading |
| `Heading 4` | h5 | 5 | Fourth level heading |
| `Heading 5` | h6 | 6 | Fifth level heading |
| `Heading 6` | h6 | 6 | Sixth level (capped at h6) |
| `Code block` | fenced_code | - | Multi-line code blocks (default: html) |
| `List Paragraph` | bullet_list | - | Unordered list items (`-`) |
| `List Number` | numbered_list | - | Ordered list items (`1.`) |

### Excluded styles

These styles are auto-generated and excluded from conversion:

| Word Style | Reason |
|------------|--------|
| `toc 1` | Table of contents level 1 |
| `toc 2` | Table of contents level 2 |
| `toc 3` | Table of contents level 3 |

## Direct formatting

| Format | Markdown | Priority |
|--------|----------|----------|
| Bold + Italic | `***text***` | 1 (highest) |
| Bold | `**text**` | 2 |
| Italic | `*text*` | 3 |

## Code language detection

The converter auto-detects code block languages based on content patterns:

| Language | Detection Patterns |
|----------|-------------------|
| HTML | `<html>`, `<div>`, `<p>`, `<span>`, `<a>` |
| CSS | `{`, `}`, `:`, `;` (not starting with `<`) |
| JavaScript | `function`, `var `, `let `, `const `, `=>` |
| Python | `def `, `import `, `print(`, `__init__` |

**Default language:** `html`

## Defaults

| Setting | Value |
|---------|-------|
| Default code language | `html` |
| Default list marker | `-` |
| Maximum heading level | 6 |

## Adding custom styles

To add a new style mapping, edit `config/style_map.yml`:

```yaml
# Character style example
character_styles:
  MyCustomCode:
    markdown: "backticks"
    example: "`example`"
    description: "Custom inline code"

# Paragraph style example
paragraph_styles:
  "My Custom Heading":
    markdown: "h3"
    level: 3
    description: "Custom heading style"
```

After editing, test with:
```bash
python convert.py analyze-styles document.docx
python convert.py word-to-md document.docx
```

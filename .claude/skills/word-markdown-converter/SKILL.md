---
name: word-markdown-converter
description: Bidirectional conversion between Word (.docx) and Markdown (.md) with configurable style mapping, validation, and round-trip fidelity. Use when working with document conversion, Word files, Markdown generation, or when the user mentions DOCX, document formatting, style mapping, or needs to convert documents between formats.
---

# Word-Markdown converter

Bidirectional conversion between Word documents and Markdown with high-fidelity style preservation.

## Quick start

```bash
# Navigate to skill directory
cd .claude/skills/word-markdown-converter/scripts

# Convert Word to Markdown
python convert.py word-to-md document.docx

# Convert Markdown to Word
python convert.py md-to-word document.md

# Convert with template
python convert.py md-to-word document.md --template ../config/reference_template.docx
```

## Commands

### Word to Markdown

```bash
python convert.py word-to-md INPUT.docx [OUTPUT.md] [--no-images]
```

**Arguments:**
- `INPUT.docx` - Word document to convert
- `OUTPUT.md` - Output path (optional, defaults to same name with .md)
- `--no-images` - Skip image extraction

**Example:**
```bash
python convert.py word-to-md report.docx
python convert.py word-to-md report.docx output/report.md
```

### Markdown to Word

```bash
python convert.py md-to-word INPUT.md [OUTPUT.docx] [--template TEMPLATE.docx]
```

**Arguments:**
- `INPUT.md` - Markdown file to convert
- `OUTPUT.docx` - Output path (optional, defaults to same name with .docx)
- `--template, -t` - Template document for styling

**Example:**
```bash
python convert.py md-to-word guide.md
python convert.py md-to-word guide.md --template ../config/reference_template.docx
```

### Validate Markdown

```bash
python convert.py validate [DIRECTORY]
```

Validates Markdown files for style compliance.

### Analyze styles

```bash
python convert.py analyze-styles [INPUT.docx]
```

Reports Word document style usage and identifies unmapped styles.

## Bundled contents

```
word-markdown-converter/
├── SKILL.md                 # This file
├── STYLE_REFERENCE.md       # Detailed style mapping reference
├── config/
│   ├── style_map.yml        # Style mapping configuration
│   └── reference_template.docx  # Default Word template
└── scripts/
    ├── convert.py           # Main entry point
    ├── core/
    │   ├── conversion/      # Converter modules
    │   ├── analysis/        # Validation and analysis
    │   └── utils/           # Utilities
    └── filters/             # Pandoc Lua filters
```

## Dependencies

**Required:**
- Python 3.8+
- python-docx (`pip install python-docx`)
- PyYAML (`pip install PyYAML`)
- Pandoc (for Markdown to Word conversion)

**Optional:**
- marko (`pip install marko`) - For Markdown validation

Install all dependencies:
```bash
pip install python-docx PyYAML marko
```

Pandoc installation:
- macOS: `brew install pandoc`
- Ubuntu: `apt install pandoc`
- Windows: Download from https://pandoc.org/installing.html

## Style mapping

All conversions use `config/style_map.yml`. See [STYLE_REFERENCE.md](STYLE_REFERENCE.md) for complete details.

### Key mappings

| Word Style | Markdown |
|------------|----------|
| Title | `# H1` |
| Heading 1 | `## H2` |
| Heading 2 | `### H3` |
| Code (character) | `` `backticks` `` |
| Input (character) | `<kbd>key</kbd>` |
| Code block | ` ```html ` |

### Priority order

1. Character styles (highest)
2. Paragraph styles
3. Direct formatting (bold, italic)
4. Plain text (lowest)

## Common workflows

### Convert a batch of documents

```bash
# From skill scripts directory
cd .claude/skills/word-markdown-converter/scripts

# Convert multiple files
for f in /path/to/docs/*.docx; do
    python convert.py word-to-md "$f" "output/$(basename "${f%.docx}.md")"
done
```

### Round-trip conversion

```bash
# Word -> Markdown
python convert.py word-to-md original.docx

# Edit the markdown...

# Markdown -> Word
python convert.py md-to-word original.md final.docx --template ../config/reference_template.docx
```

### Using from another directory

```bash
# Set PYTHONPATH to include scripts
export SKILL_DIR="/path/to/.claude/skills/word-markdown-converter"
python "$SKILL_DIR/scripts/convert.py" word-to-md document.docx
```

## Troubleshooting

### "Pandoc not found"

The Markdown-to-Word conversion requires Pandoc. Install it:
- macOS: `brew install pandoc`
- Linux: `apt install pandoc` or `dnf install pandoc`

Without Pandoc, the converter falls back to a basic manual conversion.

### "ModuleNotFoundError: No module named 'docx'"

Install python-docx:
```bash
pip install python-docx
```

### Style not converted correctly

1. Run `python convert.py analyze-styles document.docx`
2. Check if the style is mapped in `config/style_map.yml`
3. Add missing styles to the config

### Images not appearing

Images are extracted to a directory next to the output file. Ensure write permissions exist.
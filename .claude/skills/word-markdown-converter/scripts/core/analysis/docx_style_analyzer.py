#!/usr/bin/env python3
"""
Analyze styles used in DOCX files to ensure complete coverage
"""

import sys
from pathlib import Path
from collections import defaultdict

try:
    from docx import Document
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)

def analyze_styles_in_document(docx_path):
    """Analyze all styles used in a DOCX document"""
    print(f"\nAnalyzing: {docx_path}")

    doc = Document(docx_path)

    # Track style usage
    para_styles = defaultdict(int)
    char_styles = defaultdict(int)

    # Analyze paragraph styles
    for para in doc.paragraphs:
        style_name = para.style.name if para.style else "Normal"
        para_styles[style_name] += 1

        # Analyze character styles in runs
        for run in para.runs:
            if run.style and run.style.name != 'Default Paragraph Font':
                char_styles[run.style.name] += 1

    # Report findings
    print(f"Paragraph styles found:")
    for style, count in sorted(para_styles.items()):
        print(f"  {style}: {count} occurrences")

    print(f"\nCharacter styles found:")
    if char_styles:
        for style, count in sorted(char_styles.items()):
            print(f"  {style}: {count} occurrences")
    else:
        print("  No custom character styles found")

    return para_styles, char_styles

def main():
    # Analyze all organizational Word documents
    docx_dir = Path(__file__).parent.parent.parent / "content/docx"

    all_para_styles = defaultdict(int)
    all_char_styles = defaultdict(int)

    print("Analyzing all organizational Word documents for complete style inventory...\n")

    # Find all DOCX files
    docx_files = list(docx_dir.rglob("*.docx"))

    for docx_path in docx_files:
        para_styles, char_styles = analyze_styles_in_document(docx_path)

        # Aggregate counts
        for style, count in para_styles.items():
            all_para_styles[style] += count
        for style, count in char_styles.items():
            all_char_styles[style] += count

    # Summary report
    print("\n" + "="*60)
    print("COMPLETE ORGANIZATIONAL STYLE INVENTORY")
    print("="*60)

    print(f"\nALL PARAGRAPH STYLES FOUND:")
    for style, count in sorted(all_para_styles.items()):
        print(f"  {style}: {count} total occurrences")

    print(f"\nALL CHARACTER STYLES FOUND:")
    if all_char_styles:
        for style, count in sorted(all_char_styles.items()):
            print(f"  {style}: {count} total occurrences")
    else:
        print("  No custom character styles found")

    print(f"\nAnalyzed {len(docx_files)} documents total.")

if __name__ == "__main__":
    main()

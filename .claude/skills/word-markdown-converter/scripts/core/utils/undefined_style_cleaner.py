#!/usr/bin/env python3
"""
Remove styles that aren't explicitly defined from reference.docx
Keep only styles that have explicit formatting properties
"""

import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)

def has_explicit_formatting(style):
    """Check if a style has explicit formatting properties defined"""

    # Always keep these essential styles
    essential_styles = {
        'Normal', 'Default Paragraph Font', 'Code', 'Input',
        'Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'Heading 5', 'Heading 6',
        'Code block', 'List Paragraph', 'List Bullet', 'Block Text', 'Title', 'Subtitle',
        'toc 1', 'toc 2'
    }

    if style.name in essential_styles:
        return True

    # Check if style has any explicit formatting
    try:
        font = style.font
        has_font_formatting = any([
            font.name,
            font.size,
            font.bold is not None,
            font.italic is not None,
            font.underline is not None,
            font.color.rgb
        ])

        # For paragraph styles, check paragraph formatting
        has_para_formatting = False
        if hasattr(style, 'paragraph_format'):
            para_format = style.paragraph_format
            has_para_formatting = any([
                para_format.left_indent,
                para_format.right_indent,
                para_format.first_line_indent,
                para_format.space_before,
                para_format.space_after
            ])

        # Check for background shading
        has_background = False
        try:
            element = style._element
            shd = element.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd')
            if shd is not None:
                fill_color = shd.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill')
                has_background = bool(fill_color)
        except:
            pass

        return has_font_formatting or has_para_formatting or has_background

    except Exception as e:
        print(f"Error checking formatting for {style.name}: {e}")
        return False

def clean_undefined_styles():
    """Remove styles without explicit formatting from reference.docx"""
    ref_path = Path(__file__).parent / 'reference.docx'

    if not ref_path.exists():
        print(f"Reference document not found at: {ref_path}")
        return

    print(f"Cleaning undefined styles from: {ref_path}")

    doc = Document(ref_path)
    styles = doc.styles

    # Collect styles to remove
    styles_to_remove = []
    styles_to_keep = []

    for style in styles:
        if has_explicit_formatting(style):
            styles_to_keep.append(style.name)
        else:
            styles_to_remove.append(style.name)

    print(f"\nStyles to keep ({len(styles_to_keep)}):")
    for style_name in sorted(styles_to_keep):
        print(f"  ✓ {style_name}")

    print(f"\nStyles to remove ({len(styles_to_remove)}):")
    for style_name in sorted(styles_to_remove):
        print(f"  ❌ {style_name}")

    # Remove undefined styles
    removed_count = 0
    for style_name in styles_to_remove:
        try:
            style_to_remove = styles[style_name]
            style_element = style_to_remove._element
            style_element.getparent().remove(style_element)
            removed_count += 1
        except Exception as e:
            print(f"Could not remove '{style_name}': {e}")

    if removed_count > 0:
        # Save the cleaned document
        backup_path = ref_path.with_suffix('.cleaned.backup.docx')
        ref_path.rename(backup_path)
        print(f"\nCreated backup at: {backup_path}")

        doc.save(str(ref_path))
        print(f"Saved cleaned reference document: {ref_path}")
        print(f"Removed {removed_count} undefined styles")
    else:
        print("\nNo undefined styles found to remove")

if __name__ == "__main__":
    clean_undefined_styles()

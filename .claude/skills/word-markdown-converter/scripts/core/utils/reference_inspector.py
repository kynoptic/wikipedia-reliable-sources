#!/usr/bin/env python3
"""
Word Document Style Inspector and Analysis Tool.

This module provides comprehensive inspection and analysis of Microsoft Word document
styles, including both character and paragraph styles. It extracts detailed formatting
properties from .docx files and reports on style usage patterns, font specifications,
and formatting characteristics.

Key Components:
    - Style enumeration and classification
    - Font property extraction and analysis
    - Color and formatting attribute reporting
    - Comprehensive style inventory generation

Usage Patterns:
    - Style guide development and validation
    - Document template analysis
    - Formatting consistency assessment
    - Style mapping for document conversion

Dependencies:
    - python-docx: Word document processing and style extraction
    - pathlib: Modern path handling utilities
"""

import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)


def _extract_character_styles(document_styles):
    """Extract character styles from document styles."""
    return [style for style in document_styles if style.type == 2]  # WD_STYLE_TYPE.CHARACTER


def _extract_paragraph_styles(document_styles):
    """Extract paragraph styles from document styles."""
    return [style for style in document_styles if style.type == 1]  # WD_STYLE_TYPE.PARAGRAPH


def _report_font_properties(font, indent="  "):
    """Report font properties for a style."""
    if font.name:
        print(f"{indent}Font name: {font.name}")
    if font.size:
        print(f"{indent}Font size: {font.size.pt} pt")
    if font.bold is not None:
        print(f"{indent}Bold: {font.bold}")
    if font.italic is not None:
        print(f"{indent}Italic: {font.italic}")
    if font.underline is not None:
        print(f"{indent}Underline: {font.underline}")
    if font.color.rgb:
        print(f"{indent}Font color: #{font.color.rgb}")


def _report_background_shading(style, indent="  "):
    """Report background shading for a character style."""
    try:
        style_element = style._element
        shading_element = style_element.find(
            ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd"
        )
        if shading_element is not None:
            background_fill_color = shading_element.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill"
            )
            if background_fill_color:
                print(f"{indent}Background: #{background_fill_color}")
    except Exception:
        pass


def _report_paragraph_formatting(paragraph_format, indent="  "):
    """Report paragraph formatting properties."""
    if paragraph_format.left_indent:
        print(f"{indent}Left indent: {paragraph_format.left_indent.pt} pt")
    if paragraph_format.right_indent:
        print(f"{indent}Right indent: {paragraph_format.right_indent.pt} pt")
    if paragraph_format.first_line_indent:
        print(f"{indent}First line indent: {paragraph_format.first_line_indent.pt} pt")
    if paragraph_format.space_before:
        print(f"{indent}Space before: {paragraph_format.space_before.pt} pt")
    if paragraph_format.space_after:
        print(f"{indent}Space after: {paragraph_format.space_after.pt} pt")


def _report_character_styles(character_styles):
    """Generate report for all character styles."""
    print("\nCHARACTER STYLES:")
    print("-" * 40)

    for character_style in character_styles:
        print(f"\n'{character_style.name}' character style:")
        _report_font_properties(character_style.font)
        _report_background_shading(character_style)


def _report_paragraph_styles(paragraph_styles):
    """Generate report for all paragraph styles."""
    print("\n\nPARAGRAPH STYLES:")
    print("-" * 40)

    for paragraph_style in paragraph_styles:
        print(f"\n'{paragraph_style.name}' paragraph style:")
        _report_font_properties(paragraph_style.font)
        _report_paragraph_formatting(paragraph_style.paragraph_format)


def _report_style_summary(character_styles, paragraph_styles):
    """Generate summary statistics for styles."""
    print(f"\nTotal character styles: {len(character_styles)}")
    print(f"Total paragraph styles: {len(paragraph_styles)}")


def inspect_reference_styles() -> None:
    """
    Inspect and report all styles in the reference Word document.

    Performs comprehensive analysis of both character and paragraph styles
    in the reference.docx file, extracting detailed formatting properties
    including fonts, sizes, colors, indentation, and spacing attributes.

    Returns:
        None: Prints detailed style analysis to console

    Raises:
        FileNotFoundError: If reference.docx is not found in expected location
        python_docx.exceptions.PackageNotFoundError: If file is not a valid .docx

    Output Format:
        - Character styles section with font properties
        - Paragraph styles section with formatting details
        - Summary statistics for style counts

    Side Effects:
        - Prints extensive style information to console
        - Logs style analysis details during processing

    Example Output:
        CHARACTER STYLES:
        ----------------------------------------
        'Code' character style:
          Font name: Consolas
          Font size: 10.0 pt
          Background: #F0F0F0
    """
    reference_document_path = Path(__file__).parent / "reference.docx"

    if not reference_document_path.exists():
        print(f"Reference document not found at: {reference_document_path}")
        return

    print(f"Inspecting reference document: {reference_document_path}")
    print("=" * 60)

    reference_document = Document(reference_document_path)
    document_styles = reference_document.styles

    character_styles = _extract_character_styles(document_styles)
    paragraph_styles = _extract_paragraph_styles(document_styles)

    _report_character_styles(character_styles)
    _report_paragraph_styles(paragraph_styles)
    _report_style_summary(character_styles, paragraph_styles)


if __name__ == "__main__":
    inspect_reference_styles()

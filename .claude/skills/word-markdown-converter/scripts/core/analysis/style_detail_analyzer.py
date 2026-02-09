#!/usr/bin/env python3
"""
Analyze detailed formatting properties of organizational Word document styles
"""

import sys
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)


def _initialize_style_entry(style_name, style_obj):
    """Initialize a new style entry with default values"""
    return {
        "samples": [],
        "font_name": None,
        "font_size": None,
        "font_color": None,
        "bold": None,
        "italic": None,
        "underline": None,
        "style_obj": style_obj,
    }


def _collect_sample_text(style_details, style_name, run_text):
    """Collect sample text for a style if under the limit"""
    if len(style_details[style_name]["samples"]) < 3:
        style_details[style_name]["samples"].append(run_text)


def _update_font_properties(style_details, style_name, font):
    """Update font properties for a style from a run's font"""
    if font.name:
        style_details[style_name]["font_name"] = font.name
    if font.size:
        style_details[style_name]["font_size"] = font.size
    if font.color.rgb:
        style_details[style_name]["font_color"] = font.color.rgb
    if font.bold is not None:
        style_details[style_name]["bold"] = font.bold
    if font.italic is not None:
        style_details[style_name]["italic"] = font.italic
    if font.underline is not None:
        style_details[style_name]["underline"] = font.underline


def _process_document_runs(doc, target_styles):
    """Process all runs in document and extract style information"""
    style_details = {}

    for para in doc.paragraphs:
        for run in para.runs:
            if run.style and run.style.name in target_styles:
                style_name = run.style.name

                if style_name not in style_details:
                    style_details[style_name] = _initialize_style_entry(style_name, run.style)

                _collect_sample_text(style_details, style_name, run.text)
                _update_font_properties(style_details, style_name, run.font)

    return style_details


def _format_color_output(rgb_color):
    """Format RGB color for display"""
    if rgb_color:
        return f"RGB({rgb_color.red}, {rgb_color.green}, {rgb_color.blue}) #{rgb_color.red:02x}{rgb_color.green:02x}{rgb_color.blue:02x}"
    return "Default/None"


def _print_run_properties(details):
    """Print run-level style properties"""
    print(f"Sample text: {details['samples']}")
    print(f"Font name: {details['font_name']}")
    print(
        f"Font size: {details['font_size']} ({details['font_size'].pt if details['font_size'] else 'N/A'} pt)"
    )
    print(f"Font color: {_format_color_output(details['font_color'])}")
    print(f"Bold: {details['bold']}")
    print(f"Italic: {details['italic']}")
    print(f"Underline: {details['underline']}")


def _print_style_definition_properties(style_obj):
    """Print style definition properties"""
    style_font = style_obj.font
    print(f"\nStyle definition properties:")
    print(f"  Style font name: {style_font.name}")
    print(
        f"  Style font size: {style_font.size} ({style_font.size.pt if style_font.size else 'N/A'} pt)"
    )
    print(f"  Style font color: {_format_color_output(style_font.color.rgb)}")
    print(f"  Style bold: {style_font.bold}")
    print(f"  Style italic: {style_font.italic}")
    print(f"  Style underline: {style_font.underline}")

    _print_additional_style_properties(style_font, style_obj)


def _print_additional_style_properties(style_font, style_obj):
    """Print additional style properties like highlighting and background"""
    # Check for highlighting/background color
    if hasattr(style_font, "highlight_color") and style_font.highlight_color:
        print(f"  Style highlight: {style_font.highlight_color}")

    # Check shading/background (this is trickier with python-docx)
    try:
        element = style_obj._element
        shd = element.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}shd")
        if shd is not None:
            fill_color = shd.get(
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fill"
            )
            if fill_color:
                print(f"  Background fill: #{fill_color}")
    except:
        pass


def _print_style_analysis_report(style_details):
    """Print detailed analysis report for all styles"""
    for style_name, details in style_details.items():
        print(f"\n--- {style_name} Character Style ---")
        _print_run_properties(details)

        style_obj = details["style_obj"]
        if style_obj:
            _print_style_definition_properties(style_obj)


def analyze_style_details(docx_path, target_styles=["Code", "Input"]):
    """Analyze detailed formatting of specific styles in a DOCX document"""
    print(f"\nAnalyzing style details in: {docx_path}")

    doc = Document(docx_path)
    style_details = _process_document_runs(doc, target_styles)
    _print_style_analysis_report(style_details)

    return style_details


def main():
    # Focus on documents that use Input and Code styles heavily
    test_docs = [
        "content/docx/General/Style guide for IT.docx",
        "content/docx/IT website/Content guidelines for the Getting started page on the IT website.docx",
        "content/docx/IT website/Content template for services on the IT website.docx",
    ]

    base_path = Path(__file__).parent.parent

    all_details = {}

    for doc_path in test_docs:
        full_path = base_path / doc_path
        if full_path.exists():
            details = analyze_style_details(full_path)
            for style_name, style_info in details.items():
                if style_name not in all_details:
                    all_details[style_name] = style_info
        else:
            print(f"Document not found: {full_path}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY - ORGANIZATIONAL STYLE FORMATTING REQUIREMENTS")
    print("=" * 60)

    for style_name, details in all_details.items():
        print(f"\n{style_name} style should be:")
        print(f"  Font: {details['font_name']}")
        if details["font_size"]:
            print(f"  Size: {details['font_size'].pt} pt")
        if details["font_color"]:
            rgb = details["font_color"]
            print(f"  Color: RGB({rgb.red}, {rgb.green}, {rgb.blue})")
        print(f"  Bold: {details['bold']}")
        print(f"  Italic: {details['italic']}")
        print(f"  Underline: {details['underline']}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Standalone document converter for the word-markdown-converter skill.

This script provides bidirectional conversion between Word (.docx) and Markdown (.md)
files. It is self-contained and can be run from within the skill directory.

Usage:
    python convert.py word-to-md INPUT.docx [OUTPUT.md]
    python convert.py md-to-word INPUT.md [OUTPUT.docx] [--template TEMPLATE.docx]
    python convert.py validate [DIRECTORY]
    python convert.py analyze-styles [INPUT.docx]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from core.conversion.markdown_to_word_converter import MarkdownToWordConverter
from core.conversion.word_to_markdown_converter import EnhancedWordToMarkdownConverter
from core.utils.logging_setup import setup_logging


def get_default_config_path() -> Path:
    """Get path to the bundled style_map.yml config."""
    return SCRIPT_DIR.parent / "config" / "style_map.yml"


def get_default_template_path() -> Path:
    """Get path to the bundled reference template."""
    return SCRIPT_DIR.parent / "config" / "reference_template.docx"


def get_filters_path() -> Path:
    """Get path to the bundled Lua filters."""
    return SCRIPT_DIR / "filters"


def convert_word_to_markdown(
    input_path: Path,
    output_path: Path | None = None,
    extract_images: bool = True,
    logger: logging.Logger | None = None,
) -> bool:
    """
    Convert a Word document to Markdown.

    Args:
        input_path: Path to input .docx file
        output_path: Path for output .md file (auto-generated if None)
        extract_images: Whether to extract embedded images
        logger: Optional logger instance

    Returns:
        True if conversion succeeded, False otherwise
    """
    if logger is None:
        logger = setup_logging("word_to_md")

    input_path = Path(input_path)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    if output_path is None:
        output_path = input_path.with_suffix(".md")
    else:
        output_path = Path(output_path)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    converter = EnhancedWordToMarkdownConverter(logger)

    try:
        success = converter.convert_document(
            str(input_path), str(output_path), extract_images=extract_images
        )

        if success:
            logger.info(f"Successfully converted: {input_path} -> {output_path}")
        return success

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False


def convert_markdown_to_word(
    input_path: Path,
    output_path: Path | None = None,
    template_path: Path | None = None,
    logger: logging.Logger | None = None,
) -> bool:
    """
    Convert a Markdown file to Word document.

    Args:
        input_path: Path to input .md file
        output_path: Path for output .docx file (auto-generated if None)
        template_path: Optional template .docx for styling
        logger: Optional logger instance

    Returns:
        True if conversion succeeded, False otherwise
    """
    if logger is None:
        logger = setup_logging("md_to_word")

    input_path = Path(input_path)

    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False

    if output_path is None:
        output_path = input_path.with_suffix(".docx")
    else:
        output_path = Path(output_path)

    # Use bundled template if none specified and it exists
    if template_path is None:
        default_template = get_default_template_path()
        if default_template.exists():
            template_path = default_template
    elif template_path:
        template_path = Path(template_path)
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}")
            template_path = None

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    converter = MarkdownToWordConverter(logger)

    # Set the filters path to use bundled filters
    converter.filters_dir = get_filters_path()

    try:
        success = converter.convert_document(
            str(input_path), str(output_path), str(template_path) if template_path else None
        )

        if success:
            logger.info(f"Successfully converted: {input_path} -> {output_path}")
        return success

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False


def validate_markdown(directory: Path | None = None, logger: logging.Logger | None = None) -> int:
    """
    Validate Markdown files for style compliance.

    Args:
        directory: Directory containing .md files (defaults to current)
        logger: Optional logger instance

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    if logger is None:
        logger = setup_logging("validate")

    try:
        from core.analysis.markdown_format_validator import main as validate_main

        return validate_main()
    except ImportError:
        logger.error("Validation module not available")
        return 1


def analyze_styles(input_path: Path | None = None, logger: logging.Logger | None = None) -> int:
    """
    Analyze Word document styles.

    Args:
        input_path: Optional specific .docx file to analyze
        logger: Optional logger instance

    Returns:
        Exit code (0 for success, 1 for failures)
    """
    if logger is None:
        logger = setup_logging("analyze")

    try:
        from core.analysis.docx_style_analyzer import main as analyze_main

        return analyze_main()
    except ImportError:
        logger.error("Analysis module not available")
        return 1


def main():
    """Main entry point for the converter CLI."""
    parser = argparse.ArgumentParser(
        description="Bidirectional Word/Markdown document converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s word-to-md document.docx
  %(prog)s word-to-md document.docx output.md
  %(prog)s md-to-word document.md
  %(prog)s md-to-word document.md --template template.docx
  %(prog)s validate
  %(prog)s analyze-styles
        """,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    subparsers = parser.add_subparsers(dest="command", help="Conversion command")

    # Word to Markdown
    w2m = subparsers.add_parser("word-to-md", help="Convert Word to Markdown")
    w2m.add_argument("input", type=Path, help="Input .docx file")
    w2m.add_argument("output", type=Path, nargs="?", help="Output .md file")
    w2m.add_argument("--no-images", action="store_true", help="Skip image extraction")

    # Markdown to Word
    m2w = subparsers.add_parser("md-to-word", help="Convert Markdown to Word")
    m2w.add_argument("input", type=Path, help="Input .md file")
    m2w.add_argument("output", type=Path, nargs="?", help="Output .docx file")
    m2w.add_argument("--template", "-t", type=Path, help="Template .docx for styling")

    # Validate
    val = subparsers.add_parser("validate", help="Validate Markdown formatting")
    val.add_argument("directory", type=Path, nargs="?", help="Directory to validate")

    # Analyze styles
    analyze = subparsers.add_parser("analyze-styles", help="Analyze Word document styles")
    analyze.add_argument("input", type=Path, nargs="?", help="Specific .docx to analyze")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    if args.command == "word-to-md":
        success = convert_word_to_markdown(
            args.input, args.output, extract_images=not args.no_images, logger=logger
        )
        sys.exit(0 if success else 1)

    elif args.command == "md-to-word":
        success = convert_markdown_to_word(args.input, args.output, args.template, logger=logger)
        sys.exit(0 if success else 1)

    elif args.command == "validate":
        sys.exit(validate_markdown(args.directory, logger))

    elif args.command == "analyze-styles":
        sys.exit(analyze_styles(args.input, logger))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Word-to-Markdown Document Converter with Advanced Style Mapping.

This module provides comprehensive conversion of Microsoft Word documents (.docx)
to Markdown format with sophisticated style mapping, image extraction, and
document structure preservation. It supports configurable style mappings,
intelligent content classification, and high-fidelity conversion workflows.

Key Components:
    - EnhancedWordToMarkdownConverter: Main conversion engine with style awareness
    - Image extraction and deterministic naming with alt-text preservation
    - Configurable style mapping system with YAML configuration
    - Intelligent list detection and formatting preservation
    - Hyperlink processing and URL resolution
    - Statistical analysis and conversion reporting

Conversion Features:
    - Document structure preservation (headings, lists, tables)
    - Character and paragraph style mapping via configuration
    - Automatic title detection and synthesis
    - Code block grouping and language detection
    - Image extraction with hash-based naming
    - YAML frontmatter generation with metadata

Advanced Capabilities:
    - Context-aware paragraph vs. list classification
    - Definition-style content detection
    - Form field label recognition
    - Table handling with markdown and HTML fallback
    - Continuation paragraph processing under list items

Configuration:
    - Style mappings defined in tools/style_map.yml
    - Customizable code language detection patterns
    - Configurable markdown output preferences
    - Image extraction and naming conventions

Dependencies:
    - python-docx: Word document processing and style extraction
    - PyYAML: Configuration file parsing and processing
    - pathlib: Modern path handling utilities
    - hashlib: Deterministic image naming and integrity

Usage:
    converter = EnhancedWordToMarkdownConverter(logger)
    success = converter.convert_document('input.docx', 'output.md')
"""

import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from docx import Document
    from docx.text.paragraph import Paragraph
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    sys.exit(1)


from .code_processor import CodeProcessor
from .document_processor import DocumentProcessor
from .frontmatter_generator import FrontmatterGenerator
from .hyperlink_processor import HyperlinkProcessor
from .image_extractor import ImageExtractor
from .list_converter import ListConverter
from .paragraph_converter import ParagraphConverter
from .run_formatter import RunFormatter
from .table_converter import TableConverter
from .title_handler import TitleHandler


def setup_logging() -> logging.Logger:
    """Configure logging for the enhanced converter"""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "word_to_markdown_converter.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file, mode="a")],
    )
    return logging.getLogger(__name__)


class EnhancedWordToMarkdownConverter:
    """Enhanced Word to Markdown converter with advanced style mapping"""

    def __init__(self, logger: logging.Logger, config_path: str | None = None):
        self.logger = logger
        self.image_counter = 0
        self.images_dir = None
        self.style_stats = defaultdict(int)
        self.image_mapping = {}
        # Track simple list context for continuation paragraphs
        self._last_was_list_item = False
        self._last_list_level = 0
        self._last_list_indent = None

        # Initialize specialist handlers
        self.title_handler = TitleHandler(logger)
        self.document_processor = DocumentProcessor(logger)
        self.image_extractor = ImageExtractor(logger)
        self.frontmatter_generator = FrontmatterGenerator(logger)
        self.hyperlink_processor = HyperlinkProcessor(logger)
        # CodeProcessor and ParagraphConverter will be initialized after config is loaded

        # Load style configuration
        if config_path is None:
            skill_config = Path(__file__).parent.parent.parent.parent / "config" / "style_map.yml"
            repo_config = Path(__file__).parent.parent.parent / "tools" / "style_map.yml"
            config_path = skill_config if skill_config.exists() else repo_config

        self.config = self._load_config(config_path)
        self.logger.info(f"Loaded style configuration from: {config_path}")

        # Initialize specialist converters with config
        self.code_processor = CodeProcessor(logger, self.config)
        self.paragraph_converter = ParagraphConverter(logger, self.config)
        self.paragraph_converter._parent_converter = self  # Allow access to run processing methods
        self.list_converter = ListConverter(logger, self.config)
        self.table_converter = TableConverter(logger, self.config)
        self.run_formatter = RunFormatter(logger, self.config)

        # Set up dependencies for specialist converters
        self.list_converter.set_converters(
            self.hyperlink_processor.convert_paragraph_with_hyperlinks, self._convert_paragraph_runs
        )
        self.table_converter.set_converters(self._convert_paragraph_runs)

    def convert_document(
        self,
        word_document_path: str,
        markdown_output_path: str,
        extract_images: bool = True,
        include_metadata: bool = False,
    ) -> bool:
        """Convert a Word document to Markdown with advanced formatting support

        Args:
            word_document_path: Path to input Word document
            markdown_output_path: Path for output Markdown file
            extract_images: Whether to extract images from document
            include_metadata: Whether to include YAML frontmatter metadata
        """
        try:
            self.logger.info(f"Starting conversion: {word_document_path} -> {markdown_output_path}")

            if not os.path.exists(word_document_path):
                self.logger.error(f"Input file not found: {word_document_path}")
                return False

            word_document = self._prepare_document(
                word_document_path, markdown_output_path, extract_images
            )
            markdown_content = self._convert_document_content(word_document)
            final_content = self._finalize_content(
                markdown_content,
                word_document_path,
                markdown_output_path,
                word_document,
                include_metadata,
            )

            self._write_output(markdown_output_path, final_content)
            self._log_conversion_stats()
            self.logger.info(f"Conversion completed successfully: {markdown_output_path}")
            return True

        except Exception as e:
            import traceback

            self.logger.error(f"Conversion failed: {e}")
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return False

    def _prepare_document(self, word_path, markdown_path, extract_images):
        """Prepare document for conversion by loading and initializing state"""
        if extract_images:
            if not self.image_extractor.setup_extraction_directory(markdown_path):
                self.logger.warning("Image extraction setup failed, continuing without images")
                extract_images = False
            else:
                self.images_dir = self.image_extractor.images_dir

        word_document = Document(word_path)
        self.logger.info(f"Loaded document with {len(word_document.paragraphs)} paragraphs")

        self._reset_state()
        self._setup_document_processors(word_document, markdown_path, extract_images)

        return word_document

    def _reset_state(self):
        """Reset converter state for new conversion"""
        self.style_stats = defaultdict(int)
        self.image_counter = 0
        self.image_extractor.reset_state()

    def _setup_document_processors(self, word_document, markdown_path, extract_images):
        """Setup processors with document context"""
        self._current_doc_part = word_document.part
        self.hyperlink_processor.set_document_part(word_document.part)
        self.logger.debug(f"Stored document part with {len(word_document.part.rels)} relationships")

        if extract_images:
            self.image_mapping = self.image_extractor.extract_images_with_mapping(
                word_document, markdown_path
            )
            # Sync image counter from image extractor
            self.image_counter = self.image_extractor.image_counter
            self.logger.info(f"Built image mapping: {self.image_mapping}")
        else:
            self.image_mapping = {}

        self.run_formatter.set_dependencies(
            self.image_extractor.extract_run_images,
            self.image_extractor.get_alt_text_for_image,
            self.style_stats,
            self.image_mapping,
        )

    def _finalize_content(
        self, markdown_content, word_path, markdown_path, word_doc, include_metadata
    ):
        """Finalize markdown content with optional frontmatter"""
        if include_metadata:
            yaml_frontmatter = self.frontmatter_generator.generate_frontmatter(
                word_path, markdown_path, word_doc, self.style_stats, self.image_mapping
            )
            return f"{yaml_frontmatter}\n{markdown_content}"
        return markdown_content

    def _write_output(self, output_path, content):
        """Write final content to output file"""
        with open(output_path, "w", encoding="utf-8") as f:
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)

    def batch_convert(
        self,
        input_dir: str,
        output_dir: str,
        extract_images: bool = True,
        include_metadata: bool = False,
    ) -> tuple[int, int]:
        """
        Batch convert all Word documents in a directory.

        Args:
            input_dir: Directory containing Word documents
            output_dir: Directory for output Markdown files
            extract_images: Whether to extract images from documents
            include_metadata: Whether to include YAML frontmatter metadata

        Returns:
            Tuple of (successful_conversions, failed_conversions)
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            self.logger.error(f"Input directory not found: {input_dir}")
            return (0, 0)

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Find all Word documents
        docx_files = list(input_path.glob("**/*.docx"))

        successful = 0
        failed = 0

        for docx_file in docx_files:
            # Skip temporary Word files (start with ~$)
            if docx_file.name.startswith("~$"):
                continue

            # Calculate relative path for output
            rel_path = docx_file.relative_to(input_path)
            output_file = output_path / rel_path.with_suffix(".md")

            # Create output subdirectory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert file
            if self.convert_document(
                str(docx_file), str(output_file), extract_images, include_metadata
            ):
                successful += 1
                self.logger.info(f"Converted: {docx_file.name}")
            else:
                failed += 1
                self.logger.error(f"Failed: {docx_file.name}")

        self.logger.info(f"Batch conversion complete: {successful} successful, {failed} failed")
        return (successful, failed)

    def _convert_document_content(self, word_document: Document) -> str:
        """Convert the full document content to markdown with proper element ordering"""
        self._initialize_document_state()
        markdown_parts = []

        grouped_elements = self.document_processor.get_processed_elements(word_document)
        self._process_title(word_document, markdown_parts)

        for element in grouped_elements:
            self._process_element(element, markdown_parts)

        return self._smart_join_markdown_parts(markdown_parts)

    def _initialize_document_state(self):
        """Initialize state tracking for document conversion"""
        self._title_emitted = False
        self._last_was_list_item = False
        self._last_list_level = 0
        self._skip_title_paragraph = None
        self._last_list_indent = None

    def _process_title(self, word_document, markdown_parts):
        """Process document title if present"""
        title_markdown, skip_paragraph = self.title_handler.detect_and_process_title(word_document)
        if title_markdown:
            markdown_parts.append(title_markdown)
            self._title_emitted = True
            self._skip_title_paragraph = skip_paragraph

    def _process_element(self, element, markdown_parts):
        """Process a single document element (list, table, or paragraph)"""
        if isinstance(element, list):
            self._process_element_group(element, markdown_parts)
        elif hasattr(element, "rows"):
            self._process_table(element, markdown_parts)
        else:
            self._process_paragraph(element, markdown_parts)

    def _process_element_group(self, element_group, markdown_parts):
        """Process a group of consecutive elements (code blocks or list items)"""
        if self._is_code_block_group(element_group):
            md_content = self.code_processor.convert_code_block_group(element_group)
        else:
            md_content = self.list_converter.convert_list_item_group(element_group)

        if md_content and md_content.strip():
            markdown_parts.append(md_content)

    def _is_code_block_group(self, element_group):
        """Check if element group is a code block group"""
        return (
            element_group
            and hasattr(element_group[0], "style")
            and element_group[0].style
            and element_group[0].style.name == "Code block"
        )

    def _process_table(self, table, markdown_parts):
        """Process a table element"""
        md_content = self.table_converter.convert_table(table)
        if not md_content or not md_content.strip():
            return

        if self._last_was_list_item:
            md_content = self.table_converter.indent_table_under_list(
                md_content, self._last_list_level
            )
        markdown_parts.append(md_content)

    def _process_paragraph(self, paragraph, markdown_parts):
        """Process a single paragraph element"""
        if self._skip_title_paragraph is not None and paragraph is self._skip_title_paragraph:
            return

        list_context = {
            "last_was_list_item": self._last_was_list_item,
            "last_list_level": self._last_list_level,
            "last_list_indent": self._last_list_indent,
        }

        md_content, updated_context = self.paragraph_converter.convert_paragraph(
            paragraph,
            list_context,
            self.style_stats,
            self._extract_list_info,
            self._skip_title_paragraph,
        )

        self._update_list_context(updated_context)

        if md_content and md_content.strip():
            self._check_title_emission(paragraph)
            markdown_parts.append(md_content)

    def _update_list_context(self, updated_context):
        """Update list context from paragraph converter"""
        self._last_was_list_item = updated_context.get("last_was_list_item", False)
        self._last_list_level = updated_context.get("last_list_level", 0)
        self._last_list_indent = updated_context.get("last_list_indent", None)

    def _check_title_emission(self, element):
        """Check and update title emission status"""
        if (
            not self._title_emitted
            and hasattr(element, "style")
            and getattr(element.style, "name", "") == "Title"
        ):
            self._title_emitted = True

    def _extract_list_info(self, para: Paragraph) -> dict[str, Any] | None:
        """Extract list numbering information from paragraph"""
        if not hasattr(para._element, "pPr") or para._element.pPr is None:
            return None

        numPr = para._element.pPr.numPr
        if numPr is None:
            return None

        # Extract numId and ilvl
        numId = numPr.numId.val if hasattr(numPr, "numId") and numPr.numId is not None else None
        ilvl = numPr.ilvl.val if hasattr(numPr, "ilvl") and numPr.ilvl is not None else 0

        if numId is None:
            return None

        # Try to determine if this is a numbered or bulleted list
        # This is a heuristic approach since determining exact numbering type
        # from numId requires accessing the document's numbering definitions
        is_numbered = self._is_numbered_list(para, numId, ilvl)

        return {"numId": numId, "level": ilvl, "is_numbered": is_numbered}

    def _is_numbered_list(self, para: Paragraph, numId: int, ilvl: int) -> bool:
        """Heuristic to determine if a list is numbered or bulleted"""
        return self.list_converter.is_numbered_list(para, numId, ilvl)

    def _convert_regular_paragraph(self, para: Paragraph) -> str:
        """Convert regular paragraphs with inline formatting"""
        return self._convert_paragraph_runs(para.runs)

    def _convert_paragraph_runs(self, runs) -> str:
        """Convert paragraph runs to markdown with inline formatting and hyperlinks"""
        # First, check if this paragraph contains hyperlinks and handle them specially
        paragraph = runs[0]._element.getparent() if runs else None
        if paragraph is not None:
            hyperlinks = paragraph.xpath(".//w:hyperlink")
            self.logger.debug(f"Found {len(hyperlinks)} hyperlinks in paragraph")
            if hyperlinks:
                # Process paragraph with hyperlinks using special handling
                self.logger.debug("Processing paragraph with hyperlinks")
                return self.hyperlink_processor.convert_paragraph_with_hyperlinks(paragraph)

        # Standard run processing for paragraphs without hyperlinks
        return self._convert_runs_with_smart_formatting(runs)

    def _convert_runs_with_smart_formatting(self, runs) -> str:
        """Convert runs with intelligent bold/italic consolidation and character style coalescing"""
        return self.run_formatter.convert_runs_with_smart_formatting(runs)

    def _format_character_style_group(self, text_parts, style_name) -> str:
        """Format a group of text parts with consistent character style"""
        return self.run_formatter._format_character_style_group(text_parts, style_name)

    def _resolve_character_style_alias(self, style_name: str | None, run) -> str | None:
        """Normalize character style names and infer from font to determine canonical style"""
        return self.run_formatter._resolve_character_style_alias(style_name, run)

    def _format_run_group(self, text_parts, is_bold, is_italic) -> str:
        """Format a group of text parts with consistent bold/italic formatting"""
        return self.run_formatter.format_run_group(text_parts, is_bold, is_italic)

    def _load_config(self, config_path: Path) -> dict[str, Any]:
        """Load style mapping configuration from YAML file"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.logger.info("Style configuration loaded successfully")
                return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {config_path}")
            # Return minimal fallback config
            return self._get_fallback_config()
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            return self._get_fallback_config()

    def _get_fallback_config(self) -> dict[str, Any]:
        """Provide fallback configuration if file loading fails"""
        return {
            "character_styles": {
                "Code": {"markdown": "backticks"},
                "Input": {"markdown": "kbd_tag"},
            },
            "paragraph_styles": {
                "Code block": {"markdown": "fenced_code", "default_language": "html"}
            },
            "defaults": {"code_language": "html", "heading_max_level": 6},
        }

    def _convert_run_to_markdown(self, run) -> str:
        """Convert a single run to markdown based on style hierarchy and config"""
        return self.run_formatter.convert_run_to_markdown(run)

    def _log_conversion_stats(self):
        """Log conversion statistics"""
        self.logger.info("=== CONVERSION STATISTICS ===")

        # Character styles
        char_styles = {k: v for k, v in self.style_stats.items() if k.startswith("char_style_")}
        if char_styles:
            self.logger.info("Character styles detected:")
            for style, count in char_styles.items():
                style_name = style.replace("char_style_", "")
                self.logger.info(f"  {style_name}: {count} instances")

        # Paragraph styles
        para_styles = {k: v for k, v in self.style_stats.items() if k.startswith("para_style_")}
        if para_styles:
            self.logger.info("Paragraph styles detected:")
            for style, count in para_styles.items():
                style_name = style.replace("para_style_", "")
                self.logger.info(f"  {style_name}: {count} instances")

        if self.image_counter > 0:
            self.logger.info(f"Images extracted: {self.image_counter}")

    def _smart_join_markdown_parts(self, markdown_parts: list[str]) -> str:
        """Join markdown parts with intelligent spacing.

        List groups already have proper internal spacing, so they should be joined
        with other elements using single spacing to avoid double spacing issues.
        """
        if not markdown_parts:
            return ""

        result_parts = []
        for i, part in enumerate(markdown_parts):
            if not part or not part.strip():
                continue

            # Check if this part is a list (contains list markers)
            is_list = self._is_list_content(part)

            if i == 0:
                # First part - no leading spacing
                result_parts.append(part)
            else:
                # Check if previous part was also a list
                prev_part = markdown_parts[i - 1] if i > 0 else ""
                prev_is_list = self._is_list_content(prev_part)

                if is_list and prev_is_list:
                    # Both are lists - use single newline to avoid extra spacing
                    result_parts.append("\n" + part)
                else:
                    # Standard spacing between different element types
                    result_parts.append("\n\n" + part)

        return "".join(result_parts)

    def _is_list_content(self, content: str) -> bool:
        """Check if content appears to be a list group."""
        if not content:
            return False
        lines = content.strip().split("\n")
        # Check if any line starts with list markers
        for line in lines:
            stripped = line.strip()
            if (
                stripped.startswith("- ")
                or stripped.startswith("* ")
                or re.match(r"^\d+\. ", stripped)
            ):
                return True
        return False


def main():
    """Main entry point for the enhanced converter"""
    logger = setup_logging()

    if len(sys.argv) < 3:
        print(
            "Usage: python enhanced_word_converter.py <input.docx> <output.md> "
            "[--extract-images] [--config=path/to/config.yml]"
        )
        return 1

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    extract_images = "--extract-images" in sys.argv

    # Check for custom config path
    config_path = None
    for arg in sys.argv:
        if arg.startswith("--config="):
            config_path = arg.split("=", 1)[1]
            break

    converter = EnhancedWordToMarkdownConverter(logger, config_path)

    success = converter.convert_document(input_path, output_path, extract_images)

    if success:
        print(f"✅ Conversion completed: {output_path}")
        config_lang = converter.config.get("defaults", {}).get("code_language", "html")
        print(f"📋 Configuration used: {config_lang} (default language)")
        if extract_images:
            print("📷 Images extracted to: assets/images/")
        return 0
    else:
        print("❌ Conversion failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

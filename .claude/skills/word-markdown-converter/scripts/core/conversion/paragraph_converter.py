#!/usr/bin/env python3
"""
Paragraph Conversion for Word-to-Markdown Processing.

This module provides intelligent paragraph conversion and formatting for Word documents,
including style detection, list continuation handling, and formatting preservation.

Key Components:
    - ParagraphConverter: Main class for paragraph processing and conversion
    - Style-aware paragraph classification and formatting
    - List continuation and indentation handling
    - Regular paragraph processing with inline formatting

Features:
    - Multi-style paragraph handling (headings, code blocks, lists)
    - Smart list continuation detection
    - Indentation preservation for non-list content
    - Style configuration integration
    - Robust error handling and logging

Dependencies:
    - python-docx: Word document processing
    - re: Pattern matching for style analysis
    - logging: Error and debug logging
"""

import logging
import re
from typing import Any, Dict, Optional

from docx.text.paragraph import Paragraph


class ParagraphConverter:
    """Handles paragraph conversion and formatting for Word documents."""

    def __init__(self, logger: logging.Logger, config: Dict[str, Any]):
        """Initialize the paragraph converter.

        Args:
            logger: Logger instance for error and debug messages
            config: Style configuration dictionary
        """
        self.logger = logger
        self.config = config

    def convert_paragraph(
        self,
        para: Paragraph,
        list_context: Dict[str, Any],
        style_stats: Dict[str, int],
        extract_list_info_func,
        skip_paragraph: Optional[Paragraph] = None,
    ) -> tuple[str, Dict[str, Any]]:
        """Convert a paragraph to markdown with style-aware formatting.

        Args:
            para: The paragraph to convert
            list_context: Current list context state
            style_stats: Style statistics dictionary
            extract_list_info_func: Function to extract list information
            skip_paragraph: Paragraph to skip (e.g., title paragraph)

        Returns:
            Tuple of (markdown_text, updated_list_context)
        """
        # Skip the designated skip paragraph
        if para == skip_paragraph:
            return "", list_context

        # Check if paragraph has images even if text is empty
        has_images = any(run._element.xpath(".//w:drawing") for run in para.runs)

        # Skip empty paragraphs unless they contain images
        if not para.text.strip() and not has_images:
            return "", list_context

        style_name = para.style.name if para.style else "Normal"
        list_info_current = extract_list_info_func(para)

        # Check if this style should be excluded
        if self._should_exclude_paragraph(style_name):
            return "", list_context

        style_stats[f"para_style_{style_name}"] += 1

        # Handle different paragraph types
        if self._is_heading_style(style_name):
            # Reset list context on headings
            updated_context = self._reset_list_context()
            return self._convert_heading(para), updated_context

        elif style_name == "Subtitle":
            updated_context = self._reset_list_context()
            return self._convert_subtitle(para), updated_context

        elif self._is_code_block_style(style_name):
            updated_context = self._reset_list_context()
            return self._convert_code_block(para), updated_context

        elif list_info_current is not None or self._is_list_styled_paragraph(para):
            # Handle list items
            return self._convert_list_item(para, list_context)

        elif self._is_blockquote_by_indent(para):
            # Handle blockquote paragraphs detected by indentation
            return self._convert_blockquote(para, list_context)

        else:
            # Handle regular paragraphs and list continuations
            return self._handle_regular_or_continuation_paragraph(para, list_context)

    def _should_exclude_paragraph(self, style_name: str) -> bool:
        """Check if paragraph style should be excluded from conversion."""
        paragraph_styles = self.config.get("paragraph_styles", {})
        if style_name in paragraph_styles:
            style_config = paragraph_styles[style_name]
            if style_config.get("markdown") == "exclude":
                self.logger.debug(f"Excluding paragraph with style '{style_name}' from conversion")
                return True
        return False

    def _is_heading_style(self, style_name: str) -> bool:
        """Check if style represents a heading."""
        return style_name.startswith("Heading") or style_name == "Title"

    def _is_code_block_style(self, style_name: str) -> bool:
        """Check if style represents a code block."""
        return style_name == "Code block" or "code" in style_name.lower()

    def _is_blockquote_by_indent(self, para: Paragraph) -> bool:
        """Check if paragraph is a blockquote based on indentation level.

        Blockquotes are detected by indentation (typically 0.5" or 457200 EMUs from Pandoc).
        We exclude list items which have their own numbering/bullets.

        Args:
            para: Paragraph to check

        Returns:
            True if paragraph appears to be a blockquote based on indentation
        """
        try:
            left_indent = para.paragraph_format.left_indent
            if left_indent is None:
                return False

            indent_emus = int(left_indent)

            # Standard blockquote indent is around 0.5" (457200 EMUs)
            # Accept range of 228600-685800 EMUs (0.25" to 0.75") to handle variations
            # Note: python-docx uses EMUs (914400 EMUs = 1 inch), not twips
            if 228600 <= indent_emus <= 685800:
                # Exclude list items - they have numbering properties in XML
                if para._element.xpath(".//w:numPr"):
                    return False

                # Exclude paragraphs with list-related styles
                style_name = para.style.name if para.style else ""
                if "List" in style_name:
                    return False

                return True

        except Exception:
            return False

        return False

    def _is_list_styled_paragraph(self, para: Paragraph) -> bool:
        """Check if paragraph has list styling."""
        return para.style and (
            ("List" in (para.style.name or ""))
            or (para.style.base_style and "List" in (para.style.base_style.name or ""))
        )

    def _reset_list_context(self) -> Dict[str, Any]:
        """Reset list context for non-list elements."""
        return {"last_was_list_item": False, "last_list_level": 0, "last_list_indent": None}

    def _convert_heading(self, para: Paragraph) -> str:
        """Convert heading paragraphs to markdown headers using config."""
        style_name = para.style.name
        paragraph_styles = self.config.get("paragraph_styles", {})
        heading_level = 1

        if style_name in paragraph_styles and "level" in paragraph_styles[style_name]:
            heading_level = paragraph_styles[style_name]["level"]
        elif "Heading" in style_name:
            level_match = re.search(r"(\d+)", style_name)
            if level_match:
                max_level = self.config.get("defaults", {}).get("heading_max_level", 6)
                heading_level = min(int(level_match.group(1)), max_level)

        if style_name == "Title":
            heading_level = 1

        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs)
            # Replace line breaks with spaces to keep heading on single line
            text_content = text_content.replace("\n", " ").strip()
        else:
            text_content = para.text.strip()

        heading_prefix = "#" * heading_level
        return f"{heading_prefix} {text_content}"

    def _convert_subtitle(self, para: Paragraph) -> str:
        """Convert subtitle to markdown."""
        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs)
        else:
            text_content = para.text.strip()

        # Apply italic formatting for subtitle
        return f"*{text_content}*"

    def _convert_blockquote(
        self, para: Paragraph, list_context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Convert blockquote paragraph to markdown blockquote syntax.

        Blockquotes are now detected by indentation level rather than style name.
        Supports both standalone blockquotes and blockquotes nested within lists.

        Args:
            para: The indented paragraph to convert as blockquote
            list_context: Current list context state

        Returns:
            Tuple of (markdown_text, updated_list_context)
        """
        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs).strip()
        else:
            text_content = para.text.strip()

        # Check if blockquote is nested in a list (continuation of list item)
        last_was_list_item = list_context.get("last_was_list_item", False)
        last_list_level = list_context.get("last_list_level", 0)

        if last_was_list_item:
            # Indent blockquote to align with list item
            indent = "    " * (last_list_level + 1)
            markdown_text = f"{indent}> {text_content}"
            # Maintain list context for subsequent blockquotes or content
            return markdown_text, list_context
        else:
            # Standalone blockquote
            markdown_text = f"> {text_content}"
            # Reset list context for standalone blockquotes
            updated_context = self._reset_list_context()
            return markdown_text, updated_context

    def _convert_code_block(self, para: Paragraph) -> str:
        """Convert code block paragraph to markdown.

        Delegates to CodeProcessor for consistent language detection,
        run formatting, and escaping logic matching multi-block processing.
        """
        # Delegate to CodeProcessor for proper language detection and formatting
        if (
            hasattr(self, "_parent_converter")
            and self._parent_converter
            and hasattr(self._parent_converter, "code_processor")
            and self._parent_converter.code_processor
        ):
            return self._parent_converter.code_processor.convert_code_block(para)

        # Fallback if no parent converter available (shouldn't happen in normal usage)
        self.logger.warning("CodeProcessor unavailable, using fallback code block conversion")
        return f"```\n{para.text}\n```"

    def _convert_list_item(
        self, para: Paragraph, list_context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Convert list item paragraph."""
        # This would delegate to ListConverter when that's extracted
        # For now, return simple bullet point and update context
        updated_context = list_context.copy()
        updated_context["last_was_list_item"] = True
        updated_context["last_list_level"] = 0  # Simplified
        return f"- {para.text.strip()}", updated_context

    def _handle_regular_or_continuation_paragraph(
        self, para: Paragraph, list_context: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Handle regular paragraphs and list continuation logic."""
        try:
            left_indent = para.paragraph_format.left_indent
            left_val = int(left_indent) if left_indent is not None else 0
            last_val = int(list_context.get("last_list_indent") or 0)
        except Exception:
            left_val = 0
            last_val = 0

        style_name = para.style.name if para.style else "Normal"
        last_was_list_item = list_context.get("last_was_list_item", False)
        last_list_level = list_context.get("last_list_level", 0)

        # Continuation heuristics
        if last_was_list_item:
            # Special case: fallback bullet for deep lists
            if last_list_level >= 1 and (style_name == "List Paragraph" or left_val >= last_val):
                parent_level = max(0, last_list_level - 1)
                return self._convert_fallback_bullet(para, parent_level), list_context

            # List continuation block
            elif style_name == "List Paragraph" or left_val > last_val:
                return (
                    self._convert_list_continuation_paragraph(para, last_list_level),
                    list_context,
                )

            else:
                # Normal paragraph after list - reset context
                updated_context = self._reset_list_context()
                return self._convert_regular_paragraph(para), updated_context
        else:
            # Reset list context for normal paragraphs
            updated_context = self._reset_list_context()
            if left_val > 0:
                return self._convert_indented_paragraph(para, left_val), updated_context
            return self._convert_regular_paragraph(para), updated_context

    def _convert_fallback_bullet(self, para: Paragraph, level: int) -> str:
        """Convert to fallback bullet point at specified level - respects style_map.yml."""
        indent = "    " * level

        # Check style configuration to determine marker type
        style_name = para.style.name if para.style else "Normal"
        paragraph_styles = self.config.get("paragraph_styles", {})

        if style_name in paragraph_styles:
            style_config = paragraph_styles[style_name]
            if style_config.get("markdown") == "numbered_list":
                marker = style_config.get("marker", "1.")
            else:
                marker = style_config.get("marker", "-")
        else:
            marker = "-"  # Default to bullets

        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs).strip()
        else:
            text_content = para.text.strip()
        return f"{indent}{marker} {text_content}"

    def _convert_list_continuation_paragraph(self, para: Paragraph, list_level: int) -> str:
        """Convert paragraph as list continuation."""
        indent = "    " * (list_level + 1)
        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs).strip()
        else:
            text_content = para.text.strip()
        return f"{indent}{text_content}"

    def _convert_indented_paragraph(self, para: Paragraph, left_val: int) -> str:
        """Convert indented paragraph preserving indentation."""
        # Convert twips to spaces (720 twips = 1 inch, ~4 spaces per indent level)
        # Cap excessive indentation to prevent invisible text in markdown
        margin_left = left_val // 720  # Convert to approximate spaces

        # If indentation is excessive (>10 spaces), treat as block quote instead
        # This handles template examples that are heavily indented in Word for visual effect
        if margin_left > 10:
            # Convert runs for inline formatting
            if hasattr(self, "_parent_converter") and self._parent_converter:
                text_content = self._parent_converter._convert_paragraph_runs(para.runs).strip()
            else:
                text_content = para.text.strip()
            # Use blockquote for heavily indented content
            return f"> {text_content}"

        indent = "  " * max(1, margin_left)
        # Convert runs for inline formatting
        if hasattr(self, "_parent_converter") and self._parent_converter:
            text_content = self._parent_converter._convert_paragraph_runs(para.runs).strip()
        else:
            text_content = para.text.strip()
        return f"{indent}{text_content}"

    def _convert_regular_paragraph(self, para: Paragraph) -> str:
        """Convert regular paragraph with proper run formatting."""
        # Delegate to the main converter's run processing logic
        # This ensures character styles are properly handled
        if hasattr(self, "_parent_converter") and self._parent_converter:
            return self._parent_converter._convert_paragraph_runs(para.runs)
        else:
            # Fallback to simple text if converter not available
            return para.text.strip()

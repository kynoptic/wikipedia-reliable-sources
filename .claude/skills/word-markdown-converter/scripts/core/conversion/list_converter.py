#!/usr/bin/env python3
"""
List Processing and Conversion for Word-to-Markdown Processing.

This module provides intelligent list detection, conversion, and formatting for Word documents,
including numbered/bulleted list detection, nesting, and markdown formatting.

Key Components:
    - ListConverter: Main class for list processing and conversion
    - List type detection (numbered vs bulleted)
    - List nesting and indentation handling
    - List continuation paragraph processing
    - Smart list item classification

Features:
    - Advanced list type heuristics using Word numbering properties
    - Context-aware list item vs paragraph classification
    - Explanatory text detection to avoid false list items
    - Support for multi-level nested lists
    - List group processing for consecutive items

Dependencies:
    - python-docx: Word document processing
    - re: Pattern matching for content analysis
    - logging: Error and debug logging
"""

import logging
import re
from typing import List, Optional

from docx.text.paragraph import Paragraph


class ListConverter:
    """Handles list detection, processing, and conversion for Word documents."""

    def __init__(self, logger: logging.Logger, config: dict = None):
        """Initialize the list converter.

        Args:
            logger: Logger instance for error and debug messages
            config: Configuration dictionary for defaults and settings
        """
        self.logger = logger
        self.config = config or {}
        self._hyperlink_converter = None
        self._run_converter = None

    def set_converters(self, hyperlink_converter, run_converter):
        """Set the converter functions for hyperlinks and runs.

        Args:
            hyperlink_converter: Function to convert paragraph elements with hyperlinks
            run_converter: Function to convert paragraph runs
        """
        self._hyperlink_converter = hyperlink_converter
        self._run_converter = run_converter

    def convert_list_item_group(self, list_paragraphs: List[Paragraph]) -> str:
        """Convert a group of consecutive list items to markdown.

        Args:
            list_paragraphs: List of consecutive list item paragraphs

        Returns:
            Markdown string for the list group
        """
        if not list_paragraphs:
            return ""

        markdown_parts = []
        for para in list_paragraphs:
            item_markdown = self.convert_list_item(para)
            if item_markdown and item_markdown.strip():
                markdown_parts.append(item_markdown)

        # Join list items with double newlines (loose list format) to match golden fixtures
        return "\n\n".join(markdown_parts)

    def convert_list_item(self, para: Paragraph) -> str:
        """Convert list items to markdown list format with proper numbering and nesting.

        Args:
            para: The paragraph to convert as a list item

        Returns:
            Markdown string for the list item
        """
        # Check for hyperlinks first
        paragraph_element = para._element
        hyperlinks = paragraph_element.xpath(".//w:hyperlink")

        if hyperlinks:
            self.logger.debug(f"List item has {len(hyperlinks)} hyperlinks")
            text_content = self._convert_paragraph_with_hyperlinks(paragraph_element)
        else:
            text_content = self._convert_paragraph_runs(para.runs)

        # Extract numbering information
        list_info = self._extract_list_info(para)

        # Check if this is explanatory text that shouldn't be a list
        if self._is_explanatory_text(text_content, para):
            return text_content  # Return as regular paragraph

        # Process as list item
        if list_info:
            numId, ilvl = list_info
            is_numbered = self.is_numbered_list(para, numId, ilvl)

            # Create list marker
            if is_numbered:
                marker = "1."  # Markdown auto-numbers
            else:
                marker = "-"

            # Handle nesting - use 4 spaces per level for proper markdown rendering
            indent = "    " * ilvl if ilvl > 0 else ""

            return f"{indent}{marker} {text_content.strip()}"
        else:
            # Fallback for lists without proper numbering - check style_map.yml
            style_name = para.style.name if para.style else "Normal"
            paragraph_styles = self.config.get("paragraph_styles", {})

            # Check if this style is configured in style_map.yml
            if style_name in paragraph_styles:
                style_config = paragraph_styles[style_name]
                if style_config.get("markdown") == "numbered_list":
                    marker = style_config.get("marker", "1.")
                else:
                    marker = style_config.get("marker", "-")
            else:
                # Use default marker if style not in config
                marker = self.config.get("defaults", {}).get("list_marker", "-")

            return f"{marker} {text_content.strip()}"

    def is_numbered_list(self, para: Paragraph, numId: int, ilvl: int) -> bool:
        """Heuristic to determine if a list is numbered or bulleted.

        Args:
            para: The paragraph to analyze
            numId: Numbering ID from Word
            ilvl: Indentation level

        Returns:
            True if numbered list, False if bulleted
        """
        # Strategy 1: Check style name
        style_name = para.style.name if para.style else ""
        if "Number" in style_name:
            return True
        if "Bullet" in style_name:
            return False

        # Strategy 2: Check numbering format from document
        try:
            doc_part = para.part
            if hasattr(doc_part, "numbering_part") and doc_part.numbering_part:
                numbering_part = doc_part.numbering_part

                # Find the num element with our numId
                for num_elem in numbering_part.element.xpath("//w:num"):
                    num_id_attr = num_elem.get(
                        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId"
                    )
                    if num_id_attr == str(numId):
                        # Get the abstractNumId
                        abstract_num_id_elem = num_elem.xpath(".//w:abstractNumId")
                        if abstract_num_id_elem:
                            abstract_id = abstract_num_id_elem[0].get(
                                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                            )

                            # Find the abstractNum with this ID
                            return self._check_abstract_num_format(
                                numbering_part, abstract_id, ilvl
                            )

        except Exception as e:
            self.logger.debug(f"Error checking numbering format: {e}")

        # Strategy 3: Check content context
        if self._has_numbered_context(para):
            return True

        # Default to bullets for safety
        return False

    def _check_abstract_num_format(self, numbering_part, abstract_id: str, ilvl: int) -> bool:
        """Check abstract numbering format for numbered vs bullet detection."""
        try:
            for abstract_num in numbering_part.element.xpath("//w:abstractNum"):
                abstract_num_id = abstract_num.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}abstractNumId"
                )
                if abstract_num_id == abstract_id:
                    # Check the number format at this level
                    for child in abstract_num:
                        if child.tag.endswith("}lvl"):
                            level_ilvl = child.get(
                                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl"
                            )
                            if level_ilvl == str(ilvl):
                                # Get the number format
                                for fmt_child in child:
                                    if fmt_child.tag.endswith("}numFmt"):
                                        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"  # noqa: E501
                                        fmt_val = fmt_child.get(f"{ns}val")
                                        if fmt_val in [
                                            "decimal",
                                            "upperRoman",
                                            "lowerRoman",
                                            "upperLetter",
                                            "lowerLetter",
                                        ]:
                                            return True
                                        elif fmt_val == "bullet":
                                            return False
        except Exception as e:
            self.logger.debug(f"Error checking abstract num format: {e}")

        return False

    def _has_numbered_context(self, para: Paragraph) -> bool:
        """Check if paragraph context suggests numbered list."""
        numbered_context_phrases = [
            "step",
            "steps",
            "first",
            "second",
            "third",
            "next",
            "then",
            "finally",
            "procedure",
            "sequence",
        ]

        try:
            doc_paragraphs = para._parent.paragraphs if hasattr(para, "_parent") else []
            para_index = list(doc_paragraphs).index(para) if para in doc_paragraphs else -1

            if para_index > 0:
                # Look at preceding paragraphs for context clues
                for i in range(max(0, para_index - 3), para_index):
                    prev_text = doc_paragraphs[i].text.strip().lower()
                    if any(phrase in prev_text for phrase in numbered_context_phrases):
                        return True
        except Exception as e:
            self.logger.debug(f"Error checking numbered context: {e}")

        return False

    def _is_explanatory_text(self, text_content: str, para: Paragraph) -> bool:
        """Check if text is explanatory rather than a true list item.

        Args:
            text_content: The text content to analyze
            para: The paragraph object

        Returns:
            True if text appears to be explanatory
        """
        # FIRST: Check if paragraph has explicit list formatting
        # If it does, it's a list item regardless of content heuristics
        has_list_formatting = (
            self._extract_list_info(para) is not None
            or (para.style and "List" in (para.style.name or ""))
        )

        if has_list_formatting:
            self.logger.debug("Paragraph has explicit list formatting - treating as list item")
            return False

        # THEN: Apply content-based heuristics for paragraphs without list formatting
        text_lower = text_content.lower()

        # Explanatory keywords with word boundaries
        explanatory_keywords = [
            r"\bprovides\b",
            r"\bprovide\b",
            r"\bexplains\b",
            r"\bexplain\b",
            r"\bdescribes\b",
            r"\bensures\b",
            r"\bensure\b",
            r"\bdeveloped\b",
            r"\bhelps\b",
            r"\bhelp\b",
            r"\ballows\b",
            r"\ballow\b",
            r"\benables\b",
            r"\benable\b",
            r"\bcaptures\b",
            r"\bcapture\b",
            r"\bidentifies\b",
            r"\bidentify\b",
            r"\bdefines\b",
            r"\bdefine\b",
            r"\bthis word list\b",
            r"\bthe word list\b",
            r"\bthis list\b",
            r"\bthis guide\b",
        ]

        # Check for explanatory patterns
        for keyword in explanatory_keywords:
            if re.search(keyword, text_lower):
                self.logger.debug(f"Found explanatory keyword: {keyword}")
                return True

        # Check for definition-style content
        if self._is_definition_style(text_content):
            return True

        # Long sentences are often explanatory
        if len(text_content.split()) > 25:
            self.logger.debug("Long sentence without list formatting - likely explanatory")
            return True

        return False

    def _is_definition_style(self, text_content: str) -> bool:
        """Check if content follows definition-style patterns."""
        definition_patterns = [
            r"^[A-Z][a-z]+ (is|are|means|refers to)",
            r"^The .+ (is|are|means|refers to)",
            r"^This .+ (is|are|means|refers to)",
        ]

        for pattern in definition_patterns:
            if re.search(pattern, text_content):
                return True

        return False

    def _extract_list_info(self, para: Paragraph) -> Optional[tuple[int, int]]:
        """Extract list numbering information from paragraph.

        Args:
            para: The paragraph to analyze

        Returns:
            Tuple of (numId, ilvl) or None if not a list item
        """
        try:
            # Check for numbering properties
            numPr = para._element.find(".//w:numPr", para._element.nsmap)
            if numPr is not None:
                numId_elem = numPr.find(".//w:numId", para._element.nsmap)
                ilvl_elem = numPr.find(".//w:ilvl", para._element.nsmap)

                if numId_elem is not None and ilvl_elem is not None:
                    numId = int(
                        numId_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        )
                    )
                    ilvl = int(
                        ilvl_elem.get(
                            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val"
                        )
                    )
                    return (numId, ilvl)
        except Exception as e:
            self.logger.debug(f"Error extracting list info: {e}")

        return None

    def _convert_paragraph_with_hyperlinks(self, paragraph_element) -> str:
        """Convert paragraph with hyperlinks - delegates to main converter."""
        if self._hyperlink_converter:
            return self._hyperlink_converter(paragraph_element)
        # Fallback to simple text extraction
        return paragraph_element.text or ""

    def _convert_paragraph_runs(self, runs) -> str:
        """Convert paragraph runs - delegates to main converter."""
        if self._run_converter:
            return self._run_converter(runs)
        # Fallback to simple text concatenation
        return "".join(run.text for run in runs if run.text)

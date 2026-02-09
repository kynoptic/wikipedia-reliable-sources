#!/usr/bin/env python3
"""
Code Block Processing for Word-to-Markdown Conversion.

This module provides comprehensive code block detection, grouping, and conversion
for Word documents, including language detection and fenced code block formatting.

Key Components:
    - CodeProcessor: Main class for code block processing and conversion
    - Language detection based on content patterns
    - Code block grouping for consecutive blocks
    - Fenced code block formatting with language hints
    - Configuration-driven language mapping

Features:
    - Advanced code language detection using pattern matching
    - Support for consecutive code block grouping
    - Configurable language patterns and exclusion rules
    - Fenced code block generation with proper escaping
    - HTML, CSS, JavaScript, and other language detection
    - Fallback language configuration support

Dependencies:
    - python-docx: Word document processing
    - re: Pattern matching for language detection
    - logging: Error and debug logging
"""

import logging
from typing import Dict, List

from docx.text.paragraph import Paragraph


class CodeProcessor:
    """Handles code block detection, processing, and conversion for Word documents."""

    def __init__(self, logger: logging.Logger, config: dict = None):
        """Initialize the code processor.

        Args:
            logger: Logger instance for error and debug messages
            config: Configuration dictionary for language detection and defaults
        """
        self.logger = logger
        self.config = config or {}

    def convert_code_block(self, para: Paragraph) -> str:
        """Convert code block paragraphs to fenced code blocks using config.

        Note: This method handles individual code blocks. For consecutive blocks,
        use convert_code_block_group() to handle them as a unit.

        Args:
            para: The paragraph to convert as a code block

        Returns:
            Fenced code block markdown string
        """
        text = self._get_paragraph_text(para)
        if not text.strip():
            return ""

        # Get language from config or detect it
        code_languages = self.config.get("code_languages", {})
        default_language = self.config.get("defaults", {}).get("code_language", "html")

        detected_language = self._detect_code_language(text, code_languages, default_language)

        return f"```{detected_language}\n{text}\n```"

    def convert_code_block_group(self, code_paragraphs: List[Paragraph]) -> str:
        """Convert a group of consecutive 'Code block' paragraphs into a single fenced block.

        Args:
            code_paragraphs: List of consecutive code block paragraphs

        Returns:
            Single fenced code block containing all text
        """
        if not code_paragraphs:
            return ""

        # Collect all text from the group
        all_text = []
        for paragraph in code_paragraphs:
            text = self._get_paragraph_text(paragraph)
            if text.strip():  # Only add non-empty lines
                all_text.append(text)

        if not all_text:
            return ""

        # Combine all text
        combined_text = "\n".join(all_text)

        # Detect language from the combined text
        code_languages = self.config.get("code_languages", {})
        default_language = self.config.get("defaults", {}).get("code_language", "html")
        detected_language = self._detect_code_language(
            combined_text, code_languages, default_language
        )

        return f"```{detected_language}\n{combined_text}\n```"

    def _detect_code_language(
        self, code_text: str, code_languages: Dict = None, default_language: str = "html"
    ) -> str:
        """Detect programming language from code content using config patterns.

        Args:
            code_text: The code text to analyze
            code_languages: Language pattern configuration
            default_language: Fallback language if detection fails

        Returns:
            Detected language identifier
        """
        code_lower = code_text.lower().strip()

        if code_languages is None:
            code_languages = self.config.get("code_languages", {})

        # Check each language pattern from config
        for language, rules in code_languages.items():
            patterns = rules.get("patterns", [])
            exclude_starts_with = rules.get("exclude_starts_with", [])

            # Check exclusion rules first
            if exclude_starts_with and any(
                code_lower.startswith(exclude) for exclude in exclude_starts_with
            ):
                continue

            # Check if any pattern matches
            if any(pattern in code_lower for pattern in patterns):
                return language

        # Return provided default or config default
        return default_language or self.config.get("defaults", {}).get("code_language", "html")

    def _get_paragraph_text(self, para: Paragraph) -> str:
        """Get plain text from paragraph.

        Args:
            para: The paragraph to extract text from

        Returns:
            Plain text content
        """
        return para.text

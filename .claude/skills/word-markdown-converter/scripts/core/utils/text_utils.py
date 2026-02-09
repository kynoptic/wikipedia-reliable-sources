#!/usr/bin/env python3
"""
Text Processing Utilities for Word-to-Markdown Conversion.

This module provides lightweight text processing functions extracted from
the main converter to reduce complexity and improve maintainability.
Part of the NOW phase quick wins to reduce converter complexity by 200 lines.

Functions:
    - sanitize_filename: Safe filename generation from document titles
    - escape_markdown_chars: Escape special markdown characters in text
    - normalize_whitespace: Clean up whitespace and formatting
    - extract_text_content: Safely extract text from various objects
    - is_empty_content: Check if content is effectively empty
    - format_heading_text: Clean and format heading text
"""

import re
from typing import Any


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Convert text to a safe filename by removing/replacing problematic characters.

    Args:
        text: Input text to sanitize
        max_length: Maximum length for resulting filename

    Returns:
        Safe filename string
    """
    if not text or not text.strip():
        return "untitled"

    # Remove or replace problematic characters
    safe_text = re.sub(r'[<>:"/\\|?*]', "", text)
    safe_text = re.sub(r"\s+", "_", safe_text.strip())
    safe_text = re.sub(r"[^\w\-_.]", "", safe_text)

    # Limit length and ensure it doesn't end with a dot
    safe_text = safe_text[:max_length].rstrip(".")

    return safe_text if safe_text else "untitled"


def escape_markdown_chars(text: str) -> str:
    """
    Escape special markdown characters to prevent formatting issues.

    Args:
        text: Text that may contain markdown special characters

    Returns:
        Text with markdown characters properly escaped
    """
    if not text:
        return text

    # Characters that need escaping in markdown
    escape_chars = {
        "\\": "\\\\",
        "`": "\\`",
        "*": "\\*",
        "_": "\\_",
        "[": "\\[",
        "]": "\\]",
        "(": "\\(",
        ")": "\\)",
        "#": "\\#",
        "+": "\\+",
        "-": "\\-",
        ".": "\\.",
        "!": "\\!",
        "|": "\\|",
    }

    for char, escaped in escape_chars.items():
        text = text.replace(char, escaped)

    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text - collapse multiple spaces, trim, etc.

    Args:
        text: Text to normalize

    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""

    # Replace various whitespace with regular spaces
    text = re.sub(r"[\t\n\r\f\v]", " ", text)

    # Collapse multiple spaces into single space
    text = re.sub(r" +", " ", text)

    # Trim leading/trailing whitespace
    return text.strip()


def extract_text_content(obj: Any) -> str:
    """
    Safely extract text content from various object types.

    Args:
        obj: Object that may have text content (paragraph, run, etc.)

    Returns:
        Extracted text or empty string if not available
    """
    if obj is None:
        return ""

    # Try different ways to get text content
    if hasattr(obj, "text"):
        return str(obj.text) if obj.text is not None else ""
    elif hasattr(obj, "getText"):
        return str(obj.getText()) if obj.getText() is not None else ""
    elif isinstance(obj, str):
        return obj
    else:
        return str(obj) if obj is not None else ""


def is_empty_content(text: str) -> bool:
    """
    Check if text content is effectively empty (whitespace, special chars only).

    Args:
        text: Text to check

    Returns:
        True if content is effectively empty
    """
    if not text:
        return True

    # Remove common "empty" characters and check if anything remains
    cleaned = re.sub(r"[\s\u00A0\u2000-\u200F\u2028-\u202F\u205F\u3000]", "", text)
    cleaned = re.sub(r"[^\w\d]", "", cleaned)

    return len(cleaned.strip()) == 0


def format_heading_text(text: str) -> str:
    """
    Clean and format text for use as heading content.

    Args:
        text: Raw heading text

    Returns:
        Cleaned heading text suitable for markdown
    """
    if not text:
        return ""

    # Normalize whitespace first
    text = normalize_whitespace(text)

    # Remove leading/trailing punctuation that doesn't belong in headings
    text = re.sub(r"^[^\w\d]+", "", text)
    text = re.sub(r"[^\w\d\s\-()]+$", "", text)

    # Ensure reasonable length for headings
    if len(text) > 100:
        text = text[:97] + "..."

    return text.strip()


def clean_style_name(style_name: str) -> str:
    """
    Clean and normalize Word style names for mapping.

    Args:
        style_name: Raw style name from Word document

    Returns:
        Cleaned style name for use in mappings
    """
    if not style_name:
        return "Normal"

    # Remove common prefixes/suffixes that vary
    cleaned = re.sub(r"\s*(Char|Character)\s*$", "", style_name)
    cleaned = re.sub(r"^\s*(List|Heading)\s*", "", cleaned)

    # Normalize whitespace and casing
    cleaned = normalize_whitespace(cleaned)

    return cleaned if cleaned else "Normal"


def truncate_with_ellipsis(text: str, max_length: int) -> str:
    """
    Truncate text to maximum length, adding ellipsis if needed.

    Args:
        text: Text to potentially truncate
        max_length: Maximum allowed length

    Returns:
        Text truncated with ellipsis if necessary
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."

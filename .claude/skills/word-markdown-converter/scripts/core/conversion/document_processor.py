#!/usr/bin/env python3
"""
Document Element Processing for Word-to-Markdown Conversion.

This module provides document element ordering, grouping, and preprocessing
functionality to maintain proper document structure during conversion.

Key Components:
    - DocumentProcessor: Main class for element processing and grouping
    - Element ordering preservation from Word document structure
    - Consecutive element grouping for improved output formatting
    - List item detection and processing support

Features:
    - Document element ordering maintenance
    - Consecutive code block grouping
    - Consecutive list item grouping for spacing control
    - Element type detection and classification
    - Robust element property inspection

Dependencies:
    - python-docx: Word document processing
    - logging: Error and debug logging
"""

import logging
from typing import Any

from docx import Document


class DocumentProcessor:
    """Handles document element processing and grouping for conversion."""

    def __init__(self, logger: logging.Logger):
        """Initialize the document processor.

        Args:
            logger: Logger instance for error and debug messages
        """
        self.logger = logger

    def get_processed_elements(self, doc: Document) -> list:
        """Get processed document elements with proper ordering and grouping.

        Args:
            doc: The Word document to process

        Returns:
            List of processed elements ready for conversion
        """
        # Get elements in document order
        elements = self._get_document_elements_in_order(doc)

        # Group consecutive code blocks
        grouped_elements = self._group_consecutive_code_blocks(elements)

        # Group consecutive list items to avoid double spacing
        grouped_elements = self._group_consecutive_list_items(grouped_elements)

        return grouped_elements

    def _get_document_elements_in_order(self, doc: Document) -> list:
        """Get document elements (paragraphs and tables) in correct document flow order.

        This method uses a dictionary-based O(n) algorithm to map XML elements to
        their corresponding document objects, avoiding the O(n²) nested loop approach.

        Args:
            doc: The Word document to process

        Returns:
            List of elements in document order
        """
        # Build a mapping from XML element to document object
        # This is O(n) where n is the number of paragraphs + tables
        element_to_object = {}

        # Map paragraph XML elements to paragraph objects
        for para in doc.paragraphs:
            element_to_object[para._element] = para

        # Map table XML elements to table objects
        for table in doc.tables:
            element_to_object[table._element] = table

        # Access the document body element tree to maintain proper ordering
        body = doc.element.body
        elements = []

        # Process each child element of the document body
        # This is O(m) where m is the number of body elements
        for element in body:
            tag_name = element.tag.split("}")[-1] if "}" in element.tag else element.tag

            # Only process paragraphs and tables
            if tag_name in ("p", "tbl"):
                # O(1) dictionary lookup instead of O(n) list scan
                doc_object = element_to_object.get(element)
                if doc_object is not None:
                    elements.append(doc_object)
            # Skip other elements like section properties, etc.

        return elements

    def _group_consecutive_code_blocks(self, document_elements: list) -> list:
        """Group consecutive 'Code block' paragraphs into single units for coalescence.

        Args:
            document_elements: List of paragraphs and tables from document

        Returns:
            List where consecutive code blocks are grouped into sublists
        """
        grouped = []
        current_code_group = []

        for element in document_elements:
            if hasattr(element, "style") and element.style and element.style.name == "Code block":
                current_code_group.append(element)
            else:
                # End of consecutive code blocks
                if current_code_group:
                    if len(current_code_group) == 1:
                        # Single code block, add as-is
                        grouped.append(current_code_group[0])
                    else:
                        # Multiple consecutive code blocks, add as group
                        grouped.append(current_code_group)
                    current_code_group = []
                grouped.append(element)

        # Handle trailing code blocks
        if current_code_group:
            if len(current_code_group) == 1:
                grouped.append(current_code_group[0])
            else:
                grouped.append(current_code_group)

        return grouped

    def _group_consecutive_list_items(self, document_elements: list) -> list:
        """Group consecutive list items to avoid double spacing between them.

        Args:
            document_elements: List of paragraphs, tables, and grouped elements

        Returns:
            List where consecutive list items are grouped into sublists
        """
        grouped = []
        current_list_group = []

        for element in document_elements:
            # Check if this element is a list item
            is_list_item = self._is_element_list_item(element)

            if is_list_item:
                current_list_group.append(element)
            else:
                # End of consecutive list items
                if current_list_group:
                    # Always group list items (even single ones) to ensure consistent formatting
                    grouped.append(current_list_group)
                    current_list_group = []
                grouped.append(element)

        # Handle trailing list items
        if current_list_group:
            # Always group list items (even single ones) to ensure consistent formatting
            grouped.append(current_list_group)

        return grouped

    def _is_element_list_item(self, element: Any) -> bool:
        """Check if an element is a list item by examining its properties.

        Args:
            element: The element to check

        Returns:
            True if element is a list item
        """
        if not hasattr(element, "_element"):
            return False

        # Exclude Table objects - they should not be treated as list items
        if hasattr(element, "rows"):  # Table objects have a 'rows' attribute
            return False

        # Check for numbering properties that indicate a list item
        try:
            numPr = element._element.find(".//w:numPr", element._element.nsmap)
            if numPr is not None:
                return True
        except Exception as e:
            self.logger.debug(f"Error checking numbering properties: {e}")

        # Check style name for list patterns
        if hasattr(element, "style") and element.style:
            style_name = element.style.name
            if style_name and "List" in style_name:
                return True

        return False

#!/usr/bin/env python3
"""
Table Processing and Conversion for Word-to-Markdown Processing.

This module provides intelligent table detection, conversion, and formatting for Word documents,
including markdown table generation, merged cell detection, and HTML fallback handling.

Key Components:
    - TableConverter: Main class for table processing and conversion
    - Markdown table generation with pipe formatting
    - Merged cell detection and HTML fallback
    - Table cell content processing with run formatting
    - Header row detection and separator generation

Features:
    - Advanced table structure analysis and conversion
    - Context-aware markdown vs HTML table selection
    - Cell content processing with inline formatting
    - Support for complex table structures with merged cells
    - Intelligent header row detection
    - List context indentation for tables under list items

Dependencies:
    - python-docx: Word document processing
    - lxml: XML processing for table structure analysis
    - logging: Error and debug logging
"""

import logging

from docx.table import Table


class TableConverter:
    """Handles table detection, processing, and conversion for Word documents."""

    def __init__(self, logger: logging.Logger, config: dict = None):
        """Initialize the table converter.

        Args:
            logger: Logger instance for error and debug messages
            config: Configuration dictionary for defaults and settings
        """
        self.logger = logger
        self.config = config or {}
        self._run_converter = None

    def set_converters(self, run_converter):
        """Set the converter function for paragraph runs.

        Args:
            run_converter: Function to convert paragraph runs
        """
        self._run_converter = run_converter

    def convert_table(self, table: Table) -> str:
        """Convert Word tables to markdown pipe tables or HTML for merged cells.

        Detects merged cells before conversion. If merged cells are present,
        uses HTML format with rowspan/colspan attributes to preserve structure.
        Otherwise, uses markdown pipe table format.

        Args:
            table: The Word table to convert

        Returns:
            Markdown or HTML string for the table
        """
        if not table.rows:
            return ""

        # Detect merged cells before attempting markdown conversion
        has_merged_cells = self._detect_merged_cells(table)

        if has_merged_cells:
            self.logger.warning(
                "Table contains merged cells - using HTML format to preserve structure"
            )
            return self._convert_table_to_html(table)

        # No merged cells - use markdown pipe table format
        try:
            return self._convert_table_to_markdown(table)
        except Exception as e:
            self.logger.warning(f"Markdown table conversion failed (fallback to HTML): {e}")
            return self._convert_table_to_html(table)

    def indent_table_under_list(self, table_content: str, list_level: int) -> str:
        """Indent a table to appear under a list item at the specified level.

        Args:
            table_content: The table content to indent
            list_level: The list nesting level

        Returns:
            Indented table content
        """
        if not table_content.strip():
            return table_content

        # Calculate indentation for list continuation (2 spaces per level + 2 for continuation)
        base_indent = "  " * list_level  # Base list indentation
        continuation_indent = base_indent + "  "  # Additional 2 spaces for continuation

        # Split table into lines and indent each line
        lines = table_content.split("\n")
        indented_lines = []

        for line in lines:
            if line.strip():  # Only indent non-empty lines
                indented_lines.append(continuation_indent + line)
            else:
                indented_lines.append(line)  # Preserve empty lines as-is

        return "\n".join(indented_lines)

    def _detect_merged_cells(self, table: Table) -> bool:
        """Detect if table contains merged cells that would break markdown format.

        Args:
            table: The Word table to analyze

        Returns:
            True if merged cells are detected
        """
        try:
            W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            for row in table.rows:
                for cell in row.cells:
                    tc = cell._tc

                    # Get tcPr (table cell properties) element
                    tcPr = tc.find(f"{W_NS}tcPr")
                    if tcPr is None:
                        continue

                    # Check for horizontal merging (gridSpan > 1)
                    grid_span = tcPr.find(f"{W_NS}gridSpan")
                    if grid_span is not None:
                        span_val = grid_span.get(f"{W_NS}val")
                        if span_val and int(span_val) > 1:
                            self.logger.debug(f"Detected horizontal merge: gridSpan={span_val}")
                            return True

                    # Check for vertical merging (vMerge)
                    # vMerge with val="restart" starts a merge, without val continues it
                    v_merge = tcPr.find(f"{W_NS}vMerge")
                    if v_merge is not None:
                        self.logger.debug("Detected vertical merge: vMerge present")
                        return True

        except Exception as e:
            self.logger.debug(f"Error detecting merged cells: {e}")

        return False

    def _convert_table_to_markdown(self, table: Table) -> str:
        """Convert Word table to standard markdown table format.

        Args:
            table: The Word table to convert

        Returns:
            Markdown table string
        """
        try:
            markdown_rows = []

            # Detect header row using heuristics
            header_row_index = self._detect_header_row(table)
            expected_cols = None

            # Process all rows
            for row_idx, row in enumerate(table.rows):
                row_cells = []
                for cell in row.cells:
                    cell_text = self._convert_table_cell_content(cell)
                    row_cells.append(cell_text)

                # Capture expected column count from header
                if row_idx == header_row_index:
                    expected_cols = len(row_cells)

                # Heuristic fix: Some authoring patterns place two logical columns
                # into one physical cell separated by a line break.
                # If the header declares one more column than present in data rows, and the last
                # cell contains a <br>, split the last cell at the first <br> into two cells.
                if expected_cols and len(row_cells) + 1 == expected_cols and row_cells:
                    last = row_cells[-1]
                    if "<br>" in last:
                        left, right = last.split("<br>", 1)
                        row_cells[-1] = left.strip()
                        row_cells.append(right.strip())

                # Format cells: empty cells get spaces, content cells have no padding
                formatted_cells = []
                for cell in row_cells:
                    if cell.strip():
                        formatted_cells.append(cell)
                    else:
                        formatted_cells.append("  ")  # Two spaces for empty cells

                markdown_rows.append("|" + "|".join(formatted_cells) + "|")

                # Add separator after header row
                if row_idx == header_row_index:
                    separators = [" --- " for _ in row_cells]
                    markdown_rows.append("|" + "|".join(separators) + "|")

            return "\n".join(markdown_rows)

        except Exception as e:
            # If markdown table conversion fails, fall back to HTML
            self.logger.warning(f"Markdown table conversion failed: {e}")
            self.logger.info("Falling back to HTML table format")
            return self._convert_table_to_html(table)

    def _detect_header_row(self, table: Table) -> int:
        """Use heuristics to detect which row should be treated as header.

        Args:
            table: The Word table to analyze

        Returns:
            Row index that should be treated as header
        """
        if not table.rows:
            return 0

        # Simple heuristic: first row is usually the header
        # In the future, we could check for bold formatting, different styling, etc.
        return 0

    def _convert_table_to_html(self, table: Table) -> str:
        """Convert Word table to HTML table format to preserve complex structure.

        Args:
            table: The Word table to convert

        Returns:
            HTML table string
        """
        try:
            html_parts = ["<table>"]
            header_row_index = self._detect_header_row(table)
            rendered_cells = set()

            # Add thead if we have more than one row
            if len(table.rows) > 1:
                html_parts.append("  <thead>")
                html_parts.append("    <tr>")
                rendered_cells = self._process_header_row(
                    table, header_row_index, html_parts, rendered_cells
                )
                html_parts.append("    </tr>")
                html_parts.append("  </thead>")

            # Add tbody
            html_parts.append("  <tbody>")
            start_row = header_row_index + 1 if len(table.rows) > 1 else 0
            self._process_data_rows(table, start_row, html_parts, rendered_cells)
            html_parts.append("  </tbody>")
            html_parts.append("</table>")

            return "\n".join(html_parts)

        except Exception as e:
            self.logger.warning(f"HTML table conversion failed: {e}")
            return f"<!-- Table conversion failed: {e} -->"

    def _process_header_row(self, table, header_row_index, html_parts, rendered_cells):
        """Process header row cells and populate html_parts.

        Args:
            table: The Word table
            header_row_index: Index of the header row
            html_parts: List to accumulate HTML output
            rendered_cells: Set to track rendered cell positions

        Returns:
            Updated rendered_cells set
        """
        try:
            header_row = table.rows[header_row_index]
            col_offset = 0
            seen_tcs_in_row = set()

            for cell_idx in range(len(header_row.cells)):
                cell = header_row.cells[cell_idx]
                tc_id = id(cell._tc)

                if tc_id in seen_tcs_in_row:
                    continue
                seen_tcs_in_row.add(tc_id)

                while (header_row_index, col_offset) in rendered_cells:
                    col_offset += 1

                if self._is_merged_continuation_cell(cell):
                    col_offset += 1
                    continue

                cell_content = self._convert_table_cell_content(cell)
                colspan, rowspan = self._get_cell_spans(cell, table, header_row_index, col_offset)

                for r_offset in range(rowspan):
                    for c_offset in range(colspan):
                        rendered_cells.add((header_row_index + r_offset, col_offset + c_offset))

                th_tag = self._build_th_tag(cell_content, colspan, rowspan)
                html_parts.append(f"      {th_tag}")
                col_offset += colspan

        except Exception as e:
            self.logger.debug(f"Error processing header row: {e}")
            html_parts.append("      <th>Column 1</th>")

        return rendered_cells

    def _process_data_rows(self, table, start_row, html_parts, rendered_cells):
        """Process data rows and populate html_parts.

        Args:
            table: The Word table
            start_row: Starting row index
            html_parts: List to accumulate HTML output
            rendered_cells: Set tracking rendered cell positions
        """
        for row_idx in range(start_row, len(table.rows)):
            try:
                row = table.rows[row_idx]
                html_parts.append("    <tr>")
                col_offset = 0
                seen_tcs_in_row = set()

                for cell_idx in range(len(row.cells)):
                    cell = row.cells[cell_idx]
                    tc_id = id(cell._tc)

                    if tc_id in seen_tcs_in_row:
                        continue
                    seen_tcs_in_row.add(tc_id)

                    while (row_idx, col_offset) in rendered_cells:
                        col_offset += 1

                    if self._is_merged_continuation_cell(cell):
                        col_offset += 1
                        continue

                    cell_content = self._convert_table_cell_content(cell)
                    colspan, rowspan = self._get_cell_spans(cell, table, row_idx, col_offset)

                    for r_offset in range(rowspan):
                        for c_offset in range(colspan):
                            rendered_cells.add((row_idx + r_offset, col_offset + c_offset))

                    td_tag = self._build_td_tag(cell_content, colspan, rowspan)
                    html_parts.append(f"      {td_tag}")
                    col_offset += colspan

                html_parts.append("    </tr>")
            except Exception as e:
                self.logger.debug(f"Error processing table row {row_idx}: {e}")
                continue

    def _build_th_tag(self, cell_content: str, colspan: int, rowspan: int) -> str:
        """Build an HTML th tag with optional span attributes.

        Args:
            cell_content: The cell content
            colspan: Column span value
            rowspan: Row span value

        Returns:
            HTML th tag string
        """
        attrs = []
        if colspan > 1:
            attrs.append(f'colspan="{colspan}"')
        if rowspan > 1:
            attrs.append(f'rowspan="{rowspan}"')

        if attrs:
            return f"<th {' '.join(attrs)}>{cell_content}</th>"
        return f"<th>{cell_content}</th>"

    def _build_td_tag(self, cell_content: str, colspan: int, rowspan: int) -> str:
        """Build an HTML td tag with optional span attributes.

        Args:
            cell_content: The cell content
            colspan: Column span value
            rowspan: Row span value

        Returns:
            HTML td tag string
        """
        attrs = []
        if colspan > 1:
            attrs.append(f'colspan="{colspan}"')
        if rowspan > 1:
            attrs.append(f'rowspan="{rowspan}"')

        if attrs:
            return f"<td {' '.join(attrs)}>{cell_content}</td>"
        return f"<td>{cell_content}</td>"

    def _get_cell_spans(self, cell, table=None, row_idx=None, col_offset=None) -> tuple:
        """Get colspan and rowspan for a table cell.

        Args:
            cell: The table cell to analyze
            table: Optional table object to calculate rowspan
            row_idx: Optional row index for rowspan calculation
            col_offset: Optional logical column offset (unused, kept for API compatibility)

        Returns:
            Tuple of (colspan, rowspan)

        Note:
            Rowspan detection uses _tc identity to find continuation cells,
            which correctly handles tables with both horizontal and vertical merges.
        """
        try:
            tc = cell._tc
            colspan = 1
            rowspan = 1
            NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

            # Check for horizontal span (gridSpan)
            tcPr = tc.find(f"{{{NS['w']}}}tcPr")
            if tcPr is not None:
                grid_span = tcPr.find(f"{{{NS['w']}}}gridSpan")
                if grid_span is not None:
                    span_val = grid_span.get(f"{{{NS['w']}}}val")
                    if span_val:
                        colspan = int(span_val)

                # Check for vertical span (vMerge)
                v_merge = tcPr.find(f"{{{NS['w']}}}vMerge")
                if v_merge is not None:
                    merge_val = v_merge.get(f"{{{NS['w']}}}val")
                    # Only "restart" means this cell starts a vertical merge
                    # No val attribute means continuation cell, which should be skipped
                    if merge_val == "restart":
                        # Count continuation cells in subsequent rows by _tc identity
                        # This handles cases where horizontal merges affect physical cell indices
                        rowspan = 1  # Start with current cell
                        if table and row_idx is not None:
                            current_tc_id = id(tc)
                            for next_row_idx in range(row_idx + 1, len(table.rows)):
                                try:
                                    next_row = table.rows[next_row_idx]
                                    # Find cell with same _tc (vertical merge continuation)
                                    found_continuation = False
                                    for next_cell in next_row.cells:
                                        if id(next_cell._tc) == current_tc_id:
                                            # Found a cell sharing the same _tc
                                            if self._is_merged_continuation_cell(next_cell):
                                                rowspan += 1
                                                found_continuation = True
                                            break
                                    if not found_continuation:
                                        break
                                except Exception:
                                    break

            return colspan, rowspan

        except Exception as e:
            self.logger.debug(f"Error getting cell spans: {e}")
            return 1, 1

    def _is_merged_continuation_cell(self, cell) -> bool:
        """Check if this cell is a continuation of a merged cell.

        Args:
            cell: The table cell to check

        Returns:
            True if cell is a merge continuation
        """
        try:
            tc = cell._tc
            NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

            # Check for vMerge without val attribute (indicates continuation)
            tcPr = tc.find(f"{{{NS['w']}}}tcPr")
            if tcPr is not None:
                v_merge = tcPr.find(f"{{{NS['w']}}}vMerge")
                if v_merge is not None:
                    merge_val = v_merge.get(f"{{{NS['w']}}}val")
                    if merge_val is None:  # No val attribute means continuation
                        return True

            return False

        except Exception as e:
            self.logger.debug(f"Error checking merge continuation: {e}")
            return False

    def _convert_table_cell_content(self, cell) -> str:
        """Convert table cell content to markdown.

        Args:
            cell: The table cell to convert

        Returns:
            Markdown string for cell content
        """
        cell_parts = []

        for paragraph in cell.paragraphs:
            if self._run_converter:
                para_content = self._run_converter(paragraph.runs)
            else:
                # Fallback to simple text concatenation
                para_content = "".join(run.text for run in paragraph.runs if run.text)

            if para_content.strip():
                # Handle line breaks within the paragraph content
                # Convert newlines to <br> tags to maintain table formatting
                para_content_fixed = para_content.strip().replace("\n", "<br>")
                cell_parts.append(para_content_fixed)

        # Join multiple paragraphs with line breaks
        result = (
            "<br>".join(cell_parts)
            if len(cell_parts) > 1
            else (cell_parts[0] if cell_parts else "")
        )

        # Escape pipe characters in table cells
        return result.replace("|", "\\|")

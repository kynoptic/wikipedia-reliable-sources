#!/usr/bin/env python3
"""
AST-based Markdown Format Analyzer and Validation Tool.

This module provides comprehensive Abstract Syntax Tree (AST) analysis of Markdown documents
with automated fix generation and quality validation. It parses Markdown content using the
marko library to construct a true AST representation, enabling precise analysis and
suggestion of formatting improvements.

Key Components:
    - AnalysisFix: Dataclass representing specific formatting issues with suggested fixes
    - ASTMarkdownAnalyzer: Main analyzer class with AST-based validation rules
    - Automated fix generation with confidence scoring
    - Comprehensive reporting and statistics collection

Usage Patterns:
    - Standalone markdown file analysis
    - Batch processing of markdown collections
    - Integration with document conversion pipelines
    - Quality assurance and style guide enforcement

Dependencies:
    - marko: AST parsing and markdown processing
    - typing: Comprehensive type annotation support
    - pathlib: Modern path handling utilities
"""

import logging
import re
import sys
from pathlib import Path
from typing import Any
from dataclasses import dataclass
from collections import defaultdict

try:
    import marko
    from marko import block, inline
    from marko.md_renderer import MarkdownRenderer
except ImportError:
    print("Error: marko is required. Install with: pip install marko")
    sys.exit(1)

try:
    from marko.block import Document, Paragraph, CodeBlock, FencedCode
    from marko.block import Heading, List as MarkdownList, ListItem, HTMLBlock
    from marko.inline import RawText, CodeSpan, Link, Emphasis, StrongEmphasis
except ImportError:
    print("Error: marko is required. Install with: pip install marko")
    sys.exit(1)

from datetime import datetime

@dataclass
class AnalysisFix:
    """
    Represents a specific formatting issue and its suggested fix in markdown content.

    This dataclass encapsulates all information needed to identify, describe, and
    apply an automated fix to markdown formatting issues. Each fix includes
    location information, issue classification, and confidence scoring.

    Attributes:
        line_number (int): One-based line number where the issue occurs
        column (int): Zero-based column position within the line
        issue_type (str): Classification of the formatting issue type
        description (str): Human-readable description of the issue and fix
        original_text (str): The problematic text that needs to be replaced
        suggested_fix (str): The recommended replacement text
        confidence (float): Confidence score from 0.0 to 1.0 for the fix

    Example:
        >>> fix = AnalysisFix(
        ...     line_number=15,
        ...     column=23,
        ...     issue_type='unescaped_html_tag',
        ...     description='HTML tag <div> should be wrapped in backticks',
        ...     original_text='<div>',
        ...     suggested_fix='`<div>`',
        ...     confidence=0.9
        ... )
    """
    line_number: int
    column: int
    issue_type: str
    description: str
    original_text: str
    suggested_fix: str
    confidence: float  # 0.0 to 1.0

class ASTMarkdownAnalyzer:
    """
    Advanced markdown format analyzer using Abstract Syntax Tree parsing.

    This analyzer constructs a true AST representation of Markdown documents using
    the marko library, enabling precise detection of formatting issues and generation
    of high-confidence automated fixes. It supports comprehensive rule-based validation
    and statistical analysis of document structure.

    The analyzer implements multiple analysis passes:
    1. AST construction and validation
    2. Node-based rule application
    3. Context-aware issue detection
    4. Confidence-scored fix generation
    5. Statistical reporting and metrics collection

    Attributes:
        logger (logging.Logger): Logger instance for analysis operations
        fixes (List[AnalysisFix]): Collection of detected issues and fixes
        parser (marko): Markdown parser instance for AST construction

    Methods:
        analyze_file: Analyze a markdown file from disk
        analyze_content: Analyze markdown content directly
        generate_fixes_patch: Create patch file for automated fixes

    Example:
        >>> analyzer = ASTMarkdownAnalyzer()
        >>> report = analyzer.analyze_file('document.md')
        >>> print(f"Found {report['total_issues']} issues")
    """

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger(__name__)
        self.fixes: list[AnalysisFix] = []
        self.parser = marko

    def analyze_file(self, markdown_file_path: str) -> dict[str, Any]:
        """Analyze a markdown file using AST parsing and return detailed results"""
        try:
            with open(markdown_file_path, 'r', encoding='utf-8') as markdown_file:
                markdown_content = markdown_file.read()

            return self.analyze_content(markdown_content, Path(markdown_file_path))

        except Exception as analysis_error:
            self.logger.error(f"Error analyzing {markdown_file_path}: {analysis_error}")
            return {'file_path': markdown_file_path, 'error': str(analysis_error)}

    def analyze_content(self, markdown_content: str, file_path: Path | None = None) -> dict[str, Any]:
        """Analyze markdown content using AST parsing and return detailed results"""
        try:
            # Parse markdown to AST
            parsed_document = self.parser.parse(markdown_content)

            # Clear previous fixes
            self.fixes = []

            # Run AST-based analysis rules
            self._analyze_ast(parsed_document, markdown_content)

            # Generate analysis report
            report = {
                'file_path': str(file_path) if file_path else 'content',
                'analysis_timestamp': datetime.now().isoformat(),
                'total_issues': len(self.fixes),
                'issues_by_type': self._categorize_issues(),
                'fixes': [self._fix_to_dict(fix) for fix in self.fixes],
                'ast_stats': self._collect_ast_stats(parsed_document),
                'success': True
            }

            return report

        except Exception as analysis_error:
            self.logger.error(f"Error analyzing content: {analysis_error}")
            return {
                'file_path': str(file_path) if file_path else 'content',
                'error': str(analysis_error),
                'success': False,
                'total_issues': 0,
                'issues_by_type': {},
                'fixes': [],
                'ast_stats': {}
            }

    def _analyze_ast(self, doc: Document, content: str) -> None:
        """Run all analysis rules on the AST"""
        lines = content.split('\n')

        # Walk the AST and apply rules
        self._walk_ast_node(doc, lines, content)

    def _walk_ast_node(self, ast_node, markdown_lines: list[str], complete_markdown_content: str) -> None:
        """Recursively walk AST nodes and apply validation rules"""

        # Apply rules based on node type
        if isinstance(ast_node, FencedCode):
            self._check_code_block_language(ast_node, markdown_lines)
        elif isinstance(ast_node, CodeSpan):
            self._check_code_span_content(ast_node, markdown_lines, complete_markdown_content)
        elif isinstance(ast_node, RawText):
            self._check_raw_text_issues(ast_node, markdown_lines, complete_markdown_content)
        elif hasattr(ast_node, '__class__') and 'InlineHTML' in ast_node.__class__.__name__:
            self._check_inline_html_issues(ast_node, markdown_lines, complete_markdown_content)
        elif isinstance(ast_node, Link):
            self._check_link_formatting(ast_node, markdown_lines, complete_markdown_content)
        elif isinstance(ast_node, Heading):
            self._check_heading_formatting(ast_node, markdown_lines)
        elif isinstance(ast_node, HTMLBlock):
            self._check_html_block_usage(ast_node, markdown_lines)

        # Recursively process child nodes
        if hasattr(ast_node, 'children') and ast_node.children:
            for child_node in ast_node.children:
                self._walk_ast_node(child_node, markdown_lines, complete_markdown_content)

    def _check_code_block_language(self, code_block_node: FencedCode, markdown_lines: list[str]) -> None:
        """Check if fenced code blocks have language specifications"""
        try:
            line_number = getattr(code_block_node, 'line_number', None)
            if line_number is None:
                # Try to find line number by content matching
                line_number = self._find_line_number(markdown_lines, '```')

            if hasattr(code_block_node, 'lang') and not code_block_node.lang:
                self.fixes.append(AnalysisFix(
                    line_number=line_number or 0,
                    column=0,
                    issue_type='missing_code_language',
                    description='Code block missing language specification',
                    original_text='```',
                    suggested_fix='```html',
                    confidence=0.8
                ))
        except Exception as e:
            self.logger.debug(f"Error checking code block language: {e}")

    def _check_code_span_content(self, code_span_node: CodeSpan, markdown_lines: list[str], complete_markdown_content: str) -> None:
        """Check code span usage and suggest improvements"""
        try:
            if hasattr(code_span_node, 'children') and code_span_node.children:
                code_span_content = str(code_span_node.children)

                # Check for HTML tags that should be in code spans
                html_tag_patterns = ['<div>', '<span>', '<p>', '<h1>', '<h2>', '<h3>', '<strong>', '<em>']
                for html_tag in html_tag_patterns:
                    if html_tag in code_span_content and not code_span_content.startswith('`') and not code_span_content.endswith('`'):
                        # This is already in a code span, which is correct
                        pass

        except Exception as e:
            self.logger.debug(f"Error checking code span: {e}")

    def _check_raw_text_issues(self, raw_text_node: RawText, markdown_lines: list[str], complete_markdown_content: str) -> None:
        """Check raw text for various formatting issues"""
        try:
            if not hasattr(raw_text_node, 'children'):
                return

            raw_text_content = str(raw_text_node.children)

            # Check for HTML tags not in backticks
            html_tag_patterns = ['<code>', '<samp>', '<pre>', '<kbd>', '<strong>', '<b>', '<em>', '<div>', '<span>']
            for html_tag in html_tag_patterns:
                if html_tag in raw_text_content:
                    # Find position in complete content
                    line_number = self._find_line_with_content(markdown_lines, raw_text_content)
                    column_position = raw_text_content.find(html_tag)

                    self.fixes.append(AnalysisFix(
                        line_number=line_number,
                        column=column_position,
                        issue_type='unescaped_html_tag',
                        description=f'HTML tag {html_tag} should be wrapped in backticks',
                        original_text=html_tag,
                        suggested_fix=f'`{html_tag}`',
                        confidence=0.9
                    ))

            # Check for keyboard references without <kbd> tags
            keyboard_reference_patterns = [
                (r'\bSpace bar\b', 'Space bar'),
                (r'\bEnter\b(?!prise)', 'Enter'),
                (r'\bTab\b(?!le)', 'Tab'),
                (r'\bControl\+\w+', 'Control+'),
                (r'\bCommand\+\w+', 'Command+'),
                (r'\bShift\+\w+', 'Shift+')
            ]

            for keyboard_pattern, keyboard_name in keyboard_reference_patterns:
                keyboard_matches = re.finditer(keyboard_pattern, raw_text_content)
                for keyboard_match in keyboard_matches:
                    # Check if not already in <kbd> tags
                    context_start = max(0, keyboard_match.start()-10)
                    context_end = keyboard_match.end()+10
                    if '<kbd>' not in raw_text_content[context_start:context_end]:
                        line_number = self._find_line_with_content(markdown_lines, raw_text_content)

                        self.fixes.append(AnalysisFix(
                            line_number=line_number,
                            column=keyboard_match.start(),
                            issue_type='missing_kbd_tag',
                            description=f'Keyboard reference "{keyboard_match.group()}" should use <kbd> tags',
                            original_text=keyboard_match.group(),
                            suggested_fix=f'<kbd>{keyboard_match.group()}</kbd>',
                            confidence=0.8
                        ))

            # Check for file paths without backticks
            file_path_pattern = r'(/[a-zA-Z0-9_./]+|[A-Za-z]:\\[^\\/:*?"<>|]+)'
            file_path_matches = re.finditer(file_path_pattern, raw_text_content)
            for file_path_match in file_path_matches:
                path_context_start = max(0, file_path_match.start()-1)
                path_context_end = file_path_match.end()+1
                if '`' not in raw_text_content[path_context_start:path_context_end]:
                    line_number = self._find_line_with_content(markdown_lines, raw_text_content)

                    self.fixes.append(AnalysisFix(
                        line_number=line_number,
                        column=file_path_match.start(),
                        issue_type='unformatted_file_path',
                        description='File path should be wrapped in backticks',
                        original_text=file_path_match.group(),
                        suggested_fix=f'`{file_path_match.group()}`',
                        confidence=0.7
                    ))

        except Exception as e:
            self.logger.debug(f"Error checking raw text: {e}")

    def _check_inline_html_issues(self, node, lines: list[str], full_content: str) -> None:
        """Check inline HTML for formatting issues"""
        try:
            if hasattr(node, 'children'):
                html_content = str(node.children)

                # Check for HTML tags that should be in backticks
                if html_content.startswith('<') and html_content.endswith('>'):
                    line_num = self._find_line_with_content(lines, html_content)

                    self.fixes.append(AnalysisFix(
                        line_number=line_num,
                        column=0,
                        issue_type='unescaped_html_tag',
                        description=f'HTML tag {html_content} should be wrapped in backticks when referenced as code',
                        original_text=html_content,
                        suggested_fix=f'`{html_content}`',
                        confidence=0.9
                    ))

        except Exception as e:
            self.logger.debug(f"Error checking inline HTML: {e}")

    def _check_link_formatting(self, node: Link, lines: list[str], full_content: str) -> None:
        """Check link formatting and accessibility"""
        try:
            if hasattr(node, 'dest') and node.dest:
                url = node.dest

                # Check for accessible link text
                if hasattr(node, 'children') and node.children:
                    link_text = str(node.children)

                    # Flag generic link text
                    generic_texts = ['click here', 'here', 'link', 'read more']
                    if link_text.lower() in generic_texts:
                        line_num = self._find_line_with_content(lines, url)

                        self.fixes.append(AnalysisFix(
                            line_number=line_num,
                            column=0,
                            issue_type='generic_link_text',
                            description=f'Link text "{link_text}" is not descriptive',
                            original_text=f'[{link_text}]({url})',
                            suggested_fix=f'[{url}]({url})',  # Use URL as text as fallback
                            confidence=0.6
                        ))

        except Exception as e:
            self.logger.debug(f"Error checking link: {e}")

    def _check_heading_formatting(self, node: Heading, lines: list[str]) -> None:
        """Check heading formatting and structure"""
        try:
            if hasattr(node, 'level') and hasattr(node, 'children'):
                level = node.level

                # Extract heading text
                heading_text = ''
                if node.children:
                    heading_text = str(node.children)

                # Check for title case (should be sentence case)
                if self._is_title_case(heading_text):
                    line_num = self._find_line_with_content(lines, heading_text)

                    self.fixes.append(AnalysisFix(
                        line_number=line_num,
                        column=0,
                        issue_type='heading_case',
                        description='Heading should use sentence case, not title case',
                        original_text=f'{"#" * level} {heading_text}',
                        suggested_fix=f'{"#" * level} {self._to_sentence_case(heading_text)}',
                        confidence=0.7
                    ))

        except Exception as e:
            self.logger.debug(f"Error checking heading: {e}")

    def _check_html_block_usage(self, node: HTMLBlock, lines: list[str]) -> None:
        """Check HTML block usage and suggest markdown alternatives"""
        try:
            if hasattr(node, 'content'):
                html_content = node.content

                # Check for simple formatting that could be markdown
                if '<strong>' in html_content or '<b>' in html_content:
                    line_num = self._find_line_with_content(lines, html_content)

                    self.fixes.append(AnalysisFix(
                        line_number=line_num,
                        column=0,
                        issue_type='html_could_be_markdown',
                        description='HTML bold tags could be replaced with markdown **bold**',
                        original_text=html_content.strip(),
                        suggested_fix=html_content.replace('<strong>', '**').replace('</strong>', '**').replace('<b>', '**').replace('</b>', '**'),
                        confidence=0.5
                    ))

        except Exception as e:
            self.logger.debug(f"Error checking HTML block: {e}")

    def _find_line_number(self, markdown_lines: list[str], search_text: str) -> int:
        """Find line number containing specific text"""
        for line_index, line_content in enumerate(markdown_lines):
            if search_text in line_content:
                return line_index + 1
        return 1

    def _find_line_with_content(self, markdown_lines: list[str], target_content: str) -> int:
        """Find line number containing specific content"""
        content_snippet = target_content[:30] if len(target_content) > 30 else target_content
        for line_index, line_content in enumerate(markdown_lines):
            if content_snippet in line_content:
                return line_index + 1
        return 1

    def _is_title_case(self, heading_text: str) -> bool:
        """Check if text is in title case"""
        words_in_heading = heading_text.split()
        if len(words_in_heading) <= 1:
            return False

        # Simple heuristic: if most words are capitalized, it's probably title case
        capitalized_word_count = sum(1 for word in words_in_heading if word and word[0].isupper())
        return capitalized_word_count >= len(words_in_heading) * 0.7

    def _to_sentence_case(self, heading_text: str) -> str:
        """Convert text to sentence case"""
        if not heading_text:
            return heading_text
        return heading_text[0].upper() + heading_text[1:].lower()

    def _categorize_issues(self) -> dict[str, int]:
        """Categorize fixes by issue type"""
        categories = {}
        for fix in self.fixes:
            categories[fix.issue_type] = categories.get(fix.issue_type, 0) + 1
        return categories

    def _collect_ast_stats(self, doc: Document) -> dict[str, int]:
        """Collect statistics from the AST"""
        stats = {
            'headings': 0,
            'paragraphs': 0,
            'code_blocks': 0,
            'links': 0,
            'lists': 0,
            'html_blocks': 0
        }

        def count_nodes(node):
            if isinstance(node, Heading):
                stats['headings'] += 1
            elif isinstance(node, Paragraph):
                stats['paragraphs'] += 1
            elif isinstance(node, (CodeBlock, FencedCode)):
                stats['code_blocks'] += 1
            elif isinstance(node, Link):
                stats['links'] += 1
            elif isinstance(node, MarkdownList):
                stats['lists'] += 1
            elif isinstance(node, HTMLBlock):
                stats['html_blocks'] += 1

            if hasattr(node, 'children') and node.children:
                for child in node.children:
                    count_nodes(child)

        count_nodes(doc)
        return stats

    def _fix_to_dict(self, fix: AnalysisFix) -> dict[str, Any]:
        """Convert fix to dictionary for serialization"""
        return {
            'line_number': fix.line_number,
            'column': fix.column,
            'issue_type': fix.issue_type,
            'description': fix.description,
            'original_text': fix.original_text,
            'suggested_fix': fix.suggested_fix,
            'confidence': fix.confidence
        }

    def generate_fixes_patch(self, markdown_path: str, analysis_report: dict[str, Any]) -> str:
        """Generate a patch file with automated fixes"""
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            lines = original_content.split('\n')
            fixes = analysis_report.get('fixes', [])

            # Sort fixes by line number (descending) to avoid offset issues
            fixes_sorted = sorted(fixes, key=lambda x: x['line_number'], reverse=True)

            # Apply high-confidence fixes
            modified_lines = lines.copy()
            applied_fixes = []

            for fix in fixes_sorted:
                if fix['confidence'] >= 0.8:  # Only apply high-confidence fixes
                    line_idx = fix['line_number'] - 1
                    if 0 <= line_idx < len(modified_lines):
                        original_line = modified_lines[line_idx]
                        modified_line = original_line.replace(fix['original_text'], fix['suggested_fix'])

                        if modified_line != original_line:
                            modified_lines[line_idx] = modified_line
                            applied_fixes.append(fix)

            # Generate unified diff format
            patch_content = f"""--- {markdown_path}
+++ {markdown_path}
@@ -1,{len(lines)} +1,{len(modified_lines)} @@
"""

            for i, (original, modified) in enumerate(zip(lines, modified_lines)):
                if original != modified:
                    patch_content += f"-{original}\n+{modified}\n"
                else:
                    patch_content += f" {original}\n"

            return patch_content

        except Exception as e:
            self.logger.error(f"Error generating patch: {e}")
            return f"# Error generating patch: {e}"


def setup_logging() -> logging.Logger:
    """Setup logging for the analyzer"""
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / 'ast_markdown_analyzer.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode='a')
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Main entry point for the AST analyzer"""
    logger = setup_logging()

    if len(sys.argv) < 2:
        print("Usage: python ast_markdown_analyzer.py <markdown_file>")
        return 1

    markdown_file = sys.argv[1]

    analyzer = ASTMarkdownAnalyzer(logger)
    report = analyzer.analyze_file(markdown_file)

    # Print analysis results
    print(f"=== AST MARKDOWN ANALYSIS: {markdown_file} ===\n")
    print(f"Total issues found: {report.get('total_issues', 0)}")

    issues_by_type = report.get('issues_by_type', {})
    if issues_by_type:
        print("\nIssues by type:")
        for issue_type, count in issues_by_type.items():
            print(f"  {issue_type}: {count}")

    # Generate and save patch
    if report.get('total_issues', 0) > 0:
        patch = analyzer.generate_fixes_patch(markdown_file, report)
        patch_file = markdown_file.replace('.md', '.fixes.patch')

        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(patch)

        print(f"\nGenerated fixes patch: {patch_file}")
        print("Apply with: patch < {patch_file}")

    return 0


if __name__ == '__main__':
    sys.exit(main())

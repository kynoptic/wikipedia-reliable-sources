#!/usr/bin/env python3
"""
Document Conversion - Markdown Format Validator
Entry point for AST-based markdown analysis and validation
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

# Import our new AST-based analyzer
from .ast_markdown_analyzer import ASTMarkdownAnalyzer, setup_logging


def find_target_markdown_file(logger: logging.Logger) -> Path | None:
    """Find the main Style guide markdown file for analysis"""
    possible_paths = [
        Path(__file__).parent.parent.parent / 'content' / 'markdown' / 'General' / 'Style guide for your organization.md',
        Path('content/markdown/General/Style guide for your organization.md'),
        Path('../content/markdown/General/Style guide for your organization.md')
    ]

    for path in possible_paths:
        if path.exists():
            logger.info(f"Found target markdown file: {path.absolute()}")
            return path

    logger.error("Could not find 'Style guide for your organization.md' in expected locations:")
    for path in possible_paths:
        logger.error(f"  - {path.absolute()}")
    return None


def find_all_markdown_files(logger: logging.Logger) -> list[Path]:
    """Find all markdown files in the content directory"""
    content_dir = Path(__file__).parent.parent.parent / 'content' / 'markdown'
    markdown_files = []

    if content_dir.exists():
        for md_file in content_dir.rglob('*.md'):
            markdown_files.append(md_file)
            logger.debug(f"Found markdown file: {md_file.relative_to(content_dir)}")
    else:
        logger.warning(f"Content directory not found: {content_dir}")

    return markdown_files


def display_analysis_results(analysis_result: dict[str, Any], file_path: Path, logger: logging.Logger):
    """Display formatted analysis results to console"""
    print(f"=== AST MARKDOWN ANALYSIS: {file_path.name} ===\n")

    # Display AST statistics
    ast_stats = analysis_result.get('ast_stats', {})
    if ast_stats:
        print("Basic formatting counts:")
        stats_display = {
            'headings': 'Headings (#)',
            'paragraphs': 'Paragraphs',
            'code_blocks': 'Code blocks (```)',
            'links': 'Links',
            'lists': 'Lists',
            'html_blocks': 'HTML blocks'
        }
        for key, label in stats_display.items():
            count = ast_stats.get(key, 0)
            print(f"  {label}: {count}")
        print()

    # Display issues found
    total_issues = analysis_result.get('total_issues', 0)
    issues_by_type = analysis_result.get('issues_by_type', {})

    if total_issues > 0:
        print("=== ISSUES FOUND ===")
        fixes = analysis_result.get('fixes', [])

        # Group issues by severity
        errors = [f for f in fixes if f.get('confidence', 0) >= 0.9]
        warnings = [f for f in fixes if 0.7 <= f.get('confidence', 0) < 0.9]
        suggestions = [f for f in fixes if f.get('confidence', 0) < 0.7]

        if errors:
            print("High priority (errors):")
            for fix in errors[:5]:  # Show top 5
                print(f"  Line {fix['line_number']}: {fix['description']}")
                print(f"    Fix: {fix['original_text']} → {fix['suggested_fix']}")

        if warnings:
            print("Medium priority (warnings):")
            for fix in warnings[:3]:  # Show top 3
                print(f"  Line {fix['line_number']}: {fix['description']}")

        if suggestions:
            print(f"Low priority suggestions: {len(suggestions)}")
        print()

        print("=== IMPROVEMENTS NEEDED ===")
        print("Priority fixes:")
        priority_messages = []

        if issues_by_type.get('missing_code_language', 0) > 0:
            priority_messages.append(f"Add language specs to {issues_by_type['missing_code_language']} code blocks (likely \"html\")")

        if issues_by_type.get('unescaped_html_tag', 0) > 0:
            priority_messages.append(f"Wrap {issues_by_type['unescaped_html_tag']} HTML tags in backticks when referenced as code")

        if issues_by_type.get('missing_kbd_tag', 0) > 0:
            priority_messages.append(f"Use <kbd> tags for {issues_by_type['missing_kbd_tag']} keyboard references")

        if issues_by_type.get('generic_link_text', 0) > 0:
            priority_messages.append(f"Improve {issues_by_type['generic_link_text']} generic link texts for better accessibility")

        for i, msg in enumerate(priority_messages, 1):
            print(f"  {i}. {msg}")

        if not priority_messages:
            print("  No critical issues found!")
        print()
    else:
        print("✅ No formatting issues found!")
        print()


def generate_patch_files(analysis_result: dict[str, Any], file_path: Path, logger: logging.Logger) -> Path | None:
    """Generate patch files for automated fixes"""
    fixes = analysis_result.get('fixes', [])
    high_confidence_fixes = [f for f in fixes if f.get('confidence', 0) >= 0.8]

    if not high_confidence_fixes:
        return None

    # Generate patch file
    logs_dir = Path(__file__).parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)

    patch_file = logs_dir / f"{file_path.stem}_ast_fixes.patch"

    try:
        with patch_file.open('w', encoding='utf-8') as f:
            f.write(f"# Automated AST-based fixes for {file_path.name}\n")
            f.write(f"# Generated by Organizational Content Governance AST Analyzer\n")
            f.write(f"# Apply with: patch < {patch_file.name}\n\n")

            for fix in high_confidence_fixes:
                f.write(f"## Line {fix['line_number']}: {fix['issue_type']}\n")
                f.write(f"# {fix['description']}\n")
                f.write(f"- {fix['original_text']}\n")
                f.write(f"+ {fix['suggested_fix']}\n")
                f.write(f"# Confidence: {fix['confidence']:.1%}\n\n")

        logger.info(f"Generated patch file: {patch_file}")
        return patch_file

    except Exception as e:
        logger.error(f"Failed to generate patch file: {e}")
        return None


def main():
    """Main entry point for markdown format validation"""
    logger = setup_logging()

    try:
        # Find the target file to analyze
        target_file = find_target_markdown_file(logger)
        if not target_file:
            print("❌ Could not find target markdown file for analysis")
            return 2

        # Create AST analyzer
        analyzer = ASTMarkdownAnalyzer(logger)

        # Analyze the file
        logger.info(f"Starting AST-based analysis of {target_file.name}")
        analysis_result = analyzer.analyze_file(str(target_file))

        if 'error' in analysis_result:
            logger.error(f"Analysis failed: {analysis_result['error']}")
            print(f"❌ Analysis failed: {analysis_result['error']}")
            return 2

        # Display results
        display_analysis_results(analysis_result, target_file, logger)

        # Generate patch file if there are fixes
        patch_file = generate_patch_files(analysis_result, target_file, logger)
        if patch_file:
            print(f"📄 Patch file generated: {patch_file}")
            print(f"    Apply with: cd {patch_file.parent} && patch < {patch_file.name}")
            print()

        # Log completion
        logs_dir = Path(__file__).parent.parent.parent / 'logs'
        print(f"📝 Analysis complete. Check '{logs_dir / 'ast_markdown_analyzer.log'}' for detailed logs.")

        # Return appropriate exit code
        total_issues = analysis_result.get('total_issues', 0)
        if total_issues > 0:
            return 1  # Issues found that need attention
        return 0  # All good

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\n⏹️  Analysis interrupted")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"💥 Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

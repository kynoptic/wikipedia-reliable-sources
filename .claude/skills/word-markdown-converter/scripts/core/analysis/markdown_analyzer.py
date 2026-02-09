#!/usr/bin/env python3
"""
DEPRECATED: This regex-based analyzer is deprecated.

Use ast_markdown_analyzer.py instead, which provides:
- More accurate AST-based analysis
- Better fix suggestions with confidence scoring
- Comprehensive validation rules
- Single source of truth for markdown analysis

This file is kept temporarily for backwards compatibility but will be removed.
Migration path: Replace imports of markdown_analyzer with ast_markdown_analyzer.
"""

import os
import re
import warnings
from pathlib import Path

warnings.warn(
    "markdown_analyzer.py is deprecated. Use ast_markdown_analyzer.py instead.",
    DeprecationWarning,
    stacklevel=2,
)


def analyze_single_file(markdown_path):
    """Analyze formatting quality of a single markdown file"""

    if not os.path.exists(markdown_path):
        return None

    with open(markdown_path, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []
    issues.extend(_check_html_tags(content))
    issues.extend(_check_keyboard_references(content))
    issues.extend(_check_code_blocks(content))
    issues.extend(_check_file_paths_and_ips(content))
    issues.extend(_check_urls(content))

    return issues


def _check_html_tags(content):
    """Check for HTML tags that should be in backticks"""
    issues = []
    html_tags_to_check = [
        "<code>",
        "<samp>",
        "<pre>",
        "<kbd>",
        "<strong>",
        "<b>",
        "<em>",
        "<var>",
        "<cite>",
        "<div>",
        "<span>",
        "<p>",
        "<h1>",
        "<h2>",
        "<h3>",
        "<h4>",
        "<h5>",
        "<h6>",
    ]
    for tag in html_tags_to_check:
        pattern = rf"(?<!`){re.escape(tag)}(?!`)"
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"HTML tag {tag} found {len(matches)} times without backticks")
    return issues


def _check_keyboard_references(content):
    """Check for keyboard references without <kbd> tags"""
    issues = []
    keyboard_refs = [
        ("Space bar", r"\bSpace bar\b"),
        ("Control+", r"\bControl\+"),
        ("Command+", r"\bCommand\+"),
        ("Enter", r"\bEnter\b(?!prise)"),
        ("Tab", r"\bTab\b(?!le)"),
        ("Shift+", r"\bShift\+"),
        ("Alt+", r"\bAlt\+"),
        ("Option+", r"\bOption\+"),
    ]
    for ref_name, ref_pattern in keyboard_refs:
        matches = re.findall(ref_pattern, content)
        if matches:
            untagged_count = sum(
                1
                for match in matches
                if f"<kbd>{match}" not in content and f"<kbd>{ref_name}" not in content
            )
            if untagged_count > 0:
                issues.append(
                    f"Keyboard reference '{ref_name}' found {untagged_count} "
                    f"times without <kbd> tags"
                )
    return issues


def _check_code_blocks(content):
    """Check for code blocks without language specification"""
    issues = []
    lines = content.split("\n")
    code_blocks_no_lang = sum(1 for line in lines if line.strip() == "```")

    if code_blocks_no_lang > 0:
        issues.append(f"{code_blocks_no_lang} code blocks missing language specification")
    return issues


def _check_file_paths_and_ips(content):
    """Check for file paths and IP addresses without backticks"""
    issues = []

    if re.search(r"/Users/[^\s`]+", content):
        matches = re.findall(r"(?<!`)/Users/[^\s`]+(?!`)", content)
        if matches:
            issues.append(f"File paths found {len(matches)} times without backticks")

    if re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", content):
        matches = re.findall(r"(?<!`)\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b(?!`)", content)
        if matches:
            issues.append(f"IP addresses found {len(matches)} times without backticks")

    return issues


def _check_urls(content):
    """Check for URLs without backticks"""
    issues = []

    url_pattern = r"\]\((?!`)https?://[^\s)]+(?!`)\)"
    url_matches = re.findall(url_pattern, content)
    if url_matches:
        issues.append(f"URLs in markdown links found {len(url_matches)} times without backticks")

    standalone_url_pattern = r"(?<!\[)(?<!`)\bhttps?://[^\s`]+(?!`)(?!\))"
    standalone_matches = re.findall(standalone_url_pattern, content)
    if standalone_matches:
        issues.append(f"Standalone URLs found {len(standalone_matches)} times without backticks")

    return issues


def analyze_all_markdown_files():
    """Analyze all markdown files in the content directory"""

    print("=== ORGANIZATIONAL CONTENT GOVERNANCE - MARKDOWN FORMATTING ANALYSIS ===\n")

    # Find all markdown files
    markdown_dir = Path("content/markdown")
    if not markdown_dir.exists():
        print("Error: content/markdown directory not found")
        return

    markdown_files = list(markdown_dir.glob("**/*.md"))

    print(f"Found {len(markdown_files)} markdown files to analyze\n")

    all_issues = {}
    total_issues = 0

    for md_file in markdown_files:
        rel_path = str(md_file)
        issues = analyze_single_file(md_file)

        if issues:
            all_issues[rel_path] = issues
            total_issues += len(issues)
            print(f"📄 {rel_path}")
            for issue in issues:
                print(f"  ⚠️  {issue}")
            print()
        else:
            print(f"✅ {rel_path} - No formatting issues found")

    print("\n=== SUMMARY ===")
    print(f"Files analyzed: {len(markdown_files)}")
    print(f"Files with issues: {len(all_issues)}")
    print(f"Total issues found: {total_issues}")

    if all_issues:
        print("\n=== PRIORITY ACTIONS NEEDED ===")

        # Group common issues
        common_issues = {}
        for file_path, file_issues in all_issues.items():
            for issue in file_issues:
                if issue not in common_issues:
                    common_issues[issue] = []
                common_issues[issue].append(file_path)

        for issue, files in sorted(common_issues.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"• {issue}")
            file_names = [f.split("/")[-1] for f in files[:3]]
            suffix = "..." if len(files) > 3 else ""
            print(f'  Affects {len(files)} files: {", ".join(file_names)}{suffix}')
            print()

    return all_issues


if __name__ == "__main__":
    analyze_all_markdown_files()

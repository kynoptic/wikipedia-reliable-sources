#!/usr/bin/env python3
"""
Run Formatter for Word-to-Markdown Conversion.

This module provides specialized handling for converting Word document runs
to Markdown with intelligent formatting, character style processing, and
image extraction. Extracted from the main converter to reduce complexity.

Key Features:
    - Smart bold/italic consolidation to avoid broken markdown
    - Character style mapping with configurable aliases
    - Image extraction and markdown generation
    - Direct formatting handling with whitespace management
    - Style hierarchy resolution (character styles > direct formatting > plain text)

Classes:
    RunFormatter: Handles all run-level formatting and conversion logic
"""

import logging
from typing import Any


class RunFormatter:
    """Handles formatting and conversion of Word document runs to Markdown"""

    def __init__(self, logger: logging.Logger, config: dict[str, Any]):
        """Initialize the run formatter with configuration

        Args:
            logger: Logger instance for debugging and error reporting
            config: Style mapping configuration loaded from YAML
        """
        self.logger = logger
        self.config = config

        # Dependencies injected by the main converter
        self._extract_run_images_func = None
        self._get_alt_text_for_image_func = None
        self.style_stats = None
        self.image_mapping = None

    def set_dependencies(
        self, extract_run_images_func, get_alt_text_for_image_func, style_stats, image_mapping
    ):
        """Inject dependencies from the main converter

        Args:
            extract_run_images_func: Function to extract images from runs
            get_alt_text_for_image_func: Function to get alt text for images
            style_stats: Dictionary for tracking style usage statistics
            image_mapping: Dictionary mapping image IDs to file paths
        """
        self._extract_run_images_func = extract_run_images_func
        self._get_alt_text_for_image_func = get_alt_text_for_image_func
        self.style_stats = style_stats
        self.image_mapping = image_mapping

    def convert_runs_with_smart_formatting(self, runs) -> str:
        """Convert runs with intelligent bold/italic consolidation and character style coalescing"""
        if not runs:
            return ""

        state = {
            "result_parts": [],
            "current_group": [],
            "current_bold": None,
            "current_italic": None,
            "current_char_style": None,
            "current_char_style_group": [],
        }

        for run in runs:
            self._process_run(run, state)

        self._flush_final_groups(state)

        result = "".join(state["result_parts"])
        return self._optimize_nested_formatting(result)

    def _process_run(self, run, state):
        """Process a single run and update state"""
        image_markdown = self._extract_run_images(run)
        if image_markdown:
            self._flush_all_groups(state)
            state["result_parts"].append(image_markdown)
            return

        if not run.text:
            return

        raw_style_name = (
            run.style.name if run.style and run.style.name != "Default Paragraph Font" else None
        )
        style_name = self._resolve_character_style_alias(raw_style_name, run)

        if style_name and style_name in self.config.get("character_styles", {}):
            self._handle_character_style_run(run, style_name, state)
        else:
            self._handle_direct_formatting_run(run, state)

    def _flush_all_groups(self, state):
        """Flush all pending groups to result"""
        if state["current_char_style_group"]:
            state["result_parts"].append(
                self._format_character_style_group(
                    state["current_char_style_group"], state["current_char_style"]
                )
            )
            state["current_char_style_group"] = []
            state["current_char_style"] = None

        if state["current_group"]:
            state["result_parts"].append(
                self.format_run_group(
                    state["current_group"], state["current_bold"], state["current_italic"]
                )
            )
            state["current_group"] = []
            state["current_bold"] = None
            state["current_italic"] = None

    def _handle_character_style_run(self, run, style_name, state):
        """Handle a run with character style"""
        if state["current_group"]:
            state["result_parts"].append(
                self.format_run_group(
                    state["current_group"], state["current_bold"], state["current_italic"]
                )
            )
            state["current_group"] = []
            state["current_bold"] = None
            state["current_italic"] = None

        if state["current_char_style"] == style_name:
            state["current_char_style_group"].append(run.text)
        else:
            if state["current_char_style_group"]:
                state["result_parts"].append(
                    self._format_character_style_group(
                        state["current_char_style_group"], state["current_char_style"]
                    )
                )
            state["current_char_style_group"] = [run.text]
            state["current_char_style"] = style_name

    def _handle_direct_formatting_run(self, run, state):
        """Handle a run with direct formatting (bold/italic)"""
        if state["current_char_style_group"]:
            state["result_parts"].append(
                self._format_character_style_group(
                    state["current_char_style_group"], state["current_char_style"]
                )
            )
            state["current_char_style_group"] = []
            state["current_char_style"] = None

        run_bold = run.bold
        run_italic = run.italic

        if state["current_bold"] == run_bold and state["current_italic"] == run_italic:
            state["current_group"].append(run.text)
        else:
            if state["current_group"]:
                state["result_parts"].append(
                    self.format_run_group(
                        state["current_group"], state["current_bold"], state["current_italic"]
                    )
                )
            state["current_group"] = [run.text]
            state["current_bold"] = run_bold
            state["current_italic"] = run_italic

    def _flush_final_groups(self, state):
        """Flush any remaining groups at the end"""
        if state["current_char_style_group"]:
            state["result_parts"].append(
                self._format_character_style_group(
                    state["current_char_style_group"], state["current_char_style"]
                )
            )
        if state["current_group"]:
            state["result_parts"].append(
                self.format_run_group(
                    state["current_group"], state["current_bold"], state["current_italic"]
                )
            )

    def format_run_group(self, text_parts, is_bold, is_italic) -> str:
        """Format a group of text parts with consistent bold/italic formatting"""
        if not text_parts:
            return ""

        combined_text = "".join(text_parts)
        if not combined_text:
            return ""

        if (is_bold or is_italic) and (combined_text.strip() != combined_text):
            return self._format_with_whitespace_handling(combined_text, is_bold, is_italic)

        return self._apply_direct_formatting(combined_text, is_bold, is_italic)

    def _format_with_whitespace_handling(self, text, is_bold, is_italic) -> str:
        """Format text with proper whitespace handling outside markdown markers"""
        leading_space = text[: len(text) - len(text.lstrip())]
        trimmed_text = text.strip()
        trailing_space = text[len(leading_space) + len(trimmed_text) :]

        formatted = self._apply_direct_formatting(trimmed_text, is_bold, is_italic)
        if formatted == trimmed_text:
            return text
        return f"{leading_space}{formatted}{trailing_space}"

    def _apply_direct_formatting(self, text, is_bold, is_italic) -> str:
        """Apply direct formatting based on config"""
        direct_formatting = self.config.get("direct_formatting", {})

        if is_bold and is_italic and "bold_italic" in direct_formatting:
            return f"***{text}***"
        elif is_bold and "bold" in direct_formatting:
            return f"**{text}**"
        elif is_italic and "italic" in direct_formatting:
            return f"*{text}*"
        else:
            return text

    def convert_run_to_markdown(self, run) -> str:
        """Convert a single run to markdown based on style hierarchy and config"""
        image_markdown = self._extract_run_images(run)
        if image_markdown:
            return image_markdown

        if not run.text:
            return ""

        text = run.text
        style_name = (
            run.style.name if run.style and run.style.name != "Default Paragraph Font" else None
        )

        if style_name and self.style_stats is not None:
            self.style_stats[f"char_style_{style_name}"] += 1

        # Priority 1: Character styles (highest priority)
        char_style_result = self._try_character_style_formatting(text, style_name, run)
        if char_style_result:
            return char_style_result

        # Priority 2: Direct formatting
        return self._apply_direct_formatting(text, run.bold, run.italic)

    def _try_character_style_formatting(self, text, style_name, run):
        """Try to apply character style formatting if applicable"""
        resolved_style = self._resolve_character_style_alias(style_name, run)
        if not resolved_style or resolved_style not in self.config.get("character_styles", {}):
            return None

        char_style = self.config["character_styles"][resolved_style]
        if char_style.get("markdown") == "backticks":
            return f"`{text}`"
        elif char_style.get("markdown") == "kbd_tag":
            return f"<kbd>{text}</kbd>"
        return None

    def _format_character_style_group(self, text_parts, style_name) -> str:
        """Format a group of text parts with consistent character style"""
        if not text_parts or not style_name:
            return ""

        combined_text = "".join(text_parts)
        if not combined_text:
            return ""

        char_style = self.config.get("character_styles", {}).get(style_name, {})
        if char_style.get("markdown") == "backticks":
            return f"`{combined_text}`"
        elif char_style.get("markdown") == "kbd_tag":
            return f"<kbd>{combined_text}</kbd>"
        else:
            # Fallback - return text as-is
            return combined_text

    def _resolve_character_style_alias(self, style_name: str | None, run) -> str | None:
        """Normalize character style names and infer from font to determine canonical style.

        Returns 'Code' or 'Input' when detected; otherwise returns the original style_name if it
        matches config; else None.
        """
        cfg_styles = set(self.config.get("character_styles", {}).keys())
        name = (style_name or "").strip()
        lname = name.lower()

        # Aliases for Code
        code_aliases = {
            "code",
            "code inline",
            "inline code",
            "monospace",
            "tt",
            "teletype",
            "fixed",
            "preformatted",
        }

        # Aliases for Input/kbd
        kbd_aliases = {"input", "kbd", "keyboard", "key", "user input", "keyboard input"}

        if lname in code_aliases:
            return "Code"
        if lname in kbd_aliases:
            return "Input"

        # If exact style exists in config, keep it
        if name in cfg_styles:
            return name

        # Infer Code from monospaced fonts
        try:
            font_name = (getattr(run.font, "name", None) or "").strip().lower()
        except Exception:
            font_name = ""

        mono_fonts = {
            "courier",
            "courier new",
            "consolas",
            "menlo",
            "monaco",
            "source code pro",
            "roboto mono",
            "aptos mono",
            "dejavu sans mono",
            "lucida console",
            "ubuntu mono",
        }

        if font_name in mono_fonts:
            return "Code"

        return None

    def _extract_run_images(self, run) -> str:
        """Extract images from a run using injected function"""
        if self._extract_run_images_func:
            return self._extract_run_images_func(run)
        return ""

    def _optimize_nested_formatting(self, text: str) -> str:
        """Optimize adjacent bold/italic markdown markers.

        Converts patterns like:
            **text** ***italic*** **text**
        To:
            **text *italic* text**

        This handles cases where bold text contains italic segments,
        created when transitioning between bold and bold+italic formatting.

        Only operates on actual markdown formatting (asterisks surrounding text),
        not literal asterisks in plain text content.
        """
        import re

        # Pattern 1: **text** ***more*** -> **text *more***
        # Only match when preceded by text and followed by non-whitespace (actual formatting)
        text = re.sub(r"(\S)\*\* \*\*\*(\S)", r"\1 *\2", text)

        # Pattern 2: ***text*****more** -> ***text*more**
        # Only match when between non-whitespace characters (actual formatting)
        text = re.sub(r"(\S)\*\*\*\*\*(\S)", r"\1*\2", text)

        return text

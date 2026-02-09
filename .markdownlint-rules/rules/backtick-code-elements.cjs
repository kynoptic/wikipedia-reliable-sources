"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _sharedConstants = require("./shared-constants.cjs");
// @ts-check

/**
 * Rule that requires code snippets, file names and directory paths
 * to be wrapped in backticks when used in prose.
 */
// Import the centralized ignoredTerms Set

/**
 * markdownlint rule enforcing backticks around file paths and commands.
 *
 * @param {import('markdownlint').RuleParams} params - Parsed Markdown input.
 * @param {import('markdownlint').RuleOnError} onError - Callback to report violations.
 * @returns {void}
 */
function backtickCodeElements(params, onError) {
  if (!params || !Array.isArray(params.lines) || typeof onError !== 'function') {
    return;
  }
  const lines = params.lines;
  let inCodeBlock = false;
  let inMathBlock = false;
  for (let i = 0; i < lines.length; i++) {
    const lineNumber = i + 1;
    const line = lines[i];

    // Special flag for lines containing $
    if (line.includes('$')) {
      // Extra debug for lines containing specific patterns we're looking for
      if (line.includes('$pattern') || line.includes('$value')) {}
    }

    // Detect both ``` and ~~~ as code block fences (ATX or tilde).
    const fenceMatch = line.trim().match(/^(`{3,}|~{3,})/);
    if (fenceMatch) {
      inCodeBlock = !inCodeBlock;
      continue;
    }

    // Detect $$ as math block fences.
    if (line.trim() === '$$') {
      inMathBlock = !inMathBlock;
      continue;
    }

    // Skip lines that are in a code block, heading, or math block
    // NOTE: We skip headings and code blocks entirely but for math blocks
    // we need to check if the line contains code-like patterns outside of math expressions
    if (inCodeBlock || /^\s*#/.test(line)) {
      continue;
    }

    // For math blocks, we need to be more nuanced - only skip if the line doesn't contain
    // code-like patterns outside of LaTeX expressions
    if (inMathBlock) {
      // Check for shell-like patterns that should still be flagged even in math blocks
      // This regex matches:
      // 1. grep/export followed directly by $word: grep $pattern
      // 2. export with variable assignment: export x=$value
      const hasShellPattern = /(?:grep\s+\$\w+|export\s+(?:\w+=)?\$\w+)/.test(line);
      if (hasShellPattern) {

        // Continue processing this line to catch the shell pattern
      } else {
        continue;
      }
    }
    const codeSpans = [];
    const spanRegex = /`[^`]+`/g;
    let spanMatch;
    while ((spanMatch = spanRegex.exec(line)) !== null) {
      codeSpans.push([spanMatch.index, spanMatch.index + spanMatch[0].length]);
    }
    const patterns = [/\b(?:\.?\/?[\w.-]+\/)+[\w.-]+\b/g,
    // directory or file path
    /\b(?=[^\d\s])[\w.-]*[a-zA-Z][\w.-]*\.[a-zA-Z0-9]{1,5}\b/g,
    // file name with letters
    /\b[a-zA-Z][\w.-]*\([^)]*\)/g,
    // simple function or command()
    /\B\.[\w.-]+\b/g,
    // dotfiles like .env
    /\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b/g,
    // environment variables like NODE_ENV
    /\b(?:PATH|HOME|TEMP|TMPDIR|USER|SHELL|PORT|HOST)\b/g,
    // env vars
    /\B--?[a-zA-Z][\w-]*\b/g,
    // CLI flags

    // common CLI commands like "git clone" or "npm install"
    /\b(?:git|npm|pip|yarn|docker|brew|cargo|pnpm)\s+[a-z][\w-]*/g,
    // common CLI commands
    /\bimport\s+\w+/g,
    // import statements
    // host:port patterns, avoids bible verses like "1:10"
    /\b(?!\d+:\d+\b)[A-Za-z0-9.-]+:\d+\b/g, /\b[A-Z]+\+[A-Z]\b/g,
    // key combos like CTRL+C
    /\b(?:export|set)\s+[A-Za-z_][\w.-]*=\$?[\w.-]+\b/g,
    // shell variable assignments
    // Permissive shell variable usage, avoids prices like $50 or $19.99.
    // Allows single-digit variables like $1, but not $10 or more.
    /\$(?!\d{2,}(?:\.\d*)?\b|\d\.\d+)\S+/g];
    const flaggedPositions = new Set();
    const linkRegex = /!?\[[^\]]*\]\([^)]*\)/g;
    const wikiLinkRegex = /!?\[\[[^\]]+\]\]/g;
    /**
     * Determine if an index range is within a Markdown link or image.
     *
     * @param {string} text - Line being evaluated.
     * @param {number} start - Start index of match.
     * @param {number} end - End index of match.
     * @returns {boolean}
     */
    function inMarkdownLink(text, start, end) {
      let m;
      linkRegex.lastIndex = 0;
      while ((m = linkRegex.exec(text)) !== null) {
        if (start >= m.index && end <= m.index + m[0].length) {
          return true;
        }
      }
      return false;
    }

    /**
     * Check if an index range falls inside a wiki-style link.
     *
     * @param {string} text - Line being evaluated.
     * @param {number} start - Start index of match.
     * @param {number} end - End index of match.
     * @returns {boolean} True when the range is within a wiki link.
     */
    function inWikiLink(text, start, end) {
      let m;
      wikiLinkRegex.lastIndex = 0;
      while ((m = wikiLinkRegex.exec(text)) !== null) {
        if (start >= m.index && end <= m.index + m[0].length) {
          return true;
        }
      }
      return false;
    }

    /**
     * Check if an index range falls inside an HTML comment.
     *
     * @param {string} text - Line being evaluated.
     * @param {number} start - Start index of match.
     * @param {number} end - End index of match.
     * @returns {boolean} True when the range is within an HTML comment.
     */
    function inHtmlComment(text, start, end) {
      const commentRegex = /<!--.*?-->/g;
      let m;
      while ((m = commentRegex.exec(text)) !== null) {
        if (start >= m.index && end <= m.index + m[0].length) {
          return true;
        }
      }
      return false;
    }

    /**
     * Check if an index range falls inside a LaTeX math expression.
     * Handles both inline ($...$) and block ($$...$$) math expressions.
     * Distinguishes between LaTeX math and shell variables like $value.
     *
     * @param {string} text - Line being evaluated.
     * @param {number} start - Start index of match.
     * @param {number} end - End index of match.
     * @returns {boolean} True when the range is within a LaTeX math expression.
     */
    function inLatexMath(text, start, end) {
      // Check for inline math expressions ($...$)
      const inlineMathRegex = /\$([^$]+?)\$/g;
      let m;
      while ((m = inlineMathRegex.exec(text)) !== null) {
        const content = m[1];
        const isMathLike = /[\\{}^_]/.test(content) ||
        // Contains LaTeX special characters
        /[a-zA-Z][+\-*/=<> ]/.test(content) ||
        // Contains variables in equations
        / [+\-*/=] /.test(content) ||
        // Contains operators with spacing
        !/^\d+(\.\d+)?$/.test(content.trim()); // Not just a number (price)

        if (isMathLike && start >= m.index && end <= m.index + m[0].length) {
          return true;
        }
      }

      // Check for block math expressions ($$...$$) on a single line
      const blockMathRegex = /\$\$([^$]|\$[^\$])*\$\$/g;
      blockMathRegex.lastIndex = 0; // Reset regex state
      while ((m = blockMathRegex.exec(text)) !== null) {
        if (start >= m.index && end <= m.index + m[0].length) {
          return true;
        }
      }

      // If the line contains common LaTeX math functions, it's likely math-related.
      if (/\\(?:sum|frac|int|lim|sqrt|sin|cos|log|alpha|beta|gamma|delta|theta|pi|sigma)\b/.test(text)) {
        return true;
      }
      return false;
    }

    /**
     * Heuristically determine if a string looks like a file path.
     * This is used to reduce false positives from natural language
     * that can resemble a path (e.g., "pass/fail", "read/write").
     *
     * @param {string} str - Text to evaluate.
     * @returns {boolean} True if the string resembles a file path.
     */
    function isLikelyFilePath(str) {
      // Paths must contain a slash.
      if (!str.includes('/')) {
        return false;
      }

      // Paths with spaces are uncommon in un-quoted prose.
      if (/\s/.test(str)) {
        return false;
      }
      const segments = str.split('/');

      // Reject if all segments are numeric (e.g., "1/2", "2023/10/15").
      // Allows for empty segments from leading/trailing slashes.
      if (segments.every(s => /^\d+$/.test(s) || s === '')) {
        return false;
      }

      // For simple "a/b" paths without file extensions, be more skeptical.
      if (segments.length === 2 && !/\.[^/]+$/.test(segments[1])) {
        // Avoids flagging common short phrases like "on/off", "i/o".
        if (segments[0].length <= 2 || segments[1].length <= 2) {
          return false;
        }
      }

      // A likely path should contain at least one letter.
      return /[a-zA-Z]/.test(str);
    }
    for (const pattern of patterns) {
      pattern.lastIndex = 0;
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const fullMatch = match[0];
        const start = match.index;
        const end = start + fullMatch.length;

        // For the path pattern, apply extra heuristics to avoid false positives
        // on natural language like "read/write" or "pass/fail".
        if (pattern.source.includes('\\/') && !isLikelyFilePath(fullMatch)) {
          continue;
        }

        // Skip if inside a code span
        if (codeSpans.some(([s, e]) => start >= s && end <= e)) {
          continue;
        }
        // Skip if inside a Markdown link, wiki link, or HTML comment
        if (inMarkdownLink(line, start, end) || inWikiLink(line, start, end) || inHtmlComment(line, start, end)) {
          // eslint-disable-next-line no-console

          continue;
        }
        // Skip if in ignored terms
        if (_sharedConstants.backtickIgnoredTerms.has(fullMatch)) {
          // eslint-disable-next-line no-console

          continue;
        }
        // Skip if already flagged
        if (flaggedPositions.has(start)) {
          // eslint-disable-next-line no-console

          continue;
        }
        // Only skip if this match is inside a true LaTeX math region
        if (inLatexMath(line, start, end)) {
          // eslint-disable-next-line no-console

          continue;
        }
        // Skip if inside a URL (e.g., after http:// or https://)
        const urlRegex = /https?:\/\/[\w\-._~:/?#[\]@!$&'()*+,;=%]+/g;
        let urlMatch;
        let isInUrl = false;
        while ((urlMatch = urlRegex.exec(line)) !== null) {
          if (start >= urlMatch.index && end <= urlMatch.index + urlMatch[0].length) {
            isInUrl = true;
            break;
          }
        }
        if (isInUrl) {
          // eslint-disable-next-line no-console

          continue;
        }

        // For shell patterns with $ variables, prioritize reporting the whole command
        if (fullMatch.includes('$') && fullMatch.includes(' ') && (fullMatch.includes('grep') || fullMatch.includes('export'))) {
          // This is a shell command - report it and skip further matches on this line
          onError({
            lineNumber,
            detail: `Wrap command ${fullMatch} in backticks.`,
            context: fullMatch,
            range: [start + 1, fullMatch.length],
            // Convert to 1-indexed
            fixInfo: {
              editColumn: start + 1,
              deleteCount: fullMatch.length,
              insertText: `\`${fullMatch}\``
            }
          });
        } else if (!fullMatch.startsWith('$')) {
          // For non-shell variables, report normally
          onError({
            lineNumber,
            detail: `Wrap code-like element ${fullMatch} in backticks.`,
            context: fullMatch,
            range: [start + 1, fullMatch.length],
            // Convert to 1-indexed
            fixInfo: {
              editColumn: start + 1,
              deleteCount: fullMatch.length,
              insertText: `\`${fullMatch}\``
            }
          });
        }
        flaggedPositions.add(start);
      }
    }
  }
}
var _default = exports.default = {
  names: ['backtick-code-elements', 'BCE001'],
  description: 'Require code snippets, folder names and directories to be wrapped in backticks.',
  tags: ['style', 'code', 'prose'],
  parser: 'micromark',
  function: backtickCodeElements,
  fixable: true
};
module.exports = exports.default;
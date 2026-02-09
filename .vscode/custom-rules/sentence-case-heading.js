// @ts-check

/**
 * Custom markdownlint rule that enforces sentence case for headings.
 * Extracted helpers improve readability and performance.
 */

import { specialCasedTerms as defaultSpecialCasedTerms } from './shared-constants.js';

/**
 * Extract the plain heading text from tokens.
 * @param {object[]} tokens
 * @param {string[]} lines
 * @param {object} token
 * @returns {string} The extracted heading text.
 */
function extractHeadingText(tokens, lines, token) {
  const lineNumber = token.startLine;
  const lineText = lines[lineNumber - 1];
  const seq = tokens.find(
    (t) => t.type === 'atxHeadingSequence' &&
            t.startLine === lineNumber &&
            t.startColumn === token.startColumn
  );
  if (seq) {
    const textStartColumn = seq.endColumn;
    const text = lineText.substring(textStartColumn - 1, token.endColumn - 1);
    return text.replace(/<!--.*-->/g, '').trim();
  }
  const match = lineText.match(/^#+\s*(.*)/);
  return match && match[1] ? match[1].replace(/<!--.*-->/g, '').trim() : '';
}

/**
 * Main rule implementation.
 * @param {import("markdownlint").RuleParams} params
 * @param {import("markdownlint").RuleOnError} onError
 */
function basicSentenceCaseHeadingFunction(params, onError) {
  if (
    !params ||
    !params.parsers ||
    !params.parsers.micromark ||
    !params.parsers.micromark.tokens ||
    !Array.isArray(params.lines) ||
    typeof onError !== 'function'
  ) {
    return;
  }

  const tokens = params.parsers.micromark.tokens;
  const lines = params.lines;
  const config = params.config?.['sentence-case-heading'] || params.config?.SC001 || {};
  // Support both new `specialTerms` and old `technicalTerms`/`properNouns` for user config
  const userSpecialTerms = config.specialTerms || [];
  const userTechnicalTerms = config.technicalTerms || [];
  const userProperNouns = config.properNouns || [];
  const allUserTerms = [...userSpecialTerms, ...userTechnicalTerms, ...userProperNouns];

  const specialCasedTerms = { ...defaultSpecialCasedTerms };
  if (Array.isArray(allUserTerms)) { // User terms are added with their correct casing
    allUserTerms.forEach((term) => {
      if (typeof term === 'string') {
        specialCasedTerms[term.toLowerCase()] = term;
      }
    });
  }

  /**
   * Converts a string to sentence case, respecting preserved segments.
   * @param {string} text The text to convert.
   * @returns {string | null} The fixed text, or null if no change is needed.
   */
  function toSentenceCase(text) {
    const preserved = [];
    const preservedSegmentsRegex = /`[^`]+`|\[[^\]]+\]\([^)]+\)|\[[^\]]+\]|\b(v?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9.]+)?)\b|\b(\d{4}-\d{2}-\d{2})\b|(\*\*|__)(.*?)\1|(\*|_)(.*?)\1/g;
    const processed = text
      .replace(preservedSegmentsRegex, (m) => {
        preserved.push(m);
        return `__P_${preserved.length - 1}__`;
      });
    const words = processed.split(/\s+/).filter(Boolean);
    const firstWordIndex = words.findIndex((w) => !w.startsWith('__P_'));
    if (firstWordIndex === -1) { return null; }

    let firstVisibleWordCased = false;
    const fixedWords = words.map((w) => {
      if (w.startsWith('__P_')) return w;
      const lower = w.toLowerCase();
      if (specialCasedTerms[lower]) return specialCasedTerms[lower];
      if (!firstVisibleWordCased) {
        firstVisibleWordCased = true;
        return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
      }
      return w.toLowerCase();
    });
    let fixed = fixedWords.join(' ');

    fixed = fixed.replace(/__P_(\d+)__/g, (_, idx) => preserved[Number(idx)]);

    return fixed === text ? null : fixed;
  }

  function getFixInfoForHeading(line, text) {
    const match = /^(#{1,6})(\s+)(.*)$/.exec(line);
    if (!match) {
      return undefined;
    }
    const prefixLength = match[1].length + match[2].length;

    const preserved = [];
    const fixedText = toSentenceCase(text);

    if (!fixedText) {
      return undefined;
    }
    return {
      editColumn: prefixLength + 1,
      deleteCount: text.length,
      insertText: fixedText
    };
  }

  /**
   * Report a violation with auto-fix information.
   * @param {string} detail - Description of the issue.
   * @param {number} lineNumber - Line number for context.
   * @param {string} headingText - Heading text in question.
   * @param {string} line - Original source line.
   */
  function reportForHeading(detail, lineNumber, headingText, line) {
    const commentIndex = line.indexOf('<!--');
    const headingContent = commentIndex !== -1 ?
      line.slice(0, commentIndex).trimEnd() :
      line;
    const textToFix = headingContent.replace(/^#+\s*/, '');

    onError({
      lineNumber,
      detail,
      context: headingText,
      fixInfo: getFixInfoForHeading(line, textToFix)
    });
  }

  /**
   * Determine indices of words that are part of multi-word proper nouns.
   * @param {string[]} words - Tokenized heading words.
   * @returns {Set<number>} Indices that should be ignored during case checks.
   */
  function getProperPhraseIndices(words) {
    const indices = new Set();
    const lowerWords = words.map((w) => w.toLowerCase());
    Object.keys(specialCasedTerms).forEach((key) => {
      if (!key.includes(' ')) {
        return;
      }
      const parts = key.split(' ');
      for (let i = 0; i <= lowerWords.length - parts.length; i++) {
        const match = parts.every((p, j) => lowerWords[i + j] === p);
        if (match) {
          for (let j = 0; j < parts.length; j++) {
            indices.add(i + j);
          }
        }
      }
    });
    return indices;
  }

  /**
   * Validate multi-word proper nouns for correct capitalization.
   * @param {string} text - Original heading text.
   * @param {number} lineNumber - Line number for error reporting.
   * @returns {boolean} True if a violation was reported.
   */
  function validateProperPhrases(text, lineNumber) {
    for (const [phrase, expected] of Object.entries(specialCasedTerms)) {
      if (!phrase.includes(' ')) {
        continue;
      }
      const regex = new RegExp(`\\b${phrase}\\b`, 'i');
      const match = regex.exec(text);
      if (match && match[0] !== expected) {
        onError({
          lineNumber,
          detail: `Phrase "${match[0]}" should be "${expected}".`,
          context: text
        });
        return true;
      }
    }
    return false;
  }

  /**
   * Determine if all non-acronym words are uppercase.
   * @param {string[]} words - Words extracted from the heading.
   * @returns {boolean} True when every relevant word is uppercase.
   */
  function isAllCapsHeading(words) {
    const relevant = words.filter(
      (w) =>
        w.length > 1 &&
        !(w.startsWith('__PRESERVED_') && w.endsWith('__'))
    );
    const allCaps = relevant.filter((w) => w === w.toUpperCase());
    return (
      relevant.length > 1 &&
      allCaps.length === relevant.length &&
      !/\d/.test(relevant.join(''))
    );
  }

  /**
   * Validates a string for sentence case and reports errors.
   * @param {string} headingText The text to validate.
   * @param {number} lineNumber The line number of the text.
   * @param {string} sourceLine The full source line.
   * @param {Function} reportFn The function to call to report an error.
   */
  function validate(headingText, lineNumber, sourceLine, reportFn) {
    if (!headingText || headingText.trim().length === 0) {
      return;
    }
    
    // Debug logging
    if (process.env.DEBUG === 'markdownlint-trap*' || params.config?.debug) {
      console.log(`Validating text at line ${lineNumber}: "${headingText}"`);
    }
    
    // Strip leading emoji or symbol characters before analysis
    headingText = headingText
      .replace(/^[\u{1F000}-\u{1FFFF}\u{2000}-\u{3FFF}\u{FE0F}]+\s*/u, '')
      .trim();
    if (!headingText) {
      return;
    }

    const codeContentRegex = /`[^`]+`|\([A-Z0-9]+\)/g;
    const matches = [...headingText.matchAll(codeContentRegex)];
    const totalCodeLength = matches.reduce((sum, m) => sum + m[0].length, 0);
    if (totalCodeLength > 0 && totalCodeLength / headingText.length > 0.4) {
      return;
    }

    // If the heading consists only of numbers and symbols after removing markup,
    // it's likely a non-prose heading (e.g., a version in a changelog)
    // that should be ignored.
    const textWithoutMarkup = headingText
      .replace(/`[^`]+`/g, '')
      .replace(/\[([^\]]+)\]/g, '$1');
    if (!/[a-zA-Z]/.test(textWithoutMarkup)) {
      return;
    }

    if (validateProperPhrases(headingText, lineNumber)) {
      return;
    }

    const preservedSegments = [];
    let processed = headingText
      .replace(/`([^`]+)`/g, (m) => {
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      })
      .replace(/\[[^\]]+\]\([^)]+\)|\[[^\]]+\]/g, (m) => {
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      })
      .replace(/\b(v?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9.]+)?)\b/g, (m) => {
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      })
      .replace(/\b(\d{4}-\d{2}-\d{2})\b/g, (m) => {
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      })
      .replace(/(\*\*|__)(.*?)\1/g, (m) => { // Bold
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      })
      .replace(/(\*|_)(.*?)\1/g, (m) => { // Italic
        preservedSegments.push(m);
        return `__PRESERVED_${preservedSegments.length - 1}__`;
      });

    const clean = processed
      .replace(/[\#\*_~!+=\{\}|:;"<>,.?\\]/g, ' ')
      .trim();
    if (!clean) {
      return;
    }
    if (/^\d+[\d./-]*$/.test(clean)) {
      return;
    }
    const words = clean.split(/\s+/).filter((w) => w.length > 0);
    const phraseIgnore = getProperPhraseIndices(words);
    if (words.every((w) => w.startsWith('__PRESERVED_') && w.endsWith('__'))) {
      return;
    }

    let firstIndex = 0;
    const numeric = /^[-\d.,/]+$/;
    const startsWithYear = /^\d{4}(?:\D|$)/.test(headingText);
    const isSingleWordHyphen = headingText.trim().split(/\s+/).length === 1 && headingText.includes('-');
    while (
      firstIndex < words.length &&
      ((words[firstIndex].startsWith('__PRESERVED_') &&
        words[firstIndex].endsWith('__')) ||
        numeric.test(words[firstIndex]))
    ) {
      firstIndex++;
    }
    if (firstIndex >= words.length) {
      return; // No valid words found
    }

    // Validate the first word's casing
    const firstWord = words[firstIndex];
    const firstWordLower = firstWord.toLowerCase();
    const expectedFirstWordCasing = specialCasedTerms[firstWordLower];

    // Skip numeric headings like "2023 updates"
    if (/^\d/.test(firstWord)) {
      return;
    }

    const hyphenBase = firstWordLower.split('-')[0];
    const hyphenExpected = specialCasedTerms[hyphenBase];

    if (startsWithYear) {
      return;
    }

    if (!phraseIgnore.has(firstIndex) && !firstWord.startsWith('__PRESERVED_')) { // Skip if part of ignored phrase or preserved
      if (expectedFirstWordCasing) {
        // If it's a known proper noun or technical term, check if its casing matches the expected one.
        if (firstWord !== expectedFirstWordCasing) {
          reportFn(
            `First word "${firstWord}" should be "${expectedFirstWordCasing}".`,
            lineNumber,
            headingText,
            sourceLine
          );
          return;
        }
      } else if (hyphenExpected) {
        const expected = hyphenExpected + firstWord.slice(hyphenExpected.length);
        if (firstWord !== expected) {
          reportFn(
            `First word "${firstWord}" should be "${expected}".`,
            lineNumber,
            headingText,
            sourceLine
          );
          return;
        }
      } else {
        // For other words, ensure the first letter is capitalized and the rest are lowercase.
        const expectedSentenceCase = firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
        if (firstWord !== expectedSentenceCase) {
          // Allow short acronyms (<= 4 chars, all caps)
          if (!(firstWord.length <= 4 && firstWord.toUpperCase() === firstWord)) {
            reportFn(
              "Heading's first word should be capitalized.",
              lineNumber,
              headingText,
              sourceLine
            );
            return;
          }
        }
      }
    }

    if (isAllCapsHeading(words)) {
      reportFn(
        'Heading should not be in all caps.', lineNumber, headingText, sourceLine
      );
      return;
    }

    const colonIndex = headingText.indexOf(':');
    for (let i = firstIndex + 1; i < words.length; i++) {
      if (phraseIgnore.has(i)) {
        continue;
      }
      const word = words[i];
      const wordLower = word.toLowerCase();
      const expectedWordCasing = specialCasedTerms[wordLower];

      const wordPos = headingText.indexOf(word);
      if (colonIndex !== -1 && colonIndex < 10 && wordPos > colonIndex) {
        const afterColon = headingText.slice(colonIndex + 1).trimStart();
        if (afterColon.startsWith(word)) {
          continue; // allow capitalization after colon
        }
      }
      if (word.startsWith('__PRESERVED_') && word.endsWith('__')) {
        continue;
      }
      if (
        headingText.includes(`(${word})`) ||
        (headingText.includes('(') && headingText.includes(')') &&
          headingText.substring(headingText.indexOf('('), headingText.indexOf(')') + 1).includes(word))
      ) {
        continue;
      }

      if (expectedWordCasing) {
        // If it's a known proper noun or technical term, check if its casing matches the expected one.
        if (
          word !== expectedWordCasing &&
          !(expectedWordCasing === 'Markdown' && wordLower === 'markdown')
        ) {
          reportFn(
            `Word "${word}" should be "${expectedWordCasing}".`,
            lineNumber,
            headingText,
            sourceLine
          );
          return;
        }
      } else { // Word is not in specialCasedTerms
        // Acronym detection: Allow short (<= 4 chars) all-uppercase words,
        // and the pronoun "I", to retain their casing. Otherwise, enforce lowercase.
        // Longer acronyms or specific brand names should be added to specialCasedTerms.
        // For other words, ensure they are lowercase, unless they are short acronyms or 'I'.
      }

      if (word.includes('-')) {
        const parts = word.split('-');
        if (parts.length > 1 && parts[1] !== parts[1].toLowerCase()) {
          reportFn(
            `Word "${parts[1]}" in heading should be lowercase.`, lineNumber, headingText, sourceLine
          );
          return;
        }
      }

      if (
        word !== word.toLowerCase() &&
        !(word.length <= 4 && word === word.toUpperCase()) && // Allow short acronyms
        word !== 'I' && // Allow the pronoun "I"
        !expectedWordCasing && // If it's not a known proper noun/technical term
        !word.startsWith('PRESERVED')
      ) {
        reportFn(
          `Word "${word}" in heading should be lowercase.`, lineNumber, headingText, sourceLine
        );
        return;
      }
    }
  }

  tokens.forEach((token) => {
    if (token.type === 'atxHeading') {
      const lineNumber = token.startLine;
      if (lineNumber === 1 && /README\.md$/i.test(params.name || '')) {
        return;
      }
      const sourceLine = lines[lineNumber - 1];
      const headingText = extractHeadingText(tokens, lines, token);
      validate(headingText, lineNumber, sourceLine, reportForHeading);
    } else if (token.type === 'paragraph') {
      const lineNumber = token.startLine;
      const sourceLine = lines[lineNumber - 1];
      // Debug the source line to see what we're working with
      if (process.env.DEBUG === 'markdownlint-trap*' || params.config?.debug) {
        console.log(`Processing line ${lineNumber}: "${sourceLine}"`);
      }

      // Enhanced regex to better match list items with bold text
      // This handles both standalone bold items and those with colons
      // Using a more permissive regex that should match all bold text in list items
      const listMatch = sourceLine.match(/^\s*[-*+]\s+(\*\*|__)(.+?)(\*\*|__)/);

      if (listMatch) {
        // listMatch[1] is the opening marker (** or __)
        // listMatch[2] is the content inside the bold markers
        // listMatch[3] is the closing marker (** or __)
        const originalBoldText = listMatch[2];
        // Get the text to validate - either before the colon or the entire text if no colon
        const textToValidate = originalBoldText.includes(':') ? 
          originalBoldText.split(':')[0] : originalBoldText;
          
        // Debug the extracted text
        if (process.env.DEBUG === 'markdownlint-trap*' || params.config?.debug) {
          console.log(`Line ${lineNumber}: Extracted bold text: "${originalBoldText}", validating: "${textToValidate}"`);
        }
        
        // Instead of trying to validate directly, use the existing validate function
        // which already has all the logic for sentence case validation

        const reportFn = (detail, ln, validatedText, line) => {
          const fixedPart = toSentenceCase(validatedText);
          if (!fixedPart) return;
          
          const restOfBold = originalBoldText.slice(validatedText.length);
          const newBoldText = fixedPart + restOfBold;

          const fixMatch = line.match(/^(\s*[-*+]\s+(?:\*\*|__))(.+?)(?:(?:\*\*|__).*)$/);
          if (!fixMatch) return;

          const prefixLength = fixMatch[1].length;
          onError({
            lineNumber: ln, detail, context: originalBoldText, 
            fixInfo: {
              editColumn: prefixLength + 1, deleteCount: originalBoldText.length, insertText: newBoldText
            }
          });
        };
        // Debug logging to help troubleshoot
        if (process.env.DEBUG === 'markdownlint-trap*' || params.config?.debug) {
          console.log(`Processing list item at line ${lineNumber}: "${textToValidate}"`); 
        }
        
        // Direct validation for bold list items
        const words = textToValidate.split(/\s+/);
        
        // Check if first word is capitalized correctly
        if (words.length > 0) {
          const firstWord = words[0];
          const wordLower = firstWord.toLowerCase();
          const expectedCasing = specialCasedTerms[wordLower];
          
          // If it's a special term, check if it matches expected casing
          if (expectedCasing && firstWord !== expectedCasing) {
            onError({
              lineNumber,
              detail: `First word "${firstWord}" should be "${expectedCasing}".`,
              context: originalBoldText
            });
          } 
          // Otherwise check if first letter is capitalized and rest is lowercase
          else if (!expectedCasing && firstWord !== firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase()) {
            // Allow acronyms (all caps, 4 chars or less)
            if (!(firstWord.length <= 4 && firstWord === firstWord.toUpperCase())) {
              onError({
                lineNumber,
                detail: "Bold text's first word should be capitalized.",
                context: originalBoldText
              });
            }
          }
          
          // Check for all caps
          const allCaps = words.filter(w => w === w.toUpperCase() && w.length > 1);
          if (words.length > 1 && allCaps.length === words.length) {
            onError({
              lineNumber,
              detail: 'Bold text should not be in all caps.',
              context: originalBoldText
            });
          }
          
          // Check remaining words for proper case
          for (let i = 1; i < words.length; i++) {
            const word = words[i];
            const wordLower = word.toLowerCase();
            const expectedCasing = specialCasedTerms[wordLower];
            
            // Skip single-letter words, pronouns, and special terms
            if (word.length <= 1 || word === 'I' || expectedCasing) {
              continue;
            }
            
            // Words that aren't proper nouns should be lowercase
            if (word !== wordLower && !(/^[A-Z][a-z]+$/.test(word) && specialCasedTerms[word])) {
              onError({
                lineNumber,
                detail: `Word "${word}" should be lowercase in bold text.`,
                context: originalBoldText
              });
            }
          }
        }
      }
    }
  });
}

export default {
  names: ['sentence-case-heading', 'SC001'],
  description: 'Ensures ATX (`# `) headings use sentence case: first word capitalized, rest lowercase except acronyms and "I".',
  tags: ['headings', 'style', 'custom', 'basic'],
  parser: 'micromark',
  function: basicSentenceCaseHeadingFunction
};

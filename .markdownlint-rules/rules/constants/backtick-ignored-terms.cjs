"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.ignoredTerms = void 0;
/**
 * @file A centralized list of terms to ignore for the `backtick-code-elements` rule.
 * @copyright 2023 
 */

// This set contains common abbreviations, acronyms, and technical terms
// that are often written without backticks. Adding them here helps reduce
// false positives from the `backtick-code-elements` rule.
// The list is case-sensitive.
const ignoredTerms = exports.ignoredTerms = new Set(['set up', 'github.com', 'ulca.edu', 'pass/fail',
// Common Abbreviations
'e.g.', 'i.e.', 'etc.', 'vs.', 'et al.', 'aka', 'viz.', 'N/A',
// Common Acronyms & Initialisms
'API', 'AJAX', 'CI', 'CD', 'CSS', 'DOM', 'GraphQL', 'GUID', 'HTML', 'IDE', 'IaaS', 'JS', 'JSON', 'JWT', 'OAuth', 'OS', 'PaaS', 'REST', 'SaaS', 'SDK', 'SQL', 'TS', 'UI', 'UX', 'URL', 'URI', 'UUID', 'XML', 'YAML',
// Common Tech Terms (often lowercase)
'api', 'cli', 'db', 'git', 'npm', 'os', 'pnpm', 'sdk', 'ui', 'ux', 'yarn',
// File extensions (without dot)
'css', 'go', 'html', 'java', 'js', 'jsx', 'json', 'kt', 'md', 'ps1', 'py', 'rb', 'rs', 'scss', 'sh', 'swift', 'toml', 'ts', 'tsx', 'xml', 'yaml', 'yml',
// Other
'localhost', 'regex']);
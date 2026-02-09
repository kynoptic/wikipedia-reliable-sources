"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _backtickCodeElements = _interopRequireDefault(require("../.vscode/custom-rules/backtick-code-elements.cjs"));
var _sentenceCaseHeading = _interopRequireDefault(require("../.vscode/custom-rules/sentence-case-heading.cjs"));
function _interopRequireDefault(e) { return e && e.__esModule ? e : { default: e }; }
/**
 * Export all custom rules as a single array for markdownlint.
 * @type {import('markdownlint').Rule[]}
 */
var _default = exports.default = [_backtickCodeElements.default, _sentenceCaseHeading.default];
module.exports = exports.default;
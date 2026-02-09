"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = void 0;
var _debug = _interopRequireDefault(require("debug"));
function _interopRequireDefault(e) { return e && e.__esModule ? e : { default: e }; }
/**
 * Base debug instance for the project.
 * Enable by setting `DEBUG=markdownlint-trap*`.
 */
const debug = (0, _debug.default)('markdownlint-trap');
var _default = exports.default = debug;
module.exports = exports.default;
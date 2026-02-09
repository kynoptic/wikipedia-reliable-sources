/**
 * @fileoverview Rule to enforce that URLs are always wrapped in a proper Markdown link.
 * @author 
 */

/**
 * @typedef {import("markdownlint").Rule} Rule
 * @typedef {import("markdownlint").RuleParams} RuleParams
 * @typedef {import("markdownlint").RuleOnError} RuleOnError
 */

/** @type {Rule} */
export default {
  names: ["wt/no-bare-urls"],
  description: "Bare URL used. Surround with < and >.",
  tags: ["links", "url"],
  function: 
    /**
     * @param {RuleParams} params
     * @param {RuleOnError} onError
     */
    function rule(params, onError) {
      // This rule relies on markdown-it's linkify option to identify bare URLs.
      // It flags any URL that was automatically converted into a link.
      // The fix is to wrap the URL in angle brackets, e.g., <http://example.com>.
      // Note: Ensure markdown-it is configured with { linkify: true } in your test setup.
      params.tokens.filter(t => t.type === "inline" && t.children).forEach(token => {
        token.children.forEach((child) => {
          if (child.type === "link_open" && child.info === "auto" && child.markup !== "autolink") {
            const href = child.attrGet("href");
            onError({ lineNumber: child.lineNumber, detail: "Bare URL used.", context: href });
          }
        });
      });
    },
};
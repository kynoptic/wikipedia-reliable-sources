---
trigger: glob
description: "Best practices for authoring Windsurf rule files."
globs: ".windsurf/rules/*.md,.windsurf/rules/**/*.md,global_rules.md"
---
# Windsurf rule authoring best practices

- Begin every rule file with a YAML front matter block, including at minimum: `trigger`, `description`, and `globs` (if applicable).
- Use an H1 heading that clearly summarizes the intent of the rule.
- Write bullet point rules using imperative, specific, and token-efficient language.
- Avoid vague guidance; each rule must be immediately actionable and minimal.
- Limit rules to 10 bullet points unless additional specificity is absolutely required. For longer rules, use sub-sections or references to keep each bullet actionable.
- Select the appropriate `trigger` type (`manual`, `always`, `model_decision`, `glob`) based on context.
- Use `glob` trigger when the rule targets specific file types or directories.
- Include a `name` field for rules that may be mentioned in conversations or other rule files.
- Follow Wave 8+ Windsurf documentation and Cascade formatting standards rigorously.
- Run the `repo-naming-check` workflow to validate rule filenames follow the naming pattern.
- Write each line exactly as you’d tell a junior dev. Short, direct, imperative sentences work best.

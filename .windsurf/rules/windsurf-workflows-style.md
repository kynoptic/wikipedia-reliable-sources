---
trigger: glob
description: "Best practices for writing Windsurf workflow files that automate developer tasks using Cascade agents."
globs: ".windsurf/workflows/*.md,.windsurf/workflows/**/*.md"
---
# Windsurf workflow authoring guidelines

- Use Markdown `.md` files with a top-level `# Title`, a clear description, and a numbered list of steps.
- Ensure the description explains the workflow’s purpose, output, and any key tools or preconditions.
- Never start with a user input step, and never prompt for confirmation or clarification after Step 1.
- Decompose multi-step tasks into linear, executable instructions suitable for AI agent execution.
- Write each step as a bolded title followed by an imperative instruction (e.g., **Install dependencies** – Use `npm install` to…).
- Favor tool-specific commands (e.g., terminal, file I/O, git) and avoid vague or generic language.
- Incorporate conditional logic or retries where appropriate; ensure agents can act autonomously without external input.
- Maintain state continuity across steps using consistent references (e.g., filenames, paths).
- Write each workflow step exactly as you’d tell a junior dev. Short, direct, imperative sentences work best.
- Conclude with a step that summarizes outputs or suggests follow-up actions.
- Use the `repo-naming-check` workflow to verify workflow filenames follow the naming pattern.

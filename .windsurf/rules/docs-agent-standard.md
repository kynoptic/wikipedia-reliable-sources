---
trigger: glob
description: "Canonical standard for `AGENT.md` files that provide comprehensive context and safety guidance for AI coding agents."
globs: "**/AGENT.md"
---
# Canonical standard for `AGENT.md` files

- Begin with a concise **Project overview** describing the software’s purpose and what high-level user goals it supports.
- Include a **Repository structure** section listing key folders and files, each with a one-line description.
- Provide explicit **Setup, run, and test commands** the agent can copy and use as-is.
- Summarize **Coding guidelines** as specific, enforceable rules (e.g., naming, formatting, architecture).
- List any **Tools and APIs** the agent can access, including libraries, env vars, or runtime capabilities.
- Define **Agent roles** (if multiple agents are used) and explain how they interact or communicate.
- Add a **Constraints and safety** section stating non-negotiable rules (e.g., “NEVER commit secrets”).
- Optionally include **Known issues** or contextual caveats (e.g., flaky tests or migration workarounds).
- Provide one or two **Example tasks** with file names and expected outputs to guide agent behavior.
- Organize content with clear headings (##) and bullet points; avoid long prose blocks or ambiguous phrasing.


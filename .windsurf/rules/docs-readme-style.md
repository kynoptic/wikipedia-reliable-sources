---
trigger: glob
description: "Ensure README.md files serve as accessible orientation points that guide users to appropriate documentation without duplicating Diátaxis content."
globs: "**/README.md"
---
# README structure and content requirements

## Main project README.md

- Begin with a clear overview describing the project's name, purpose, and core problem it solves.
- Include a **Key features** section with a bullet list summarizing major capabilities.
- Provide **Getting started** section that links to appropriate Diátaxis documentation rather than duplicating content:
  - Link to `docs/tutorials/getting-started.md` for new users
  - Link to `docs/reference/installation.md` for detailed installation options
  - Link to `docs/how-to/` for common tasks
- Add a minimal **Usage example** that demonstrates core functionality without becoming a tutorial.
- State the **Project status** and link to roadmap documentation in `/docs/explanations/` if detailed.
- Clearly identify the **License** and provide attribution where appropriate.
- Link to **Further resources** organized by user intent (learning, problem-solving, reference, understanding).

## Folder README.md files

- Create only when needed: if a folder's purpose is self-evident from its name and contents, omit the README.
- Serve as **orientation points** that explain why the folder exists and how to navigate it.
- Keep minimal: 1–2 sentence purpose, when to use, and links to deeper docs; avoid exhaustive file listings.
- For `/docs/` subfolders, clarify the Diátaxis type and when to consult that area.
- Use clear headings and bullets for scanning, and avoid duplicating content from other docs.


Create or update the main `README.md` file in the project root:

1. **Analyze project code and documentation** – Scan the repository to understand the project's purpose and structure. Review `package.json`, `pyproject.toml`, existing `.md` files (e.g., CONTRIBUTING, docs), and the main source code entry points to infer functionality, tech stack, and architectural intent.

2. **Check for existing README** – Use the terminal to determine if `/README.md` exists in the root directory.

3. **Define README structure** – Construct a standardized README outline with the following sections:
   - Project overview
   - Key features
   - Installation instructions
   - Usage instructions
     - Usage example
   - Project status and roadmap
   - License and attribution
   - Links to further resources

4. **Populate content** – Populate each section. Include:
   - **Project overview**: A short description of the project.
   - **Key features**: Bullet points summarizing major capabilities.
   - **Installation**: Steps for installation with appropriate alerts (use IMPORTANT for prerequisites, WARNING for destructive commands, TIP for best practices).
   - **Usage**: Explain usage and provide an example command with relevant alerts.
   - **Project status and roadmap**: Indicate active/beta status and link to `ROADMAP.md` if present.
   - **License and attribution**: MIT or appropriate license, and any necessary attributions.
   - **Resources**: Links to `docs/`, `CONTRIBUTING.md`, GitHub Issues, etc.

   **Alert usage guidelines**: Follow GitHub Markdown Alerts standards from `docs-github-alerts.md`:
   - Use IMPORTANT for critical prerequisites or required steps
   - Use WARNING for destructive operations or security risks
   - Use CAUTION for compatibility issues or potential problems
   - Use TIP for best practices or helpful shortcuts
   - Use NOTE for supplementary context or clarification
   - Limit to 1-2 alerts per section maximum

   **Exact alert syntax** (copy exactly):
   ```markdown
   > [!NOTE]
   > Note content here

   > [!TIP]
   > Tip content here

   > [!IMPORTANT]
   > Important content here

   > [!WARNING]
   > Warning content here

   > [!CAUTION]
   > Caution content here
   ```

   **Optional illustrative emojis for navigation signposts**:
   - Use purposefully for 1-2 key sections maximum: `## 🚀 Getting started`, `## ✨ Features`, `## 📋 Requirements`, `## 🔧 Installation`
   - Choose emojis that enhance navigation and relate to content meaning
   - Apply consistently if used at all - don't mix emoji and non-emoji headings
   - Maximum 1 emoji per heading, functional purpose only (aid navigation, not decoration)

5. **Create or overwrite `/README.md`** –
   - If `/README.md` does not exist, create it using the standardized content.
   - If it exists, overwrite it to align with the current project state and documentation expectations.

6. **Add `/LICENSE` if missing** – Check for an existing `/LICENSE` file. If absent, generate a new MIT license (or other as specified in metadata or existing content).

7. **Verify README formatting** – Lint the README with `markdownlint` or similar tools to enforce consistent formatting. Automatically fix issues if supported by the linter.

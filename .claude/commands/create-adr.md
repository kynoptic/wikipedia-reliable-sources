Create a new Architecture Decision Record (ADR) in `docs/adr/` following these steps:

1. **Gather the decision inputs** – Confirm why the ADR is needed and collect references:
   - Identify the problem or opportunity driving the decision
   - List linked issues, RFCs, experiments, or PRs that provide supporting evidence
   - Capture stakeholders, reviewers, and affected teams

2. **Ensure ADR directory exists** – Verify the repository contains `docs/adr/`:
   - If missing, create it with `mkdir -p docs/adr`
   - Check for an ADR template (e.g., `docs/adr/ADR-template.md`) to reuse language or structure

3. **Determine the next ADR number** – Inspect existing ADRs and calculate the next sequential ID:
   - Use `ls docs/adr/adr-*.md 2>/dev/null | sort` to review current files
   - Extract the highest numeric suffix and increment it (e.g., highest `adr-011-*.md` → next is `012`)
   - When no ADRs exist, start with `001`
   - Store the zero-padded number (e.g., `ADR_NUMBER=$(printf "%03d" "$NEXT")`)

4. **Derive the ADR slug from the title** – Convert the decision title to a kebab-case slug:
   - Capture the human-readable title: `read -rp "ADR title: " ADR_TITLE`
   - Generate the slug with `ADR_SLUG=$(echo "$ADR_TITLE" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9]/-/g' -e 's/--*//g' -e 's/^-//' -e 's/-$//')`:
   - Combine number and slug for the filename: `docs/adr/adr-${ADR_NUMBER}-${ADR_SLUG}.md`

5. **Draft the ADR from the standard template** – Create the file using the approved sections:
   ```bash
   cat <<MARKDOWN > "docs/adr/adr-${ADR_NUMBER}-${ADR_SLUG}.md"
   # ADR-${ADR_NUMBER}: ${ADR_TITLE}

   ## Status
   Proposed

   ## Context
   <What is changing? What forces or constraints matter?>

   > [!IMPORTANT]
   > This decision affects [scope/impact area].

   ## Decision
   <Summarize the chosen option and rationale>

   ## Alternatives Considered
   1. **Option A** — <pros/cons>
   2. **Option B** — <pros/cons>

   ## Consequences
   ### Positive
   - <Expected benefits>

   ### Negative
   - <Known trade-offs or follow-up work>

   > [!CAUTION]
   > This decision involves [migration complexity/risks/limitations].

   ## Implementation Plan
   - [ ] <First step>
   - [ ] <Second step>

   > [!TIP]
   > Consider [best practice/optimization/helpful approach].

   ## Related Issues
   - Issue #<id>

   ## Date
   $(date +%Y-%m-%d)
   MARKDOWN
   ```
   - Replace placeholders with concrete details for the decision
   - Adjust the status (`Proposed`, `Accepted`, `Rejected`, etc.) as appropriate

   **GitHub Markdown Alerts in ADRs**: Use alerts strategically to highlight:
   - IMPORTANT for scope/impact of decision
   - CAUTION for migration complexity, risks, or future limitations
   - TIP for implementation best practices or optimization opportunities
   - NOTE for additional context or clarifications
   - WARNING for security implications or destructive consequences

   **Exact alert syntax** (copy exactly):
   ```markdown
   > [!IMPORTANT]
   > This decision affects the entire authentication architecture.

   > [!CAUTION]
   > Migration from the current system will require 2-3 weeks of effort.

   > [!TIP]
   > Consider implementing this change incrementally to reduce risk.

   > [!NOTE]
   > This approach aligns with industry standard practices.

   > [!WARNING]
   > This decision has security implications that must be reviewed.
   ```

   **Optional illustrative emojis for ADR sections**:
   - Use for ADR organization: `## 🎯 Context`, `## ✅ Decision`, `## ⚖️ Alternatives considered`, `## 📊 Consequences`
   - Apply consistently throughout ADR if used, maximum 1 emoji per heading
   - Choose emojis that aid navigation and relate to decision-making process

6. **Cross-reference supporting work** – Link the ADR to related resources:
   - Prompt for a related issue number.
     ```bash
     read -rp "Related issue number (optional): " ISSUE_NUM
     ```
   - If an issue number is provided, replace the placeholder in the ADR file and add a backlink comment to the issue.
     ```bash
     if [ ! -z "$ISSUE_NUM" ]; then
       sed -i '' "s/- Issue #<id>/- Issue #${ISSUE_NUM}/" "docs/adr/adr-${ADR_NUMBER}-${ADR_SLUG}.md"
       gh issue comment "$ISSUE_NUM" --body "This issue is addressed by [ADR-${ADR_NUMBER}: ${ADR_TITLE}](<link-to-adr-file-or-pr>)."
     fi
     ```
   - If the decision supersedes a previous ADR, manually note it in the Status block.

7. **Review for completeness and standards** – Validate the ADR content:
   - Ensure Context/Decision/Consequences sections convey clear rationale
   - Confirm spelling, grammar, and Markdown structure (run `npm run lint` if available)
   - Verify numbering matches the filename and there are no gaps

8. **Commit and communicate** – Stage the new ADR and share the update:
   - `git add docs/adr/adr-${ADR_NUMBER}-${ADR_SLUG}.md`
   - Draft a Conventional Commit message (e.g., `docs(adr): record Postgres provider decision`)
   - Notify stakeholders that the decision has been captured and request review if needed

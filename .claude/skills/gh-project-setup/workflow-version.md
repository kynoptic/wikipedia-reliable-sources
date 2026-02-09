---
name: git-project-setup
descriptive-title: Bootstrap planning project and milestones
description: Create and configure the GitHub project, custom fields, and automated workflows that enforce Value/Effort tracking and metadata hygiene across issues and PRs.
persona: You are an operations-focused maintainer establishing the planning infrastructure so that issues, branches, and PRs inherit consistent metadata.
tools: gh, Bash, Read, Write, Edit
---

# GitHub project and milestone setup

## Purpose
Stand up the planning infrastructure required by the global rules: a GitHub Projects (v2) board with custom fields (Value/Effort/Status), repository labels, dependency tracking, standard views, and automated issue management.

## Preconditions
- Maintainer access to the repository and its organization.
- `gh` CLI authenticated (`gh auth status`).
- GraphQL API permissions for managing projects (`gh auth refresh -s project` if needed).
- Repository has `.github/ISSUE_TEMPLATE/feature.md` and other templates in place.

## Step 1 — Create the project (Projects v2)
1. Choose a project name that describes your roadmap or workflow (e.g., `Product roadmap`, `Development workflow`).
2. Create the project at the organization scope so multiple repos can participate:

   ```bash
   ORG="your-org-name"
   PROJECT_NAME="Your project name"

   gh project create "$PROJECT_NAME" --organization "$ORG"
   PROJECT_ID=$(gh project list --owner "$ORG" --limit 50 --format json | jq -r \
     ".[] | select(.title == \"$PROJECT_NAME\") | .id")
   ```

3. Share the project link with the team so they can pin it in GitHub.

## Step 2 — Define project custom fields
Projects v2 requires GraphQL to add custom single-select fields (these are project-scoped).

   ```bash
   # Helper to create single-select custom fields for the project
   create_custom_field() {
     local name="$1"; shift
     local options="$1"; shift

     gh api graphql -f query='mutation($project:ID!, $data:ProjectV2SingleSelectFieldInput!) {
       addProjectV2Field(input:{projectId:$project, projectField:$data}) {
         projectV2Field { ... on ProjectV2SingleSelectField { id name } }
       }
     }' -F project="$PROJECT_ID" -F data="{\"name\":\"$name\",\"options\":[$options]}"
   }

   # Create project custom fields (these apply across all repos in the project)
   create_custom_field "Value" '{"name":"Essential"},{"name":"Useful"},{"name":"Nice-to-have"}'
   create_custom_field "Effort" '{"name":"Heavy"},{"name":"Moderate"},{"name":"Light"}'
   create_custom_field "Status" '{"name":"Backlog"},{"name":"Todo"},{"name":"Doing"},{"name":"Done"}'
   ```

Record the returned field IDs—they are needed for automation scripts.

## Step 2.5 — Setup repository labels
Repository labels are managed separately and are repository-scoped.

   ```bash
   # Create/update repository labels (these are specific to each repository)
   REPO="owner/repo-name"

   # Type labels
   gh label create "type:bug" --description "Something isn't working" --color "d73a4a" --repo "$REPO" || true
   gh label create "type:feature" --description "New feature or request" --color "a2eeef" --repo "$REPO" || true
   gh label create "type:chore" --description "Maintenance or cleanup" --color "fef2c0" --repo "$REPO" || true
   gh label create "type:docs" --description "Documentation" --color "0075ca" --repo "$REPO" || true

   # Area labels
   gh label create "area:frontend" --description "Frontend code" --color "1d76db" --repo "$REPO" || true
   gh label create "area:backend" --description "Backend code" --color "fbca04" --repo "$REPO" || true
   gh label create "area:api" --description "API related" --color "0e8a16" --repo "$REPO" || true
   gh label create "area:infra" --description "Infrastructure" --color "5319e7" --repo "$REPO" || true

   # Priority labels (alternative to custom fields if needed)
   gh label create "priority:high" --description "High priority" --color "b60205" --repo "$REPO" || true
   gh label create "priority:medium" --description "Medium priority" --color "fbca04" --repo "$REPO" || true
   gh label create "priority:low" --description "Low priority" --color "0e8a16" --repo "$REPO" || true
   ```

## Step 3 — Configure default views
1. Set board view grouped by `Status` for active planning.
2. Add a table view sorted by Value (desc) then Effort (asc) for backlog grooming.
3. Create filtered view for blocked issues: `is:blocked is:open`
4. Create critical path view for blocking issues: `is:blocking is:open sort:comments-desc`

Use the GitHub UI or GraphQL:

   ```bash
   gh api graphql -f query='mutation($project:ID!) {
     updateProjectV2(input:{projectId:$project, readme:"## How to use\n- Drag cards across Status columns for workflow tracking"}) {
       projectV2 { id }
     }
   }' -F project="$PROJECT_ID"
   ```

## Step 4 — Auto-add issues and PRs
Enable auto-add so new issues and PRs land in the project:

   ```bash
   gh project edit "$PROJECT_ID" \
     --add-repository "ultimate-ranks/ultimate-ranks-data" \
     --enable-item-creation
   ```

If CLI support is limited, configure via the web UI (Project settings → Auto-add).

## Step 5 — Configure issue defaults
Set up automation to ensure all new issues start with Status: Backlog:

   ```bash
   # Use GitHub Actions or project automation to set default Status
   # Example workflow in .github/workflows/issue-defaults.yml
   cat > .github/workflows/issue-defaults.yml << 'EOF'
   name: Set issue defaults
   on:
     issues:
       types: [opened]
   jobs:
     set-defaults:
       runs-on: ubuntu-latest
       steps:
         - name: Set Status to Backlog
           uses: actions/github-script@v6
           with:
             script: |
               github.rest.issues.addLabels({
                 owner: context.repo.owner,
                 repo: context.repo.repo,
                 issue_number: context.issue.number,
                 labels: ['status:backlog']
               });
   EOF
   ```

## Step 6 — Wire templates to metadata
1. Update issue templates to collect Value/Effort and ensure Status defaults to Backlog.
2. Ensure `.github/ISSUE_TEMPLATE/feature.md` includes checkboxes for metadata and links to the project.
3. Add automation scripts (optional):

   ```bash
   # Example: script to sync issue metadata from template responses
   python scripts/sync_issue_metadata.py --project "$PROJECT_ID"
   ```

## Step 7 — Document the setup
- Update `docs/process-issue-management.md` with project ID, field IDs, and milestone naming conventions.
- Capture automation commands in `docs/process.md` for new maintainers.

## Validation checklist
- [ ] Project exists and is visible to the team
- [ ] Project custom fields created: Value/Effort/Status with expected options
- [ ] Repository labels created for type and area classification
- [ ] Board and backlog views configured
- [ ] Dependency tracking views created (blocked/blocking)
- [ ] Auto-add of issues/PRs enabled for the repository
- [ ] Issue automation sets Status to Backlog for new issues
- [ ] Issue templates reference both project custom fields and repository labels
- [ ] Dependency webhooks configured for status updates
- [ ] README/Process docs updated with usage instructions for both labels and custom fields

## Key metadata requirements

**Required project custom fields for all issues**:
- **Value**: Essential/Useful/Nice-to-have (business or technical impact)
- **Effort**: Heavy/Moderate/Light (engineering effort estimate)
- **Status**: Always set to "Backlog" for new issues (then Todo/In Progress/Review/Done/Blocked)
- **Project**: Associated GitHub project board

> **Note**: Status, Value, and Effort are custom fields in GitHub Projects V2, NOT labels. Never create labels like `high-priority`, `todo`, `essential`, or `heavy` - these duplicate custom field functionality.

**Required repository labels for all issues**:
- **Type**: bug/feature/chore/docs (classification)
- **Area**: frontend/backend/api/infra (scope)

**Required for all PRs**:
- **Custom fields**: Inherited from linked issue (Value/Effort)
- **Labels**: Inherited from linked issue (Type/Area)
- **Project**: Same as linked issue

**CLI Usage Differences**:

Managing repository labels:
```bash
# Add labels to issue/PR (repository-scoped)
gh issue edit 123 --add-label "type:bug,area:frontend"
gh pr edit 456 --add-label "type:feature,area:api"

# List repository labels
gh label list --repo owner/repo
```

Managing project custom fields:
```bash
# Update project custom field values (project-scoped, requires GraphQL)
gh api graphql -f query='mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "PROJECT_ID"
    itemId: "ITEM_ID"
    fieldId: "FIELD_ID"
    value: {singleSelectOptionId: "OPTION_ID"}
  }) { projectV2Item { id } }
}'

# Get project field IDs and option IDs
gh api graphql -f query='query($project: ID!) {
  node(id: $project) {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2SingleSelectField { id name options { id name } }
        }
      }
    }
  }
}' -F project="PROJECT_ID"
```

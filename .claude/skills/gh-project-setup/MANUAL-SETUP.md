# Manual Setup (Reference/Fallback)

Use these steps if the automation script cannot be used or for understanding the implementation.

## Phase 1: Verify prerequisites

```bash
# Check GitHub auth and project scope
gh auth status

# If project scope missing, authorize:
gh auth refresh -h github.com -s project
```

**Important**: The user is assumed to be the owner. Ask for the repository name to link (format: `owner/repo`). The project name will be aligned with the repository name.

## Phase 2: Create project

```bash
# Get current user ID
USER_ID=$(gh api graphql -f query='{viewer {id}}' --jq '.data.viewer.id')

# Create project with name matching the repository
# PROJECT_NAME should match the repository name
gh api graphql -f query='
mutation($owner: ID!, $title: String!) {
  createProjectV2(input: {ownerId: $owner, title: $title}) {
    projectV2 {
      id
      number
      url
    }
  }
}' -F owner="$USER_ID" -F title="$PROJECT_NAME"
```

## Phase 3: Add custom fields

Use the standard template (Status/Value/Effort) with semantic colors.

**CRITICAL**: Use `--input` with JSON files (not `-F` flags) for mutations with array parameters. Each option MUST include a `description` field. See [REFERENCE.md](REFERENCE.md) for API details.

**GitHub auto-creates a Status field**: When a project is created, GitHub automatically adds a Status field with default options (Todo, In Progress, Done). The skill detects this and **updates** the existing field to match the standard template (Backlog, Todo, Doing, Done) using the `updateProjectV2Field` mutation.

```bash
# Create Status field
cat > /tmp/create_status_field.json << 'EOF'
{
  "query": "mutation($project: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!, $singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { createProjectV2Field(input: { projectId: $project name: $name dataType: $dataType singleSelectOptions: $singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "project": "PROJECT_ID_HERE",
    "name": "Status",
    "dataType": "SINGLE_SELECT",
    "singleSelectOptions": [
      {"name": "Backlog", "color": "GRAY", "description": "Not yet prioritized or ready to start"},
      {"name": "Todo", "color": "GREEN", "description": "Ready to start, requirements clear"},
      {"name": "Doing", "color": "BLUE", "description": "Currently being worked on"},
      {"name": "Done", "color": "PURPLE", "description": "Completed and merged"}
    ]
  }
}
EOF

gh api graphql --input /tmp/create_status_field.json

# Create Value field
cat > /tmp/create_value_field.json << 'EOF'
{
  "query": "mutation($project: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!, $singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { createProjectV2Field(input: { projectId: $project name: $name dataType: $dataType singleSelectOptions: $singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "project": "PROJECT_ID_HERE",
    "name": "Value",
    "dataType": "SINGLE_SELECT",
    "singleSelectOptions": [
      {"name": "Essential", "color": "PURPLE", "description": "Critical functionality, must have"},
      {"name": "Useful", "color": "BLUE", "description": "Valuable improvement, should have"},
      {"name": "Nice-to-have", "color": "GREEN", "description": "Optional enhancement, could have"}
    ]
  }
}
EOF

gh api graphql --input /tmp/create_value_field.json

# Create Effort field
cat > /tmp/create_effort_field.json << 'EOF'
{
  "query": "mutation($project: ID!, $name: String!, $dataType: ProjectV2CustomFieldType!, $singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { createProjectV2Field(input: { projectId: $project name: $name dataType: $dataType singleSelectOptions: $singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "project": "PROJECT_ID_HERE",
    "name": "Effort",
    "dataType": "SINGLE_SELECT",
    "singleSelectOptions": [
      {"name": "Heavy", "color": "RED", "description": "Complex task, significant work"},
      {"name": "Moderate", "color": "YELLOW", "description": "Standard task, some complexity"},
      {"name": "Light", "color": "GRAY", "description": "Quick task, minimal complexity"}
    ]
  }
}
EOF

gh api graphql --input /tmp/create_effort_field.json
```

## Phase 4: Update existing fields (if needed)

If a field already exists and needs updating, use the `updateProjectV2Field` mutation (added December 2024). This allows modifying options WITHOUT data loss.

```bash
# Update Status field options
cat > /tmp/update_status_field.json << 'EOF'
{
  "query": "mutation($fieldId: ID!, $name: String, $singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { updateProjectV2Field(input: { fieldId: $fieldId name: $name singleSelectOptions: $singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "fieldId": "FIELD_ID_HERE",
    "name": "Status",
    "singleSelectOptions": [
      {"name": "Backlog", "color": "GRAY", "description": "Not yet prioritized or ready to start"},
      {"name": "Todo", "color": "GREEN", "description": "Ready to start, requirements clear"},
      {"name": "Doing", "color": "BLUE", "description": "Currently being worked on"},
      {"name": "Done", "color": "PURPLE", "description": "Completed and merged"}
    ]
  }
}
EOF

gh api graphql --input /tmp/update_status_field.json
```

**Important notes**:
- If `singleSelectOptions` is empty, no changes are made
- If values are present, they **overwrite** all existing options
- This preserves data - previously set values on items remain intact
- Reference: [GitHub Changelog December 2024](https://github.blog/changelog/2024-12-12-github-issues-projects-close-issue-as-a-duplicate-rest-api-for-sub-issues-and-more/)

## Phase 5: Link repository

```bash
# Get repository node ID
REPO_ID=$(gh api graphql -f query='
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id
  }
}' -F owner="REPO_OWNER" -F name="REPO_NAME" --jq '.data.repository.id')

# Link repository to project
gh api graphql -f query='
mutation($project: ID!, $repo: ID!) {
  linkProjectV2ToRepository(input: {
    projectId: $project
    repositoryId: $repo
  }) {
    repository {
      projectsV2(first: 1) {
        nodes {
          title
        }
      }
    }
  }
}' -F project="$PROJECT_ID" -F repo="$REPO_ID"
```

## Phase 6: Create repository labels

Create standard labels aligned with the repository's semantic color psychology:

```bash
REPO="$REPO_OWNER/$REPO_NAME"

# Critical/Urgency (Red-Orange spectrum)
gh label create "bug" --description "Something isn't working" --color "FF3B30" --repo "$REPO" || true
gh label create "security" --description "Security-related issues" --color "FF9500" --repo "$REPO" || true
gh label create "performance" --description "Performance improvements" --color "FF6B35" --repo "$REPO" || true

# Quality/Success (Green spectrum)
gh label create "testing" --description "Test suite and infrastructure" --color "34C759" --repo "$REPO" || true

# Refinement (Purple spectrum)
gh label create "refactor" --description "Code refactoring" --color "AF52DE" --repo "$REPO" || true

# Technical infrastructure (Blue-Cyan spectrum)
gh label create "ci" --description "Continuous integration and automation" --color "00C7BE" --repo "$REPO" || true
gh label create "dependencies" --description "Dependency updates" --color "007AFF" --repo "$REPO" || true

# Neutral/Routine (Gray spectrum)
gh label create "config" --description "Configuration files and management" --color "C7C7CC" --repo "$REPO" || true
gh label create "docs" --description "Documentation improvements" --color "8E8E93" --repo "$REPO" || true
```

## Phase 7: Create views (MANUAL - NO API SUPPORT)

**IMPORTANT**: GitHub's GraphQL API has NO mutation to create views. Views must be created manually via web UI.

Instruct the user:

```text
Manual step required (no API available):
1. Go to the project URL
2. Click "New view" and create:
   - Status Board (Board layout, group by Status)
   - Table View (Table layout, show all fields)
   - Value Board (Board layout, group by Value)
   - Effort Board (Board layout, group by Effort)
```

## Phase 8: Enable automations (if available via API)

Built-in GitHub Project automations:
- Auto-add to project (when issues/PRs are created in linked repo)
- Item closed → Status = Done
- Pull request merged → Status = Done
- Auto-add sub-issues

**Note**: These are typically configured via the web UI. Document them in the output.

## Phase 9: Save configuration

Generate a configuration file for use with `gh-project-manage` skill:

```bash
# Save to docs/github-project-config.json
cat > docs/github-project-config.json << EOF
{
  "project": {
    "id": "$PROJECT_ID",
    "number": $PROJECT_NUMBER,
    "title": "$PROJECT_TITLE",
    "owner": "$OWNER",
    "url": "$PROJECT_URL"
  },
  "fields": {
    "status": {
      "id": "$STATUS_FIELD_ID",
      "options": {
        "Backlog": "$BACKLOG_OPTION_ID",
        "Todo": "$TODO_OPTION_ID",
        "Doing": "$DOING_OPTION_ID",
        "Done": "$DONE_OPTION_ID"
      }
    },
    "value": {
      "id": "$VALUE_FIELD_ID",
      "options": {
        "Essential": "$ESSENTIAL_OPTION_ID",
        "Useful": "$USEFUL_OPTION_ID",
        "Nice-to-have": "$NICE_TO_HAVE_OPTION_ID"
      }
    },
    "effort": {
      "id": "$EFFORT_FIELD_ID",
      "options": {
        "Heavy": "$HEAVY_OPTION_ID",
        "Moderate": "$MODERATE_OPTION_ID",
        "Light": "$LIGHT_OPTION_ID"
      }
    }
  },
  "repository": "$REPO"
}
EOF
```

## Phase 10: Output summary

Provide the user with:

1. **Project URL** - Direct link to the new project
2. **Project ID** - For use with `gh-project-manage` and GraphQL
3. **Field IDs** - For automation scripts
4. **Configuration file location** - Path to saved config
5. **Next steps**:
   - Manually create views (no API support)
   - Configure automations via web UI
   - Update issue templates to reference project
   - Test by creating an issue and adding to project

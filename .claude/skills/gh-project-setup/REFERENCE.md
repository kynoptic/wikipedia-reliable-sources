# GitHub Projects V2 API Reference

Detailed API information, limitations, and technical notes for working with GitHub Projects V2.

## GitHub CLI `-F` Flag Limitation

**Problem**: The `-F` (field) flag in `gh api` does NOT parse JSON arrays or objects - it stringifies them instead.

**Examples that FAIL**:

```bash
# This gets stringified to a string, not parsed as JSON
gh api graphql -F 'options=[{"name":"Todo"}]' -f query='...'

# This also fails - even with @filename syntax
gh api graphql -F 'options=@/tmp/options.json' -f query='...'
```

**Solution**: Use `--input` with a complete JSON file:

```bash
cat > /tmp/mutation.json << 'EOF'
{
  "query": "mutation(...) { ... }",
  "variables": {
    "options": [{"name": "Todo", "color": "GREEN", "description": "..."}]
  }
}
EOF

gh api graphql --input /tmp/mutation.json
```

**References**:
- [GitHub CLI issue #1484](https://github.com/cli/cli/issues/1484) - Allow JSON array parameters
- [GitHub CLI issue #4368](https://github.com/cli/cli/issues/4368) - Input object as variable
- [GitHub CLI issue #8621](https://github.com/cli/cli/issues/8621) - `-F` doesn't parse JSON object inside array

## Required Field Properties

**Discovery**: The `ProjectV2SingleSelectFieldOptionInput` type requires a `description` field for every option.

**Error without description**:

```
Expected value to not be null for 0.description, 1.description, 2.description
```

**Correct format**:

```json
{
  "name": "Todo",
  "color": "GREEN",
  "description": "This item hasn't been started"
}
```

## updateProjectV2Field Mutation (December 2024)

**Major API enhancement**: GitHub added `updateProjectV2Field` mutation in December 2024, allowing field option updates WITHOUT data loss.

**Before**: Had to delete and recreate fields, losing all set values on items
**After**: Can update options in-place, preserving existing data

**Key behaviors**:
- If `singleSelectOptions` is empty array `[]`, no changes are made
- If values are present, they completely replace existing options
- Previously set values on project items are preserved
- Option IDs change when updated (old IDs become invalid)

**Example usage**:

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

**Reference**: [GitHub Changelog - December 12, 2024](https://github.blog/changelog/2024-12-12-github-issues-projects-close-issue-as-a-duplicate-rest-api-for-sub-issues-and-more/)

## GraphQL Mutation Names

**Correct mutation names**:
- `createProjectV2Field` - Create new custom field
- `updateProjectV2Field` - Update existing field (December 2024+)
- `deleteProjectV2Field` - Delete a field

**Common mistake**: Using `addProjectV2Field` (this doesn't exist)

## Available Colors for Options

The following colors are available for single-select field options:

- `GRAY`
- `BLUE`
- `GREEN`
- `YELLOW`
- `ORANGE`
- `RED`
- `PINK`
- `PURPLE`

## View Creation Limitations

**CONFIRMED**: No `createProjectV2View` mutation exists in GitHub's GraphQL API (verified via schema introspection).

**API Status**:
- ❌ Cannot create views via API
- ❌ Cannot modify view configurations via API
- ✅ Can query existing views (read-only)

**Workaround**: Create views manually via web UI.

**Standard views to create**:
- Status Board (Board layout, group by Status)
- Table View (Table layout, show all fields)
- Value Board (Board layout, group by Value)
- Effort Board (Board layout, group by Effort)

## Built-in Automations

Built-in GitHub Project automations (configured via web UI):
- Auto-add to project (when issues/PRs are created in linked repo)
- Item closed → Status = Done
- Pull request merged → Status = Done
- Auto-add sub-issues

**Note**: These are typically configured via the web UI as API support is limited.

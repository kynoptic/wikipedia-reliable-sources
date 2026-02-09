#!/bin/bash
set -euo pipefail

# GitHub Projects V2 Setup Script
# Automatically creates and configures a GitHub project for a repository
# Usage: ./setup-project.sh [owner/repo] [project-name]

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO="${1:-}"
readonly PROJECT_NAME="${2:-}"

# Color output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}✓${NC} $*"
}

log_warn() {
  echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
  echo -e "${RED}✗${NC} $*" >&2
}

# Check prerequisites
check_prerequisites() {
  log_info "Checking prerequisites..."

  # Check gh auth
  if ! gh auth status > /dev/null 2>&1; then
    log_error "GitHub authentication required. Run: gh auth login"
    exit 1
  fi

  # Check project scope
  if ! gh auth status --show-token 2>/dev/null | grep -q "project"; then
    log_warn "Project scope not authorized. Run: gh auth refresh -s project"
    log_warn "Continuing without project scope..."
  fi

  log_info "Prerequisites verified"
}

# Get repository info
get_repo_info() {
  local repo="$1"

  if [[ ! "$repo" =~ ^[^/]+/[^/]+$ ]]; then
    log_error "Invalid repository format. Use: owner/repo"
    exit 1
  fi

  local owner="${repo%/*}"
  local name="${repo##*/}"

  # Verify repository exists
  if ! gh api graphql -f query='
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        nameWithOwner
      }
    }' -F owner="$owner" -F name="$name" > /dev/null 2>&1; then
    log_error "Repository not found: $repo"
    exit 1
  fi

  echo "$repo"
}

# Get or derive project name
get_project_name() {
  local repo="$1"
  local project_name="${2:-}"

  # If project name not provided, use repository name
  if [[ -z "$project_name" ]]; then
    project_name="${repo##*/}"
  fi

  echo "$project_name"
}

# Create project
create_project() {
  local project_name="$1"
  local owner_id="$2"

  local response
  response=$(gh api graphql -f query='
    mutation($owner: ID!, $title: String!) {
      createProjectV2(input: {ownerId: $owner, title: $title}) {
        projectV2 {
          id
          number
          url
        }
      }
    }' -F owner="$owner_id" -F title="$project_name" 2>&1)

  if echo "$response" | grep -q "errors"; then
    log_error "Failed to create project: $response"
    exit 1
  fi

  echo "$response" | jq -r '.data.createProjectV2.projectV2.id'
}

# Create custom fields
create_custom_fields() {
  local project_id="$1"

  log_info "Creating custom fields..."

  # Create Status field
  create_field "$project_id" "Status" '[
    {"name": "Backlog", "color": "GRAY", "description": "Not yet prioritized or ready to start"},
    {"name": "Todo", "color": "GREEN", "description": "Ready to start, requirements clear"},
    {"name": "Doing", "color": "BLUE", "description": "Currently being worked on"},
    {"name": "Done", "color": "PURPLE", "description": "Completed and merged"}
  ]'

  # Create Value field
  create_field "$project_id" "Value" '[
    {"name": "Essential", "color": "PURPLE", "description": "Critical functionality, must have"},
    {"name": "Useful", "color": "BLUE", "description": "Valuable improvement, should have"},
    {"name": "Nice-to-have", "color": "GREEN", "description": "Optional enhancement, could have"}
  ]'

  # Create Effort field
  create_field "$project_id" "Effort" '[
    {"name": "Heavy", "color": "RED", "description": "Complex task, significant work"},
    {"name": "Moderate", "color": "YELLOW", "description": "Standard task, some complexity"},
    {"name": "Light", "color": "GRAY", "description": "Quick task, minimal complexity"}
  ]'

  log_info "Custom fields created"
}

# Helper to create a single field
create_field() {
  local project_id="$1"
  local field_name="$2"
  local options="$3"

  # Try to create the field
  local mutation_json
  mutation_json=$(cat <<EOF
{
  "query": "mutation(\$project: ID!, \$name: String!, \$dataType: ProjectV2CustomFieldType!, \$singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { createProjectV2Field(input: { projectId: \$project name: \$name dataType: \$dataType singleSelectOptions: \$singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "project": "$project_id",
    "name": "$field_name",
    "dataType": "SINGLE_SELECT",
    "singleSelectOptions": $options
  }
}
EOF
)

  echo "$mutation_json" > /tmp/field_mutation.json

  if gh api graphql --input /tmp/field_mutation.json > /dev/null 2>&1; then
    rm -f /tmp/field_mutation.json
    return 0
  fi

  # Field creation failed - likely already exists. Try to update it.
  log_warn "$field_name field already exists. Attempting to update..."

  # Query for existing field ID
  local field_id
  field_id=$(gh api graphql -f query='
    query($project: ID!, $name: String!) {
      node(id: $project) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
              }
            }
          }
        }
      }
    }' -F project="$project_id" -F name="$field_name" --jq ".data.node.fields.nodes[] | select(.name == \"$field_name\") | .id")

  if [[ -z "$field_id" ]]; then
    log_error "Could not find existing $field_name field to update"
    rm -f /tmp/field_mutation.json
    return 1
  fi

  # Update existing field with new options
  local update_json
  update_json=$(cat <<EOF
{
  "query": "mutation(\$fieldId: ID!, \$name: String, \$singleSelectOptions: [ProjectV2SingleSelectFieldOptionInput!]) { updateProjectV2Field(input: { fieldId: \$fieldId name: \$name singleSelectOptions: \$singleSelectOptions }) { projectV2Field { ... on ProjectV2SingleSelectField { id name options { id name color description } } } } }",
  "variables": {
    "fieldId": "$field_id",
    "name": "$field_name",
    "singleSelectOptions": $options
  }
}
EOF
)

  echo "$update_json" > /tmp/field_update.json

  if gh api graphql --input /tmp/field_update.json > /dev/null 2>&1; then
    log_info "$field_name field updated successfully"
  else
    log_error "Failed to update $field_name field"
  fi

  rm -f /tmp/field_mutation.json /tmp/field_update.json
}

# Link repository to project
link_repository() {
  local project_id="$1"
  local repo="$2"

  log_info "Linking repository: $repo"

  local owner="${repo%/*}"
  local name="${repo##*/}"

  # Get repository ID
  local repo_id
  repo_id=$(gh api graphql -f query='
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
      }
    }' -F owner="$owner" -F name="$name" --jq '.data.repository.id')

  # Link repository to project
  if ! gh api graphql -f query='
    mutation($project: ID!, $repo: ID!) {
      linkProjectV2ToRepository(input: {
        projectId: $project
        repositoryId: $repo
      }) {
        repository {
          id
        }
      }
    }' -F project="$project_id" -F repo="$repo_id" > /dev/null 2>&1; then
    log_warn "Failed to link repository. It may already be linked."
  fi

  log_info "Repository linked"
}

# Create repository labels
create_labels() {
  local repo="$1"

  log_info "Creating repository labels..."

  # Critical/Urgency (Red-Orange spectrum)
  gh label create "bug" --description "Something isn't working" --color "FF3B30" --repo "$repo" || true
  gh label create "security" --description "Security-related issues" --color "FF9500" --repo "$repo" || true
  gh label create "performance" --description "Performance improvements" --color "FF6B35" --repo "$repo" || true

  # Quality/Success (Green spectrum)
  gh label create "testing" --description "Test suite and infrastructure" --color "34C759" --repo "$repo" || true

  # Refinement (Purple spectrum)
  gh label create "refactor" --description "Code refactoring" --color "AF52DE" --repo "$repo" || true

  # Technical infrastructure (Blue-Cyan spectrum)
  gh label create "ci" --description "Continuous integration and automation" --color "00C7BE" --repo "$repo" || true
  gh label create "dependencies" --description "Dependency updates" --color "007AFF" --repo "$repo" || true

  # Neutral/Routine (Gray spectrum)
  gh label create "config" --description "Configuration files and management" --color "C7C7CC" --repo "$repo" || true
  gh label create "docs" --description "Documentation improvements" --color "8E8E93" --repo "$repo" || true

  log_info "Repository labels created"
}

# Save configuration
save_configuration() {
  local project_id="$1"
  local project_number="$2"
  local project_url="$3"
  local repo="$4"

  log_info "Saving configuration..."

  local config_file=".github/project-config.json"
  mkdir -p "$(dirname "$config_file")"

  cat > "$config_file" << EOF
{
  "project": {
    "id": "$project_id",
    "number": $project_number,
    "title": "$project_name",
    "owner": "$(echo "$repo" | cut -d/ -f1)",
    "url": "$project_url"
  },
  "repository": "$repo",
  "fields": {
    "status": {
      "name": "Status",
      "options": ["Backlog", "Todo", "Doing", "Done"]
    },
    "value": {
      "name": "Value",
      "options": ["Essential", "Useful", "Nice-to-have"]
    },
    "effort": {
      "name": "Effort",
      "options": ["Heavy", "Moderate", "Light"]
    }
  }
}
EOF

  log_info "Configuration saved to: $config_file"
}

# Main execution
main() {
  # Parse arguments or detect from current repository
  local repo="$REPO"
  local project_name="$PROJECT_NAME"

  if [[ -z "$repo" ]]; then
    # Try to get from current git repository
    if git rev-parse --git-dir > /dev/null 2>&1; then
      local remote_url
      remote_url=$(git config --get remote.origin.url 2>/dev/null || echo "")

      # Extract owner/repo from git URL
      if [[ "$remote_url" =~ github.com[:/]([^/]+)/([^/\.]+) ]]; then
        repo="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
      fi
    fi
  fi

  if [[ -z "$repo" ]]; then
    log_error "Repository not specified. Usage: $0 owner/repo [project-name]"
    exit 1
  fi

  # Verify and normalize repository
  repo=$(get_repo_info "$repo")

  # Get project name
  project_name=$(get_project_name "$repo" "$project_name")

  # Get current user ID (owner)
  local owner_id
  owner_id=$(gh api graphql -f query='{viewer {id}}' --jq '.data.viewer.id')

  echo ""
  log_info "GitHub Project Setup"
  echo "Repository: $repo"
  echo "Project: $project_name"
  echo ""

  check_prerequisites

  # Create project
  local project_id
  project_id=$(create_project "$project_name" "$owner_id")
  log_info "Project created: $project_id"

  # Get project details (number and URL)
  local project_info
  project_info=$(gh api graphql -f query='
    query($id: ID!) {
      node(id: $id) {
        ... on ProjectV2 {
          number
          url
        }
      }
    }' -F id="$project_id" 2>/dev/null)

  local project_number
  local project_url
  project_number=$(echo "$project_info" | jq -r '.data.node.number')
  project_url=$(echo "$project_info" | jq -r '.data.node.url')

  # Create custom fields
  create_custom_fields "$project_id"

  # Link repository
  link_repository "$project_id" "$repo"

  # Create labels
  create_labels "$repo"

  # Save configuration
  save_configuration "$project_id" "$project_number" "$project_url" "$repo"

  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  log_info "Project setup complete!"
  echo ""
  echo "Project URL: $project_url"
  echo "Repository: $repo"
  echo "Configuration: .github/project-config.json"
  echo ""
  echo "Next steps:"
  echo "  1. Open the project: $project_url"
  echo "  2. Create views (Status, Table, Value, Effort boards)"
  echo "  3. Enable automations in project settings"
  echo "  4. Review label colors in LABEL-COLORS.md"
  echo "  5. Test by creating an issue in the repository"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

main "$@"

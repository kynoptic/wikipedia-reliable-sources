---
name: git-issue-dependencies
descriptive-title: Analyze and establish intelligent issue dependency relationships
description: Scan existing issues and their content to identify missing dependency relationships, parent-child hierarchies, and blocking patterns, then automatically establish these relationships through GitHub CLI commands.
persona: You are a repository analyst that identifies patterns in issue relationships and automatically establishes proper dependencies to improve project planning visibility.
tools: gh, Bash, Read, Write, Edit, Grep
---

# Issue dependency relationship analyzer

## Purpose
Analyze existing issues to identify missing dependency relationships based on content patterns, cross-references, and logical prerequisites, then automatically establish these relationships using GitHub's dependency system.

## Prerequisites
- GitHub CLI (`gh`) authenticated and configured
- Repository with existing issues
- Write access to manage issue relationships
- GitHub API access for dependency management

## Workflow

### Step 1: Scan existing issues for relationship patterns

**Collect all open issues with metadata:**
```bash
#!/bin/bash
# collect_issues.sh

echo "Scanning repository for issue relationship patterns..."

# Get all issues with key metadata
gh issue list --state all --limit 500 --json number,title,body,labels,assignees,milestone > issues.json

# Extract issues that mention other issues
echo "Issues referencing other issues:"
jq -r '.[] | select(.body | test("#[0-9]+")) | "\(.number): \(.title)"' issues.json

# Find issues with parent/child keywords
echo -e "\nIssues with hierarchical keywords:"
jq -r '.[] | select(.title | test("(?i)(parent|child|depends|requires|blocks|prerequisite)")) | "\(.number): \(.title)"' issues.json

# Find issues by component/area that might be related
echo -e "\nGrouping by component/area:"
jq -r 'group_by(.labels[].name | select(test("^(area|component):"))) | .[] | "\(.[0].labels[] | select(.name | test("^(area|component):")).name): \([.[].number] | join(", "))"' issues.json
```

### Step 2: Analyze cross-references and mentions

**Extract issue references from descriptions:**
```bash
#!/bin/bash
# analyze_references.sh

echo "Analyzing issue cross-references..."

# Function to extract issue numbers from text
extract_issue_refs() {
    local text="$1"
    echo "$text" | grep -oE '#[0-9]+' | sed 's/#//' | sort -u
}

# Analyze each issue for references
while read -r issue_data; do
    issue_num=$(echo "$issue_data" | jq -r '.number')
    issue_title=$(echo "$issue_data" | jq -r '.title')
    issue_body=$(echo "$issue_data" | jq -r '.body // ""')

    # Find all issue references in title and body
    refs=$(extract_issue_refs "$issue_title $issue_body")

    if [ ! -z "$refs" ]; then
        echo "Issue #$issue_num references: $refs"

        # Check if references indicate dependencies
        if echo "$issue_body" | grep -qi "depends.*on\|requires\|blocked.*by\|prerequisite"; then
            echo "  → Potential dependency relationship detected"
            echo "$issue_num,$refs,dependency" >> potential_dependencies.csv
        fi

        # Check if references indicate parent-child relationships
        if echo "$issue_body" | grep -qi "parent\|child\|subtask\|epic"; then
            echo "  → Potential parent-child relationship detected"
            echo "$issue_num,$refs,hierarchy" >> potential_relationships.csv
        fi
    fi
done < <(jq -c '.[]' issues.json)
```

### Step 3: Identify missing dependencies by pattern analysis

**Analyze architectural dependencies:**
```bash
#!/bin/bash
# identify_architectural_dependencies.sh

echo "Identifying architectural dependency patterns..."

# Group issues by component/layer
declare -A components
declare -A database_issues
declare -A api_issues
declare -A frontend_issues
declare -A infrastructure_issues

while read -r issue_data; do
    issue_num=$(echo "$issue_data" | jq -r '.number')
    issue_title=$(echo "$issue_data" | jq -r '.title')
    issue_body=$(echo "$issue_data" | jq -r '.body // ""')
    issue_labels=$(echo "$issue_data" | jq -r '.labels[].name' | tr '\n' ' ')

    # Categorize by technical component
    if echo "$issue_title $issue_body $issue_labels" | grep -qi "database\|db\|schema\|migration"; then
        database_issues[$issue_num]="$issue_title"
    elif echo "$issue_title $issue_body $issue_labels" | grep -qi "api\|endpoint\|route\|backend"; then
        api_issues[$issue_num]="$issue_title"
    elif echo "$issue_title $issue_body $issue_labels" | grep -qi "frontend\|ui\|component\|react\|vue"; then
        frontend_issues[$issue_num]="$issue_title"
    elif echo "$issue_title $issue_body $issue_labels" | grep -qi "deploy\|infra\|docker\|ci\|pipeline"; then
        infrastructure_issues[$issue_num]="$issue_title"
    fi
done < <(jq -c '.[]' issues.json)

# Suggest logical dependency chains
echo -e "\nSuggested dependency relationships:"
echo "Database → API → Frontend logical chain:"

for api_issue in "${!api_issues[@]}"; do
    for db_issue in "${!database_issues[@]}"; do
        # Check if API issue might depend on database issue
        if [[ "${api_issues[$api_issue]}" =~ $(echo "${database_issues[$db_issue]}" | cut -d' ' -f1-3) ]]; then
            echo "  API #$api_issue may depend on DB #$db_issue"
            echo "$api_issue,$db_issue,architectural" >> suggested_dependencies.csv
        fi
    done
done

for frontend_issue in "${!frontend_issues[@]}"; do
    for api_issue in "${!api_issues[@]}"; do
        # Check if frontend issue might depend on API issue
        if [[ "${frontend_issues[$frontend_issue]}" =~ $(echo "${api_issues[$api_issue]}" | cut -d' ' -f1-3) ]]; then
            echo "  Frontend #$frontend_issue may depend on API #$api_issue"
            echo "$frontend_issue,$api_issue,architectural" >> suggested_dependencies.csv
        fi
    done
done
```

### Step 4: Check for existing dependencies and gaps

**Audit current dependency state:**
```bash
#!/bin/bash
# audit_existing_dependencies.sh

echo "Auditing existing dependencies..."

# Get all current dependencies
echo "Current blocking relationships:"
for issue_num in $(jq -r '.[].number' issues.json); do
    blocked_by=$(gh api "repos/{owner}/{repo}/issues/$issue_num/blocked_by" 2>/dev/null | jq -r '.[].number' 2>/dev/null | tr '\n' ',' | sed 's/,$//')
    blocking=$(gh api "repos/{owner}/{repo}/issues/$issue_num/blocking" 2>/dev/null | jq -r '.[].number' 2>/dev/null | tr '\n' ',' | sed 's/,$//')

    if [ ! -z "$blocked_by" ]; then
        echo "Issue #$issue_num blocked by: $blocked_by"
        echo "$issue_num,blocked_by,$blocked_by" >> existing_dependencies.csv
    fi

    if [ ! -z "$blocking" ]; then
        echo "Issue #$issue_num blocking: $blocking"
        echo "$issue_num,blocking,$blocking" >> existing_dependencies.csv
    fi
done

# Compare with suggested dependencies
if [ -f suggested_dependencies.csv ] && [ -f existing_dependencies.csv ]; then
    echo -e "\nMissing dependencies (suggested but not set):"
    comm -23 <(sort suggested_dependencies.csv) <(sort existing_dependencies.csv)
fi
```

### Step 5: Automatically establish missing relationships

**Apply suggested dependencies:**
```bash
#!/bin/bash
# apply_dependencies.sh

if [ ! -f suggested_dependencies.csv ]; then
    echo "No suggested dependencies found. Run analysis first."
    exit 1
fi

echo "Applying suggested dependency relationships..."

while IFS=',' read -r issue_num dependency_num relationship_type; do
    echo "Setting up: Issue #$issue_num depends on #$dependency_num ($relationship_type)"

    # Get issue IDs for GraphQL
    issue_id=$(gh issue view "$issue_num" --json id -q .id)
    dependency_id=$(gh issue view "$dependency_num" --json id -q .id)

    if [ ! -z "$issue_id" ] && [ ! -z "$dependency_id" ]; then
        # Add blocking relationship
        result=$(gh api graphql -f query='
        mutation($issueId: ID!, $blockedById: ID!) {
          addBlockedBy(input: {
            issueOrPullRequestId: $issueId,
            blockedByIssueOrPullRequestId: $blockedById
          }) {
            issueOrPullRequest {
              ... on Issue {
                number
                title
              }
            }
          }
        }' -F issueId="$issue_id" -F blockedById="$dependency_id" 2>/dev/null)

        if echo "$result" | jq -e '.data.addBlockedBy' >/dev/null 2>&1; then
            echo "  ✅ Successfully set dependency"

            # Add explanatory comment
            gh issue comment "$issue_num" --body "🔗 This issue has been automatically identified as depending on #$dependency_num based on $relationship_type analysis. Please verify this relationship is correct."
        else
            echo "  ❌ Failed to set dependency"
        fi
    else
        echo "  ⚠️ Could not resolve issue IDs"
    fi

    sleep 1  # Rate limiting
done < suggested_dependencies.csv
```

### Step 6: Establish epic/parent-child hierarchies

**Create parent-child relationships for large issues:**
```bash
#!/bin/bash
# establish_hierarchies.sh

echo "Establishing parent-child hierarchies..."

# Find potential epic/parent issues (high effort, broad scope)
echo "Identifying potential parent issues:"
jq -r '.[] | select(
    (.labels[]?.name | test("^effort:(large|xl)")) and
    (.title | test("(?i)(epic|milestone|feature)")) and
    (.body | length > 200)
) | "\(.number): \(.title)"' issues.json > potential_parents.txt

# Find potential child issues that reference parents
while read -r parent_line; do
    parent_num=$(echo "$parent_line" | cut -d: -f1)
    parent_title=$(echo "$parent_line" | cut -d: -f2-)

    echo "Checking for child issues of parent #$parent_num..."

    # Find issues that reference this parent
    children=$(jq -r --arg parent "#$parent_num" '.[] | select(.body | contains($parent)) | .number' issues.json | tr '\n' ' ')

    if [ ! -z "$children" ]; then
        echo "  Potential children: $children"

        # For each child, check if it should be blocked by parent
        for child_num in $children; do
            child_title=$(jq -r --arg num "$child_num" '.[] | select(.number == ($num | tonumber)) | .title' issues.json)

            # Check if child seems to be a subtask
            if echo "$child_title" | grep -qi "implement\|add\|create\|update\|fix" &&
               echo "$child_title" | grep -qiE "$(echo "$parent_title" | cut -d' ' -f1-2)"; then

                echo "    Setting #$child_num as dependent on parent #$parent_num"

                child_id=$(gh issue view "$child_num" --json id -q .id)
                parent_id=$(gh issue view "$parent_num" --json id -q .id)

                gh api graphql -f query='
                mutation($issueId: ID!, $blockedById: ID!) {
                  addBlockedBy(input: {
                    issueOrPullRequestId: $issueId,
                    blockedByIssueOrPullRequestId: $blockedById
                  }) {
                    issueOrPullRequest { ... on Issue { number } }
                  }
                }' -F issueId="$child_id" -F blockedById="$parent_id" >/dev/null 2>&1

                # Add hierarchical comment
                gh issue comment "$child_num" --body "📋 This issue has been identified as a subtask of epic #$parent_num and has been marked as dependent accordingly."
            fi
        done
    fi
done < potential_parents.txt
```

### Step 7: Generate dependency report and validation

**Create comprehensive dependency report:**
```bash
#!/bin/bash
# generate_dependency_report.sh

echo "# Issue Dependency Analysis Report - $(date +%Y-%m-%d)" > dependency_report.md
echo "============================================" >> dependency_report.md
echo "" >> dependency_report.md

echo "## Analysis Summary" >> dependency_report.md
echo "- Total issues analyzed: $(jq length issues.json)" >> dependency_report.md
echo "- Potential dependencies identified: $(wc -l < suggested_dependencies.csv 2>/dev/null || echo 0)" >> dependency_report.md
echo "- Existing dependencies found: $(wc -l < existing_dependencies.csv 2>/dev/null || echo 0)" >> dependency_report.md
echo "" >> dependency_report.md

echo "## Suggested Relationships Applied" >> dependency_report.md
if [ -f suggested_dependencies.csv ]; then
    echo "| Dependent Issue | Blocks Issue | Relationship Type |" >> dependency_report.md
    echo "|-----------------|--------------|-------------------|" >> dependency_report.md
    while IFS=',' read -r issue_num dependency_num relationship_type; do
        issue_title=$(jq -r --arg num "$issue_num" '.[] | select(.number == ($num | tonumber)) | .title' issues.json)
        dep_title=$(jq -r --arg num "$dependency_num" '.[] | select(.number == ($num | tonumber)) | .title' issues.json)
        echo "| #$issue_num: $issue_title | #$dependency_num: $dep_title | $relationship_type |" >> dependency_report.md
    done < suggested_dependencies.csv
fi
echo "" >> dependency_report.md

echo "## Current Dependency State" >> dependency_report.md
echo "### Blocked Issues" >> dependency_report.md
gh issue list --search "is:blocked is:open" --json number,title | \
  jq -r '.[] | "- #\(.number): \(.title)"' >> dependency_report.md

echo "" >> dependency_report.md
echo "### Issues Blocking Others" >> dependency_report.md
gh issue list --search "is:blocking is:open" --json number,title | \
  jq -r '.[] | "- #\(.number): \(.title)"' >> dependency_report.md

echo "" >> dependency_report.md
echo "## Validation Commands" >> dependency_report.md
echo "To verify dependencies were set correctly:" >> dependency_report.md
echo '```bash' >> dependency_report.md
echo "# Check specific issue dependencies" >> dependency_report.md
echo "gh api repos/{owner}/{repo}/issues/{issue_number}/blocked_by" >> dependency_report.md
echo "gh api repos/{owner}/{repo}/issues/{issue_number}/blocking" >> dependency_report.md
echo "" >> dependency_report.md
echo "# Search for dependency patterns" >> dependency_report.md
echo "gh issue list --search 'is:blocked is:open'" >> dependency_report.md
echo "gh issue list --search 'is:blocking is:open'" >> dependency_report.md
echo '```' >> dependency_report.md

echo "Dependency analysis complete. Report saved to dependency_report.md"
```

### Step 8: Manual verification and cleanup

**Review and adjust automated relationships:**
```bash
#!/bin/bash
# manual_review.sh

echo "Manual review checklist for dependency relationships:"
echo ""

echo "1. Review automatically created dependencies:"
if [ -f suggested_dependencies.csv ]; then
    while IFS=',' read -r issue_num dependency_num relationship_type; do
        echo "   - Verify #$issue_num depends on #$dependency_num ($relationship_type)"
        echo "     gh issue view $issue_num"
        echo "     gh issue view $dependency_num"
    done < suggested_dependencies.csv
fi

echo ""
echo "2. Check for circular dependencies:"
echo "   python3 -c \""
cat << 'PYTHON'
import subprocess
import json
from collections import defaultdict

def check_circular_deps():
    try:
        result = subprocess.run(['gh', 'issue', 'list', '--state', 'open', '--json', 'number'],
                              capture_output=True, text=True)
        issues = json.loads(result.stdout)

        graph = defaultdict(set)
        for issue in issues:
            issue_num = issue['number']
            try:
                blocked_result = subprocess.run(
                    ['gh', 'api', f'repos/{{owner}}/{{repo}}/issues/{issue_num}/blocked_by'],
                    capture_output=True, text=True
                )
                if blocked_result.returncode == 0:
                    blocked_by = json.loads(blocked_result.stdout)
                    for blocker in blocked_by:
                        graph[issue_num].add(blocker['number'])
            except:
                continue

        # Simple cycle detection
        def has_cycle(node, visited, rec_stack, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path):
                        return True
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    print(f'Circular dependency: {" → ".join(map(str, path[cycle_start:] + [neighbor]))}')
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        visited = set()
        for issue in graph:
            if issue not in visited:
                if has_cycle(issue, visited, set(), []):
                    return
        print('No circular dependencies found')

    except Exception as e:
        print(f'Error checking dependencies: {e}')

check_circular_deps()
PYTHON
echo "\""

echo ""
echo "3. Validate relationship logic:"
echo "   - Ensure dependencies reflect actual work prerequisites"
echo "   - Verify parent-child relationships are meaningful"
echo "   - Check that blocking relationships support project timeline"
```

## Master execution script

**Run complete dependency analysis:**
```bash
#!/bin/bash
# run_dependency_analysis.sh

echo "Starting comprehensive issue dependency analysis..."

# Create working directory
mkdir -p dependency_analysis
cd dependency_analysis

# Run analysis steps
echo "Step 1: Collecting issues..."
../collect_issues.sh

echo "Step 2: Analyzing references..."
../analyze_references.sh

echo "Step 3: Identifying architectural dependencies..."
../identify_architectural_dependencies.sh

echo "Step 4: Auditing existing dependencies..."
../audit_existing_dependencies.sh

echo "Step 5: Applying suggested dependencies..."
read -p "Apply suggested dependencies automatically? (y/N): " apply_deps
if [[ $apply_deps =~ ^[Yy]$ ]]; then
    ../apply_dependencies.sh
fi

echo "Step 6: Establishing hierarchies..."
read -p "Establish parent-child hierarchies? (y/N): " apply_hierarchies
if [[ $apply_hierarchies =~ ^[Yy]$ ]]; then
    ../establish_hierarchies.sh
fi

echo "Step 7: Generating report..."
../generate_dependency_report.sh

echo "Step 8: Manual review..."
../manual_review.sh

echo ""
echo "Dependency analysis complete!"
echo "Review dependency_report.md and run manual verification steps."
```

## Benefits

1. **Intelligent discovery**: Automatically identifies missing relationships from issue content
2. **Pattern recognition**: Recognizes architectural and hierarchical dependencies
3. **Automated setup**: Uses GitHub CLI to establish relationships programmatically
4. **Validation**: Checks for circular dependencies and relationship logic
5. **Comprehensive reporting**: Provides detailed analysis of all dependency relationships
6. **Manual oversight**: Includes verification steps for human review and adjustment
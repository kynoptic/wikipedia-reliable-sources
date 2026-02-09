---
area: type
subarea: check
goal: ratchet
platforms:
  - windsurf
  - claude
status: active
requires: []
---

# Type check ratchet

## Purpose
Implement a no-regression type checking strategy that progressively improves type coverage without allowing backsliding.

## Core principle
**Never allow type coverage to decrease.** Every change must maintain or improve type safety.

## Ratchet strategy

### 1. Baseline establishment
Create a baseline of current type coverage:
```bash
# Python (mypy)
make mypy-status > type_baseline.txt

# TypeScript
npx tsc --noEmit --strict false > type_baseline.txt

# Other tools
eslint --ext .ts . > type_baseline.txt
```

### 2. Validation commands
Projects MUST implement these commands:

**`make mypy-status`** - Show current type coverage
```bash
mypy --show-error-codes --no-error-summary src/ | tee type_status.txt
echo "Type errors: $(grep -c ': error:' type_status.txt || echo 0)"
```

**`make mypy-validate`** - Enforce no regression
```bash
# Generate current status
make mypy-status > current_status.txt

# Compare with baseline
BASELINE_ERRORS=$(grep -c ': error:' type_baseline.txt || echo 0)
CURRENT_ERRORS=$(grep -c ': error:' current_status.txt || echo 0)

if [ $CURRENT_ERRORS -gt $BASELINE_ERRORS ]; then
    echo "❌ Type coverage regression: $CURRENT_ERRORS errors (was $BASELINE_ERRORS)"
    echo "New type errors introduced:"
    diff type_baseline.txt current_status.txt
    exit 1
else
    echo "✅ Type coverage maintained: $CURRENT_ERRORS errors"
fi
```

### 3. Progressive improvement
When type errors are fixed, update the baseline:
```bash
# After fixing type errors
make mypy-status > type_baseline.txt
git add type_baseline.txt
git commit -m "feat: improve type coverage (fixed 3 type errors)"
```

## Implementation by language

### Python (mypy)
```makefile
mypy-status: ## Show current type coverage
	@echo "Checking type coverage..."
	@mypy --show-error-codes --no-error-summary src/ tests/ || true
	@echo "Type errors: $$(mypy src/ tests/ 2>&1 | grep -c ': error:' || echo 0)"

mypy-validate: ## Validate no type regression
	@echo "Validating type coverage..."
	@$(eval CURRENT := $(shell mypy src/ tests/ 2>&1 | grep -c ': error:' || echo 0))
	@$(eval BASELINE := $(shell cat .type_baseline 2>/dev/null || echo 999))
	@if [ $(CURRENT) -gt $(BASELINE) ]; then \
		echo "❌ Type regression: $(CURRENT) errors (was $(BASELINE))"; \
		exit 1; \
	else \
		echo "✅ Type coverage OK: $(CURRENT) errors"; \
	fi

mypy-update-baseline: ## Update type baseline after improvements
	@mypy src/ tests/ 2>&1 | grep -c ': error:' | tee .type_baseline
	@echo "Updated baseline to $$(cat .type_baseline) errors"
```

### TypeScript
```json
// package.json scripts
{
  "scripts": {
    "type:check": "tsc --noEmit",
    "type:status": "tsc --noEmit 2>&1 | grep -c 'error TS' || echo 0",
    "type:validate": "scripts/validate-types.sh",
    "type:update-baseline": "npm run type:status > .type_baseline"
  }
}
```

```bash
#!/bin/bash
# scripts/validate-types.sh
CURRENT=$(npm run type:status --silent)
BASELINE=$(cat .type_baseline 2>/dev/null || echo 999)

if [ "$CURRENT" -gt "$BASELINE" ]; then
    echo "❌ Type regression: $CURRENT errors (was $BASELINE)"
    exit 1
else
    echo "✅ Type coverage OK: $CURRENT errors"
fi
```

### Go
```bash
# Go has built-in type checking, focus on vet and staticcheck
go-type-check:
	@echo "Running Go type validation..."
	@go vet ./...
	@staticcheck ./... || true
	@golint ./... | wc -l > .type_baseline
```

### Rust
```bash
# Rust enforces types by default, focus on clippy warnings
cargo-type-check:
	@cargo check
	@cargo clippy -- -D warnings || true
	@cargo clippy 2>&1 | grep -c "warning:" > .type_baseline
```

## Workflow integration

### Pre-commit hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: type-check-ratchet
        name: Type check ratchet
        entry: make mypy-validate
        language: system
        pass_filenames: false
        stages: [commit]
```

### CI pipeline
```yaml
# .github/workflows/type-check.yml
name: Type Check
on: [push, pull_request]
jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install mypy types-requests
      - name: Validate type coverage
        run: make mypy-validate
```

### Development workflow
```bash
# Before making changes
make mypy-status  # Note current error count

# Make your changes
# ... code changes ...

# Validate no regression
make mypy-validate

# If you fixed type errors, update baseline
make mypy-update-baseline
```

## Progressive improvement strategy

### 1. Start where you are
Don't try to fix all type errors at once:
```bash
# Establish baseline with current errors
make mypy-status > .type_baseline
git add .type_baseline
git commit -m "chore: establish type check baseline"
```

### 2. Improve incrementally
Fix type errors in small batches:
- Target one module/file at a time
- Fix related errors together
- Update baseline after each improvement

### 3. Prevent regression
The ratchet ensures progress is never lost:
- New code cannot introduce type errors
- Refactoring cannot worsen type coverage
- All team members maintain the same standard

## Type error categories

### High priority (fix immediately)
- Unsafe type casts
- Untyped function parameters
- Missing return type annotations
- Dynamic attribute access without checks

### Medium priority (fix when touching code)
- Generic type parameters
- Union type refinements
- Optional type handling
- Complex type compositions

### Low priority (fix during focused type improvement sessions)
- Missing type hints on internal helpers
- Overly broad type annotations
- Type comment to annotation conversions

## Monitoring and reporting

### Regular reporting
```bash
# Weekly type coverage report
echo "Type Coverage Report - $(date)"
echo "Current errors: $(make mypy-status --silent | grep -c ': error:')"
echo "Baseline errors: $(cat .type_baseline)"
echo "Improvement: $(($(cat .type_baseline) - $(make mypy-status --silent | grep -c ': error:')))"
```

### Progress tracking
Track metrics over time:
- Total type errors
- Errors per module
- Time to fix type errors
- Regression frequency

## Best practices

### 1. Type annotation guidelines
```python
# GOOD: Explicit, precise types
def process_user(user_id: int, data: Dict[str, Any]) -> User:
    pass

# BAD: Vague or missing types
def process_user(user_id, data):
    pass
```

### 2. Gradual typing
```python
# Start with basic types
def calculate(x: float, y: float) -> float:
    return x + y

# Progress to more specific types
def calculate(x: Union[int, float], y: Union[int, float]) -> float:
    return float(x + y)

# Eventually use precise protocols
from typing import Protocol

class Numeric(Protocol):
    def __add__(self, other: 'Numeric') -> 'Numeric': ...

def calculate(x: Numeric, y: Numeric) -> Numeric:
    return x + y
```

### 3. Type safety boundaries
```python
# Validate external data at boundaries
def api_handler(request: HttpRequest) -> JsonResponse:
    # Validate and type raw input
    user_data = UserSchema.parse(request.json)  # Pydantic/similar

    # Now work with typed data
    user = create_user(user_data)
    return JsonResponse({"id": user.id})
```

## Emergency procedures

### Temporary regression allowance
In exceptional circumstances (critical production fix):
```bash
# Temporarily allow regression
ALLOW_TYPE_REGRESSION=1 make mypy-validate

# Must be followed by immediate fix
git commit -m "fix: critical security issue (type regression allowed)"

# Create follow-up issue
gh issue create --title "Fix type regression from security fix" \
                --body "Commit abc123 introduced type regression for security fix"
```

### Recovery from broken baseline
```bash
# If baseline becomes unrealistic
make mypy-status > .type_baseline
git add .type_baseline
git commit -m "chore: reset type baseline after major refactor"
```

## Benefits

1. **Gradual improvement**: Type safety improves over time
2. **No regression**: Progress is never lost
3. **Team alignment**: Everyone maintains the same standard
4. **Early detection**: Type errors caught at development time
5. **Refactoring confidence**: Types enable safe code changes
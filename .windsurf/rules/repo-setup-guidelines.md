---
trigger: model_decision
description: "Standardize project setup, environment config, and onboarding."
---
# Project setup and environment conventions

## One-command setup

### Primary setup command
Every project MUST provide a single command that sets up everything:
```bash
make init        # Preferred for Make-based projects
npm run setup    # Node.js projects
./setup.sh       # Shell script fallback
task init        # Taskfile-based projects
```

### Setup command requirements
The one-command setup MUST:
1. **Check prerequisites** - Verify required tools/versions are installed
2. **Create environment** - Set up virtualenv, node_modules, or language-specific environment
3. **Install dependencies** - All packages, libraries, and tools needed for development
4. **Configure environment** - Copy `.env.example` to `.env`, generate secrets if needed
5. **Initialize data** - Create databases, run migrations, seed test data
6. **Install hooks** - Set up pre-commit, pre-push, or other git hooks
7. **Run validation** - Execute `make fast` or equivalent to verify setup worked
8. **Display next steps** - Show developer what commands to run next

### Setup script template
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Setting up development environment..."

# 1. Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required"; exit 1; }
command -v make >/dev/null 2>&1 || { echo "Make required"; exit 1; }

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Configure environment
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env from template"
fi

# 5. Initialize database
make db-migrate
make db-seed

# 6. Install git hooks
pre-commit install

# 7. Run validation
make fast

echo "✨ Setup complete! Run 'make dev' to start developing"
```

## Task runner conventions

### Standard commands
Projects SHOULD implement these standard commands:
- `make init` / `make setup` - One-time setup
- `make dev` - Start development server
- `make test` - Run test suite
- `make lint` - Run linters
- `make format` - Auto-format code
- `make clean` - Remove generated files
- `make help` - List available commands

### Makefile structure
```makefile
.PHONY: help init dev test lint format clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

init: ## One-time project setup
	./scripts/setup.sh

dev: ## Start development server
	python manage.py runserver

test: ## Run test suite
	pytest

fast: ## Run fast tests only
	pytest -m "not slow"

lint: ## Check code style
	pylint src/
	mypy src/

format: ## Auto-format code
	black src/ tests/
	isort src/ tests/
```

## Environment configuration

### Environment file structure
```bash
.env                 # Local overrides (gitignored)
.env.example         # Template with all variables documented
.env.test           # Test environment settings
.env.production     # Production settings (in secure location)
```

### Environment validation
Applications MUST validate environment on startup:
```python
import os
import sys

REQUIRED_ENV_VARS = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']

def validate_environment():
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print(f"Copy .env.example to .env and fill in the values")
        sys.exit(1)

validate_environment()
```

## Git hooks setup

### Pre-commit configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: fast-tests
        name: Run fast tests
        entry: make fast
        language: system
        pass_filenames: false
        stages: [commit]

      - id: lint
        name: Run linters
        entry: make lint
        language: system
        pass_filenames: false
        stages: [commit]
```

### Hook installation
The `make init` command MUST install hooks automatically:
```bash
# Install pre-commit hooks
pre-commit install

# Install pre-push hooks
cp .githooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

## Onboarding checklist

New developers should be able to:
- [ ] Clone repository and run `make init` successfully
- [ ] Have all dependencies installed automatically
- [ ] Run `make test` and see all tests pass
- [ ] Start development server with `make dev`
- [ ] Make a change and see tests/lints run on commit
- [ ] Find all available commands with `make help`
- [ ] Complete entire setup in under 10 minutes

## Anti-patterns to avoid

- Multiple manual setup steps in README
- Undocumented environment variables
- Setup that only works on one OS
- Missing or outdated .env.example
- No validation of environment configuration
- Assuming global tool installations
- Setup that requires admin/root access


---
area: tests
subarea: tiered
goal: workflow
platforms:
  - windsurf
  - claude
status: active
requires: []
---

# Tests tiered workflow

## Purpose
Establish a canonical test execution ladder that optimizes for fast feedback while ensuring comprehensive validation.

## Tier definitions

### Tier 1: Fast tests (`make fast`)
- **Execution time**: < 1 second per test
- **Scope**: Pure unit tests, no I/O operations
- **Dependencies**: No external services, databases, or network
- **Mocking**: Minimal, only for immediate dependencies
- **Purpose**: Rapid feedback during development
- **Run frequency**: After every code change

### Tier 2: Standard tests (`make test-tiered`)
- **Execution time**: < 10 seconds per test
- **Scope**: Integration tests within a component
- **Dependencies**: May use test databases, file system
- **Mocking**: External services and APIs
- **Purpose**: Validate component interactions
- **Run frequency**: Before committing code

### Tier 3: Full tests (`make test`)
- **Execution time**: < 60 seconds per test
- **Scope**: Cross-component integration tests
- **Dependencies**: Full test environment setup
- **Mocking**: Only third-party services
- **Purpose**: Ensure system-wide compatibility
- **Run frequency**: Before opening PR

### Tier 4: Complete validation (`make full`)
- **Execution time**: Unrestricted
- **Scope**: Everything - tests, lints, type checks, security scans
- **Dependencies**: Complete development environment
- **Mocking**: Production-like conditions
- **Purpose**: Final validation before merge
- **Run frequency**: In CI and before release

## Execution ladder

Follow this progression strictly:

```
make fast        # Start here - immediate feedback
    ↓ (pass)
make test-tiered # Component validation
    ↓ (pass)
make test        # System integration
    ↓ (pass)
make full        # Complete validation
    ↓ (pass)
Ready to commit
```

## Fast-first principles

1. **Fail fast**: Run quickest tests first to catch obvious errors
2. **Progressive depth**: Each tier adds more comprehensive checks
3. **Skip tiers only upward**: Can jump from fast to full, never skip fast
4. **Local-first**: All tiers except full must run without network
5. **Deterministic**: Same input produces same output every time

## Command conventions

### Required commands
Every project MUST implement:
- `make fast` - Tier 1 tests only
- `make test-tiered` - Tiers 1 and 2
- `make test` - Tiers 1, 2, and 3
- `make full` - All tiers plus quality gates

### Optional toggles
Projects MAY implement:
- `FAST_ONLY=1 make test` - Force tier 1 only
- `NO_SLOW=1 make test` - Skip tier 3+ tests
- `PARALLEL=1 make test` - Run tests in parallel
- `FOCUS=<pattern> make test` - Run subset matching pattern

## Tier selection rules

### When to use each tier

| Scenario | Recommended tier | Rationale |
|----------|-----------------|-----------|
| Writing new code | `make fast` | Immediate feedback loop |
| Before git commit | `make test-tiered` | Catch integration issues |
| Before opening PR | `make test` | Full compatibility check |
| Before merging PR | `make full` | Complete validation |
| Debugging test failure | Start with `make fast` | Isolate tier-by-tier |
| CI pipeline | All tiers in sequence | Fail fast, detailed reporting |

## Implementation requirements

### Makefile setup
```makefile
# Fast tier - unit tests only
fast:
	@echo "Running Tier 1: Fast tests..."
	pytest tests/unit -m "not slow" --maxfail=1

# Standard tier - unit + integration
test-tiered: fast
	@echo "Running Tier 2: Standard tests..."
	pytest tests/integration -m "not slow"

# Full tier - all automated tests
test: test-tiered
	@echo "Running Tier 3: Full tests..."
	pytest tests/

# Complete tier - tests + quality gates
full: test
	@echo "Running Tier 4: Complete validation..."
	make lint
	make typecheck
	make security-scan
```

### Test marking
```python
# Python/pytest example
@pytest.mark.fast  # Tier 1
def test_pure_logic():
    assert calculate(2, 3) == 5

@pytest.mark.integration  # Tier 2
def test_database_query():
    with test_database():
        assert fetch_user(123).name == "Test"

@pytest.mark.slow  # Tier 3
def test_full_workflow():
    # Complex end-to-end test
    pass
```

## Anti-patterns to avoid

- **Skipping tiers**: Never jump straight to `make full` during development
- **Slow tier 1**: Tests taking >1 second don't belong in fast tier
- **Network in tier 2**: Standard tests must work offline
- **Flaky tests**: Non-deterministic tests break the ladder
- **Missing tiers**: Implementing only `make test` without tiered options
- **Tier confusion**: Mixing slow tests into fast tier

## Monitoring and optimization

### Tier performance targets
- Tier 1: Complete in < 10 seconds total
- Tier 2: Complete in < 1 minute total
- Tier 3: Complete in < 5 minutes total
- Tier 4: Complete in < 15 minutes total

### Regular audits
- Weekly: Review tests taking >1 second in tier 1
- Monthly: Analyze tier distribution and rebalance
- Quarterly: Optimize slowest 10% of tests
- Continuous: Move flaky tests to higher tiers

## Benefits

1. **Developer velocity**: Fast feedback keeps flow state
2. **CI efficiency**: Fail fast saves compute resources
3. **Debugging ease**: Isolate failures to specific tiers
4. **Quality confidence**: Comprehensive validation when needed
5. **Flexible workflow**: Adapt to task requirements
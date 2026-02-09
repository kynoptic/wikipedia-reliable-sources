Walk through the tiered testing ladder systematically, interpreting failures at each level and escalating appropriately.

## Prerequisites
- Project has `make fast`, `make test-tiered`, `make test`, and `make full` commands configured
- Tests are properly marked/categorized by tier
- Test runner provides clear failure output

## Workflow

### Step 1: Start with fast tests

```bash
# Always begin here for rapid feedback
make fast
```

**If fast tests pass**: Proceed to Step 2.

**If fast tests fail**:
1. Read the failure output carefully
2. Identify the failing test name and assertion
3. Fix the immediate issue (usually a logic error)
4. Re-run `make fast` until all pass
5. DO NOT proceed until fast tests pass

Common fast test failures:
- Syntax errors or typos
- Incorrect calculations or logic
- Missing imports or dependencies
- Assertion errors in pure functions

### Step 2: Run standard tier tests

```bash
# Validates component interactions
make test-tiered
```

**If standard tests pass**: Proceed to Step 3.

**If standard tests fail**:
1. Check if it's a tier 1 regression (fix immediately)
2. For tier 2 failures, examine:
   - Database connection issues
   - File system permissions
   - Mock configuration problems
   - Component integration errors
3. Fix identified issues
4. Re-run `make test-tiered` (not just the failed test)
5. Ensure both tier 1 and 2 pass before proceeding

Common standard test failures:
- Test database not initialized
- Fixtures missing or outdated
- Mock responses don't match reality
- Race conditions in async code

### Step 3: Execute full test suite

```bash
# Comprehensive test coverage
make test
```

**If all tests pass**: Proceed to Step 4.

**If tests fail**:
1. Identify if failure is in tier 1, 2, or 3
2. For tier 3 failures, investigate:
   - Cross-component compatibility
   - End-to-end workflow issues
   - Performance timeouts
   - Resource exhaustion
3. Consider if the test is flaky:
   - Re-run 3 times to confirm
   - If intermittent, mark as flaky and fix separately
4. Fix the root cause
5. Re-run from appropriate tier:
   - Logic change: Start from `make fast`
   - Integration change: Start from `make test-tiered`
   - Config change: Can start from `make test`

Common full test failures:
- Slow tests timing out
- Memory or resource leaks
- Circular dependencies
- Environment-specific issues

### Step 4: Complete validation

```bash
# Final quality gates
make full
```

**If validation passes**: Ready to commit/merge!

**If validation fails**:
1. Check which quality gate failed:
   - **Linting**: Fix style issues, re-run `make full`
   - **Type checking**: Add type hints, re-run from `make fast`
   - **Security scan**: Address vulnerabilities, full re-test needed
   - **Coverage**: Add missing tests, start from tier 1
2. Fix issues in order of severity
3. For non-test failures, can often re-run just `make full`
4. For test additions/changes, restart from appropriate tier

Common validation failures:
- Code style violations
- Missing type annotations
- Security vulnerabilities in dependencies
- Coverage below threshold

## Optimization strategies

### Parallel execution
When tests are slow, parallelize within tiers:
```bash
PARALLEL=1 make test-tiered  # Run tier 2 in parallel
```

### Focused testing
During debugging, run specific test subsets:
```bash
FOCUS="test_user_" make fast  # Only user-related fast tests
```

### Fail fast
Stop at first failure for quicker debugging:
```bash
make fast MAXFAIL=1  # Stop after first failure
```

### Skip tiers (use sparingly)
In emergency fixes, skip to specific tier:
```bash
# Only when you're certain about the change scope
make test  # Skip straight to full suite
```

## Failure diagnosis flowchart

```
Test fails
    ↓
Is it deterministic?
    ├─ No → Mark as flaky, create issue, skip for now
    └─ Yes ↓
        What tier?
            ├─ Tier 1 → Fix logic, restart from fast
            ├─ Tier 2 → Fix integration, restart from test-tiered
            └─ Tier 3 → Fix system issue, can restart from test
```

## Best practices

1. **Never skip tier 1**: Fast tests catch 80% of bugs
2. **Fix failures immediately**: Don't accumulate test debt
3. **Run locally before CI**: Save CI resources and time
4. **Keep tiers pure**: Don't mix slow tests in fast tier
5. **Monitor tier times**: Rebalance if tiers get too slow

## Troubleshooting

### "make fast" not found
- Check if Makefile exists
- Verify command is defined: `make -n fast`
- Fall back to direct test runner: `pytest tests/unit -m fast`

### Tests pass locally but fail in CI
- Check environment variables
- Verify test database setup
- Compare dependency versions
- Look for timezone or locale issues

### Tier 2 slower than tier 3
- Audit test categorization
- Move slow tier 2 tests to tier 3
- Check for missing test markers

### Flaky test detection
```bash
# Run test multiple times to detect flakiness
for i in {1..10}; do
    make test || echo "Failed on iteration $i"
done
```

## Emergency protocols

When you need to ship immediately:
1. Run `make fast` - must pass
2. Run specific tests for changed code
3. Document skipped tiers in PR
4. Create follow-up issue for full validation
5. Run full suite post-merge

Never skip all testing, no matter the urgency.
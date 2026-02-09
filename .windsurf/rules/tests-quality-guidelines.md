---
trigger: model_decision
description: "Focus on test behavior and quality over coverage metrics to prevent vanity tests and ensure meaningful validation."
---
# Test quality over coverage metrics

## Quality-first approach

- **Prioritize behavior verification** over code coverage percentages
- Write tests that would fail if the underlying functionality broke
- Focus on user-facing behaviors and system contracts, not implementation details
- Replace coverage targets with test quality metrics

## Behavioral test naming

- Use descriptive names that specify expected behavior:
  - `test_should_X_when_Y` - Describes positive outcomes
  - `test_rejects_X_when_Y` - Describes error handling
  - `test_returns_X_given_Y` - Describes transformations
- Avoid vague names like `test_calculate()` or `test_save()`
- Test names should make the expected behavior obvious to readers

## Strategic mocking approach

- **Mock external dependencies only**: databases, APIs, file systems, external services
- **Don't mock internal objects**: validators, business logic, domain objects
- Test real object interactions to verify actual system behavior
- Excessive mocking often indicates shallow "vanity tests"

### Mock discipline limits
- **Maximum 5 mocks per test**: More indicates poor test design
- **3:1 mock-to-assertion ratio**: At least 3 assertions per mock
- **Zero mock returns for logic**: Never mock to return calculated values
- **Mock boundaries only**: External services, I/O, time, randomness

## Identify and eliminate vanity tests

Remove tests that:
- Only verify mocks were called without checking outcomes
- Pass regardless of whether the feature actually works
- Test implementation details instead of behavior
- Were written solely to increase coverage numbers

### Vanity test examples (BAD)
```python
# BAD: Tests mock instead of behavior
def test_save_calls_database():
    mock_db.save.assert_called_once()  # Only checks mock

# BAD: Tests implementation not behavior
def test_uses_specific_algorithm():
    assert obj._internal_method() == 'quicksort'

# BAD: Would pass even if broken
def test_calculator():
    mock_calc.add.return_value = 5
    assert calculator.add(2, 3) == 5  # Always passes!
```

### Behavioral test examples (GOOD)
```python
# GOOD: Tests observable behavior
def test_should_calculate_total_with_tax_when_items_added():
    cart = ShoppingCart()
    cart.add_item(price=100, tax_rate=0.1)
    assert cart.total() == 110

# GOOD: Tests error handling
def test_rejects_negative_quantity_when_adding_item():
    with pytest.raises(ValueError, match="Quantity must be positive"):
        cart.add_item(price=10, quantity=-1)

# GOOD: Tests actual data transformation
def test_returns_sorted_items_when_multiple_added():
    items = [Item(3), Item(1), Item(2)]
    result = sort_items(items)
    assert [i.value for i in result] == [1, 2, 3]
```

## Property-based and edge case testing

- Use property-based testing (e.g., `hypothesis`, `fast-check`) to validate invariants
- Include error paths and boundary conditions
- Test with realistic data, not just happy-path scenarios
- Verify error messages and exception types are meaningful

## Quality metrics over coverage metrics

Replace percentage targets with:
- **Behavioral naming score**: % of tests with behavior-focused names
- **Error path coverage**: % of functions with error condition tests
- **Mock ratio**: Lower is better - fewer mocks per assertion
- **Mutation score**: % of introduced bugs caught by tests
- **Test maintenance effort**: Time needed to update tests when requirements change

## Integration with AI workflows

When using AI agents for test improvement:
- Request behavioral test names in prompts
- Ask for tests that verify outcomes, not implementation
- Specify minimal strategic mocking
- Require error cases and edge conditions
- Validate that tests would fail if behavior broke

## Test audit requirements

### Mandatory audit script
Every project MUST include a test quality audit script to detect:
- Tests exceeding 5 mocks
- Tests with poor mock-to-assertion ratios
- Tests with only mock assertions
- Tests with implementation-focused names
- Tests that don't verify outcomes

Example audit script:
```python
#!/usr/bin/env python3
"""Test quality audit script"""
import ast
import sys
from pathlib import Path

def audit_test_file(file_path):
    """Audit a single test file for quality issues"""
    issues = []

    with open(file_path) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            # Check naming
            if not any(word in node.name for word in ['should', 'when', 'given', 'returns', 'rejects']):
                issues.append(f"{node.name}: Non-behavioral test name")

            # Count mocks and assertions
            mock_count = count_mocks(node)
            assert_count = count_assertions(node)

            if mock_count > 5:
                issues.append(f"{node.name}: Too many mocks ({mock_count})")

            if mock_count > 0 and assert_count / mock_count < 3:
                issues.append(f"{node.name}: Poor mock-to-assertion ratio ({assert_count}/{mock_count})")

    return issues

# Run: python audit_tests.py
```

### Quality gates
The audit script must be run:
- Before every commit (pre-commit hook)
- In CI pipeline (must pass to merge)
- Weekly in team reviews
- When adding new tests

## FORBIDDEN practices

- **NEVER bypass failing tests** without explicit user permission
- **NEVER write tests just to hit coverage targets**
- **NEVER mock everything** - preserve real object interactions where safe
- **NEVER accept tests that pass with broken functionality**
- **NEVER sacrifice test quality for coverage metrics**
- **NEVER skip the audit script** - quality checks are mandatory
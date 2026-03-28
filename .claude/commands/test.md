---
name: test
description: Run test suite with coverage analysis and reporting
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Test Command

Route to the **TDD Guide** or **Debugger** agent to run tests, analyze coverage, and debug test failures.

## Usage

```
/test [--coverage] [--watch] [--debug] [--suite=<name>]
```

## Examples

### Example 1: Run All Tests
```
/test --coverage
```

Response: Test Runner:
1. Executes unit, integration, and E2E tests
2. Generates coverage report
3. Shows gaps in coverage
4. Identifies flaky tests
5. Reports summary

### Example 2: Watch Mode (Development)
```
/test --watch
```

Response: Test Runner:
1. Runs tests in watch mode
2. Re-runs on file changes
3. Provides quick feedback
4. Enables rapid iteration

### Example 3: Debug Failing Test
```
/test --debug
```

Response: Test Debugger:
1. Identifies failing tests
2. Provides context about failure
3. Suggests root cause
4. Recommends fix
5. Shows how to reproduce locally

### Example 4: Specific Test Suite
```
/test --suite=api
```

Response: Test Runner:
1. Runs only API integration tests
2. Provides detailed output
3. Shows any failures with context
4. Reports execution time

## Test Organization

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx
├── services/
│   ├── api.ts
│   └── api.test.ts
└── __tests__/
    ├── integration/
    └── e2e/
```

## Test Types

- **Unit Tests**: Individual functions, utilities, components
- **Integration Tests**: Components working together, API endpoints
- **E2E Tests**: Complete user workflows

## Coverage Requirements

- **Minimum**: 80% line coverage
- **Target**: 85%+ coverage
- **Critical Paths**: 95%+ for auth, payments, data integrity
- **Exclusions**: Generated code, third-party code, test files

## Test Execution

### Pre-Commit
```
npm test -- --related-to-changed-files
```

### Before Merge
```
npm test --coverage
```

### CI/CD Pipeline
```
npm test -- --ci --coverage --reporters=github-actions
```

## Coverage Report

Shows:
- Line coverage percentage
- Branch coverage percentage
- Function coverage percentage
- Statement coverage percentage
- Files below threshold

## Common Test Failures

- **Timeout**: Test takes too long
- **Flakiness**: Test passes sometimes, fails other times
- **Mock Issues**: Mock not set up correctly
- **Data Setup**: Test data missing or incorrect
- **Assertion Failure**: Expected vs actual mismatch

## Debugging Failing Tests

1. **Understand**: Read error message carefully
2. **Isolate**: Run single test in isolation
3. **Inspect**: Add temporary console.log to debug
4. **Reproduce**: Create minimal reproducible case
5. **Fix**: Update code or test
6. **Verify**: Run test again to confirm

## Test Performance

- **Target**: Individual tests <100ms
- **Suite**: All tests <30 seconds
- **CI**: <5 minutes for full suite
- **Parallel Execution**: Run tests concurrently when possible

## Flaky Test Handling

Flaky tests are failures that pass when retried:

1. **Identify**: Mark with @flaky
2. **Investigate**: Find root cause
3. **Fix**: Make test deterministic
4. **Verify**: Runs 10x without failure

## Test Output Format

```
PASS src/components/Button.test.tsx
  Button Component
    ✓ renders with text (45ms)
    ✓ handles click events (32ms)
    ✓ applies custom className (28ms)

Test Suites: 1 passed, 1 total
Tests:       3 passed, 3 total
Coverage:    86% lines, 84% branches
Time:        1.234s
```

## When to Use

- Before committing code
- Before merging pull requests
- Validating bug fixes
- Regression testing
- Before deployments
- Debugging test failures

## When NOT to Use

- Tests not written yet (use /tdd first)
- Spike/exploratory code
- Documentation-only changes

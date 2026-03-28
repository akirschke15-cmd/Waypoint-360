---
name: tdd
description: Write tests first before implementing code following TDD methodology
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# TDD Command

Route to the **TDD Guide** agent to establish test-first development workflow and ensure comprehensive test coverage.

## Usage

```
/tdd <feature_or_module>
```

## Examples

### Example 1: Feature Implementation
```
/tdd User authentication system
```

Response: TDD Guide:
1. Identifies test types needed (unit, integration, e2e)
2. Writes failing tests for each requirement
3. Provides test file templates with RED tests
4. Validates 80%+ coverage targets
5. Suggests mock/stub strategy

### Example 2: Bug Fix with Tests
```
/tdd Fix N+1 query issue in user list endpoint
```

Response: TDD Guide:
1. Writes test that reproduces the performance issue
2. Establishes baseline (current slow query count)
3. Implements fix
4. Validates test now passes with improved query count
5. Adds regression test

## Expected Output

- **Test Plan**: Unit/integration/e2e breakdown
- **RED Tests**: Initial failing test files
- **Test Structure**: How tests are organized
- **Coverage Target**: 80%+ coverage goals
- **Mock Strategy**: What to mock vs. test integration
- **Verification Checklist**: How to verify tests are correct

## Test Types

- **Unit Tests**: Individual functions, utilities, components
- **Integration Tests**: Multiple components working together, API endpoints
- **E2E Tests**: Complete user workflows, critical paths

## Coverage Requirements

- **Target**: 80%+ line coverage minimum
- **Critical Paths**: 95%+ for auth, payment, data integrity
- **Edge Cases**: All boundary conditions covered

## When to Use

- Starting new feature development
- Fixing bugs with test coverage
- Improving test coverage
- Reducing test flakiness
- Adding regression tests

## When NOT to Use

- Legacy code with existing tests
- Pure documentation tasks
- Infrastructure configuration
- Configuration-only changes

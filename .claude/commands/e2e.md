---
name: e2e
description: Design and implement end-to-end tests for critical user workflows
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# E2E Command

Route to the **TDD Guide** or **Fullstack Engineer** agent to design and implement end-to-end tests for critical user workflows.

## Usage

```
/e2e <user_workflow>
```

## Examples

### Example 1: Payment Flow
```
/e2e User completes checkout and payment successfully
```

Response: Agent designs and implements:
1. Test steps: Browse products, add to cart, checkout, enter payment
2. Verification: Order created, email sent, payment recorded
3. Error cases: Failed payment, network error, validation failure
4. Cleanup: Test data removed after test

### Example 2: Authentication Flow
```
/e2e User signs up, verifies email, and logs in
```

Response: Agent designs and implements:
1. Test steps: Sign up form, email verification link, login
2. Verification: User created, email sent, session established
3. Edge cases: Duplicate email, expired token, wrong password
4. Cleanup: Test user and data removed

## Test Structure

- **Setup**: Create test data, establish starting state
- **Steps**: User actions (click, type, navigate)
- **Assertions**: Verify expected outcomes at each step
- **Cleanup**: Remove test data, restore state

## Critical Workflows

Minimum E2E coverage for:
- [ ] User authentication (sign up, login, logout)
- [ ] Payment/checkout flow
- [ ] Core feature workflows
- [ ] Error handling paths
- [ ] Data validation

## Test Framework

- **Frontend**: Playwright, Cypress, Selenium
- **Decision**: Based on project stack
- **Configuration**: Isolated test environment

## Output

- **Test Suite**: Implementation-ready test code
- **Scenarios**: Happy path + error cases
- **Assertions**: Clear success/failure criteria
- **Execution Guide**: How to run E2E tests
- **CI Integration**: Pipeline integration instructions

## Best Practices

- Tests are independent, can run in any order
- Use stable selectors (data-testid preferred)
- Realistic test data and workflows
- Clear, descriptive test names
- Error messages explain failures
- Screenshot/video on failure

## Performance

- Tests complete in <5 seconds each
- Suite runs <2 minutes total
- Run on every merge to main
- Parallelizable tests preferred

## When to Use

- Testing critical user workflows
- Validation of multi-step processes
- Cross-layer integration testing
- Regression testing after breaking changes
- Pre-launch verification

## When NOT to Use

- Single-component testing (use unit tests)
- Pure API testing (use integration tests)
- UI styling verification
- Performance testing

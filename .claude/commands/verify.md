---
name: verify
description: Comprehensive verification and testing of implementation completeness and correctness
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Verify Command

Route to the **Fullstack Engineer** or **Code Reviewer** agent to verify implementation completeness before deployment.

## Usage

```
/verify <feature_or_component>
```

## Examples

### Example 1: Feature Verification
```
/verify user authentication feature
```

Response: Verifier:
1. Confirms all requirements implemented
2. Validates test coverage (80%+)
3. Checks API contracts match spec
4. Verifies frontend/backend integration
5. Confirms documentation complete
6. Validates error handling
7. Checks for hardcoded values or TODO comments

### Example 2: Component Verification
```
/verify UserProfile component
```

Response: Verifier:
1. Verifies component renders correctly
2. Confirms props are properly typed
3. Validates accessibility (a11y)
4. Checks responsive behavior
5. Confirms tests cover happy path and edge cases
6. Validates no performance issues

## Pre-Deployment Checklist

- [ ] All requirements implemented and working
- [ ] Tests passing (unit, integration, e2e)
- [ ] Test coverage meets 80%+ minimum
- [ ] Code review completed and approved
- [ ] No linting errors
- [ ] No console.log or debug statements
- [ ] No hardcoded values (use environment variables)
- [ ] No TODO/FIXME comments left
- [ ] Error handling implemented and tested
- [ ] Edge cases handled
- [ ] Performance acceptable
- [ ] Security reviewed
- [ ] Database migrations (if needed)
- [ ] Environment variables documented
- [ ] API contracts match documentation
- [ ] Accessibility standards met (if UI)
- [ ] Mobile responsive (if UI)
- [ ] Loading states visible to user
- [ ] Error messages user-friendly
- [ ] Documentation updated

## Verification Categories

- **Functional**
  - Requirements met
  - Happy path works
  - Edge cases handled
  - Error scenarios covered

- **Testing**
  - Unit tests: 80%+ coverage
  - Integration tests: APIs working
  - E2E tests: Critical workflows
  - No test flakiness

- **Code Quality**
  - Linting: 0 errors
  - Type checking: 0 errors
  - Complexity: Reasonable
  - Duplication: Minimized

- **Performance**
  - API p95 < 200ms
  - Page load LCP < 2.5s
  - Bundle size appropriate
  - No N+1 queries

- **Security**
  - No hardcoded secrets
  - Input validation
  - Authentication/authorization
  - OWASP compliance

- **Accessibility (UI)**
  - ARIA labels present
  - Keyboard navigation works
  - Color contrast WCAG AA
  - Alt text on images

- **Documentation**
  - API documented
  - Architecture clear
  - README updated
  - Examples provided

## Output Format

- **Verification Status**: PASS/FAIL/CONDITIONAL
- **Checklist**: All items with status
- **Issues Found**: By severity
- **Blockers**: Must fix before deploy
- **Warnings**: Should fix, but not blocking
- **Suggestions**: Nice-to-have improvements

## Blocking Issues

Can't deploy if:
- Tests failing
- Critical security vulnerability
- Missing authentication
- Data integrity at risk
- Breaking API change undocumented

## When to Use

- Before merging to main
- Before deployment to production
- Feature completion verification
- Release validation
- Handoff verification

## When NOT to Use

- Work in progress (use during development, not at end)
- Pure documentation updates
- Configuration changes only

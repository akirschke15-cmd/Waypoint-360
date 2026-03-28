---
name: quality-gate
description: Enforce quality standards and gate code promotion through quality checks
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Quality Gate Command

Route to the **Code Reviewer** or **Performance Optimizer** agent to enforce quality standards and gate code promotion.

## Usage

```
/quality-gate [--strict] [--focus=<area>]
```

## Examples

### Example 1: Standard Quality Gate
```
/quality-gate
```

Response: Gate Evaluator:
1. Runs comprehensive quality checks
2. Validates all standards met
3. Reports pass/fail status
4. Provides detailed metrics
5. Blocks promotion if failures

### Example 2: Strict Mode
```
/quality-gate --strict
```

Response: Gate Evaluator:
1. Applies stricter thresholds
2. No warnings allowed (all issues must be fixed)
3. Higher coverage requirements (90% instead of 80%)
4. Zero-tolerance for security issues

### Example 3: Performance Focused
```
/quality-gate --focus=performance
```

Response: Gate Evaluator:
1. Emphasizes performance metrics
2. Validates latency targets
3. Checks bundle size impact
4. Reviews caching strategies

## Quality Standards

### Mandatory (Blocking)

- [ ] Test coverage: 80%+ minimum
- [ ] Linting: 0 errors
- [ ] Type checking: 0 errors
- [ ] No hardcoded secrets
- [ ] Critical security issues: 0
- [ ] Tests passing: 100%

### Strong (Enforced)

- [ ] Test coverage: 85%+ recommended
- [ ] No linting warnings
- [ ] No type warnings
- [ ] Code review approved
- [ ] High security issues: 0
- [ ] API documented

### Guidelines (Encouraged)

- [ ] 90%+ test coverage
- [ ] <30 line functions
- [ ] <10 cyclomatic complexity
- [ ] No TODO comments
- [ ] Clean git history

## Gate Levels

### Level 1: PR Gate
When opening pull request:
- Linting passes
- Type checking passes
- Tests pass

### Level 2: Review Gate
Before approval:
- Code review completed
- Coverage maintained or improved
- No security issues
- Documentation updated

### Level 3: Merge Gate
Before merging to main:
- All Level 1 and 2 gates pass
- All reviews approved
- Build succeeds
- E2E tests pass

### Level 4: Deploy Gate
Before production deployment:
- All previous gates pass
- Performance acceptable
- Database migrations tested
- Rollback plan documented
- Monitoring configured

## Metrics Dashboard

- **Coverage**: Current vs. target
- **Performance**: Latency p50/p95/p99
- **Reliability**: Test pass rate, build success rate
- **Security**: Vulnerabilities by severity
- **Code Quality**: Complexity, duplication, issues

## Bypass Procedures

Urgent fixes may bypass gates if:
1. **Exception Approved**: By tech lead
2. **Justification Documented**: Why gate waived
3. **Follow-up Task**: To address gaps within 24 hours
4. **Monitoring Enhanced**: Increased alerting
5. **Audit Trail**: Logged for compliance

## When Gate Fails

1. **Identify**: Which gate and why
2. **Root Cause**: What caused failure
3. **Fix**: Address the underlying issue
4. **Verify**: Run gate again
5. **Learn**: Update processes if pattern

## Severity Levels

- **Critical**: Data loss, security, availability
- **High**: Performance, breaking change
- **Medium**: Code quality, maintainability
- **Low**: Style, documentation

## When to Use

- Pull request checks
- Pre-merge validation
- Release gating
- Environment promotion
- Quality audits

## When NOT to Use

- Work in progress (gates shouldn't exist during development)
- Experimental branches
- Spike/exploratory work

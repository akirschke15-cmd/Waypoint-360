---
name: code-review
description: Conduct comprehensive code review for quality, security, and best practices
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Code Review Command

Route to the **Code Reviewer** agent for comprehensive code quality, security, and standards review.

## Usage

```
/code-review <file_or_directory>
```

## Examples

### Example 1: PR Code Review
```
/code-review src/auth/login.ts
```

Response: Code Reviewer:
1. Reviews code against team standards
2. Identifies security issues (OWASP)
3. Checks test coverage
4. Validates performance implications
5. Provides specific feedback with line numbers

### Example 2: Module Audit
```
/code-review src/components/ --security
```

Response: Code Reviewer:
1. Audits all files in directory
2. Focuses on security vulnerabilities
3. Checks authentication/authorization patterns
4. Validates input sanitization
5. Reviews error handling

## Review Checklist

- **Code Quality**
  - [ ] Naming conventions followed
  - [ ] Functions under 50 lines
  - [ ] Single responsibility principle
  - [ ] DRY (Don't Repeat Yourself)
  - [ ] Comments explain WHY not WHAT

- **Security (OWASP)**
  - [ ] No hardcoded secrets
  - [ ] Input validation present
  - [ ] SQL injection prevention
  - [ ] XSS protection (if web)
  - [ ] CSRF protection (if web)
  - [ ] Authentication/authorization correct

- **Testing**
  - [ ] Tests pass
  - [ ] 80%+ coverage maintained
  - [ ] Edge cases covered
  - [ ] Error paths tested

- **Performance**
  - [ ] No N+1 queries
  - [ ] Caching strategies appropriate
  - [ ] Bundle size impact reasonable
  - [ ] No memory leaks

- **Accessibility (if UI)**
  - [ ] ARIA labels present
  - [ ] Keyboard navigation works
  - [ ] Color contrast adequate
  - [ ] Alt text on images

## Output Format

- **Issues Found**: Categorized by severity (Critical, High, Medium, Low)
- **Line-by-Line Feedback**: Specific suggestions with context
- **Best Practices**: Proactive improvements suggested
- **Risk Assessment**: What could go wrong?
- **Approval Decision**: Ready to merge / Needs changes

## Severity Levels

- **Critical**: Security vulnerability, data loss risk, production outage
- **High**: Performance issue, coverage drop, architectural concern
- **Medium**: Best practice violation, maintainability concern
- **Low**: Style suggestion, documentation improvement

## When to Use

- Before merging pull requests
- Security audit of sensitive code
- Code quality gate
- Onboarding code review
- Refactoring validation

## When NOT to Use

- Simple documentation updates
- Configuration-only changes
- Work in progress (WIP)
- Spike/exploratory code

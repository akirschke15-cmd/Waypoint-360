---
name: review
description: Conduct pull request review with focus on requirements, testing, and quality
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Review Command

Route to the **Code Reviewer** agent for comprehensive pull request review.

## Usage

```
/review [file_or_branch] [--security] [--performance]
```

## Examples

### Example 1: Quick PR Review
```
/review
```

Response: Code Reviewer:
1. Examines changed files in current branch
2. Reviews code against standards
3. Checks test coverage
4. Validates quality gates
5. Provides feedback

### Example 2: Security-Focused Review
```
/review --security
```

Response: Code Reviewer:
1. Focuses on security implications
2. Checks for vulnerabilities
3. Validates authentication/authorization
4. Reviews access control changes
5. Checks for secrets leakage

### Example 3: Performance Review
```
/review --performance
```

Response: Code Reviewer:
1. Analyzes performance impact
2. Checks for N+1 queries
3. Reviews caching strategies
4. Evaluates bundle size impact
5. Suggests optimizations

## Review Checklist

### Requirements
- [ ] Implementation matches requirements
- [ ] No scope creep
- [ ] Acceptance criteria met
- [ ] Edge cases handled
- [ ] Error scenarios covered

### Testing
- [ ] Test coverage 80%+
- [ ] All tests passing
- [ ] Tests are meaningful (not just coverage)
- [ ] Edge cases tested
- [ ] Error paths tested

### Code Quality
- [ ] Naming is clear and consistent
- [ ] Functions are focused (single responsibility)
- [ ] No magic numbers or strings
- [ ] Comments explain WHY not WHAT
- [ ] No code smells or anti-patterns

### Performance
- [ ] No N+1 database queries
- [ ] Caching strategies appropriate
- [ ] Bundle size impact acceptable
- [ ] No unnecessary re-renders (if React)
- [ ] No memory leaks

### Security
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Output properly escaped
- [ ] Authentication/authorization correct
- [ ] No security vulnerabilities

### Accessibility (if UI changes)
- [ ] ARIA labels present
- [ ] Keyboard navigation works
- [ ] Color contrast adequate
- [ ] Alt text on images
- [ ] Focus management correct

### Documentation
- [ ] README updated if needed
- [ ] API docs updated if changed
- [ ] Code comments where needed
- [ ] Commit messages clear
- [ ] Migration docs (if DB changes)

## Review Levels

### Approve
- Meets all standards
- High quality code
- Tests comprehensive
- No blocking issues

### Approve with Comments
- Generally good
- Minor suggestions for improvement
- No blocking issues
- Improvements can be done post-merge if non-critical

### Request Changes
- Blocking issues found
- Must fix before merge
- Re-review required

### Comments Only
- FYI information
- Discussion points
- No blocking

## Feedback Format

```
[Category]: [Title]
[Severity]: [Critical/High/Medium/Low]

[Description of issue]

Suggestion:
[How to fix]

[Code example if applicable]
```

## Response Time

- **Urgent (critical fix)**: 1 hour
- **High priority**: 4 hours
- **Normal**: 24 hours
- **Low priority**: 48 hours

## When to Use

- Before merging any code
- Pull request review automation
- Code quality enforcement
- Knowledge sharing and mentoring
- Compliance verification

## When NOT to Use

- WIP branches (no review yet)
- Experimental spikes
- Documentation-only changes (might skip review)
- Configuration updates (depends on impact)

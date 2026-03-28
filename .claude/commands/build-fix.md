---
name: build-fix
description: Resolve build, compile, or CI/CD pipeline errors with minimal targeted fixes
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Build Fix Command

Route to the **Build Error Resolver** agent to quickly diagnose and fix pipeline failures.

## Usage

```
/build-fix [error_context]
```

## Examples

### Example 1: Compile Error
```
/build-fix npm run build failed with type error in UserComponent.tsx
```

Response: Build Error Resolver:
1. Parses error context
2. Identifies root cause (type mismatch, missing import, etc.)
3. Provides minimal fix with line-by-line explanation
4. Verifies fix doesn't introduce regressions

### Example 2: CI Pipeline Failure
```
/build-fix GitHub Actions test suite timeout on main branch
```

Response: Build Error Resolver:
1. Analyzes test execution logs
2. Identifies slow test causing timeout
3. Suggests optimization or timeout increase
4. Validates pipeline passes locally before push

## Resolution Approach

1. **Understand**: Parse error message carefully
2. **Isolate**: Identify exact file and line causing failure
3. **Root Cause**: Why is this failing? (Missing dep, breaking change, env issue?)
4. **Fix**: Minimal, targeted change only
5. **Verify**: Build passes, tests pass, no new errors

## Minimal Diff Principle

- One logical change per fix
- No refactoring in fix commits
- No unrelated cleanup
- Reverse change immediately if causes regression

## Output

- **Error Analysis**: What went wrong?
- **Root Cause**: Why it failed
- **Minimal Fix**: Exact changes needed (copy-paste ready)
- **Verification**: How to confirm fix works
- **Prevention**: How to prevent next time

## Common Build Issues

- **Compile Errors**
  - Missing imports
  - Type mismatches
  - Syntax errors
  - Undefined references

- **Test Failures**
  - Assertion failures
  - Timeout/flakiness
  - Environment setup
  - Mock/stub issues

- **Integration Issues**
  - Dependency conflicts
  - Version mismatch
  - Breaking API changes
  - Configuration errors

- **Deployment Issues**
  - Artifact not found
  - Environment variable missing
  - Permission denied
  - Service unavailable

## When to Use

- Build pipeline blocked (red CI/CD)
- Local build fails
- Test suite failing
- Deploy failing
- Urgent fix needed quickly

## When NOT to Use

- Feature development (use plan/tdd)
- Code quality issues (use code-review)
- Architecture changes (use architect)

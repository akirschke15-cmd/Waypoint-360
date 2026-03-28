---
name: fix-loop
description: Autonomous test-driven bug fix cycle with baseline capture, failure analysis, fix iteration, and regression checking.
origin: Boiler 3.0
version: 1.0
---

# Test-Driven Fix Loop Skill

Autonomous bug fix cycle. Point at a failing test or bug, and iterate fix-test-fix until the suite is green.

## Inputs

The user provides one of:
- A specific failing test name or file
- A bug description or error message
- "Fix all failing tests"

## Workflow

### 1. Baseline
Run the full test suite (or the relevant subset) and capture the state:
```bash
npm run test 2>&1 | tail -30
```
Record: total tests, passing, failing, error messages.

### 2. Analyze Failures
For each failing test:
- Read the test file to understand what it expects.
- Read the source code it exercises.
- Identify the root cause (not the symptom).

Group related failures. A single root cause often breaks multiple tests.

### 3. Fix Loop

**For each root cause:**

a) Apply the fix to the source code (not the test, unless the test itself is wrong).

b) Run the affected test(s):
```bash
npm run test -- --testPathPattern="<relevant_test>" 2>&1 | tail -20
```

c) If still failing, read the new error, adjust, and re-run. Max 3 iterations per root cause before escalating to the user.

d) If passing, run the full suite to check for regressions:
```bash
npm run test 2>&1 | tail -30
```

e) If regressions appeared, fix them before moving to the next root cause.

### 4. Wrap Up

Once all originally-failing tests pass and no new failures exist:
- Run `npx tsc --noEmit` to confirm type safety.
- Log a summary:
  ```
  ## Fix Loop Summary
  - Tests fixed: <count>
  - Root causes addressed: <list>
  - Files modified: <list>
  - Total suite: <passing>/<total> passing
  ```
- Commit with message: `fix: resolve <N> failing tests - <root cause summary>`

## Rules

- Never modify a test to make it pass unless the test itself is genuinely wrong (outdated assertion, wrong mock). If you suspect the test is wrong, flag it to the user.
- Fix source code to match test expectations, not the other way around.
- 3-iteration max per root cause. If you can't fix it in 3, report what you tried and let the user decide.
- Always run the FULL suite after all fixes, not just the previously-failing tests.
- Do not ask for clarification mid-loop. Make your best judgment and keep moving. Report decisions in the summary.

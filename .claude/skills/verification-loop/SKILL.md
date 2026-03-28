---
name: verification-loop
description: Systematic code verification with 6-phase validation loop. Build, type check, lint, test, security, and diff review. Ensures every change meets production standards before deployment.
origin: ECC
version: 2.0
---

# Verification Loop Skill

A systematic 6-phase verification loop ensuring every code change meets production standards.

## When to Activate

- Before committing code
- After implementing features
- During code review
- Before deployment
- Establishing CI/CD validation gates

## The 6-Phase Loop

### Phase 1: Build

Verify code compiles and bundles correctly.

```bash
# TypeScript/Node.js
npm run build

# Python
python -m py_compile src/
python -m pytest --collect-only  # syntax check

# Go
go build ./...

# Rust
cargo build
```

Check for:
- Syntax errors
- Missing imports
- Broken references
- Bundling failures

**Failure action:** Fix compilation errors before proceeding.

### Phase 2: Type Check

Verify type safety across the codebase.

```bash
# TypeScript
npx tsc --noEmit

# Python (with type hints)
mypy src/ --strict

# Go (built-in)
go vet ./...
```

Check for:
- Type mismatches
- Missing type annotations
- Unsafe any usage
- Generic constraint violations

**Failure action:** Add proper types or fix type errors.

### Phase 3: Lint

Verify code style and best practices.

```bash
# JavaScript/TypeScript
npx eslint src/ --fix

# Python
ruff check src/ --fix
pylint src/

# Go
golangci-lint run ./...
```

Check for:
- Style violations
- Unused variables
- Dead code
- Anti-patterns
- Security issues (via linters)

**Failure action:** Fix linting errors or update linter config.

### Phase 4: Test

Verify functionality with automated tests.

```bash
# Run all tests
npm test

# With coverage
npm test -- --coverage

# Specific test file
npm test -- user.test.ts

# Python
pytest -v --cov=src/

# Go
go test ./...
```

Check for:
- Failing unit tests
- Failing integration tests
- Coverage below threshold (>80%)
- Flaky tests
- Performance regression

**Failure action:** Fix broken tests or improve coverage. Mark flaky tests for investigation.

### Phase 5: Security

Verify no security vulnerabilities introduced.

```bash
# Dependency vulnerabilities
npm audit
cargo audit
pip install safety && safety check

# SAST (Static Application Security Testing)
npm install --save-dev @typescript-eslint/eslint-plugin
# ESLint with security plugins catches common issues

# Secret scanning
npm install --save-dev secretlint
secretlint "**/*.ts" "**/*.js"

# Container security (if using Docker)
docker scan myimage:latest
```

Check for:
- Known vulnerabilities in dependencies
- Hardcoded secrets
- SQL injection vulnerabilities
- XSS vulnerabilities
- Insecure patterns (weak crypto, no auth checks)

**Failure action:** Update dependencies, remove secrets, fix vulnerabilities.

### Phase 6: Diff Review

Verify changes match intent and standards.

```bash
# View changes before committing
git diff

# Compare against main
git diff main...HEAD

# View changed files
git status

# Review specific file
git diff file.ts
```

Check for:
- Unintended changes
- Incomplete features
- Hardcoded debugging code
- Large functions that should be split
- Changes that violate coding standards

**Failure action:** Revert unintended changes, break up large changes, refactor as needed.

## Automated Verification Script

```bash
#!/bin/bash
# verify-loop.sh

set -e

echo "=== PHASE 1: Build ==="
npm run build

echo "=== PHASE 2: Type Check ==="
npx tsc --noEmit

echo "=== PHASE 3: Lint ==="
npx eslint src/

echo "=== PHASE 4: Test ==="
npm test -- --coverage

echo "=== PHASE 5: Security ==="
npm audit
npm run secret-check

echo "=== PHASE 6: Diff Review ==="
git diff --stat
echo "Review changes above carefully"

echo "All verification phases passed!"
```

Run with:
```bash
chmod +x verify-loop.sh
./verify-loop.sh
```

## Configuration Examples

### ESLint (.eslintrc.json)

```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint", "security"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "no-console": ["error", { "allow": ["warn", "error"] }],
    "security/detect-non-literal-regexp": "warn",
    "security/detect-unsafe-regex": "warn"
  }
}
```

### Prettier (.prettierrc.json)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false
}
```

### TypeScript (tsconfig.json)

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

### pytest (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=src --cov-report=html --strict-markers"
markers = ["slow: marks tests as slow", "integration: marks tests as integration"]

[tool.mypy]
strict = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Pre-Commit Hook Integration

Automatically run verification on commit:

```bash
# .githooks/pre-commit
#!/bin/bash

echo "Running verification loop..."

npm run build || exit 1
npx tsc --noEmit || exit 1
npx eslint src/ || exit 1
npm test || exit 1
npm run security-check || exit 1

echo "All checks passed!"
```

Install:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "npm"

      - name: Phase 1 - Build
        run: npm run build

      - name: Phase 2 - Type Check
        run: npx tsc --noEmit

      - name: Phase 3 - Lint
        run: npx eslint src/

      - name: Phase 4 - Test
        run: npm test -- --coverage

      - name: Phase 5 - Security
        run: npm audit

      - name: Upload Coverage
        uses: codecov/codecov-action@v3
        if: always()
        with:
          files: ./coverage/lcov.info
```

## Common Failure Scenarios

### TypeScript Errors

```
src/user.ts:5:20 - error TS7006: Parameter 'id' implicitly has type 'any'

// Fix: Add type annotation
async function getUser(id: string) { ... }
```

### Test Failures

```
FAIL  src/__tests__/user.test.ts
  User Service
    X should create user with valid email (45ms)
    - Expected: { email: "test@example.com" }
    + Received: null

// Fix: Check implementation logic
```

### Linting Issues

```
src/api.ts:12:1 - error: Unexpected console statement (no-console)

// Fix: Use proper logger
logger.info("Starting server")
```

### Coverage Below Threshold

```
ERROR: Coverage threshold not met. Expected 80%, actual 72%

// Fix: Add missing tests
test("edge case: empty input", () => { ... })
```

## Verification Checklist

Before marking code as verified:

- [x] Build completes without errors
- [x] All type checks pass (no any usage)
- [x] Linting passes (0 errors, 0 warnings)
- [x] All tests pass with >80% coverage
- [x] No security vulnerabilities detected
- [x] Changes reviewed and intentional
- [x] No hardcoded secrets
- [x] No debugging code left
- [x] Commit message is clear
- [x] Ready for merge/deployment

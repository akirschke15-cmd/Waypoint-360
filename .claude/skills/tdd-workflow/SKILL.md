---
name: tdd-workflow
description: Test-driven development patterns with coverage requirements, testing strategies for unit/integration/E2E tests, mocking patterns, and test maintenance. Build confidence through tests before implementation.
origin: ECC
version: 2.0
---

# TDD Workflow Skill

Test-driven development approach: write tests first, then implementation.

## When to Activate

- Starting new features
- Fixing bugs (write failing test first)
- Refactoring legacy code
- Building API endpoints
- Implementing business logic
- Ensuring code quality and maintainability

## TDD Workflow: Red-Green-Refactor

### Red: Write Failing Test

Start with a test that describes the desired behavior.

```typescript
// src/__tests__/user.service.test.ts
import { describe, it, expect } from 'vitest'
import { createUser } from '../user.service'

describe('createUser', () => {
  it('should create a user with valid email and password', async () => {
    const user = await createUser({
      email: 'alice@example.com',
      password: 'SecurePass123!'
    })

    expect(user.id).toBeDefined()
    expect(user.email).toBe('alice@example.com')
    expect(user.createdAt).toBeInstanceOf(Date)
  })

  it('should reject invalid email', async () => {
    expect(
      createUser({ email: 'invalid-email', password: 'Pass123!' })
    ).rejects.toThrow('Invalid email format')
  })

  it('should hash password before storage', async () => {
    const user = await createUser({
      email: 'bob@example.com',
      password: 'SecurePass123!'
    })

    // Password should not be stored in plaintext
    const stored = await db.users.findUnique({ where: { id: user.id } })
    expect(stored.password).not.toBe('SecurePass123!')
  })
})
```

Test fails because createUser doesn't exist yet. This is "Red" state.

### Green: Minimal Implementation

Implement just enough to make the test pass.

```typescript
// src/user.service.ts
import { hash } from 'bcrypt'

interface CreateUserInput {
  email: string
  password: string
}

export async function createUser(input: CreateUserInput) {
  // Validate email
  if (!input.email.includes('@')) {
    throw new Error('Invalid email format')
  }

  // Hash password
  const hashedPassword = await hash(input.password, 10)

  // Create user
  const user = await db.users.create({
    data: {
      email: input.email,
      password: hashedPassword,
      createdAt: new Date()
    }
  })

  return {
    id: user.id,
    email: user.email,
    createdAt: user.createdAt
  }
}
```

Test now passes. This is "Green" state.

### Refactor: Improve Without Changing Behavior

Extract validation, add error handling, improve types.

```typescript
// src/validation.ts
export function validateEmail(email: string): void {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    throw new Error('Invalid email format')
  }
}

export function validatePassword(password: string): void {
  if (password.length < 8) {
    throw new Error('Password must be at least 8 characters')
  }
}

// src/user.service.ts (refactored)
import { hash } from 'bcrypt'
import { validateEmail, validatePassword } from './validation'

export async function createUser(input: CreateUserInput) {
  validateEmail(input.email)
  validatePassword(input.password)

  const hashedPassword = await hash(input.password, 10)

  const user = await db.users.create({
    data: {
      email: input.email,
      password: hashedPassword,
      createdAt: new Date()
    }
  })

  return user
}
```

Tests still pass. Code is now cleaner and more maintainable. This is "Refactor" state.

## Test Layers

### Unit Tests

Test single functions in isolation, mocking dependencies.

```typescript
// src/__tests__/user.service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createUser } from '../user.service'

// Mock the database
vi.mock('../db', () => ({
  db: {
    users: {
      create: vi.fn()
    }
  }
}))

describe('createUser - Unit', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should call db.users.create with hashed password', async () => {
    const mockDb = vi.mocked(db)
    mockDb.users.create.mockResolvedValue({
      id: '123',
      email: 'alice@example.com',
      password: 'hashed_pass',
      createdAt: new Date()
    })

    await createUser({ email: 'alice@example.com', password: 'Pass123!' })

    expect(mockDb.users.create).toHaveBeenCalledWith({
      data: expect.objectContaining({
        email: 'alice@example.com',
        password: expect.not.stringContaining('Pass123!')
      })
    })
  })
})
```

Benefits:
- Fast (no I/O, no network)
- Isolated (easy to identify failure)
- Deterministic (no flakiness)

### Integration Tests

Test multiple components working together, with real dependencies or stubs.

```typescript
// src/__tests__/user.integration.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { createUser, getUserById } from '../user.service'
import { setupTestDb, teardownTestDb } from './test-db'

describe('User Service - Integration', () => {
  beforeAll(async () => {
    await setupTestDb()
  })

  afterAll(async () => {
    await teardownTestDb()
  })

  it('should create and retrieve user', async () => {
    const created = await createUser({
      email: 'alice@example.com',
      password: 'Pass123!'
    })

    const retrieved = await getUserById(created.id)

    expect(retrieved).toBeDefined()
    expect(retrieved.email).toBe('alice@example.com')
  })

  it('should prevent duplicate emails', async () => {
    await createUser({ email: 'bob@example.com', password: 'Pass123!' })

    expect(
      createUser({ email: 'bob@example.com', password: 'Pass456!' })
    ).rejects.toThrow('Email already exists')
  })
})
```

Benefits:
- Tests real database behavior
- Catches integration issues
- More confidence in functionality

### E2E Tests

Test complete user flows through the UI.

```typescript
// tests/e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test.describe('User Registration', () => {
  test('should register new user and redirect to dashboard', async ({ page }) => {
    await page.goto('/register')

    await page.locator('input[name="email"]').fill('alice@example.com')
    await page.locator('input[name="password"]').fill('SecurePass123!')
    await page.locator('button:has-text("Register")').click()

    await expect(page).toHaveURL('/dashboard')
    await expect(page.locator('h1')).toContainText('Welcome, alice@example.com')
  })

  it('should show error for invalid email', async ({ page }) => {
    await page.goto('/register')

    await page.locator('input[name="email"]').fill('invalid-email')
    await page.locator('button:has-text("Register")').click()

    await expect(page.locator('[role="alert"]')).toContainText('Invalid email')
  })
})
```

Benefits:
- Tests actual user experience
- Catches UI integration issues
- Validates entire feature

## Test Coverage

### Coverage Target: >80%

```typescript
// Measure with coverage tools
npm test -- --coverage

// Example output
file                   | stmts | branch | funcs | lines
-----------------------|-------|--------|-------|------
all files              |  85.2 |  78.4  | 90.1  | 85.5
 src/user.service.ts   |  92.5 |  88.3  | 100   | 92.0
 src/api/users.ts      |  78.9 |  65.2  | 80.0  | 79.5
```

Types of coverage:
- **Statements:** % of code lines executed
- **Branches:** % of conditional paths tested
- **Functions:** % of functions called
- **Lines:** % of source lines executed

### Coverage Checklist

- [x] Happy path covered
- [x] Edge cases covered (empty input, null, undefined)
- [x] Error conditions tested
- [x] Boundary conditions tested
- [x] Performance-critical paths measured
- [x] Security-sensitive code fully tested

## Mocking Patterns

### Function Mocking

```typescript
import { vi } from 'vitest'

const mockFetch = vi.fn()
mockFetch.mockResolvedValue({ ok: true, json: () => ({ id: 1 }) })

// Use in test
const result = await mockFetch('/api/users')
expect(mockFetch).toHaveBeenCalledWith('/api/users')
```

### Module Mocking

```typescript
vi.mock('../auth', () => ({
  authenticate: vi.fn().mockResolvedValue({ userId: '123' })
}))
```

### Partial Mocking

```typescript
import * as auth from '../auth'

vi.spyOn(auth, 'authenticate').mockResolvedValue({ userId: '456' })
```

### Spy (Track Without Replacing)

```typescript
const spy = vi.spyOn(console, 'log')
console.log('test')
expect(spy).toHaveBeenCalledWith('test')
```

## Test Organization

```
src/
├── user.service.ts
├── __tests__/
│   ├── user.service.test.ts      # Unit tests
│   ├── user.integration.test.ts  # Integration tests
│   └── fixtures/
│       └── user.fixtures.ts      # Test data
├── db.ts
└── validation.ts

tests/
└── e2e/
    └── auth.spec.ts             # E2E tests
```

## Test Data Fixtures

```typescript
// src/__tests__/fixtures/user.fixtures.ts
export const userFixture = {
  validInput: {
    email: 'alice@example.com',
    password: 'SecurePass123!'
  },
  invalidEmail: {
    email: 'invalid-email',
    password: 'SecurePass123!'
  },
  weakPassword: {
    email: 'bob@example.com',
    password: 'weak'
  }
}

// Use in tests
import { userFixture } from './fixtures/user.fixtures'

test('should create user with valid input', async () => {
  const user = await createUser(userFixture.validInput)
  expect(user.email).toBe('alice@example.com')
})
```

## Continuous Testing

### Watch Mode

```bash
npm test -- --watch
```

Auto-runs tests when files change.

### Pre-Commit Hook

```bash
# .githooks/pre-commit
npm test -- --bail
```

Prevents commits if tests fail.

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
```

## TDD Best Practices

- [x] Write failing test first
- [x] Make minimal changes to pass test
- [x] Run tests frequently (watch mode)
- [x] Keep tests independent (no shared state)
- [x] Test behavior, not implementation
- [x] Use descriptive test names
- [x] DRY up test code with fixtures and helpers
- [x] Aim for >80% coverage
- [x] Delete tests that no longer provide value
- [x] Refactor tests alongside code

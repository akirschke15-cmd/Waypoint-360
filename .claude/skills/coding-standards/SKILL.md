---
name: coding-standards
description: Universal coding standards for TypeScript, JavaScript, React, and Node.js. Covers naming conventions, immutability patterns, error handling, async/await, type safety, testing structure, and production-grade code quality.
origin: ECC
version: 2.1
---

# Coding Standards Skill

Universal standards ensuring consistency across all TypeScript, JavaScript, React, and Node.js projects.

## When to Activate

- Starting a new project or feature
- Code review and refactoring
- Establishing team/personal coding conventions
- Ensuring consistency in mixed-language codebases
- Implementing production-grade standards

## Naming Conventions

### Variables & Functions

```typescript
// GOOD: descriptive, camelCase
const userEmail = "user@example.com"
const maxRetries = 3
const isAuthenticated = true
const fetchUserData = async () => {}

// GOOD: boolean prefixes (is, has, can, should)
const isLoading = false
const hasPermission = true
const canDelete = false
const shouldRetry = true

// BAD: ambiguous, single letters (except loop indices)
const x = 5
const user_data = {}
const TEMP = "value"
const fetchData = () => {} // unclear what data
```

### Classes & Constructors

```typescript
// GOOD: PascalCase
class UserRepository {}
class ApiClient {}
class PaymentProcessor {}

// BAD: camelCase
class userRepository {}
class apiClient {}
```

### Constants

```typescript
// GOOD: UPPER_SNAKE_CASE (only for true constants)
const MAX_RETRIES = 3
const API_TIMEOUT_MS = 30000
const DEFAULT_PAGE_SIZE = 20

// GOOD: camelCase for const objects (values can change)
const defaultConfig = { port: 3000, env: "development" }
const apiEndpoints = { users: "/api/users", posts: "/api/posts" }

// BAD: mixing styles
const max_retries = 3
const maxRetries = 3 // use if not truly constant across app
```

### Files & Exports

```typescript
// GOOD: kebab-case for files
user-repository.ts
api-client.ts
payment-processor.ts

// GOOD: match filename to main export
export class UserRepository {} // in user-repository.ts
export const fetchUserData = () => {} // in fetch-user-data.ts

// GOOD: index.ts for barrel exports
// index.ts
export * from "./user-repository"
export * from "./api-client"
```

## Immutability Patterns

```typescript
// GOOD: const-first, reassign only when necessary
const user = { name: "Alice", age: 30 }
const updated = { ...user, age: 31 } // creates new object

// GOOD: readonly for object properties
interface User {
  readonly id: string
  readonly email: string
  name: string // only name is mutable
}

// GOOD: Array methods that don't mutate
const nums = [1, 2, 3]
const doubled = nums.map(n => n * 2) // returns new array
const filtered = nums.filter(n => n > 1) // returns new array

// BAD: mutating arrays
const nums = [1, 2, 3]
nums.push(4) // mutates original

// BAD: mutating objects
const user = { name: "Alice" }
user.name = "Bob" // mutates original (unless intentional)
```

## Type Safety

```typescript
// GOOD: explicit types
function getUserById(id: string): Promise<User | null> {
  return db.users.findUnique({ where: { id } })
}

// GOOD: type unions for multiple states
type AsyncState<T> =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: Error }

// GOOD: generic types for reusable patterns
function createMemo<T>(fn: () => T): () => T {
  let cached: T | undefined
  return () => {
    if (cached === undefined) cached = fn()
    return cached
  }
}

// BAD: any types (avoid)
const user: any = {} // loses type safety
function process(data: any) {} // any parameter

// BAD: overly broad unions
type Result = string | number | boolean | object | null // unclear intent
```

## Error Handling

```typescript
// GOOD: explicit error types
class ValidationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = "ValidationError"
  }
}

// GOOD: throw errors, don't return error codes
async function createUser(input: unknown) {
  const validated = UserSchema.parse(input) // throws on invalid
  return await db.users.create(validated)
}

// GOOD: catch specific errors
try {
  await deleteUser(id)
} catch (error) {
  if (error instanceof ValidationError) {
    return { success: false, error: error.message }
  }
  throw error // re-throw unknown errors
}

// GOOD: error boundaries for React
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    logger.error("Error boundary caught:", error, errorInfo)
  }
  render() {
    if (this.state.hasError) return <ErrorPage />
    return this.props.children
  }
}

// BAD: silent failures
try {
  await riskyOperation()
} catch (error) {
  // swallowed error, hard to debug
}

// BAD: error codes
function createUser(input: unknown): number {
  if (!validate(input)) return 1 // unclear what 1 means
  if (dbFails()) return 2 // unclear what 2 means
  return 0 // success
}
```

## Async/Await Patterns

```typescript
// GOOD: async/await over promise chains
async function fetchAndProcess(id: string) {
  const data = await fetchData(id)
  const processed = transform(data)
  await saveResult(processed)
  return processed
}

// GOOD: parallel execution with Promise.all
async function loadDashboard(userId: string) {
  const [user, posts, notifications] = await Promise.all([
    getUser(userId),
    getPosts(userId),
    getNotifications(userId)
  ])
  return { user, posts, notifications }
}

// GOOD: error handling in async
async function operation() {
  try {
    const result = await riskyOp()
    return { success: true, result }
  } catch (error) {
    console.error("Operation failed:", error)
    return { success: false, error: error.message }
  }
}

// BAD: promise chains (less readable)
fetchData(id)
  .then(data => transform(data))
  .then(processed => saveResult(processed))
  .catch(error => console.error(error))

// BAD: blocking on sequential operations
async function load() {
  const user = await getUser() // waits
  const posts = await getPosts() // waits, could parallel
  return { user, posts }
}
```

## React Patterns

```typescript
// GOOD: functional components, hooks
function UserCard({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUser(userId).then(u => {
      setUser(u)
      setLoading(false)
    })
  }, [userId])

  if (loading) return <Skeleton />
  if (!user) return <Error />
  return <div>{user.name}</div>
}

// GOOD: custom hooks for reusable logic
function useUser(userId: string) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUser(userId).then(u => {
      setUser(u)
      setLoading(false)
    })
  }, [userId])

  return { user, loading }
}

// GOOD: composition over props drilling
function App() {
  return (
    <UserProvider>
      <Dashboard />
    </UserProvider>
  )
}

// BAD: class components (unless legacy)
class UserCard extends React.Component {}

// BAD: props drilling
<Component userId={userId} userName={userName} userEmail={userEmail} />
// instead: use context, custom hooks, or composition
```

## Testing Structure

```typescript
// GOOD: clear test names
test("creates user with valid email", async () => {
  const user = await createUser({ email: "test@example.com" })
  expect(user.email).toBe("test@example.com")
})

// GOOD: arrange-act-assert pattern
test("updates user name", async () => {
  // Arrange
  const user = await createUser({ name: "Alice" })

  // Act
  const updated = await updateUser(user.id, { name: "Bob" })

  // Assert
  expect(updated.name).toBe("Bob")
})

// GOOD: isolated, fast tests
test("validates email format", () => {
  expect(isValidEmail("test@example.com")).toBe(true)
  expect(isValidEmail("invalid-email")).toBe(false)
})

// BAD: test interdependencies
test("creates user", async () => {
  userId = await createUser({ email: "test@example.com" })
})
test("updates user", async () => {
  // depends on previous test!
  await updateUser(userId, { name: "Bob" })
})
```

## Node.js/Backend Patterns

```typescript
// GOOD: middleware pattern
app.use((req, res, next) => {
  req.user = extractUser(req)
  next()
})

// GOOD: separation of concerns
const userRouter = Router()
userRouter.get("/:id", userController.getById)
userRouter.post("/", userController.create)

// GOOD: environment config via env vars
const config = {
  port: process.env.PORT || 3000,
  dbUrl: process.env.DATABASE_URL,
  apiKey: process.env.API_KEY
}

// BAD: hardcoded secrets
const API_KEY = "sk-proj-xxxxx" // never hardcode

// BAD: fat controllers
app.get("/users/:id", async (req, res) => {
  const user = await db.query(...)
  const posts = await db.query(...)
  const comments = await db.query(...)
  // ... 50 more lines
})
```

## Code Organization

```
src/
├── components/        # React components (if frontend)
│   ├── Header.tsx
│   └── UserCard.tsx
├── hooks/            # Custom React hooks
│   └── useUser.ts
├── pages/            # Route pages (if Next.js/SPA)
│   ├── users.tsx
│   └── posts.tsx
├── api/              # API routes or client
│   ├── client.ts
│   └── routes.ts
├── services/         # Business logic layer
│   ├── user.service.ts
│   └── post.service.ts
├── repositories/     # Data access layer
│   ├── user.repository.ts
│   └── post.repository.ts
├── types/            # Shared types
│   └── models.ts
├── utils/            # Utilities, helpers
│   ├── validation.ts
│   └── formatting.ts
├── constants.ts      # App constants
├── config.ts         # Configuration
└── index.ts          # Entry point
```

## Comments & Documentation

```typescript
// GOOD: why, not what (code is self-documenting)
// Retry with exponential backoff to handle transient failures
async function fetchWithRetry(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetch(url)
    } catch (error) {
      if (i === retries - 1) throw error
      await sleep(Math.pow(2, i) * 100) // 100ms, 200ms, 400ms
    }
  }
}

// GOOD: JSDoc for public APIs
/**
 * Fetches user by ID from the database.
 * @param id - User ID
 * @returns User object or null if not found
 * @throws ValidationError if ID format is invalid
 */
export async function getUserById(id: string): Promise<User | null> {
  return db.users.findUnique({ where: { id } })
}

// BAD: obvious comments
const name = "Alice" // set name to Alice
const count = 0 // initialize count to 0

// BAD: stale comments (more harm than help)
// TODO: optimize this query (done 2 years ago, comment never removed)
```

## Production Checklist

- [ ] No console.log in production code (use logging library)
- [ ] No hardcoded secrets or credentials
- [ ] All types properly defined (no any)
- [ ] Error handling covers edge cases
- [ ] Immutability enforced where appropriate
- [ ] Tests pass with >80% coverage
- [ ] Code is readable without explanation
- [ ] Performance-sensitive code profiled
- [ ] Security checks passed (if handling user data)
- [ ] Documentation reflects current code

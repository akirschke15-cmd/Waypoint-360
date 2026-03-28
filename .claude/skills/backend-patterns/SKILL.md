---
name: backend-patterns
description: Backend architecture with API structure, repository pattern, service layer, middleware, database optimization, N+1 prevention, caching, error handling, and auth/authorization patterns.
origin: ECC
version: 2.1
---

# Backend Patterns Skill

Production-grade backend architecture patterns for scalable, maintainable APIs.

## When to Activate

- Building API layer for new service
- Designing database schema and queries
- Refactoring legacy backend code
- Implementing authentication/authorization
- Optimizing database performance
- Handling complex business logic

## Layered Architecture

Three-layer pattern: routes -> services -> repositories.

```
HTTP Request
    |
    v
Routes (Express, FastAPI)
    - Parse request
    - Call service
    - Return response
    |
    v
Services (Business Logic)
    - Validate input
    - Orchestrate operations
    - Handle errors
    |
    v
Repositories (Data Access)
    - Query database
    - Handle transactions
    - Return entities
    |
    v
Database
```

## Routes (HTTP Layer)

Handle HTTP concerns, delegate to services.

```typescript
// routes/users.ts
import { Router } from 'express'
import { userService } from '../services/user.service'
import { authMiddleware } from '../middleware/auth'

const router = Router()

// Create user
router.post('/', async (req, res, next) => {
  try {
    const user = await userService.createUser(req.body)
    res.status(201).json({
      data: user,
      meta: { timestamp: new Date().toISOString() }
    })
  } catch (error) {
    next(error) // Pass to error middleware
  }
})

// Get user
router.get('/:id', authMiddleware, async (req, res, next) => {
  try {
    const user = await userService.getById(req.params.id)
    if (!user) {
      return res.status(404).json({
        error: 'User not found',
        code: 'USER_NOT_FOUND'
      })
    }
    res.json({ data: user })
  } catch (error) {
    next(error)
  }
})

// Update user
router.patch('/:id', authMiddleware, async (req, res, next) => {
  try {
    // Authorization: users can only update themselves
    if (req.user.id !== req.params.id && req.user.role !== 'admin') {
      return res.status(403).json({
        error: 'Forbidden',
        code: 'FORBIDDEN'
      })
    }

    const user = await userService.updateUser(req.params.id, req.body)
    res.json({ data: user })
  } catch (error) {
    next(error)
  }
})

export const usersRouter = router
```

## Services (Business Logic)

Orchestrate repositories and other services. Contain business rules.

```typescript
// services/user.service.ts
import { userRepository } from '../repositories/user.repository'
import { emailService } from './email.service'
import { ValidationError } from '../errors'

export const userService = {
  async createUser(input: CreateUserInput) {
    // Validate
    if (!input.email.includes('@')) {
      throw new ValidationError('Invalid email format')
    }

    // Check for duplicates
    const existing = await userRepository.findByEmail(input.email)
    if (existing) {
      throw new ValidationError('Email already registered')
    }

    // Create user
    const user = await userRepository.create({
      email: input.email,
      name: input.name,
      password_hash: await hashPassword(input.password)
    })

    // Side effects (after success)
    await emailService.sendWelcomeEmail(user.email, user.name)

    return user
  },

  async getById(id: string) {
    return userRepository.findById(id)
  },

  async updateUser(id: string, updates: Partial<User>) {
    // Validate updates
    if (updates.email) {
      const existing = await userRepository.findByEmail(updates.email)
      if (existing && existing.id !== id) {
        throw new ValidationError('Email already in use')
      }
    }

    return userRepository.update(id, updates)
  },

  async deleteUser(id: string) {
    // Soft delete for audit trail
    return userRepository.update(id, { deletedAt: new Date() })
  }
}
```

## Repositories (Data Access)

Abstract database operations. Return entities, not raw data.

```typescript
// repositories/user.repository.ts
import { db } from '../db'

export const userRepository = {
  async findById(id: string) {
    const record = await db.users.findUnique({ where: { id } })
    return record ? toUser(record) : null
  },

  async findByEmail(email: string) {
    const record = await db.users.findUnique({ where: { email } })
    return record ? toUser(record) : null
  },

  async create(data: CreateUserInput) {
    const record = await db.users.create({ data })
    return toUser(record)
  },

  async update(id: string, updates: Partial<CreateUserInput>) {
    const record = await db.users.update({
      where: { id },
      data: updates
    })
    return toUser(record)
  },

  async findMany(options: { limit: number; offset: number }) {
    const records = await db.users.findMany({
      take: options.limit,
      skip: options.offset,
      where: { deletedAt: null }
    })
    return records.map(toUser)
  }
}

// Domain model
interface User {
  id: string
  email: string
  name: string
  createdAt: Date
}

// Mapper: database record -> domain model
function toUser(record: any): User {
  return {
    id: record.id,
    email: record.email,
    name: record.name,
    createdAt: record.created_at
  }
}
```

## Database Optimization

### N+1 Query Prevention

BAD: N+1 queries (1 for users, N for each user's posts)
```typescript
const users = await db.users.findMany()
const userPosts = await Promise.all(
  users.map(user => db.posts.findMany({ where: { userId: user.id } }))
)
```

GOOD: Single query with join
```typescript
const users = await db.users.findMany({
  include: { posts: true }
})
```

GOOD: Separate, efficient queries
```typescript
const users = await db.users.findMany()
const userIds = users.map(u => u.id)
const postsPerUser = await db.posts.findMany({
  where: { userId: { in: userIds } }
})
```

### Query Optimization

```typescript
// GOOD: Select only needed fields
const users = await db.users.findMany({
  select: { id: true, name: true, email: true },
  // Not: select: '*'
})

// GOOD: Add indexes for common queries
// schema.prisma
model User {
  id String @id
  email String @unique
  createdAt DateTime @default(now())

  @@index([createdAt]) // Index for sorting/filtering by date
}

// GOOD: Pagination (avoid full table scans)
const users = await db.users.findMany({
  take: limit,
  skip: offset
})

// BAD: Loading all records
const allUsers = await db.users.findMany()
```

## Caching Strategy

### Cache Layers

```
Tier 1: In-Memory Cache (process)
  - Fastest, local only
  - Lost on restart
  - Good for: config, computed values

Tier 2: Redis (distributed)
  - Fast, shared across processes
  - TTL-based expiration
  - Good for: user data, session, expensive queries

Tier 3: Database
  - Slowest, source of truth
  - Persistent
```

Implementation:
```typescript
async function getUserWithCache(userId: string) {
  // Check in-memory cache
  if (memoryCache.has(userId)) {
    return memoryCache.get(userId)
  }

  // Check Redis
  const cachedUser = await redis.get(`user:${userId}`)
  if (cachedUser) {
    memoryCache.set(userId, cachedUser)
    return JSON.parse(cachedUser)
  }

  // Query database
  const user = await userRepository.findById(userId)
  if (user) {
    // Set Redis cache (expire in 1 hour)
    await redis.setex(`user:${userId}`, 3600, JSON.stringify(user))
    memoryCache.set(userId, user)
  }

  return user
}

// Invalidate on update
async function updateUser(userId: string, updates: any) {
  const user = await userRepository.update(userId, updates)
  memoryCache.delete(userId)
  await redis.del(`user:${userId}`)
  return user
}
```

## Error Handling

### Custom Error Classes

```typescript
// errors/index.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public code: string,
    public status: number = 500
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export class ValidationError extends AppError {
  constructor(message: string, public details?: any[]) {
    super(message, 'VALIDATION_ERROR', 400)
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404)
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401)
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Forbidden') {
    super(message, 'FORBIDDEN', 403)
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super(message, 'CONFLICT', 409)
  }
}
```

### Error Middleware

```typescript
// middleware/errorHandler.ts
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  // Log error
  logger.error('Error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method
  })

  // Handle known errors
  if (err instanceof AppError) {
    return res.status(err.status).json({
      error: err.message,
      code: err.code,
      ...(err instanceof ValidationError && { details: err.details })
    })
  }

  // Unknown error
  res.status(500).json({
    error: 'Internal server error',
    code: 'INTERNAL_ERROR'
  })
}

app.use(errorHandler)
```

## Middleware

### Request Logging

```typescript
app.use((req, res, next) => {
  const start = Date.now()

  res.on('finish', () => {
    const duration = Date.now() - start
    logger.info('Request:', {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: `${duration}ms`
    })
  })

  next()
})
```

### Authentication

```typescript
export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '')

  if (!token) {
    throw new UnauthorizedError('Missing token')
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!)
    req.user = decoded
    next()
  } catch (error) {
    throw new UnauthorizedError('Invalid token')
  }
}
```

### Authorization

```typescript
export function requireRole(roles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      throw new ForbiddenError('Insufficient permissions')
    }
    next()
  }
}

// Usage
router.delete('/:id', authMiddleware, requireRole(['admin']), deleteUserHandler)
```

## Database Transactions

```typescript
// Use transaction for multi-step operations
async function transferFunds(fromUserId: string, toUserId: string, amount: number) {
  return await db.$transaction(async (tx) => {
    // Deduct from sender
    const sender = await tx.users.update({
      where: { id: fromUserId },
      data: { balance: { decrement: amount } }
    })

    // Ensure sender has sufficient balance
    if (sender.balance < 0) {
      throw new ValidationError('Insufficient balance')
    }

    // Add to receiver
    await tx.users.update({
      where: { id: toUserId },
      data: { balance: { increment: amount } }
    })

    // Log transaction
    await tx.transactions.create({
      data: {
        fromUserId,
        toUserId,
        amount,
        timestamp: new Date()
      }
    })
  })
}
```

## Production Checklist

- [x] Error handling covers all paths
- [x] Validation on all inputs
- [x] Authentication on protected routes
- [x] Authorization checks (not just auth)
- [x] Database queries optimized (no N+1)
- [x] Indexes on common queries
- [x] Caching strategy for hot data
- [x] Proper HTTP status codes
- [x] Rate limiting enabled
- [x] Logging comprehensive but not verbose
- [x] Secrets in environment variables
- [x] Database transactions for critical operations
- [x] Error messages don't leak internals
- [x] Graceful shutdown handling

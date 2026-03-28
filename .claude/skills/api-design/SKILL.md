---
name: api-design
description: REST API design with resource naming, HTTP methods, status codes, pagination (offset vs cursor), filtering, versioning, rate limiting, and best practices for client-server communication.
origin: ECC
version: 2.0
---

# API Design Skill

RESTful API design patterns for scalable, intuitive, maintainable services.

## When to Activate

- Designing new API endpoints
- Planning API structure for new service
- Reviewing API design in code review
- Migrating APIs to new versions
- Documenting API standards for team
- Optimizing API response shapes

## Resource Naming

### Naming Conventions

```
# GOOD: plural, lowercase, kebab-case
GET /api/v1/users
GET /api/v1/user-profiles
GET /api/v1/order-items

# GOOD: nested for relationships
GET /api/v1/users/:userId/orders
GET /api/v1/orders/:orderId/items

# BAD: singular (inconsistent)
GET /api/v1/user

# BAD: verbs in path (should be HTTP method)
GET /api/v1/getUsers
POST /api/v1/createOrder

# BAD: camelCase (inconsistent with REST convention)
GET /api/v1/userProfiles
```

### Resource Hierarchy

```
/api/v1/organizations
  /:orgId
    /teams
      /:teamId
        /members
        /projects
          /:projectId
            /tasks
```

Limit nesting to 3 levels. Use query parameters for filtering instead:
```
# Good: 2-level nesting
GET /api/v1/organizations/:orgId/teams

# Better: Flatten, filter with query params
GET /api/v1/teams?organizationId=org-123
```

## HTTP Methods

### GET (Retrieve)

```typescript
// Fetch single resource
GET /api/v1/users/:id

// Fetch collection
GET /api/v1/users

// Fetch with query params
GET /api/v1/users?status=active&limit=20

// Response
200 OK
{
  "data": { "id": "123", "name": "Alice" },
  "meta": { "timestamp": "2026-03-20T12:00:00Z" }
}

// Not found
404 Not Found
{
  "error": "User not found",
  "code": "USER_NOT_FOUND"
}
```

### POST (Create)

```typescript
// Create resource
POST /api/v1/users
Content-Type: application/json

{
  "email": "alice@example.com",
  "name": "Alice"
}

// Response
201 Created
Location: /api/v1/users/123
{
  "data": { "id": "123", "email": "alice@example.com" },
  "meta": { "timestamp": "2026-03-20T12:00:00Z" }
}

// Validation error
400 Bad Request
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    { "field": "email", "message": "Invalid email format" }
  ]
}
```

### PATCH (Partial Update)

```typescript
// Update specific fields
PATCH /api/v1/users/:id
Content-Type: application/json

{
  "name": "Alice Updated"
}

// Response
200 OK
{
  "data": { "id": "123", "name": "Alice Updated" },
  "meta": { "timestamp": "2026-03-20T12:00:00Z" }
}
```

### PUT (Full Replacement)

```typescript
// Replace entire resource
PUT /api/v1/users/:id
Content-Type: application/json

{
  "email": "alice@example.com",
  "name": "Alice",
  "role": "admin"
}

// Response
200 OK
{
  "data": { "id": "123", "email": "alice@example.com", "name": "Alice", "role": "admin" }
}
```

Note: PATCH is more common than PUT in modern APIs.

### DELETE (Remove)

```typescript
// Delete resource
DELETE /api/v1/users/:id

// Response (204 No Content, best practice)
204 No Content

// Or with response body
200 OK
{
  "data": { "id": "123", "deleted": true },
  "meta": { "timestamp": "2026-03-20T12:00:00Z" }
}
```

## Status Codes

### Success Responses

```
200 OK              - GET, PATCH, PUT successful
201 Created         - POST successful, resource created
204 No Content      - DELETE successful, no response body
```

### Client Errors

```
400 Bad Request     - Validation failed, malformed request
401 Unauthorized    - Auth required, invalid/missing token
403 Forbidden       - Auth successful but lacks permission
404 Not Found       - Resource doesn't exist
409 Conflict        - Constraint violation (duplicate key, etc.)
422 Unprocessable   - Semantic error (can't process request)
429 Too Many        - Rate limit exceeded
```

### Server Errors

```
500 Internal Error  - Unexpected server error
503 Service         - Server temporarily unavailable
```

## Pagination

### Offset-Based (Simple, Best for Small Sets)

```typescript
GET /api/v1/users?offset=0&limit=20

Response:
{
  "data": [...],
  "meta": {
    "offset": 0,
    "limit": 20,
    "total": 150,
    "hasNext": true
  }
}
```

Use for:
- Small datasets (<1M records)
- Admin/internal tools
- Sorted collections

Avoid:
- Large datasets (performance degrades)
- Real-time data (records shifting between requests)

### Cursor-Based (Efficient for Large Sets)

```typescript
GET /api/v1/users?cursor=null&limit=20

Response:
{
  "data": [...],
  "meta": {
    "limit": 20,
    "nextCursor": "eyJpZCI6IjI1In0",  // base64 encoded
    "hasNext": true
  }
}

// Next page
GET /api/v1/users?cursor=eyJpZCI6IjI1In0&limit=20
```

Use for:
- Large datasets (>1M records)
- Real-time data
- Public APIs

Implementation:
```typescript
// Encode cursor
const cursor = Buffer.from(JSON.stringify({ id: lastId })).toString('base64')

// Decode cursor
const { id: lastId } = JSON.parse(Buffer.from(cursor, 'base64').toString())

// Query next page
const nextRecords = await db.users
  .where({ id: { gt: lastId } })
  .limit(limit + 1)
```

## Filtering & Searching

### Query Parameters

```typescript
// Filter by field
GET /api/v1/users?status=active&role=admin

// Search
GET /api/v1/users?search=alice

// Complex filters
GET /api/v1/orders?status=pending&minAmount=100&maxAmount=500

// Multiple values
GET /api/v1/users?tags=vip&tags=premium
```

### Search vs Filter

```typescript
// FILTER: exact match on field
GET /api/v1/users?status=active

// SEARCH: full-text search
GET /api/v1/users?search=alice
// Matches: name, email, bio, etc.

// COMBINATION
GET /api/v1/users?status=active&search=alice
```

## Sorting

```typescript
// Sort ascending
GET /api/v1/users?sort=name

// Sort descending
GET /api/v1/users?sort=-name

// Multiple sort keys
GET /api/v1/users?sort=status,-createdAt
```

Implement safely:
```typescript
// Only allow sorting by specific fields (whitelist)
const ALLOWED_SORT_FIELDS = ['name', 'createdAt', 'email']

function parseSort(sortParam: string) {
  const field = sortParam.replace(/^-/, '')
  const direction = sortParam.startsWith('-') ? 'desc' : 'asc'

  if (!ALLOWED_SORT_FIELDS.includes(field)) {
    throw new Error(`Cannot sort by ${field}`)
  }

  return { field, direction }
}
```

## Response Shape

### Success Response

```typescript
// Single resource
200 OK
{
  "data": {
    "id": "123",
    "name": "Alice",
    "email": "alice@example.com"
  },
  "meta": {
    "timestamp": "2026-03-20T12:00:00Z"
  }
}

// Collection
200 OK
{
  "data": [
    { "id": "1", "name": "Alice" },
    { "id": "2", "name": "Bob" }
  ],
  "meta": {
    "total": 150,
    "limit": 20,
    "offset": 0
  }
}
```

### Error Response

```typescript
// Validation error
400 Bad Request
{
  "error": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}

// Generic error
500 Internal Error
{
  "error": "An unexpected error occurred",
  "code": "INTERNAL_ERROR"
}
```

## Versioning

### URL Path Versioning (Recommended for REST)

```typescript
GET /api/v1/users
GET /api/v2/users  // Different response shape, new structure
```

Benefits:
- Clear in URL
- Easy to have multiple versions running
- Good for breaking changes

Drawbacks:
- More code duplication

### Header Versioning

```typescript
GET /api/users
Accept: application/vnd.api+json;version=1
```

Benefits:
- Cleaner URLs
- Single endpoint versioning

Drawbacks:
- Less obvious to API users
- Harder to deprecate versions

### Deprecation Timeline

```typescript
// Version 1: Current (supported)
GET /api/v1/users

// Version 2: New (transitional)
GET /api/v2/users

// Deprecation flow:
// - Announce v1 deprecation 3 months in advance
// - Require clients to migrate
// - Monitor v1 usage
// - Sunset v1 after grace period
```

## Rate Limiting

### Headers

```
X-RateLimit-Limit: 1000       # Max requests per hour
X-RateLimit-Remaining: 950    # Requests remaining
X-RateLimit-Reset: 1234567890 # Unix timestamp of reset
```

### Implementation

```typescript
// Per-IP rate limiting
const limiter = rateLimit({
  windowMs: 60 * 60 * 1000,  // 1 hour
  max: 1000,                  // 1000 requests
  keyGenerator: (req) => req.ip,
  message: 'Too many requests, please try again later'
})

app.use('/api/', limiter)

// Per-user rate limiting (stricter for expensive operations)
const searchLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 10,              // 10 requests per minute
  skip: (req) => req.user?.role === 'admin'
})

app.get('/api/search', searchLimiter, searchHandler)
```

## API Documentation

### OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0

paths:
  /api/v1/users:
    get:
      summary: List users
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive]
      responses:
        200:
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        email:
          type: string
```

## API Security

- [x] HTTPS only (enforce via headers)
- [x] Authentication required for sensitive endpoints
- [x] Authorization checked (user can only access own data)
- [x] Input validated (size, format, type)
- [x] SQL injection prevented (parameterized queries)
- [x] Rate limiting enabled
- [x] CORS configured for allowed origins
- [x] No sensitive data in URLs (use request body)
- [x] Error messages don't leak internals

## Common Mistakes

- Mixing verbs and nouns (GET /api/getUsers)
- Inconsistent naming (users vs user_profiles)
- No pagination on large collections
- Returning all fields always
- Breaking changes without versioning
- No error details (generic "Error" messages)
- Sending secrets in responses
- No rate limiting

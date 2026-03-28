# General Coding Style

## Core Principles

1. **Readability** - Code is read more than written. Optimize for clarity.
2. **No Magic Numbers** - Every constant deserves a named variable or enum
3. **Explicit Over Implicit** - Make intent clear; avoid clever shortcuts
4. **DRY** - Do not Repeat Yourself. Extract common patterns to shared functions
5. **Single Responsibility** - Each function/class does one thing well

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Constants | SCREAMING_SNAKE_CASE | MAX_RETRIES, API_URL |
| Variables/Functions | camelCase (JS/TS) snake_case (Python) | userName, user_name |
| Classes | PascalCase | UserService, DatabaseConnection |
| Private/Internal | Leading underscore | _internalMethod, __private |
| Booleans | is/has/should prefix | isValid, hasPermission, shouldRetry |

## Comments

- Write comments for WHY, not WHAT (code shows WHAT)
- Remove obvious comments: `count++` needs no comment
- Keep comments updated with code changes
- Use TODO for planned work, FIXME for known issues

## Function Complexity

- Max 50 lines per function
- If exceeding 50 lines, extract helper functions
- One concern per function
- Function name should describe what it does

## Error Handling

- Never silently fail
- Always handle edge cases explicitly
- Provide context in error messages
- Log errors with sufficient detail for debugging

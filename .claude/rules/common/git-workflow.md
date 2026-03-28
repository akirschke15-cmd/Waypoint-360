# Git Workflow

## Commit Standards

### Message Format

```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

### Type
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring (no behavior change)
- `test:` Test additions/modifications
- `docs:` Documentation changes
- `chore:` Dependencies, build config, etc.

### Subject Line
- Max 50 characters
- Imperative mood: "add feature", not "added feature"
- No period at end

### Body (optional)
- Max 72 characters per line
- Explain WHAT and WHY, not HOW
- Reference related issues: "Closes #123"

### Example

```
feat: Add user authentication flow

Implements JWT-based authentication with refresh token rotation.
Adds login, logout, and token refresh endpoints.

Closes #45
```

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation

## Pull Request Process

1. Create feature branch from main
2. Write code following style guide
3. All tests pass locally
4. No console.log/debug statements (unless necessary)
5. Create PR with clear description
6. Await code review
7. Merge only when approved
8. Delete feature branch after merge

## Before Pushing

```bash
git diff HEAD      # Review changes
npm/pytest test    # All tests pass
npm run typecheck  # Type checking clean
npm run lint       # No linting errors
```

## Rebase vs. Merge

- Prefer squash + merge for feature branches (keeps main clean)
- Use rebase for interactive history cleanup
- Never force push to main

# Development Workflow

## Local Development Setup

1. **Environment Variables**: Copy `.env.example` to `.env.local`
2. **Dependencies**: Run `npm install` or `pip install -r requirements.txt`
3. **Database**: Run migrations: `npm run migrate` or `python manage.py migrate`
4. **Dev Server**: Start with `npm run dev` or `python manage.py runserver`

## Before Writing Code

1. Create feature branch: `git checkout -b feature/description`
2. Read relevant documentation in `.claude/docs/`
3. Check `.claude/REQUIREMENT-CONFORMANCE-FRAMEWORK.md` for scope
4. Break feature into tasks if Large/XL scope

## During Development

### For New Features

1. Write test first (TDD): `test.ts` or `test.py`
2. Run test: should FAIL (RED)
3. Implement feature
4. Run test: should PASS (GREEN)
5. Refactor code quality
6. Verify integration points

### Code Quality Checks

```bash
# Before every commit
npm run lint        # Style/logic errors
npm run typecheck   # Type safety (TS/Python)
npm run test        # All tests pass
npm run build       # Build succeeds
```

## Integration Points to Verify

- [ ] Database schema matches models
- [ ] API endpoints match contracts
- [ ] Frontend calls correct endpoints
- [ ] Error handling on all paths
- [ ] Loading states visible to user
- [ ] No mock data in production code
- [ ] No hardcoded values (use env vars)

## Debugging

If something breaks:

1. Understand: Read error message carefully
2. Isolate: Create minimal reproducible case
3. Test Hypothesis: Verify your theory with test
4. Fix: Implement minimal fix
5. Verify: Test suite passes, integration works

## Performance Checklist

Before marking complete:
- [ ] No N+1 database queries
- [ ] Large lists paginated
- [ ] Images optimized and lazy-loaded
- [ ] Bundles analyzed (no unexpected large deps)
- [ ] API responses cached appropriately
- [ ] Database indexes exist for queries

## Accessibility Checklist

If UI component:
- [ ] ARIA labels on interactive elements
- [ ] Keyboard navigation works
- [ ] Color contrast meets WCAG AA
- [ ] Form fields properly labeled
- [ ] Alt text on images

## Mobile-First Development

- Design mobile first
- Test on real mobile devices
- Touch targets at least 44x44px
- Responsive breakpoints: 640px, 1024px, 1280px

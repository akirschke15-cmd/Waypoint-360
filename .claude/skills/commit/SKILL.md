---
name: commit
description: Standardized commit workflow with type checking, test verification, and conventional commit message format.
origin: Boiler 3.0
version: 1.0
---

# Commit Skill

Standardized commit workflow. Run this after completing a phase, feature, or batch of work.

## Steps

1. Run `npx tsc --noEmit` to verify no type errors. If errors exist, fix them before proceeding.
2. Run `npm run test -- --passWithNoTests 2>&1 | tail -5` to confirm no regressions.
3. Run `git status` and `git diff --stat` to review all staged and unstaged changes.
4. Group changes by area (auth, UI, API, infra, tests, config, etc).
5. Write a commit message following this format:

```
<type>(<scope>): <summary line under 72 chars>

- <area>: <what changed and why>
- <area>: <what changed and why>
- ...
```

Types: feat, fix, refactor, chore, test, docs, infra

6. Stage all relevant files with `git add -A` (or selectively if the user specifies).
7. Commit with the message.
8. Push to the current branch.
9. Confirm the push succeeded and report the commit hash.

## Rules

- Never commit with type errors or failing tests unless the user explicitly overrides.
- If there are 50+ changed files, group the summary by directory/area, not per-file.
- If the diff is enormous, ask the user if they want to split into multiple commits before proceeding.

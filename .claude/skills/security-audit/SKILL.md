---
name: security-audit
description: Parallel multi-agent security review with scope definition, dispatch, finding consolidation, and fix round execution for comprehensive code security audits.
origin: Boiler 3.0
version: 1.0
---

# Security Audit Skill

Parallel multi-agent security review producing actionable findings. Use for pre-deployment security sweeps, code review rounds, or periodic audits.

## Workflow

### 1. Scope
Identify the target directories and concern areas. Default split for a full-stack TypeScript app:

| Agent | Scope | Focus |
|-------|-------|-------|
| Agent 1 | Auth & session files | Credential handling, token expiry, session fixation, bcrypt config, tRPC context |
| Agent 2 | API routes & tRPC routers | Input validation, authorization checks, injection risks, rate limiting |
| Agent 3 | Database layer (Prisma) | Raw queries, N+1 patterns, missing indexes, data exposure in includes |
| Agent 4 | Client-side & config | XSS vectors, exposed secrets, CORS config, CSP headers, env var leakage |

### 2. Dispatch
Launch all agents in parallel using Task agents. Each agent:
- Reads only its scoped files
- Writes findings to `docs/security-audit-<area>.md`
- Uses severity levels: CRITICAL / HIGH / MEDIUM / LOW / INFO
- Each finding includes: file, line (approx), description, recommended fix

### 3. Consolidate
After all agents complete:
- Merge all findings into `docs/security-audit-full.md`
- Sort by severity (CRITICAL first)
- Deduplicate any cross-cutting findings
- Add a summary table at the top:

```
| Severity | Count |
|----------|-------|
| CRITICAL | X     |
| HIGH     | X     |
| MEDIUM   | X     |
| LOW      | X     |
```

### 4. Fix Round (if requested)
- Address CRITICAL and HIGH findings immediately
- Run typecheck and tests after each fix
- Update the audit doc to mark findings as RESOLVED with commit hash

## Rules

- Agents must not modify code during the audit phase. Read-only.
- Every finding needs a concrete file reference, not a vague "consider adding validation."
- If an agent finds nothing in its scope, it still writes a clean report confirming the review was done.
- Always check `.env`, `.env.local`, and any config files for leaked secrets.

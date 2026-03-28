---
name: strategic-compact
description: Manual context compaction at logical phase boundaries rather than arbitrary auto-compaction. Preserve continuity in complex projects. Capture state for session continuation.
origin: ECC
version: 1.2
---

# Strategic Compaction Skill

Context management via manual compaction at logical phase boundaries.

## When to Activate

- Approaching context limits
- Completing major project phases
- Before long pauses in work
- When handing off to another session
- After major architectural decisions
- Transitioning between problem domains

## Core Principle

Compact at logical boundaries, not arbitrary token limits. Preserve semantic continuity.

## Phase Boundaries

Work progresses through logical phases. Compact between them.

### Phase Boundaries by Project Type

**Web Application Development:**
1. Architecture & Planning -> Scaffold & Setup
2. Core API Build -> Frontend Build
3. Feature Development -> Testing & Hardening
4. Deployment Setup -> Production Release

**Data Processing Pipeline:**
1. Requirements & Schema -> ETL Build
2. Validation & Testing -> Optimization
3. Integration & Deployment -> Monitoring

**Infrastructure/DevOps:**
1. Architecture Review -> Terraform Scaffolding
2. Core Resources -> Monitoring & Logging
3. Deployment Automation -> Production Validation

## Compaction Structure

When compacting, create this artifact:

```markdown
# Context Compaction: [Project Name]
Date: YYYY-MM-DD
Phase Transition: [FROM] -> [TO]

## What Was Done
- Completed: [major accomplishment 1]
- Completed: [major accomplishment 2]
- Completed: [major accomplishment 3]

## Current State
- Files created: [list key files]
- Database schema: [summary]
- API endpoints: [list with methods]
- Frontend components: [list]
- Tests: [coverage %, passing count]

## Key Decisions Made
1. Architecture choice: [decision + rationale]
2. Technology selection: [decision + rationale]
3. Data model: [decision + rationale]

## Known Issues & Blockers
- Issue: [description]
  Status: [blocked/in progress]
  Impact: [low/medium/high]

## Next Steps (Prioritized)
1. [Task] - blocking [downstream task] - est. time
2. [Task] - nice to have - est. time
3. [Task] - can defer to v2 - est. time

## Code Location & Structure
```
src/
├── api/                    # API routes, handlers
├── db/                     # Database schema, migrations
├── components/             # React components
├── types/                  # TypeScript types
├── utils/                  # Utilities and helpers
```

## Active Instincts
- Instinct 1: [name] (confidence: X)
- Instinct 2: [name] (confidence: Y)

## Session Continuation
To continue this work:
1. Review "Current State" section above
2. Check "Known Issues" for context
3. Start with first item in "Next Steps"
4. Validate schema with: `npm run typecheck`
5. Run tests with: `npm test`

---
```

## Example Compaction

### Web App: Architecture -> Setup Phase

```markdown
# Context Compaction: ServicePro
Date: 2026-03-20
Phase Transition: Architecture & Planning -> Scaffold & Setup

## What Was Done
- Finalized tech stack: React 18 + Vite, Node.js + Express, SQLite (local) / Postgres (prod)
- Designed data model: users, services, bookings, reviews
- Planned API structure: 12 core endpoints across 4 resources
- Set up GitHub repo with CI/CD skeleton
- Created database schema with migration setup

## Current State
- Files created:
  - package.json (dependencies locked)
  - tsconfig.json (strict mode enabled)
  - .github/workflows/test.yml (basic CI)
  - prisma/schema.prisma (initial schema)
  - src/server.ts (Express bootstrap)
  - src/types/index.ts (core types)
  - README.md (setup instructions)

- Database schema ready:
  - users (id, email, password_hash, created_at)
  - services (id, name, category, base_price, created_at)
  - bookings (id, user_id, service_id, status, created_at)

- API endpoints designed but not implemented:
  - POST /api/auth/register
  - POST /api/auth/login
  - GET /api/services
  - POST /api/bookings
  - ... (8 more)

- Tests: None yet

## Key Decisions Made
1. React 18 + Vite: Fast dev experience, modern tooling
2. Express + Node: Lightweight, straightforward, team familiar
3. Prisma ORM: Type-safe, migration-first, SQL transparent
4. SQLite for local, Postgres for prod: Reduces friction for dev
5. Strict TypeScript: Catch errors early, better DX

## Known Issues & Blockers
- None at this stage (greenfield project)

## Next Steps (Prioritized)
1. Build auth API (register, login, JWT) - blocking all features - 4h
2. Build service listing API - blocking booking feature - 2h
3. Set up React scaffold, navigation - blocking UI build - 1h
4. Build booking form + API - core feature - 3h
5. Add E2E tests for auth flow - quality gate - 2h

## Code Location & Structure
```
src/
├── api/
│   ├── auth.ts         # Auth routes (TODO)
│   ├── services.ts     # Service listing (TODO)
│   └── bookings.ts     # Booking routes (TODO)
├── db/
│   ├── schema.prisma   # Finalized ✓
│   └── seed.ts         # TODO
├── types/
│   ├── index.ts        # Core types ✓
│   └── auth.ts         # Auth types (TODO)
├── utils/
│   ├── jwt.ts          # TODO
│   └── password.ts     # TODO
└── server.ts           # Bootstrap ✓
```

## Active Instincts
- API Response Normalization (confidence: 0.88)
- Error Handling Pattern (confidence: 0.85)
- Type Safety (confidence: 0.92)

## Session Continuation
To continue this work:
1. Review "Current State" and "Next Steps" above
2. Bootstrap Express app: `npm run dev`
3. Implement auth endpoints first (blocking other features)
4. Run `npm run migrate:dev` for schema setup
5. Then proceed to service listing API
```

## Compaction Triggers

Compact when:
- **Phase completion:** Architecture -> Implementation, Implementation -> Testing
- **Context approaching limit:** When approaching 70% of token budget
- **Long pause:** Work paused >1 day, or handing off to someone else
- **Major milestone:** Major feature complete, architectural decision made
- **Integration point:** Between frontend and backend work, before deployment

## What To Preserve

In compaction, prioritize:
1. **Current State**: Exact code structure, what's built, what's left
2. **Decisions**: Why choices were made (prevents rework)
3. **Known Issues**: What failed attempts existed
4. **Next Steps**: Exact priority order
5. **Instincts**: Project-specific patterns discovered
6. **File Paths**: Exact locations so next session knows where to look

## What To Discard

Remove from compaction:
- Verbose debug logs
- Intermediate attempts and failures
- Code snippets you're not using
- Full transcript of all reasoning
- Resolved blockers (keep only active ones)

## Anti-Pattern: Arbitrary Compaction

BAD: Compacting at arbitrary points
```
- Compacted at 50k tokens (mid-feature)
- Lost context on why architecture chosen
- Next session duplicates work
```

GOOD: Compacting at phase boundary
```
- Completed API scaffold and tests (Phase 1)
- Compacted with full state snapshot
- Next session starts React build with full context (Phase 2)
```

## Continuation After Compaction

When resuming after compaction:
1. Read compaction summary first
2. Verify "Current State" by spot-checking key files
3. Validate tests pass: `npm test`
4. Run build: `npm run build`
5. Check first item in "Next Steps"
6. Ask clarifying questions only if summary unclear

This ensures zero ramp-up time and semantic continuity across sessions.

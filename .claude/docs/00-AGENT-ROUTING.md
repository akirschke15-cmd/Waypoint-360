# Waypoint 360 - Agent Routing Map

## How This File Works

This maps every task in `00-TASK-QUEUE.md` to Boiler agents + skills.
When executing a task in Claude Code:

**Option A: Manual Invocation (Recommended)**
```
Use the {AGENT} agent to complete task {NUMBER}: {TITLE}
```

**Option B: Auto-Activation**
Task descriptions contain keywords that trigger auto-activation via `agent-rules.json`.

**Option C: Worktree Agents**
Each worktree gets a `.claude/` config that pins a specific agent set.

---

## Agent Assignment Table

### PHASE 0: Foundation (COMPLETE)

| Task | Title | Primary Agent | Secondary Agent | Skill | Phase |
|------|-------|--------------|----------------|-------|-------|
| 001 | Project scaffolding + Boiler 4.0 init | devops-engineer | planner | deployment-patterns | foundation |
| 002 | CLAUDE.md project brain | planner | technical-writer | strategic-compact | foundation |
| 003 | SQLAlchemy model definitions | python-expert | backend-engineer | python-patterns | foundation |
| 004 | FastAPI app + config + database init | backend-engineer | python-expert | backend-patterns | foundation |
| 005 | Seed data from Commercial Workshop PDF | backend-engineer | python-expert | seed-safety | foundation |

### PHASE 1: Backend API (COMPLETE)

| Task | Title | Primary Agent | Secondary Agent | Skill | Phase |
|------|-------|--------------|----------------|-------|-------|
| 006 | Auth router (stub JWT) | backend-engineer | security-reviewer | backend-patterns | core |
| 007 | Program router (overview + seed) | backend-engineer | python-expert | api-design | core |
| 008 | Workstreams router (CRUD + detail) | backend-engineer | python-expert | api-design | core |
| 009 | Gates router (list + timeline matrix) | backend-engineer | python-expert | api-design | core |
| 010 | Dependencies router (D3 graph + critical path) | backend-engineer | python-expert | api-design | core |
| 011 | AI router (5 stub endpoints) | backend-engineer | python-expert | api-design | core |

### PHASE 2: Frontend (COMPLETE)

| Task | Title | Primary Agent | Secondary Agent | Skill | Phase |
|------|-------|--------------|----------------|-------|-------|
| 012 | React + Vite + Tailwind scaffold | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 013 | TypeScript types matching backend API | typescript-expert | frontend-engineer | typescript-development | ui |
| 014 | API service (Axios) | frontend-engineer | typescript-expert | typescript-development | ui |
| 015 | Theme system (SWA + neutral) | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 016 | App layout + sidebar + routing | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 017 | CommandCenter dashboard | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 018 | GateTimeline matrix view | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 019 | DependencyGraph (D3 force-directed) | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 020 | WorkstreamCard detail view | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 021 | RiskHeatMap matrix view | frontend-engineer | typescript-expert | frontend-patterns | ui |
| 022 | WorkstreamForm create form | frontend-engineer | typescript-expert | frontend-patterns | ui |

### PHASE 3: LangGraph AI (NEXT)

| Task | Title | Primary Agent | Secondary Agent | Skill | Phase |
|------|-------|--------------|----------------|-------|-------|
| 023 | LangGraph StateGraph definition | python-expert | backend-engineer | python-patterns | ai |
| 024 | Intent Classifier node | python-expert | backend-engineer | python-patterns | ai |
| 025 | Scope Creep Detector node | python-expert | backend-engineer | python-patterns | ai |
| 026 | Dependency Analyzer node | python-expert | backend-engineer | python-patterns | ai |
| 027 | Gate Readiness Assessor node | python-expert | backend-engineer | python-patterns | ai |
| 028 | Risk Aggregator node | python-expert | backend-engineer | python-patterns | ai |
| 029 | Status Synthesizer node | python-expert | backend-engineer | python-patterns | ai |
| 030 | Response Formatter node | python-expert | backend-engineer | python-patterns | ai |
| 031 | Wire LangGraph to /ai endpoints | backend-engineer | python-expert | api-design | ai |
| 032 | Prompt validation + guardrails | security-reviewer | python-expert | security-audit | ai |
| 033 | LangGraph unit tests | python-expert | tdd-guide | python-testing | ai |

### PHASE 4: Hardening & Integrations (FUTURE)

| Task | Title | Primary Agent | Secondary Agent | Skill | Phase |
|------|-------|--------------|----------------|-------|-------|
| 034 | JWT auth hardening (real login flow) | backend-engineer | security-reviewer | security-audit | hardening |
| 035 | Alembic migration setup | backend-engineer | python-expert | python-patterns | hardening |
| 036 | PostgreSQL production config | devops-engineer | backend-engineer | deployment-patterns | hardening |
| 037 | Docker + docker-compose | devops-engineer | backend-engineer | deployment-patterns | hardening |
| 038 | Backend pytest suite | tdd-guide | python-expert | python-testing | hardening |
| 039 | Frontend Vitest + RTL suite | tdd-guide | typescript-expert | testing-best-practices | hardening |
| 040 | Playwright E2E tests | tdd-guide | frontend-engineer | e2e-testing | hardening |
| 041 | Confluence MCP endpoint stub | backend-engineer | python-expert | api-design | integration |
| 042 | Jira MCP endpoint stub | backend-engineer | python-expert | api-design | integration |
| 043 | Slack notification webhook | backend-engineer | python-expert | api-design | integration |
| 044 | OTel + CloudWatch integration | devops-engineer | backend-engineer | deployment-patterns | integration |
| 045 | Performance audit + optimization | performance-optimizer | backend-engineer | python-patterns | polish |
| 046 | Security audit | security-reviewer | backend-engineer | security-audit | polish |
| 047 | Documentation finalization | technical-writer | planner | coding-standards | polish |

---

## Worktree Strategy

| Worktree | Focus | Agents Pinned | Tasks |
|----------|-------|--------------|-------|
| main | Foundation + Config | devops-engineer, planner | 001-005 |
| api | Backend API | backend-engineer, python-expert | 006-011 |
| ui | Frontend React | frontend-engineer, typescript-expert | 012-022 |
| ai | LangGraph Pipeline | python-expert, backend-engineer | 023-033 |
| hardening | Tests + Deploy | tdd-guide, devops-engineer, security-reviewer | 034-047 |

---

## Agent Selection Guide

| When the task involves... | Use this agent |
|--------------------------|----------------|
| FastAPI routes, SQLAlchemy queries, Pydantic models | backend-engineer |
| React components, Tailwind, D3.js visualization | frontend-engineer |
| LangGraph nodes, Claude API, prompt engineering | python-expert |
| TypeScript types, Vite config, frontend build | typescript-expert |
| Docker, CI/CD, AWS deployment, OTel | devops-engineer |
| System design, architecture decisions | architect |
| pytest, Vitest, Playwright test suites | tdd-guide |
| JWT auth, RBAC, input validation, OWASP | security-reviewer |
| CLAUDE.md, API docs, README | technical-writer |
| Bug investigation, error tracing | debugger |
| Query optimization, bundle analysis | performance-optimizer |
| Sprint planning, task decomposition | planner |
| Code quality review, PR review | code-reviewer |

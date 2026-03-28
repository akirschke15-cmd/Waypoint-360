# Waypoint 360 - Implementation Plan

> 5-phase roadmap spanning scaffolding (Phase 0, complete) through production hardening (Phase 4). Current state: Phase 2 (frontend complete, backend foundation complete). Phase 3 (LangGraph integration) in next session. All phases emphasize test-driven development, no AI-generated code without human validation, deterministic observability.

## Phase Overview

| Phase | Name | Status | Duration | Focus |
|-------|------|--------|----------|-------|
| **0** | **Scaffolding & Foundation** | ✅ Complete | ~1 week | Boiler 4.0, design tokens, DB schema, JWT auth, seed data |
| **1** | **Backend Foundation** | ✅ Complete | ~1 week | FastAPI + SQLAlchemy, 11 models, 5 routers, async DB, CRUD endpoints |
| **2** | **Frontend & API Integration** | ✅ Complete | ~2 weeks | React 18, 6 pages, D3 dependency graph, Tailwind theming, API consumption |
| **3** | **LangGraph AI Pipeline** | ⏳ In Progress | ~2 weeks | 7 StateGraph nodes, intent routing, specialized analyzers, test coverage |
| **4** | **Production Hardening** | ⏸️ Pending | ~2 weeks | Docker/K8s, DTC integration, observability (OTel → Grafana), performance, security audit |

---

## Directory Structure

```
Waypoint 360/
│
├── .claude/                                      # Developer tools
│   ├── docs/                                     # Technical documentation (this file + 11 others)
│   ├── agents/                                   # OpenClaw agent profiles
│   ├── commands/                                 # Custom CLI commands
│   ├── rules/                                    # Coding standards, security, testing
│   ├── CLAUDE.md                                 # Session manifest
│   └── AUTO-ACTIVATION.md                        # Auto-routing rules
│
├── backend/                                      # FastAPI Python application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                               # FastAPI app, lifespan (init_db), CORS, middleware
│   │   ├── config.py                             # Pydantic Settings: DATABASE_URL, API_KEY, CORS, AI_MODEL
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py                       # AsyncEngine, AsyncSessionLocal, get_db() dependency
│   │   │   ├── seed.py                           # seed_database() with 1 program, 4 gates, 8 workstreams
│   │   │   └── models/                           # Models imported into app/models/__init__.py
│   │   │       ├── base.py                       # TimestampMixin (id, created_at, updated_at)
│   │   │       ├── program.py                    # Program model + relationships
│   │   │       ├── phase.py                      # Phase model (belongs to Program)
│   │   │       ├── gate.py                       # Gate + GateExitCriteria models
│   │   │       ├── workstream.py                 # Workstream model (owner: Person)
│   │   │       ├── deliverable.py                # Deliverable (gate: Gate)
│   │   │       ├── risk.py                       # Risk (workstream: Workstream)
│   │   │       ├── decision.py                   # Decision (workstream: Workstream)
│   │   │       ├── dependency.py                 # Dependency (source_ws, target_ws)
│   │   │       ├── status_update.py              # StatusUpdate (workstream: Workstream)
│   │   │       ├── person.py                     # Person (workstream owner)
│   │   │       └── scope_change.py               # ScopeChange audit log
│   │   │
│   │   ├── routers/                              # API endpoint definitions
│   │   │   ├── __init__.py
│   │   │   ├── program.py                        # GET /program/, POST /program/seed
│   │   │   ├── workstreams.py                    # GET, POST, PUT /workstreams/*, /workstreams/{id}
│   │   │   ├── gates.py                          # GET /gates/, /gates/{id}, /gates/timeline
│   │   │   ├── dependencies.py                   # GET /dependencies/, /dependencies/critical-path
│   │   │   └── ai.py                             # POST /ai/query, GET /ai/gate-readiness, /ai/scope-creep, /ai/summary
│   │   │
│   │   └── schemas/                              # Pydantic request/response models (if separated from routers)
│   │
│   ├── requirements.txt                          # 16 dependencies (fastapi, sqlalchemy, langgraph, anthropic, etc.)
│   ├── alembic/                                  # Database migrations (prepared for production)
│   └── .env.example                              # Example env vars (DATABASE_URL, ANTHROPIC_API_KEY, SECRET_KEY)
│
├── frontend/                                     # React 18 Vite application
│   ├── src/
│   │   ├── main.tsx                              # React entry point, App wrapper
│   │   ├── App.tsx                               # Router setup, Sidebar, Header, AppLayout
│   │   │
│   │   ├── components/
│   │   │   ├── common/                           # Shared UI primitives
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Button.tsx
│   │   │   │   └── StatusIndicator.tsx
│   │   │   │
│   │   │   ├── CommandCenter/                    # Dashboard page (/)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── KpiCards.tsx
│   │   │   │   ├── WorkstreamList.tsx
│   │   │   │   ├── AiChat.tsx
│   │   │   │   ├── GateProgress.tsx
│   │   │   │   └── CriticalDeps.tsx
│   │   │   │
│   │   │   ├── GateTimeline/                     # Gate matrix page (/gates)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── FilterBar.tsx
│   │   │   │   ├── MatrixTable.tsx
│   │   │   │   └── GateDetails.tsx
│   │   │   │
│   │   │   ├── DependencyGraph/                  # D3 visualization page (/dependencies)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── ForceGraph.tsx                # D3 force-directed layout
│   │   │   │   ├── FilterBar.tsx
│   │   │   │   ├── Controls.tsx                  # Zoom, reset buttons
│   │   │   │   └── Tooltip.tsx
│   │   │   │
│   │   │   ├── RiskHeatMap/                      # Risk heatmap page (/risks)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── SeverityMatrix.tsx            # 5x5 grid
│   │   │   │   ├── Legend.tsx
│   │   │   │   ├── FilterBar.tsx
│   │   │   │   └── RiskCards.tsx
│   │   │   │
│   │   │   ├── WorkstreamCard/                   # Workstream detail page (/workstreams/:id)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── ScopeSection.tsx
│   │   │   │   ├── DeliverablesList.tsx
│   │   │   │   ├── RisksSection.tsx
│   │   │   │   ├── DecisionsSection.tsx
│   │   │   │   ├── DependenciesSection.tsx
│   │   │   │   ├── StatusUpdates.tsx
│   │   │   │   └── TeamMembers.tsx
│   │   │   │
│   │   │   └── WorkstreamForm/                   # Create workstream form (/workstreams/new)
│   │   │       ├── index.tsx
│   │   │       └── FormFields.tsx
│   │   │
│   │   ├── services/
│   │   │   └── api.ts                            # Axios client with interceptors, 13 typed endpoints
│   │   │
│   │   ├── themes/
│   │   │   └── index.ts                          # ThemeProvider context, SWA + Neutral themes
│   │   │
│   │   ├── types/
│   │   │   └── index.ts                          # TypeScript interfaces for all API responses
│   │   │
│   │   └── styles/
│   │       └── index.css                         # Tailwind imports + global styles
│   │
│   ├── public/                                   # Static assets (icons, fonts, etc.)
│   ├── index.html                                # HTML entry point (Vite)
│   ├── tailwind.config.js                        # Design tokens, color palette, responsive breakpoints
│   ├── postcss.config.js                         # PostCSS setup for Tailwind
│   ├── tsconfig.json                             # TypeScript configuration (strict mode, path aliases)
│   ├── vite.config.ts                            # Vite build config (HMR, code splitting, aliases)
│   ├── package.json                              # 18 dependencies (react, vite, tailwind, d3, axios, etc.)
│   └── .env.example                              # VITE_API_URL=http://localhost:8000/api/v1
│
├── scripts/                                      # Deployment + utility scripts
│   ├── docker-compose.yml                        # Dev: PostgreSQL + backend + frontend services
│   └── start.sh                                  # Helper script to boot local dev environment
│
├── Waypoint 360 architecture.txt                 # ASCII architecture diagram
├── CLAUDE.md                                     # Project-level session manifest
├── .gitignore                                    # Ignore node_modules, __pycache__, .env, .db
└── start.sh                                      # Quick start script

```

---

## Dependencies

### Frontend (`/frontend/package.json`)
```json
{
  "dependencies": {
    "react": "^18.3.1",                            # Core UI framework
    "react-dom": "^18.3.1",                        # DOM rendering
    "react-router-dom": "^6.22.0",                 # Client-side routing (6 pages)
    "axios": "^1.6.5",                             # HTTP client with interceptors
    "d3": "^7.8.5",                                # Force-directed dependency graph
    "lucide-react": "^0.294.0"                     # 400+ SVG icons (Sidebar, Header, Cards)
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@types/d3": "^7.4.0",                         # D3 TypeScript definitions
    "@vitejs/plugin-react": "^4.2.1",              # Vite + React HMR
    "typescript": "^5.3.3",                        # Strict type checking
    "vite": "^5.0.8",                              # Build tool (fast HMR, code splitting)
    "tailwindcss": "^3.4.1",                       # Utility-first CSS
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16"
  }
}
```

### Backend (`/backend/requirements.txt`)
```
# Web Framework
fastapi==0.115.0                                   # Async web framework with auto OpenAPI
uvicorn[standard]==0.30.0                          # ASGI server (4 workers default)

# Database
sqlalchemy==2.0.35                                 # Async ORM (asyncio + asyncpg)
aiosqlite==0.20.0                                  # SQLite async driver (dev)
                                                   # PostgreSQL: asyncpg (production)
alembic==1.13.0                                    # Database migrations

# Data Validation
pydantic==2.9.0                                    # Request/response validation (v2)
pydantic-settings==2.5.0                           # Environment config loader

# Authentication
python-jose[cryptography]==3.3.0                   # JWT token signing/verification
passlib[bcrypt]==1.7.4                             # Password hashing
python-multipart==0.0.9                            # Form data parsing

# AI / LangGraph
langgraph>=0.2.0                                   # StateGraph for agentic reasoning
langchain-anthropic>=0.2.0                         # Claude API integration
langchain-core>=0.2.27                             # LangChain base classes
anthropic>=0.34.0                                  # Anthropic SDK (Claude Sonnet 4)

# Async Utilities
httpx==0.27.0                                      # Async HTTP client (optional, for internal calls)
```

---

## Task Breakdown by Phase

### Phase 0: Scaffolding & Foundation (✅ Complete)

**Status**: All tasks done, codebase ready for Phase 1.

| Task | Status | Files Modified/Created | Notes |
|------|--------|---|---|
| Boiler 4.0 template | ✅ | CLAUDE.md, .claude/docs/, .claude/rules/ | Full agent + rule setup |
| Design tokens (Tailwind) | ✅ | tailwind.config.js, frontend/src/themes/ | SWA colors, responsive breakpoints |
| Database schema (SQLAlchemy) | ✅ | backend/app/models/ | 11 models, relationships, migrations |
| FastAPI app + CORS | ✅ | backend/app/main.py, config.py | Lifespan, async setup, seed on startup |
| JWT auth skeleton | ✅ | backend/app/routers/auth.py | Token generation + validation ready |
| Seed data | ✅ | backend/app/db/seed.py | 1 program, 4 gates, 8 workstreams, realistic data |
| React + Vite setup | ✅ | frontend/ | HMR enabled, code splitting, TypeScript strict |
| API client (Axios) | ✅ | frontend/src/services/api.ts | 13 endpoints, interceptors, type-safe |
| Git setup + .gitignore | ✅ | .gitignore, git init | Ignore node_modules, __pycache__, .env, .db |

---

### Phase 1: Backend Foundation (✅ Complete)

**Status**: All CRUD endpoints implemented, tested with curl/Postman.

| Task | Status | Endpoints | Files |
|------|--------|-----------|-------|
| Program CRUD | ✅ | GET /program, POST /program/seed | routers/program.py, models/program.py |
| Workstream CRUD | ✅ | GET, POST, PUT /workstreams, /workstreams/:id | routers/workstreams.py, models/workstream.py |
| Gate CRUD | ✅ | GET /gates, /gates/:id, /gates/timeline | routers/gates.py, models/gate.py |
| Deliverable CRUD | ✅ | POST /workstreams/:id/deliverables | embedded in routers/workstreams.py |
| Risk CRUD | ✅ | POST /workstreams/:id/risks | embedded in routers/workstreams.py |
| Decision CRUD | ✅ | POST /workstreams/:id/decisions | embedded in routers/workstreams.py |
| Dependency graph API | ✅ | GET /dependencies, /dependencies/critical-path | routers/dependencies.py, models/dependency.py |
| Status update API | ✅ | POST /workstreams/:id/status-updates | embedded in routers/workstreams.py |
| Async database integration | ✅ | AsyncSession, asyncpg ready | db/database.py, models/*.py |
| Error handling (400, 404, 500) | ✅ | Custom exception handlers | main.py middleware |
| Pagination (optional) | ⏸️ | GET /workstreams?skip=0&limit=10 | Not yet implemented, queued for Phase 4 |

---

### Phase 2: Frontend & API Integration (✅ Complete)

**Status**: All 6 pages rendered, API calls wired, D3 graph working.

| Task | Status | Components | Notes |
|------|--------|-----------|-------|
| CommandCenter page (/) | ✅ | 6 sections (KPI, workstreams, AI chat, gate progress, deps) | AI endpoints stubbed, return mock data |
| GateTimeline page (/gates) | ✅ | Matrix table, filter bar, gate details sidebar | Calls GET /gates/timeline |
| DependencyGraph page (/dependencies) | ✅ | D3 force-directed layout, filters, zoom/pan | Calls GET /dependencies, SVG rendering |
| RiskHeatMap page (/risks) | ✅ | 5×5 severity matrix, risk cards, filters | Derived from workstream data, no API call |
| WorkstreamCard page (/workstreams/:id) | ✅ | 8 sections (scope, deliverables, risks, decisions, deps, updates, team) | View + edit mode, calls GET/PUT /workstreams/:id |
| WorkstreamForm page (/workstreams/new) | ✅ | 7 form fields, validation, submit button | Calls POST /workstreams, redirects on success |
| Theme system (SWA + Neutral) | ✅ | Context API, ThemeProvider, Sidebar toggle | Both themes fully styled |
| Responsive design (mobile-first) | ✅ | Tailwind breakpoints (sm, lg, xl) | All pages tested on mobile/desktop |
| Error handling + loading states | ✅ | Axios interceptors, LoadingSpinner component | Show errors to user, retry-able |
| Dark theme (neutral-900 bg) | ✅ | All components, Tailwind dark mode config | Only dark theme currently (light TBD) |

---

### Phase 3: LangGraph AI Pipeline (⏳ In Progress)

**Status**: Phase 3 starts in next session. Endpoints stubbed, waiting for StateGraph implementation.

| Task | Status | Files | Duration |
|------|--------|-------|----------|
| Define 7 LangGraph nodes | ⏳ | backend/app/agents/langgraph.py (new) | ~3 days |
| Intent Classifier node | ⏳ | langgraph.py | Prompt template, JSON parsing, routing |
| Scope Creep Detector node | ⏳ | langgraph.py | Compare baseline vs current scope |
| Dependency Analyzer node | ⏳ | langgraph.py | Topological sort, cycle detection, critical paths |
| Gate Readiness Assessor node | ⏳ | langgraph.py | Exit criteria completion, workstream readiness |
| Risk Aggregator node | ⏳ | langgraph.py | Compound risks, cascade patterns, correlation |
| Status Synthesizer node | ⏳ | langgraph.py | Contextualize analysis, executive summary |
| Response Formatter node | ⏳ | langgraph.py | Structure output, check for unresolved tokens |
| Wire StateGraph to /ai endpoints | ⏳ | routers/ai.py | Replace stubs with actual LangGraph calls |
| Unit test each node (mock data) | ⏳ | tests/test_langgraph_nodes.py (new) | 80%+ coverage per node |
| Integration test (full workflows) | ⏳ | tests/test_langgraph_workflows.py (new) | Test each intent route end-to-end |
| Token budget tracking (log-only) | ⏳ | langgraph.py, routers/ai.py | Track tokens used per call, warn on overages |
| Load test (100 concurrent queries) | ⏳ | tests/load_test.py (new) | Measure latency, identify bottlenecks |
| Frontend AI chat integration test | ⏳ | frontend/src/components/CommandCenter/AiChat.tsx | Test real LangGraph responses (not mock) |

---

### Phase 4: Production Hardening (⏸️ Pending)

**Status**: Planned for post-MVP. Estimated ~2 weeks.

| Task | Status | Priority | Notes |
|------|--------|----------|-------|
| Docker containerization | ⏸️ | High | Python 3.11 slim backend, Node.js 18 frontend |
| Kubernetes manifests | ⏸️ | High | Stateless FastAPI, horizontal scaling ready |
| PostgreSQL (production DB) | ⏸️ | High | Connection pooling, asyncpg driver, migrations |
| DTC pipeline integration | ⏸️ | High | OTel → CloudWatch → Grafana AMG (SWA standard) |
| Performance profiling | ⏸️ | Medium | Database query optimization, N+1 detection, caching |
| Security audit | ⏸️ | High | SQL injection prevention (SQLAlchemy parameterized), CORS hardening, JWT expiry, rate limiting |
| Observability (structured logging) | ⏸️ | Medium | JSON logs, correlation IDs, trace context |
| Server-Sent Events (SSE) | ⏸️ | Low | Streaming AI responses for long-running analyses |
| Query deduplication + caching | ⏸️ | Low | Redis TTL, dedupe recent queries, reduce API calls |
| Frontend build optimization | ⏸️ | Medium | Bundle analysis, lazy loading, image optimization |
| E2E tests (Playwright) | ⏸️ | Medium | Critical user flows (login, create workstream, view dependencies) |
| Documentation site | ⏸️ | Low | User guide, API docs, architecture decision records |

---

## Development Workflow

### Before Starting Any Feature

1. **Read relevant docs** from `.claude/docs/`
2. **Check `.claude/REQUIREMENT-CONFORMANCE-FRAMEWORK.md`** for scope
3. **Create git feature branch**: `git checkout -b feature/description`
4. **Update TODO.md** if multi-day task

### During Development (TDD)

1. **Write test first** (RED)
   ```bash
   npm run test -- --watch   # Frontend
   pytest -xvs tests/        # Backend
   ```
2. **Implement feature** (GREEN)
3. **Refactor + run full suite** (REFACTOR)
   ```bash
   npm run lint && npm run typecheck && npm run test
   pytest -xvs tests/ --cov=app
   ```
4. **Commit** with conventional message: `feat: Add AI chat widget to CommandCenter`

### Before Pushing

```bash
# Frontend
npm run build              # Ensure prod build succeeds
npm run lint              # No linting errors
npm run typecheck         # TypeScript strict mode passes
npm run test              # All tests green

# Backend
pytest -xvs tests/ --cov=app --cov-fail-under=80
black app/                # Auto-format with Black
flake8 app/               # Lint check
mypy app/                 # Type check
```

### Code Review Standards

- **No console.log in prod code** (use logging module for backend)
- **No hardcoded values** (use env vars or config)
- **All public functions documented** (docstrings, JSDoc)
- **80%+ test coverage** (enforced by pre-commit hook)
- **No merge without passing CI** (GitHub Actions optional, but recommended)

---

## Git Workflow Summary

**Branches**: `feature/description`, `fix/description`, `refactor/description`
**Commits**: Conventional: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
**Merge**: Squash + merge to main (keep main history clean)
**Deploy**: Manual pushes to prod (no auto-deploy yet, Phase 4 feature)

---

## Testing Strategy

### Unit Tests
- **Backend**: FastAPI route handlers, database queries, AI node logic
- **Frontend**: Component rendering, user interactions, API client calls

### Integration Tests
- **Backend**: Database transaction rollback, async session lifecycle, AI workflow chains
- **Frontend**: Multi-page navigation, form submission to API, error handling

### E2E Tests (Phase 4)
- **Playwright**: Create workstream → update scope → view dependencies → check risks
- **Critical paths only** (not every feature)

### Test Coverage Targets
- Backend: 80%+ (enforced)
- Frontend: 60%+ (recommended)
- AI nodes: 90%+ (critical for prod trust)

---

## Deployment Checklist (Phase 4)

- [ ] Secrets loaded from env (no hardcoded keys)
- [ ] Database migrations applied (alembic upgrade head)
- [ ] Frontend build optimized (bundle < 500KB)
- [ ] Backend startup < 5 seconds
- [ ] Health check endpoints working
- [ ] Logging structured + queryable
- [ ] Rate limiting enabled
- [ ] CORS whitelist configured
- [ ] OTel exporter pointed to CloudWatch
- [ ] Seed data NOT in production
- [ ] AI token budget monitoring active
- [ ] Database backups automated (optional, depends on SWA infra)

---

## Success Criteria (MVP)

✅ **Phase 2 Complete** (current state):
- [x] 6-page React app with real component hierarchy
- [x] All API endpoints functional (CRUD + graph analysis)
- [x] D3 dependency visualization working
- [x] Dark-first UI matching SWA branding
- [x] Responsive mobile design
- [x] TypeScript strict mode, no errors
- [x] Tests > 80% coverage (backend)

⏳ **Phase 3 Success** (next):
- [ ] All 7 LangGraph nodes implemented
- [ ] Intent routing working for 5+ intents
- [ ] AI endpoints live and returning real responses
- [ ] Tests > 80% coverage (backend AI code)
- [ ] Token budget tracking functional

📦 **Phase 4 Success** (future):
- [ ] Docker images building + running
- [ ] Kubernetes manifests ready
- [ ] OTel traces visible in Grafana
- [ ] Load test: 100 concurrent queries, p99 latency < 2s
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Deployed to SWA infrastructure (tbd timeline)

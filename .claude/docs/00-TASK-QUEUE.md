# Waypoint 360 - Task Queue

## How to Use This File

Each task is a single Claude Code session. Start fresh context per task.

**Per-task workflow:**
1. Read the task below
2. Read ONLY the docs/sections listed in `READ:`
3. Check `DEPENDS ON:` - verify those files exist
4. Build what's in `CREATE:` / `MODIFY:`
5. Run the `VALIDATE:` command
6. If clean, task is done. Move to next.

**Rules:**
- Never read all docs at once. Only read what the task says.
- Never modify files outside your `CREATE:` / `MODIFY:` list.
- If a task says "frozen" in a dependency, that file MUST NOT be edited.
- Each task targets <= 200 lines of new code. If you are writing more, stop and check.

**Parallelism:** Tasks with no shared dependencies can run in separate worktrees simultaneously.

---

## Dependency DAG

```
PHASE 0: Foundation
001 ──┬── 002
      ├── 003 ──── 004 ──── 005
      │
PHASE 1: Backend API
      ├── 006
      ├── 007
      ├── 008
      ├── 009
      ├── 010
      └── 011
           │
PHASE 2: Frontend
      ┌── 012 ──── 013 ──── 014 ──── 015 ──── 016
      │                                        │
      ├── 017 (depends: 007, 016)              │
      ├── 018 (depends: 009, 016)              │
      ├── 019 (depends: 010, 016)              │
      ├── 020 (depends: 008, 016)              │
      ├── 021 (depends: 008, 016)              │
      └── 022 (depends: 008, 016)              │
                                               │
PHASE 3: LangGraph AI                         │
      ┌── 023 ──── 024                         │
      ├── 025 (depends: 023)                   │
      ├── 026 (depends: 023)                   │
      ├── 027 (depends: 023)                   │
      ├── 028 (depends: 023)                   │
      ├── 029 (depends: 023)                   │
      ├── 030 (depends: 023)                   │
      ├── 031 (depends: 024-030, 011)          │
      ├── 032 (depends: 031)                   │
      └── 033 (depends: 024-030)               │
                                               │
PHASE 4: Hardening & Integrations              │
      ┌── 034 (depends: 006)                   │
      ├── 035 (depends: 003)                   │
      ├── 036 (depends: 004)                   │
      ├── 037 (depends: 004, 012)              │
      ├── 038 (depends: 006-011)               │
      ├── 039 (depends: 017-022)               │
      ├── 040 (depends: 038, 039)              │
      ├── 041 (depends: 004)                   │
      ├── 042 (depends: 004)                   │
      ├── 043 (depends: 004)                   │
      ├── 044 (depends: 004, 036)              │
      ├── 045 (depends: 031, 017-022)          │
      ├── 046 (depends: 034, 032)              │
      └── 047 (depends: ALL)                   │
```

---

## PHASE 0: Foundation

### Task 001 - Project Scaffolding + Boiler 4.0 Init
- **STATUS:** COMPLETE
- **READ:** `docs/01-ARCHITECTURE.md` (tech stack, directory structure), `docs/06-IMPLEMENTATION-PLAN.md` (Phase 0)
- **DEPENDS ON:** Nothing (first task)
- **CREATE:**
  - `backend/requirements.txt` with all Python dependencies
  - `backend/app/__init__.py`, `backend/app/config.py`
  - `frontend/package.json`, `frontend/tsconfig.json`, `frontend/vite.config.ts`
  - `frontend/tailwind.config.js`, `frontend/postcss.config.js`
  - `.env.example` with all environment variables
  - `start.sh` startup script
- **VALIDATE:** `cd backend && pip install -r requirements.txt && cd ../frontend && npm install`
- **FROZEN AFTER:** Directory structure, config files, `requirements.txt`, `package.json`

### Task 002 - CLAUDE.md Project Brain
- **STATUS:** COMPLETE
- **READ:** `docs/01-ARCHITECTURE.md` (full), `docs/06-IMPLEMENTATION-PLAN.md` (full)
- **DEPENDS ON:** 001
- **CREATE:**
  - `CLAUDE.md` with project overview, architecture, conventions, agent instructions
- **VALIDATE:** `cat CLAUDE.md | wc -l` (should be 100-300 lines)
- **FROZEN AFTER:** `CLAUDE.md`

### Task 003 - SQLAlchemy Model Definitions
- **STATUS:** COMPLETE
- **READ:** `docs/02-DATABASE-SCHEMA.md` (all models, enums, relationships)
- **DEPENDS ON:** 001
- **CREATE:**
  - `backend/app/models.py` - All 12 SQLAlchemy models + 16 enums
  - Program, Phase, Gate, ExitCriterion, Workstream, Deliverable, Risk, Decision, Dependency, StatusUpdate, User, AuditLog
- **VALIDATE:** `cd backend && python -c "from app.models import *; print('Models OK')"`
- **FROZEN AFTER:** Model class names, table names, primary key columns

### Task 004 - FastAPI App + Config + Database Init
- **STATUS:** COMPLETE
- **READ:** `docs/01-ARCHITECTURE.md` (backend section), `docs/03-API-SPECIFICATION.md` (app structure)
- **DEPENDS ON:** 001, 003
- **CREATE:**
  - `backend/app/main.py` - FastAPI app with CORS, lifespan, router mounting
  - `backend/app/database.py` - Async SQLAlchemy engine + session factory
  - `backend/app/dependencies.py` - Dependency injection (get_db, get_current_user)
- **VALIDATE:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 & sleep 3 && curl http://localhost:8000/api/v1/health`
- **FROZEN AFTER:** `main.py` app initialization, `database.py` engine config

### Task 005 - Seed Data from Commercial Workshop PDF
- **STATUS:** COMPLETE
- **READ:** `docs/02-DATABASE-SCHEMA.md` (enums, relationships), `docs/08-BUSINESS-RULES.md` (gate structure)
- **DEPENDS ON:** 003, 004
- **CREATE:**
  - `backend/app/seed.py` - Seed script with Waypoint program data
  - 11 workstreams, 6 gates (Align + 5 Incept), exit criteria, sample deliverables, risks, dependencies
- **VALIDATE:** `cd backend && python -c "from app.seed import seed_database; import asyncio; asyncio.run(seed_database())"`
- **FROZEN AFTER:** Seed data structure (can add data, not change schema)

---

## PHASE 1: Backend API

### Task 006 - Auth Router (Stub JWT)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (auth endpoints), `docs/07-SECURITY.md` (JWT section)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/routers/auth.py` - POST /auth/login, POST /auth/refresh, GET /auth/me
  - Stub JWT generation (hardcoded secret for dev, env var for prod)
  - Role-based middleware (admin, owner, viewer)
- **VALIDATE:** `curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin"}'`
- **FROZEN AFTER:** Auth middleware signature, JWT payload structure

### Task 007 - Program Router (Overview + Seed)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (program endpoints), `docs/02-DATABASE-SCHEMA.md` (Program, Phase models)
- **DEPENDS ON:** 004, 005
- **CREATE:**
  - `backend/app/routers/program.py` - GET /program/overview, GET /program/phases
  - Returns program metadata, phase summaries, gate counts, workstream counts
- **VALIDATE:** `curl http://localhost:8000/api/v1/program/overview`

### Task 008 - Workstreams Router (CRUD + Detail)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (workstream endpoints), `docs/02-DATABASE-SCHEMA.md` (Workstream + related models)
- **DEPENDS ON:** 004, 005
- **CREATE:**
  - `backend/app/routers/workstreams.py` - GET /workstreams, GET /workstreams/{id}, POST /workstreams
  - Detail includes deliverables, risks, decisions, dependencies, status updates
- **VALIDATE:** `curl http://localhost:8000/api/v1/workstreams && curl http://localhost:8000/api/v1/workstreams/1`

### Task 009 - Gates Router (List + Timeline Matrix)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (gate endpoints), `docs/02-DATABASE-SCHEMA.md` (Gate, ExitCriterion)
- **DEPENDS ON:** 004, 005
- **CREATE:**
  - `backend/app/routers/gates.py` - GET /gates, GET /gates/timeline, GET /gates/{id}
  - Timeline returns workstream x gate matrix with status per cell
- **VALIDATE:** `curl http://localhost:8000/api/v1/gates/timeline`

### Task 010 - Dependencies Router (D3 Graph + Critical Path)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (dependency endpoints), `docs/02-DATABASE-SCHEMA.md` (Dependency model)
- **DEPENDS ON:** 004, 005
- **CREATE:**
  - `backend/app/routers/dependencies.py` - GET /dependencies/graph, GET /dependencies/critical-path
  - Graph returns nodes + links for D3 force-directed layout
  - Critical path returns ordered list of blocking dependencies
- **VALIDATE:** `curl http://localhost:8000/api/v1/dependencies/graph`

### Task 011 - AI Router (5 Stub Endpoints)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (AI endpoints), `docs/05-AI-PIPELINE.md` (endpoint contracts)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/routers/ai.py` - POST /ai/query, POST /ai/scope-check, POST /ai/dependency-analysis, POST /ai/gate-readiness, POST /ai/risk-assessment
  - Stub responses with correct schema (will be wired to LangGraph in Phase 3)
- **VALIDATE:** `curl -X POST http://localhost:8000/api/v1/ai/query -H "Content-Type: application/json" -d '{"query":"test"}'`

---

## PHASE 2: Frontend

### Task 012 - React + Vite + Tailwind Scaffold
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (tech stack, project structure)
- **DEPENDS ON:** 001
- **CREATE:**
  - `frontend/src/main.tsx` - React 18 entry point
  - `frontend/src/App.tsx` - Root component with Router
  - `frontend/index.html` - HTML shell
  - `frontend/src/index.css` - Tailwind imports + SWA brand tokens
- **VALIDATE:** `cd frontend && npm run build`
- **FROZEN AFTER:** `main.tsx`, `index.html`, Tailwind config

### Task 013 - TypeScript Types Matching Backend API
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (all response schemas), `docs/04-FRONTEND-ARCHITECTURE.md` (type conventions)
- **DEPENDS ON:** 012
- **CREATE:**
  - `frontend/src/types/index.ts` - All TypeScript interfaces matching backend Pydantic models
  - Program, Phase, Gate, GateDetail, GateTimelineData, WorkstreamSummary, WorkstreamDetail, Deliverable, Risk, Decision, DependencyNode, DependencyLink, DependencyGraphData, CriticalPathData, AIQueryResponse
- **VALIDATE:** `cd frontend && npx tsc --noEmit`
- **FROZEN AFTER:** Type names, required fields (can add optional fields)

### Task 014 - API Service (Axios)
- **STATUS:** COMPLETE
- **READ:** `docs/03-API-SPECIFICATION.md` (all endpoints), `docs/04-FRONTEND-ARCHITECTURE.md` (API layer)
- **DEPENDS ON:** 012, 013
- **CREATE:**
  - `frontend/src/services/api.ts` - Axios instance + typed API methods for all endpoints
  - Base URL config, auth header injection, response interceptor
- **VALIDATE:** `cd frontend && npx tsc --noEmit`

### Task 015 - Theme System (SWA + Neutral)
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (design tokens, themes)
- **DEPENDS ON:** 012
- **CREATE:**
  - `frontend/src/themes/index.ts` - ThemeProvider context, SWA theme (blue #304CB2, gold #FFBF00, red #C8102E), neutral theme (zinc/indigo)
  - Theme toggle hook
- **VALIDATE:** `cd frontend && npx tsc --noEmit`

### Task 016 - App Layout + Sidebar + Routing
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (layout, navigation, routes)
- **DEPENDS ON:** 012, 015
- **CREATE:**
  - Update `frontend/src/App.tsx` - Layout shell with sidebar navigation, header, theme toggle
  - Routes: /, /gates, /dependencies, /workstreams/:id, /risks, /workstreams/new
  - Active link highlighting, responsive sidebar
- **VALIDATE:** `cd frontend && npm run build`

### Task 017 - CommandCenter Dashboard
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (CommandCenter section), `docs/03-API-SPECIFICATION.md` (program + workstream endpoints)
- **DEPENDS ON:** 007, 016
- **CREATE:**
  - `frontend/src/components/CommandCenter/index.tsx` - Program banner, 5 KPI cards, workstream sidebar with status badges, AI chat interface, gate progress bars, critical dependency summary
- **VALIDATE:** `cd frontend && npm run build`

### Task 018 - GateTimeline Matrix View
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (GateTimeline section), `docs/03-API-SPECIFICATION.md` (gates/timeline endpoint)
- **DEPENDS ON:** 009, 016
- **CREATE:**
  - `frontend/src/components/GateTimeline/index.tsx` - Workstream x Gate matrix, color-coded status cells, expandable gate detail cards with exit criteria progress
- **VALIDATE:** `cd frontend && npm run build`

### Task 019 - DependencyGraph (D3 Force-Directed)
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (DependencyGraph section), `docs/03-API-SPECIFICATION.md` (dependencies endpoints)
- **DEPENDS ON:** 010, 016
- **CREATE:**
  - `frontend/src/components/DependencyGraph/index.tsx` - D3 force-directed graph with SimNode/SimLink types, criticality filtering, zoom/drag behavior, arrow markers, hover tooltip
- **VALIDATE:** `cd frontend && npm run build`

### Task 020 - WorkstreamCard Detail View
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (WorkstreamCard section), `docs/03-API-SPECIFICATION.md` (workstreams/{id} endpoint)
- **DEPENDS ON:** 008, 016
- **CREATE:**
  - `frontend/src/components/WorkstreamCard/index.tsx` - Collapsible sections, scope parsing, deliverables by gate, risks with severity/likelihood, decisions, dependency links, status updates
- **VALIDATE:** `cd frontend && npm run build`

### Task 021 - RiskHeatMap Matrix View
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (RiskHeatMap section), `docs/03-API-SPECIFICATION.md` (workstream endpoints)
- **DEPENDS ON:** 008, 016
- **CREATE:**
  - `frontend/src/components/RiskHeatMap/index.tsx` - Severity x Likelihood heatmap matrix, risk aggregation from all workstreams, status filtering, risk register list
- **VALIDATE:** `cd frontend && npm run build`

### Task 022 - WorkstreamForm Create Form
- **STATUS:** COMPLETE
- **READ:** `docs/04-FRONTEND-ARCHITECTURE.md` (WorkstreamForm section), `docs/03-API-SPECIFICATION.md` (POST /workstreams)
- **DEPENDS ON:** 008, 016
- **CREATE:**
  - `frontend/src/components/WorkstreamForm/index.tsx` - Create workstream form with name, short_name, purpose, scope_in, scope_out fields, validation, submit to API
- **VALIDATE:** `cd frontend && npm run build`

---

## PHASE 3: LangGraph AI

### Task 023 - LangGraph StateGraph Definition
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (state schema, graph topology), `docs/01-ARCHITECTURE.md` (AI layer)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/ai/graph.py` - StateGraph definition with WaypointState TypedDict
  - `backend/app/ai/__init__.py`
  - State fields: query, intent, context, analysis, risks, recommendations, response, metadata
  - Graph topology: intent_classifier -> conditional routing -> analysis nodes -> response_formatter
- **VALIDATE:** `cd backend && python -c "from app.ai.graph import create_graph; g = create_graph(); print('Graph OK')"`

### Task 024 - Intent Classifier Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Intent Classifier section), `docs/09-PROMPT-TEMPLATES.md` (intent classification prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/intent_classifier.py` - Classifies user query into: status_check, scope_analysis, dependency_query, gate_readiness, risk_assessment, general_question
  - Uses Claude API with structured output (Pydantic model)
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.intent_classifier import classify_intent; print('Classifier OK')"`

### Task 025 - Scope Creep Detector Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Scope Creep Detector section), `docs/09-PROMPT-TEMPLATES.md` (scope analysis prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/scope_creep_detector.py` - Compares workstream scope_in/scope_out against deliverables and status updates
  - Flags items outside original scope, estimates scope drift percentage
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.scope_creep_detector import detect_scope_creep; print('Scope Detector OK')"`

### Task 026 - Dependency Analyzer Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Dependency Analyzer section), `docs/09-PROMPT-TEMPLATES.md` (dependency analysis prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/dependency_analyzer.py` - Builds dependency graph from DB, identifies circular dependencies, calculates critical path, flags at-risk chains
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.dependency_analyzer import analyze_dependencies; print('Dependency Analyzer OK')"`

### Task 027 - Gate Readiness Assessor Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Gate Readiness section), `docs/08-BUSINESS-RULES.md` (gate exit criteria), `docs/09-PROMPT-TEMPLATES.md` (gate readiness prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/gate_readiness.py` - Evaluates exit criteria completion per gate, calculates readiness score (0.0-1.0), identifies blockers, recommends remediation
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.gate_readiness import assess_gate_readiness; print('Gate Assessor OK')"`

### Task 028 - Risk Aggregator Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Risk Aggregator section), `docs/09-PROMPT-TEMPLATES.md` (risk assessment prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/risk_aggregator.py` - Aggregates risks across workstreams, calculates compound risk scores, identifies risk clusters, generates mitigation recommendations
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.risk_aggregator import aggregate_risks; print('Risk Aggregator OK')"`

### Task 029 - Status Synthesizer Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Status Synthesizer section), `docs/09-PROMPT-TEMPLATES.md` (status synthesis prompt)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/status_synthesizer.py` - Generates executive summary from workstream statuses, gate progress, risk posture, and dependency health
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.status_synthesizer import synthesize_status; print('Status Synthesizer OK')"`

### Task 030 - Response Formatter Node
- **STATUS:** PENDING
- **READ:** `docs/05-AI-PIPELINE.md` (Response Formatter section), `docs/09-PROMPT-TEMPLATES.md` (formatting templates)
- **DEPENDS ON:** 023
- **CREATE:**
  - `backend/app/ai/nodes/response_formatter.py` - Formats analysis results into structured response with summary, details, recommendations, confidence scores, source references
- **VALIDATE:** `cd backend && python -c "from app.ai.nodes.response_formatter import format_response; print('Formatter OK')"`

### Task 031 - Wire LangGraph to /ai Endpoints
- **STATUS:** PENDING
- **READ:** `docs/03-API-SPECIFICATION.md` (AI endpoints), `docs/05-AI-PIPELINE.md` (endpoint-to-node mapping)
- **DEPENDS ON:** 011, 024, 025, 026, 027, 028, 029, 030
- **MODIFY:**
  - `backend/app/routers/ai.py` - Replace stub responses with LangGraph graph invocations
  - Map each endpoint to appropriate graph entry point / intent override
- **VALIDATE:** `curl -X POST http://localhost:8000/api/v1/ai/query -H "Content-Type: application/json" -d '{"query":"What is the status of the Agent Design workstream?"}'`

### Task 032 - Prompt Validation + Guardrails
- **STATUS:** PENDING
- **READ:** `docs/07-SECURITY.md` (AI security section), `docs/09-PROMPT-TEMPLATES.md` (guardrails)
- **DEPENDS ON:** 031
- **CREATE:**
  - `backend/app/ai/guardrails.py` - Input sanitization, prompt injection detection, output validation, PII filtering, token budget enforcement
- **MODIFY:**
  - `backend/app/ai/graph.py` - Add guardrail nodes as pre/post processing steps
- **VALIDATE:** `cd backend && python -c "from app.ai.guardrails import validate_input, validate_output; print('Guardrails OK')"`

### Task 033 - LangGraph Unit Tests
- **STATUS:** PENDING
- **READ:** `docs/10-TESTING-STRATEGY.md` (AI testing section), `docs/05-AI-PIPELINE.md` (expected behaviors)
- **DEPENDS ON:** 024, 025, 026, 027, 028, 029, 030
- **CREATE:**
  - `backend/tests/test_ai/test_intent_classifier.py`
  - `backend/tests/test_ai/test_scope_creep_detector.py`
  - `backend/tests/test_ai/test_dependency_analyzer.py`
  - `backend/tests/test_ai/test_gate_readiness.py`
  - `backend/tests/test_ai/test_risk_aggregator.py`
  - `backend/tests/test_ai/test_status_synthesizer.py`
  - `backend/tests/test_ai/test_response_formatter.py`
- **VALIDATE:** `cd backend && pytest tests/test_ai/ -v`

---

## PHASE 4: Hardening & Integrations

### Task 034 - JWT Auth Hardening (Real Login Flow)
- **STATUS:** PENDING
- **READ:** `docs/07-SECURITY.md` (auth section), `docs/03-API-SPECIFICATION.md` (auth endpoints)
- **DEPENDS ON:** 006
- **MODIFY:**
  - `backend/app/routers/auth.py` - Replace stub JWT with bcrypt password hashing, refresh token rotation, token blacklisting, configurable expiry
- **CREATE:**
  - `backend/app/auth/jwt_handler.py` - JWT creation, validation, refresh logic
  - `backend/app/auth/password.py` - bcrypt hashing utilities
- **VALIDATE:** `cd backend && pytest tests/test_auth.py -v`

### Task 035 - Alembic Migration Setup
- **STATUS:** PENDING
- **READ:** `docs/02-DATABASE-SCHEMA.md` (all models), `docs/01-ARCHITECTURE.md` (database section)
- **DEPENDS ON:** 003
- **CREATE:**
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/versions/001_initial_schema.py` - Initial migration matching all models
- **VALIDATE:** `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head`

### Task 036 - PostgreSQL Production Config
- **STATUS:** PENDING
- **READ:** `docs/01-ARCHITECTURE.md` (database section), `docs/12-INTEGRATIONS.md` (infrastructure)
- **DEPENDS ON:** 004
- **MODIFY:**
  - `backend/app/config.py` - Add PostgreSQL connection string support, connection pooling config
  - `backend/app/database.py` - Async PostgreSQL engine with pool settings
- **VALIDATE:** `cd backend && python -c "from app.config import settings; print(settings.DATABASE_URL)"`

### Task 037 - Docker + Docker Compose
- **STATUS:** PENDING
- **READ:** `docs/01-ARCHITECTURE.md` (deployment section), `docs/12-INTEGRATIONS.md` (infrastructure)
- **DEPENDS ON:** 004, 012
- **CREATE:**
  - `backend/Dockerfile` - Python 3.11 multi-stage build
  - `frontend/Dockerfile` - Node 20 build + nginx serve
  - `docker-compose.yml` - Backend, frontend, PostgreSQL services
  - `docker-compose.dev.yml` - Dev overrides with hot reload
- **VALIDATE:** `docker-compose config && docker-compose build`

### Task 038 - Backend Pytest Suite
- **STATUS:** PENDING
- **READ:** `docs/10-TESTING-STRATEGY.md` (backend testing), `docs/03-API-SPECIFICATION.md` (all endpoints)
- **DEPENDS ON:** 006, 007, 008, 009, 010, 011
- **CREATE:**
  - `backend/tests/conftest.py` - Async test fixtures, test database, test client
  - `backend/tests/test_program.py`
  - `backend/tests/test_workstreams.py`
  - `backend/tests/test_gates.py`
  - `backend/tests/test_dependencies.py`
  - `backend/tests/test_auth.py`
- **VALIDATE:** `cd backend && pytest --cov=app --cov-report=term-missing`

### Task 039 - Frontend Vitest + RTL Suite
- **STATUS:** PENDING
- **READ:** `docs/10-TESTING-STRATEGY.md` (frontend testing), `docs/04-FRONTEND-ARCHITECTURE.md` (components)
- **DEPENDS ON:** 017, 018, 019, 020, 021, 022
- **CREATE:**
  - `frontend/src/test/setup.ts` - Vitest + RTL config
  - `frontend/src/components/CommandCenter/__tests__/index.test.tsx`
  - `frontend/src/components/GateTimeline/__tests__/index.test.tsx`
  - `frontend/src/components/DependencyGraph/__tests__/index.test.tsx`
  - `frontend/src/components/WorkstreamCard/__tests__/index.test.tsx`
  - `frontend/src/components/RiskHeatMap/__tests__/index.test.tsx`
- **VALIDATE:** `cd frontend && npx vitest run --coverage`

### Task 040 - Playwright E2E Tests
- **STATUS:** PENDING
- **READ:** `docs/10-TESTING-STRATEGY.md` (E2E testing), `docs/11-EDGE-CASES.md` (critical user flows)
- **DEPENDS ON:** 038, 039
- **CREATE:**
  - `e2e/playwright.config.ts`
  - `e2e/tests/dashboard.spec.ts` - Load dashboard, verify KPIs, click workstreams
  - `e2e/tests/gate-timeline.spec.ts` - Navigate to gates, expand details, verify matrix
  - `e2e/tests/dependency-graph.spec.ts` - Load graph, filter, zoom, hover tooltips
  - `e2e/tests/workstream-crud.spec.ts` - Create workstream, view detail, verify data
- **VALIDATE:** `npx playwright test`

### Task 041 - Confluence MCP Endpoint Stub
- **STATUS:** PENDING
- **READ:** `docs/12-INTEGRATIONS.md` (Confluence section), `docs/03-API-SPECIFICATION.md` (integration endpoints)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/integrations/confluence.py` - MCP-compatible endpoint for Confluence page sync
  - Stub: accepts page ID, returns mock structured content
- **VALIDATE:** `curl http://localhost:8000/api/v1/integrations/confluence/health`

### Task 042 - Jira MCP Endpoint Stub
- **STATUS:** PENDING
- **READ:** `docs/12-INTEGRATIONS.md` (Jira section), `docs/03-API-SPECIFICATION.md` (integration endpoints)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/integrations/jira.py` - MCP-compatible endpoint for Jira issue sync
  - Stub: accepts project key, returns mock issue list
- **VALIDATE:** `curl http://localhost:8000/api/v1/integrations/jira/health`

### Task 043 - Slack Notification Webhook
- **STATUS:** PENDING
- **READ:** `docs/12-INTEGRATIONS.md` (Slack section), `docs/08-BUSINESS-RULES.md` (notification events)
- **DEPENDS ON:** 004
- **CREATE:**
  - `backend/app/integrations/slack.py` - Webhook sender for gate status changes, risk threshold breaches, dependency blockers
  - Configurable webhook URL via env var
- **VALIDATE:** `cd backend && python -c "from app.integrations.slack import send_notification; print('Slack OK')"`

### Task 044 - OTel + CloudWatch Integration
- **STATUS:** PENDING
- **READ:** `docs/12-INTEGRATIONS.md` (observability section), `docs/01-ARCHITECTURE.md` (DTC pipeline)
- **DEPENDS ON:** 004, 036
- **CREATE:**
  - `backend/app/telemetry.py` - OpenTelemetry instrumentation for FastAPI + SQLAlchemy
  - `backend/app/telemetry_config.py` - OTel exporter config (stdout for dev, CloudWatch for prod)
  - Trace context propagation, custom spans for AI pipeline nodes
- **VALIDATE:** `cd backend && python -c "from app.telemetry import setup_telemetry; print('OTel OK')"`

### Task 045 - Performance Audit + Optimization
- **STATUS:** PENDING
- **READ:** `docs/01-ARCHITECTURE.md` (performance targets), `docs/03-API-SPECIFICATION.md` (all endpoints)
- **DEPENDS ON:** 031, 017, 018, 019, 020, 021, 022
- **MODIFY:**
  - Backend: Add database query optimization, connection pooling tuning, response caching
  - Frontend: Bundle analysis, code splitting, lazy loading, image optimization
- **VALIDATE:** `cd frontend && npx vite-bundle-visualizer && cd ../backend && python -m pytest tests/ --benchmark`

### Task 046 - Security Audit
- **STATUS:** PENDING
- **READ:** `docs/07-SECURITY.md` (full), `docs/03-API-SPECIFICATION.md` (all endpoints)
- **DEPENDS ON:** 034, 032
- **CREATE:**
  - `docs/SECURITY-AUDIT.md` - Findings, severity ratings, remediation status
- **MODIFY:**
  - Fix any identified vulnerabilities: SQL injection, XSS, CSRF, auth bypass, rate limiting gaps
- **VALIDATE:** `cd backend && bandit -r app/ && cd ../frontend && npx eslint --ext .tsx,.ts src/ --rule 'no-dangerouslySetInnerHTML: error'`

### Task 047 - Documentation Finalization
- **STATUS:** PENDING
- **READ:** All `docs/` files, `CLAUDE.md`
- **DEPENDS ON:** All previous tasks
- **CREATE:**
  - `README.md` - Project overview, setup instructions, architecture diagram, contribution guide
  - `docs/API.md` - OpenAPI-generated API documentation
  - `docs/DEPLOYMENT.md` - Production deployment runbook
- **MODIFY:**
  - Update all `docs/` files to reflect final implementation state
  - Verify all code examples in docs are accurate
- **VALIDATE:** `cat README.md && ls docs/`

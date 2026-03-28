# Waypoint 360 - System Architecture

> Tech stack: React 18 + FastAPI + SQLAlchemy 2.0 + LangGraph. Deployment: Docker containerized, PostgreSQL production, async throughout. Directory structure mirrors monorepo organization. RBAC: admin/owner/viewer roles with JWT auth. Multi-program support with deterministic gate framework and agentic AI analysis.

## Overview

Waypoint 360 is a real-time program management and observability platform for Southwest Airlines' Waypoint initiative. The system provides cross-workstream visibility, gate readiness assessment, dependency tracking, and AI-powered insights for complex, multi-workstream programs spanning ~10 weeks across 4 gates on a 2-week sprint cadence.

The platform combines deterministic project orchestration (gate framework, phase structure, deliverables) with agentic AI analysis (LangGraph StateGraph) to deliver both structured governance and intelligent decision support. It feeds observability telemetry into Southwest's DTC (Detect to Correct) pipeline via OpenTelemetry → CloudWatch → Grafana.

### Target Users

- **Leadership** (Tamara, Julie, Peter): Cross-workstream visibility dashboard, AI-assisted status aggregation, gate readiness assessment
- **Workstream Owners** (Chris, Stephanie, etc.): Detailed workstream status, risk/decision management, dependency tracking
- **Delivery Teams**: Deliverable progress, scope creep detection, decision deadlines
- **Architecture/Governance**: AI-powered impact assessment, regulatory/compliance tracking

## Technology Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite (ES2020 target, code splitting enabled)
- **Styling**: Tailwind CSS (utility-first, responsive design)
- **Visualization**: D3.js for dependency graph (force-directed), Chart.js for heatmaps
- **State Management**: React Query (server state), Context API (UI state)
- **HTTP Client**: Axios with custom interceptors for auth/error handling
- **Build**: Vite with HMR on localhost:5173, production bundle optimization
- **Package Manager**: npm

### Backend
- **Framework**: FastAPI 0.104+ (async by default, auto OpenAPI docs)
- **Runtime**: Python 3.11+ with asyncio
- **ORM**: SQLAlchemy 2.0 with async support (AsyncSession, asyncio event loop integration)
- **Data Validation**: Pydantic v2 for request/response schemas
- **Database Drivers**:
  - **Dev**: aiosqlite (async SQLite, single-file, /tmp/waypoint360.db)
  - **Prod**: asyncpg (async PostgreSQL, connection pooling)
- **AI Integration**: LangGraph 0.1+ with Claude API (claude-sonnet-4-20250514 or configurable)
- **Authentication**: JWT with HS256 signing, 8-hour token lifespan
- **Async Concurrency**: uvicorn workers (default 4, configurable)

### Database

**Development**: SQLite with aiosqlite
- Single-file database at `/tmp/waypoint360.db` (via DATABASE_URL env var)
- Auto-initialized on startup via `init_db()` in lifespan context
- Full transaction support with rollback on exception

**Production**: PostgreSQL with asyncpg
- Connection pooling: pool_size=20, max_overflow=0, timeout=30s
- Async prepared statements for query performance
- ACID compliance, supports distributed transactions
- Parameterized queries (no SQL injection risk)

**Schema**:
- SQLAlchemy ORM with declarative base (DeclarativeBase)
- TimestampMixin: every model has id (PK), created_at, updated_at
- Relationships: cascade delete-orphan for hierarchies (Program → Phases → Gates)
- Foreign key constraints enforced at database level

### Infrastructure

**Containerization**:
- Backend: Python 3.11 slim + FastAPI + gunicorn worker class (uvicorn)
- Frontend: Node.js 18 + nginx for static serving
- Orchestration: Docker Compose (dev), Kubernetes (prod-ready)

**Environment Configuration**:
- `.env` files with Pydantic Settings for type-safe config
- Required vars: DATABASE_URL, ANTHROPIC_API_KEY, SECRET_KEY
- Optional vars: OTEL_EXPORTER_OTLP_ENDPOINT, ALLOWED_ORIGINS, AI_MODEL

**Observability**:
- OpenTelemetry (OTel) tracing prepared for CloudWatch export
- Structured logging with Python logging module
- Metrics: Prometheus-compatible format (prepared for AMP)
- DTC pipeline integration: OTel → OTel Collector → CloudWatch → Grafana AMG

**Security**:
- CORS middleware with configurable allowed_origins
- JWT bearer token validation on protected routes
- Secrets never in code (loaded from environment)
- Parameterized SQL queries (SQLAlchemy handles)
- Input validation with Pydantic v2

**Scaling**:
- Stateless API design: JWT tokens carry all needed claims, no server sessions
- Horizontal scalability: load balancer routes to multiple FastAPI instances
- Async I/O: all database access is async, 100s of concurrent requests/worker
- Connection pooling: SQLAlchemy AsyncEngine manages database connections

## Directory Structure

```
Waypoint 360/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app, lifespan (init_db), CORS middleware
│   │   ├── config.py                    # Settings: DATABASE_URL, API_KEY, CORS, AI_MODEL
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py              # AsyncEngine, AsyncSessionLocal, get_db() dependency
│   │   │   └── seed.py                  # seed_waypoint_data() from Commercial Workshop PDF
│   │   ├── models/
│   │   │   ├── __init__.py              # __all__ export for easy imports
│   │   │   ├── base.py                  # DeclarativeBase, TimestampMixin (id, created_at, updated_at)
│   │   │   ├── program.py               # Program, ProgramStatus (planning/active/on_hold/complete)
│   │   │   ├── phase.py                 # Phase (name, start_week, end_week, goal, key_activities, exit_criteria)
│   │   │   ├── gate.py                  # Gate, GateStatus, GateExitCriteria, CriteriaStatus
│   │   │   ├── workstream.py            # Workstream, WorkstreamStatus (baseline_scope for creep detection)
│   │   │   ├── person.py                # Person, UserRole (admin/owner/viewer), password hashing
│   │   │   ├── deliverable.py           # Deliverable, DeliverableStatus, assignee link
│   │   │   ├── risk.py                  # Risk, Severity, Likelihood, RiskStatus, category
│   │   │   ├── decision.py              # Decision, DecisionStatus, decision_maker, due_date
│   │   │   ├── dependency.py            # Dependency, DependencyType, DependencyStatus, Criticality
│   │   │   ├── status_update.py         # StatusUpdate, StatusColor (green/yellow/red)
│   │   │   └── scope_change.py          # ScopeChange, ChangeType, FlaggedBy (user/ai)
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── auth.py                  # GET /me, POST /login (stub, JWT implementation pending)
│   │       ├── program.py               # GET / (full overview), POST /seed (trigger seeding)
│   │       ├── workstreams.py           # GET /, GET /{id}, PUT /{id} (RBAC check on PUT)
│   │       ├── gates.py                 # GET /, GET /timeline (matrix), GET /{id}
│   │       ├── dependencies.py          # GET / (D3 format), GET /critical-path
│   │       └── ai.py                    # POST /query, GET /gate-readiness/{id}, GET /scope-creep, GET /risks/correlated, GET /summary
│   ├── tests/
│   │   ├── conftest.py                  # pytest fixtures: async_client, async_session
│   │   ├── unit/
│   │   │   ├── test_models.py           # Relationship validation, status transitions
│   │   │   └── test_enums.py            # Enum membership tests
│   │   ├── integration/
│   │   │   ├── test_routers.py          # Endpoint tests with in-memory SQLite
│   │   │   └── test_auth.py             # JWT validation, RBAC enforcement
│   │   └── e2e/
│   │       └── test_workflows.py        # Full seed → query → update → export flows
│   ├── .env.example                     # Template: DATABASE_URL, ANTHROPIC_API_KEY, SECRET_KEY
│   ├── .env                             # (gitignored) Runtime configuration
│   ├── requirements.txt                 # Python dependencies (fastapi, sqlalchemy, pydantic, etc.)
│   ├── Dockerfile                       # Multi-stage: python:3.11-slim → gunicorn app
│   ├── docker-compose.yml               # Dev: backend + PostgreSQL + frontend
│   └── pyproject.toml                   # Project metadata, tool config (black, isort, pytest)

├── frontend/
│   ├── src/
│   │   ├── main.tsx                     # React root, ReactDOM.createRoot, Provider hierarchy
│   │   ├── index.css                    # Tailwind directives (@apply, @layer)
│   │   ├── types/
│   │   │   ├── index.ts                 # TypeScript interfaces mirroring API contracts
│   │   │   ├── models.ts                # Program, Phase, Gate, Workstream, etc.
│   │   │   ├── api.ts                   # Request/response types per router
│   │   │   └── ui.ts                    # Component prop types
│   │   ├── api/
│   │   │   ├── client.ts                # Axios instance, base URL, interceptors
│   │   │   ├── auth.ts                  # login, logout, getProfile
│   │   │   ├── program.ts               # getProgram, seedProgram
│   │   │   ├── workstreams.ts           # listWorkstreams, getWorkstream, updateWorkstream
│   │   │   ├── gates.ts                 # listGates, getGateTimeline, getGate
│   │   │   ├── dependencies.ts          # listDependencies, getCriticalPath
│   │   │   └── ai.ts                    # query, gateReadiness, scopeCreep, correlatedRisks, summary
│   │   ├── hooks/
│   │   │   ├── useAuth.ts               # useAuthContext, useLogin, useLogout
│   │   │   ├── useProgram.ts            # useQuery for GET /program
│   │   │   ├── useWorkstreams.ts        # useQuery for list/detail, useMutation for updates
│   │   │   ├── useGates.ts              # useQuery for gates, timeline
│   │   │   ├── useDependencies.ts       # useQuery for graph data
│   │   │   └── useAI.ts                 # useMutation for /query, useQuery for assessments
│   │   ├── context/
│   │   │   ├── AuthContext.tsx          # User, token, role (admin/owner/viewer)
│   │   │   └── ProgramContext.tsx       # Selected program, active gate, workstream filters
│   │   ├── components/
│   │   │   ├── CommandCenter.tsx        # Dashboard: banner, KPI cards, workstream list, AI chat, gate progress
│   │   │   ├── GateTimeline.tsx         # Matrix: rows=workstreams, cols=gates, expandable exit criteria
│   │   │   ├── DependencyGraph.tsx      # D3 force-directed graph, criticality colors, zoom/pan
│   │   │   ├── WorkstreamCard.tsx       # Detail: scope_in/out, deliverables, risks, decisions, deps
│   │   │   ├── WorkstreamForm.tsx       # Create/edit workstream with validation
│   │   │   ├── RiskHeatMap.tsx          # Severity x Likelihood matrix, drill-down to risk register
│   │   │   ├── DecisionTable.tsx        # List decisions by status, due date, decision maker
│   │   │   ├── StatusUpdateList.tsx     # Recent updates with color (green/yellow/red), timestamps
│   │   │   ├── AIChat.tsx               # Query input, loading state, response display with recommendations
│   │   │   ├── GateExitCriteriaModal.tsx # Expandable modal showing per-gate criteria + status
│   │   │   └── [other components]/     # Modular, reusable UI components
│   │   ├── layouts/
│   │   │   └── MainLayout.tsx           # Sidebar nav (program/gates/workstreams), header, main content
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx            # CommandCenter + KPIs
│   │   │   ├── GatesPage.tsx            # GateTimeline + detail view
│   │   │   ├── WorkstreamPage.tsx       # WorkstreamCard + form
│   │   │   ├── DependenciesPage.tsx     # DependencyGraph + critical path
│   │   │   └── [other pages]/          # Route-per-view pattern
│   │   └── App.tsx                      # Router setup (React Router v6), theme provider
│   ├── index.html                       # Entry point: <div id="root"></div>
│   ├── vite.config.ts                   # Vite: proxy to http://localhost:8000, React plugin, TS config
│   ├── tsconfig.json                    # Strict mode, ES2020 target, path aliases
│   ├── tailwind.config.ts               # Theme: colors, spacing, dark mode (optional)
│   ├── postcss.config.cjs               # Tailwind + autoprefixer
│   ├── package.json                     # Dependencies, scripts (dev, build, preview, test, lint)
│   ├── .env.example                     # VITE_API_URL, VITE_ENVIRONMENT
│   ├── .env                             # (gitignored) Runtime env vars
│   └── public/                          # Static assets (favicon, etc.)

├── docker-compose.yml                   # Services: backend, frontend, postgres, pgadmin (optional)
├── .gitignore                           # .env, node_modules, dist, venv, __pycache__, *.db
└── README.md                            # Setup, run, test, deploy instructions
```

## Data Flow

### Request Lifecycle (Frontend → Backend → DB → Response)

```
User Action (e.g., click "Update Workstream Status")
    ↓
React Component Handler
    ↓
React Query useMutation (or useQuery)
    ↓
Axios HTTP request (PUT /api/v1/workstreams/42)
    ↓
Vite proxy: http://localhost:8000/api/v1/workstreams/42
    ↓
FastAPI Router (@router.put("/{workstream_id}"))
    ↓
Dependency Injection: get_db(AsyncSession), verify_token(JWT claims)
    ↓
Pydantic v2 request validation
    ↓
Business Logic: auth check (claims["user_id"] == workstream.owner_id or claims["role"] == "admin")
    ↓
SQLAlchemy async query with eager loading (selectinload)
    ↓
    update Model fields
    ↓
    await db.commit()
    ↓
aiosqlite (dev) / asyncpg (prod) → SQL execution
    ↓
Database (SQLite / PostgreSQL)
    ↓
Transaction commit/rollback
    ↓
Response serialization (Model → dict → JSON)
    ↓
HTTP 200 OK with JSON body
    ↓
Axios response interceptor
    ↓
React Query cache update (automatic)
    ↓
Component re-render with new data
    ↓
UI updated on screen
```

### Async Execution Model

All I/O is async. FastAPI's async context allows uvicorn workers to handle concurrent requests:

```python
# Example: GET endpoint with eager loading
@router.get("/{workstream_id}")
async def get_workstream(workstream_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Workstream)
        .where(Workstream.id == workstream_id)
        .options(
            selectinload(Workstream.owner),
            selectinload(Workstream.deliverables).selectinload(Deliverable.gate),
            selectinload(Workstream.risks),
            selectinload(Workstream.decisions),
            selectinload(Workstream.outbound_dependencies).selectinload(Dependency.target_workstream)
        )
    )
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(status_code=404, detail="Workstream not found")

    # Response automatically serialized to JSON by FastAPI
    return {
        "id": w.id,
        "name": w.name,
        "deliverables": [{"id": d.id, "name": d.name, ...} for d in w.deliverables],
        # ... full response
    }
```

### AI / LangGraph Pipeline (Planned for v2)

LangGraph StateGraph with intent-based routing to specialized subgraphs:

```
POST /api/v1/ai/query { "query": "Is Gate 1 ready to proceed?" }
    ↓
Intent Classification Node
    ├── Extract intent: gate_readiness | scope_creep | risk_correlation | summary
    ├── Route to domain-specific subgraph
    ↓
[Gate Readiness Subgraph]
    ├── Load gate 1 + exit_criteria
    ├── Query all workstreams' deliverables for gate 1
    ├── Per-workstream readiness evaluation (LLM-as-judge)
    │   └── "Are deliverables complete? Are dependencies resolved? Confidence?"
    ├── Aggregate confidence scores
    ├── Identify blockers
    ├── Generate recommendations
    ↓
LLM Node (Claude Sonnet 4)
    └── "Gate 1 is 87% ready. Blockers: Platform team awaiting API specs. Recommend: escalate to Chris."
    ↓
Response: { gate_id: 1, confidence: 0.87, blockers: [...], recommendations: [...] }
    ↓
OTel span generation (prepared for CloudWatch export)
    ↓
HTTP 200 JSON response → Frontend
```

Model: `claude-sonnet-4-20250514` (configurable via `AI_MODEL` env var)
API Key: `ANTHROPIC_API_KEY` from environment
Determinism: StateGraph ensures deterministic node execution order
Mocking: Seed data allows offline testing without LangGraph calls

## Authentication & Authorization (RBAC)

### JWT Model

- **Issuer**: FastAPI `POST /api/v1/auth/login`
- **Token Format**: JWT (JSON Web Token)
- **Signing Algorithm**: HS256 with `SECRET_KEY`
- **Payload Fields**: `{"sub": user_id, "role": "admin|owner|viewer", "exp": timestamp, "iat": timestamp}`
- **Duration**: 8 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Transport**: HTTP `Authorization: Bearer <token>` header
- **Storage (Frontend)**: localStorage (with CSRF protection on sensitive mutations)
- **Refresh**: (Prepared for v2: refresh token rotation)

### Role-Based Access Control

| Role | Permissions | Scope |
|------|-------------|-------|
| **admin** | Create/read/update/delete all resources. Manage users. Change program status. | Organization-wide |
| **owner** | Create/read/update own workstream. Read other workstreams. Make decisions. Close risks. | Workstream-scoped |
| **viewer** | Read all resources. View dashboards. Export reports. Cannot create/edit. | Read-only |

### Validation Flow

```python
# 1. Token validation at router layer
async def verify_token(token: str = Header(...)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
        role: str = payload.get("role")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 2. RBAC check in endpoint
@router.put("/{workstream_id}")
async def update_workstream(
    workstream_id: int,
    data: dict,
    claims: dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workstream).where(Workstream.id == workstream_id))
    w = result.scalar_one_or_none()

    # Owner can update own workstream, admin can update any
    if claims["role"] not in ("admin",) and claims["user_id"] != w.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this workstream")

    # ... perform update
```

## 1P Telemetry & Observability Integration

Waypoint 360 feeds into Southwest Airlines' DTC (Detect to Correct) observability pipeline for unified observability of the Waypoint program.

### Architecture Alignment

**1P Agent Execution Path**:
```
LangGraph Nodes (deterministic orchestration)
    ↓ (OTel instrumentation in each node)
OTel Span generation (parent: request_id, child: node_id, span_id)
    ├── Span attributes: workstream_id, gate_id, user_id, model_name, token_count
    ├── Events: "risk_detected", "scope_drift_flagged", "decision_blocking_gate"
    ↓
OTel Collector (local sidecar or centralized)
    ↓ (OTLP/gRPC protocol)
CloudWatch (metrics + logs)
    ├── Custom metrics: waypoint.gate.readiness_score, waypoint.dependency.critical_path_length
    ├── Logs: structured JSON with trace_id, span_id for correlation
    ↓
Grafana (via Amazon Managed Grafana)
    ├── Live dashboards: gate readiness trends, risk open count, scope drift timeline
    ├── Alarms: trigger when gate readiness < 0.7, critical dependencies blocked
    ↓
Alerting & Escalation (PagerDuty, Slack)
```

### Metrics Exported to DTC

| Metric | Type | Description | Dimensions |
|--------|------|-------------|-----------|
| `waypoint.gate.readiness_score` | Gauge (0-1) | AI confidence that gate is ready to proceed | gate_id, phase_name |
| `waypoint.workstream.risk_open_count` | Gauge | Number of open risks (not mitigated/closed) | workstream_id, severity |
| `waypoint.workstream.scope_drift_detected` | Event | Scope change detected (addition/removal/mod) | workstream_id, change_type |
| `waypoint.dependency.critical_path_length` | Gauge | Count of critical + high criticality dependencies on critical path | gate_id |
| `waypoint.decision.pending_count` | Gauge | Number of pending decisions blocking progress | gate_id, decision_status |
| `waypoint.ai.query_latency_ms` | Histogram | Time for AI query execution (intent → response) | intent_type, model_name |

### Configuration

OTel exporter in backend/.env:
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=waypoint-360
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=otlp
OTEL_LOGS_EXPORTER=otlp
```

### DTC Contact & Engagement

- **Contact**: Sasja Tse, #help-dtc-observability Slack channel
- **Call to Action**: Migrate off on-prem Grafana by EOY 2026, participate in AIOps enablement PI 2026.3
- **Status**: (Not yet engaged as of 2026-03-28, marked as GAP in CLAUDE.md)

## Security & Compliance

### Secrets Management

- **Database Credentials**: Via `DATABASE_URL` environment variable (connection string)
- **API Keys**: `ANTHROPIC_API_KEY`, `SECRET_KEY` stored in .env (never in code)
- **Never Hardcode**: All secrets loaded from environment at startup via `pydantic-settings`
- **Validation**: `settings.py` validates required secrets exist on app boot (raises ConfigError if missing)
- **Rotation**: (Prepared for v2: automatic secret rotation via AWS Secrets Manager)

### Input Validation

- **Pydantic v2**: All request bodies validated against type-annotated schemas
- **SQL Injection Prevention**: SQLAlchemy parameterized queries, no string concatenation
- **CORS**: Whitelist of allowed origins (localhost:5173 dev, production domain in .env)
- **Rate Limiting**: (Prepared for v2 via slowapi middleware: max 100 req/min per IP)
- **CSRF Protection**: (Prepared for v2: SameSite=Strict cookies, token validation on mutations)

### Audit Trail & Compliance

- **Timestamp Mixin**: Every entity has `created_at`, `updated_at` (UTC, auto-managed)
- **Author Tracking**: `StatusUpdate.author_id`, `ScopeChange.flagged_by` (user vs AI)
- **Decision Recording**: `Decision.decided_at` (timestamp when decision was made)
- **Change Log**: `ScopeChange` entities retain `baseline_scope` vs `current_scope` for drift tracking
- **Risk History**: `Risk` status transitions logged (open → mitigated → closed)
- **Access Logs**: (Prepared for v2: log all mutations with user_id, timestamp, changes)

## Performance Considerations

### Database Optimization

1. **Eager Loading**: SQLAlchemy `selectinload()` prevents N+1 queries
   ```python
   # Example: gate detail with exit criteria and deliverables
   selectinload(Gate.exit_criteria)
   selectinload(Gate.deliverables).selectinload(Deliverable.workstream)
   ```
2. **Indexes**: Foreign keys auto-indexed; composite index on (workstream_id, gate_id) for deliverables
3. **Query Patterns**: `order_by(Model.sort_order)` for deterministic ordering (required for gate/phase sequencing)
4. **Connection Pooling**: AsyncEngine with pool_size=20, max_overflow=0, timeout=30s
5. **Batch Operations**: (Prepared for v2: bulk insert/update for seed and data migrations)

### Frontend Optimization

1. **Code Splitting**: Vite generates separate chunks per route (CommandCenter, GateDetail, etc.)
2. **Lazy Loading**: `React.lazy()` on page components with Suspense boundaries
3. **Icon Optimization**: Tailwind SVG icons (no PNG/JPG imports)
4. **Query Caching**: React Query with `staleTime=5m`, `gcTime=10m` defaults (prevents excessive API calls)
5. **Memoization**: `useMemo` for computed dependency graph, `useCallback` for event handlers
6. **Bundle Analysis**: (Prepared: npm run build:analyze via vite-plugin-visualizer)

## Error Handling & Recovery

### Backend

```python
# HTTPException for 4xx/5xx responses
raise HTTPException(status_code=404, detail="Workstream not found")

# Database session auto-rollback on exception
async def get_workstream(...):
    try:
        result = await db.execute(...)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
```

### Frontend

- **Query Errors**: React Query retry logic (default 3 retries with exponential backoff 100ms → 300ms → 900ms)
- **Network Errors**: Fallback UI, toast notifications (React Hot Toast)
- **Validation Errors**: Form-level error display via Pydantic validation messages
- **Auth Errors**: Redirect to login on 401, show auth error toast

## Testing Strategy

### Unit Tests

- Model relationships (Person can own multiple Workstreams, Workstream has many Deliverables)
- Status transitions (WorkstreamStatus: not_started → on_track → at_risk → blocked → complete)
- Enum validation (Severity.CRITICAL vs Severity.HIGH correct values)
- Utility functions (compute gate readiness, detect scope drift)

### Integration Tests

- Router endpoints with in-memory SQLite DB (via `sqlite:///:memory:`)
- Async session management (test fixtures with asyncio)
- Dependency injection (mock get_db with test session)
- Full workflows: seed → list → detail → update → verify

### E2E Tests

- Full user flows: login → view program → expand gate → create decision → check status
- Frontend navigation: dashboard → workstream detail → dependencies → risks
- AI queries: natural language prompt → LangGraph execution → response format validation
- Data consistency: mutations update cache, UI reflects changes immediately

## Deployment Checklist

- [ ] Backend `.env` created with DATABASE_URL, ANTHROPIC_API_KEY, SECRET_KEY (production values)
- [ ] PostgreSQL connection pool tuned: pool_size=20, max_overflow=0, timeout=30s
- [ ] OTel collector configured and running (OTLP endpoint reachable)
- [ ] JWT SECRET_KEY rotated from dev value ("waypoint360-dev-secret-change-in-production")
- [ ] CORS allowed_origins updated for production domain
- [ ] Database migrations applied: `init_db()` idempotent and tested
- [ ] Seed data (Waypoint Commercial Workshop) loaded via `POST /api/v1/program/seed`
- [ ] Frontend built: `npm run build` succeeds, no TypeScript errors
- [ ] Frontend served from CDN or nginx (static files, SPA routing configured)
- [ ] Monitoring dashboards linked to DTC pipeline (Grafana dashboards created)
- [ ] Incident playbook created: "Gate readiness assessment failed" → escalation steps
- [ ] Load testing: 100+ concurrent users, verify response times < 500ms
- [ ] Smoke tests: health endpoint, seed, list endpoints, sample queries all pass

# Waypoint 360 - API Contracts

## API Overview

- **Base URL**: `/api/v1` (prefix applied to all routes)
- **Auth**: JWT Bearer token in `Authorization: Bearer <token>` header (stub implementation, v2 adds validation)
- **Rate Limits**: Prepared for v2 (slowapi middleware: 100 req/min per IP)
- **Response Format**: JSON (FastAPI auto-serializes dict responses)
- **Error Handling**: FastAPI HTTPException with status_code + detail dict

---

## Response Format

**Success (200, 201)**: Returns response dict directly (serialized to JSON)
```typescript
// Example: GET /api/v1/workstreams/{id}
{
  "id": 1,
  "name": "AgentOps",
  "status": "on_track",
  "owner": { "id": 5, "name": "Alex Kirschke", "title": "Sr AI Ops Engineer" },
  // ... other fields
}
```

**Error (4xx, 5xx)**: FastAPI HTTPException
```typescript
// HTTP 404
{
  "detail": "Workstream not found"
}

// HTTP 400 (Pydantic validation error)
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "capacity_pct"],
      "msg": "ensure this value is less than or equal to 100",
      "input": 150.0
    }
  ]
}

// HTTP 401 (Auth error)
{
  "detail": "Invalid token"
}

// HTTP 403 (Unauthorized)
{
  "detail": "Not authorized to update this workstream"
}
```

---

## Endpoints

### Health & Status

#### `GET /health`

**Auth**: None
**Status Code**: 200

**Response**:
```typescript
interface HealthResponse {
  status: "healthy";
  project: "Waypoint 360";
  version: "1.0.0";
}
```

**Example**:
```json
{
  "status": "healthy",
  "project": "Waypoint 360",
  "version": "1.0.0"
}
```

---

### Auth Router

#### `POST /api/v1/auth/login`

**Auth**: None (stub implementation)
**Status Code**: 200

**Request**:
```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

**Response**:
```typescript
interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  user: { id: number; name: string; email: string; role: "admin" | "owner" | "viewer" };
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alex@swa.com", "password": "secret"}'

# Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Alex Kirschke",
    "email": "alex@swa.com",
    "role": "admin"
  }
}
```

---

#### `GET /api/v1/auth/me`

**Auth**: Required (Bearer token)
**Status Code**: 200

**Response**:
```typescript
interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: "admin" | "owner" | "viewer";
  title: string | null;
  team: string | null;
  organization: string | null;
  capacity_pct: number;
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Response 200
{
  "id": 1,
  "name": "Alex Kirschke",
  "email": "alex@swa.com",
  "role": "admin",
  "title": "Sr AI Operations Engineer",
  "team": "AgentOps",
  "organization": "SWA",
  "capacity_pct": 100.0
}
```

---

### Program Router

#### `GET /api/v1/program/`

**Auth**: Not required (stub)
**Status Code**: 200

**Response**:
```typescript
interface ProgramOverview {
  id: number;
  name: string;
  description: string | null;
  status: "planning" | "active" | "on_hold" | "complete";
  phases: {
    id: number;
    name: string;
    description: string | null;
    start_week: number;
    end_week: number | null;
    goal: string | null;
  }[];
  gates: {
    id: number;
    name: string;
    short_name: string | null;
    week_number: number;
    status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
    exit_criteria: {
      id: number;
      description: string;
      status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
    }[];
  }[];
  workstreams: {
    id: number;
    name: string;
    short_name: string | null;
    status: "not_started" | "on_track" | "at_risk" | "blocked" | "complete";
    purpose: string | null;
  }[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/program/

# Response 200
{
  "id": 1,
  "name": "Waypoint 360",
  "description": "Real-time program management platform",
  "status": "active",
  "phases": [
    {
      "id": 1,
      "name": "Align",
      "description": "Weeks 1-2: Alignment and planning",
      "start_week": 1,
      "end_week": 2,
      "goal": "Clear scope and priorities"
    }
  ],
  "gates": [
    {
      "id": 1,
      "name": "Align Gate",
      "short_name": "ALIGN",
      "week_number": 2,
      "status": "complete",
      "exit_criteria": [
        {
          "id": 1,
          "description": "All workstream scope locked",
          "status": "complete"
        }
      ]
    }
  ],
  "workstreams": [...]
}
```

---

#### `POST /api/v1/program/seed`

**Auth**: Not required (stub)
**Status Code**: 200

**Request**: None (request body ignored)

**Response**:
```typescript
interface SeedResponse {
  status: "seeded";
  message: "Waypoint program data loaded from Commercial Workshop PDF";
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/program/seed

# Response 200
{
  "status": "seeded",
  "message": "Waypoint program data loaded from Commercial Workshop PDF"
}
```

---

### Workstreams Router

#### `GET /api/v1/workstreams/`

**Auth**: Not required (stub)
**Status Code**: 200

**Response**:
```typescript
interface WorkstreamSummary {
  id: number;
  name: string;
  short_name: string | null;
  purpose: string | null;
  status: "not_started" | "on_track" | "at_risk" | "blocked" | "complete";
  owner: { id: number; name: string } | null;
  risk_count: number;  // count of open risks
  deliverable_count: number;
  deliverables_complete: number;
}

type WorkstreamsListResponse = WorkstreamSummary[];
```

**Example**:
```bash
curl http://localhost:8000/api/v1/workstreams/

# Response 200
[
  {
    "id": 1,
    "name": "AgentOps",
    "short_name": "AGOPS",
    "purpose": "Build and validate observability platform",
    "status": "on_track",
    "owner": { "id": 5, "name": "Alex Kirschke" },
    "risk_count": 2,
    "deliverable_count": 5,
    "deliverables_complete": 2
  },
  {
    "id": 2,
    "name": "Solution Design",
    "short_name": "SDES",
    "purpose": "Define technical architecture",
    "status": "at_risk",
    "owner": { "id": 10, "name": "John Hartfield" },
    "risk_count": 3,
    "deliverable_count": 4,
    "deliverables_complete": 1
  }
]
```

---

#### `GET /api/v1/workstreams/{workstream_id}`

**Auth**: Not required (stub)
**Status Code**: 200 | 404

**Response**:
```typescript
interface WorkstreamDetail {
  id: number;
  name: string;
  short_name: string | null;
  purpose: string | null;
  scope_in: string | null;
  scope_out: string | null;
  baseline_scope: string | null;
  status: "not_started" | "on_track" | "at_risk" | "blocked" | "complete";
  owner: { id: number; name: string; title: string | null } | null;
  members: { id: number; name: string; title: string | null; capacity_pct: number }[];
  deliverables: {
    id: number;
    name: string;
    description: string | null;
    status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
    gate: { id: number; name: string; short_name: string | null } | null;
  }[];
  risks: {
    id: number;
    description: string;
    severity: "critical" | "high" | "medium" | "low";
    likelihood: "high" | "medium" | "low";
    mitigation: string | null;
    status: "open" | "mitigated" | "closed" | "accepted";
  }[];
  decisions: {
    id: number;
    description: string;
    status: "needed" | "pending" | "made" | "deferred";
    decision_maker: string | null;
    due_date: string | null;  // ISO 8601 date
  }[];
  needs_from: {
    id: number;
    workstream: { id: number; name: string };
    description: string;
    status: "open" | "in_progress" | "resolved" | "blocked" | "at_risk";
    criticality: "critical" | "high" | "medium" | "low";
  }[];
  provides_to: {
    id: number;
    workstream: { id: number; name: string };
    description: string;
    status: "open" | "in_progress" | "resolved" | "blocked" | "at_risk";
    criticality: "critical" | "high" | "medium" | "low";
  }[];
  status_updates: {
    id: number;
    content: string;
    status_color: "green" | "yellow" | "red";
    created_at: string;  // ISO 8601 datetime
  }[];  // Last 10 most recent
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/workstreams/1

# Response 200
{
  "id": 1,
  "name": "AgentOps",
  "short_name": "AGOPS",
  "purpose": "Build and validate observability platform",
  "scope_in": "Evaluation framework, CloudWatch integration, Grafana dashboard",
  "scope_out": "Real-time streaming, custom ML models, third-party integrations",
  "baseline_scope": "...",  // snapshot from Align gate
  "status": "on_track",
  "owner": { "id": 5, "name": "Alex Kirschke", "title": "Sr AI Ops Engineer" },
  "members": [
    { "id": 6, "name": "Isaac", "title": "Sr Data Scientist", "capacity_pct": 50.0 }
  ],
  "deliverables": [
    {
      "id": 1,
      "name": "Observability Landscape Assessment",
      "description": "Current state baseline",
      "status": "in_progress",
      "gate": { "id": 2, "name": "Gate 2", "short_name": "INCEPT-1" }
    }
  ],
  "risks": [
    {
      "id": 1,
      "description": "Legal clearance of OpenAI/SWA agreement blocked",
      "severity": "critical",
      "likelihood": "high",
      "mitigation": "Escalate to leadership",
      "status": "open"
    }
  ],
  "decisions": [
    {
      "id": 1,
      "description": "Formalize 3P architecture pattern",
      "status": "pending",
      "decision_maker": "Peter",
      "due_date": "2026-04-03"
    }
  ],
  "needs_from": [
    {
      "id": 1,
      "workstream": { "id": 5, "name": "Solution Design" },
      "description": "Architecture direction package",
      "status": "in_progress",
      "criticality": "critical"
    }
  ],
  "provides_to": [],
  "status_updates": [
    {
      "id": 1,
      "content": "Inception plan draft completed. Ready for review.",
      "status_color": "green",
      "created_at": "2026-03-28T10:30:00Z"
    }
  ]
}
```

---

#### `PUT /api/v1/workstreams/{workstream_id}`

**Auth**: Required (admin or workstream owner)
**Status Code**: 200 | 403 | 404

**Request**:
```typescript
interface UpdateWorkstreamRequest {
  name?: string;
  purpose?: string;
  scope_in?: string;
  scope_out?: string;
  status?: "not_started" | "on_track" | "at_risk" | "blocked" | "complete";
}
```

**Response**:
```typescript
interface UpdateResponse {
  status: "updated";
  id: number;
}
```

**Example**:
```bash
curl -X PUT http://localhost:8000/api/v1/workstreams/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "status": "at_risk",
    "scope_in": "Updated scope statement"
  }'

# Response 200
{
  "status": "updated",
  "id": 1
}
```

---

### Gates Router

#### `GET /api/v1/gates/`

**Auth**: Not required (stub)
**Status Code**: 200

**Response**:
```typescript
interface GateSummary {
  id: number;
  name: string;
  short_name: string | null;
  description: string | null;
  week_number: number;
  due_date: string | null;  // ISO 8601 date
  status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
  exit_criteria: {
    id: number;
    description: string;
    status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
  }[];
  criteria_complete: number;
  criteria_total: number;
}

type GatesListResponse = GateSummary[];
```

**Example**:
```bash
curl http://localhost:8000/api/v1/gates/

# Response 200
[
  {
    "id": 1,
    "name": "Align Gate",
    "short_name": "ALIGN",
    "description": "Program alignment and scope locked",
    "week_number": 2,
    "due_date": "2026-03-28",
    "status": "complete",
    "exit_criteria": [
      {
        "id": 1,
        "description": "All workstream scope locked",
        "status": "complete"
      }
    ],
    "criteria_complete": 1,
    "criteria_total": 1
  },
  {
    "id": 2,
    "name": "Inception Gate 1",
    "short_name": "INCEPT-1",
    "description": "Technical readiness for prototype",
    "week_number": 4,
    "due_date": "2026-04-10",
    "status": "in_progress",
    "exit_criteria": [
      {
        "id": 2,
        "description": "Architecture direction finalized",
        "status": "in_progress"
      }
    ],
    "criteria_complete": 0,
    "criteria_total": 1
  }
]
```

---

#### `GET /api/v1/gates/timeline`

**Auth**: Not required (stub)
**Status Code**: 200

**Response**:
```typescript
interface GateTimeline {
  gates: { id: number; name: string; short_name: string | null; week: number }[];
  matrix: {
    workstream: { id: number; name: string; short_name: string | null };
    gates: Record<string, {
      gate_id: number;
      status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
      deliverable_count: number;
    }>;
  }[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/gates/timeline

# Response 200
{
  "gates": [
    { "id": 1, "name": "Align Gate", "short_name": "ALIGN", "week": 2 },
    { "id": 2, "name": "Inception Gate 1", "short_name": "INCEPT-1", "week": 4 }
  ],
  "matrix": [
    {
      "workstream": { "id": 1, "name": "AgentOps", "short_name": "AGOPS" },
      "gates": {
        "ALIGN": { "gate_id": 1, "status": "complete", "deliverable_count": 2 },
        "INCEPT-1": { "gate_id": 2, "status": "in_progress", "deliverable_count": 3 }
      }
    }
  ]
}
```

---

#### `GET /api/v1/gates/{gate_id}`

**Auth**: Not required (stub)
**Status Code**: 200 | 404

**Response**:
```typescript
interface GateDetail {
  id: number;
  name: string;
  short_name: string | null;
  description: string | null;
  week_number: number;
  status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
  exit_criteria: {
    id: number;
    description: string;
    status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
    notes: string | null;
  }[];
  workstream_deliverables: {
    workstream: { id: number; name: string };
    deliverables: {
      id: number;
      name: string;
      status: "not_started" | "in_progress" | "complete" | "at_risk" | "blocked";
    }[];
  }[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/gates/2

# Response 200
{
  "id": 2,
  "name": "Inception Gate 1",
  "short_name": "INCEPT-1",
  "description": "Technical readiness checkpoint",
  "week_number": 4,
  "status": "in_progress",
  "exit_criteria": [
    {
      "id": 2,
      "description": "Architecture direction finalized",
      "status": "in_progress",
      "notes": "Awaiting Chris decision on Pattern 2"
    }
  ],
  "workstream_deliverables": [
    {
      "workstream": { "id": 1, "name": "AgentOps" },
      "deliverables": [
        {
          "id": 1,
          "name": "Observability Landscape Assessment",
          "status": "in_progress"
        }
      ]
    }
  ]
}
```

---

### Dependencies Router

#### `GET /api/v1/dependencies/`

**Auth**: Not required (stub)
**Status Code**: 200

**Response** (D3.js force graph format):
```typescript
interface DependencyGraph {
  nodes: {
    id: number;
    name: string;
    short_name: string | null;
    status: "not_started" | "on_track" | "at_risk" | "blocked" | "complete";
    group: number;  // sort_order for grouping
  }[];
  links: {
    id: number;
    source: number;  // workstream_id
    target: number;  // workstream_id
    description: string;
    type: "needs_from" | "provides_to" | "blocks" | "informs";
    status: "open" | "in_progress" | "resolved" | "blocked" | "at_risk";
    criticality: "critical" | "high" | "medium" | "low";
    gate: string | null;  // gate short_name
  }[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/dependencies/

# Response 200
{
  "nodes": [
    { "id": 1, "name": "AgentOps", "short_name": "AGOPS", "status": "on_track", "group": 0 },
    { "id": 2, "name": "Solution Design", "short_name": "SDES", "status": "at_risk", "group": 1 }
  ],
  "links": [
    {
      "id": 1,
      "source": 1,
      "target": 2,
      "description": "Needs architecture direction from SDES",
      "type": "needs_from",
      "status": "in_progress",
      "criticality": "critical",
      "gate": "INCEPT-1"
    }
  ]
}
```

---

#### `GET /api/v1/dependencies/critical-path`

**Auth**: Not required (stub)
**Status Code**: 200

**Response**:
```typescript
interface CriticalPath {
  critical_dependencies: number;  // count of critical criticality
  high_dependencies: number;      // count of high criticality
  blocked_or_at_risk: {
    dependency_id: number;
    from: { id: number; name: string };
    to: { id: number; name: string };
    description: string;
    status: "blocked" | "at_risk";
    criticality: "critical" | "high";
  }[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/dependencies/critical-path

# Response 200
{
  "critical_dependencies": 3,
  "high_dependencies": 5,
  "blocked_or_at_risk": [
    {
      "dependency_id": 1,
      "from": { "id": 1, "name": "AgentOps" },
      "to": { "id": 2, "name": "Solution Design" },
      "description": "Architecture decision blocking eval framework",
      "status": "blocked",
      "criticality": "critical"
    }
  ]
}
```

---

### AI Router

#### `POST /api/v1/ai/query`

**Auth**: Not required (stub, v2 adds validation)
**Status Code**: 200

**Request**:
```typescript
interface AIQueryRequest {
  query: string;  // Natural language prompt
}
```

**Response** (stub, v2 routes to LangGraph):
```typescript
interface AIQueryResponse {
  query: string;
  intent: string;  // "general" (stub), v2: "gate_readiness" | "scope_creep" | "risk_correlation" | "summary"
  response: string;
  recommendations: any[];
  sources: any[];
  confidence: number;  // 0.0 stub, v2: 0.0-1.0
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is Gate 1 ready to proceed?"}'

# Response 200
{
  "query": "Is Gate 1 ready to proceed?",
  "intent": "general",
  "response": "[LangGraph integration pending] Analysis for: Is Gate 1 ready to proceed?",
  "recommendations": [],
  "sources": [],
  "confidence": 0.0
}
```

---

#### `GET /api/v1/ai/gate-readiness/{gate_id}`

**Auth**: Not required (stub, v2 adds validation)
**Status Code**: 200

**Response** (stub, v2 performs LLM-as-judge evaluation):
```typescript
interface GateReadinessResponse {
  gate_id: number;
  status: "stub";  // v2: "ready" | "at_risk" | "blocked"
  message: string;
  confidence: number;  // 0.0 stub, v2: 0.0-1.0
  workstream_readiness: any[];
  blockers: any[];
  recommendations: any[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/ai/gate-readiness/2

# Response 200
{
  "gate_id": 2,
  "status": "stub",
  "message": "[LangGraph integration pending] Gate readiness assessment",
  "confidence": 0.0,
  "workstream_readiness": [],
  "blockers": [],
  "recommendations": []
}
```

---

#### `GET /api/v1/ai/scope-creep`

**Auth**: Not required (stub, v2 adds validation)
**Status Code**: 200

**Response** (stub, v2 compares baseline_scope vs scope_in/scope_out):
```typescript
interface ScopeCreepResponse {
  status: "stub";  // v2: "detected" | "clean"
  message: string;
  workstreams_flagged: any[];
  total_changes: number;
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/ai/scope-creep

# Response 200
{
  "status": "stub",
  "message": "[LangGraph integration pending] Scope creep analysis",
  "workstreams_flagged": [],
  "total_changes": 0
}
```

---

#### `GET /api/v1/ai/risks/correlated`

**Auth**: Not required (stub, v2 adds validation)
**Status Code**: 200

**Response** (stub, v2 identifies compound risks across workstreams):
```typescript
interface CorrelatedRisksResponse {
  status: "stub";  // v2: "has_correlations" | "no_correlations"
  message: string;
  correlated_risks: any[];
  compound_risk_score: number;  // 0.0 stub, v2: 0.0-1.0
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/ai/risks/correlated

# Response 200
{
  "status": "stub",
  "message": "[LangGraph integration pending] Risk correlation analysis",
  "correlated_risks": [],
  "compound_risk_score": 0.0
}
```

---

#### `GET /api/v1/ai/summary`

**Auth**: Not required (stub, v2 adds validation)
**Status Code**: 200

**Response** (stub, v2 generates executive narrative):
```typescript
interface ExecutiveSummaryResponse {
  status: "stub";  // v2: "generated"
  message: string;
  summary: string;  // v2: narrative executive brief
  key_highlights: any[];
  action_items: any[];
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/ai/summary

# Response 200
{
  "status": "stub",
  "message": "[LangGraph integration pending] Executive summary generation",
  "summary": "",
  "key_highlights": [],
  "action_items": []
}
```

---

## Status Codes

| Code | Meaning | Endpoint Examples |
|------|---------|------------------|
| **200** | OK | GET, PUT endpoints on success |
| **201** | Created | POST endpoints (prepared for v2) |
| **400** | Bad Request | Invalid Pydantic schema (e.g., capacity_pct > 100) |
| **401** | Unauthorized | Missing/invalid JWT token on protected routes |
| **403** | Forbidden | User lacks RBAC permission (e.g., non-owner updating workstream) |
| **404** | Not Found | Resource not found (e.g., workstream_id=999) |
| **500** | Server Error | Unhandled exception (database error, LangGraph crash) |

---

## Error Handling Examples

**Validation Error (400)**:
```bash
curl -X PUT http://localhost:8000/api/v1/workstreams/1 \
  -H "Content-Type: application/json" \
  -d '{"capacity_pct": 150}'

# Response 400
{
  "detail": [
    {
      "type": "value_error.number.not_le",
      "loc": ["body", "capacity_pct"],
      "msg": "ensure this value is less than or equal to 100",
      "input": 150
    }
  ]
}
```

**Not Found (404)**:
```bash
curl http://localhost:8000/api/v1/workstreams/999

# Response 404
{
  "detail": "Workstream not found"
}
```

**Authorization Error (403)** (prepared for v2):
```bash
curl -X PUT http://localhost:8000/api/v1/workstreams/1 \
  -H "Authorization: Bearer <viewer_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "at_risk"}'

# Response 403
{
  "detail": "Not authorized to update this workstream"
}
```

---

## Authentication Flow (v2 Design)

1. **Login**: `POST /api/v1/auth/login` → receive JWT token
2. **Store Token**: localStorage or sessionStorage (frontend)
3. **Include Token**: Axios interceptor adds `Authorization: Bearer <token>` to all requests
4. **Validate**: FastAPI middleware validates token on protected routes
5. **Handle Expiry**: If 401 response, redirect to login or attempt token refresh (v2)

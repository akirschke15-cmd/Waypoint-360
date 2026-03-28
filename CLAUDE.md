# Waypoint 360: Boiler 4.0 Project Brain

**Framework:** Boiler 4.0 (ECC runtime + Boiler 3.0 governance)
**Project:** Waypoint 360
**Description:** AI-powered 360-degree program facilitation platform for Southwest Airlines' Project Waypoint -- the enterprise agentic shopping & booking initiative. Provides full cross-workstream visibility, dependency tracking, gate readiness assessment, and AI-driven project intelligence.
**Target Users:** Waypoint program leadership (Tamara, Peter, Justin), 11 workstream owners, and their teams
**BOILER_MODE:** `lean` (rapid iteration -- 1-week v1 target)

---

## What is Waypoint 360

**Purpose:** Eliminate the transparency gap across Waypoint's 11 interdependent workstreams by providing a single platform where every workstream's purpose, scope, deliverables, dependencies, risks, decisions, resourcing, and timing are visible to all stakeholders -- with AI-powered analysis that surfaces scope creep, dependency risks, and gate readiness automatically.

**Core Problem:** Waypoint's 11 workstreams are planning in isolation. Dependencies surface late, risks compound silently, and leadership lacks a single view of program health. The Commercial Workshop (3/9/26) established the Align/Incept/Deliver framework with 6 stage gates, but no tool exists to track cross-workstream state, enforce gate exit criteria, or provide real-time program intelligence.

**Success Metric:** Leadership can open Waypoint 360 and within 30 seconds understand: which workstreams are on track, which are blocked, what the critical path is, and what decisions need to be made before the next gate.

**Non-Goals:**
- Not a replacement for Jira/Confluence (complementary -- future API integration)
- Not a project management tool for individual task tracking within workstreams
- Not a code repository or deployment pipeline
- Not a customer-facing product

**User Segments:**
- **Leadership (Tamara, Peter, Justin):** Read-only dashboards, AI command center for natural language queries, gate readiness reports
- **Workstream Owners (11):** CRUD access to their workstream data, structured forms matching the Workstream Inception Planning Guide
- **Program Management (John):** Full access, cross-workstream editing, RAID log management
- **AgentOps (Alex):** Admin access, AI configuration, system management

**Key Constraints:**
- Must be deployable to AWS lab environment
- Configurable theme system (SWA branded default, neutral option)
- Configurable gate framework (not hardcoded to current 6-gate structure)
- Future API/MCP endpoints for Confluence, Jira, Slack (stubbed in v1)
- LangGraph for all AI orchestration

---

## Tech Stack

**Frontend:** React 18 + TypeScript + Vite + Tailwind CSS + D3.js (dependency graph)
**Backend:** Python 3.11+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2
**Database:** SQLite (development) / PostgreSQL (production)
**AI Layer:** LangGraph + Claude API (Anthropic)
**Containerization:** Docker + docker-compose
**Auth:** JWT-based with role-based access control (RBAC)

---

## Data Model (Core Entities)

### Program
- id, name, description, start_date, end_date, status, created_at

### Phase
- id, program_id, name (Align/Incept/Deliver), description, start_week, end_week, goal, key_activities, exit_criteria

### Gate
- id, program_id, phase_id, name, description, week_number, due_date, status (not_started/in_progress/complete/at_risk/blocked)
- exit_criteria (JSON array of criteria with status)

### Workstream
- id, program_id, name, purpose, scope_in, scope_out, owner_id, status, created_at
- Key relationships tracked via Dependency entity

### Person
- id, name, email, role, team, capacity_pct, workstream_ids

### Deliverable
- id, workstream_id, gate_id, name, description, status (not_started/in_progress/complete/at_risk/blocked), due_date, assignee_id

### Dependency
- id, source_workstream_id, target_workstream_id, gate_id, description, type (needs_from/provides_to), status (open/resolved/blocked), criticality (high/medium/low)

### Risk
- id, workstream_id, description, severity (critical/high/medium/low), likelihood (high/medium/low), mitigation, status (open/mitigated/accepted/closed), owner_id

### Decision
- id, workstream_id, gate_id, description, status (needed/pending/made/deferred), decision_maker, due_date, resolution, decided_at

### StatusUpdate
- id, workstream_id, gate_id, author_id, content, status_color (green/yellow/red), created_at

### ScopeChange
- id, workstream_id, description, change_type (addition/removal/modification), baseline_scope, current_scope, flagged_by (user/ai), flagged_at, resolution

---

## LangGraph Agent Architecture

All AI capabilities are orchestrated through a single LangGraph StateGraph with the following nodes:

### State Schema
```python
class WaypointAnalysisState(TypedDict):
    query: str                      # User's natural language query
    query_type: str                 # Classified intent
    workstream_data: dict           # Loaded workstream context
    dependency_graph: dict          # Full dependency map
    gate_data: dict                 # Gate status and criteria
    analysis_results: list          # Accumulated analysis outputs
    recommendations: list           # Action recommendations
    summary: str                    # Final synthesized response
```

### Agent Nodes
1. **Intent Classifier** -- Routes user queries to appropriate analysis nodes
2. **Scope Creep Detector** -- Compares baseline vs current scope per workstream, flags drift
3. **Dependency Analyzer** -- Traverses dependency graph, identifies critical path, cascading delay risks
4. **Gate Readiness Assessor** -- Evaluates exit criteria across all workstreams for a given gate, produces confidence scores
5. **Risk Aggregator** -- Cross-workstream risk correlation, identifies compound risks
6. **Status Synthesizer** -- Generates executive summaries from all workstream updates
7. **Response Formatter** -- Structures final output for the command center UI

### Graph Edges (Conditional Routing)
- Intent Classifier -> (scope_creep | dependency | gate_readiness | risk | status | general)
- All analysis nodes -> Response Formatter
- Complex queries -> multiple analysis nodes in sequence

---

## Frontend Architecture

### Primary View: AI Command Center
- Central chat interface (natural language queries powered by LangGraph)
- Flanked by real-time status panels:
  - Left: Workstream status cards (compact, color-coded)
  - Right: Active gate progress + upcoming deliverables
  - Bottom: AI-generated alerts (scope creep, blocked dependencies, at-risk gates)

### Secondary Views (navigable from command center)
1. **Gate Timeline** -- Horizontal timeline, gates as columns, workstreams as rows, deliverable status in cells
2. **Dependency Graph** -- Interactive D3 force-directed graph, nodes = workstreams, edges = dependencies
3. **Workstream Detail** -- Full workstream card with structured form (matches Inception Planning Guide)
4. **Risk Heat Map** -- Severity x Likelihood matrix across all workstreams
5. **RAID Log** -- Tabular view of Risks, Assumptions, Issues, Dependencies, Decisions

### Theme System
- CSS custom properties for all colors, fonts, spacing
- SWA theme: Blue (#304CB2), Gold (#FFBF00), Red (#C8102E)
- Neutral theme: Dark professional palette
- Theme toggle in UI header

---

## API Contracts

### Workstreams
- `GET /api/v1/workstreams` -- List all with summary status
- `GET /api/v1/workstreams/{id}` -- Full detail with deliverables, risks, dependencies
- `POST /api/v1/workstreams` -- Create workstream
- `PUT /api/v1/workstreams/{id}` -- Update workstream
- `GET /api/v1/workstreams/{id}/dependencies` -- Inbound and outbound dependencies

### Gates
- `GET /api/v1/gates` -- All gates with exit criteria status
- `GET /api/v1/gates/{id}` -- Gate detail with per-workstream deliverable status
- `PUT /api/v1/gates/{id}/criteria/{criteria_id}` -- Update exit criteria status

### Dependencies
- `GET /api/v1/dependencies` -- Full dependency graph data
- `POST /api/v1/dependencies` -- Create dependency
- `PUT /api/v1/dependencies/{id}` -- Update dependency status
- `GET /api/v1/dependencies/critical-path` -- Computed critical path

### AI (LangGraph)
- `POST /api/v1/ai/query` -- Natural language query -> LangGraph analysis
- `GET /api/v1/ai/gate-readiness/{gate_id}` -- Gate readiness assessment
- `GET /api/v1/ai/scope-creep` -- Scope creep detection across all workstreams
- `GET /api/v1/ai/risks/correlated` -- Cross-workstream risk correlation
- `GET /api/v1/ai/summary` -- Executive program summary

### Auth
- `POST /api/v1/auth/login` -- JWT token
- `GET /api/v1/auth/me` -- Current user + role

### Future Integrations (Stubbed)
- `GET /api/v1/integrations/confluence/sync` -- Confluence page sync
- `GET /api/v1/integrations/jira/sync` -- Jira issue sync
- `POST /api/v1/integrations/slack/notify` -- Slack notification

---

## Waypoint Program Data (from Commercial Workshop 3/9/26)

### Phases
1. **Align** (Wk 0-2): Communicate scope priorities, stand up team/decision structures/plans
2. **Incept** (Wk 3-12): Converge on build-ready, value-backed scope and MVP solutions
3. **Deliver** (Wk 13+): Translate inception outputs into executable backlog, begin development

### Gates (Default Configuration)
| Gate | Name | Week | Purpose |
|------|------|------|---------|
| ALIGN | Establish Operating Clarity | 2 | Scope cascaded, ownership confirmed, operating structure defined |
| INCEPT 1 | Set the Direction | 4 | Shared context established, constraints inventoried |
| INCEPT 2 | Lock Scope & Requirements | 6 | Scope locked, process requirements emerging, value framework defined |
| INCEPT 3 | Validate with Customers | 8 | Prototypes tested, evidence synthesized, architecture converging |
| INCEPT 4 | Finalize Solution & Value | 10 | Specifications complete, business case quantified, delivery readiness staged |
| INCEPT 5 | Confirm Dev Readiness | 12 | Specs accepted by dev teams, business case packaged for executive review |

### Workstreams (11)
1. Customer Experience -- Owner: Nicola
2. Process Discovery & Design -- Owner: Haylee
3. Business Strategy & Value Case -- Owner: Hursh (ProServ)
4. Experience & Conversation Design -- Owner: Hursh (ProServ)
5. Agent & Solution Delivery -- Owner: Preethi, Jon H
6. AgentOps -- Owner: Julie (Alex is workstream lead)
7. Prototyping & Validation -- Owner: Hursh (ProServ), supported by Nicola
8. AI Governance, Risk & Compliance -- Owner: Jenn
9. Program Management -- Owner: John
10. Cyber -- Owner: TBD
11. Merchandising (pending scope decision by Mark)

### Scope Overview (Waypoint MVP)
- **3P**: Help customers search, compare, book flights via ChatGPT (Apps SDK). Read + recommend only.
- **1P**: Help customers search, compare, book flights + ancillaries on southwest.com. Flight inventory only (no vacations). Web only (no mobile). Logged-in customers only. Revenue trips only. US-only. USD-only.
- **Merchandising**: Drive incremental revenue through awareness/take rate of SWA products. Scope TBD.
- **Interdependence**: 3P creates market presence; 1P gives control over brand, data, commercial logic; merchandising protects/grows margin.

---

## Session Behavior

- **BOILER_MODE=lean** for rapid iteration during 1-week v1 sprint
- Vertical slice rule applies: features go from database to API to UI
- AI features use LangGraph exclusively (no direct API calls)
- Theme system is data-driven (CSS custom properties, not hardcoded colors)
- Gate framework is configurable (gates are data, not code)
- All workstream data is seeded from Commercial Workshop PDF
- Future integrations (Confluence, Jira, Slack) are stubbed with interface contracts
- Auth is JWT with RBAC: admin, owner, viewer roles

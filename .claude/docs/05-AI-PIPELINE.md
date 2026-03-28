# Waypoint 360 - AI Pipeline

> LangGraph-based agentic reasoning system. 7 StateGraph nodes orchestrate intent classification, scope analysis, dependency reasoning, gate readiness assessment, risk correlation, and executive synthesis. Claude Sonnet 4 as primary model. Stateless, async, deterministic routing.

## Pipeline Overview

**Architecture**: LangGraph StateGraph with 7 nodes + conditional edges, fed by FastAPI `/ai/` endpoints.

**Data Flow**:
```
User Query → Route Handler → LangGraph StateGraph
  → Intent Classifier (route to specific analyzer)
  → Specialized Nodes (scope creep, deps, gate readiness, risks, synthesis)
  → Response Formatter (structure for frontend)
  → Return JSON response
```

**Deployment Status**:
- ✅ Node definitions (boilerplate structure ready)
- ✅ State schema (defined, typed)
- ✅ Routing logic (intent-based branching)
- ❌ LangGraph integration (pending: Session Phase 3)
- ❌ Live endpoint testing (pending: after Phase 3)

---

## State Schema

**StateGraph Input Type** (`LangGraphState`):
```python
class LangGraphState(TypedDict):
    # Original query + metadata
    query: str                                  # User natural language input
    intent: str                                 # Classified intent (scope_creep, gate_readiness, etc.)
    confidence: float                           # 0.0-1.0 confidence in intent classification

    # Program context (fetched from DB)
    program_id: int
    workstreams: list[WorkstreamDetail]        # All workstreams in program
    gates: list[Gate]                          # All gates
    dependencies: list[Dependency]             # All dependencies
    risks: list[Risk]                          # All risks

    # Analysis results (populated by specialized nodes)
    scope_creep_analysis: dict                 # {workstream_id: {baseline, current, drift}}
    dependency_analysis: dict                  # {blocked_chains, circular_deps, critical_paths}
    gate_readiness: dict                       # {gate_id: {status, criteria_complete, workstreams}}
    risk_analysis: dict                        # {correlated_risks, compound_score, cascade_patterns}

    # Final response
    response: str                              # Human-readable response text
    recommendations: list[str]                 # 3-5 actionable recommendations
    sources: list[str]                         # Data sources used (e.g., "workstream xyz", "gate 1")
    metadata: dict                             # Additional context (tokens used, timing, etc.)
```

---

## 7 StateGraph Nodes

### Node 1: Intent Classifier
**Input**: `query` (raw user input)
**Output**: `intent`, `confidence`

**Logic**:
- Use Claude to classify query into one of 7 intent categories:
  - `general_query` → Route to Status Synthesizer
  - `scope_creep` → Route to Scope Creep Detector
  - `gate_readiness` → Route to Gate Readiness Assessor (may require gate_id extraction)
  - `dependency_analysis` → Route to Dependency Analyzer
  - `risk_correlation` → Route to Risk Aggregator
  - `workstream_detail` → Route to Status Synthesizer with workstream filter
  - `executive_summary` → Route to Status Synthesizer (full synthesis mode)

**Prompt Template**:
```
User query: "{query}"

Classify this query into one of these intents:
1. scope_creep - User asking about scope changes, drifts, or baseline vs actual
2. gate_readiness - User asking about gate completion status, exit criteria
3. dependency_analysis - User asking about blocked chains, circular deps, critical paths
4. risk_correlation - User asking about cross-workstream risks, compound risks
5. executive_summary - User asking for overall program status, key highlights
6. workstream_detail - User asking about a specific workstream
7. general_query - General question about program state

Respond with JSON:
{
  "intent": "<intent_name>",
  "confidence": 0.0-1.0,
  "extracted_params": {"gate_id": 1, "workstream_id": 2}  // if applicable
}
```

**Conditional Edge**:
```
intent_classifier
  ├→ scope_creep: Scope Creep Detector
  ├→ gate_readiness: Gate Readiness Assessor
  ├→ dependency_analysis: Dependency Analyzer
  ├→ risk_correlation: Risk Aggregator
  └→ (all others): Status Synthesizer
```

---

### Node 2: Scope Creep Detector
**Input**: `workstreams`, `query`
**Output**: `scope_creep_analysis`

**Logic**:
- For each workstream, compare `baseline_scope` vs `scope_in` + `scope_out`
- Identify drift (new items in scope_in not in baseline, items in scope_out that were in baseline)
- Flag severity based on change magnitude

**Analysis**:
```python
scope_creep_analysis = {
    workstream_id: {
        "baseline": "...",
        "current_in": "...",
        "current_out": "...",
        "drift_detected": bool,
        "drift_type": "expansion" | "contraction" | "misalignment",
        "severity": "low" | "medium" | "high",
        "explanation": "..."
    }
}
```

**Prompt Template**:
```
Analyze scope creep for workstream: {workstream_name}

Baseline (approved scope):
{baseline_scope}

Current Scope In (confirmed in scope):
{scope_in}

Current Scope Out (explicitly out of scope):
{scope_out}

Compare and identify:
1. Items in Scope In not in baseline (expansion)
2. Items in baseline not in Scope In or Out (unaddressed)
3. Items in Scope Out that should be addressed

Respond with JSON:
{
  "drift_detected": bool,
  "drift_type": "expansion|contraction|misalignment",
  "severity": "low|medium|high",
  "explanation": "...",
  "recommendations": ["...", "..."]
}
```

---

### Node 3: Dependency Analyzer
**Input**: `dependencies`, `query`
**Output**: `dependency_analysis`

**Logic**:
- Traverse dependency graph, identify blocked chains (A→B→C where B is blocked)
- Detect circular dependencies (A→B→A)
- Find critical paths (chains of critical dependencies)
- Flag with status and gate due dates

**Analysis**:
```python
dependency_analysis = {
    "blocked_chains": [
        {"chain": ["ws_a", "ws_b", "ws_c"], "blocker": "ws_b", "reason": "..."}
    ],
    "circular_dependencies": [
        {"cycle": ["ws_x", "ws_y", "ws_x"], "severity": "high"}
    ],
    "critical_paths": [
        {"path": ["ws_1", "ws_2", "ws_3"], "total_criticality": 3}
    ],
    "recommendations": ["..."]
}
```

**Logic in Code**:
- Use topological sort to detect cycles
- BFS/DFS to find all paths from each node
- Mark chains where any intermediate node has status != "on_track"

---

### Node 4: Gate Readiness Assessor
**Input**: `gates`, `workstreams`, `query` (may include gate_id from Intent Classifier)
**Output**: `gate_readiness`

**Logic**:
- For specified gate (or all gates if unspecified):
  - Count exit criteria (complete vs total)
  - List workstreams and their deliverable completion %
  - Identify blockers (if any dependency blocker)
  - Assess readiness confidence

**Analysis**:
```python
gate_readiness = {
    gate_id: {
        "name": "Gate 1",
        "week": 2,
        "status": "on_track|at_risk|blocked",
        "exit_criteria": {
            "complete": 6,
            "total": 10,
            "percentage": 60
        },
        "workstream_readiness": [
            {
                "workstream_id": 1,
                "name": "AgentOps",
                "deliverables": {"complete": 4, "total": 6},
                "blockers": ["dependency_from_ws_2"]
            }
        ],
        "confidence": 0.7,
        "recommendations": ["..."]
    }
}
```

**Prompt Template**:
```
Assess readiness for Gate {gate_name} (Week {week_number})

Exit Criteria Completion: {complete}/{total} ({percentage}%)
Criteria Status: {criteria_list}

Workstream Deliverables:
{workstream_table}

Blockers: {blockers_list}

Assess the likelihood this gate will be completed on time.
Respond with JSON:
{
  "status": "on_track|at_risk|blocked",
  "confidence": 0.0-1.0,
  "summary": "...",
  "blockers": ["...", "..."],
  "recommendations": ["...", "..."]
}
```

---

### Node 5: Risk Aggregator
**Input**: `risks`, `workstreams`, `dependencies`, `query`
**Output**: `risk_analysis`

**Logic**:
- Analyze risks across all workstreams
- Identify compound risks (same risk across multiple workstreams, or multiple risks in same workstream)
- Detect cascade patterns (risk in A affects B and C via dependencies)
- Compute compound risk score (0-1 scale)

**Analysis**:
```python
risk_analysis = {
    "correlated_risks": [
        {
            "risk_type": "Technical",
            "workstreams": ["ws_a", "ws_b"],
            "count": 2,
            "avg_severity": 4.5,
            "cascade_risk": True
        }
    ],
    "compound_risk_score": 0.65,
    "cascade_patterns": [
        {
            "origin_workstream": "ws_platform",
            "origin_risk": "API delay",
            "affected_workstreams": ["ws_1p", "ws_3p"],
            "severity": "critical"
        }
    ],
    "recommendations": ["..."]
}
```

**Prompt Template**:
```
Analyze cross-workstream risks.

All Risks:
{risks_table}

Dependencies:
{dependencies_list}

Identify:
1. Risks repeated across workstreams (compound risks)
2. Risks that affect multiple workstreams via dependencies (cascades)
3. High-severity clustering in specific workstreams

Respond with JSON:
{
  "compound_risk_score": 0.0-1.0,
  "correlated_risks": [{"type": "...", "workstreams": [...], "severity": "..."}],
  "cascade_patterns": [...],
  "recommendations": ["...", "..."]
}
```

---

### Node 6: Status Synthesizer
**Input**: All state (program_id, workstreams, gates, dependencies, risks, + any previous analysis)
**Output**: `response`, `recommendations`, `sources`

**Logic**:
- Synthesize program status from all available data
- Highlight key metrics (gate progress, deliverable %, at-risk count)
- Surface highest-priority issues (critical risks, blocked dependencies, at-risk workstreams)
- Generate executive summary or focused response based on query intent

**Response Template**:
```python
response = {
    "response": "Program is {status}. Gate 1 is {progress}%. {key_issues}. {recommendations}.",
    "recommendations": [
        "Unblock dependency between A and B (due by {date})",
        "Escalate critical risk in Platform workstream",
        "Review scope changes in AgentOps workstream"
    ],
    "sources": [
        "workstream:agentops",
        "gate:1",
        "dependency:platform->1p",
        "risk:api_delay"
    ]
}
```

**Prompt Template**:
```
Synthesize program status for Southwest Airlines' Waypoint program.

Program Overview:
- Status: {program_status}
- Current Gate: {current_gate}
- Phases: {phases}

Gate Progress:
{gates_status_table}

Workstreams ({count}):
{workstreams_table}

Key Issues:
{issues_list}

Generate a concise executive summary addressing the user's query:
"{original_query}"

Respond with JSON:
{
  "response": "...",
  "key_highlights": ["...", "..."],
  "action_items": ["...", "..."],
  "recommendations": ["...", "..."]
}
```

---

### Node 7: Response Formatter
**Input**: All analysis nodes + synthesized response
**Output**: Final `response` object (JSON)

**Logic**:
- Merge all analysis results into frontend-compatible JSON
- Ensure all placeholders filled (no {token} syntax)
- Structure recommendations (limit to 3-5)
- Add metadata (confidence, sources, token usage if tracked)

**Output Format**:
```python
@router.post("/query")
async def ai_query(data: dict):
    # ... StateGraph execution ...
    return {
        "query": original_query,
        "intent": classified_intent,
        "response": formatted_response,
        "recommendations": ["rec1", "rec2", "rec3"],
        "sources": ["workstream:xyz", "gate:1"],
        "confidence": 0.85,
        "metadata": {
            "nodes_executed": ["intent_classifier", "status_synthesizer"],
            "execution_time_ms": 1234,
            "tokens_used": 2500  # if tracked
        }
    }
```

---

## Routing Logic

**Conditional Edges** (determined by Intent Classifier):
```
START
  ↓
intent_classifier
  ├─ scope_creep → scope_creep_detector → status_synthesizer → response_formatter → END
  ├─ gate_readiness → gate_readiness_assessor → status_synthesizer → response_formatter → END
  ├─ dependency_analysis → dependency_analyzer → status_synthesizer → response_formatter → END
  ├─ risk_correlation → risk_aggregator → status_synthesizer → response_formatter → END
  └─ (general/summary/workstream_detail) → status_synthesizer → response_formatter → END
```

**Key Principle**: Every path flows through Status Synthesizer (to contextualize analysis) and Response Formatter (to finalize output). Specialized analyzers enrich the state, Status Synthesizer interprets results in context.

---

## Token Budgets & Cost Estimates

**Model**: `claude-sonnet-4-20250514` (default, configurable via env var `AI_MODEL`)

**Pricing** (as of March 2026):
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

**Per-Call Estimates**:

| Operation | Avg Input Tokens | Avg Output Tokens | Total | Approx Cost |
|-----------|---|---|---|---|
| Intent Classification | 300 | 50 | 350 | $0.0015 |
| Scope Creep Analysis (1 WS) | 800 | 200 | 1000 | $0.0045 |
| Gate Readiness (1 gate) | 1200 | 300 | 1500 | $0.007 |
| Dependency Analysis | 1500 | 400 | 1900 | $0.009 |
| Risk Aggregation | 1800 | 500 | 2300 | $0.011 |
| Status Synthesis (full program) | 2500 | 600 | 3100 | $0.015 |
| Full Workflow (specialized analyzer + synthesis) | 4000 | 1000 | 5000 | $0.023 |

**Budget Allocation** (example: $100/month):
- 4,000-5,000 full workflow calls (most AI interactions)
- OR 10,000+ intent classifications + lightweight analyses

**Cost Control**:
- Cache redundant program data (re-fetch only on changes)
- Batch related queries (e.g., all gate readiness in one call)
- Use simpler models (e.g., Opus 3.5 Sonnet) for deterministic operations
- Implement query deduplication (log queries, reuse recent responses within TTL)

---

## Error Handling

**Per-Stage**:

### Intent Classifier Errors
- **Invalid JSON response**: Retry with simpler prompt, fallback to `general_query`
- **Ambiguous intent**: Log confidence < 0.5, route to Status Synthesizer (safest)
- **Missing extracted params**: Continue without (gate_readiness works with all gates if no gate_id)

### Specialized Analyzer Errors
- **Missing data**: Gracefully skip that analyzer, route directly to Status Synthesizer
- **API call failure**: Catch exception, return error message to user (e.g., "Unable to analyze gate readiness at this time")
- **Malformed response**: Log full error, fallback to generic analysis

### Status Synthesizer Errors
- **Analysis data incomplete**: Work with available data, note gaps in response
- **Synthesis fails**: Return aggregated facts (metrics, status) without narrative

### Response Formatter Errors
- **Unresolved tokens**: Scan for {template} strings, replace with placeholder or error message
- **Missing recommendations**: Return empty list (better than error)
- **Metadata collection fails**: Omit metadata section (not critical)

**Retry Strategy**:
- Max 2 retries per node (exponential backoff: 1s, 2s)
- After 2 retries, log and continue (don't block user)
- Return partial response (what succeeded) with error note

**Observability**:
- Log all API calls to stdout (structured JSON): `{"node": "intent_classifier", "query": "...", "tokens": 350, "latency_ms": 450}`
- Track success rate per node (async, non-blocking)
- Alert on repeated failures (e.g., 3+ failures in 10 min)

---

## Current Implementation Status

### Phase 2 (Completed)
- ✅ FastAPI route stubs (`/ai/query`, `/ai/gate-readiness`, `/ai/scope-creep`, `/ai/summary`)
- ✅ Response type definitions (frontend types in sync)
- ✅ Seed data with realistic workstreams, gates, risks

### Phase 3 (Next)
- ❌ Implement StateGraph with 7 nodes
- ❌ Connect nodes to database queries (SQLAlchemy AsyncSession)
- ❌ Wire state schema to Claude API calls (langchain-anthropic)
- ❌ Test each node independently (unit tests with mock data)
- ❌ Test routing logic (conditional edges)
- ❌ Integration test: full workflows end-to-end
- ❌ Implement token budget tracking (optional, log-only at first)
- ❌ Load test (simulate 100 concurrent queries, measure latency)

### Phase 4 (Future)
- ❌ Query deduplication + caching (Redis TTL)
- ❌ Streaming responses (Server-Sent Events to frontend for long-running analyses)
- ❌ Fine-tuned model for Waypoint-specific queries
- ❌ Custom evaluators for response quality (automated vs manual)

---

## Integration with Frontend

**AI Chat Widget** (CommandCenter):
- User enters query → POST `/api/v1/ai/query`
- Shows loading spinner while StateGraph executes
- Displays response text in chat panel
- Shows 3-5 recommendations as bulleted list
- Displays sources as gray tags (e.g., "workstream: agentops")

**Specialized Endpoints** (used by specific pages):
- `/api/v1/ai/gate-readiness/{gate_id}` → GateTimeline uses for detailed status
- `/api/v1/ai/scope-creep` → RiskHeatMap or Dashboard alerts
- `/api/v1/ai/summary` → CommandCenter executive summary section

---

## Example Workflow

**User Query**: "Are we on track for Gate 1?"

**Flow**:
1. **Intent Classifier**: Identifies `gate_readiness`, extracts gate_id=1
2. **Gate Readiness Assessor**: Fetches gate 1 data, analyzes exit criteria (6/10 complete), checks workstreams (5 on-track, 1 at-risk), assesses confidence (70%)
3. **Status Synthesizer**: Contextualizes result ("Gate 1 is on track but depends on 2 critical deliverables from AgentOps workstream"), highlights blocker if any
4. **Response Formatter**: Returns:
```json
{
  "query": "Are we on track for Gate 1?",
  "intent": "gate_readiness",
  "response": "Gate 1 is on track (60% of exit criteria complete). 5 of 6 workstreams are on schedule. At-risk: Platform workstream (depends on API finalization from AWS). No blockers currently, but recommend confirming AWS API delivery by Friday.",
  "recommendations": [
    "Confirm AWS API delivery timeline (due Friday 3/31)",
    "Schedule Platform workstream sync Monday to address dependencies",
    "Escalate if AWS timeline slips beyond Gate 1 start date"
  ],
  "sources": ["gate:1", "workstream:platform", "dependency:aws->platform"],
  "confidence": 0.7
}
```

5. **Frontend**: Displays response in chat, highlights recommendations, links to Platform workstream and dependency graph.

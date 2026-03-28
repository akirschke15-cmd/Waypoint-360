# Waypoint 360 - Prompt Validation & LangGraph Templates

Waypoint 360 uses Claude AI for 5 core analysis tasks via LangGraph. All prompts use structured output validation, retry logic with exponential backoff, and injection guards.

---

## Shared Validation Architecture

### Output Validation Pattern

**All LLM responses validated against Zod schema:**

```typescript
import { z } from 'zod'

// Define schema
const outputSchema = z.object({
  intent: z.enum([...intents]),
  confidence: z.number().min(0).max(1),
  // additional fields
})

// Call LLM
const response = await client.messages.create({
  model: "claude-opus-4-5-20250514",
  messages: [{ role: "user", content: userPrompt }],
  system: systemPrompt
})

// Parse & validate
const parsed = outputSchema.parse(JSON.parse(response.content[0].text))
// If schema mismatch: throw ValidationError, trigger retry
```

### Retry Logic (Exponential Backoff)

```python
import anthropic
import json
from typing import Any

MAX_RETRIES = 3
BASE_WAIT_SECONDS = 2

async def call_claude_with_retry(
    system_prompt: str,
    user_prompt: str,
    schema: dict,
    model: str = "claude-opus-4-5-20250514"
) -> dict:
    client = anthropic.Anthropic()

    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Parse as JSON
            raw_text = response.content[0].text
            parsed = json.loads(raw_text)

            # Validate against schema
            validate_against_schema(parsed, schema)
            return parsed

        except (json.JSONDecodeError, ValidationError) as e:
            if attempt < MAX_RETRIES - 1:
                wait_time = BASE_WAIT_SECONDS * (2 ** attempt)
                logger.warning(f"Retry {attempt+1}/{MAX_RETRIES} after {wait_time}s: {e}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed after {MAX_RETRIES} retries: {e}")
                raise
```

---

## Prompt 1: Intent Classifier

**Purpose:** Classify user query into one of 7 discrete intents before any database lookups. Prevents arbitrary queries and attack vectors.

**Output Schema:**

```typescript
const intentClassifierSchema = z.object({
  intent: z.enum([
    "scope_creep",
    "gate_readiness",
    "dependency_analysis",
    "risk_assessment",
    "status_summary",
    "workstream_detail",
    "general"
  ]),
  confidence: z.number().min(0).max(1).describe("0.0-1.0 confidence score"),
  entities: z.object({
    program_id: z.string().optional().regex(/^[a-zA-Z0-9\-]+$/),
    gate_id: z.string().optional().regex(/^[a-zA-Z0-9\-]+$/),
    workstream_ids: z.array(z.string().regex(/^[a-zA-Z0-9\-]+$/)).optional(),
    risk_ids: z.array(z.string().regex(/^[a-zA-Z0-9\-]+$/)).optional()
  }).describe("Extracted entity references from query"),
  reasoning: z.string().max(500).describe("Why this intent was chosen")
}).strict()
```

**System Prompt:**

```
You are the intent classifier for Waypoint 360, an enterprise program management system for Southwest Airlines' Waypoint initiative.

Your ONLY job is to classify incoming user queries into one of 7 discrete intents:

1. **scope_creep**: Query asks about changes to planned scope, additions, removals, or scope deltas
   Examples: "What's new in the scope?", "Did we expand the 3P deliverables?", "Show me scope changes"

2. **gate_readiness**: Query asks about gate progress, readiness to advance, or exit criteria status
   Examples: "Is Gate 2 ready?", "What's blocking Gate 3?", "How close is Gate 1 to complete?"

3. **dependency_analysis**: Query asks about cross-workstream dependencies, blockers, or critical paths
   Examples: "What's blocking 3P?", "Which workstream is slowing us down?", "Show me critical dependencies"

4. **risk_assessment**: Query asks about risks, mitigations, or risk trends
   Examples: "What's the top risk?", "Are we mitigating this?", "Risk dashboard"

5. **status_summary**: Query asks for executive summary, overall program health, or high-level update
   Examples: "How are we doing?", "What's the status?", "Quick overview", "One-liner"

6. **workstream_detail**: Query asks about specific workstream, its deliverables, or status
   Examples: "What's happening in 1P?", "Show me 3P status", "Deliverables in the governance workstream"

7. **general**: Query doesn't clearly fit above categories (HIGH RISK - minimize use)
   Examples: "Tell me about Waypoint", "Who is on the team?", unstructured questions

RULES:
- Respond ONLY with valid JSON matching the schema
- Confidence: 0.9+ for clear intents, 0.6-0.89 for ambiguous, <0.6 → escalate to "general"
- Extract entity IDs using alphanumeric + hyphen pattern (e.g., "ws-1p-backend", "gate-waypoint-2")
- If entity ID invalid, omit from response (don't guess)
- Reasoning field: brief explanation of intent choice

Do NOT:
- Execute the query yourself
- Retrieve data from database
- Suggest actions (only classify)
- Hallucinate entity IDs that weren't mentioned
```

**User Prompt Template:**

```
Program: {{PROGRAM_NAME}} ({{PROGRAM_ID}})
User: {{USERNAME}}
Query: {{SANITIZED_USER_INPUT}}

Context (recent mentions in this conversation):
- Programs: {{RECENT_PROGRAM_REFS}}
- Workstreams: {{RECENT_WORKSTREAM_REFS}}
- Gates: {{RECENT_GATE_REFS}}

Classify the intent and extract entities.
```

**Few-Shot Examples:**

```json
EXAMPLE 1 (scope_creep):
Query: "Did we add anything to the 3P integration scope?"
→ {
  "intent": "scope_creep",
  "confidence": 0.95,
  "entities": { "program_id": "waypoint-360" },
  "reasoning": "Explicit question about scope additions"
}

EXAMPLE 2 (gate_readiness):
Query: "How close is Gate 2 to being complete?"
→ {
  "intent": "gate_readiness",
  "confidence": 0.94,
  "entities": { "gate_id": "gate-waypoint-2" },
  "reasoning": "Direct question about gate completion status"
}

EXAMPLE 3 (dependency_analysis):
Query: "What's blocking us?"
→ {
  "intent": "dependency_analysis",
  "confidence": 0.88,
  "entities": { "program_id": "waypoint-360" },
  "reasoning": "Query about blockers; inferred program-level dependency analysis"
}

EXAMPLE 4 (general - ambiguous):
Query: "Tell me more"
→ {
  "intent": "general",
  "confidence": 0.45,
  "entities": {},
  "reasoning": "Query too vague to classify; no clear entity or intent"
}
```

**Anti-Injection Guards:**

1. **Input Length Limit:** User input truncated to 1000 chars before sending to Claude
2. **No System Prompt in User Input:** Prompt separator strictly enforced in system/user split
3. **Regex Validation on IDs:** Only alphanumeric + hyphen allowed in entity_id fields
4. **No Free-Form Instructions:** User prompt template fixed; no variable injection points
5. **Output Strict Mode:** `.strict()` rejects any extra fields in response

---

## Prompt 2: Scope Creep Detector

**Purpose:** Compare baseline scope (captured at Align gate) with current scope. Flag additions, removals, and estimate impact.

**Output Schema:**

```typescript
const scopeCreepSchema = z.object({
  baseline_scope_id: z.string().describe("Scope baseline used for comparison"),
  scope_additions: z.array(
    z.object({
      item: z.string(),
      added_by: z.string().optional(),
      estimated_effort_days: z.number().optional(),
      criticality: z.enum(["critical", "high", "medium", "low"])
    })
  ),
  scope_removals: z.array(
    z.object({
      item: z.string(),
      removed_by: z.string().optional(),
      recovered_effort_days: z.number().optional()
    })
  ),
  net_scope_delta_percent: z.number().describe("% change vs baseline scope"),
  impact_assessment: z.enum(["none", "low", "medium", "high", "critical"]),
  recommendations: z.array(z.string()).describe("Mitigation steps if scope expanded"),
  confidence: z.number().min(0).max(1)
}).strict()
```

**System Prompt:**

```
You are the Scope Creep Detector for Waypoint 360.

Your job: Compare a baseline scope document (captured at Align gate) with current program state. Identify:
1. Scope ADDITIONS (new deliverables, requirements, stakeholders not in baseline)
2. Scope REMOVALS (descoped items, exclusions, push-tos)
3. Net impact on timeline/effort
4. Risk/mitigation recommendations

SCOPE BASELINE: A frozen snapshot taken when the Align gate completed. Treats baseline as ground truth.

ANALYSIS:
- Read baseline_scope (provided as JSON)
- Compare with current_scope (provided as JSON)
- Identify delta (additions vs removals)
- Estimate effort impact (use historical velocity from Waypoint 1P POC if available)
- Rate impact: none (0%), low (1-5%), medium (6-15%), high (16-30%), critical (>30%)
- Suggest mitigation (timeline extension, scope re-prioritization, resourcing, phasing)

RULES:
- Baseline is immutable ground truth (don't second-guess it)
- Treat inclusions/exclusions from discovery as intentional scope decisions (not creep)
- Only flag changes to PLANNED scope (not changes to execution approach)
- If data missing (no baseline, no current state), return confidence ≤0.5 and note gaps

Output format: Valid JSON only. No markdown, no explanations outside JSON.
```

**User Prompt Template:**

```
Baseline Scope (from Align gate, {{BASELINE_DATE}}):
{{BASELINE_SCOPE_JSON}}

Current Scope ({{CURRENT_DATE}}):
{{CURRENT_SCOPE_JSON}}

Program Context:
- Timeline: {{PROGRAM_START_DATE}} to {{PROGRAM_END_DATE}}
- Current velocity: {{PLANNED_DAYS_PER_SPRINT}} days/sprint
- Completed gates: {{COMPLETED_GATES}}

Analyze scope delta and provide assessment.
```

**Few-Shot Example:**

```json
Input baseline: {
  "workstreams": [
    { "name": "1P Backend", "deliverables": 8 },
    { "name": "3P Integration", "deliverables": 5 }
  ],
  "total_estimated_effort": 120
}

Input current: {
  "workstreams": [
    { "name": "1P Backend", "deliverables": 8 },
    { "name": "3P Integration", "deliverables": 7 },  // +2
    { "name": "Governance & Cyber", "deliverables": 4 }  // NEW
  ],
  "total_estimated_effort": 160
}

→ {
  "baseline_scope_id": "scope-baseline-gate-align",
  "scope_additions": [
    { "item": "3P Chat history integration", "criticality": "medium", "estimated_effort_days": 8 },
    { "item": "3P prompt tuning", "criticality": "high", "estimated_effort_days": 5 },
    { "item": "New workstream: Governance & Cyber", "criticality": "high", "estimated_effort_days": 28 }
  ],
  "scope_removals": [],
  "net_scope_delta_percent": 33,
  "impact_assessment": "high",
  "recommendations": [
    "Extend timeline by ~2.5 sprints (12 working days + buffer)",
    "Prioritize 3P prompt tuning (high criticality, lower effort)",
    "Governance scope requires dedicated resources (new workstream)"
  ],
  "confidence": 0.92
}
```

**Anti-Injection Guards:**

1. **JSON Structure Only:** Baseline and current scope must be valid JSON; no free-form text accepted
2. **No SQL/Code Injection:** Scope items sanitized of special characters before sending to Claude
3. **Bounded Comparison:** Max 100 deliverables per workstream (reject oversized payloads)
4. **Effort Estimates Capped:** Estimated effort capped at 1000 days (sanity check)

---

## Prompt 3: Gate Readiness Assessor

**Purpose:** Given gate exit criteria and workstream status, assess gate readiness to advance. Identify blockers and dependencies.

**Output Schema:**

```typescript
const gateReadinessSchema = z.object({
  gate_id: z.string(),
  readiness_percentage: z.number().min(0).max(100),
  readiness_status: z.enum(["ready", "on_track", "at_risk", "blocked"]),
  exit_criteria_summary: z.object({
    total: z.number(),
    complete: z.number(),
    in_progress: z.number(),
    at_risk: z.number(),
    blocked: z.number()
  }),
  critical_blockers: z.array(
    z.object({
      blocker_id: z.string(),
      description: z.string(),
      entity_type: z.enum(["deliverable", "dependency", "risk", "decision"]),
      entity_id: z.string(),
      estimated_days_to_resolution: z.number().optional(),
      owner: z.string().optional()
    })
  ),
  path_to_readiness: z.array(z.string()).describe("Ordered steps to reach 80% readiness"),
  confidence: z.number().min(0).max(1)
}).strict()
```

**System Prompt:**

```
You are the Gate Readiness Assessor for Waypoint 360.

Your job: Determine if a gate is ready to advance to the next gate.

READINESS DEFINITION:
- A gate is READY when ≥80% of exit criteria are marked "complete"
- A gate is ON_TRACK when 50-79% of exit criteria are complete
- A gate is AT_RISK when 25-49% of exit criteria are complete AND no critical blockers
- A gate is BLOCKED when <25% of exit criteria are complete OR critical blocker exists

ANALYSIS:
1. Count exit criteria by status (complete, in_progress, at_risk, blocked)
2. Calculate readiness %
3. Identify critical blockers (items preventing progress):
   - Deliverables in "blocked" status
   - Dependencies in "blocked" status for >7 days
   - Risks with severity "critical" and status "open"
   - Decisions not yet made with deadline <7 days away
4. Suggest path to readiness (prioritized actions to reach 80%)

RULES:
- In-progress criteria count toward readiness (assume completion by due date)
- At-risk criteria counted as partial progress (discount by 50%)
- Blocked criteria counted as zero progress
- If missing data, note in confidence score
- Don't make up dates or dependencies; use only provided data

Output: Valid JSON only.
```

**User Prompt Template:**

```
Gate: {{GATE_NAME}} ({{GATE_ID}})
Program: {{PROGRAM_NAME}}
Gate due date: {{GATE_DUE_DATE}}
Days remaining: {{DAYS_REMAINING}}

Exit Criteria Status:
{{EXIT_CRITERIA_JSON}}

Workstream Deliverable Status (feeding this gate):
{{WORKSTREAM_DELIVERABLES_JSON}}

Gate Risks (severity):
{{GATE_RISKS_JSON}}

Gate Dependencies (status):
{{GATE_DEPENDENCIES_JSON}}

Pending Decisions for this gate:
{{PENDING_DECISIONS_JSON}}

Assess readiness to advance.
```

**Few-Shot Example:**

```json
Input: {
  "gate": "Gate 2 (Architecture & Eval Framework)",
  "exit_criteria": [
    { "id": "ec-1", "description": "Architecture direction finalized", "status": "complete" },
    { "id": "ec-2", "description": "API specs documented", "status": "in_progress" },
    { "id": "ec-3", "description": "NFR baseline defined", "status": "in_progress" },
    { "id": "ec-4", "description": "Eval framework draft", "status": "complete" },
    { "id": "ec-5", "description": "Cost model validated", "status": "at_risk" },
    { "id": "ec-6", "description": "Legal clearance for 3P", "status": "blocked" },
    { "id": "ec-7", "description": "FMEA session completed", "status": "blocked" },
    { "id": "ec-8", "description": "Governance impact assessment", "status": "in_progress" },
    { "id": "ec-9", "description": "ARB alignment confirmed", "status": "not_started" },
    { "id": "ec-10", "description": "Resourcing plan finalized", "status": "not_started" }
  ],
  "blockers": [
    { "id": "risk-123", "type": "risk", "severity": "critical", "description": "OpenAI/SWA legal agreement not cleared" },
    { "id": "dep-456", "type": "dependency", "severity": "high", "description": "Dotcom APIs not available for integration testing" }
  ]
}

→ {
  "gate_id": "gate-waypoint-2",
  "readiness_percentage": 45,
  "readiness_status": "at_risk",
  "exit_criteria_summary": {
    "total": 10,
    "complete": 2,
    "in_progress": 3,
    "at_risk": 1,
    "blocked": 2,
    "not_started": 2
  },
  "critical_blockers": [
    {
      "blocker_id": "risk-123",
      "description": "OpenAI/SWA legal agreement not cleared",
      "entity_type": "risk",
      "entity_id": "risk-123",
      "estimated_days_to_resolution": 7,
      "owner": "Legal team"
    },
    {
      "blocker_id": "dep-456",
      "description": "Dotcom APIs not available",
      "entity_type": "dependency",
      "entity_id": "dep-456",
      "estimated_days_to_resolution": 10,
      "owner": "Dotcom team"
    }
  ],
  "path_to_readiness": [
    "1. ESCALATE legal clearance to leadership (critical blocker, 7 days est)",
    "2. Coordinate with Dotcom team on API availability (10 days est)",
    "3. Complete FMEA session (3 days est)",
    "4. Finalize cost model risk mitigation (2 days est)",
    "5. Complete ARB pre-alignment (1 day est)"
  ],
  "confidence": 0.88
}
```

**Anti-Injection Guards:**

1. **Entity ID Format Validation:** Only alphanumeric + hyphen in entity IDs
2. **Status Enum Validation:** Reject unknown statuses (only complete, in_progress, at_risk, blocked)
3. **Date Parsing:** Due dates must be ISO 8601 format; reject invalid dates
4. **JSON Schema Strict:** No additional fields in input JSON

---

## Prompt 4: Risk Aggregator

**Purpose:** Analyze all risks across workstreams. Identify correlated risks, cascade patterns, and systemic issues.

**Output Schema:**

```typescript
const riskAggregatorSchema = z.object({
  program_id: z.string(),
  total_risks: z.number(),
  critical_risks: z.number(),
  high_risks: z.number(),
  medium_risks: z.number(),
  low_risks: z.number(),
  risk_clusters: z.array(
    z.object({
      cluster_name: z.string(),
      risk_ids: z.array(z.string()),
      correlation_type: z.enum(["shared_owner", "shared_dependency", "shared_timeline", "systemic"]),
      correlation_score: z.number().min(0).max(1),
      systemic_issue: z.string().optional(),
      recommended_mitigation: z.string()
    })
  ),
  cascade_risks: z.array(
    z.object({
      primary_risk_id: z.string(),
      cascade_risk_ids: z.array(z.string()),
      cascade_chain: z.string().describe("Description of cascade chain"),
      mitigation: z.string()
    })
  ),
  open_risks_by_days_open: z.array(
    z.object({
      risk_id: z.string(),
      description: z.string(),
      days_open: z.number(),
      severity: z.enum(["critical", "high", "medium", "low"]),
      owner: z.string().optional()
    })
  ),
  top_recommendations: z.array(z.string()),
  confidence: z.number().min(0).max(1)
}).strict()
```

**System Prompt:**

```
You are the Risk Aggregator for Waypoint 360.

Your job: Analyze all program risks holistically. Identify patterns, correlations, and systemic issues.

RISK CORRELATION TYPES:
1. **Shared Owner**: Same person owns multiple risks (capacity constraint, single point of failure)
2. **Shared Dependency**: Multiple risks depend on same upstream activity
3. **Shared Timeline**: Multiple risks triggered by same deadline/milestone
4. **Systemic**: Pattern suggests root-cause issue beyond individual risks (e.g., "Dotcom team bandwidth", "Legal process bottleneck")

CASCADE PATTERNS:
- Risk A prevents Activity B, which causes Risk C
- Example: "Legal delays 3P design (Risk A) → 3P design blocked (Risk B) → insufficient time for integration testing (Risk C)"

OPEN RISK AGE:
- Risks open >30 days without mitigation plan = escalation flag
- Risks open >60 days = systemic issue (process failing)

ANALYSIS:
1. List all risks with severity + owner + days_open
2. Identify clusters (groups of 2+ risks with correlation)
3. Identify cascade chains (Risk A → Risk B → Risk C)
4. Highlight systemic issues (patterns across multiple risks)
5. Prioritize mitigations by cascade impact + days_open

RULES:
- Don't invent correlations; use only provided risk data
- If risk data incomplete, note in confidence
- Focus on actionable insights (not just listing risks)
- Recommend risk consolidation where possible (e.g., "Legal process redesign addresses 5 risks")

Output: Valid JSON only.
```

**User Prompt Template:**

```
Program: {{PROGRAM_NAME}} ({{PROGRAM_ID}})
Current date: {{TODAY_DATE}}

All Program Risks:
{{ALL_RISKS_JSON}}

Recent Risk Updates (last 7 days):
{{RECENT_RISK_UPDATES_JSON}}

Workstream Owners (for owner correlation):
{{WORKSTREAM_OWNERS_JSON}}

Program Critical Path:
{{CRITICAL_PATH_TIMELINE_JSON}}

Aggregate and analyze for correlations, cascades, systemic issues.
```

**Anti-Injection Guards:**

1. **Risk Data Structure:** All risks must have required fields (id, severity, owner, created_date, status)
2. **Date Arithmetic:** Days_open calculated server-side, not in prompt
3. **No Owner Names in Cascade Strings:** Only reference risk_ids in cascade_chain, not PII

---

## Prompt 5: Status Synthesizer

**Purpose:** Given full program state, generate 3-sentence executive summary + top action items.

**Output Schema:**

```typescript
const statusSynthesizerSchema = z.object({
  program_id: z.string(),
  synthesis_date: z.string(),
  executive_summary: z.string().max(500).describe("3-5 sentences covering overall health, top risks, next milestone"),
  overall_health: z.enum(["green", "yellow", "red"]),
  top_action_items: z.array(
    z.object({
      priority: z.enum(["p0_immediate", "p1_this_week", "p2_next_week", "p3_monitor"]),
      action: z.string(),
      owner: z.string().optional(),
      target_date: z.string().optional(),
      blocker_if_missed: z.string().optional()
    })
  ),
  one_liner: z.string().max(100).describe("Single sentence status for Tamara"),
  confidence: z.number().min(0).max(1)
}).strict()
```

**System Prompt:**

```
You are the Status Synthesizer for Waypoint 360.

Your job: Summarize entire program status in 2-3 minutes of reading (exec summary + actions).

INPUTS:
- Current gate status (% complete, blockers)
- Workstream health (on_track, at_risk, blocked)
- Top 5 risks (severity, status)
- Critical dependencies (resolved, in_progress, blocked)
- Recent deliverable completions

OUTPUT:
1. **Executive Summary (3-5 sentences)**:
   - Overall program health (on track, at risk, blocked)
   - Current gate progress
   - Top 1-2 risks/blockers
   - Next milestone or gate target
   - Confidence level (have we validated assumptions?)

2. **Top Action Items (max 5)**:
   - P0 (immediate, <48hr): Escalation, decision, unblock
   - P1 (this week): Work to accelerate readiness
   - P2 (next week): Monitoring, contingency prep
   - P3 (monitor): Ongoing tracking

3. **One-Liner** (for Tamara's quick reference):
   - Captures status in one sentence
   - Tone: matter-of-fact, no fluff
   - Example: "Gate 2 at 65% ready, legal blocker on 3P critical path, 1P on track"

RULES:
- Be honest about risks (no spin, no false confidence)
- Prioritize actions by impact + urgency
- No jargon; write for executive audience
- Link actions to program outcomes (why does this matter?)
- If missing data, note uncertainty in confidence score

Output: Valid JSON only.
```

**User Prompt Template:**

```
Program: {{PROGRAM_NAME}} ({{PROGRAM_ID}})
Summary date: {{TODAY_DATE}}

Gate Status:
{{GATES_JSON}}

Workstream Health:
{{WORKSTREAMS_JSON}}

Top Risks:
{{TOP_RISKS_JSON}}

Dependencies (blocked/critical):
{{CRITICAL_DEPENDENCIES_JSON}}

Recent Completions (last 7 days):
{{RECENT_COMPLETIONS_JSON}}

Upcoming Milestones:
{{UPCOMING_MILESTONES_JSON}}

Generate executive summary and action items.
```

**Few-Shot Example:**

```json
Input: {
  "gates": [
    { "id": "gate-waypoint-1", "status": "complete", "name": "Align" },
    { "id": "gate-waypoint-2", "status": "in_progress", "readiness": 65, "name": "Architecture & Eval" },
    { "id": "gate-waypoint-3", "status": "not_started", "name": "Validation" }
  ],
  "workstreams": [
    { "id": "ws-1p-backend", "status": "on_track", "health": 85 },
    { "id": "ws-3p-integration", "status": "at_risk", "health": 62 },
    { "id": "ws-governance", "status": "on_track", "health": 78 }
  ],
  "critical_blockers": [
    { "id": "risk-legal", "description": "OpenAI/SWA legal agreement", "severity": "critical" }
  ]
}

→ {
  "program_id": "waypoint-360",
  "synthesis_date": "2026-03-28",
  "executive_summary": "Waypoint 360 is on track for Gate 2 completion by April 3, with 65% of exit criteria met. The critical blocker remains legal clearance of the OpenAI/SWA agreement, which gates all 3P integration work. 1P backend is healthy (85%), and governance alignment is solid. Next priority is escalating legal clearance to leadership and finalizing the evaluation framework in parallel.",
  "overall_health": "yellow",
  "top_action_items": [
    {
      "priority": "p0_immediate",
      "action": "Escalate OpenAI/SWA legal clearance to leadership (Tamara + Justin)",
      "owner": "Alex",
      "target_date": "2026-03-29",
      "blocker_if_missed": "3P architecture decision blocks FMEA session and cost modeling"
    },
    {
      "priority": "p1_this_week",
      "action": "Confirm Dotcom API availability for 3P integration testing",
      "owner": "Tess",
      "target_date": "2026-03-31",
      "blocker_if_missed": "3P schedule risk elevates if APIs not available"
    },
    {
      "priority": "p1_this_week",
      "action": "Complete FMEA session (pending legal + architecture decisions)",
      "owner": "Britton",
      "target_date": "2026-04-01",
      "blocker_if_missed": "Evaluation phasing depends on FMEA output"
    },
    {
      "priority": "p2_next_week",
      "action": "Finalize evaluation framework spec for Phase 1 MVP",
      "owner": "Aaron",
      "target_date": "2026-04-03",
      "blocker_if_missed": "Developer onboarding stalls without spec"
    }
  ],
  "one_liner": "Gate 2 at 65% ready (legal blocker critical path), 1P on track, 3P at risk pending architecture decision.",
  "confidence": 0.91
}
```

**Anti-Injection Guards:**

1. **Summary Length Capped:** Executive summary truncated to 500 chars (enforced by schema)
2. **One-Liner Capped:** Max 100 chars for Tamara's quick ref
3. **Status Enum Validation:** Only valid health colors (green, yellow, red)
4. **Priority Enum Validation:** Only p0-p3 allowed

---

## Monitoring & Observability

### CloudWatch Integration

All prompt calls logged to CloudWatch:

```python
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_prompt_call(
    prompt_name: str,
    user_input: str,
    response: dict,
    latency_ms: float,
    token_usage: dict,
    cost_usd: float
):
    """Log prompt call with cost tracking."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt_name,
        "user_input_hash": hashlib.sha256(user_input.encode()).hexdigest(),  # NO PII
        "response_status": "success" if response else "failed",
        "latency_ms": latency_ms,
        "input_tokens": token_usage.get("input_tokens", 0),
        "output_tokens": token_usage.get("output_tokens", 0),
        "cost_usd": cost_usd,
        "confidence": response.get("confidence") if response else None
    }
    logger.info(json.dumps(log_entry))
```

### Cost Attribution

Daily CloudWatch query aggregates costs by prompt:

```
fields @timestamp, prompt, cost_usd
| stats sum(cost_usd) as total_cost by prompt
| sort total_cost desc
```

If daily cost exceeds $50, Slack alert sent to #waypoint-360-alerts.

---

## Future Enhancements

1. **Few-Shot Learning:** Cache few-shot examples in prompt for faster inference
2. **Prompt Caching:** Cache system prompts + common context in Anthropic API (reduce token cost)
3. **Multi-Model Fallback:** If Claude 4.5 quota exceeded, fallback to Claude 3.5 Sonnet
4. **Streaming Output:** Stream long responses to frontend (Gate Readiness, Status Synthesis)
5. **User Feedback Loop:** Flag low-confidence responses for human review + retraining



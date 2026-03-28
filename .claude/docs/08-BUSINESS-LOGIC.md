# Waypoint 360 - Business Logic

## State Machines

All entities use explicit finite state machines to enforce valid transitions. Transitions may include guard conditions (e.g., all exit criteria complete before advancing gate). Regressions allowed where specified (e.g., at_risk → on_track).

---

### Program Lifecycle

```
planning
  ├─ start_execution → active (no guard)
  ├─ pause → on_hold
  └─ cancel → complete

active
  ├─ pause → on_hold (no guard)
  ├─ resume_from_hold → active (from on_hold only)
  ├─ complete → complete
  └─ cancel → complete (can cancel mid-execution)

on_hold
  ├─ resume_from_hold → active (no guard)
  ├─ cancel → complete
  └─ (no auto-transition)

complete
  └─ (terminal state; no transitions)

Regressions: on_hold → active (allowed), complete → active (not allowed)
```

**Guard Conditions:**
- `start_execution`: Requires Gate 1 at minimum (Program.gates.count ≥ 1)
- `complete`: Requires all gates at "complete" status
- `pause`: Allowed from any active state

**Triggers:**
- User action: Admin clicks "Start Program"
- Automatic: None (manual state management)

---

### Gate Lifecycle

```
not_started
  ├─ begin → in_progress (no guard)
  └─ (can be skipped if marked "not applicable")

in_progress
  ├─ flag_risk → at_risk (guard: at least 1 risk exists)
  ├─ flag_blocker → blocked (guard: at least 1 dependency blocked)
  ├─ complete → complete (guard: ≥80% exit criteria complete)
  └─ (stay in progress)

at_risk
  ├─ mitigate → in_progress (guard: risk severity reduced below threshold)
  ├─ escalate → blocked (guard: risk becomes critical)
  └─ complete → complete (guard: risks mitigated + ≥80% exit criteria)

blocked
  ├─ unblock → at_risk (guard: blocking dependency resolved)
  ├─ escalate → blocked (can remain blocked with multiple reasons)
  └─ (no auto-recovery; manual intervention required)

complete
  ├─ regress → in_progress (allowed if re-opened by Admin)
  └─ (terminal unless reopened)

Regressions: at_risk ↔ in_progress (bidirectional), blocked → at_risk (allowed)
```

**Guard Conditions:**
- `complete`: GateExitCriteria.status count where "complete" ≥ 80% of total
- `flag_risk`: Gate.risks.count ≥ 1 AND risk.severity in [critical, high]
- `flag_blocker`: Gate.dependencies.count ≥ 1 AND dependency.status == "blocked"
- `mitigate`: Risk score decreases by ≥30 points OR risk severity moves from critical → high

**Automatic Transitions (Daily Scheduler):**
- If all child workstreams reach "complete", parent gate auto-advances to "complete" (notification sent)
- If any workstream regresses to "at_risk", gate auto-regresses to "at_risk" (notification sent)

---

### Workstream Lifecycle

```
not_started
  ├─ kickoff → on_track (no guard)
  └─ (awaiting project start)

on_track
  ├─ flag_risk → at_risk (guard: deliverable stuck >2 sprint cycles)
  ├─ flag_blocker → blocked (guard: critical dependency blocked)
  └─ (stay on track)

at_risk
  ├─ mitigate → on_track (guard: blocker resolved OR deliverable deadline extended)
  ├─ escalate → blocked (guard: multiple deliverables past due)
  └─ (stay at risk)

blocked
  ├─ unblock → at_risk (guard: blocking dependency resolved)
  └─ (escalation required to proceed)

complete
  ├─ regress → on_track (allowed if workstream reopened)
  └─ (terminal unless reopened by Admin)

Regressions: at_risk ↔ on_track (bidirectional), blocked → at_risk (allowed)
```

**Guard Conditions:**
- `flag_risk`: Any deliverable.status == "at_risk" OR "blocked" for >2 sprint cycles (14 days)
- `flag_blocker`: Workstream.dependencies.count ≥ 1 AND dependency.status == "blocked"
- `complete`: All deliverables.status == "complete"
- `mitigate`: Workstream.risks.count == 0 AND all blocked dependencies resolved

**Automatic Transitions (Daily Scheduler):**
- If all deliverables reach "complete", workstream auto-advances to "complete"
- If any deliverable regresses to "at_risk", workstream auto-regresses to "at_risk"

---

### Deliverable Lifecycle

```
not_started
  ├─ start_work → in_progress (no guard)
  └─ (awaiting assignment)

in_progress
  ├─ flag_risk → at_risk (guard: work >50% complete, deadline at risk)
  ├─ flag_blocker → blocked (guard: blocker dependency encountered)
  ├─ complete → complete (guard: acceptance criteria met)
  └─ (stay in progress)

at_risk
  ├─ mitigate → in_progress (guard: deadline extended OR scope reduced)
  ├─ escalate → blocked (guard: critical blocker encountered)
  └─ (stay at risk)

blocked
  ├─ unblock → at_risk (guard: blocker dependency resolved)
  └─ (escalation required to proceed)

complete
  ├─ regress → in_progress (allowed if rework required)
  └─ (terminal unless reopened)

Regressions: at_risk ↔ in_progress (bidirectional), blocked → at_risk (allowed)
```

**Guard Conditions:**
- `flag_risk`: Deliverable completion_percentage ≥ 50 AND (due_date - today ≤ 7 days)
- `complete`: Deliverable.acceptance_criteria_met == True AND assigned_owner approves
- `flag_blocker`: Deliverable.blockers.count ≥ 1 AND blocker.severity == critical

---

### Risk Lifecycle

```
open
  ├─ mitigate → mitigated (guard: mitigation plan documented + owner assigned)
  ├─ escalate → open (severity increases, no state change)
  └─ (stay open)

mitigated
  ├─ revert → open (guard: mitigation ineffective, risk re-emerges)
  ├─ accept → accepted (guard: mitigation cost > residual risk)
  └─ close → closed (guard: risk eliminated OR outside scope)

accepted
  ├─ close → closed (guard: contingency plan triggered if risk occurs)
  └─ (await risk event or end of program)

closed
  └─ (terminal; no transitions)

Regressions: mitigated → open (allowed), accepted → open (allowed)
```

**Guard Conditions:**
- `mitigate`: Risk.mitigation_plan not null AND Risk.mitigation_owner_id not null
- `accept`: Mitigation cost estimate ≥ residual risk impact
- `close`: Risk.closure_rationale not null

**Automatic Transitions:**
- If risk's parent gate reaches "complete", risk auto-closes (if status != closed)

---

### Decision Lifecycle

```
needed
  ├─ assign_owner → pending (guard: owner assigned from RACI matrix)
  └─ (awaiting decision ownership)

pending
  ├─ decide → made (guard: decision rationale + stakeholder sign-off)
  ├─ defer → deferred (guard: decision deadline extended)
  └─ (stay pending)

made
  ├─ revert → pending (guard: new information warrants reconsideration)
  └─ (decision final)

deferred
  ├─ revisit → pending (guard: deferred deadline arrives OR trigger event occurs)
  └─ (awaiting revisit condition)

Regressions: made → pending (allowed with rationale), deferred → pending (allowed)
```

**Guard Conditions:**
- `decide`: Decision.owner_id not null AND stakeholder_signoff_count ≥ required_count
- `defer`: new_decision_deadline > current_decision_deadline

---

### Dependency Lifecycle

```
open
  ├─ start_tracking → in_progress (guard: upstream workstream begins execution)
  └─ (awaiting upstream start)

in_progress
  ├─ resolve → resolved (guard: upstream deliverable complete)
  ├─ block → blocked (guard: upstream delayed >7 days beyond plan)
  └─ (stay in progress)

resolved
  └─ (terminal; dependency satisfied)

blocked
  ├─ escalate → blocked (severity increases, no state change)
  ├─ unblock → in_progress (guard: upstream workstream resumes)
  └─ (await escalation or unblock)

Regressions: blocked → in_progress (allowed), in_progress ↔ blocked (bidirectional if delta <7 days)
```

**Guard Conditions:**
- `block`: Today - upstream_due_date > 7 days
- `resolve`: Upstream deliverable status == "complete"

---

### GateExitCriteria Lifecycle

```
not_started
  ├─ begin_work → in_progress (guard: no guard)
  └─ (awaiting team assignment)

in_progress
  ├─ meet_criteria → complete (guard: acceptance_evidence submitted + owner validated)
  ├─ flag_risk → at_risk (guard: criteria on path to failure)
  └─ (stay in progress)

at_risk
  ├─ mitigate → in_progress (guard: risk mitigation plan assigned)
  ├─ miss_criteria → complete (guard: criteria waived by gate lead)
  └─ (stay at risk)

complete
  └─ (terminal; criteria met or waived)

Regressions: complete → in_progress (allowed if evidence invalidated), at_risk ↔ in_progress
```

**Guard Conditions:**
- `meet_criteria`: Acceptance_evidence not null AND evidence_validated_by_owner == True
- `miss_criteria`: Gate.lead approval required + waiver_rationale documented

---

### ScopeChange Lifecycle

```
flagged
  ├─ submit_for_review → reviewed (guard: change description + business_justification)
  └─ (awaiting review slot)

reviewed
  ├─ approve → approved (guard: gate lead + PM sign-off)
  ├─ request_revision → flagged (guard: feedback provided to submitter)
  └─ reject → rejected (guard: rejection rationale documented)

approved
  ├─ deploy_change → deployed (guard: change implemented + artifacts updated)
  └─ (awaiting implementation)

rejected
  └─ (terminal; change not proceeding)

deployed
  └─ (terminal; change complete)

Regressions: approved → flagged (allowed if implementation blocked), reviewed → flagged
```

**Guard Conditions:**
- `submit_for_review`: change_description not null AND business_justification not null
- `approve`: reviewed_by_gate_lead == True AND reviewed_by_pm == True
- `deploy_change`: approved_at not null AND implementation_complete == True

---

## Scoring / Ranking Algorithms

### Gate Readiness Score

**Formula:**
```
readiness_score = (exit_criteria_complete / exit_criteria_total) * 100

Status determination:
  - readiness_score ≥ 80% → "Ready for Advance"
  - readiness_score 50-79% → "On Track"
  - readiness_score 25-49% → "At Risk"
  - readiness_score < 25% → "Blocked"
```

**Example:**
- Gate 2 has 10 exit criteria
- 8 marked "complete", 2 marked "in_progress"
- Score: (8 / 10) * 100 = 80%
- Status: "Ready for Advance"

**Input to Calculation:**
- `GateExitCriteria` query filtered by gate_id
- Count where status == "complete"
- Divide by total count
- Multiply by 100

---

### Risk Severity Matrix

**Severity × Likelihood = Risk Score:**

| Likelihood \ Severity | Critical (4) | High (3) | Medium (2) | Low (1) |
|----------------------|-------------|---------|-----------|---------|
| Very High (5)        | 20 (red)    | 15 (red)| 10 (yellow) | 5 (green) |
| High (4)             | 16 (red)    | 12 (red)| 8 (yellow) | 4 (green) |
| Medium (3)           | 12 (red)    | 9 (orange) | 6 (yellow) | 3 (green) |
| Low (2)              | 8 (orange)  | 6 (yellow) | 4 (green) | 2 (green) |
| Very Low (1)         | 4 (green)   | 3 (green) | 2 (green) | 1 (green) |

**Risk Color Coding:**
- **Red (≥15):** Critical, immediate escalation required
- **Orange (9-14):** High, requires mitigation plan
- **Yellow (5-8):** Medium, monitor closely
- **Green (<5):** Low, accept as is

**Gate Status Trigger (Automatic):**
- If any risk score ≥ 15, gate auto-regresses to "at_risk" (if not already blocked)
- If critical risk unmitigated >7 days, gate auto-regresses to "blocked"

---

### Workstream Health Score

**Formula:**
```
health_score = (deliverable_completion * 0.5) + (risk_mitigation * 0.3) + (dependency_resolution * 0.2)

where:
  deliverable_completion = (deliverables_complete / deliverables_total) * 100
  risk_mitigation = (1 - (open_risks / total_risks)) * 100  [capped at 100]
  dependency_resolution = (resolved_dependencies / total_dependencies) * 100  [capped at 100]

Status:
  - score ≥ 80: on_track (green)
  - score 50-79: at_risk (yellow)
  - score < 50: blocked (red)
```

**Example:**
- Deliverable completion: 60% (6/10 complete)
- Open risks: 2 of 5 = 60% mitigated
- Resolved dependencies: 8 of 10 = 80% resolved

Score = (60 * 0.5) + (60 * 0.3) + (80 * 0.2) = 30 + 18 + 16 = 64

Status: "at_risk" (yellow)

---

### Deliverable Priority Ranking

**Scoring (0-100):**

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Criticality to Gate | 30% | User-provided 1-5 score × 20 |
| Deadline Proximity | 25% | (1 - days_remaining / planned_days) × 100, capped 0-100 |
| Blocker Count | 20% | (blocker_count / max_blockers) × 100, capped 0-100 |
| Dependencies Met | 15% | (resolved_deps / total_deps) × 100, capped 0-100 |
| Risk Exposure | 10% | max_risk_score / 20 × 100, capped 0-100 |

**Example:**
- Deliverable marked "critical to gate" (5) = 30 × (5/5) = 30 points
- 10 days remaining of 30 planned = (1 - 10/30) × 100 × 0.25 = 16.7 points
- 2 blockers of max 5 = (2/5) × 100 × 0.20 = 8 points
- 3 resolved of 4 dependencies = (3/4) × 100 × 0.15 = 11.3 points
- Max risk score 12 of 20 = (12/20) × 100 × 0.10 = 6 points

**Total: 30 + 16.7 + 8 + 11.3 + 6 = 72 points**

**Rank:** High priority (top quartile if score ≥ 70)

---

## Notification Events

### Event Catalog

| Event | Trigger | Recipients | Channel | Frequency |
|-------|---------|-----------|---------|-----------|
| **Gate Readiness Alert** | Gate reaches ≥80% exit criteria complete | Gate lead, Program manager, Admin | Slack + Email | On state change |
| **Gate Regression** | Gate regresses from complete/at_risk to blocked | Gate lead, skip-level manager, Admin | Slack (urgent) + Email | On state change |
| **Workstream at Risk** | Workstream.status changes to at_risk | Workstream owner, PM, Admin | Slack + Email | On state change |
| **Workstream Blocked** | Workstream.status changes to blocked | Workstream owner, PM, skip-level, Admin | Slack (urgent) + Email | On state change |
| **Deliverable Overdue** | Deliverable past due_date, status not complete | Deliverable owner, workstream owner, Admin | Slack (daily reminder) | Daily, 9am PT |
| **Critical Risk Flagged** | Risk score ≥ 15 (critical severity) | Gate lead, risk owner, Admin | Slack (urgent) + SMS | On state change |
| **Risk Escalation** | Risk moves from mitigated → open | Risk owner, gate lead, Admin | Slack + Email | On state change |
| **Blocker Dependency** | Dependency.status changes to blocked | Upstream owner, downstream owner, Admin | Slack + Email | On state change |
| **Dependency Resolved** | Dependency.status changes to resolved | Downstream owner, workstream owner, Admin | Slack | On state change |
| **Decision Overdue** | Decision pending >decision_deadline | Decision owner, gate lead, Admin | Slack + Email | Daily at 9am PT |
| **Scope Change Flagged** | ScopeChange.status = flagged (user or AI flagged) | Gate lead, PM, Admin | Slack | On creation |
| **Scope Change Approved** | ScopeChange.status = approved | Affected workstream owners, Admin | Slack | On state change |
| **AI Analysis Complete** | Scope creep / gate readiness / risk aggregation analysis finishes | Requesting user, Admin | In-app toast + Slack | On completion |
| **Daily Status Summary** | Scheduled daily report | Tamara (skip-level), program leads | Email + Slack | 8am PT daily |

### Notification Configuration

**Slack Integration:**
- Webhook URL: `SLACK_WEBHOOK_URL` (environment variable)
- Channel: `#waypoint-360-alerts` (default; user-configurable)
- Formatting: Blocks API for structured layout
- Urgency levels: Critical (red), High (orange), Medium (yellow), Low (blue)

**Email Integration:**
- SMTP server: `SMTP_SERVER` (environment variable)
- From address: `waypoint360-alerts@southwest.com`
- Template: HTML with logo, context, action links
- Recipient: role-based (gate lead, PM, admin)

**In-App Notifications:**
- Toast message (top-right, 5-second auto-dismiss)
- Notification bell icon with unread count
- Notification center sidebar (expandable)
- Rich preview (entity name, new status, action button)

### Opt-Out / Preferences

**Future Enhancement (Phase 2):**
- User notification preferences dashboard
- Per-event opt-out (e.g., "Don't notify me of daily summaries")
- Notification digest consolidation (hourly, daily, weekly)
- Do-not-disturb windows (e.g., 6pm-8am no Slack)

---

## Business Rule Enforcement

### Immutable Rules (Hard Constraints)

1. **Gate must have ≥1 workstream** — Cannot create empty gate
2. **Workstream must have ≥1 deliverable** — Cannot create empty workstream
3. **Exit criteria must belong to gate** — Cannot assign criteria from another gate
4. **Risk owner must be SWA employee** — Cannot assign to external user
5. **Deliverable cannot complete until blockers resolved** — Cannot mark complete if blocked status
6. **Decision cannot be made without sign-off** — Cannot mark made if stakeholder_signoff_count < required_count
7. **Program cannot complete until all gates complete** — Cannot mark complete if any gate not complete

### Soft Constraints (Warnings, Allowed Override)

1. **Deadline approaching** — Warning if ≤7 days to deliverable due_date
2. **Scope change late in gate** — Warning if change submitted in final 10% of gate timeline
3. **Risk remains open >14 days** — Warning, escalate to skip-level if >30 days
4. **Deliverable blocked >7 days** — Warning to workstream owner, escalate to PM if >14 days
5. **Dependency chain >3 levels deep** — Warning of hidden critical path
6. **High-risk decision with <24hr review** — Warning, allow override with VP sign-off

---

## Concurrency & Data Consistency

### Optimistic Locking

All mutable entities include a `version` field (integer, incremented on each write):

```python
class Workstream(Base):
    id: str
    name: str
    status: WorkstreamStatus
    version: int  # Optimistic lock field
    updated_at: datetime

# On update attempt:
# IF current.version != submitted.version:
#   RAISE ConflictError("Workstream updated by another user")
# ELSE:
#   Save with version += 1
```

**Benefit:** Prevents lost updates when two users edit same entity simultaneously.

### Eventual Consistency (Automatic State Propagation)

Daily scheduler job (9am PT) runs:
- Gate auto-advance: If all workstreams complete → gate complete
- Gate auto-regress: If any workstream at_risk/blocked → gate regresses
- Workstream auto-advance: If all deliverables complete → workstream complete
- Workstream auto-regress: If any deliverable at_risk/blocked → workstream regresses
- Risk auto-close: If parent gate complete and risk status != closed → auto-close

**Rationale:** Users update deliverable status; parent statuses follow automatically within 24 hours.



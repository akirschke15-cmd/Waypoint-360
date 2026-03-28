# Waypoint 360 - Data Models

## Schema Overview

Waypoint 360 uses SQLAlchemy 2.0 ORM with async support. Database supports SQLite (dev) and PostgreSQL (production). All models inherit from `TimestampMixin` (provides `id: int PK`, `created_at: datetime`, `updated_at: datetime`). Relationships use cascade delete-orphan for hierarchical data (Program → Phases → Gates).

## Entity Relationship Diagram

```
┌─────────────┐
│  Program    │ (1)
│ ─────────── │
│ id (PK)     │
│ name        │
│ description │
│ start_date  │
│ end_date    │
│ status      │
│ created_at  │
│ updated_at  │
└─────────────┘
      │ (1)
      ├──────────────────┬─────────────────┐
      │ (N)              │ (N)              │ (N)
┌───────────┐  ┌──────────────┐  ┌──────────────┐
│  Phase    │  │   Gate       │  │ Workstream   │
│ ────────  │  │ ───────────  │  │ ────────────  │
│ id (PK)   │  │ id (PK)      │  │ id (PK)      │
│ program_id├──┤ program_id ──┤  │ program_id ──┤
│ name      │  │ phase_id     │  │ name         │
│ description│ │ name         │  │ short_name   │
│ start_week│  │ short_name   │  │ purpose      │
│ end_week  │  │ description  │  │ scope_in     │
│ goal      │  │ week_number  │  │ scope_out    │
│ key_activities│ due_date    │  │ baseline_scope│
│ exit_criteria │ status      │  │ owner_id ──┐ │
│ sort_order│  │ sort_order   │  │ status      │ │
└───────────┘  └──────────────┘  │ sort_order  │ │
      │ (1)              │ (1)    └──────────────┘ │
      │                  │              │          │
      │                  │       ┌──────┘          │
      │         ┌────────┘       │ (1)             │
      │         │ (N)            │                 │
      │    ┌─────────────────┐   │  ┌──────────┐   │
      │    │GateExitCriteria │   │  │  Person  │<──┤
      │    │────────────────│   │  │ ────────  │   │
      │    │id (PK)         │   │  │ id (PK)  │   │
      │    │gate_id ────────┤   │  │ name     │   │
      │    │description     │   │  │ email    │   │
      │    │status          │   │  │ role     │   │
      │    │notes           │   │  │ title    │   │
      │    │sort_order      │   │  │ team     │   │
      │    └─────────────────┘   │  │ organization│
      │                          │  │ capacity_pct│
      │                          │  │ workstream_id├┐
      │                          │  │ hashed_password
      │                          │  └──────────────┘
      │                          │
      └──────────────┬───────────┘ (N workstreams per gate)
                     │
      ┌──────────────┴──────────────┬─────────────────┐
      │                             │                 │
  ┌──────────────┐         ┌─────────────────┐ ┌──────────┐
  │ Deliverable  │         │    Risk         │ │Decision  │
  │ ────────────│         │────────────────│ │────────  │
  │ id (PK)     │         │ id (PK)        │ │ id (PK) │
  │ workstream_id├────┐    │ workstream_id ─┤ │ workstream_id─┐
  │ gate_id ────┤────┼──┐ │ description    │ │ gate_id       │
  │ name        │    │  │ │ severity       │ │ description  │
  │ description │    │  │ │ likelihood     │ │ status       │
  │ status      │    │  │ │ impact         │ │ decision_maker
  │ due_date    │    │  │ │ mitigation     │ │ due_date     │
  │ assignee_id ├─┐  │  │ │ status         │ │ resolution   │
  └──────────────┘ │  │  │ │ owner_id       │ │ decided_at   │
                   │  │  │ │ category       │ │ impact       │
                   │  │  │ └─────────────────┘ └──────────────┘
                   │  │  │
                   │  │  └─────────────────┬───────────────────┐
                   │  │                    │                   │
                   │  │         ┌────────────────┐   ┌──────────────┐
                   │  │         │ StatusUpdate   │   │ ScopeChange  │
                   │  │         │───────────────│   │ ────────────│
                   │  │         │ id (PK)       │   │ id (PK)    │
                   │  │         │ workstream_id │   │ workstream_id
                   │  │         │ gate_id       │   │ description  │
                   │  │         │ author_id ────┼─┐ │ change_type  │
                   │  │         │ content       │ │ │ baseline_scope
                   │  │         │ status_color  │ │ │ current_scope│
                   │  │         └────────────────┘ │ │ flagged_by   │
                   │  │                            │ │ flagged_at   │
                   └──┼────────────────────────────┤ │ resolution   │
                      │                            │ └──────────────┘
            ┌──────────┘                            │
            │ (N)                                    │
            │         ┌──────────────────────┐      │
            │         │  Dependency          │      │
            │         │──────────────────────│      │
            │         │ id (PK)              │      │
            │         │ source_workstream_id │──────┤
            │         │ target_workstream_id │──────┘
            │         │ gate_id              │
            │         │ description          │
            │         │ dep_type             │
            │         │ status               │
            │         │ criticality          │
            │         │ notes                │
            │         └──────────────────────┘
            │
            └────────────────────────────────────
                (Dependency source/target self-referential)
```

## Model Definitions

### Program
Main program container. Organizes phases, gates, and workstreams.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | TimestampMixin inherited |
| name | string(255) | NOT NULL | e.g., "Waypoint 360" |
| description | text | nullable | Program overview |
| start_date | date | nullable | Program kick-off date |
| end_date | date | nullable | Program planned completion |
| status | enum(ProgramStatus) | DEFAULT ACTIVE | planning, active, on_hold, complete |
| created_at | datetime | NOT NULL, auto | UTC timestamp |
| updated_at | datetime | NOT NULL, auto | UTC timestamp on write |

**Relationships**:
- Has many `Phase` (cascade delete-orphan)
- Has many `Gate` (cascade delete-orphan)
- Has many `Workstream` (cascade delete-orphan)

---

### Phase
Grouping of gates within a program (e.g., Align, Incept, Deliver phases).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| program_id | integer | FK → Program.id | NOT NULL |
| name | string(100) | NOT NULL | e.g., "Align", "Incept", "Deliver" |
| description | text | nullable | Phase purpose |
| start_week | integer | NOT NULL | Week number when phase starts |
| end_week | integer | nullable | Week number when phase ends |
| goal | text | nullable | Phase objective |
| key_activities | text | nullable | Summary of key work |
| exit_criteria | text | nullable | Narrative description of phase exit requirements |
| sort_order | integer | DEFAULT 0 | Controls display order |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Program`
- Has many `Gate` (back_populates via phase_id FK)

---

### Gate
Checkpoint within a phase. Evaluates readiness of all workstreams to proceed.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| program_id | integer | FK → Program.id | NOT NULL |
| phase_id | integer | FK → Phase.id | nullable (gate may not belong to explicit phase) |
| name | string(255) | NOT NULL | e.g., "Align Gate", "Inception Gate 1" |
| short_name | string(50) | nullable | e.g., "ALIGN", "INCEPT-1" (used in UI) |
| description | text | nullable | Gate purpose and exit criteria narrative |
| week_number | integer | NOT NULL | Week in program timeline |
| due_date | date | nullable | Target completion date |
| status | enum(GateStatus) | DEFAULT NOT_STARTED | not_started, in_progress, complete, at_risk, blocked |
| sort_order | integer | DEFAULT 0 | Controls display order in gate timeline |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Program`
- Belongs to `Phase` (optional)
- Has many `GateExitCriteria` (cascade delete-orphan)
- Has many `Deliverable` (back_populates)
- Has many `Dependency` (back_populates via gate_id)
- Has many `Decision` (back_populates via gate_id, nullable)

---

### GateExitCriteria
Exit criteria for a gate. Each criterion tracks readiness independently.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| gate_id | integer | FK → Gate.id | NOT NULL |
| description | text | NOT NULL | e.g., "All workstream deliverables complete" |
| status | enum(CriteriaStatus) | DEFAULT NOT_STARTED | not_started, in_progress, complete, at_risk, blocked |
| notes | text | nullable | Progress notes, blockers, comments |
| sort_order | integer | DEFAULT 0 | Controls display order within gate |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Gate`

---

### Workstream
A stream of work within the program. Contains deliverables, risks, decisions.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| program_id | integer | FK → Program.id | NOT NULL |
| name | string(255) | NOT NULL | e.g., "AgentOps", "Solution Design", "CX Research" |
| short_name | string(50) | nullable | e.g., "AGOPS", "SDES", "CXRES" |
| purpose | text | nullable | Why this workstream exists |
| scope_in | text | nullable | What IS included |
| scope_out | text | nullable | What is explicitly NOT included |
| baseline_scope | text | nullable | Snapshot of original scope at Align gate (for drift detection) |
| owner_id | integer | FK → Person.id | nullable (workstream may be unassigned) |
| status | enum(WorkstreamStatus) | DEFAULT NOT_STARTED | not_started, on_track, at_risk, blocked, complete |
| sort_order | integer | DEFAULT 0 | Controls display order in lists |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Program`
- Belongs to `Person` as owner (foreign_keys=[owner_id], back_populates="owned_workstreams")
- Has many `Person` as members (foreign_keys="Person.workstream_id", back_populates="workstream")
- Has many `Deliverable` (cascade delete-orphan)
- Has many `Risk` (cascade delete-orphan)
- Has many `Decision` (cascade delete-orphan)
- Has many `StatusUpdate` (cascade delete-orphan)
- Has many `ScopeChange` (cascade delete-orphan)
- Has many `Dependency` outbound (source_workstream_id) → needs_from
- Has many `Dependency` inbound (target_workstream_id) → provides_to

---

### Person
User/team member. Can own workstreams, author updates, own risks.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| name | string(255) | NOT NULL | Full name |
| email | string(255) | UNIQUE, nullable | Email address (login identifier) |
| role | enum(UserRole) | DEFAULT VIEWER | admin, owner (workstream), viewer |
| title | string(255) | nullable | Job title |
| team | string(255) | nullable | Team/org unit |
| organization | string(255) | nullable | e.g., "ProServ", "SWA", "TBD" |
| capacity_pct | float | DEFAULT 100.0 | % allocated to Waypoint program |
| workstream_id | integer | FK → Workstream.id | nullable (person may not be on a workstream) |
| hashed_password | string(255) | nullable | bcrypt hash for JWT auth |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Owns many `Workstream` (foreign_keys="Workstream.owner_id", back_populates="owner")
- Is member of `Workstream` (foreign_keys=[workstream_id], back_populates="members")
- Has many `Deliverable` assigned (back_populates="assignee")
- Owns many `Risk` (back_populates="owner")
- Authors many `StatusUpdate` (back_populates="author")

---

### Deliverable
Tangible output of a workstream, tied to a specific gate.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| workstream_id | integer | FK → Workstream.id | NOT NULL |
| gate_id | integer | FK → Gate.id | NOT NULL |
| name | string(255) | NOT NULL | e.g., "Observability Landscape Assessment" |
| description | text | nullable | What the deliverable contains |
| status | enum(DeliverableStatus) | DEFAULT NOT_STARTED | not_started, in_progress, complete, at_risk, blocked |
| due_date | date | nullable | Target completion date |
| assignee_id | integer | FK → Person.id | nullable |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Workstream`
- Belongs to `Gate`
- Belongs to `Person` as assignee (back_populates="assigned_deliverables")

---

### Risk
Risk to the program identified in a workstream.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| workstream_id | integer | FK → Workstream.id | NOT NULL |
| description | text | NOT NULL | Risk statement |
| severity | enum(Severity) | DEFAULT MEDIUM | critical, high, medium, low |
| likelihood | enum(Likelihood) | DEFAULT MEDIUM | high, medium, low |
| impact | text | nullable | Consequence if risk occurs |
| mitigation | text | nullable | Planned response/mitigation |
| status | enum(RiskStatus) | DEFAULT OPEN | open, mitigated, accepted, closed |
| owner_id | integer | FK → Person.id | nullable |
| category | string(100) | nullable | e.g., "technical", "resourcing", "dependency", "timeline", "scope" |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Workstream`
- Belongs to `Person` as owner (back_populates="owned_risks")

---

### Decision
Decision point that must be made within a workstream.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| workstream_id | integer | FK → Workstream.id | NOT NULL |
| gate_id | integer | FK → Gate.id | nullable |
| description | text | NOT NULL | Decision to be made |
| status | enum(DecisionStatus) | DEFAULT NEEDED | needed, pending, made, deferred |
| decision_maker | string(255) | nullable | Who must make the decision |
| due_date | date | nullable | Deadline for decision |
| resolution | text | nullable | The decision made |
| decided_at | datetime | nullable | When decision was made |
| impact | text | nullable | What happens if delayed |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Workstream`
- Belongs to `Gate` (optional)

---

### Dependency
Dependency between two workstreams (who needs what from whom).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| source_workstream_id | integer | FK → Workstream.id | NOT NULL (who needs/provides) |
| target_workstream_id | integer | FK → Workstream.id | NOT NULL (who provides/needs) |
| gate_id | integer | FK → Gate.id | nullable (which gate is this relevant to) |
| description | text | NOT NULL | What is needed/provided |
| dep_type | enum(DependencyType) | DEFAULT NEEDS_FROM | needs_from, provides_to, blocks, informs |
| status | enum(DependencyStatus) | DEFAULT OPEN | open, in_progress, resolved, blocked, at_risk |
| criticality | enum(Criticality) | DEFAULT MEDIUM | critical (on critical path), high, medium, low |
| notes | text | nullable | Additional context |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Source: `Workstream` (foreign_keys=[source_workstream_id], back_populates="outbound_dependencies")
- Target: `Workstream` (foreign_keys=[target_workstream_id], back_populates="inbound_dependencies")
- Belongs to `Gate` (optional)

---

### StatusUpdate
Narrative update on workstream progress.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| workstream_id | integer | FK → Workstream.id | NOT NULL |
| gate_id | integer | FK → Gate.id | nullable |
| author_id | integer | FK → Person.id | nullable |
| content | text | NOT NULL | Update narrative |
| status_color | enum(StatusColor) | DEFAULT GREEN | green (on_track), yellow (at_risk), red (blocked) |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Workstream`
- Belongs to `Person` as author (back_populates="status_updates")

---

### ScopeChange
Scope change detected in a workstream (addition, removal, modification).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | integer | PK, autoincrement | |
| workstream_id | integer | FK → Workstream.id | NOT NULL |
| description | text | NOT NULL | What changed |
| change_type | enum(ChangeType) | NOT NULL | addition, removal, modification |
| baseline_scope | text | nullable | Original scope snapshot |
| current_scope | text | nullable | Current scope after change |
| flagged_by | enum(FlaggedBy) | DEFAULT USER | user (manual entry), ai (detected by LangGraph) |
| flagged_at | datetime | nullable | When scope change was detected |
| resolution | text | nullable | How change was addressed |
| created_at | datetime | NOT NULL, auto | |
| updated_at | datetime | NOT NULL, auto | |

**Relationships**:
- Belongs to `Workstream`

---

## Enums

### ProgramStatus
```python
class ProgramStatus(str, enum.Enum):
    PLANNING = "planning"      # Pre-kickoff
    ACTIVE = "active"          # Currently executing
    ON_HOLD = "on_hold"        # Paused
    COMPLETE = "complete"      # Finished
```

### GateStatus
```python
class GateStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"        # On track but risks present
    BLOCKED = "blocked"        # Cannot proceed
```

### CriteriaStatus
```python
class CriteriaStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
```

### WorkstreamStatus
```python
class WorkstreamStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETE = "complete"
```

### UserRole
```python
class UserRole(str, enum.Enum):
    ADMIN = "admin"             # Organization admin
    OWNER = "owner"             # Workstream owner
    VIEWER = "viewer"           # Leadership, read-only
```

### DeliverableStatus
```python
class DeliverableStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
```

### Severity
```python
class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### Likelihood
```python
class Likelihood(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### RiskStatus
```python
class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"
```

### DecisionStatus
```python
class DecisionStatus(str, enum.Enum):
    NEEDED = "needed"           # Not yet identified decision maker
    PENDING = "pending"         # Awaiting decision
    MADE = "made"               # Decision resolved
    DEFERRED = "deferred"       # Postponed to later gate
```

### DependencyType
```python
class DependencyType(str, enum.Enum):
    NEEDS_FROM = "needs_from"   # Source workstream needs something from target
    PROVIDES_TO = "provides_to" # Source provides to target
    BLOCKS = "blocks"           # Source blocks target
    INFORMS = "informs"         # Source informs target (non-blocking)
```

### DependencyStatus
```python
class DependencyStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"
```

### Criticality
```python
class Criticality(str, enum.Enum):
    CRITICAL = "critical"       # On critical path, delay cascades
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### StatusColor
```python
class StatusColor(str, enum.Enum):
    GREEN = "green"             # On track
    YELLOW = "yellow"           # At risk
    RED = "red"                 # Blocked
```

### ChangeType
```python
class ChangeType(str, enum.Enum):
    ADDITION = "addition"       # Work added to scope
    REMOVAL = "removal"         # Work removed from scope
    MODIFICATION = "modification" # Existing work modified
```

### FlaggedBy
```python
class FlaggedBy(str, enum.Enum):
    USER = "user"               # Manual entry by person
    AI = "ai"                   # Detected by LangGraph
```

---

## Indexes

| Index | Columns | Type | Rationale |
|-------|---------|------|-----------|
| **programs.pkey** | id | PK | Primary key |
| **phases.pkey** | id | PK | Primary key |
| **phases.program_id** | program_id | FK | Query phases by program |
| **gates.pkey** | id | PK | Primary key |
| **gates.program_id** | program_id | FK | Query gates by program |
| **gates.phase_id** | phase_id | FK | Query gates by phase |
| **gate_exit_criteria.pkey** | id | PK | Primary key |
| **gate_exit_criteria.gate_id** | gate_id | FK | Query criteria by gate |
| **workstreams.pkey** | id | PK | Primary key |
| **workstreams.program_id** | program_id | FK | Query workstreams by program |
| **workstreams.owner_id** | owner_id | FK | Query workstreams by owner |
| **people.pkey** | id | PK | Primary key |
| **people.email** | email | UNIQUE | Ensure email uniqueness for login |
| **people.workstream_id** | workstream_id | FK | Query team members by workstream |
| **deliverables.pkey** | id | PK | Primary key |
| **deliverables.workstream_id** | workstream_id | FK | Query deliverables by workstream |
| **deliverables.gate_id** | gate_id | FK | Query deliverables by gate |
| **deliverables.(workstream_id, gate_id)** | (workstream_id, gate_id) | COMPOSITE | Fast lookup of deliverables for gate timeline |
| **deliverables.assignee_id** | assignee_id | FK | Query assigned deliverables |
| **risks.pkey** | id | PK | Primary key |
| **risks.workstream_id** | workstream_id | FK | Query risks by workstream |
| **risks.owner_id** | owner_id | FK | Query risks owned by person |
| **decisions.pkey** | id | PK | Primary key |
| **decisions.workstream_id** | workstream_id | FK | Query decisions by workstream |
| **decisions.gate_id** | gate_id | FK | Query decisions due at gate |
| **dependencies.pkey** | id | PK | Primary key |
| **dependencies.source_workstream_id** | source_workstream_id | FK | Query dependencies from workstream |
| **dependencies.target_workstream_id** | target_workstream_id | FK | Query dependencies to workstream |
| **dependencies.gate_id** | gate_id | FK | Query gate-relevant dependencies |
| **status_updates.pkey** | id | PK | Primary key |
| **status_updates.workstream_id** | workstream_id | FK | Query updates by workstream |
| **status_updates.author_id** | author_id | FK | Query updates by author |
| **scope_changes.pkey** | id | PK | Primary key |
| **scope_changes.workstream_id** | workstream_id | FK | Query scope changes by workstream |
| **(created_at) on all tables** | created_at | INDEX | Fast queries for recent activity |
| **(updated_at) on all tables** | updated_at | INDEX | Fast queries for recently modified items |

---

## Migration Notes

- **SQLite → PostgreSQL**: Connection string changes only (DATABASE_URL env var). SQLAlchemy async layer abstracts database differences.
- **Seed Script**: `seed.py` populates from Commercial Workshop PDF data (idempotent, can be run multiple times).
- **Soft Deletes**: Not currently implemented. To add: add `deleted_at: datetime` field and filter with `where(Model.deleted_at == None)` in queries.
- **Audit Trail**: Currently only `created_at`, `updated_at`. To add: add `created_by_id`, `updated_by_id` FKs to Person.

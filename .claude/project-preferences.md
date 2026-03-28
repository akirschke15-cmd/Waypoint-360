# Project Preferences: Boiler 4.0 Conformance Framework

**Framework:** Boiler 4.0
**Last Updated:** 2026-03-20
**BOILER_MODE:** `strict` (production) | `lean` (rapid iteration)

---

## Core Implementation Philosophy: 100% Requirement Conformance

Every implementation artifact must trace directly to an explicit requirement or acceptance criterion. No code exists in isolation. No features are partial. No promises are deferred.

**The Rule:** If a requirement doesn't have measurable acceptance criteria, the requirement is not accepted. If acceptance criteria can't be validated, the task cannot be marked complete.

This is the defining principle that separates Boiler 4.0 projects from drifting codebases.

---

## Requirement Drift Prevention

Drift happens when the gap between stated requirements and implemented behavior grows over time. Boiler 4.0 closes this gap through three mechanisms:

### Mechanism 1: Explicit Acceptance Criteria

Every requirement must answer these questions before implementation begins:

1. What is the measurable outcome?
2. How will success be validated?
3. What are the boundary conditions (edge cases that should pass)?
4. What explicitly does NOT need to work?
5. What constraints apply (performance, security, compatibility)?

If any of these cannot be answered clearly, the requirement is incomplete. Route back to requirements-agent for clarification.

**Example (Bad):** "Add user authentication"

**Example (Good):** "Implement JWT-based authentication with 15-minute token expiry. Accept credentials via POST /auth/login with username and password. Return JWT in response body. Reject credentials with <2 minutes remaining in token TTL. Validate token on every authenticated endpoint. Log failed attempts with timestamp and IP address. Must not store plaintext passwords."

### Mechanism 2: Design Document References

Every task queue entry must list which design documents must be read before implementation. This prevents the "but nobody told me about that" defense.

Example task queue entry:

```
Requirement: Implement product search endpoint
Acceptance Criteria: [list of specific criteria]
Read Before Coding: 03-API-SPECIFICATION.md, 02-DATABASE-SCHEMA.md, 07-PERFORMANCE-TARGETS.md
Design Docs This Task Creates/Updates: 03-API-SPECIFICATION.md
Frozen Files Affected: None
```

The implementation-agent must read these documents and reference them in code comments where relevant.

### Mechanism 3: Validation Gate Before Sign-Off

No task is marked complete until validation-agent runs acceptance criteria as a checklist:

```
Requirement: Implement product search endpoint
Acceptance Criteria:
  [ ] Endpoint returns 200 with results for valid search terms
  [ ] Endpoint returns 400 with error detail for invalid query syntax
  [ ] Query performance is <100ms for typical search (P95)
  [ ] Search is case-insensitive
  [ ] Partial matches return results (e.g., "produ" matches "product")
  [ ] Results are sorted by relevance score, highest first
  [ ] Endpoint rejects unauthenticated requests with 401
  [ ] Logged searches include timestamp, user_id, query_string

Validation Result: [✓ All pass] or [✗ Failures listed with details]
```

If any criterion fails, the task is not marked complete. It returns to task queue with details.

---

## Implementation Verification Protocol

This is how code gets validated before it ships.

### Pre-Implementation Verification

1. **Requirement Completeness Check** (requirements-agent)
   - Does the requirement have specific acceptance criteria?
   - Are design documents identified?
   - Are scope boundaries clear?
   - Are constraints listed?
   - If any fail: return to clarification queue

2. **Scope Boundary Check** (requirements-agent)
   - Does this requirement modify frozen files?
   - Does it create new files in approved locations?
   - Does it depend on unfinished tasks?
   - Does it conflict with in-progress work?
   - If any fail: route to task queue for dependency resolution

3. **Design Document Availability Check** (agent-router)
   - Are all referenced design documents available?
   - Are they current (updated within last sprint)?
   - Are they approved (marked in status)?
   - If any fail: implementation is blocked until docs exist

### During Implementation

1. **Code references design documents**
   - Comments explain why decisions were made
   - Architectural patterns match 01-ARCHITECTURE.md
   - Database schema changes match 02-DATABASE-SCHEMA.md
   - API responses match 03-API-SPECIFICATION.md
   - Validation rules match 06-SECURITY-REQUIREMENTS.md

2. **Tests are written to acceptance criteria**
   - One test per acceptance criterion (minimum)
   - Tests cover boundary conditions and error cases
   - Tests run and pass locally before code is submitted
   - Test names describe the criterion they validate

3. **Audit trail is maintained**
   - Every decision is logged with timestamp
   - Why a particular approach was chosen over alternatives
   - Any deviations from design documents are noted and justified
   - Any conformance concerns are flagged for validation-agent

### Post-Implementation Verification

1. **Acceptance Criteria Validation** (validation-agent)
   - Run each criterion as a test
   - Confirm manual testing for non-automatable criteria
   - Document which criteria passed and failed
   - Any failures block sign-off

2. **Frozen File Protection** (automated)
   - Scan diff for modifications to frozen files
   - If found: reject and require justification and conformance review
   - Update audit trail if frozen file was intentionally modified

3. **Design Document Consistency** (validation-agent)
   - Confirm code matches referenced design documents
   - If discrepancies exist: halt and clarify with requirements-agent
   - Update design documents if requirements changed during implementation

4. **Conformance Audit** (conformance-auditor skill)
   - Check: all acceptance criteria addressed
   - Check: no partial features (vertical slice rule)
   - Check: no mock data or placeholder code
   - Check: audit trail is complete
   - Check: design documents are accurate
   - If any check fails: return to task queue

---

## Anti-Patterns to Prevent

Boiler 4.0 explicitly rejects these common failure modes. Conformance-auditor blocks them automatically.

### 1. UI Shell Pattern

**What it is:** Code exists that looks complete but doesn't actually do anything. A form that submits but doesn't validate. An API endpoint that returns 200 but doesn't create records.

**Why it happens:** Implementing UI first, then deferring backend logic to "later".

**How Boiler 4.0 prevents it:**
- Vertical slice rule: database to UI in single task
- Acceptance criteria are measurable and specific
- Mock data is explicitly forbidden
- Validation-agent rejects incomplete features

**Enforcement:** If a feature doesn't work end-to-end, it's not accepted, period.

### 2. Mock Data Pattern

**What it is:** Code that returns hard-coded test data instead of real data. Acceptance criteria say "show user's transactions" but the code returns a static array defined in the source file.

**Why it happens:** Faster to fake it than build it; easier to demo.

**How Boiler 4.0 prevents it:**
- Code review checks for hard-coded test fixtures in production code
- Acceptance criteria specify "real data from database" not "sample data"
- conformance-auditor blocks code with TODOs like "replace with real API call"

**Enforcement:** Mock data in production code is a conformance failure. Task is rejected.

### 3. Implicit Deferral Pattern

**What it is:** Code is submitted with a TODO comment: "TODO: Add error handling". Acceptance criteria say "endpoint returns appropriate error for invalid input" but validation is missing.

**Why it happens:** Time pressure; "we'll do it next sprint".

**How Boiler 4.0 prevents it:**
- Task queue is source of truth, not implicit TODOs
- Deferred work must be explicit in task queue
- Acceptance criteria are validated before sign-off
- If feature isn't complete, it's not accepted

**Enforcement:** No implicit deferral. Either the task is complete or it's not. If incomplete, it stays in queue.

### 4. Async Integration Pattern (Premature)

**What it is:** Code calls external services (payments, notifications, analytics) synchronously in the request path, causing high latency and cascading failures if the external service is slow.

**Why it happens:** Simpler to implement; test pass locally.

**How Boiler 4.0 prevents it:**
- 07-PERFORMANCE-TARGETS.md specifies latency requirements
- 05-INTEGRATION-PATTERNS.md prescribes async patterns for external services
- conformance-auditor checks for sync calls to external services
- acceptance criteria include "request completes in <X ms even if external service is slow"

**Enforcement:** Sync external calls are rejected. Code must use async queue, webhook, or background job.

### 5. Copy-Paste Code Pattern

**What it is:** The same logic is duplicated across multiple files. A validation function is copied and modified. Query logic appears in three places.

**Why it happens:** Faster to copy and modify than refactor.

**How Boiler 4.0 prevents it:**
- 01-ARCHITECTURE.md prescribes where logic lives
- Code review during validation phase catches duplicates
- acceptance criteria include "no logic duplication in [specific domain]"

**Enforcement:** Duplicated code is a conformance failure. Task is returned for refactoring.

### 6. Configuration Drift Pattern

**What it is:** Secrets, API keys, or configuration values are hard-coded in source or inconsistently managed. Environment variables work in dev but not in production.

**Why it happens:** Easier to debug with hard-coded values.

**How Boiler 4.0 prevents it:**
- 06-SECURITY-REQUIREMENTS.md defines configuration handling
- 09-DEPLOYMENT-PROCESS.md defines env var strategy
- conformance-auditor scans for hard-coded secrets
- acceptance criteria specify "all secrets are environment variables"

**Enforcement:** Hard-coded secrets are rejected. Task is returned with requirement to use secure configuration.

---

## Decision-Making Framework

When you encounter ambiguity, use this framework:

### Question 1: Is this a requirement or an implementation detail?

**Requirement:** Affects user behavior, success metric, or acceptance criteria
**Implementation Detail:** Affects how the requirement is met, but user doesn't care

If it's a requirement and not explicitly listed in task queue: stop and route to requirements-agent for clarification.

If it's an implementation detail and covered by design documents: proceed with design-doc-guided implementation.

If it's an implementation detail not in design documents: decide and document in audit trail. Update design documents post-hoc if the decision should guide future work.

### Question 2: Does this modify a frozen file?

**Frozen files:** CLAUDE.md, settings.json, project-preferences.md, plugin.json, package.json, .gitignore

If YES: stop. Create a decision record explaining why modification is necessary. Route to validation-agent for conformance review. Proceed only with explicit approval.

If NO: proceed with normal implementation workflow.

### Question 3: Does this create a new file?

**Allowed locations:** ./agents/**, ./hooks/**, ./skills/**, ./src/**, ./tests/**, ./db/migrations/**, ./integrations/**, ./docs/**

If location is in allowed list: proceed.

If location is not in allowed list: stop. Update .claude/settings.json to add location to allowedCreations. Route for approval before creating.

### Question 4: Can this acceptance criterion be validated?

**Validatable:** Has specific, measurable outcome; can be tested or verified
**Not validatable:** Vague ("user-friendly"), subjective ("elegant"), or depends on future work

If criterion is not validatable: stop. Route to requirements-agent for rewrite.

---

## Vertical Slice Requirement

One of Boiler 4.0's defining rules: every feature goes from database to UI in a single task. No partial features.

**What this means:**

A task that says "Add user profile page" must include:
- Database schema (migrations + table changes)
- Backend API endpoints to fetch and update profile
- Frontend components and routing
- Tests for the entire flow
- Documentation updates

A task that says only "Add profile API endpoints" is incomplete. The implementation-agent rejects the narrow scope and asks: which other parts of the vertical slice are included?

**Why vertical slices matter:**

- Partial features are untestable and unmergeable
- Deferring UI or tests creates technical debt
- Validation at end-to-end prevents "it works on my machine" failures
- Stakeholders see working features, not theoretical progress

**How Boiler 4.0 enforces it:**

- Task queue entries must identify all layers affected (database, API, UI, tests, docs)
- Acceptance criteria include "feature works end-to-end from UI to database"
- Conformance-auditor rejects code that covers only one layer
- Code review during validation confirms vertical slice is complete

**Exception:** Async work (background jobs, notifications) can be deferred if explicitly listed in task queue with dependency on separate task.

---

## BOILER_MODE Behavior Differences

### BOILER_MODE=strict (Production)

- All requirements must have explicit acceptance criteria before work begins
- Task queue is mandatory; off-queue work is not recognized
- Conformance failures halt execution; issues must be resolved before proceeding
- Design documents must exist and be approved before implementation
- Frozen files cannot be modified without formal process
- Vertical slice rule is strictly enforced
- Every task requires validation-agent sign-off before completion
- Mock data, placeholders, and implicit deferral are blocking failures

**When to use:** Production systems, enterprise projects, regulatory compliance contexts, shipping to external users.

### BOILER_MODE=lean (Rapid Iteration)

- Requirements can be implicit if intent is clear from context
- Task queue is optional for well-scoped work; developer judgment is trusted
- Conformance check is advisory; failures can be overridden with justification
- Design documents can be created post-hoc if blocking implementation
- Frozen files can be modified with notification to team
- Vertical slice rule still applies, but incremental validation acceptable
- Task completion doesn't require sign-off if developer confirms criteria met
- Deferred work is acceptable if documented with follow-up task

**When to use:** Proof-of-concepts, internal tools, rapid experimentation, early-stage product development where learning velocity matters more than perfection.

**Lean Mode Safety Guardrails:**
- Even in lean mode: vertical slice rule is mandatory
- Even in lean mode: mock data in production code is not allowed
- Even in lean mode: frozen files (CLAUDE.md, settings.json) are protected
- Even in lean mode: security requirements (06-SECURITY-REQUIREMENTS.md) are enforced
- Lean mode is not a license to skip testing or documentation

---

## How to Use This Document

**For requirements-agent:**
- Use this to evaluate completeness of incoming requirements
- Reject requirements without explicit acceptance criteria
- Route ambiguous requirements back to stakeholder with questions from Decision-Making Framework

**For implementation-agent:**
- Read the Anti-Patterns section before coding
- Validate your implementation against frozen files, allowed locations, vertical slice rule
- Reference design documents in code comments
- Keep audit trail of why specific decisions were made

**For validation-agent:**
- Run the Acceptance Criteria Validation checklist
- Use the Anti-Patterns section to flag code that doesn't pass
- Confirm design document consistency
- Run conformance-auditor before signing off

**For agent-router:**
- Use BOILER_MODE to determine enforcement strictness
- Check Conformance Rules from settings.json before routing to implementation
- Use the Decision-Making Framework for ambiguous scoping decisions

**For documentation-agent:**
- Maintain design documents per Design Documents list in CLAUDE.md
- Follow Requirement Drift Prevention mechanisms when creating docs
- Mark documents with status (draft/approved) in CLAUDE.md table

---

## Conformance Audit Checklist

Before any task is marked complete, run this checklist:

- [ ] Original requirement from task queue is clearly stated
- [ ] Every acceptance criterion was run and passed
- [ ] No frozen files were modified (or modification was justified and approved)
- [ ] Design documents were read and referenced in code
- [ ] Feature works end-to-end from database to UI (vertical slice)
- [ ] No mock data in production code
- [ ] No implicit deferral (TODOs referring to future work)
- [ ] No code duplication without justification
- [ ] Configuration is externalized (no hard-coded secrets or env-specific values)
- [ ] Tests exist and pass for all acceptance criteria
- [ ] Async operations to external services are used for integrations
- [ ] Audit trail is complete with decision rationale
- [ ] Design documents are updated to reflect implementation decisions
- [ ] Code follows style conventions in 01-ARCHITECTURE.md or project preferences

If any item fails: reject task and return to queue with specific feedback.

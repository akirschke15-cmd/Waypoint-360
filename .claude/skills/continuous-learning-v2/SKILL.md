---
name: continuous-learning-v2
description: Instinct-based learning system v2.1 with project-scoped instincts, confidence scoring, evolution pipeline, and structured knowledge capture. Build and maintain project-specific decision patterns.
origin: ECC
version: 2.1
---

# Continuous Learning v2 Skill

An instinct-based learning system for capturing, scoring, and evolving project-specific knowledge patterns.

## When to Activate

- Discovering repeating patterns or decisions
- Building project-specific conventions
- Codifying expert knowledge
- Improving code review consistency
- Establishing team best practices
- Maintaining institutional memory

## Core Concepts

An "instinct" is a decision pattern with confidence score, context, and evolution history.

```yaml
# Example instinct
name: "React Hook Composition"
confidence: 0.92
context: "frontend patterns"
discovered: "2026-03-15"

pattern: |
  For complex state logic across components, extract custom hooks
  rather than using Context. Custom hooks compose better and are
  easier to test in isolation.

evidence:
  - "3 refactorings where we moved from Context to custom hooks"
  - "custom hooks reduced testing complexity by ~40%"
  - "easier for new team members to understand"

counter_cases:
  - "Global theme switching uses Context (global scope, rarely changes)"
  - "Authentication state uses Context (truly global, rarely accessed from tests)"

applies_to:
  - "feature-level state (cart, filters, form state)"
  - "shared state between sibling components"

avoids:
  - "truly global state (theme, auth, language)"
  - "state that needs time-travel debugging"
  - "state stored in URL/localStorage"

status: "active"
version: 2
updated: "2026-03-20"
```

## Instinct Types

### Pattern Instincts
How to structure code or make architectural decisions.

```yaml
name: "API Response Normalization"
type: "pattern"

pattern: |
  Always normalize API responses to match local domain model.
  Never use API response shapes directly in components.
  Add a normalization layer between API client and component.

example: |
  // API returns { user_id, first_name, last_name }
  // Client normalizes to { id, name }
  function normalizeUser(apiUser) {
    return {
      id: apiUser.user_id,
      name: `${apiUser.first_name} ${apiUser.last_name}`
    }
  }
```

### Anti-Pattern Instincts
What NOT to do and why.

```yaml
name: "Global Mutable State"
type: "anti-pattern"

anti_pattern: |
  Avoid global mutable state that multiple parts of the app can modify
  without clear ownership. Makes debugging and testing extremely difficult.

bad_example: |
  // window.appState = { user: null }
  // any component can mutate this

good_alternative: |
  // Use React Context + useContext or Zustand with clear mutations
```

### Tool/Library Instincts
Preferred libraries and configurations.

```yaml
name: "Form Validation: Zod"
type: "tool"

recommendation: |
  Use Zod for all form validation in React projects.
  - Type-safe schemas with TypeScript inference
  - Works client and server
  - Better DX than Yup
```

## Confidence Scoring

Confidence reflects how confident we are in this instinct.

```
0.0 - 0.3: Hypothesis
  - New pattern, few examples
  - Under investigation
  - May be overturned

0.3 - 0.7: Emerging Pattern
  - Multiple examples
  - Some counter-cases
  - Generally solid but evolving

0.7 - 0.9: Established Pattern
  - Many examples
  - Proven across projects
  - Well-understood trade-offs

0.9 - 1.0: Core Instinct
  - Universal in our codebase
  - No known counter-cases
  - Part of team identity
```

Update confidence as evidence grows:

```yaml
name: "Error Boundary Placement"
confidence: 0.45  # Before: Emerging Pattern
evidence:
  - "caught 2 major crashes in dev"
  - "missed 1 edge case (async errors)"
  - "implementation varies across team"

# Later...
confidence: 0.78  # After: Established Pattern
evidence:
  - "standardized with async error catching"
  - "caught 5+ production issues"
  - "team fully aligned on implementation"
```

## Evolution Pipeline

### Stage 1: Observation (Confidence 0.1-0.3)

Notice a pattern, document initial observations.

```yaml
name: "Component File Organization"
stage: "observation"
confidence: 0.15
notes: |
  - Noticed teams organizing components differently
  - Some use (Component.tsx + Component.module.css)
  - Others use (Component/index.tsx + Component/styles.ts)
  - Unclear which is better
```

### Stage 2: Hypothesis (Confidence 0.3-0.5)

Propose a rule, gather evidence.

```yaml
name: "Component File Organization"
stage: "hypothesis"
confidence: 0.42
hypothesis: |
  Flat structure (Component.tsx + Component.module.css) is better than
  directory structure for simple components. Directory structure is only
  needed when component has sub-components or complex internal logic.

testing:
  - "Apply to 3 new features"
  - "Measure refactoring difficulty"
  - "Ask team feedback"
```

### Stage 3: Validation (Confidence 0.5-0.8)

Apply across projects, validate effectiveness.

```yaml
name: "Component File Organization"
stage: "validation"
confidence: 0.68
validation_results:
  - "Applied to 5 features, all simpler than directory approach"
  - "Easier for onboarding (less file navigation)"
  - "Still need directories for complex components (AuthFlow, etc.)"
  - "Team consensus building"
```

### Stage 4: Canonicalization (Confidence 0.8+)

Elevate to team standard, document in project conventions.

```yaml
name: "Component File Organization"
stage: "canonical"
confidence: 0.87
rule: |
  Use flat structure (Component.tsx) for single-component features.
  Use directory structure (Component/index.tsx + Component/hooks.ts) only when:
    - Component has sub-components
    - Component has >2 internal utilities
    - Component file would exceed 300 lines

documented_in:
  - "CODING_STANDARDS.md"
  - "Code review checklist"
  - ".claude/instincts/component-organization.yaml"
```

## Instinct Storage Structure

```
.claude/
├── instincts/
│   ├── README.md                    # Index of all instincts
│   ├── component-organization.yaml
│   ├── error-handling.yaml
│   ├── api-design.yaml
│   ├── performance.yaml
│   └── security.yaml
├── hooks/
│   ├── on-code-review.md           # Hook: triggered during code review
│   ├── on-api-design.md            # Hook: triggered when designing APIs
│   ├── on-component-creation.md    # Hook: triggered on new components
│   └── on-refactoring.md           # Hook: triggered during refactoring
└── evolution-log.md                # Chronological log of instinct changes
```

## Instinct Hooks

Hooks are decision points where instincts get applied.

### on-code-review Hook

```yaml
# .claude/hooks/on-code-review.md

When reviewing pull requests, check these instincts:

1. **Component Organization** (confidence: 0.87)
   - [ ] Single-component features use flat structure
   - [ ] Complex components properly split into files

2. **Error Handling** (confidence: 0.82)
   - [ ] All async operations wrapped in try-catch
   - [ ] Error boundaries at page level

3. **Type Safety** (confidence: 0.91)
   - [ ] No implicit any types
   - [ ] All function parameters typed

4. **Testing** (confidence: 0.79)
   - [ ] Unit tests for logic
   - [ ] Happy path + error path covered
```

### on-api-design Hook

```yaml
# .claude/hooks/on-api-design.md

When designing new APIs, apply these instincts:

1. **Resource Naming** (confidence: 0.88)
   - GET /users (collection)
   - GET /users/:id (single)
   - POST /users (create)
   - PATCH /users/:id (update)
   - DELETE /users/:id (delete)

2. **Response Shape** (confidence: 0.81)
   - Success: { data: {...}, meta: {...} }
   - Error: { error: string, code: string }

3. **Pagination** (confidence: 0.75)
   - Cursor-based for large datasets
   - Offset-based for small/admin endpoints
```

## Capturing New Instincts

Process when discovering a pattern:

### 1. Observe & Record

```yaml
date: "2026-03-20"
context: "Code review on payment feature"

observation: |
  Noticed all database queries are wrapped in try-catch blocks.
  This catches query errors cleanly but silently swallows some issues.
  Should probably have different handling for connection vs constraint errors.

pattern: |
  Differentiate database error types:
  - Connection errors -> retry with backoff
  - Constraint errors -> return 409 Conflict
  - Unexpected errors -> return 500, log
```

### 2. Investigate

```yaml
investigation: |
  - Checked 8 database operations
  - 6 properly distinguish error types
  - 2 generic catch-all approach (older code)
  - No performance issues with distinction
```

### 3. Propose Rule

```yaml
proposed_rule: |
  All database operations should catch and handle three error categories:
  1. Connection errors (timeout, network)
  2. Constraint errors (unique key, foreign key)
  3. Unexpected errors (unknown, internal)
```

### 4. Test & Validate

```yaml
validated_on:
  - "New order processing API (passed)"
  - "User update endpoint (passed)"
  - "Refactored payment reconciliation (passed)"

confidence_update: "0.15 -> 0.68 (moved to validation stage)"
```

### 5. Elevate

```yaml
final_rule: |
  Categorize database errors into three types. See db-error-handling.yaml
  for implementation patterns.

stage: "canonical"
confidence: 0.82
documented_in:
  - "docs/database-patterns.md"
  - ".claude/instincts/db-error-handling.yaml"
```

## Evolution Log

Track changes to instincts over time:

```markdown
# Instinct Evolution Log

## 2026-03-20
- **Updated**: Component Organization (0.68 -> 0.87)
  Reason: Validated on 5 features, team consensus reached
  Impact: Elevated to coding standard

## 2026-03-15
- **New**: Database Error Handling (0.15)
  Reason: Observed pattern in code review
  Status: Under investigation

## 2026-03-10
- **Deprecated**: Redux for State Management (0.82 -> archived)
  Reason: Switched to Zustand, no projects using Redux
  Replaced by: Zustand State Management (0.78)

## 2026-03-05
- **Updated**: API Response Shape (0.71 -> 0.81)
  Reason: Added validation at API boundary
  Impact: Improved type safety in clients
```

## Confidence Adjustment Protocol

When confidence should change:

```yaml
increase_confidence_when:
  - Pattern works consistently across 3+ projects
  - Zero counter-examples or only edge cases
  - Team understands and applies pattern
  - Pattern prevents bugs or improves quality metrics

decrease_confidence_when:
  - Counter-example found in real usage
  - Team struggles with implementation
  - Pattern violates new constraints
  - Simpler alternative discovered

archive_confidence_when:
  - Technology becomes deprecated
  - Better pattern found and validated
  - No longer applicable to project scope
```

## Querying Instincts

During implementation, access instincts:

```
# Get all instincts for component creation
instincts --hook on-component-creation

# Get specific instinct with confidence threshold
instincts --name "error-handling" --min-confidence 0.7

# Show evolution history
instincts --history --name "api-design"

# Find relevant instincts for task
instincts --search "performance"
```

## Team Alignment

Make instincts discoverable:

- Document in `.claude/instincts/README.md`
- Reference in code review checklists
- Link in CODING_STANDARDS.md
- Discuss in team standups when new
- Update when counter-examples found

Instincts are living, team-owned knowledge. They evolve with project understanding.

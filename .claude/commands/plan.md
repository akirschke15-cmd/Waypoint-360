---
name: plan
description: Break down a feature or task into a structured plan with phases, milestones, and estimates
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Plan Command

Route to the **Planner** agent to break down work into phases, create timelines, and establish milestones.

## Usage

```
/plan <feature_description>
```

## Examples

### Example 1: Feature Planning
```
/plan Implement user authentication with JWT tokens
```

Response: Planner creates:
- Phase 1: Design auth architecture and security model
- Phase 2: Backend JWT implementation (login, logout, refresh)
- Phase 3: Frontend authentication UI and state management
- Phase 4: Integration testing and security validation
- Phase 5: Documentation and deployment

### Example 2: Bug Fix Planning
```
/plan High memory usage in production affecting P99 latency
```

Response: Planner creates:
- Phase 1: Reproduce issue in staging
- Phase 2: Profile memory usage and identify leak
- Phase 3: Implement fix with minimal changes
- Phase 4: Regression testing
- Phase 5: Verification and monitoring setup

## Expected Output

- **Phase breakdown**: Logical sequence of work
- **Milestones**: Completion criteria for each phase
- **Dependencies**: Cross-phase dependencies identified
- **Estimates**: Effort sizing (S/M/L/XL) per phase
- **Risks**: Identified blockers and mitigation strategies
- **Success criteria**: How to verify completion

## When to Use

- Starting a new feature
- Scope is unclear or ambiguous
- Large/XL effort needed
- Multiple teams involved
- Timeline or deadline pressure
- Complex dependencies between tasks

## When NOT to Use

- Simple bug fixes (one phase)
- Maintenance tasks (clear scope)
- Isolated refactoring

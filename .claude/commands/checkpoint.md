---
name: checkpoint
description: Create milestone checkpoint with progress snapshot and validation
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Checkpoint Command

Route to the **Planner** or **Fullstack Engineer** agent to create milestone checkpoints with progress validation.

## Usage

```
/checkpoint [milestone_name]
```

## Examples

### Example 1: Feature Milestone
```
/checkpoint Authentication system Phase 2 complete
```

Response: Checkpoint Creator:
1. Validates current progress against plan
2. Documents completed work
3. Identifies remaining tasks
4. Creates snapshot for recovery
5. Plans next phase

### Example 2: Project Checkpoint
```
/checkpoint v1.0 Beta Release
```

Response: Checkpoint Creator:
1. Summarizes completed features
2. Lists known issues
3. Documents blockers
4. Captures deployment snapshot
5. Prepares release notes

## Checkpoint Contents

- **Progress Summary**
  - Features completed
  - Tests passing
  - Coverage percentage
  - Performance metrics

- **Quality Snapshot**
  - Code quality score
  - Security assessment
  - Accessibility status
  - Documentation coverage

- **Risk Assessment**
  - Known issues
  - Blockers
  - Dependencies
  - Mitigation strategies

- **Recovery Information**
  - Git commit hash
  - Deployment timestamp
  - Configuration snapshot
  - Database state (if applicable)

- **Next Steps**
  - Remaining tasks
  - Dependencies
  - Timeline estimate
  - Resource needs

## Checkpoint Validation

Before creating checkpoint, verify:

- [ ] All planned features implemented
- [ ] Tests passing (unit, integration, e2e)
- [ ] Coverage at 80%+
- [ ] Code review completed
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Performance acceptable
- [ ] No critical bugs
- [ ] Deployment tested

## Checkpoint Naming Convention

Format: `[project]-[phase]-[date]`

Examples:
- `payments-phase2-2026-03-20`
- `auth-beta-2026-03-20`
- `mobile-v1.0-2026-03-20`

## Checkpoint Output

- **Snapshot Report**: Markdown file with full status
- **Recovery Guide**: How to restore from checkpoint
- **Release Notes**: Changes since last checkpoint
- **Metrics Comparison**: Progress vs. plan
- **Next Milestones**: Upcoming checkpoints

## Checkpoint History

Maintained at: `.claude/logs/checkpoints.log`

Format:
```
[2026-03-20T14:32:00Z] Checkpoint: auth-phase2-2026-03-20
  Status: PASS
  Features: 12/12 complete
  Coverage: 86%
  Issues: 3 known (0 critical)
  Commit: a1b2c3d4e5f6
```

## Recovery Process

If need to rollback to checkpoint:

1. Reference checkpoint name
2. Run: `git checkout <commit-hash>`
3. Restore database state (if needed)
4. Verify services healthy
5. Monitor metrics

## When to Use

- Feature phase completion
- Release readiness validation
- Major milestone achievement
- Before major refactoring
- End of sprint/iteration
- Before production deployment

## When NOT to Use

- Every single commit (too granular)
- Work in progress
- Incomplete features
- Failed quality gates

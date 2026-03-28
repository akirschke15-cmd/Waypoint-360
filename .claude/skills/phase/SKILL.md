---
name: phase
description: Structured multi-phase build execution with parallel agents, integration checkpoints, phase commits, and progress tracking for complex projects.
origin: Boiler 3.0
version: 1.0
---

# Phase Execution Skill

Structured multi-phase build execution with parallel agents and checkpoints. Use this for any multi-step plan, build, audit, or migration.

## Inputs

The user will provide either:
- A phased plan (inline or referencing a doc in `docs/`)
- A high-level goal that needs to be broken into phases

## Workflow

### 1. Plan (skip if user provides a plan)
- Break the work into numbered phases with clear deliverables per phase.
- Identify which tasks within each phase can run in parallel vs. have dependencies.
- Persist the plan to `docs/phase-plan-<name>.md`.

### 2. Execute Each Phase
For each phase:

**a) Dispatch parallel agents** for all independent tasks within the phase. Use Task agents. Each agent gets:
- A specific scope (files, feature area, or concern)
- An output target (file to write, code to change, doc to produce)
- Instruction to not modify files outside its scope

**b) After all agents complete**, run integration checks:
```bash
npx tsc --noEmit
npm run test -- --passWithNoTests 2>&1 | tail -20
npm run build 2>&1 | tail -10
```

**c) If checks fail**, fix issues before moving on. Do not proceed with broken state.

**d) Checkpoint**: commit with message `Phase N: <description>` and update `docs/phase-progress.md`:
```
## Phase N: <name>
- Status: COMPLETE
- Files changed: <count>
- Tests passing: <count>
- Committed: <hash>
```

**e) Only then proceed to Phase N+1.**

### 3. Wrap Up
- Run full test suite and typecheck one final time.
- Update `docs/phase-progress.md` with final status.
- Report summary: phases completed, total files changed, total tests passing.

## Rules

- Never skip the checkpoint commit between phases. Rate limits and session drops are real. Committed work is safe work.
- If a phase has more than 6 parallel tasks, split into sub-phases to stay within agent limits.
- If the user says "continue" or "pick up where we left off," check `docs/phase-progress.md` first to find the last completed phase.
- All plans and progress docs go in `docs/`. Never keep them only in conversation.

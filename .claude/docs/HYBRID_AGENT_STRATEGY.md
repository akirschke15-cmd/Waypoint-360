# Hybrid Agent Strategy

This document explains when Claude should use **visible agent execution** (Task tool) vs. **silent context injection** (hooks) for optimal workflow visibility and efficiency.

---

## Critical Directive: Hook Agent Priority

**When a hook activates a specific agent, that is a DIRECTIVE, not a suggestion.**

### The Rule

IF hook injects agent context (e.g., "test-architect")
AND task is complex (requires visible execution)
THEN:
  OK Launch THE HOOK'S AGENT using Task tool
  WRONG DO NOT substitute with a different agent
  WRONG DO NOT make your own agent choice

### Example

User: "create a dashboard test strategy"

Hook output in system reminders:
  MARKED Auto-Activated Agents: test-architect

CORRECT behavior:
  Task(subagent_type="test-architect", ...)

WRONG behavior:
  Task(subagent_type="qa-engineer", ...)  // Different agent!
  No visible Task execution  // Hook output ignored!

---

## Hook vs. Task Tool Decision Tree

```
Does the hook directive match a complex task?
  -> YES: Launch visible Task tool with hook's agent
  -> NO: Treat hook output as context injection only
```

Examples:

| Hook Directive | Task Complexity | Action |
|---|---|---|
| "test-architect" | Implement full test suite | Launch Task(test-architect) |
| "security-auditor" | Quick security check comment | Inject context only |
| "backend-engineer" | Build API endpoints | Launch Task(backend-engineer) |
| "python-expert" | One-liner code fix | Inject context only |

---

## Visible Agent Execution (Task Tool)

Use when:
- Complex feature requiring agent focus
- Multi-file architectural decisions
- Specialization needed (design, security, performance)
- User explicitly requested agent involvement

Output: System reminders show agent activation and delegation

---

## Silent Context Injection (Hooks)

Use when:
- Quick guidance or best practices
- Single-file changes
- Linting or formatting suggestions
- No agent specialization needed

Output: System reminders may show context, but no Task tool invocation

---

## Priority Matrix

| Complexity | Specialization Needed | Action |
|---|---|---|
| Low | No | Inline work (no agent) |
| Low | Yes | Inject context (no Task tool) |
| High | No | Consider Task tool for clarity |
| High | Yes | MUST use Task tool with designated agent |

---

## When Hook Directives Conflict

If multiple hooks suggest different agents:

1. Evaluate task scope
2. Pick agent matching PRIMARY concern
3. Mention other agents in Task description as secondary
4. Let chosen agent coordinate

Example:
```
Hook A: "backend-engineer" (API design)
Hook B: "database-engineer" (schema design)

User wants: Full-stack feature with DB + API

Action: Task(subagent_type="backend-engineer",
  "Coordinate with database-engineer for schema changes")
```

---

## Testing the Strategy

Before marking a task complete, verify:

- [ ] Complex tasks have visible Task tool invocations
- [ ] Hook directives were followed or explicitly overridden with reasoning
- [ ] Agent choice matches task complexity
- [ ] Secondary concerns delegated or mentioned

---
name: AUTO-ACTIVATION
description: Automatic agent selection and routing based on task context
version: 1.0
---

# Automatic Agent Activation System

This system automatically routes tasks to the most appropriate agent based on context analysis and scoring heuristics. When you describe a task, the system evaluates it against agent activation criteria and selects the best match(es).

## Activation Scoring

Each agent has a relevance score (0-100) calculated from:

1. **Keyword Matching** (Weight: 40%)
   - Task keywords matched against agent domain keywords
   - Exact matches score higher than partial matches
   - Negation keywords reduce score

2. **Context Signals** (Weight: 35%)
   - Technology stack mentioned (language, framework, tool)
   - Phase of development (design, implementation, testing, deployment)
   - Problem type (bug, feature, performance, security)
   - Output type requested (code, tests, docs, architecture)

3. **Execution Requirements** (Weight: 15%)
   - Tools needed available to agent
   - Model capability required
   - Integration dependencies

4. **Historical Performance** (Weight: 10%)
   - Agent success rate on similar tasks
   - Feedback from previous runs

## Scoring Tiers

- **80-100**: Primary agent - invoke immediately
- **60-79**: Secondary agent - consider alongside primary
- **40-59**: Tertiary agent - may assist in specific aspects
- **0-39**: Not a match - skip

## Agent Selection Strategy

1. **Single High-Score Match** (>=80): Activate that agent
2. **Multiple Matches (>=80)**: Activate all, with highest score as lead
3. **No Matches >=80**: Use highest 60-79 score agent
4. **No Matches >=60**: Request clarification or manual selection

## Agent Activation Keywords & Triggers

### Planner
- Keywords: plan, timeline, roadmap, phases, milestones, estimate, breakdown, scope
- Context: Start of project, scope definition, feature planning
- Score boost: Multiple tasks mentioned, phase references

### Architect
- Keywords: design, architecture, system, structure, pattern, trade-off, scalability, reliability
- Context: Design phase, multi-component systems, cross-service concerns
- Score boost: "Distributed", "microservices", "high-traffic"

### Code Reviewer
- Keywords: review, audit, feedback, security, quality, standards, lint, best practices
- Context: PR/MR context, code quality concerns, security review
- Score boost: Security keywords, compliance context

### TDD Guide
- Keywords: test-driven, TDD, test first, coverage, unit test, integration test
- Context: Testing phase, test failure, coverage gaps
- Score boost: Low coverage indicated, QA phase

### Build Error Resolver
- Keywords: build fail, compile error, integration fail, ci/cd error, deployment fail
- Context: Build/test pipeline failure, error logs present
- Score boost: Stack trace provided, recent change context

### Security Reviewer
- Keywords: security, vulnerability, exploit, breach, penetration, OWASP, CVE, auth, encryption
- Context: Security audit, compliance check, vulnerability fix
- Score boost: Specific threat model mentioned, regulatory context

### Product Manager
- Keywords: requirements, user story, epic, use case, user journey, PRD, feature spec
- Context: Requirements gathering, feature planning, acceptance criteria
- Score boost: Stakeholder quotes, market research provided

### Frontend Engineer
- Keywords: UI, UX, React, frontend, component, styling, accessibility, responsive
- Context: Frontend development, client-side logic, component creation
- Score boost: React-specific, mobile/responsive mentioned

### Backend Engineer
- Keywords: API, database, backend, service, endpoint, query, scaling, distributed
- Context: Backend development, server logic, data layer
- Score boost: Microservices, distributed systems mentioned

### Fullstack Engineer
- Keywords: end-to-end, feature complete, integration, full stack, backend to frontend
- Context: Complete feature implementation needed, multiple layers involved
- Score boost: Multiple tech stack, tight deadline

### Python Expert
- Keywords: Python, FastAPI, Django, async, type hints, pandas, numpy
- Context: Python codebase, Python-specific problem
- Score boost: Python version specified, specific framework mentioned

### TypeScript Expert
- Keywords: TypeScript, generics, type, interfaces, Next.js, React, Node.js
- Context: TypeScript codebase, type-related issue
- Score boost: Advanced types, strict mode issues

### Terraform Expert
- Keywords: Terraform, IaC, infrastructure, cloud, AWS, GCP, Azure, Kubernetes
- Context: Infrastructure management, deployment automation
- Score boost: Multi-cloud, compliance context

### DevOps Engineer
- Keywords: CI/CD, pipeline, deployment, Docker, Kubernetes, monitoring, observability
- Context: Deployment issues, infrastructure operations
- Score boost: Production incident, scaling issue

### Technical Writer
- Keywords: documentation, API doc, README, guide, tutorial, specification, handbook
- Context: Documentation creation, user communication
- Score boost: Multiple audiences, API changes

### Debugger
- Keywords: bug, error, crash, fail, debug, issue, troubleshoot, trace, root cause
- Context: Problem diagnosis, error investigation, reproduction steps provided
- Score boost: Intermittent issue, production problem

### Performance Optimizer
- Keywords: performance, optimization, slow, bottleneck, profiling, latency, throughput
- Context: Performance improvement, benchmarking, optimization phase
- Score boost: Metrics provided, p99 latency context

## Multi-Agent Collaboration

When multiple agents activate (60+), they collaborate as follows:

1. **Primary Agent** (highest score): Leads task execution
2. **Supporting Agents** (60-79): Provide specialized reviews/checks
3. **Feedback Loop**: Supporting agents flag issues to primary for remediation

Example: Feature implementation may activate:
- Fullstack Engineer (85) - Lead
- TDD Guide (72) - Tests-first validation
- Security Reviewer (68) - Security checks
- Code Reviewer (65) - Quality review

## Manual Override

You can manually specify agents with: `/use <agent-name>`

Example: `/use python-expert` forces Python expert for a multi-language task

## Activation Disable

Disable auto-activation for specific agents:
- Add to task context: `@skip <agent-name>`
- Example: `@skip tdd-guide` for legacy code without tests

## Performance Metrics

The system tracks:
- Activation accuracy (correct agent selected)
- Task resolution time per agent
- User satisfaction (implicit from corrections)
- False positive rate (agent activated but not needed)

Metrics guide future scoring adjustments.

## Activation Logs

All auto-activations logged to `.claude/logs/activation.log`:
```
[2026-03-20T14:32:15Z] Task: "Implement user auth"
[2026-03-20T14:32:15Z] Matches: backend-engineer(87), fullstack-engineer(81), security-reviewer(74)
[2026-03-20T14:32:15Z] Selected: backend-engineer (lead)
[2026-03-20T14:32:15Z] Activated: fullstack-engineer, security-reviewer (supporting)
```

## Tuning Auto-Activation

If auto-activation consistently selects wrong agent:

1. Check keywords in agent definition
2. Verify task context clarity
3. Add negation keywords if needed
4. Document pattern in agent-rules.json

Example: If "testing" incorrectly activates TDD Guide instead of Debugger:
- Add negation: "test-driven" vs "testing-failure"
- Boost Debugger for "reproduce bug" keyword

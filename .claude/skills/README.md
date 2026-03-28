# Claude Code Skills - Boiler 4.0

This directory contains 24 reusable, project-scoped skills for AI-powered development workflows. Each skill encapsulates best practices, procedures, and decision trees for specific domains.

## Skill Categories

### Core Workflows (5 skills)

**phase** - Structured multi-phase build execution with parallel agents, integration checkpoints, phase commits, and progress tracking for complex projects. Use for multi-step plans, builds, audits, or migrations.

**commit** - Standardized commit workflow with type checking, test verification, and conventional commit message format. Run after completing a phase, feature, or batch of work.

**fix-loop** - Autonomous test-driven bug fix cycle with baseline capture, failure analysis, fix iteration, and regression checking. Point at failing tests and iterate until suite is green.

**security-audit** - Parallel multi-agent security review with scope definition, dispatch, finding consolidation, and fix round execution. Use for pre-deployment security sweeps or periodic audits.

**seed-safety** - Pre-flight checks and safe execution protocol for database seed scripts and migrations with verification and idempotency rules.

### Development Standards (4 skills)

**coding-standards** - Universal coding standards for TypeScript, JavaScript, React, and Node.js covering naming conventions, comment practices, function complexity, error handling, and linting.

**typescript-development** - TypeScript development patterns for type-safe applications including strict tsconfig setup, utility types, generic types, conditional types, React components with types, Express.js type safety, tRPC end-to-end typing, and Vitest patterns.

**python-development** - Comprehensive Python development guidance including project structure, type hints, Pydantic validation, testing with pytest, async patterns, and framework guidance for FastAPI, Django, and Flask.

**python-testing** - pytest patterns with fixtures, parametrization, markers, and mocking. Covers test structure, isolation, edge cases, and integration testing for Python projects.

### Testing & Quality (3 skills)

**tdd-workflow** - Red-green-refactor approach with 80%+ coverage requirements. Covers test structure, mocking patterns, edge cases, and integration testing.

**testing-best-practices** - Comprehensive testing strategies across Python, TypeScript, and infrastructure. Testing pyramid (70% unit, 20% integration, 10% E2E), parametrization, mocking patterns, coverage goals.

**e2e-testing** - Playwright patterns with Page Object Model, flaky test handling, artifact management, and best practices for end-to-end test automation.

**verification-loop** - 6-phase verification: Build, Type Check, Lint, Test, Security, Diff Review. Use for pre-commit verification and deployment gate checks.

### Architecture & Patterns (5 skills)

**api-design** - REST API design with resource naming, HTTP methods, pagination, versioning, error handling, and status codes. Guidelines for consistent API interfaces.

**backend-patterns** - Layered architecture: Routes -> Services -> Repositories. N+1 prevention, query optimization, middleware patterns, error handling, logging strategies.

**frontend-patterns** - React component composition, custom hooks, state management, performance optimization, testing patterns, and accessibility best practices.

**eval-harness** - Eval-driven development framework with pass@k metrics, evaluation harnesses, grading functions, and structured benchmark reporting for AI systems.

**continuous-learning-v2** - Instinct-based learning system v2.1 with project-scoped instincts. Maintains learned patterns, context-aware execution heuristics, and decision trees.

### Infrastructure & DevOps (3 skills)

**terraform-infrastructure** - Terraform IaC for multi-cloud deployments including provider configuration, variables and outputs with validation, VPC setup, EC2 with auto-scaling, RDS database, module development, state management, secrets management, least privilege IAM.

**deployment-patterns** - Deployment strategies (Rolling, Blue-Green, Canary), multi-stage Dockerfiles, CI/CD pipeline patterns, health checks, monitoring, and rollback strategies.

**autonomous-loops** - Loop hierarchy from Simple Sequential to RFC-Driven DAG. Use for automating complex, multi-step workflows with conditional branching and error recovery.

### Security & Review (1 skill)

**security-review** - Comprehensive 10-point security checklist covering secrets, input validation, injection prevention, authentication, XSS, CSRF, rate limiting, data exposure, blockchain security, and dependencies.

### Support & Maintenance (1 skill)

**strategic-compact** - Manual context compaction at logical phase boundaries. Use to summarize progress, consolidate learnings, and reset working context for long-running projects.

## Auto-Activation Rules

Skills activate automatically based on context, keywords, and project state. See `skill-rules.json` for trigger definitions.

### Common Triggers

| Trigger | Skills |
|---------|--------|
| `run test`, `test failed` | fix-loop, tdd-workflow, testing-best-practices |
| `commit code`, `git push` | commit, verification-loop |
| `build database`, `seed data` | seed-safety |
| `security review`, `audit` | security-audit, security-review |
| `multi-phase`, `build plan` | phase |
| `TypeScript`, `type errors` | typescript-development, coding-standards |
| `Python`, `pytest` | python-development, python-testing |
| `API design`, `REST endpoint` | api-design, backend-patterns |
| `React`, `component` | frontend-patterns, coding-standards |
| `infrastructure`, `Terraform` | terraform-infrastructure, deployment-patterns |
| `deployment`, `release` | deployment-patterns, verification-loop |

## Usage Examples

### Running a Phase-Based Build

```
Use the **phase** skill to structure a 3-phase project:
- Phase 1: Database schema and migrations (parallel: 2 agents)
- Phase 2: API endpoints and business logic (parallel: 3 agents)
- Phase 3: Frontend components and integration tests (parallel: 2 agents)

The skill handles dispatch, checkpoints, and progress tracking.
```

### Fixing Test Failures

```
Use the **fix-loop** skill:
1. Point it at the failing test
2. It captures baseline state
3. Analyzes root cause
4. Iterates fix-test-fix (max 3 iterations per cause)
5. Checks for regressions
6. Reports summary and commits
```

### Pre-Deployment Security Review

```
Use the **security-audit** skill:
1. Define 4 parallel review scopes (Auth, API, Database, Client-side)
2. Dispatch agents to each scope (read-only)
3. Agents write findings to separate docs
4. Consolidate into single report sorted by severity
5. Execute fix round for CRITICAL/HIGH findings
```

### Seeding a Database

```
Use the **seed-safety** skill:
1. Pre-flight checks: verify directory, baseline count, overlap detection
2. Run seed exactly once
3. Verify result: count should match expectations
4. If count is wrong, diagnose before re-running
```

## Skill Quality Standards

All skills in Boiler 4.0 meet these standards:

- **Specific, actionable steps** - No vague guidance; every skill has a step-by-step workflow
- **Constraint-aware** - Respects Claude's rate limits, context windows, and capabilities
- **Idempotent where possible** - Repeated runs don't cause harm
- **Verified outputs** - Each skill includes verification steps
- **Error recovery** - Clear paths for handling failures
- **Version tracked** - Each skill has a version number in frontmatter

## Organizing Your Project

Skills are stored in `.claude/skills/`. Each skill is a directory containing:
- `SKILL.md` - Complete skill definition
- Related files (templates, examples, configurations)

Skills are loaded automatically by Claude Code. To use a skill:
1. Reference it by name in your request (e.g., "Use the **fix-loop** skill")
2. It loads automatically based on your context
3. Or reference it explicitly in messages to Claude

## Extending Skills

To create a new skill:
1. Create a new directory in `.claude/skills/<skill-name>/`
2. Add `SKILL.md` with frontmatter (name, description, origin, version)
3. Follow the structure of existing skills
4. Update this README with the new skill
5. Add activation rules to `skill-rules.json`

## Boiler 4.0 Versions

- **15 ECC Skills** - Enterprise-grade patterns from ECC codebase
- **9 Boiler 3.0 Skills** - Phase execution, code quality, infrastructure patterns
- **Total: 24 Skills** - Comprehensive coverage for full-stack development

Skills are versioned independently. Check individual SKILL.md files for version history and origin documentation.

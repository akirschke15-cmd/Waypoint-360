---
name: eval
description: Evaluate system performance, test coverage, code quality metrics
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Eval Command

Route to the **Performance Optimizer** or **Code Reviewer** agent to evaluate system health, metrics, and quality standards.

## Usage

```
/eval [metric_or_system]
```

## Examples

### Example 1: Test Coverage Evaluation
```
/eval test-coverage
```

Response: Evaluator:
1. Runs coverage analysis
2. Identifies coverage gaps
3. Lists files below 80% threshold
4. Suggests tests to add
5. Provides coverage report

### Example 2: Performance Evaluation
```
/eval api-performance
```

Response: Evaluator:
1. Analyzes API response times
2. Identifies slow endpoints (p95, p99)
3. Profiles database queries
4. Suggests optimizations
5. Provides benchmark report

### Example 3: Code Quality Evaluation
```
/eval code-quality
```

Response: Evaluator:
1. Runs linting and static analysis
2. Identifies code smells
3. Checks style compliance
4. Validates best practices
5. Provides quality score

## Metrics Evaluated

- **Test Coverage**
  - Line coverage: 80%+ target
  - Branch coverage: 75%+ target
  - Uncovered critical paths
  - Flaky tests

- **Performance**
  - API p50/p95/p99 latency
  - Database query times
  - Bundle size and LCP (Largest Contentful Paint)
  - Memory usage and leaks

- **Code Quality**
  - Linting errors/warnings
  - Complexity metrics
  - Duplicate code
  - Security vulnerabilities

- **Architecture**
  - Dependency health
  - Module coupling
  - Circular dependencies
  - Layer violations

- **CI/CD**
  - Build success rate
  - Test pass rate
  - Deployment frequency
  - Incident rate

## Evaluation Output

- **Current State**: Metrics summary
- **Health Score**: Overall system health (0-100)
- **Gaps**: Where standards are not met
- **Priorities**: High-impact improvements
- **Trends**: Historical performance
- **Recommendations**: What to fix first

## Standards

All projects must meet:
- [ ] 80%+ test coverage
- [ ] API p95 < 200ms
- [ ] Linting 0 errors
- [ ] Zero critical security issues
- [ ] Build success rate > 99%

## Evaluation Cadence

- **Per commit**: Quick linting check
- **Per PR**: Full code review + coverage
- **Daily**: Performance and stability
- **Weekly**: Comprehensive metrics report
- **Monthly**: Trend analysis and planning

## When to Use

- Before marking feature complete
- Regular health check
- Performance degradation suspected
- Regression testing
- Project handoff verification
- Quarterly planning

## When NOT to Use

- Active development (low coverage expected)
- Spike/exploratory work
- Proof of concept
- Before code written

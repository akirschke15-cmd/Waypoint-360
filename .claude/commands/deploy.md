---
name: deploy
description: Deploy code to staging or production with safety checks and rollback capability
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
model: sonnet
---

# Deploy Command

Route to the **DevOps Engineer** agent to safely deploy code with verification and rollback capability.

## Usage

```
/deploy <environment> [--dry-run] [--rollback] [--monitor]
```

## Examples

### Example 1: Staging Deployment
```
/deploy staging --dry-run
```

Response: DevOps Engineer:
1. Validates deployment readiness
2. Shows changes to be deployed
3. Dry-runs deployment steps
4. Verifies health checks will pass
5. Reports any issues

### Example 2: Production Deployment
```
/deploy production --monitor
```

Response: DevOps Engineer:
1. Executes final pre-deployment checks
2. Deploys with canary strategy
3. Monitors error rates and latency
4. Validates metrics post-deploy
5. Alerts if issues detected

### Example 3: Rollback
```
/deploy production --rollback
```

Response: DevOps Engineer:
1. Identifies last stable deployment
2. Initiates rollback process
3. Verifies services healthy
4. Validates rollback complete

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code review approved
- [ ] Quality gates passed
- [ ] Migration scripts validated (if DB changes)
- [ ] Environment variables configured
- [ ] Secrets properly configured
- [ ] Monitoring and alerts ready
- [ ] Rollback plan documented
- [ ] Communication sent to team

## Deployment Strategies

- **Blue-Green**: Two identical production environments
- **Canary**: Gradual rollout to percentage of users
- **Rolling**: Update instances one-by-one
- **Feature Flags**: Deploy code, enable features gradually

## Post-Deployment Validation

- [ ] Service health checks passing
- [ ] Error rates within normal range
- [ ] Latency within normal range
- [ ] Database migrations successful (if applicable)
- [ ] No critical alerts firing
- [ ] Users reporting no major issues

## Monitoring During Deployment

Track metrics:
- **Latency**: p50, p95, p99 response times
- **Errors**: Error rate and 5xx responses
- **Throughput**: Requests per second
- **Resource Usage**: CPU, memory, disk
- **Dependencies**: Database, external APIs

## Rollback Triggers

Automatically rollback if:
- Error rate spikes >5% above baseline
- p99 latency >2x baseline
- Service unavailable (5xx >1%)
- Critical alert triggered
- Health check failures

## Environments

### Staging
- Mirrors production
- Safe testing ground
- Canary deployment validation
- Load testing environment

### Production
- Live user traffic
- High availability required
- Blue-green deployment strategy
- Continuous monitoring

## Deployment Windows

- **Standard**: Business hours, staff available
- **Emergency**: Anytime, for critical fixes
- **Off-Hours**: Restricted, only for non-critical updates

## Rollback Procedure

1. **Detect**: Issue identified in monitoring
2. **Verify**: Confirm issue related to deployment
3. **Approve**: Tech lead approval required
4. **Execute**: Rollback to previous version
5. **Validate**: Verify services healthy
6. **Communicate**: Update team and users

## Metrics and Reporting

After deployment:
- [ ] Deployment duration documented
- [ ] Any issues or anomalies noted
- [ ] Rollback history tracked
- [ ] Lessons learned captured
- [ ] Performance impact measured

## When to Use

- Code ready for release
- Feature rollout
- Bug fix deployment
- Infrastructure updates
- Database migrations

## When NOT to Use

- Work in progress
- Incomplete features
- Failed tests
- Failed quality gates
- No rollback plan

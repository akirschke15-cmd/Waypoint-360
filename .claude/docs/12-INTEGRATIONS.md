# Waypoint 360 - Integrations

## Current State (v1)

**No external integrations yet.** All data is local SQLite. External integrations are planned for Phase 4+.

## Stubbed / Future Integrations

### Confluence API (Planned Phase 4)

**Purpose**: Sync Waypoint RAID log to Confluence, read/write status updates in real time.

**Auth**: OAuth 2.0 via Atlassian Cloud

**Environment Variables**
```env
CONFLUENCE_DOMAIN=your-company.atlassian.net
CONFLUENCE_USERNAME=api-user@company.com
CONFLUENCE_API_TOKEN=<base64-encoded-token>
CONFLUENCE_SPACE_KEY=WAYPOINT
```

**Endpoints Used**
```
GET  /wiki/rest/api/content/{page_id}
POST /wiki/rest/api/content/{page_id}/child
PUT  /wiki/rest/api/content/{page_id}
```

**Sync Pattern**
```python
# Read RAID log from Confluence page
GET /confluence/sync?page_id=123
Response: { risks: [...], assumptions: [...], status: "synced" }

# Write workstream status update to Confluence
POST /confluence/sync
Body: { page_id: 123, workstream_id: "WS-001", status: "on_track" }
```

**Failure Handling**
- Sync timeout > 10 sec: Show notification "Confluence sync delayed, will retry"
- Confluence down (503): Show banner "Confluence unavailable, status not synced"
- Permission denied (403): Show error "Check Confluence API token permissions"
- Retry logic: Exponential backoff 1s → 2s → 4s → 30s max

### Jira API (Planned Phase 4)

**Purpose**: Import/export deliverable status, sync sprint data, create issues for risks.

**Auth**: OAuth 2.0 or API Token

**Environment Variables**
```env
JIRA_INSTANCE=https://company.atlassian.net
JIRA_USERNAME=api-user@company.com
JIRA_API_TOKEN=<token>
JIRA_PROJECT_KEY=WAYPOINT
```

**Endpoints Used**
```
GET    /rest/api/3/issues?jql=...
POST   /rest/api/3/issues
PUT    /rest/api/3/issues/{key}
GET    /rest/api/3/sprints/{board_id}/issues
```

**Sync Pattern**
```python
# Fetch deliverables from Jira sprint
GET /jira/sync/sprints?board_id=123
Response: { deliverables: [...], status: "synced" }

# Push workstream risk as Jira issue
POST /jira/sync/issues
Body: { risk_id: "R-001", title: "Risk title", severity: "critical" }
Response: { issue_key: "WAYPOINT-456" }

# Update Jira issue status from Waypoint
PUT /jira/sync/issues/{issue_key}
Body: { status: "in_progress" }
```

**Failure Handling**
- Jira token expired: Show "Jira token expired. Please re-authenticate."
- Rate limit (429): Retry with exponential backoff
- Missing project key: Show setup error "Configure JIRA_PROJECT_KEY"

### Slack (Planned Phase 4)

**Purpose**: Post gate readiness notifications, workstream status changes, risk escalations.

**Auth**: OAuth 2.0 Slack Bot Token

**Environment Variables**
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=<secret>
SLACK_CHANNEL_WAYPOINT=#waypoint-status
SLACK_CHANNEL_ALERTS=#waypoint-alerts
```

**Webhook Patterns**

**Gate Readiness Notification**
```python
# POST to Slack when gate transitions to "at_risk"
POST /slack/notify
Body: {
  event: "gate_readiness_changed",
  gate_id: "G-001",
  status: "at_risk",
  channel: "#waypoint-status"
}

# Slack message:
# 🟡 Gate 2 is now AT RISK
# Technical: On Track | Business: At Risk | Governance: Complete
# View dashboard: https://waypoint360.example.com/gates/G-001
```

**Workstream Status Change**
```python
POST /slack/notify
Body: {
  event: "workstream_status_changed",
  workstream_id: "WS-001",
  old_status: "on_track",
  new_status: "blocked",
  channel: "#waypoint-alerts"
}

# Slack message:
# 🔴 Workstream "Backend Infrastructure" is BLOCKED
# Owner: Alex K. | Dependencies: 2 blocked
# Action: Requires unblocking WS-002, WS-003
```

**Risk Escalation**
```python
POST /slack/notify
Body: {
  event: "risk_escalated",
  risk_id: "R-001",
  severity: "critical",
  channel: "#waypoint-alerts"
}

# Slack message:
# 🔴 CRITICAL RISK: API Connectivity Blocker
# Impact: 5 | Likelihood: 5 | Gate Impact: G-001, G-002
# Assigned: Tess M. | Mitigation: Scheduled for week of 4/7
```

**Slack Webhook Signing Verification**
```python
def verify_slack_signature(request):
    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    signature = request.headers.get('X-Slack-Signature')

    # Reject if >5 min old (replay protection)
    if abs(time.time() - int(timestamp)) > 300:
        return False

    # Verify HMAC
    sig_basestring = f"v0:{timestamp}:{request.body}"
    expected_sig = f"v0={hmac.new(SLACK_SIGNING_SECRET, sig_basestring, hashlib.sha256).hexdigest()}"
    return hmac.compare_digest(expected_sig, signature)
```

**Failure Handling**
- Slack token invalid: Show "Slack integration disabled, check token"
- Channel not found: Show "Configure SLACK_CHANNEL_WAYPOINT"
- Rate limit: Queue notifications, batch send on cooldown

### AWS CloudWatch (Planned Phase 4)

**Purpose**: Stream OTel telemetry from LangGraph traces for AgentOps monitoring.

**Auth**: IAM role (EC2 instance profile or STS AssumeRole)

**Environment Variables**
```env
AWS_REGION=us-east-1
OTEL_EXPORTER_OTLP_ENDPOINT=https://cloudwatch.us-east-1.amazonaws.com/opentelemetry
AWS_CLOUDWATCH_LOG_GROUP=/aws/waypoint360/application
AWS_CLOUDWATCH_LOG_STREAM=langgraph-traces
```

**OTel Integration**
```python
from opentelemetry import trace
from opentelemetry.exporter.awsxray.trace_exporter import AWSXRayExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

exporter = AWSXRayExporter()
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))

# Trace LangGraph node execution
tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span("langgraph_node_execution") as span:
    span.set_attribute("node_name", "ai_chat_node")
    span.set_attribute("input_tokens", 150)
    result = await langgraph_node(state)
    span.set_attribute("output_tokens", 250)
```

**Metrics Sent to CloudWatch**
- Latency per span (AI node, database query, API call)
- Token cost per trace (input + output tokens × model pricing)
- Error rate per node type
- Retry frequency per operation

**Failure Handling**
- CloudWatch connection timeout: Log locally, continue (no blocking)
- IAM permission denied: Show warning "CloudWatch export disabled, check IAM role"
- Data too large: Batch traces, ship in chunks

### Claude API (Anthropic) - Current v1

**Purpose**: LangGraph AI node execution for chat queries.

**Auth**: Bearer token in header

**Environment Variables**
```env
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL=claude-sonnet-4-20250514
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.7
```

**API Contract**
```python
POST https://api.anthropic.com/v1/messages
Body: {
  model: "claude-sonnet-4-20250514",
  messages: [{ role: "user", content: "What is the status of Gate 1?" }],
  max_tokens: 4096,
  system: "You are a Waypoint 360 assistant..."
}

Response: {
  id: "msg-123",
  type: "message",
  content: [{ type: "text", text: "Gate 1 is on track..." }],
  usage: { input_tokens: 150, output_tokens: 250 }
}
```

**Streaming**
```python
# Use streaming for real-time token delivery
POST https://api.anthropic.com/v1/messages
Header: "Accept: text/event-stream"
Body: { model: "...", stream: true, ... }

# Response stream (Server-Sent Events):
data: {"type":"content_block_start","content_block":{"type":"text"}}
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Gate"}}
data: {"type":"content_block_delta","delta":{"type":"text_delta","text":" 1"}}
...
data: {"type":"message_stop"}
```

**Error Handling**
- Invalid API key (401): Show "Claude API key invalid. Check ANTHROPIC_API_KEY."
- Rate limit (429): Retry with exponential backoff, show "Pausing queries, will resume shortly"
- Token limit exceeded: Show "Query response too large. Please rephrase question more specifically."
- Timeout > 30 sec: Allow user to cancel, show "Query taking longer than expected"

## MCP Endpoints (Future - Phase 4)

**Purpose**: Tool-call interface for all external integrations via Model Context Protocol.

**Server Endpoints** (SWA will host)
```
/mcp/confluence    - Read/write RAID log to Confluence
/mcp/jira          - Sync deliverables, create risk issues
/mcp/slack         - Post notifications to Slack
/mcp/cloudwatch    - Stream metrics to CloudWatch
/mcp/servicenow    - Potential future integration
```

**Tool Definitions** (what Claude can call)
```python
{
  "name": "read_confluence_raid",
  "description": "Fetch RAID log from Confluence page",
  "inputSchema": {
    "type": "object",
    "properties": {
      "page_id": { "type": "string", "description": "Confluence page ID" }
    },
    "required": ["page_id"]
  }
}

{
  "name": "create_jira_issue",
  "description": "Create a Jira issue for a risk",
  "inputSchema": {
    "type": "object",
    "properties": {
      "risk_id": { "type": "string" },
      "title": { "type": "string" },
      "severity": { "enum": ["low", "medium", "high", "critical"] }
    },
    "required": ["risk_id", "title", "severity"]
  }
}

{
  "name": "post_slack_message",
  "description": "Send notification to Slack channel",
  "inputSchema": {
    "type": "object",
    "properties": {
      "channel": { "type": "string", "description": "#channel-name" },
      "message": { "type": "string" },
      "blocks": { "type": "array", "description": "Slack block kit objects" }
    },
    "required": ["channel", "message"]
  }
}
```

**Claude → MCP → SWA Backend Flow**
```
Claude AI node generates tool call → MCP server receives → SWA backend /integrations endpoint → External service
```

## Webhook Patterns

### Incoming Webhooks (External → Waypoint)

**Confluence Webhook**: Page updated
```python
POST /webhooks/confluence
Header: X-Atlassian-Signature
Body: {
  event: "page.updated",
  page_id: "123",
  content: "Gate 2 Risk: API connectivity issue..."
}

# Waypoint syncs RAID log
Response: { status: "synced", risks_updated: 2 }
```

**Jira Webhook**: Issue status changed
```python
POST /webhooks/jira
Header: X-Atlassian-Signature
Body: {
  event: "jira:issue_updated",
  issue_key: "WAYPOINT-456",
  fields: { status: { name: "In Progress" } }
}

# Waypoint updates deliverable status
Response: { status: "updated", deliverable_id: "D-001" }
```

**Slack Webhook**: Event callback
```python
POST /webhooks/slack
Header: X-Slack-Signature
Body: {
  type: "event_callback",
  event: { type: "app_mention", user: "U123", text: "status update" }
}

# Waypoint responds with interactive block actions
```

### Outgoing Webhooks (Waypoint → External)

All outgoing integrations use HTTPS POST with exponential backoff retry:
- Immediate retry: 1 sec
- Second retry: 2 sec
- Third retry: 4 sec
- Max: 30 sec, then fail with logged error

**Retry Logic**
```python
async def send_webhook(url: str, payload: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                if response.status_code in [200, 201, 202]:
                    return response
                if response.status_code >= 500:
                    # Transient error, retry
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    # Client error, fail immediately
                    raise HTTPException(response.status_code)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Webhook failed: {url}, {e}")
                return None
            await asyncio.sleep(2 ** attempt)
```

## Environment Variables (Complete List)

### Core Application
```env
# Database
DATABASE_URL=sqlite+aiosqlite:////tmp/waypoint360.db
# Production: postgresql+asyncpg://user:password@host/dbname

# API
SECRET_KEY=<random-256-bit-key>
ALLOWED_ORIGINS=http://localhost:5173,https://waypoint360.example.com
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### Claude API
```env
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL=claude-sonnet-4-20250514
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.7
```

### Confluence (Phase 4)
```env
CONFLUENCE_DOMAIN=your-company.atlassian.net
CONFLUENCE_USERNAME=api-user@company.com
CONFLUENCE_API_TOKEN=<base64-encoded>
CONFLUENCE_SPACE_KEY=WAYPOINT
```

### Jira (Phase 4)
```env
JIRA_INSTANCE=https://company.atlassian.net
JIRA_USERNAME=api-user@company.com
JIRA_API_TOKEN=<token>
JIRA_PROJECT_KEY=WAYPOINT
```

### Slack (Phase 4)
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=<secret>
SLACK_CHANNEL_WAYPOINT=#waypoint-status
SLACK_CHANNEL_ALERTS=#waypoint-alerts
```

### AWS (Phase 4)
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
OTEL_EXPORTER_OTLP_ENDPOINT=https://cloudwatch.us-east-1.amazonaws.com/opentelemetry
AWS_CLOUDWATCH_LOG_GROUP=/aws/waypoint360/application
AWS_CLOUDWATCH_LOG_STREAM=langgraph-traces
```

### Testing
```env
DATABASE_URL=sqlite+aiosqlite:///:memory:
ANTHROPIC_API_KEY=mock-key-for-tests
ENVIRONMENT=test
```

## Integration Readiness Checklist

- [ ] Environment variables documented in `.env.example`
- [ ] Secrets are never logged or printed
- [ ] Failing integrations don't crash the app (graceful degradation)
- [ ] Retry logic uses exponential backoff (no thundering herd)
- [ ] Webhook signatures verified (HMAC, timestamp validation)
- [ ] Integration errors show user-friendly messages
- [ ] Integration endpoints have unit tests with mocked services
- [ ] Rate limiting respected for external APIs
- [ ] Timeout set <30 sec for all external calls
- [ ] Monitoring/alerting configured for integration failures
- [ ] Documentation updated with new integrations

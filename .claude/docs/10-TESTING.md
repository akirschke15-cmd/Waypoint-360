# Waypoint 360 - Testing Strategy

## Overview

Waypoint 360 uses a structured testing pyramid across three layers: unit (70%), integration (20%), and E2E (10%). Tests are implemented incrementally with no tests written at project inception—testing is Phase 3/4 work.

## Testing Frameworks

### Backend
- **Unit & Integration**: pytest + pytest-asyncio for async SQLAlchemy tests
- **API Testing**: httpx for endpoint testing (FastAPI TestClient)
- **Async Support**: pytest-asyncio for async context, ORM session management, LangGraph node execution tests

### Frontend
- **Component Testing**: Vitest + React Testing Library
- **E2E Testing**: Playwright (browser automation, full user flows)
- **No Snapshot Tests**: Component-level validation only; UI snapshot tests deferred to Phase 4

### CI/CD
- **Pipeline**: GitHub Actions (planned, not yet configured)
- **Trigger**: Push to main, pull requests
- **Artifacts**: Test reports, coverage reports, build logs

## Testing Pyramid

### Unit Tests (70%)
Target coverage: 85% for core models and utilities.

**Backend Model Validation**
- Enum validation: GateStatus, RiskSeverity, PersonRole, WorkstreamStatus
- State machine transitions: Valid and invalid gate state progressions
- Gate readiness calculation: Combining Technical/Business/Governance readiness dimensions
- Risk severity scoring: Impact × Likelihood scoring logic
- Scope change detection: Comparing old vs. new scope_in arrays

**Backend Business Logic**
- Workstream status inference: Infer status from deliverable completion
- Dependency graph construction: Building the dependency graph from workstream relationships
- Gate exit criteria aggregation: Collecting pass/fail criteria per gate
- Person workstream assignment: Validation of person-to-workstream cardinality

**Utilities**
- Date formatting: ISO 8601 with timezone handling
- Array utilities: Split on null, deduplicate, safe indexing
- Enum helpers: String-to-enum conversion with fallback

**Example Test Structure (pytest)**
```python
@pytest.mark.asyncio
async def test_gate_readiness_all_dimensions_met():
    gate = Gate(
        technical_readiness="complete",
        business_readiness="complete",
        governance_readiness="complete"
    )
    assert gate.is_ready() == True

def test_risk_severity_scoring():
    risk = Risk(impact=4, likelihood=3)  # High impact, medium likelihood
    assert risk.severity_score() == 12

def test_enum_validation_invalid_status():
    with pytest.raises(ValueError):
        status = GateStatus("invalid_value")
```

### Integration Tests (20%)
Target coverage: 80% for API endpoints, 75% for database operations.

**API Endpoint Tests**
- GET /program: Returns program data with nested workstreams, gates, risks
- POST /program/seed: Loads seed data, creates all tables, returns success status
- GET /program/workstreams: Lists all workstreams with correct filtering
- PATCH /program/workstreams/{id}: Updates scope_in, validates dependency consistency
- GET /program/gates: Returns gate matrix with readiness aggregated
- GET /program/risks: Returns risk heatmap sorted by severity
- POST /program/chat: Sends LangGraph query, returns streaming response
- DELETE /program/reset: Clears all data, validates empty state

**Database Operations**
- Seed data loads: All 13 workstreams, 4 gates, 8 risks, 10 people load correctly
- SQLAlchemy session management: Async context, transactional rollback on error
- Relationship cascades: Deleting workstream cascades to deliverables, risks
- Foreign key constraints: Invalid workstream_id rejected
- NULL handling: Null scope_in splits safely, null notes handled in risk

**LangGraph Node Tests**
- AI chat node produces valid output: JSON response with message field
- Error handling: Malformed API key returns error message instead of crashing
- Token counting: Response includes token cost estimate
- Streaming: Response yields individual tokens in real time

**Example Test Structure (pytest + httpx)**
```python
@pytest.mark.asyncio
async def test_api_get_program():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/program")
        assert response.status_code == 200
        data = response.json()
        assert "workstreams" in data
        assert len(data["workstreams"]) == 13

@pytest.mark.asyncio
async def test_seed_data_loads():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/program/seed")
        assert response.status_code == 200

        # Verify all tables populated
        workstreams = await client.get("/program/workstreams")
        assert len(workstreams.json()) == 13
```

### E2E Tests (10%)
Target coverage: 100% for critical user flows.

**Full User Flows**
- Dashboard loads with seeded data: Page renders without JS errors, all sections visible
- Navigate to workstream detail: Click workstream card, detail page loads with correct data
- Gate timeline renders matrix: All gates visible, readiness colors correct, click filters
- Dependency graph renders D3: Graph initializes, no console errors, pan/zoom works
- AI chat sends query and displays response: Type message, submit, response appears inline
- Theme toggle works: Light/dark mode switches, persists in localStorage
- Empty state displays: Pre-seed shows seed prompt, post-delete shows empty states
- Error recovery: Connection error shows retry button, succeeds on retry

**Example Test Structure (Playwright)**
```javascript
test('Dashboard loads with seeded data', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.waitForLoadState('networkidle');

  // Verify all sections rendered
  await expect(page.locator('[data-testid="workstream-grid"]')).toBeVisible();
  await expect(page.locator('[data-testid="gate-timeline"]')).toBeVisible();
  await expect(page.locator('[data-testid="dependency-graph"]')).toBeVisible();
});

test('AI chat sends query and displays response', async ({ page }) => {
  await page.goto('http://localhost:5173');
  await page.fill('[data-testid="chat-input"]', 'What is the status of Gate 1?');
  await page.click('[data-testid="chat-send"]');

  // Wait for response to appear
  await expect(page.locator('[data-testid="chat-message"]')).toContainText(/Gate 1|status/i);
});
```

## Test Organization

### Backend (`tests/` Directory)
```
tests/
├── unit/
│   ├── test_models.py        # Enum, state, calculation tests
│   ├── test_business_logic.py # Status inference, scoring
│   └── test_utils.py          # Utilities, helpers
├── integration/
│   ├── test_api.py            # All endpoint tests
│   ├── test_database.py       # SQLAlchemy, ORM tests
│   └── test_langgraph.py      # AI node tests
└── fixtures.py                # Shared pytest fixtures, seeded data
```

### Frontend (`src/__tests__/` Directory)
```
src/__tests__/
├── components/
│   ├── Dashboard.test.tsx
│   ├── WorkstreamDetail.test.tsx
│   ├── GateTimeline.test.tsx
│   ├── DependencyGraph.test.tsx
│   └── ChatPanel.test.tsx
├── integration/
│   └── e2e.spec.ts            # Playwright tests
└── utils.test.ts              # Utility function tests
```

## Test Fixtures and Seeding

### Pytest Fixtures
```python
@pytest.fixture
async def db():
    """In-memory SQLite for tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()

@pytest.fixture
async def seeded_db(db):
    """Seed with Waypoint 360 test data."""
    async with AsyncSession(db) as session:
        # Load seed_data.json, create all fixtures
        await session.execute(insert(Workstream).values([...]))
        await session.execute(insert(Gate).values([...]))
        await session.commit()
    return db

@pytest.fixture
async def client(seeded_db):
    """FastAPI TestClient with seeded data."""
    async with httpx.AsyncClient(app=app, base_url="http://test") as c:
        yield c
```

## Coverage Targets

| Layer       | Target | Tool     | Threshold |
|-------------|--------|----------|-----------|
| Unit        | 85%    | pytest   | Fail CI if <80% |
| Integration | 80%    | pytest   | Fail CI if <75% |
| E2E         | 100%   | Playwright | Fail CI if any fail |
| Overall     | 82%    | Coverage.py | Fail CI if <80% |

## CI/CD Pipeline (GitHub Actions)

### Workflow: `.github/workflows/test.yml`
```yaml
name: Test

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements-test.txt
      - run: pytest tests/unit tests/integration --cov --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:unit
      - run: npm run test:e2e
```

### Coverage Reports
- Uploaded to Codecov after each push
- Badge added to README showing current coverage %
- Coverage diff in PR comments

## Test Execution Commands

### Local Development
```bash
# Backend
pytest tests/unit                    # Unit tests only
pytest tests/integration             # Integration tests only
pytest tests/unit tests/integration  # All backend tests
pytest --cov=app tests/              # With coverage report

# Frontend
npm run test:unit                    # Vitest component tests
npm run test:e2e                     # Playwright E2E tests
npm run test:watch                   # Watch mode
```

### Pre-commit Hook
```bash
#!/bin/bash
# .husky/pre-commit
pytest tests/unit -q || exit 1
npm run test:unit -- --run || exit 1
```

## Test Data and Scenarios

### Seed Data (seed_data.json)
- 13 workstreams spanning 4 gates
- 4 gates with varying readiness states
- 8 risks with severity distribution
- 10 people assigned to workstreams
- 3 workstreams with dependencies
- Mix of complete, at-risk, and blocked statuses

### Test Scenarios by Feature
- **Scope Changes**: Workstream A scope_in changes from [D1, D2] to [D1, D3]; validate dependency updates
- **Gate Transitions**: Force invalid transition (Blocked → Complete); expect validation error
- **Circular Dependencies**: Manually insert A→B, B→C, C→A; detect and alert
- **Null Handling**: Workstream with scope_in=null, risk with notes=null; verify safe access
- **Person Assignment**: One person assigned to 3 workstreams; verify cardinality, display
- **Empty Workstream**: Workstream with 0 deliverables; show placeholder UI, no 500 errors
- **Dependency Graph**: 0 dependencies; show "No dependencies" message, not empty D3

## Known Testing Gaps (Phase 3/4)

- [ ] No performance/load testing (scale to 100+ workstreams)
- [ ] No accessibility testing (WCAG 2.1 AA compliance)
- [ ] No visual regression testing (Chromatic/Percy)
- [ ] No mutation testing (Stryker)
- [ ] No security testing (OWASP Top 10)
- [ ] No database backup/restore testing
- [ ] No multi-user concurrency testing

## Success Criteria

- All test suites run in <5 min (CI)
- Coverage stays above 80% (code changes)
- No flaky tests (all tests pass consistently)
- E2E tests pass on Chrome, Firefox, Safari
- All error paths tested (400, 404, 500 scenarios)
- Seed data loads in <1 sec

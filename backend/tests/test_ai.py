"""Tests for AI endpoints and LangGraph graph compilation."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


# ---------------------------------------------------------------------------
# AI endpoint tests -- all expect 503 when ANTHROPIC_API_KEY is not set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ai_query_no_api_key(seeded_db, auth_headers):
    """POST /api/v1/ai/query returns 503 when ANTHROPIC_API_KEY is absent."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/ai/query",
            json={"query": "Which workstreams are most at risk for gate 1?"},
            headers=auth_headers,
        )

    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_gate_readiness_no_api_key(seeded_db, auth_headers):
    """GET /api/v1/ai/gate-readiness/{gate_id} returns 503 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        gates_resp = await client.get("/api/v1/gates/", headers=auth_headers)
        gate_id = gates_resp.json()[0]["id"]

        resp = await client.get(
            f"/api/v1/ai/gate-readiness/{gate_id}",
            headers=auth_headers,
        )

    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_scope_creep_no_api_key(seeded_db, auth_headers):
    """GET /api/v1/ai/scope-creep returns 503 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ai/scope-creep", headers=auth_headers)

    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_risks_correlated_no_api_key(seeded_db, auth_headers):
    """GET /api/v1/ai/risks/correlated returns 503 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ai/risks/correlated", headers=auth_headers)

    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_summary_no_api_key(seeded_db, auth_headers):
    """GET /api/v1/ai/summary returns 503 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ai/summary", headers=auth_headers)

    assert resp.status_code == 503
    assert "ANTHROPIC_API_KEY" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# LangGraph graph compilation test (no DB / no API key needed)
# ---------------------------------------------------------------------------

def test_graph_compiles():
    """The LangGraph StateGraph must compile without errors."""
    from app.ai.graph import build_waypoint_graph

    graph = build_waypoint_graph()
    # A compiled graph exposes an `ainvoke` coroutine
    assert callable(getattr(graph, "ainvoke", None)), (
        "Compiled graph must expose an ainvoke method"
    )


def test_graph_state_schema():
    """WaypointAnalysisState TypedDict must contain all expected keys."""
    from app.ai.state import WaypointAnalysisState
    import typing

    hints = typing.get_type_hints(WaypointAnalysisState)
    required_keys = {
        "query",
        "query_type",
        "workstream_data",
        "dependency_graph",
        "gate_data",
        "analysis_results",
        "recommendations",
        "summary",
    }
    for key in required_keys:
        assert key in hints, f"Missing key '{key}' in WaypointAnalysisState"

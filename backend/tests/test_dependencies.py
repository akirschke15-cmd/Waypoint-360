"""Tests for dependency graph endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_list_dependencies_graph(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/dependencies/", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()

    # D3 force-directed format: nodes + links
    assert "nodes" in body
    assert "links" in body

    assert len(body["nodes"]) == 10  # 10 workstreams seeded
    # Seed data creates 14 dependencies
    assert len(body["links"]) >= 1

    node = body["nodes"][0]
    assert "id" in node
    assert "name" in node
    assert "short_name" in node
    assert "status" in node

    link = body["links"][0]
    assert "id" in link
    assert "source" in link
    assert "target" in link
    assert "criticality" in link
    assert "status" in link


@pytest.mark.asyncio
async def test_get_critical_path(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/dependencies/critical-path", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert "critical_dependencies" in body
    assert "high_dependencies" in body
    assert "blocked_or_at_risk" in body
    assert isinstance(body["blocked_or_at_risk"], list)

    # Seed data uses only OPEN status, so blocked_or_at_risk should be empty
    assert body["blocked_or_at_risk"] == []
    # But critical and high counts should be > 0
    assert body["critical_dependencies"] > 0 or body["high_dependencies"] > 0


@pytest.mark.asyncio
async def test_create_dependency(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ws_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstreams = ws_resp.json()
        source_id = workstreams[0]["id"]
        target_id = workstreams[1]["id"]

        gates_resp = await client.get("/api/v1/gates/", headers=auth_headers)
        gate_id = gates_resp.json()[0]["id"]

        payload = {
            "source_workstream_id": source_id,
            "target_workstream_id": target_id,
            "gate_id": gate_id,
            "description": "Source workstream needs approval from target before proceeding",
            "dep_type": "needs_from",
            "criticality": "high",
        }
        resp = await client.post("/api/v1/dependencies/", json=payload, headers=auth_headers)

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["source_workstream_id"] == source_id
    assert body["target_workstream_id"] == target_id
    assert body["dep_type"] == "needs_from"
    assert body["criticality"] == "high"
    assert body["status"] == "open"


@pytest.mark.asyncio
async def test_update_dependency(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List existing dependencies then pick the first link's id
        graph_resp = await client.get("/api/v1/dependencies/", headers=auth_headers)
        dep_id = graph_resp.json()["links"][0]["id"]

        resp = await client.put(
            f"/api/v1/dependencies/{dep_id}",
            json={"status": "resolved", "notes": "Dependency met at gate review"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == dep_id
    assert body["status"] == "resolved"
    assert body["notes"] == "Dependency met at gate review"

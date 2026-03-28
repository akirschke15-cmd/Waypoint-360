"""Tests for workstream CRUD endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_list_workstreams(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/workstreams/", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Seed data has 10 workstreams
    assert len(body) == 10

    # Verify summary shape for the first item
    first = body[0]
    assert "id" in first
    assert "name" in first
    assert "status" in first
    assert "risk_count" in first
    assert "deliverable_count" in first


@pytest.mark.asyncio
async def test_get_workstream_detail(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get the list first to obtain a valid ID
        list_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstream_id = list_resp.json()[0]["id"]

        resp = await client.get(f"/api/v1/workstreams/{workstream_id}", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == workstream_id
    assert "name" in body
    assert "purpose" in body
    assert "scope_in" in body
    assert "scope_out" in body
    assert "deliverables" in body
    assert "risks" in body
    assert "decisions" in body
    assert "needs_from" in body
    assert "provides_to" in body


@pytest.mark.asyncio
async def test_get_workstream_not_found(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/workstreams/99999", headers=auth_headers)

    assert resp.status_code == 404
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_create_workstream(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Need a valid program_id -- fetch the first workstream's program from the list
        list_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        first_ws_id = list_resp.json()[0]["id"]
        detail_resp = await client.get(f"/api/v1/workstreams/{first_ws_id}", headers=auth_headers)
        # program_id is not in the workstream response directly, so use 1 (seeded)
        program_id = 1

        payload = {
            "program_id": program_id,
            "name": "Test Workstream",
            "short_name": "TestWS",
            "purpose": "Validate test creation flow",
            "scope_in": "All test scenarios",
            "scope_out": "Production code",
            "status": "not_started",
        }
        resp = await client.post("/api/v1/workstreams/", json=payload, headers=auth_headers)

    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "created"
    assert "id" in body
    assert body["name"] == "Test Workstream"


@pytest.mark.asyncio
async def test_update_workstream(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstream_id = list_resp.json()[0]["id"]

        resp = await client.put(
            f"/api/v1/workstreams/{workstream_id}",
            json={"status": "at_risk", "purpose": "Updated purpose for testing"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "updated"
    assert body["id"] == workstream_id


@pytest.mark.asyncio
async def test_list_workstreams_no_auth(seeded_db):
    """Unauthenticated request must be rejected with 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/workstreams/")

    assert resp.status_code == 401

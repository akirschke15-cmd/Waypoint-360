"""Tests for risks CRUD endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_list_risks(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/risks/", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Seed data loads 12 risks
    assert len(body) >= 1

    first = body[0]
    assert "id" in first
    assert "workstream_id" in first
    assert "description" in first
    assert "severity" in first
    assert "likelihood" in first
    assert "status" in first


@pytest.mark.asyncio
async def test_list_risks_filter_by_workstream(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Obtain a valid workstream id from the list
        ws_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstream_id = ws_resp.json()[0]["id"]

        resp = await client.get(
            f"/api/v1/risks/?workstream_id={workstream_id}",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Every returned risk must belong to the requested workstream
    for risk in body:
        assert risk["workstream_id"] == workstream_id


@pytest.mark.asyncio
async def test_get_risk(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/risks/", headers=auth_headers)
        risk_id = list_resp.json()[0]["id"]

        resp = await client.get(f"/api/v1/risks/{risk_id}", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == risk_id
    assert "description" in body
    assert "severity" in body


@pytest.mark.asyncio
async def test_create_risk(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ws_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstream_id = ws_resp.json()[0]["id"]

        payload = {
            "workstream_id": workstream_id,
            "description": "New test risk: integration layer not yet defined",
            "severity": "high",
            "likelihood": "medium",
            "mitigation": "Schedule discovery session with platform team",
            "category": "technical",
        }
        resp = await client.post("/api/v1/risks/", json=payload, headers=auth_headers)

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["workstream_id"] == workstream_id
    assert body["severity"] == "high"
    assert body["likelihood"] == "medium"
    assert body["status"] == "open"


@pytest.mark.asyncio
async def test_update_risk(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/risks/", headers=auth_headers)
        risk_id = list_resp.json()[0]["id"]

        resp = await client.put(
            f"/api/v1/risks/{risk_id}",
            json={"status": "mitigated", "severity": "low"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == risk_id
    assert body["status"] == "mitigated"
    assert body["severity"] == "low"


@pytest.mark.asyncio
async def test_delete_risk(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a risk first so we can delete it without affecting other tests' data
        ws_resp = await client.get("/api/v1/workstreams/", headers=auth_headers)
        workstream_id = ws_resp.json()[0]["id"]

        create_resp = await client.post(
            "/api/v1/risks/",
            json={
                "workstream_id": workstream_id,
                "description": "Temporary risk to be deleted",
                "severity": "low",
                "likelihood": "low",
            },
            headers=auth_headers,
        )
        risk_id = create_resp.json()["id"]

        # Delete it
        del_resp = await client.delete(f"/api/v1/risks/{risk_id}", headers=auth_headers)

    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"
    assert del_resp.json()["id"] == risk_id

    # Verify it is gone
    transport2 = ASGITransport(app=app)
    async with AsyncClient(transport=transport2, base_url="http://test") as client:
        get_resp = await client.get(f"/api/v1/risks/{risk_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_risk_viewer_forbidden(seeded_db, viewer_headers):
    """A viewer-role token must receive 403 when attempting to create a risk."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        ws_resp = await client.get("/api/v1/workstreams/", headers=viewer_headers)
        workstream_id = ws_resp.json()[0]["id"]

        resp = await client.post(
            "/api/v1/risks/",
            json={
                "workstream_id": workstream_id,
                "description": "Viewer should not be able to create this",
                "severity": "medium",
                "likelihood": "low",
            },
            headers=viewer_headers,
        )

    assert resp.status_code == 403

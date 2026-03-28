"""Tests for gates endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_list_gates(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/gates/", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    # Seed data creates 6 gates (ALIGN + 5 INCEPT gates)
    assert len(body) == 6

    first = body[0]
    assert "id" in first
    assert "name" in first
    assert "short_name" in first
    assert "week_number" in first
    assert "status" in first
    assert "exit_criteria" in first
    assert isinstance(first["exit_criteria"], list)
    assert "criteria_total" in first
    assert first["criteria_total"] > 0


@pytest.mark.asyncio
async def test_get_gate_detail(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/gates/", headers=auth_headers)
        gate_id = list_resp.json()[0]["id"]

        resp = await client.get(f"/api/v1/gates/{gate_id}", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == gate_id
    assert "exit_criteria" in body
    assert "workstream_deliverables" in body
    assert isinstance(body["workstream_deliverables"], list)

    # Each exit criteria entry must have the notes field (nullable)
    for ec in body["exit_criteria"]:
        assert "id" in ec
        assert "description" in ec
        assert "status" in ec
        assert "notes" in ec


@pytest.mark.asyncio
async def test_get_gate_timeline(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/gates/timeline", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert "gates" in body
    assert "matrix" in body

    assert len(body["gates"]) == 6
    assert len(body["matrix"]) == 10  # 10 workstreams seeded

    row = body["matrix"][0]
    assert "workstream" in row
    assert "gates" in row
    # The gates sub-dict should be keyed by short_name
    assert "ALIGN" in row["gates"]


@pytest.mark.asyncio
async def test_update_exit_criteria(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        list_resp = await client.get("/api/v1/gates/", headers=auth_headers)
        gate = list_resp.json()[0]
        gate_id = gate["id"]
        criteria_id = gate["exit_criteria"][0]["id"]

        resp = await client.put(
            f"/api/v1/gates/{gate_id}/criteria/{criteria_id}",
            json={"status": "complete", "notes": "Verified in planning session"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == criteria_id
    assert body["new_status"] == "complete"

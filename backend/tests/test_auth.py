"""Tests for authentication: password hashing, JWT, and auth endpoints."""
import pytest
from datetime import timedelta
from httpx import AsyncClient, ASGITransport

from app.auth.security import hash_password, verify_password, create_access_token, decode_access_token
from app.main import app


# ---------------------------------------------------------------------------
# Unit tests: password hashing
# ---------------------------------------------------------------------------

def test_hash_and_verify_password():
    plain = "supersecret123"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_hash_is_not_deterministic():
    """bcrypt generates a new salt each call -- two hashes of the same input differ."""
    plain = "samepassword"
    h1 = hash_password(plain)
    h2 = hash_password(plain)
    assert h1 != h2
    assert verify_password(plain, h1) is True
    assert verify_password(plain, h2) is True


# ---------------------------------------------------------------------------
# Unit tests: JWT create / decode
# ---------------------------------------------------------------------------

def test_create_and_decode_token():
    payload = {"sub": "42", "role": "admin"}
    token = create_access_token(payload)

    assert isinstance(token, str)
    assert len(token) > 0

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "42"
    assert decoded["role"] == "admin"
    assert "exp" in decoded


def test_decode_token_returns_none_for_garbage():
    result = decode_access_token("this.is.not.a.valid.token")
    assert result is None


def test_decode_token_returns_none_for_expired():
    token = create_access_token({"sub": "99"}, expires_delta=timedelta(seconds=-1))
    result = decode_access_token(token)
    assert result is None


# ---------------------------------------------------------------------------
# Integration tests: /api/v1/auth endpoints
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(seeded_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "alex.kirschke@waypoint360.dev", "password": "waypoint360"},
        )

    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "alex.kirschke@waypoint360.dev"
    assert body["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_login_wrong_password(seeded_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "alex.kirschke@waypoint360.dev", "password": "wrongpassword"},
        )

    assert resp.status_code == 401
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_login_nonexistent_email(seeded_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@waypoint360.dev", "password": "waypoint360"},
        )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(seeded_db, auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alex.kirschke@waypoint360.dev"
    assert body["role"] == "admin"
    assert "id" in body
    assert "name" in body


@pytest.mark.asyncio
async def test_get_me_no_token(seeded_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/auth/me")

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(seeded_db):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer this.is.not.valid"},
        )

    assert resp.status_code == 401

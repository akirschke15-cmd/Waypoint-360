"""Shared pytest fixtures for Waypoint 360 backend tests."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.db.database import get_db
from app.models.base import Base
import app.models  # noqa: F401 -- ensure all models are registered with Base.metadata
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:////tmp/waypoint360_test.db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def seeded_db():
    """
    Create a fresh test database, seed it with Waypoint program data,
    and override the FastAPI get_db dependency to use it.

    Clears dependency overrides after each test.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_factory() as session:
        from app.db.seed import seed_waypoint_data
        await seed_waypoint_data(session)

    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_token(seeded_db) -> str:
    """
    Log in as the seeded admin user (Alex Kirschke) and return a JWT token.

    Alex is seeded with role=ADMIN and password='waypoint360'.
    Email is derived from the seed logic: first.name@waypoint360.dev
    """
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "alex.kirschke@waypoint360.dev", "password": "waypoint360"},
        )
        assert resp.status_code == 200, f"Admin login failed: {resp.text}"
        return resp.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(auth_token) -> dict:
    """Return Authorization header dict for use in requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest_asyncio.fixture
async def viewer_token(seeded_db) -> str:
    """
    Log in as a viewer user (Peter, role=VIEWER) and return a JWT token.

    Peter is seeded with role=VIEWER and password='waypoint360'.
    """
    from httpx import AsyncClient, ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "peter@waypoint360.dev", "password": "waypoint360"},
        )
        assert resp.status_code == 200, f"Viewer login failed: {resp.text}"
        return resp.json()["access_token"]


@pytest_asyncio.fixture
async def viewer_headers(viewer_token) -> dict:
    """Return Authorization header dict for the viewer user."""
    return {"Authorization": f"Bearer {viewer_token}"}

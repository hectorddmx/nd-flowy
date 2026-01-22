"""Test fixtures and configuration."""

import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_db
from app.main import app
from app.models.database import Base

# Set test environment variables
os.environ["WF_API_KEY"] = "test-api-key"
os.environ["DATABASE_PATH"] = ":memory:"


# Test database engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)

test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# Sample test data
@pytest.fixture
def sample_nodes() -> list[dict]:
    """Sample node data for testing."""
    return [
        {
            "id": "wip-root-123",
            "parent_id": None,
            "name": "WIP",
            "note": None,
            "priority": 0,
            "data": {"layoutMode": "bullets"},
            "createdAt": 1700000000,
            "modifiedAt": 1700000000,
            "completedAt": None,
        },
        {
            "id": "project-456",
            "parent_id": "wip-root-123",
            "name": "PERSONAL",
            "note": None,
            "priority": 1,
            "data": {"layoutMode": "bullets"},
            "createdAt": 1700000000,
            "modifiedAt": 1700000000,
            "completedAt": None,
        },
        {
            "id": "task-789",
            "parent_id": "project-456",
            "name": "Fix bug #TODO",
            "note": "Details here",
            "priority": 0,
            "data": {"layoutMode": "todo"},
            "createdAt": 1700000000,
            "modifiedAt": 1700000000,
            "completedAt": None,
        },
        {
            "id": "task-blocked-111",
            "parent_id": "project-456",
            "name": "Waiting for review #BLOCKED",
            "note": None,
            "priority": 1,
            "data": {"layoutMode": "todo"},
            "createdAt": 1700000000,
            "modifiedAt": 1700000000,
            "completedAt": None,
        },
        {
            "id": "task-done-222",
            "parent_id": "project-456",
            "name": "Completed task #DONE",
            "note": None,
            "priority": 2,
            "data": {"layoutMode": "todo"},
            "createdAt": 1700000000,
            "modifiedAt": 1700000000,
            "completedAt": 1700001000,
        },
    ]

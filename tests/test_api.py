"""Tests for API endpoints."""

import pytest
from httpx import AsyncClient

from app.models.database import FilterHistory, NodeCache, WipConfig


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_root_redirect(client: AsyncClient):
    """Test root redirects to todos."""
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/web/todos"


@pytest.mark.asyncio
async def test_get_nodes_empty(client: AsyncClient):
    """Test getting nodes when cache is empty."""
    response = await client.get("/api/nodes")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_todos_no_wip(client: AsyncClient):
    """Test getting todos when WIP is not configured."""
    response = await client.get("/api/todos")
    assert response.status_code == 404
    assert "WIP node not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_filter_history_empty(client: AsyncClient):
    """Test getting filter history when empty."""
    response = await client.get("/api/filters/history")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_save_filter(client: AsyncClient, db_session):
    """Test saving a filter to history."""
    response = await client.post(
        "/api/filters",
        json={"filter_text": "project, urgent"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filter_text"] == "project, urgent"
    assert "id" in data
    assert "used_at" in data


@pytest.mark.asyncio
async def test_get_filter_history_with_data(client: AsyncClient, db_session):
    """Test getting filter history with saved filters."""
    # Save a filter
    await client.post("/api/filters", json={"filter_text": "test filter"})

    # Get history
    response = await client.get("/api/filters/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["filter_text"] == "test filter"


@pytest.mark.asyncio
async def test_todos_page_no_wip(client: AsyncClient):
    """Test todos page when WIP is not configured."""
    response = await client.get("/web/todos")
    assert response.status_code == 200
    assert b"No WIP node found" in response.content


@pytest.mark.asyncio
async def test_kanban_page_no_wip(client: AsyncClient):
    """Test kanban page when WIP is not configured."""
    response = await client.get("/web/kanban")
    assert response.status_code == 200
    assert b"No WIP node found" in response.content

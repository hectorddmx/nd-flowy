from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.database import FilterHistory, NodeCache, WipConfig
from app.models.schemas import (
    FilterHistoryCreate,
    FilterHistoryResponse,
    NodeCacheResponse,
    RefreshResponse,
    StatusTag,
    StatusUpdateRequest,
)
from app.services.workflowy_client import WorkflowyClient

router = APIRouter(prefix="/api", tags=["api"])


def get_workflowy_client() -> WorkflowyClient:
    """Get Workflowy client instance."""
    return WorkflowyClient(
        api_key=settings.wf_api_key,
        base_url=settings.wf_api_base_url,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_nodes(
    db: AsyncSession = Depends(get_db),
    client: WorkflowyClient = Depends(get_workflowy_client),
):
    """Trigger a full sync from Workflowy API."""
    try:
        # Fetch all nodes from Workflowy
        nodes = await client.export_all_nodes()

        # Build lookup for breadcrumb computation
        nodes_by_id = {n["id"]: n for n in nodes}

        # Find WIP node
        wip_node = client.find_wip_node(nodes)
        wip_node_id = wip_node["id"] if wip_node else None

        # Clear existing cache
        await db.execute(delete(NodeCache))

        # Store WIP config if found
        if wip_node_id:
            await db.execute(delete(WipConfig))
            db.add(WipConfig(wip_node_id=wip_node_id))

        # Cache all nodes with breadcrumbs
        cached_count = 0
        for node in nodes:
            breadcrumb = client.compute_breadcrumb(node["id"], nodes_by_id)
            status_tag = client.extract_status_tag(node.get("name"))

            # Parse timestamps
            completed_at = client.parse_timestamp(node.get("completedAt"))
            created_at = client.parse_timestamp(node.get("createdAt"))
            modified_at = client.parse_timestamp(node.get("modifiedAt"))

            # Get layout mode from data object
            data = node.get("data", {})
            layout_mode = data.get("layoutMode") if isinstance(data, dict) else None

            node_cache = NodeCache(
                id=node["id"],
                parent_id=node.get("parent_id"),
                name=node.get("name"),
                note=node.get("note"),
                priority=node.get("priority", 0),
                layout_mode=layout_mode,
                completed_at=completed_at,
                created_at=created_at,
                modified_at=modified_at,
                breadcrumb=breadcrumb,
                status_tag=status_tag.value if status_tag else None,
            )
            db.add(node_cache)
            cached_count += 1

        await db.commit()

        return RefreshResponse(nodes_cached=cached_count, wip_node_id=wip_node_id)

    finally:
        await client.close()


@router.get("/nodes", response_model=list[NodeCacheResponse])
async def get_nodes(
    parent_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get cached nodes, optionally filtered by parent."""
    query = select(NodeCache)
    if parent_id:
        query = query.where(NodeCache.parent_id == parent_id)
    query = query.order_by(NodeCache.priority)

    result = await db.execute(query)
    nodes = result.scalars().all()
    return nodes


@router.get("/todos", response_model=list[NodeCacheResponse])
async def get_todos(
    filter_text: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get flattened todo nodes with optional filtering."""
    # Get WIP node ID
    wip_result = await db.execute(select(WipConfig).limit(1))
    wip_config = wip_result.scalar_one_or_none()

    if not wip_config:
        raise HTTPException(status_code=404, detail="WIP node not found. Run refresh first.")

    # Get all nodes under WIP that are todos
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like(f"%{wip_config.wip_node_id}%")
        | NodeCache.breadcrumb.like("WIP%"),
    )

    # Apply text filter
    if filter_text:
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        for f in filters:
            query = query.where(
                NodeCache.name.ilike(f"%{f}%") | NodeCache.breadcrumb.ilike(f"%{f}%")
            )

    query = query.order_by(NodeCache.priority)
    result = await db.execute(query)
    nodes = result.scalars().all()
    return nodes


@router.post("/nodes/{node_id}/complete")
async def complete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    client: WorkflowyClient = Depends(get_workflowy_client),
):
    """Mark a node as complete."""
    try:
        await client.complete_node(node_id)

        # Update cache
        result = await db.execute(select(NodeCache).where(NodeCache.id == node_id))
        node = result.scalar_one_or_none()
        if node:
            node.completed_at = datetime.now()
            await db.commit()

        return {"status": "ok"}
    finally:
        await client.close()


@router.post("/nodes/{node_id}/uncomplete")
async def uncomplete_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    client: WorkflowyClient = Depends(get_workflowy_client),
):
    """Mark a node as incomplete."""
    try:
        await client.uncomplete_node(node_id)

        # Update cache
        result = await db.execute(select(NodeCache).where(NodeCache.id == node_id))
        node = result.scalar_one_or_none()
        if node:
            node.completed_at = None
            await db.commit()

        return {"status": "ok"}
    finally:
        await client.close()


@router.post("/nodes/{node_id}/status")
async def update_status(
    node_id: str,
    request: StatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    client: WorkflowyClient = Depends(get_workflowy_client),
):
    """Update a node's status tag."""
    try:
        # Get current node from cache
        result = await db.execute(select(NodeCache).where(NodeCache.id == node_id))
        node = result.scalar_one_or_none()

        if not node:
            raise HTTPException(status_code=404, detail="Node not found in cache")

        # Update node name with new status
        new_name = client.update_status_tag(node.name, request.status)
        await client.update_node(node_id, name=new_name)

        # Update cache
        node.name = new_name
        node.status_tag = request.status.value
        await db.commit()

        return {"status": "ok", "new_name": new_name}
    finally:
        await client.close()


@router.get("/filters/history", response_model=list[FilterHistoryResponse])
async def get_filter_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Get recent filter history."""
    query = select(FilterHistory).order_by(FilterHistory.used_at.desc()).limit(limit)
    result = await db.execute(query)
    filters = result.scalars().all()
    return filters


@router.post("/filters", response_model=FilterHistoryResponse)
async def save_filter(
    request: FilterHistoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Save a filter to history."""
    filter_entry = FilterHistory(filter_text=request.filter_text)
    db.add(filter_entry)
    await db.commit()
    await db.refresh(filter_entry)
    return filter_entry

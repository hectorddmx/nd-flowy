"""FastHTML page routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.database import NodeCache, WipConfig
from app.services.workflowy_client import WorkflowyClient

from .components import base_page, empty_state, skeleton_list, todo_list, todo_list_items
from .kanban import kanban_page

router = APIRouter(prefix="/web", tags=["web"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Redirect to todos page."""
    return HTMLResponse(
        status_code=302,
        headers={"Location": "/web/todos"},
    )


@router.get("/todos", response_class=HTMLResponse)
async def todos_page(
    request: Request,
    filter_text: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Render the todos list page."""
    # Check if WIP node is configured
    wip_result = await db.execute(select(WipConfig).limit(1))
    wip_config = wip_result.scalar_one_or_none()

    if not wip_config:
        page = base_page(
            "Todos - Workflowy Flow",
            empty_state("No WIP node found. Click refresh to sync from Workflowy."),
        )
        return HTMLResponse(str(page))

    # Get todo nodes
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
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

    # Check if this is an HTMX request (partial update)
    if request.headers.get("HX-Request"):
        return HTMLResponse(str(todo_list_items(nodes)))

    page = base_page(
        "Todos - Workflowy Flow",
        todo_list(nodes, filter_text),
    )
    return HTMLResponse(str(page))


@router.get("/kanban", response_class=HTMLResponse)
async def kanban_view(
    request: Request,
    filter_text: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Render the kanban board page."""
    # Check if WIP node is configured
    wip_result = await db.execute(select(WipConfig).limit(1))
    wip_config = wip_result.scalar_one_or_none()

    if not wip_config:
        page = base_page(
            "Kanban - Workflowy Flow",
            empty_state("No WIP node found. Click refresh to sync from Workflowy."),
        )
        return HTMLResponse(str(page))

    # Get all todo nodes under WIP
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
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

    # Check if this is an HTMX request (partial update)
    if request.headers.get("HX-Request"):
        return HTMLResponse(str(kanban_page(nodes, filter_text, partial=True)))

    page = base_page(
        "Kanban - Workflowy Flow",
        kanban_page(nodes, filter_text),
    )
    return HTMLResponse(str(page))


@router.post("/refresh", response_class=HTMLResponse)
async def refresh_and_show(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh data from Workflowy and return updated todo list."""
    client = WorkflowyClient(
        api_key=settings.wf_api_key,
        base_url=settings.wf_api_base_url,
    )

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

        await db.commit()

    finally:
        await client.close()

    # Now return the updated todo list
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
    ).order_by(NodeCache.priority)

    result = await db.execute(query)
    todo_nodes = result.scalars().all()

    return HTMLResponse(str(todo_list(todo_nodes, "")))

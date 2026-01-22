"""FastHTML page routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fasthtml.common import to_xml
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.database import NodeCache, WipConfig
from app.services.workflowy_client import WorkflowyClient

from .components import base_page, empty_state, todo_list, todo_list_items
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
    show_completed: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Render the todos list page."""
    # Parse show_completed (checkbox sends "true" when checked, empty when not)
    show_completed_bool = show_completed == "true"

    # Check if WIP node is configured
    wip_result = await db.execute(select(WipConfig).limit(1))
    wip_config = wip_result.scalar_one_or_none()

    if not wip_config:
        page = base_page(
            "Todos - Workflowy Flow",
            empty_state("No WIP node found. Click refresh to sync from Workflowy."),
        )
        return HTMLResponse(to_xml(page))

    # Get todo nodes
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
    )

    # Filter out completed items unless show_completed is true
    if not show_completed_bool:
        query = query.where(NodeCache.completed_at.is_(None))

    # Apply text filter
    if filter_text:
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        for f in filters:
            query = query.where(
                NodeCache.name.ilike(f"%{f}%") | NodeCache.breadcrumb.ilike(f"%{f}%")
            )

    query = query.order_by(NodeCache.color_priority, NodeCache.priority)
    result = await db.execute(query)
    nodes = result.scalars().all()

    # Check if this is an HTMX request (partial update)
    if request.headers.get("HX-Request"):
        return HTMLResponse(to_xml(todo_list_items(nodes)))

    page = base_page(
        "Todos - Workflowy Flow",
        todo_list(nodes, filter_text, show_completed_bool),
    )
    return HTMLResponse(to_xml(page))


@router.get("/kanban", response_class=HTMLResponse)
async def kanban_view(
    request: Request,
    filter_text: str = "",
    show_completed: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Render the kanban board page."""
    # Parse show_completed (checkbox sends "true" when checked, empty when not)
    show_completed_bool = show_completed == "true"

    # Check if WIP node is configured
    wip_result = await db.execute(select(WipConfig).limit(1))
    wip_config = wip_result.scalar_one_or_none()

    if not wip_config:
        page = base_page(
            "Kanban - Workflowy Flow",
            empty_state("No WIP node found. Click refresh to sync from Workflowy."),
        )
        return HTMLResponse(to_xml(page))

    # Get all todo nodes under WIP
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
    )

    # Filter out completed items unless show_completed is true
    if not show_completed_bool:
        query = query.where(NodeCache.completed_at.is_(None))

    # Apply text filter
    if filter_text:
        filters = [f.strip() for f in filter_text.split(",") if f.strip()]
        for f in filters:
            query = query.where(
                NodeCache.name.ilike(f"%{f}%") | NodeCache.breadcrumb.ilike(f"%{f}%")
            )

    query = query.order_by(NodeCache.color_priority, NodeCache.priority)
    result = await db.execute(query)
    nodes = result.scalars().all()

    # Check if this is an HTMX request (partial update)
    if request.headers.get("HX-Request"):
        return HTMLResponse(to_xml(kanban_page(nodes, filter_text, show_completed_bool, partial=True)))

    page = base_page(
        "Kanban - Workflowy Flow",
        kanban_page(nodes, filter_text, show_completed_bool),
    )
    return HTMLResponse(to_xml(page))


@router.post("/refresh", response_class=HTMLResponse)
async def refresh_and_show(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Refresh data from Workflowy and return updated view."""
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
                color_priority=client.get_color_priority(node.get("name")),
            )
            db.add(node_cache)

        await db.commit()

    finally:
        await client.close()

    # Determine which view to return based on the current URL
    current_url = request.headers.get("HX-Current-URL", "")
    is_kanban = "/kanban" in current_url

    # Get nodes (hide completed by default)
    query = select(NodeCache).where(
        NodeCache.layout_mode == "todo",
        NodeCache.breadcrumb.like("WIP%"),
        NodeCache.completed_at.is_(None),
    ).order_by(NodeCache.color_priority, NodeCache.priority)

    result = await db.execute(query)
    todo_nodes = result.scalars().all()

    if is_kanban:
        return HTMLResponse(to_xml(kanban_page(todo_nodes, "", False)))
    else:
        return HTMLResponse(to_xml(todo_list(todo_nodes, "", False)))

"""FastHTML page routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import NodeCache, WipConfig

from .components import base_page, empty_state, todo_list
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
        return HTMLResponse(str(todo_list(nodes, filter_text)))

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

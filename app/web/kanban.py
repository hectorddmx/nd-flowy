"""Kanban board components."""

from fasthtml.common import (
    H2,
    Div,
    Form,
    Input,
    NotStr,
    Script,
    Span,
)

from app.models.schemas import StatusTag

# Kanban column definitions with colors
KANBAN_COLUMNS = [
    (StatusTag.BACKLOG, "Backlog", "bg-gray-600"),
    (StatusTag.BLOCKED, "Blocked", "bg-red-600"),
    (StatusTag.TODO, "Todo", "bg-yellow-600"),
    (StatusTag.WIP, "WIP", "bg-blue-600"),
    (StatusTag.TEST, "Test", "bg-purple-600"),
    (StatusTag.DONE, "Done", "bg-green-600"),
]


def kanban_card(node):
    """Render a single kanban card."""
    is_completed = node.completed_at is not None

    # Render node name as HTML to support Workflowy's colored spans
    name_content = NotStr(node.name) if node.name else "(unnamed)"

    return Div(
        Div(
            Input(
                type="checkbox",
                checked=is_completed,
                hx_post=f"/api/nodes/{node.id}/{'uncomplete' if is_completed else 'complete'}",
                hx_swap="none",
                cls="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-600 bg-gray-700",
            ),
            Span(
                name_content,
                cls=f"ml-2 text-sm {'line-through text-gray-500' if is_completed else 'text-gray-100'}",
            ),
            cls="flex items-start",
        ),
        Span(
            node.breadcrumb or "",
            cls="text-xs text-gray-500 mt-1 block truncate",
        ),
        cls="p-3 bg-gray-700 rounded-lg mb-2 cursor-move hover:bg-gray-650 "
        "border border-gray-600 hover:border-gray-500 transition-colors",
        data_node_id=node.id,
        data_current_status=node.status_tag or "BACKLOG",
        draggable="true",
    )


def kanban_column(status: StatusTag, title: str, color: str, nodes):
    """Render a kanban column."""
    column_nodes = [n for n in nodes if (n.status_tag or "BACKLOG") == status.value]
    # Sort by color priority within each column
    column_nodes.sort(key=lambda n: (n.color_priority, n.priority))

    return Div(
        Div(
            H2(
                title,
                cls="font-semibold text-gray-100",
            ),
            Span(
                str(len(column_nodes)),
                cls=f"ml-2 px-2 py-0.5 text-xs rounded-full {color} text-white",
            ),
            cls="flex items-center mb-3 pb-2 border-b border-gray-700",
        ),
        Div(
            *[kanban_card(node) for node in column_nodes],
            cls="kanban-column min-h-[200px] space-y-2",
            data_status=status.value,
            id=f"column-{status.value.lower()}",
        ),
        cls="flex-1 min-w-[200px] max-w-[300px] p-3 bg-gray-800 rounded-lg",
    )


def kanban_board(nodes):
    """Render the full kanban board."""
    return Div(
        *[kanban_column(status, title, color, nodes) for status, title, color in KANBAN_COLUMNS],
        cls="flex gap-4 overflow-x-auto pb-4",
        id="kanban-board",
    )


def kanban_filter_input(current_filter: str = ""):
    """Render the kanban filter input."""
    return Form(
        Input(
            type="text",
            name="filter_text",
            value=current_filter,
            placeholder="Filter by name or project (comma-separated)...",
            cls="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg "
            "text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500",
            hx_get="/web/kanban",
            hx_trigger="keyup changed delay:300ms",
            hx_target="#kanban-board-container",
            hx_push_url="true",
        ),
        cls="mb-4",
    )


def kanban_scripts():
    """JavaScript for kanban drag and drop functionality."""
    return Script("""
        document.addEventListener('DOMContentLoaded', function() {
            initKanban();
        });

        document.addEventListener('htmx:afterSwap', function() {
            initKanban();
        });

        function initKanban() {
            document.querySelectorAll('.kanban-column').forEach(function(column) {
                if (column._sortable) return; // Already initialized

                column._sortable = new Sortable(column, {
                    group: 'kanban',
                    animation: 150,
                    ghostClass: 'opacity-50',
                    dragClass: 'shadow-lg',
                    onEnd: function(evt) {
                        const nodeId = evt.item.dataset.nodeId;
                        const newStatus = evt.to.dataset.status;
                        const oldStatus = evt.item.dataset.currentStatus;

                        if (newStatus !== oldStatus) {
                            // Update status via API
                            fetch(`/api/nodes/${nodeId}/status`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ status: newStatus }),
                            })
                            .then(response => response.json())
                            .then(data => {
                                if (data.status === 'ok') {
                                    // Update the card's data attribute
                                    evt.item.dataset.currentStatus = newStatus;
                                }
                            })
                            .catch(error => {
                                console.error('Error updating status:', error);
                                // Revert the move on error
                                evt.from.appendChild(evt.item);
                            });
                        }
                    }
                });
            });
        }
    """)


def kanban_board_items(nodes):
    """Render just the kanban board (for HTMX partial updates)."""
    return Div(
        kanban_board(nodes),
        kanban_scripts(),
        id="kanban-board-container",
    )


def kanban_page(nodes, current_filter: str = "", partial: bool = False):
    """Render the full kanban page content."""
    if partial:
        # Return only the board container for HTMX updates
        return kanban_board_items(nodes)

    return Div(
        kanban_filter_input(current_filter),
        kanban_board_items(nodes),
    )

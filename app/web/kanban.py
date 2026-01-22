"""Kanban board components."""

from fasthtml.common import (
    H2,
    Div,
    Script,
    Span,
)

from app.models.schemas import StatusTag

from .components import STATUS_TAG_COLORS, filter_input_field, render_node_name

# Kanban column definitions - uses colors from shared STATUS_TAG_COLORS
KANBAN_COLUMNS = [
    (StatusTag.BACKLOG, "Backlog"),
    (StatusTag.BLOCKED, "Blocked"),
    (StatusTag.TODO, "Todo"),
    (StatusTag.WIP, "WIP"),
    (StatusTag.TEST, "Test"),
    (StatusTag.DONE, "Done"),
]


def kanban_card(node):
    """Render a single kanban card."""
    is_completed = node.completed_at is not None

    return Div(
        Div(
            render_node_name(node.name, is_completed),
            cls="flex items-start text-sm",
        ),
        Span(
            node.breadcrumb or "",
            cls="text-xs text-gray-500 mt-1 block truncate",
        ),
        cls="p-2 bg-gray-700 rounded-lg mb-2 cursor-move hover:bg-gray-650 "
        "border border-gray-600 hover:border-gray-500 transition-colors",
        data_node_id=node.id,
        data_current_status=node.status_tag or "BACKLOG",
        draggable="true",
    )


def kanban_column(status: StatusTag, title: str, nodes):
    """Render a kanban column."""
    column_nodes = [n for n in nodes if (n.status_tag or "BACKLOG") == status.value]
    # Sort by color priority within each column
    column_nodes.sort(key=lambda n: (n.color_priority, n.priority))
    count = len(column_nodes)

    # Get color from shared STATUS_TAG_COLORS
    bg_color, _ = STATUS_TAG_COLORS.get(status.value, ("bg-gray-600", "text-white"))

    return Div(
        # Expanded header (visible when not collapsed)
        Div(
            H2(
                title,
                cls="font-semibold text-gray-100",
            ),
            Span(
                str(count),
                cls=f"ml-2 px-2 py-0.5 text-xs rounded-full {bg_color} text-white",
            ),
            cls="flex items-center mb-3 pb-2 border-b border-gray-700 cursor-pointer column-header",
        ),
        # Collapsed header (visible when collapsed)
        Div(
            Span(
                str(count),
                cls=f"px-2 py-0.5 text-xs rounded-full {bg_color} text-white mb-2",
            ),
            Span(
                title,
                cls="font-semibold text-gray-100 writing-vertical",
            ),
            cls="hidden flex-col items-center py-2 cursor-pointer collapsed-header",
        ),
        # Column content
        Div(
            *[kanban_card(node) for node in column_nodes],
            cls="kanban-column min-h-[200px] space-y-2 column-content",
            data_status=status.value,
            id=f"column-{status.value.lower()}",
        ),
        cls="flex-1 min-w-0 p-3 bg-gray-800 rounded-lg kanban-column-wrapper",
        data_column=status.value,
    )


def kanban_board(nodes):
    """Render the full kanban board."""
    return Div(
        *[kanban_column(status, title, nodes) for status, title in KANBAN_COLUMNS],
        cls="flex gap-4 pb-4",
        id="kanban-board",
    )


def kanban_filter_input(current_filter: str = "", show_completed: bool = False):
    """Render the kanban filter input."""
    return filter_input_field(current_filter, "/web/kanban", "#kanban-board-container", show_completed)


def kanban_scripts():
    """JavaScript for kanban drag and drop functionality."""
    return Script("""
        document.addEventListener('DOMContentLoaded', function() {
            initKanban();
            initColumnToggle();
            restoreCollapsedState();
        });

        document.addEventListener('htmx:afterSwap', function() {
            initKanban();
            initColumnToggle();
            restoreCollapsedState();
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

        function initColumnToggle() {
            // Use event delegation for column header clicks
            document.querySelectorAll('.column-header, .collapsed-header').forEach(function(header) {
                if (header._toggleInit) return; // Already initialized
                header._toggleInit = true;

                header.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const wrapper = this.closest('.kanban-column-wrapper');
                    if (wrapper) {
                        toggleColumn(wrapper);
                    }
                });
            });
        }

        function toggleColumn(wrapper) {
            const columnName = wrapper.dataset.column;
            const isCollapsed = wrapper.classList.toggle('collapsed');

            // Save state to localStorage
            const collapsedColumns = JSON.parse(localStorage.getItem('kanban-collapsed') || '[]');
            if (isCollapsed) {
                if (!collapsedColumns.includes(columnName)) {
                    collapsedColumns.push(columnName);
                }
            } else {
                const index = collapsedColumns.indexOf(columnName);
                if (index > -1) {
                    collapsedColumns.splice(index, 1);
                }
            }
            localStorage.setItem('kanban-collapsed', JSON.stringify(collapsedColumns));
        }

        function restoreCollapsedState() {
            const collapsedColumns = JSON.parse(localStorage.getItem('kanban-collapsed') || '[]');
            if (collapsedColumns.length === 0) return;

            // Disable transitions while restoring state
            const wrappers = document.querySelectorAll('.kanban-column-wrapper');
            wrappers.forEach(w => w.style.transition = 'none');

            collapsedColumns.forEach(function(columnName) {
                const wrapper = document.querySelector(`.kanban-column-wrapper[data-column="${columnName}"]`);
                if (wrapper) {
                    wrapper.classList.add('collapsed');
                }
            });

            // Force reflow, then re-enable transitions
            wrappers[0]?.offsetHeight;
            requestAnimationFrame(() => {
                wrappers.forEach(w => w.style.transition = '');
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


def kanban_page(nodes, current_filter: str = "", show_completed: bool = False, partial: bool = False):
    """Render the full kanban page content."""
    if partial:
        # Return only the board container for HTMX updates
        return kanban_board_items(nodes)

    return Div(
        kanban_filter_input(current_filter, show_completed),
        kanban_board_items(nodes),
    )

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
                cls="font-semibold text-gray-100 text-sm",
            ),
            Span(
                str(count),
                cls=f"ml-2 px-2 py-0.5 text-xs rounded-full {bg_color} text-white",
            ),
            cls="flex items-center pb-2 border-b border-gray-700 cursor-pointer column-header",
        ),
        # Collapsed header (visible when collapsed)
        Div(
            Span(
                str(count),
                cls=f"px-2 py-0.5 text-xs rounded-full {bg_color} text-white mb-2",
            ),
            Span(
                title,
                cls="font-semibold text-gray-100 writing-vertical text-sm",
            ),
            cls="hidden flex-col items-center py-2 cursor-pointer collapsed-header",
        ),
        # Column content (scrollable)
        Div(
            *[kanban_card(node) for node in column_nodes],
            cls="kanban-column space-y-1 column-content",
            data_status=status.value,
            id=f"column-{status.value.lower()}",
        ),
        cls="flex-1 min-w-0 p-2 bg-gray-800 rounded-lg kanban-column-wrapper",
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
    """Render the kanban filter input with sticky positioning."""
    return Div(
        filter_input_field(
            current_filter, "/web/kanban", "#kanban-board-container", show_completed
        ),
        cls="sticky-filter",
    )


def kanban_scripts():
    """JavaScript for kanban drag and drop functionality."""
    return Script("""
        document.addEventListener('DOMContentLoaded', function() {
            document.body.classList.add('kanban-view');
            initKanban();
            initColumnToggle();
            restoreCollapsedState();
        });

        document.addEventListener('htmx:afterSwap', function(evt) {
            // Toggle kanban-view class based on current view
            if (window.location.pathname.includes('/kanban')) {
                document.body.classList.add('kanban-view');
            } else {
                document.body.classList.remove('kanban-view');
            }
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
                    ghostClass: 'sortable-ghost',
                    dragClass: 'sortable-drag',
                    chosenClass: 'sortable-chosen',
                    onStart: function(evt) {
                        // Add visual indicator that dragging is active
                        document.body.classList.add('is-dragging');
                    },
                    onEnd: function(evt) {
                        // Remove dragging indicator
                        document.body.classList.remove('is-dragging');
                        // Remove any lingering drag-over classes
                        document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));

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
                    },
                    onMove: function(evt) {
                        // Highlight the target column
                        document.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
                        const targetWrapper = evt.to.closest('.kanban-column-wrapper');
                        if (targetWrapper) {
                            targetWrapper.classList.add('drag-over');
                        }
                    }
                });
            });
        }

        function initColumnToggle() {
            // Handle clicks on column headers to collapse
            document.querySelectorAll('.column-header').forEach(function(header) {
                if (header._toggleInit) return;
                header._toggleInit = true;
                header.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const wrapper = this.closest('.kanban-column-wrapper');
                    if (wrapper) {
                        toggleColumn(wrapper);
                    }
                });
            });

            // Handle clicks anywhere on collapsed column to expand
            document.querySelectorAll('.kanban-column-wrapper').forEach(function(wrapper) {
                if (wrapper._expandInit) return;
                wrapper._expandInit = true;
                wrapper.addEventListener('click', function(e) {
                    if (this.classList.contains('collapsed')) {
                        e.stopPropagation();
                        toggleColumn(this);
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
            const board = document.getElementById('kanban-board');
            if (!board) return;

            // Apply collapsed state immediately (transitions disabled via CSS)
            collapsedColumns.forEach(function(columnName) {
                const wrapper = document.querySelector(`.kanban-column-wrapper[data-column="${columnName}"]`);
                if (wrapper) {
                    wrapper.classList.add('collapsed');
                }
            });

            // Enable transitions after a brief delay
            setTimeout(() => {
                board.classList.add('transitions-ready');
            }, 50);
        }
    """)


def kanban_board_items(nodes):
    """Render just the kanban board (for HTMX partial updates)."""
    return Div(
        kanban_board(nodes),
        kanban_scripts(),
        id="kanban-board-container",
    )


def kanban_page(
    nodes, current_filter: str = "", show_completed: bool = False, partial: bool = False
):
    """Render the full kanban page content."""
    if partial:
        # Return only the board container for HTMX updates
        return kanban_board_items(nodes)

    return Div(
        kanban_filter_input(current_filter, show_completed),
        kanban_board_items(nodes),
    )

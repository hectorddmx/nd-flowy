"""Reusable FastHTML components."""

from fasthtml.common import (
    Button,
    Div,
    Form,
    Head,
    Html,
    Input,
    Li,
    Link,
    Main,
    Meta,
    Nav,
    Script,
    Span,
    Title,
    Ul,
)


def base_page(title: str, *content):
    """Base page template with Tailwind CSS dark theme."""
    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Title(title),
            # Tailwind CSS CDN
            Script(src="https://cdn.tailwindcss.com"),
            # HTMX
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            # Sortable.js for drag and drop
            Script(src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"),
            # Custom styles for dark theme
            Link(rel="stylesheet", href="/static/styles.css"),
        ),
        Div(
            Nav(
                Div(
                    Span("Workflowy Flow", cls="text-xl font-bold text-blue-400"),
                    Div(
                        Button(
                            "Todos",
                            hx_get="/web/todos",
                            hx_target="#main-content",
                            hx_push_url="true",
                            cls="px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded",
                        ),
                        Button(
                            "Kanban",
                            hx_get="/web/kanban",
                            hx_target="#main-content",
                            hx_push_url="true",
                            cls="px-4 py-2 text-gray-300 hover:text-white hover:bg-gray-700 rounded",
                        ),
                        Button(
                            "Refresh",
                            hx_post="/api/refresh",
                            hx_swap="none",
                            cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
                        ),
                        cls="flex gap-2",
                    ),
                    cls="container mx-auto flex justify-between items-center",
                ),
                cls="bg-gray-800 p-4 border-b border-gray-700",
            ),
            Main(
                *content,
                id="main-content",
                cls="container mx-auto p-4",
            ),
            cls="min-h-screen bg-gray-900 text-gray-100",
        ),
    )


def todo_item(node):
    """Render a single todo item."""
    is_completed = node.completed_at is not None
    checkbox_cls = "form-checkbox h-5 w-5 text-blue-600 rounded border-gray-600 bg-gray-700"

    return Li(
        Div(
            Input(
                type="checkbox",
                checked=is_completed,
                hx_post=f"/api/nodes/{node.id}/{'uncomplete' if is_completed else 'complete'}",
                hx_swap="outerHTML",
                hx_target="closest li",
                cls=checkbox_cls,
            ),
            Div(
                Span(
                    node.name or "(unnamed)",
                    cls=f"text-gray-100 {'line-through text-gray-500' if is_completed else ''}",
                ),
                Span(
                    node.breadcrumb or "",
                    cls="text-xs text-gray-500 block",
                ),
                cls="ml-3 flex-1",
            ),
            Span(
                f"#{node.status_tag}" if node.status_tag else "",
                cls="text-xs px-2 py-1 bg-gray-700 rounded text-gray-400",
            ) if node.status_tag else "",
            cls="flex items-center p-3 bg-gray-800 rounded-lg hover:bg-gray-750",
        ),
        cls="mb-2",
        id=f"todo-{node.id}",
    )


def filter_input(current_filter: str = ""):
    """Render the filter input component."""
    return Form(
        Input(
            type="text",
            name="filter_text",
            value=current_filter,
            placeholder="Filter by name or project (comma-separated)...",
            cls="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg "
            "text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500",
            hx_get="/web/todos",
            hx_trigger="keyup changed delay:300ms",
            hx_target="#todo-list-container",
            hx_push_url="true",
        ),
        cls="mb-4",
    )


def todo_list_items(nodes):
    """Render just the todo list items and count (for HTMX partial updates)."""
    return Div(
        Ul(
            *[todo_item(node) for node in nodes],
            cls="space-y-2",
        ),
        Div(
            f"{len(nodes)} items",
            cls="text-gray-500 text-sm mt-4",
        ),
        id="todo-list-container",
    )


def todo_list(nodes, current_filter: str = ""):
    """Render the full todo list with filter."""
    return Div(
        filter_input(current_filter),
        todo_list_items(nodes),
    )


def empty_state(message: str):
    """Render an empty state message."""
    return Div(
        Div(
            Span(message, cls="text-gray-400"),
            Button(
                "Refresh from Workflowy",
                hx_post="/api/refresh",
                hx_swap="none",
                cls="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
            ),
            cls="text-center py-12",
        ),
        cls="bg-gray-800 rounded-lg p-8",
    )

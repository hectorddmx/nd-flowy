"""Reusable FastHTML components."""

import re

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
    NotStr,
    Script,
    Span,
    Style,
    Title,
    Ul,
)

# Regex to match status tags in node names
STATUS_TAG_PATTERN = re.compile(r"\s*#(BACKLOG|BLOCKED|TODO|WIP|TEST|DONE)\b", re.IGNORECASE)

# Status tag color definitions (background, text)
STATUS_TAG_COLORS = {
    "BACKLOG": ("bg-gray-600", "text-white"),
    "BLOCKED": ("bg-red-800", "text-red-200"),
    "TODO": ("bg-yellow-600", "text-yellow-100"),
    "WIP": ("bg-blue-600", "text-blue-100"),
    "TEST": ("bg-purple-600", "text-purple-100"),
    "DONE": ("bg-green-700", "text-green-100"),
}


def strip_status_tag(name: str | None) -> str:
    """Remove status tag from node name."""
    if not name:
        return ""
    return STATUS_TAG_PATTERN.sub("", name).strip()


def status_tag_badge(status_tag: str | None):
    """Render a colored status tag badge."""
    if not status_tag:
        return ""

    bg_color, text_color = STATUS_TAG_COLORS.get(status_tag, ("bg-gray-600", "text-white"))
    return Span(
        f"#{status_tag}",
        cls=f"text-xs px-2 py-1 rounded {bg_color} {text_color}",
    )


def render_node_name(name: str | None, is_completed: bool = False):
    """Render a node name with HTML support, stripping status tags."""
    clean_name = strip_status_tag(name) if name else ""
    name_content = NotStr(clean_name) if clean_name else "(unnamed)"
    completed_cls = "line-through text-gray-500" if is_completed else "text-gray-100"
    return Span(name_content, cls=completed_cls)


def filter_input_field(
    current_filter: str = "",
    target_url: str = "/web/todos",
    htmx_target: str = "#todo-list-container",
    show_completed: bool = False,
):
    """Render a reusable filter input component with completed toggle."""
    return Form(
        Div(
            Input(
                type="text",
                name="filter_text",
                value=current_filter,
                placeholder="Filter by name or project (comma-separated)...",
                cls="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg "
                "text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500",
                hx_get=target_url,
                hx_trigger="keyup changed delay:300ms",
                hx_target=htmx_target,
                hx_push_url="true",
                hx_include="closest form",
            ),
            Div(
                Input(
                    type="checkbox",
                    name="show_completed",
                    value="true",
                    checked=show_completed,
                    id="show-completed-toggle",
                    cls="form-checkbox h-4 w-4 text-blue-600 rounded border-gray-600 bg-gray-700",
                    hx_get=target_url,
                    hx_trigger="change",
                    hx_target=htmx_target,
                    hx_push_url="true",
                    hx_include="closest form",
                ),
                Span("Show completed", cls="ml-2 text-sm text-gray-400"),
                cls="flex items-center ml-4",
            ),
            cls="flex items-center",
        ),
        cls="mb-4",
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
            # Ensure html/body have dark background
            Style("html, body { background-color: #111827; margin: 0; padding: 0; }"),
            # Skeleton loading script
            Script("""
                function showSkeleton() {
                    const main = document.getElementById('main-content');
                    if (main) {
                        main.innerHTML = `
                            <div>
                                <div class="mb-4">
                                    <div class="h-10 bg-gray-800 rounded-lg w-full animate-pulse"></div>
                                </div>
                                <div id="todo-list-container">
                                    <ul class="space-y-2">
                                        ${Array(6).fill().map(() => `
                                            <li class="mb-2">
                                                <div class="flex items-center p-3 bg-gray-800 rounded-lg">
                                                    <div class="w-5 h-5 bg-gray-700 rounded animate-pulse"></div>
                                                    <div class="ml-3 flex-1">
                                                        <div class="h-4 bg-gray-700 rounded w-3/4 animate-pulse"></div>
                                                        <div class="h-3 bg-gray-700 rounded w-1/2 mt-2 animate-pulse"></div>
                                                    </div>
                                                </div>
                                            </li>
                                        `).join('')}
                                    </ul>
                                    <div class="mt-4">
                                        <div class="h-4 bg-gray-700 rounded w-20 animate-pulse"></div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }
                }
            """),
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
                            hx_post="/web/refresh",
                            hx_target="#main-content",
                            hx_disabled_elt="this",
                            cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 "
                            "disabled:opacity-50 disabled:cursor-wait",
                            **{"hx-on:htmx:before-request": "showSkeleton()"},
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
                render_node_name(node.name, is_completed),
                Span(
                    node.breadcrumb or "",
                    cls="text-xs text-gray-500 block",
                ),
                cls="ml-3 flex-1",
            ),
            status_tag_badge(node.status_tag),
            cls="flex items-center p-3 bg-gray-800 rounded-lg hover:bg-gray-750",
        ),
        cls="mb-2",
        id=f"todo-{node.id}",
    )


def filter_input(current_filter: str = "", show_completed: bool = False):
    """Render the filter input component for todos view."""
    return filter_input_field(current_filter, "/web/todos", "#todo-list-container", show_completed)


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


def todo_list(nodes, current_filter: str = "", show_completed: bool = False):
    """Render the full todo list with filter."""
    return Div(
        filter_input(current_filter, show_completed),
        todo_list_items(nodes),
    )


def empty_state(message: str):
    """Render an empty state message."""
    return Div(
        Div(
            Span(message, cls="text-gray-400"),
            Button(
                "Refresh from Workflowy",
                hx_post="/web/refresh",
                hx_target="#main-content",
                cls="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
            ),
            cls="text-center py-12",
        ),
        cls="bg-gray-800 rounded-lg p-8",
    )


def skeleton_item():
    """Render a skeleton loading item."""
    return Li(
        Div(
            Div(cls="w-5 h-5 bg-gray-700 rounded animate-pulse"),
            Div(
                Div(cls="h-4 bg-gray-700 rounded w-3/4 animate-pulse"),
                Div(cls="h-3 bg-gray-700 rounded w-1/2 mt-2 animate-pulse"),
                cls="ml-3 flex-1",
            ),
            cls="flex items-center p-3 bg-gray-800 rounded-lg",
        ),
        cls="mb-2",
    )


def skeleton_list():
    """Render a skeleton loading list."""
    return Div(
        Div(
            Div(cls="h-10 bg-gray-800 rounded-lg w-full animate-pulse"),
            cls="mb-4",
        ),
        Div(
            Ul(
                *[skeleton_item() for _ in range(6)],
                cls="space-y-2",
            ),
            Div(
                Div(cls="h-4 bg-gray-700 rounded w-16 animate-pulse"),
                cls="mt-4",
            ),
            id="todo-list-container",
        ),
    )

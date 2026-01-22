# Tab Navigation

## Overview

The app provides two views for managing todos: a flat **Todos** list and a **Kanban** board. Users can switch between views while preserving their current filter settings.

## Features

### View Switching
- Todos button: Flat list view sorted by color priority and order
- Kanban button: Column-based board grouped by status tag
- Refresh button: Syncs data from Workflowy API

### Filter Preservation
- Filter text is preserved when switching tabs
- Show completed toggle state is preserved
- URL is updated with filter parameters

## Implementation

### Navigation Buttons
Located in `app/web/components.py` within the `base_page()` function.

### Filter Preservation Logic
Uses HTMX's `htmx:configRequest` event to inject current filter values:

```javascript
document.addEventListener('htmx:configRequest', function(evt) {
    const el = evt.detail.elt;
    if (!el.classList.contains('nav-tab-btn')) return;

    const filterInput = document.querySelector('input[name="filter_text"]');
    const showCompleted = document.querySelector('input[name="show_completed"]');

    if (filterInput && filterInput.value) {
        evt.detail.parameters['filter_text'] = filterInput.value;
    }
    if (showCompleted && showCompleted.checked) {
        evt.detail.parameters['show_completed'] = 'true';
    }
});
```

### HTMX Attributes
- `hx-get`: Target URL (`/web/todos` or `/web/kanban`)
- `hx-target`: `#main-content` for full content swap
- `hx-push-url`: Updates browser URL for bookmarking

## Routes

- `GET /web/todos` - Todos list view (`app/web/pages.py:37-94`)
- `GET /web/kanban` - Kanban board view (`app/web/pages.py:97-154`)

## Code Location

- Navigation buttons: `app/web/components.py:265-280`
- Filter preservation script: `app/web/components.py:161-175`

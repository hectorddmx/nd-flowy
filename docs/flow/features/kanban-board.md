# Kanban Board

## Overview

The Kanban board provides a visual way to manage todos by status. Cards can be dragged between columns to update their status.

## Features

### Columns
Six status columns in order:
1. **Backlog** - Items not yet started (gray)
2. **Blocked** - Items waiting on dependencies (red)
3. **Todo** - Items ready to work on (yellow)
4. **WIP** - Work in progress (blue)
5. **Test** - Items being tested (purple)
6. **Done** - Completed items (green)

### Drag and Drop
- Drag cards between columns to change status
- Visual feedback during drag (ghost card, column highlight)
- Automatic sync to Workflowy on drop
- Revert on error

### Card Display
- Todo name with HTML support
- Breadcrumb path (truncated)
- Color-coded by status

## Implementation

### Sortable.js Integration
Uses Sortable.js for drag-and-drop functionality:

```javascript
new Sortable(column, {
    group: 'kanban',
    animation: 150,
    onEnd: function(evt) {
        const nodeId = evt.item.dataset.nodeId;
        const newStatus = evt.to.dataset.status;

        fetch(`/api/nodes/${nodeId}/status`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus }),
        });
    }
});
```

### Status Update Endpoint
`POST /api/nodes/{node_id}/status` in `app/routers/api.py`:
1. Updates the node name with new status tag
2. Syncs to Workflowy API
3. Updates local cache

### Status Tags
Status is stored as a hashtag in the node name (e.g., `#WIP`, `#DONE`).
The `update_status_tag()` function handles replacing existing tags.

## Components

- `kanban_board()` - Full board with all columns
- `kanban_column()` - Single column with cards
- `kanban_card()` - Individual todo card
- `kanban_scripts()` - JavaScript for drag-and-drop

## Code Location

- Kanban components: `app/web/kanban.py`
- Status update API: `app/routers/api.py:189-216`
- Status tag utilities: `app/services/workflowy_client.py`

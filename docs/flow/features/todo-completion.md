# Todo Completion

## Overview

Users can mark todos as complete or incomplete by clicking checkboxes. Changes are synced to Workflowy and reflected in the local cache.

## Features

### Checkbox Behavior
- Click to toggle completion status
- Visual feedback: completed items show strikethrough text
- Immediate sync to Workflowy API
- Local cache updated for instant UI response

### Styling
- Unchecked: Gray background checkbox
- Checked: Blue background with white checkmark
- Completed text: Strikethrough with muted gray color

## Implementation

### Frontend Component
The `todo_item()` function in `app/web/components.py` renders each todo:

```python
Input(
    type="checkbox",
    checked=is_completed,
    hx_post=f"/web/nodes/{node.id}/{'uncomplete' if is_completed else 'complete'}",
    hx_swap="outerHTML",
    hx_target="closest li",
    cls=checkbox_cls,
)
```

### Backend Endpoints
Located in `app/web/pages.py`:

- `POST /web/nodes/{node_id}/complete` - Mark as complete
- `POST /web/nodes/{node_id}/uncomplete` - Mark as incomplete

Both endpoints:
1. Call Workflowy API to update the node
2. Update local cache with new completion timestamp
3. Return updated HTML for the todo item

### Workflowy Integration
The `WorkflowyClient` in `app/services/workflowy_client.py` handles:
- `complete_node(node_id)` - Sets completion timestamp
- `uncomplete_node(node_id)` - Removes completion timestamp

## Code Location

- Todo item component: `app/web/components.py:307-335`
- Web endpoints: `app/web/pages.py:272-319`
- API endpoints: `app/routers/api.py:145-186`

# Status Tags

## Overview

Status tags are hashtags in todo names that indicate the current status. They're displayed as colored badges and determine kanban column placement.

## Supported Tags

| Tag | Color | Description |
|-----|-------|-------------|
| `#BACKLOG` | Gray | Not yet started |
| `#BLOCKED` | Red | Waiting on dependencies |
| `#TODO` | Yellow | Ready to work on |
| `#WIP` | Blue | Work in progress |
| `#TEST` | Purple | Being tested |
| `#DONE` | Green | Completed |

## Features

### Badge Display
- Tags rendered as colored pills/badges
- Displayed in both Todos list and Kanban cards
- Tag text stripped from displayed name to avoid duplication

### Automatic Extraction
- Tags extracted from node names during sync
- Case-insensitive matching
- Stored in `status_tag` field in cache

### Kanban Grouping
- Cards grouped by status tag in kanban view
- Items without tags default to "Backlog"
- Drag-and-drop updates the tag in node name

## Implementation

### Tag Pattern
```python
STATUS_TAG_PATTERN = re.compile(
    r"\s*#(BACKLOG|BLOCKED|TODO|WIP|TEST|DONE)\b",
    re.IGNORECASE
)
```

### Color Definitions
```python
STATUS_TAG_COLORS = {
    "BACKLOG": ("bg-gray-600", "text-white"),
    "BLOCKED": ("bg-red-800", "text-red-200"),
    "TODO": ("bg-yellow-600", "text-yellow-100"),
    "WIP": ("bg-blue-600", "text-blue-100"),
    "TEST": ("bg-purple-600", "text-purple-100"),
    "DONE": ("bg-green-700", "text-green-100"),
}
```

### Key Functions

- `extract_status_tag(name)` - Get tag from node name
- `strip_status_tag(name)` - Remove tag for display
- `update_status_tag(name, new_status)` - Replace/add tag
- `status_tag_badge(tag)` - Render colored badge component

## Usage in Workflowy

Add tags directly in Workflowy node names:
- "Implement login #WIP"
- "Fix bug #TODO"
- "Review PR #TEST"

Tags are synced bidirectionally - changes in the app update Workflowy.

## Code Location

- Tag constants: `app/web/components.py:26-36`
- Badge component: `app/web/components.py:46-55`
- Extraction logic: `app/services/workflowy_client.py`
- Status enum: `app/models/schemas.py`

# Column Collapsing

## Overview

Kanban columns can be collapsed to save horizontal space and focus on relevant status columns. Collapsed state is persisted in localStorage.

## Features

### Collapse Behavior
- Click column header to collapse
- Click anywhere on collapsed column to expand
- Collapsed columns show:
  - Item count badge
  - Vertical column title
- Expanded columns show:
  - Full header with title and count
  - All cards in the column

### State Persistence
- Collapsed columns saved to `localStorage`
- State restored on page load and HTMX navigation
- Survives browser refresh and tab switching

## Implementation

### Toggle Functions

```javascript
function toggleColumn(wrapper) {
    const columnName = wrapper.dataset.column;
    const isCollapsed = wrapper.classList.toggle('collapsed');

    // Save to localStorage
    const collapsedColumns = JSON.parse(
        localStorage.getItem('kanban-collapsed') || '[]'
    );
    if (isCollapsed) {
        collapsedColumns.push(columnName);
    } else {
        const index = collapsedColumns.indexOf(columnName);
        if (index > -1) collapsedColumns.splice(index, 1);
    }
    localStorage.setItem('kanban-collapsed', JSON.stringify(collapsedColumns));
}

function restoreCollapsedState() {
    const collapsedColumns = JSON.parse(
        localStorage.getItem('kanban-collapsed') || '[]'
    );
    collapsedColumns.forEach(function(columnName) {
        const wrapper = document.querySelector(
            `.kanban-column-wrapper[data-column="${columnName}"]`
        );
        if (wrapper) wrapper.classList.add('collapsed');
    });
}
```

### CSS Classes
- `.kanban-column-wrapper` - Column container
- `.collapsed` - Applied when column is collapsed
- `.column-header` - Expanded header (hidden when collapsed)
- `.collapsed-header` - Collapsed header (shown when collapsed)
- `.column-content` - Card container (hidden when collapsed)

### Event Initialization
- Runs on `DOMContentLoaded`
- Re-runs on `htmx:afterSwap` for HTMX navigation

## Code Location

- Column toggle JavaScript: `app/web/kanban.py:191-254`
- Column component: `app/web/kanban.py:46-90`
- CSS styles: `app/static/styles.css`

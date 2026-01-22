# Filter & Search

## Overview

The filter/search feature allows users to quickly find todos by name or project (breadcrumb). It's available in both the Todos list and Kanban board views.

## Features

### Search Input
- Text input with search icon on the left
- Clear button (X) on the right that appears when text is entered
- Supports comma-separated filters for multiple terms
- Filters by both todo name and breadcrumb path

### Show Completed Toggle
- Checkbox to toggle visibility of completed items
- Hidden by default to focus on active work

### URL Persistence
- Filter state is pushed to the URL (`?filter_text=...&show_completed=true`)
- Allows bookmarking and sharing filtered views
- Preserves filter when refreshing the page

## Implementation

### Components
- `filter_input_field()` in `app/web/components.py` - Reusable filter component
- `filter_input()` - Wrapper for todos view with sticky positioning
- `kanban_filter_input()` in `app/web/kanban.py` - Wrapper for kanban view

### Behavior
- Uses HTMX for live filtering without page reload
- Debounced input (300ms delay) to avoid excessive requests
- Clear button triggers immediate filter refresh

## Usage

1. Type in the search box to filter items
2. Use commas to filter by multiple terms (e.g., "project1, urgent")
3. Click the X button or clear the input to reset
4. Toggle "Show completed" to include/exclude completed items

## Code Location

- Filter input: `app/web/components.py:66-140`
- Clear button JavaScript: `app/web/components.py:176-195`

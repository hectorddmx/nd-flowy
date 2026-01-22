# Live Reload (Development)

## Overview

Live reload automatically refreshes the browser when code changes are saved, speeding up the development workflow.

## Features

### Server Reload
- Uvicorn watches for file changes
- Automatically restarts on Python, HTML, CSS, JS changes
- Configurable file patterns

### Browser Refresh
- WebSocket connection to `/hot-reload`
- Automatic page reload when server restarts
- Only active on localhost

## Setup

### Running with Live Reload

```bash
# Using just (recommended)
mise exec -- just run

# Or directly with uvicorn
DEBUG=true uvicorn app.main:app --reload \
    --reload-include '*.html' \
    --reload-include '*.css' \
    --reload-include '*.js'
```

### Installing Dependencies

```bash
mise exec -- just install
```

This installs `arel` for browser hot reload.

## Implementation

### Server-Side (Arel)
In `app/main.py`:

```python
DEBUG = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")

if DEBUG:
    import arel
    hot_reload = arel.HotReload(
        paths=[arel.Path("app"), arel.Path("app/static")]
    )
    app.add_websocket_route("/hot-reload", route=hot_reload)
```

### Client-Side Script
Injected in `app/web/components.py`:

```javascript
(function() {
    if (window.location.hostname !== 'localhost') return;
    var ws = new WebSocket('ws://' + window.location.host + '/hot-reload');
    ws.onclose = function() {
        setTimeout(function() {
            var newWs = new WebSocket('ws://' + window.location.host + '/hot-reload');
            newWs.onopen = function() { window.location.reload(); };
        }, 1000);
    };
})();
```

## How It Works

1. You save a file
2. Uvicorn detects the change and restarts
3. The WebSocket connection closes
4. Client attempts to reconnect
5. On successful reconnection, page reloads

## Configuration

### Environment Variables
- `DEBUG=true` - Enables hot reload

### Watched Directories
Configured in `app/main.py`:
- `app/` - Python source files
- `app/static/` - CSS and other static files

### File Patterns
Configured in `justfile`:
- `*.py` - Python files (default)
- `*.html` - HTML templates
- `*.css` - Stylesheets
- `*.js` - JavaScript files

## Code Location

- Server setup: `app/main.py:14-35`
- Client script: `app/web/components.py:159-172`
- Just command: `justfile:41-45`

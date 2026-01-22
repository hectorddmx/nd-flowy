# FastHTML Live Reload Development

This guide covers setting up live reload for FastHTML development, enabling automatic browser refresh when you save changes.

## Quick Start

### Using `fast_app` with `live=True`

The simplest way to enable live reload in FastHTML:

```python
from fasthtml.common import *

app, rt = fast_app(live=True)

@rt("/")
def get():
    return Titled("Hello", P("World"))

serve()
```

Run with:

```bash
python main.py
```

### Using `FastHTMLWithLiveReload` Directly

For more control, use the class directly:

```python
from fasthtml.common import *

app = FastHTMLWithLiveReload()

@app.get("/")
def home():
    return Titled("Hello", P("World"))
```

Run with uvicorn:

```bash
uvicorn main:app --reload
```

## Configuration Options

### `fast_app` Parameters

```python
app, rt = fast_app(
    live=True,                  # Enable live reload
    reload_attempts=1,          # Number of reconnection attempts
    reload_interval=1000,       # Milliseconds between attempts
)
```

### Custom Headers with Live Reload

```python
# With Tailwind CSS
app, rt = fast_app(
    hdrs=(Script(src="https://cdn.tailwindcss.com"),),
    live=True,
    pico=False,
)

# With MonsterUI theme
from monsterui.all import Theme
app, rt = fast_app(
    hdrs=Theme.blue.headers(),
    live=True,
)
```

## How It Works

FastHTML's live reload uses a WebSocket connection:

1. The server injects a small JavaScript snippet into rendered pages
2. The script establishes a WebSocket connection to the server
3. When files change, uvicorn restarts the server
4. The WebSocket connection drops, triggering the client to reconnect
5. On successful reconnection, the page automatically reloads

This is "server-push" functionality built into the development workflow.

## Multi-Directory Projects

For projects spanning multiple directories, use uvicorn's `--reload-dir` flag:

```bash
uvicorn main:app --reload \
    --reload-dir app \
    --reload-dir components \
    --reload-dir templates
```

## Watching Non-Python Files

To reload on HTML, CSS, or JS changes:

```bash
uvicorn main:app --reload \
    --reload-include '*.html' \
    --reload-include '*.css' \
    --reload-include '*.js'
```

## Combining FastAPI and FastHTML

When using FastHTML components within a FastAPI app, you have two options:

### Option 1: Mount FastHTML as Sub-App

```python
from fastapi import FastAPI
from fasthtml.common import fast_app

# Main FastAPI app
api = FastAPI()

# FastHTML sub-app with live reload
fh_app, rt = fast_app(live=True)

@rt("/")
def home():
    return Titled("Home", P("Welcome"))

# Mount FastHTML under /web
api.mount("/web", fh_app)
```

### Option 2: Use Arel for Browser Reload

If your FastAPI app uses FastHTML components but not `fast_app`, use Arel for browser hot reload (see FastAPI live reload docs).

## Important Gotchas

1. **Save to Trigger**: Reloads only happen when you **save** files, not on every keystroke

2. **Development Only**: `FastHTMLWithLiveReload` should never be used in production
   ```python
   import os
   live = os.getenv("ENV") != "production"
   app, rt = fast_app(live=live)
   ```

3. **Component Requirement**: The reload script only injects into pages that render `ft` components. Plain HTML strings won't get the script.

4. **CSS in Head Issue**: There's a known issue where custom CSS with `live=True` might be placed in body instead of head. Use:
   ```python
   app, rt = fast_app(
       hdrs=(Link(rel="stylesheet", href="/static/styles.css"),),
       live=True,
   )
   ```

## Troubleshooting

### Page Not Reloading

- Ensure `live=True` is set
- Check that you're running with `--reload` flag
- Verify the page renders ft components (not raw HTML strings)

### Styles Not Updating

- Add CSS files to reload includes: `--reload-include '*.css'`
- Hard refresh browser to clear cache (Cmd+Shift+R / Ctrl+Shift+R)

### Multiple Reload Attempts

If the page reloads multiple times:
- Reduce `reload_attempts` parameter
- Check for multiple WebSocket connections

## References

- [FastHTML Live Reload Documentation](https://www.fastht.ml/docs/ref/live_reload.html)
- [FastHTML fast_app API](https://docs.fastht.ml/api/fastapp.html)
- [Uvicorn Development Settings](https://www.uvicorn.org/settings/#development)
- [Building Dynamic UIs with FastHTML and HTMX](https://isaacflath.com/blog/2025-04-03-Dynamic%20UI%20Interactions%20with%20FastHTML%20and%20HTMX)

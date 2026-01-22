# FastAPI Live Reload Development

This guide covers setting up live reload for FastAPI development, including both server-side auto-reload and browser hot-reload.

## Server-Side Auto-Reload (Uvicorn)

### Basic Usage

FastAPI uses Uvicorn as its ASGI server. Enable auto-reload with the `--reload` flag:

```bash
uvicorn app.main:app --reload --port 8000
```

Or using FastAPI CLI:

```bash
fastapi dev app/main.py
```

### Watching Additional File Types

By default, uvicorn only watches `.py` files. To include HTML, CSS, and other files:

```bash
uvicorn app.main:app --reload \
    --reload-include '*.html' \
    --reload-include '*.css' \
    --reload-include '*.js'
```

### Watching Multiple Directories

For multi-directory projects, use `--reload-dir`:

```bash
uvicorn app.main:app --reload \
    --reload-dir app \
    --reload-dir templates \
    --reload-dir static
```

## Browser Hot-Reload with Arel

Server reload doesn't automatically refresh the browser. Use [Arel](https://github.com/florimondmanca/arel) for browser hot-reload.

### Installation

```bash
pip install arel
# or with uv:
uv add arel
```

### Setup

1. **Add to your FastAPI app** (`app/main.py`):

```python
import os
import arel
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates("templates")

# Development-only hot reload
if _debug := os.getenv("DEBUG"):
    hot_reload = arel.HotReload(
        paths=[
            arel.Path("app"),      # Watch app directory
            arel.Path("static"),   # Watch static files
        ]
    )
    app.add_websocket_route("/hot-reload", route=hot_reload, name="hot-reload")
    app.add_event_handler("startup", hot_reload.startup)
    app.add_event_handler("shutdown", hot_reload.shutdown)

    # Make available in templates
    templates.env.globals["DEBUG"] = _debug
    templates.env.globals["hot_reload"] = hot_reload
```

2. **Add script to your HTML template**:

```html
{% if DEBUG %}
    {{ hot_reload.script(url_for('hot-reload')) | safe }}
{% endif %}
```

3. **Run with DEBUG flag**:

```bash
DEBUG=true uvicorn app.main:app --reload
```

## WebSocket-Based Hot Reload (Manual Implementation)

If you prefer not to use Arel, implement a simple WebSocket-based reload:

### Server-Side

```python
from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws-reload")
async def websocket_reload(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except:
        pass
```

### Client-Side Script

```javascript
(function() {
    const maxRetries = 5;
    let retries = 0;

    function connect() {
        const ws = new WebSocket(`ws://${window.location.host}/ws-reload`);

        ws.onopen = () => {
            console.log('Hot reload connected');
            retries = 0;
        };

        ws.onclose = () => {
            if (retries < maxRetries) {
                retries++;
                setTimeout(() => {
                    connect();
                    // Reload on successful reconnect
                    window.location.reload();
                }, 1000);
            }
        };
    }

    connect();
})();
```

## Best Practices

1. **Development Only**: Never enable hot reload in production
2. **Use Environment Variables**: Control hot reload via `DEBUG` or similar flags
3. **Watch Specific Directories**: Avoid watching `node_modules`, `.venv`, etc.
4. **Combine with `--reload`**: Use both uvicorn's `--reload` and browser hot-reload

## Troubleshooting

### Reload Not Triggering

- Ensure files are being saved (not just modified in memory)
- Check that file patterns are included: `--reload-include '*.html'`
- Verify the watched directories are correct

### WebSocket Connection Failing

- Check that the WebSocket endpoint is registered
- Ensure no firewall blocking WebSocket connections
- Verify the URL matches your server configuration

## References

- [Uvicorn Settings Documentation](https://www.uvicorn.org/settings/)
- [FastAPI CLI Documentation](https://fastapi.tiangolo.com/fastapi-cli/)
- [Arel GitHub Repository](https://github.com/florimondmanca/arel)
- [Browser Hot Reloading with Arel](https://dev.to/ashleymavericks/browser-hot-reloading-for-python-asgi-web-apps-using-arel-1l19)

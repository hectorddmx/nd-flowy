"""FastAPI + FastHTML application for Workflowy Flow."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.routers import api_router, health_router
from app.web.pages import router as web_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title=settings.app_name,
    description="Workflowy viewer with todos list and kanban board views",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(health_router)
app.include_router(api_router)
app.include_router(web_router)


@app.get("/")
async def root():
    """Redirect root to web interface."""
    return RedirectResponse(url="/web/todos")


# Create default styles.css if it doesn't exist
styles_path = static_dir / "styles.css"
if not styles_path.exists():
    styles_path.write_text("""
/* Custom dark theme styles */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

/* Custom checkbox styling */
.form-checkbox {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    display: inline-block;
    vertical-align: middle;
    background-origin: border-box;
    user-select: none;
    flex-shrink: 0;
    cursor: pointer;
}

.form-checkbox:checked {
    background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
    background-size: 100% 100%;
    background-position: center;
    background-repeat: no-repeat;
    background-color: #2563eb;
    border-color: #2563eb;
}

/* Kanban card drag styling */
.sortable-ghost {
    opacity: 0.5;
}

.sortable-drag {
    opacity: 1;
}

/* Scrollbar styling for dark theme */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #1f2937;
}

::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
}

/* Hover state for cards */
.bg-gray-650 {
    background-color: #3a4556;
}

.bg-gray-750 {
    background-color: #2d3748;
}
""")

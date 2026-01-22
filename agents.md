# Agent Instructions

## Environment Setup

This project uses `mise` for managing Python, Node.js, and development tools. To ensure environment variables (including secrets) are loaded correctly, always use:

```bash
mise exec -- <command>
```

### Examples

**Install/sync dependencies:**
```bash
mise exec -- just install
```

**Run the development server:**
```bash
mise exec -- just run
```

**Run tests:**
```bash
mise exec -- just test
```

**Run linting:**
```bash
mise exec -- just lint
```

**Run all checks (lint + test):**
```bash
mise exec -- just check
```

## Secret Management

Secrets are stored in `mise.local.toml` which is gitignored. The following environment variables are required:

- `WF_API_KEY` - Workflowy API key for authentication

These are automatically loaded when using `mise exec --`.

## Project Structure

- `app/` - Main application code
  - `core/` - Configuration and database setup
  - `models/` - SQLAlchemy models and Pydantic schemas
  - `services/` - External service clients (Workflowy)
  - `routers/` - FastAPI route handlers
  - `web/` - FastHTML pages and components
- `tests/` - Test files
- `docs/` - Documentation

## Development Workflow

1. Use `mise exec -- just run` to start the development server
2. Visit `http://localhost:8000/web/todos` for the plain todos view
3. Visit `http://localhost:8000/web/kanban` for the kanban board view
4. Use the refresh button to sync data from Workflowy

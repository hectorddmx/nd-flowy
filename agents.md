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

- `WF_API_KEY` - Workflowy API key for authentication (see [API Keys Guide](docs/workflowy/api-keys.md))

These are automatically loaded when using `mise exec --`.

### Generating .env files for Docker

To generate environment files for Docker from mise configuration:

```bash
# Generate .env for current environment
mise env --dotenv > .env.development

# Generate with specific environment
MISE_ENV=production mise env --dotenv > .env.production
```

Note: `.env*` files are gitignored and should never be committed.

## Git Safety Guidelines

**NEVER do the following without explicit user request:**
- Force push (`git push --force`)
- Hard reset (`git reset --hard`)
- Delete branches (`git branch -D`)
- Skip hooks (`--no-verify`)
- Amend commits that may have been pushed

**Safe practices:**
- Always test changes before merging
- Use safe delete patterns (`git branch -d` not `-D`)
- Create new commits instead of amending when in doubt
- Verify branch status before destructive operations
- Never merge untested code to main

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

## Chrome Extension Integration

Claude Code can interact with the browser via the Claude in Chrome extension. This enables:
- Taking screenshots to verify UI rendering
- Clicking elements and filling forms
- Reading console logs for debugging
- Inspecting DOM structure

### Setup
```bash
# Start Claude Code with Chrome integration
claude --chrome

# Verify connection
/chrome
```

### Common Testing Commands
```
# Take a screenshot
Open localhost:8000/web/todos and take a screenshot

# Test interactions
Click the Refresh button and wait for it to complete

# Check for errors
Check the browser console for any JavaScript errors

# Inspect HTML
Get the HTML structure of the todo list
```

See `docs/claude/chrome-extension.md` for full documentation.

## Documentation

### WorkFlowy
- [About WorkFlowy](docs/workflowy/about.md) - What is WorkFlowy, features, pricing, and account setup
- [API Keys](docs/workflowy/api-keys.md) - How to obtain and manage your WorkFlowy API key
- [API Reference](docs/workflowy/readme.md) - REST API endpoints and usage

### Tools & Development
- [mise](docs/mise/readme.md) - Environment and tool version management
- [just](docs/just/readme.md) - Command runner for common tasks
- [Devcontainers](docs/devcontainers/readme.md) - Development container setup
- [OrbStack](docs/orbstack/local-domains-and-https.md) - Local domains and HTTPS for containers
- [Chrome Extension](docs/claude/chrome-extension.md) - Browser automation with Claude

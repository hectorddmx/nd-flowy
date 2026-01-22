# Dev Containers

This project supports [Development Containers](https://containers.dev/) for a consistent, reproducible development environment.

## What is a Dev Container?

A dev container uses container technology to create a full-featured development environment. It includes all tools, libraries, and runtimes needed for the project, ensuring every developer has an identical setup.

## Supported Editors & Tools

| Tool | Support Level | Notes |
|------|---------------|-------|
| VS Code | Full | Via [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) |
| Zed | Supported | Native support since v0.218 |
| IntelliJ IDEA | Early support | Remote SSH or local Docker |
| GitHub Codespaces | Full | Cloud-hosted environments |
| DevPod | Full | Client-only, multiple backends |
| Dev Container CLI | Reference | `devcontainer` CLI tool |

## Quick Start

### Prerequisites

- Docker installed and running
- Your `WF_API_KEY` environment variable set (or in `mise.local.toml`)

### VS Code

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project folder
3. Click "Reopen in Container" when prompted (or use Command Palette: `Dev Containers: Reopen in Container`)
4. Wait for the container to build and start

### Zed

1. Open the project folder
2. Zed will prompt to open in a Dev Container
3. Accept to build and connect to the container
4. Alternatively, use Command Palette: `project: open remote`

### Command Line (devcontainer CLI)

```bash
# Install the CLI
npm install -g @devcontainers/cli

# Build and start the container
devcontainer up --workspace-folder .

# Execute commands in the container
devcontainer exec --workspace-folder . uv run uvicorn app.main:app --reload --host 0.0.0.0
```

## Configuration

The dev container is configured in `.devcontainer/devcontainer.json`:

```json
{
  "name": "Workflowy Flow",
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "forwardPorts": [8000],
  "containerEnv": {
    "WF_API_KEY": "${localEnv:WF_API_KEY}"
  }
}
```

### Key Settings

| Setting | Description |
|---------|-------------|
| `forwardPorts` | Ports forwarded from container to host (8000 for the app) |
| `containerEnv` | Environment variables passed to container |
| `postCreateCommand` | Runs after container creation (`uv sync`) |
| `features` | Additional tools installed (git, gh CLI) |

## Environment Variables

The container needs access to your Workflowy API key. Options:

### Option 1: Shell Environment

```bash
export WF_API_KEY=your_api_key_here
```

Then open your editor - it will pass the variable to the container.

### Option 2: mise.local.toml (recommended)

If you have mise set up locally:

```bash
# Generate .env file from mise config
mise env --dotenv > .env.development

# The devcontainer will read WF_API_KEY from your local environment
```

## Running the App

Once inside the container:

```bash
# Start development server with hot reload
uv run uvicorn app.main:app --reload --host 0.0.0.0

# Run tests
uv run pytest

# Run linter
uv run ruff check .
```

Access the app at http://localhost:8000

## Customization

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "your-extension-id"
      ]
    }
  }
}
```

### Adding System Packages

Edit `.devcontainer/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y \
    your-package \
    && rm -rf /var/lib/apt/lists/*
```

### Adding Dev Container Features

Features are reusable components. Add them to `devcontainer.json`:

```json
{
  "features": {
    "ghcr.io/devcontainers/features/node:1": {},
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  }
}
```

Browse available features at [containers.dev/features](https://containers.dev/features).

## Troubleshooting

### Container won't start

```bash
# Check Docker is running
docker info

# Rebuild the container
# VS Code: Command Palette > "Dev Containers: Rebuild Container"
# CLI: devcontainer up --workspace-folder . --rebuild
```

### Port 8000 already in use

```bash
# Find what's using the port
lsof -i :8000

# Or change the port in devcontainer.json
"forwardPorts": [8001]
```

### Environment variable not passed

Ensure `WF_API_KEY` is exported in your shell before opening the editor:

```bash
echo $WF_API_KEY  # Should print your key
```

## References

- [Dev Container Specification](https://containers.dev/)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Zed Dev Containers](https://zed.dev/docs/dev-containers)
- [devcontainer CLI](https://github.com/devcontainers/cli)
- [Available Features](https://containers.dev/features)
- [Available Templates](https://containers.dev/templates)

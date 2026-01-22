# Dev Containers: Logs and Domains with OrbStack

This guide explains how to find your dev container, access its URL, and view logs when using OrbStack.

## Finding Your Dev Container

### Using Docker CLI

```bash
# List all running containers
docker ps

# Filter for devcontainers
docker ps --filter "label=devcontainer.config_file"

# Get container names only
docker ps --format "{{.Names}}"
```

### Using OrbStack GUI

1. Open OrbStack (or Docker Desktop with OrbStack backend)
2. Click **Containers** in the sidebar
3. Look for containers with `devcontainer` labels
4. The **Info** tab shows:
   - **Name**: Container name (e.g., `musing_boyd`)
   - **Domain**: OrbStack URL (e.g., `musing_boyd.orb.local`)
   - **IP**: Direct IP address
   - **Labels**: Shows `devcontainer.config_file` and `devcontainer.local_folder`

## Finding the Container URL

### Method 1: OrbStack GUI

Select your container → Info tab → **Domain** field shows `container-name.orb.local`

### Method 2: Docker Inspect

```bash
# Get container name
docker ps --format "{{.Names}}" --filter "label=devcontainer.config_file"

# Then construct URL
# https://<container-name>.orb.local
```

### Method 3: OrbStack Index

Visit [https://orb.local](https://orb.local) to see all running containers with clickable links.

### URL Pattern

| Container Name | URL |
|----------------|-----|
| `musing_boyd` | `https://musing_boyd.orb.local` |
| `my_app` | `https://my_app.orb.local` |

## Understanding Logs

### Why `docker logs` Shows Little

When you run `docker logs <container>`, you'll typically only see:

```
Container started
```

This is because:
1. Dev containers run a shell/sleep as the main process to stay alive
2. Your application (e.g., uvicorn) runs as a **separate process** inside
3. Only the main process stdout goes to `docker logs`

### Where Application Logs Go

Application logs appear in the **terminal where you started the app**:

- **Zed**: The terminal panel at the bottom of your editor
- **VS Code**: The integrated terminal
- **Docker Desktop**: Terminal tab for the container

### Viewing Logs

#### Option 1: Use Your Editor's Terminal

If you started the app in Zed/VS Code terminal, logs are there. Look for multiple terminal tabs.

#### Option 2: Attach to the Container

```bash
# Open a shell in the container
docker exec -it <container-name> bash

# Find running processes
ps aux | grep uvicorn

# Check if app is running
curl localhost:8000/health
```

#### Option 3: Restart App in Visible Terminal

```bash
# Kill existing process
docker exec <container-name> pkill -f uvicorn

# Start fresh with visible output
docker exec -it <container-name> uv run uvicorn app.main:app --reload --host 0.0.0.0
```

#### Option 4: Docker Desktop/OrbStack Terminal Tab

1. Select your container
2. Click the **Terminal** tab
3. Run your app here to see logs directly

## Useful Commands

### List Dev Containers with Details

```bash
docker ps --filter "label=devcontainer.config_file" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Get Container Info

```bash
# Full inspection
docker inspect <container-name>

# Just the labels
docker inspect <container-name> --format '{{json .Config.Labels}}' | jq

# Mounts
docker inspect <container-name> --format '{{json .Mounts}}' | jq
```

### Check Network/Ports

```bash
# See port mappings
docker port <container-name>

# Get container IP
docker inspect <container-name> --format '{{.NetworkSettings.IPAddress}}'
```

### View Container Filesystem

```bash
# List files in workspace
docker exec <container-name> ls -la /app

# Check if app code is mounted
docker exec <container-name> cat /app/pyproject.toml
```

## Troubleshooting

### Can't Access URL

1. Ensure container is running: `docker ps`
2. Check OrbStack settings → Network → "Direct IP access" is enabled
3. Try the IP directly: `http://<ip>:8000`
4. Verify app is running inside: `docker exec <name> curl localhost:8000`

### No Logs Visible

1. Find where the app was started (check all terminal tabs)
2. Or restart the app in a visible terminal
3. Consider changing `postStartCommand` in `devcontainer.json` to auto-start

### Wrong Container Name

Dev container names are auto-generated (e.g., `musing_boyd`). To find yours:
1. Check OrbStack GUI
2. Or: `docker ps --filter "label=devcontainer.local_folder=<your-project-path>"`

## See Also

- [OrbStack Local Domains](../orbstack/local-domains-and-https.md) - How `.orb.local` domains work
- [Devcontainers Setup](./readme.md) - Dev container configuration

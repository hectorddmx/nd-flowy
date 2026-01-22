# mise - Development Environment Manager

[mise](https://mise.jdx.dev/) (formerly rtx) manages development tools, environment variables, and tasks for this project.

## Installation

```bash
# macOS
brew install mise

# Or via curl
curl https://mise.run | sh

# Activate in your shell (add to ~/.zshrc or ~/.bashrc)
eval "$(mise activate zsh)"  # or bash/fish
```

## Quick Start

```bash
# Install all project tools
mise install

# Or use just
just setup
```

## Configured Tools

The `mise.toml` file configures these tools:

| Tool | Version | Purpose |
|------|---------|---------|
| python | 3.12 | Runtime |
| node | lts | Required for npm packages |
| just | latest | Task runner |
| uv | latest | Fast Python package manager |
| ruff | latest | Python linter/formatter |
| @devcontainers/cli | latest | Dev container CLI for Zed/VS Code |

## Environment Variables

### Configuration Files

| File | Purpose | Git Status |
|------|---------|------------|
| `mise.toml` | Shared config, tools, defaults | Tracked |
| `mise.local.toml` | Local secrets (WF_API_KEY) | **Gitignored** |
| `.env.development` | Generated env file | **Gitignored** |

### Setting Up Secrets

Create `mise.local.toml` with your secrets:

```toml
[env]
WF_API_KEY = "your_workflowy_api_key_here"
```

### Generating .env Files

For Docker or other tools that need `.env` files:

```bash
# Generate from mise config
mise env --dotenv > .env.development

# Or use just
just env-generate
```

### Environment-Specific Config

Set `MISE_ENV` to load different configurations:

```bash
# Development (default)
MISE_ENV=development mise env --dotenv > .env.development

# Production
MISE_ENV=production mise env --dotenv > .env.production
```

## Common Commands

```bash
# Install/update all tools
mise install

# Show current environment
mise env

# Set a tool version
mise use python@3.12

# Run command with mise environment
mise exec -- python --version

# Trust a directory (required for new projects)
mise trust

# Update all tools
mise upgrade
```

## How It Works

1. When you `cd` into the project directory, mise automatically:
   - Adds tool binaries to your PATH
   - Sets environment variables from `mise.toml` and `mise.local.toml`
   - Loads `.env.*` files if configured

2. Tools are installed to `~/.local/share/mise/installs/`

3. Each project can have different tool versions without conflicts

## Troubleshooting

### "Command not found" after installation

```bash
# Ensure mise is activated
eval "$(mise activate zsh)"

# Reshim to update PATH
mise reshim
```

### Environment variables not loading

```bash
# Trust the directory
mise trust

# Check what's being loaded
mise env
```

### Tool version conflicts

```bash
# See which version is active
mise current python

# See where it's coming from
mise where python
```

## References

- [mise Documentation](https://mise.jdx.dev/)
- [mise Configuration](https://mise.jdx.dev/configuration.html)
- [mise Environments](https://mise.jdx.dev/environments/)
- [mise Backends (npm, etc.)](https://mise.jdx.dev/dev-tools/backends/)
